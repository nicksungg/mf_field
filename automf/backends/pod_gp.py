"""NumPy/SciPy POD GP used by M7 without importing neural dependencies.

Extracted from ``models/st_bench/st_common.py``: ``pod_fit``, ``SharedGP`` and
``PODGP``. This retains centered SVD, energy truncation, standardized POD
coefficients, a shared ARD RBF kernel and marginal likelihood fitting. SciPy
Cholesky solves replace general matrix solves, and a constant target gets an
explicit constant predictor instead of fitting a GP to zero coefficients.
"""
from __future__ import annotations

import math
import numpy as np
from scipy.linalg import cho_factor, cho_solve
from scipy.optimize import minimize


def _kernel(X, Z, parameters):
    distance = (X[:, None, :] - Z[None, :, :]) / np.exp(parameters[:-2])
    return np.exp(2 * parameters[-2] - 0.5 * np.square(distance).sum(-1))


class PODGP:
    """Fine field POD with a shared hyperparameter GP over its coefficients."""

    def __init__(self, X, Y, seed=0, energy=0.999, max_modes=64,
                 restarts=2, maxiter=200):
        if not 0 < energy <= 1 or max_modes < 1 or restarts < 1 or maxiter < 1:
            raise ValueError("POD energy must be in (0, 1] and GP budgets positive.")
        self.X = np.array(X, dtype=np.float64, copy=True)
        Y = np.asarray(Y, dtype=np.float64)
        self.mean = Y.mean(0)
        centered = Y - self.mean
        _, singular, vectors = np.linalg.svd(centered, full_matrices=False)
        variance = np.square(singular)
        total = float(variance.sum())
        self.constant = total == 0.0
        if self.constant:
            self.basis = vectors[:0]
            self.energy = 1.0
            self.fit_info = {"gp_fitted": False, "reason": "constant training fields"}
            return
        cumulative = variance.cumsum() / total
        rank = min(max_modes, len(singular),
                   max(1, int(np.searchsorted(cumulative, energy) + 1)))
        self.basis = vectors[:rank]
        self.energy = float(cumulative[rank - 1])
        coefficients = centered @ self.basis.T
        self.cm = coefficients.mean(0)
        self.cs = np.maximum(coefficients.std(0), 1e-12)
        standardized = (coefficients - self.cm) / self.cs
        n, dimension = self.X.shape
        identity = np.eye(n)

        def objective(parameters):
            K = _kernel(self.X, self.X, parameters)
            K += (np.exp(2 * parameters[-1]) + 1e-8) * identity
            try:
                factor = cho_factor(K, lower=True, check_finite=False)
                alpha = cho_solve(factor, standardized, check_finite=False)
            except np.linalg.LinAlgError:
                return 1e25
            return float(0.5 * np.sum(standardized * alpha)
                         + rank * np.log(np.diag(factor[0])).sum()
                         + 0.5 * n * rank * math.log(2 * math.pi))

        rng = np.random.default_rng(seed)
        starts = [np.r_[np.zeros(dimension), 0.0, math.log(0.1)]]
        starts.extend(np.r_[rng.uniform(-0.5, 1.0, dimension),
                            rng.normal(0, 0.3), math.log(0.3)]
                      for _ in range(restarts - 1))
        bounds = [(-3.0, 4.0)] * dimension + [(-4.0, 3.0), (-7.0, 1.0)]
        fits = [minimize(objective, start, method="L-BFGS-B", bounds=bounds,
                         options={"maxiter": maxiter}) for start in starts]
        fit = min(fits, key=lambda value: value.fun)
        self.parameters = fit.x
        K = _kernel(self.X, self.X, self.parameters)
        K += (np.exp(2 * self.parameters[-1]) + 1e-8) * identity
        self.alpha = cho_solve(cho_factor(K, lower=True), standardized)
        self.fit_info = {
            "gp_fitted": True, "gp_converged": bool(fit.success),
            "gp_optimizer_message": str(fit.message), "gp_nlml": float(fit.fun),
            "gp_log_lengthscales": self.parameters[:-2].tolist(),
            "gp_log_signal": float(self.parameters[-2]),
            "gp_log_noise": float(self.parameters[-1]),
        }

    def predict(self, X):
        X = np.asarray(X, dtype=np.float64)
        if self.constant:
            return np.broadcast_to(self.mean, (len(X), len(self.mean))).copy()
        coefficients = _kernel(X, self.X, self.parameters) @ self.alpha
        return (coefficients * self.cs + self.cm) @ self.basis + self.mean

    def info(self):
        return {"pod_modes": len(self.basis), "pod_energy_captured": self.energy,
                **self.fit_info}
