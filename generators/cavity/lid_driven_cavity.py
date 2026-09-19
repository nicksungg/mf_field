"""Reconstructed lid-driven-cavity generator (matches the documented mffpbench scheme).

2D incompressible Navier-Stokes on the unit square in vorticity-streamfunction form:
    omega = dv/dx - du/dy            (vorticity)
    -lap(psi) = omega                (streamfunction Poisson)
    u =  d psi/dy,  v = -d psi/dx
    d omega/dt + u domega/dx + v domega/dy = nu * lap(omega)

Numerics (per the dataset README):
  - First-order UPWIND on convection, central differences on diffusion
    (stable at all cell-Re; the numerical diffusion at coarse res is the genuine
    multi-fidelity signal).
  - RK2 (midpoint) time stepping.
  - dt = 0.125 * min(h^2/nu, h/U)  (RK2 diffusive CFL ~0.5).
  - Streamfunction Poisson solved once per step by sparse LU (factorised once per grid).
  - Vorticity wall BCs via Thom's formula.
  - Steady-state termination at ||omega_new - omega_old||_inf / dt < 1e-4, MAX_STEPS=8000.
  - Re sampled log-uniform in [100, 1000]; SAME Re realisations across all fidelities
    (LF and HF differ only in discretisation).
  - Output: steady-state vorticity field, flattened (N, res*res); cond x = Re (linear).
  - Array convention: omega[0,:] = bottom wall, omega[-1,:] = top wall (moving lid).

This adds a 256x256 HF level on top of the original [32,64,128] so HF is grid-converged.
"""
from __future__ import annotations
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

U_LID = 1.0
RE_LO, RE_HI = 100.0, 1000.0
# NOTE: the original mffpbench generator used MAX_STEPS=8000, which stops time-marching
# BEFORE steady state on fine grids (128 needs ~28k steps, 256 ~100k) — that, not grid
# coarseness, is why the original 128^2 HF failed the convergence check. We run to a true
# steady state (tol 1e-5) with a generous cap so every fidelity is converged ground truth.
MAX_STEPS = 200000
STEADY_TOL = 1e-5


def _poisson_factor(n):
    """LU factorisation of -lap on interior (n-2)^2 nodes, Dirichlet psi=0, unit square."""
    m = n - 2
    h = 1.0 / (n - 1)
    I = sp.identity(m)
    e = np.ones(m)
    T = sp.diags([-e, 2 * e, -e], [-1, 0, 1], shape=(m, m))
    A = (sp.kron(I, T) + sp.kron(T, I)) / h**2     # -lap, 2nd order
    return spla.factorized(A.tocsc()), m, h


def _solve_psi(omega, solve, m, h):
    """Solve -lap psi = omega on interior; psi=0 on walls. omega,(psi) are (n,n)."""
    rhs = omega[1:-1, 1:-1].reshape(-1)
    psi_int = solve(rhs).reshape(m, m)
    psi = np.zeros_like(omega)
    psi[1:-1, 1:-1] = psi_int
    return psi


def _velocities(psi, h):
    u = np.zeros_like(psi); v = np.zeros_like(psi)
    # u = d psi/dy (central), v = -d psi/dx
    u[1:-1, 1:-1] = (psi[2:, 1:-1] - psi[:-2, 1:-1]) / (2 * h)
    v[1:-1, 1:-1] = -(psi[1:-1, 2:] - psi[1:-1, :-2]) / (2 * h)
    return u, v


def _rhs(omega, u, v, nu, h):
    """d omega/dt = -upwind_convection + nu*lap(omega), interior only."""
    o = omega
    # central diffusion
    lap = (o[2:, 1:-1] + o[:-2, 1:-1] + o[1:-1, 2:] + o[1:-1, :-2] - 4 * o[1:-1, 1:-1]) / h**2
    ui = u[1:-1, 1:-1]; vi = v[1:-1, 1:-1]
    # first-order upwind on d/dx (axis=1) and d/dy (axis=0)
    dox_back = (o[1:-1, 1:-1] - o[1:-1, :-2]) / h
    dox_fwd  = (o[1:-1, 2:] - o[1:-1, 1:-1]) / h
    doy_back = (o[1:-1, 1:-1] - o[:-2, 1:-1]) / h
    doy_fwd  = (o[2:, 1:-1] - o[1:-1, 1:-1]) / h
    conv_x = np.where(ui > 0, ui * dox_back, ui * dox_fwd)
    conv_y = np.where(vi > 0, vi * doy_back, vi * doy_fwd)
    out = np.zeros_like(o)
    out[1:-1, 1:-1] = -conv_x - conv_y + nu * lap
    return out


