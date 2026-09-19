"""2D Euler Riemann (shock) dataset generation via PyClaw/Clawpack.

LF recipe: coarse grid + 1st-order Godunov ("Classic" ClawSolver2D) -> diffuses shocks.
HF recipe: fine grid + high-order WENO ("SharpClaw" SharpClawSolver2D) -> sharp shocks.

So for this PDE the fidelities differ in BOTH grid and scheme: the HF resolution
uses SharpClaw, every coarser (LF) resolution uses Classic. The field we store is
density rho at the fixed output time T (snapshot).

STATUS: written to run on the researcher's 4090 box (needs `clawpack`). NOT yet executed
locally — VALIDATE the PyClaw calls + output_time + that 32^2 Classic visibly
smears the shock during the sample round.
"""
from __future__ import annotations

import numpy as np

from ..common.sampling import sample_euler_configs

GAMMA = 1.4

NDIMS_SUPPORTED = (2,)


def sample_configs(n: int, sampling_cfg: dict, ndim: int, seed: int) -> list[dict]:
    """Schulz-Rinne base configs + jitter; inject gamma + ndim into each spec."""
    assert ndim in NDIMS_SUPPORTED, f"euler supports {NDIMS_SUPPORTED}, got {ndim}"
    gamma = sampling_cfg.get("gamma", GAMMA)
    specs = sample_euler_configs(n, sampling_cfg["jitter_frac"], seed)
    for s in specs:
        s["gamma"] = gamma
        s["ndim"] = ndim
    return specs


def _init_quadrants(state, quadrants, gamma):
    """Set conserved q from the four (rho,u,v,p) quadrant states on the unit square.

    Quadrant order: (top-right, top-left, bottom-left, bottom-right), split at (0.5, 0.5).
    """
    x, y = state.grid.p_centers
    TR, TL, BL, BR = quadrants
    rho = np.empty_like(x)
    u = np.empty_like(x)
    v = np.empty_like(x)
    p = np.empty_like(x)
    for (mask, st) in [
        ((x >= 0.5) & (y >= 0.5), TR),
        ((x < 0.5) & (y >= 0.5), TL),
        ((x < 0.5) & (y < 0.5), BL),
        ((x >= 0.5) & (y < 0.5), BR),
    ]:
        rho[mask], u[mask], v[mask], p[mask] = st
    state.q[0, ...] = rho
    state.q[1, ...] = rho * u
    state.q[2, ...] = rho * v
    state.q[3, ...] = p / (gamma - 1.0) + 0.5 * rho * (u**2 + v**2)


def _solve(res: int, quadrants, output_time: float, gamma: float, high_fidelity: bool) -> np.ndarray:
    """Run one PyClaw solve at resolution `res`; return density field [res, res]."""
    from clawpack import pyclaw, riemann

    if high_fidelity:
        solver = pyclaw.SharpClawSolver2D(riemann.euler_4wave_2D)   # WENO, high order
    else:
        solver = pyclaw.ClawSolver2D(riemann.euler_4wave_2D)        # 1st-order Godunov
        solver.order = 1
    solver.all_bcs = pyclaw.BC.extrap

    domain = pyclaw.Domain([0.0, 0.0], [1.0, 1.0], [res, res])
    state = pyclaw.State(domain, num_eqn=4)
    state.problem_data["gamma"] = gamma
    _init_quadrants(state, quadrants, gamma)

    claw = pyclaw.Controller()
    claw.solution = pyclaw.Solution(state, domain)
    claw.solver = solver
    claw.tfinal = output_time
    claw.keep_copy = False
    claw.output_format = None
    claw.verbosity = 0
    claw.run()

    rho = claw.solution.state.q[0, ...]
    return np.asarray(rho, dtype=np.float64)


def generate_sample(spec: dict, resolutions: list[int], hf_res: int, output_time: float
                    ) -> tuple[dict[int, np.ndarray], np.ndarray, list[str]]:
    """Generate one Euler sample across the fidelity ladder.

    `spec` = {"quadrants": [(rho,u,v,p) x4], "base": tag} from sampling.sample_euler_configs.
    Returns ({res: density field}, condition_vector, condition_names).
    """
    gamma = spec.get("gamma", GAMMA)
    quads = spec["quadrants"]
    fields = {
        res: _solve(res, quads, output_time, gamma, high_fidelity=(res == hf_res))
        for res in resolutions
    }
    cond, names = _condition_vector(quads, gamma)
    return fields, cond, names


def _condition_vector(quadrants, gamma) -> tuple[np.ndarray, list[str]]:
    """Reduce the 4 quadrant states to interpretable scalars (TBD final form).

    Currently: pressure ratios + density ratios across the TL/BR interfaces vs TR,
    plus gamma. Kept small (<=10). Revisit with the researcher — must remain COMPLETE
    (these + solver + T determine the field).
    """
    TR, TL, BL, BR = quadrants
    rho = [q[0] for q in quadrants]
    p = [q[3] for q in quadrants]
    cond = np.array([
        p[1] / p[0], p[2] / p[0], p[3] / p[0],     # pressure ratios vs TR
        rho[1] / rho[0], rho[2] / rho[0], rho[3] / rho[0],
        gamma,
    ], dtype=np.float64)
    names = ["pTL/pTR", "pBL/pTR", "pBR/pTR", "rTL/rTR", "rBL/rTR", "rBR/rTR", "gamma"]
    return cond, names
