"""1D/2D shallow-water dam break (bores / wet-dry fronts) via PyClaw.
Clone of the PDEBench gen_radial_dam_break recipe. BOX-ONLY (clawpack)."""
from __future__ import annotations
import numpy as np

NDIMS_SUPPORTED = (1, 2)
GRAV = 1.0


def _solve(res, inner_height, dam_radius, output_time, high_fidelity, ndim):
    from clawpack import pyclaw, riemann
    if ndim == 1:
        rs = riemann.shallow_roe_with_efix_1D
        solver = (pyclaw.SharpClawSolver1D(rs) if high_fidelity else pyclaw.ClawSolver1D(rs))
        if not high_fidelity:
            solver.order = 1
        solver.all_bcs = pyclaw.BC.extrap
        domain = pyclaw.Domain([0.0], [1.0], [res])
        state = pyclaw.State(domain, num_eqn=2)
        state.problem_data["grav"] = GRAV
        x = state.grid.p_centers[0]
        r = np.abs(x - 0.5)
        state.q[0, :] = np.where(r <= dam_radius, inner_height, 1.0)
        state.q[1, :] = 0.0
    else:
        rs = riemann.shallow_roe_with_efix_2D
        solver = (pyclaw.SharpClawSolver2D(rs) if high_fidelity else pyclaw.ClawSolver2D(rs))
        if not high_fidelity:
            solver.order = 1
        solver.all_bcs = pyclaw.BC.extrap
        domain = pyclaw.Domain([0.0, 0.0], [1.0, 1.0], [res, res])
        state = pyclaw.State(domain, num_eqn=3)
        state.problem_data["grav"] = GRAV
        x, y = state.grid.p_centers
        r = np.sqrt((x - 0.5) ** 2 + (y - 0.5) ** 2)
        state.q[0, ...] = np.where(r <= dam_radius, inner_height, 1.0)
        state.q[1, ...] = 0.0
        state.q[2, ...] = 0.0
    claw = pyclaw.Controller()
    claw.solution = pyclaw.Solution(state, domain)
    claw.solver = solver
    claw.tfinal = output_time
    claw.keep_copy = False; claw.output_format = None; claw.verbosity = 0
    claw.run()
    return np.asarray(claw.solution.state.q[0, ...], dtype=np.float64)


def sample_configs(n, sampling_cfg, ndim, seed):
    assert ndim in NDIMS_SUPPORTED, f"shallow_water supports {NDIMS_SUPPORTED}, got {ndim}"
    rng = np.random.default_rng(seed)
    lh, hh = sampling_cfg["inner_height_range"]; lr, hr = sampling_cfg["dam_radius_range"]
    return [{"inner_height": float(rng.uniform(lh, hh)),
             "dam_radius": float(rng.uniform(lr, hr)),
             "ndim": ndim, "seed": seed + i} for i in range(n)]


def generate_sample(spec, resolutions, hf_res, output_time):
    ndim = int(spec["ndim"])
    fields = {res: _solve(res, spec["inner_height"], spec["dam_radius"], output_time,
                          high_fidelity=(res == hf_res), ndim=ndim) for res in resolutions}
    cond = np.array([spec["inner_height"], spec["dam_radius"]], dtype=np.float64)
    names = ["inner_height", "dam_radius"]
    return fields, cond, names