def _apply_wall_omega(omega, psi, h, lid_u=U_LID):
    """Thom's formula wall vorticity. Top wall (row -1) is the moving lid."""
    # bottom (row 0), top (row -1), left (col 0), right (col -1)
    omega[0, :]   = -2.0 * psi[1, :] / h**2
    omega[-1, :]  = -2.0 * psi[-2, :] / h**2 - 2.0 * lid_u / h     # moving lid
    omega[:, 0]   = -2.0 * psi[:, 1] / h**2
    omega[:, -1]  = -2.0 * psi[:, -2] / h**2
    return omega


def solve_cavity(Re, n):
    nu = U_LID * 1.0 / Re                # L=1
    h = 1.0 / (n - 1)
    dt = 0.125 * min(h**2 / nu, h / U_LID)
    solve, m, hh = _poisson_factor(n)
    omega = np.zeros((n, n))
    for step in range(MAX_STEPS):
        psi = _solve_psi(omega, solve, m, h)
        omega = _apply_wall_omega(omega, psi, h)
        u, v = _velocities(psi, h)
        k1 = _rhs(omega, u, v, nu, h)
        omega_mid = omega + 0.5 * dt * k1
        psi_m = _solve_psi(omega_mid, solve, m, h)
        omega_mid = _apply_wall_omega(omega_mid, psi_m, h)
        um, vm = _velocities(psi_m, h)
        k2 = _rhs(omega_mid, um, vm, nu, h)
        omega_new = omega + dt * k2
        psi_n = _solve_psi(omega_new, solve, m, h)
        omega_new = _apply_wall_omega(omega_new, psi_n, h)
        resid = np.abs(omega_new - omega).max() / dt
        omega = omega_new
        if resid < STEADY_TOL:
            break
    return omega, step + 1, resid


def generate(fidelity_levels=(32, 64, 128, 256), n_samples=50, seed=42, train_frac=0.8):
    rng = np.random.default_rng(seed)
    n_total = n_samples
    Re = np.exp(rng.uniform(np.log(RE_LO), np.log(RE_HI), size=n_total))  # log-uniform, SAME across fids
    n_tr = int(round(train_frac * n_total))
    out = {}
    for res in fidelity_levels:
        fields = np.empty((n_total, res * res), dtype=np.float64)
        for i, re in enumerate(Re):
            omega, steps, resid = solve_cavity(re, res)
            fields[i] = omega.reshape(-1)
            print(f"  res={res} sample {i+1}/{n_total} Re={re:.0f} steps={steps} resid={resid:.2e}", flush=True)
        out[res] = (Re.reshape(-1, 1).copy(), fields)
    return out, Re, n_tr


if __name__ == "__main__":
    import argparse, os
    ap = argparse.ArgumentParser()
    ap.add_argument("--levels", default="32,64,128,256")
    ap.add_argument("--n_samples", type=int, default=50)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out_dir", default="lid_driven_cavity_generated_v2")
    args = ap.parse_args()
    levels = [int(x) for x in args.levels.split(",")]
    data, Re, n_tr = generate(levels, args.n_samples, args.seed)
    os.makedirs(args.out_dir, exist_ok=True)
    for li, res in enumerate(levels, start=1):
        X, Y = data[res]
        np.savez(os.path.join(args.out_dir, f"train_l{li}.npz"), x=X[:n_tr], y=Y[:n_tr])
        np.savez(os.path.join(args.out_dir, f"test_l{li}.npz"),  x=X[n_tr:], y=Y[n_tr:])
        print(f"[wrote] L{li} res={res}: train={n_tr} test={len(X)-n_tr}")
