"""1D Sod/Euler shock tube (canonical shock+contact+rarefaction) via PyClaw. BOX-ONLY."""
from __future__ import annotations
import numpy as np

NDIMS_SUPPORTED = (1,)
GAMMA = 1.4


def _solve(res, rho_l, p_l, gamma, output_time, high_fidelity):
    from clawpack import pyclaw, riemann
    rs = riemann.euler_with_efix_1D
    solver = (pyclaw.SharpClawSolver1D(rs) if high_fidelity else pyclaw.ClawSolver1D(rs))
    if not high_fidelity:
        solver.order = 1
    solver.all_bcs = pyclaw.BC.extrap
    domain = pyclaw.Domain([0.0], [1.0], [res])
    state = pyclaw.State(domain, num_eqn=3)
    state.problem_data["gamma"] = gamma
    x = state.grid.p_centers[0]
    left = x < 0.5
    rho = np.where(left, rho_l, 0.125)
    p = np.where(left, p_l, 0.1)
    state.q[0, :] = rho
    state.q[1, :] = 0.0
    state.q[2, :] = p / (gamma - 1.0)
    claw = pyclaw.Controller()
    claw.solution = pyclaw.Solution(state, domain)
    claw.solver = solver
    claw.tfinal = output_time
    claw.keep_copy = False; claw.output_format = None; claw.verbosity = 0
    claw.run()
    return np.asarray(claw.solution.state.q[0, :], dtype=np.float64)


def sample_configs(n, sampling_cfg, ndim, seed):
    assert ndim in NDIMS_SUPPORTED, f"sod supports {NDIMS_SUPPORTED}, got {ndim}"
    rng = np.random.default_rng(seed)
    la, ha = sampling_cfg["rho_l_range"]; lp, hp = sampling_cfg["p_l_range"]
    g = sampling_cfg.get("gamma", GAMMA)
    return [{"rho_l": float(rng.uniform(la, ha)), "p_l": float(rng.uniform(lp, hp)),
             "gamma": g, "ndim": ndim, "seed": seed + i} for i in range(n)]


def generate_sample(spec, resolutions, hf_res, output_time):
    fields = {res: _solve(res, spec["rho_l"], spec["p_l"], spec["gamma"], output_time,
                          high_fidelity=(res == hf_res)) for res in resolutions}
    cond = np.array([spec["rho_l"], spec["p_l"], spec["gamma"]], dtype=np.float64)
    names = ["rho_l", "p_l", "gamma"]
    return fields, cond, names
