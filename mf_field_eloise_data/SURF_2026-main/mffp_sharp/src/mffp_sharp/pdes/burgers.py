"""1D/2D inviscid Burgers (scalar shock) dataset generation via PyClaw.

u_t + (u^2/2)_x [+ (u^2/2)_y] = 0. A smooth sinusoidal IC steepens into a shock.
LF = coarse grid + 1st-order Godunov (ClawSolver) -> smeared shock; HF = fine grid +
WENO (SharpClawSolver) -> sharp shock. Same IC at every fidelity; only grid+scheme change.

BOX-ONLY: needs clawpack (lazy-imported inside _solve). NOT validated locally; the exact
riemann-solver name / BC / IC wiring is confirmed on the box (like euler.py).
"""
from __future__ import annotations

import numpy as np

NDIMS_SUPPORTED = (1, 2)


def _solve(res: int, ic_amplitude: float, ic_freq: int, output_time: float,
           high_fidelity: bool, ndim: int) -> np.ndarray:
    from clawpack import pyclaw, riemann
    if ndim == 1:
        rs = riemann.burgers_1D
        solver = (pyclaw.SharpClawSolver1D(rs) if high_fidelity
                  else pyclaw.ClawSolver1D(rs))
        if not high_fidelity:
            solver.order = 1
        solver.all_bcs = pyclaw.BC.periodic
        domain = pyclaw.Domain([0.0], [1.0], [res])
        state = pyclaw.State(domain, num_eqn=1)
        state.problem_data["efix"] = True
        x = state.grid.p_centers[0]
        state.q[0, :] = ic_amplitude * np.sin(2 * np.pi * ic_freq * x)
    else:
        rs = riemann.burgers_2D
        solver = (pyclaw.SharpClawSolver2D(rs) if high_fidelity
                  else pyclaw.ClawSolver2D(rs))
        if not high_fidelity:
            solver.order = 1
        solver.all_bcs = pyclaw.BC.periodic
        domain = pyclaw.Domain([0.0, 0.0], [1.0, 1.0], [res, res])
        state = pyclaw.State(domain, num_eqn=1)
        state.problem_data["efix"] = True
        x, y = state.grid.p_centers
        state.q[0, ...] = ic_amplitude * np.sin(2 * np.pi * ic_freq * x) \
            * np.sin(2 * np.pi * ic_freq * y)
    claw = pyclaw.Controller()
    claw.solution = pyclaw.Solution(state, domain)
    claw.solver = solver
    claw.tfinal = output_time
    claw.keep_copy = False
    claw.output_format = None
    claw.verbosity = 0
    claw.run()
    return np.asarray(claw.solution.state.q[0, ...], dtype=np.float64)


def sample_configs(n: int, sampling_cfg: dict, ndim: int, seed: int) -> list[dict]:
    assert ndim in NDIMS_SUPPORTED, f"burgers supports {NDIMS_SUPPORTED}, got {ndim}"
    rng = np.random.default_rng(seed)
    lo_a, hi_a = sampling_cfg["ic_amplitude_range"]
    lo_f, hi_f = sampling_cfg["ic_freq_range"]
    out = []
    for i in range(n):
        out.append({"ic_amplitude": float(rng.uniform(lo_a, hi_a)),
                    "ic_freq": int(rng.integers(lo_f, hi_f + 1)),
                    "ndim": ndim, "seed": seed + i})
    return out


def generate_sample(spec: dict, resolutions: list[int], hf_res: int, output_time: float
                    ) -> tuple[dict[int, np.ndarray], np.ndarray, list[str]]:
    ndim = int(spec["ndim"])
    fields = {
        res: _solve(res, spec["ic_amplitude"], spec["ic_freq"], output_time,
                    high_fidelity=(res == hf_res), ndim=ndim)
        for res in resolutions
    }
    cond = np.array([spec["ic_amplitude"], float(spec["ic_freq"])], dtype=np.float64)
    names = ["ic_amplitude", "ic_freq"]
    return fields, cond, names
