# PyClaw/WENO Shock Solvers (Burgers, Sod, Shallow-Water) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development or superpowers:executing-plans. Checkbox steps.

**Goal:** Add the finite-volume **shock** solvers to the build set by cloning the validated `euler.py` PyClaw pattern: inviscid Burgers (1D+2D), the 1D Sod/Euler shock tube, and shallow-water dam break (1D+2D). These are the genuine-discontinuity candidates the spectral solvers structurally cannot produce.

**Architecture:** Each clones `pdes/euler.py`: a lazy `from clawpack import pyclaw, riemann` *inside* `_solve` (so the module imports without clawpack), LF = 1st-order Godunov (`ClawSolver`, `solver.order = 1`), HF = high-order WENO (`SharpClawSolver`), same IC at every grid, density/height field stored at fixed T. `np`-only outside `_solve`.

**⚠️ COMPUTE SPLIT — READ THIS:** clawpack is **box-only** (`ssh eloise@10.80.6.224`); it is NOT in the local `.venv`. Therefore:
- The **structural** tests (sample_configs shapes, registration, config, NDIMS guard, module imports without clawpack) run **locally**.
- The **solve** tests are guarded with `pytest.importorskip("clawpack")` and **skip locally / run on the box**.
- During execution on the Mac, the solve correctness (exact riemann-solver names, BC, IC wiring) is **NOT verified** — the box-execution step (and the sample round) validates it, exactly as `euler.py` itself is still flagged "VALIDATE on box, not yet executed". Treat the `_solve` bodies as box-validated-pending.

## Global Constraints

- **LF = a real coarse consistent solve (coarse grid + 1st-order Godunov); NEVER downsampled HF.** For these PDEs the fidelities differ in grid **and** scheme (HF=WENO, LF=Godunov), exactly as `euler.py`.
- **Spectral solvers cannot make shocks (verified);** these MUST use PyClaw — that's the point of this plan.
- Condition vector complete + small. Same IC at every fidelity. Python 3.9; `from __future__ import annotations`. Deps unchanged (clawpack already a box dep).
- **Plugin contract uniform** (`NDIMS_SUPPORTED`, `sample_configs`, `generate_sample`); registered in `generate._MODULES`; config block per dataset.
- Git: branch `feat/pyclaw-shocks`; commit per task; trailer `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`. Prefix python cmds with `source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate &&`.

**Depends on:** Plans 1–5 merged. Clones `pdes/euler.py`.

---

## File Structure
| File | Action |
|---|---|
| `pdes/burgers.py` | Create (1D+2D scalar Burgers) |
| `pdes/sod.py` | Create (1D Euler shock tube) |
| `pdes/shallow_water.py` | Create (1D+2D dam break, PDEBench recipe) |
| `generate.py` | Modify — register the three |
| `configs/sample.yaml` | Modify — add config blocks |
| `tests/` | Create `test_burgers.py`, `test_sod.py`, `test_shallow_water.py` (structural local + `importorskip` solve tests) |

The reference `pdes/euler.py` shows the exact PyClaw scaffolding: `SharpClawSolver2D(riemann.euler_4wave_2D)` for HF, `ClawSolver2D(...)` + `solver.order=1` for LF, `pyclaw.Domain`, `pyclaw.State(num_eqn=...)`, `pyclaw.Controller`, `claw.run()`, read `state.q[...]`.

---

## Task 1: Burgers (1D + 2D)

**Files:** Create `pdes/burgers.py`, `tests/test_burgers.py`; modify `generate.py`, `configs/sample.yaml`.

**Interfaces:** `NDIMS_SUPPORTED=(1,2)`; `sample_configs(n,sampling_cfg,ndim,seed)`; `generate_sample(spec,resolutions,hf_res,output_time)` with `names==["ic_amplitude","ic_freq"]`; stores `u` at T. `_solve` lazy-imports clawpack.

Inviscid Burgers $u_t + (u^2/2)_x = 0$ (2D: $+ (u^2/2)_y$). A smooth sinusoidal IC steepens into a shock by T. LF Godunov smears it, HF WENO keeps it sharp.

- [ ] **Step 1: Write tests** — `tests/test_burgers.py`:

```python
import numpy as np
import pytest

from mffp_sharp.pdes import burgers


def test_module_imports_without_clawpack():
    # Lazy clawpack import: the module + sample_configs work with no clawpack installed.
    assert burgers.NDIMS_SUPPORTED == (1, 2)


def test_sample_configs_1d():
    cfg = {"ic_amplitude_range": [0.5, 1.0], "ic_freq_range": [1, 3]}
    specs = burgers.sample_configs(4, cfg, ndim=1, seed=0)
    assert len(specs) == 4 and all(s["ndim"] == 1 for s in specs)
    assert all("ic_amplitude" in s and "ic_freq" in s for s in specs)


def test_sample_configs_rejects_bad_ndim():
    with pytest.raises(AssertionError):
        burgers.sample_configs(2, {"ic_amplitude_range": [0.5, 1.0],
                                   "ic_freq_range": [1, 3]}, ndim=3, seed=0)


@pytest.mark.parametrize("ndim,res", [(1, 64), (2, 32)])
def test_solve_shapes_box(ndim, res):
    pytest.importorskip("clawpack")            # box-only
    spec = {"ic_amplitude": 0.8, "ic_freq": 2, "ndim": ndim, "seed": 0}
    fields, cond, names = burgers.generate_sample(
        spec, [res, 2 * res], 2 * res, output_time=0.2)
    shape1 = (res,) * ndim
    assert fields[res].shape == shape1
    for f in fields.values():
        assert np.isfinite(f).all()
    assert names == ["ic_amplitude", "ic_freq"]
```

- [ ] **Step 2: Run** — `... python -m pytest tests/test_burgers.py -q` → the 3 structural tests FAIL (module missing); the solve test will SKIP once the module exists (no clawpack locally).

- [ ] **Step 3: Create `pdes/burgers.py`** (clone of `euler.py`'s scaffolding):

```python
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
```

- [ ] **Step 4: Register + config.** `generate.py`: add `burgers` to imports + `_MODULES`. `configs/sample.yaml`:
```yaml
  burgers_1d:
    role: shock
    module: burgers
    ndim: 1
    output_time: 0.3
    sampling: {ic_amplitude_range: [0.6, 1.0], ic_freq_range: [1, 3]}
  burgers_2d:
    role: shock
    module: burgers
    ndim: 2
    output_time: 0.3
    sampling: {ic_amplitude_range: [0.6, 1.0], ic_freq_range: [1, 2]}
```

- [ ] **Step 5: Run local structural tests + full suite** — `... python -m pytest tests/test_burgers.py -q` (3 pass, 2 skip) and `... python -m compileall src/mffp_sharp -q && echo OK && python -m pytest tests/ -q` (all pass, PyClaw solve tests skipped). **Box step (deferred):** on the box, `pytest tests/test_burgers.py` runs the solve tests; confirm shocks form + LF smears.

- [ ] **Step 6: Commit** (`feat(burgers): PyClaw 1D/2D scalar shock solver (box-validated)` + trailer).

---

## Task 2: 1D Sod / Euler shock tube

**Files:** Create `pdes/sod.py`, `tests/test_sod.py`; modify `generate.py`, `configs/sample.yaml`.

**Interfaces:** `NDIMS_SUPPORTED=(1,)`; `names==["rho_l","p_l","gamma"]`; stores density `rho` at T. Classic shock-tube IC: left state (ρ_l, 0, p_l), right state (0.125, 0, 0.1), discontinuity at x=0.5.

- [ ] **Step 1: Tests** — `tests/test_sod.py` (mirror Burgers: structural local + `importorskip` solve test asserting `fields[res].shape==(res,)`, finite, `names==["rho_l","p_l","gamma"]`, and `NDIMS_SUPPORTED==(1,)` with ndim=2 rejected).

- [ ] **Step 2: Run → structural fail / solve skip.**

- [ ] **Step 3: Create `pdes/sod.py`** — clone euler scaffolding, 1D:
```python
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
```

- [ ] **Step 4: Register + config:**
```yaml
  sod_1d:
    role: shock
    module: sod
    ndim: 1
    output_time: 0.2
    sampling: {rho_l_range: [0.8, 1.2], p_l_range: [0.8, 1.2], gamma: 1.4}
```

- [ ] **Step 5: Local structural + full suite (solve skipped).** Box step deferred.

- [ ] **Step 6: Commit.**

---

## Task 3: Shallow-water dam break (1D + 2D)

**Files:** Create `pdes/shallow_water.py`, `tests/test_shallow_water.py`; modify `generate.py`, `configs/sample.yaml`.

**Interfaces:** `NDIMS_SUPPORTED=(1,2)`; `names==["inner_height","dam_radius"]`; stores height `h` at T. PDEBench `gen_radial_dam_break` recipe: circular bump `inner_height=2.0` inside `dam_radius~U[0.3,0.7]` over background `h=1`, `grav=1`, Neumann BC, `riemann.shallow_roe_with_efix_2D` (and `_1D`).

- [ ] **Step 1: Tests** (structural local + `importorskip` solve test: shapes per ndim, finite, `names`).

- [ ] **Step 2: Run → structural fail / solve skip.**

- [ ] **Step 3: Create `pdes/shallow_water.py`:**
```python
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
```

- [ ] **Step 4: Register + config:**
```yaml
  shallow_water_1d:
    role: shock
    module: shallow_water
    ndim: 1
    output_time: 0.5
    sampling: {inner_height_range: [1.5, 2.5], dam_radius_range: [0.3, 0.7]}
  shallow_water_2d:
    role: shock
    module: shallow_water
    ndim: 2
    output_time: 0.5
    sampling: {inner_height_range: [1.5, 2.5], dam_radius_range: [0.3, 0.7]}
```

- [ ] **Step 5: Local structural + full suite. Step 6: Commit + push.**

---

## Self-Review

**Spec coverage:** A1 Burgers (1D/2D) ✓; A2 1D Sod ✓; A4 shallow-water (1D/2D) ✓. **A5 Buckley–Leverett DEFERRED** — its non-convex flux needs a *custom* Riemann solver (no packaged PyClaw `riemann.*` for it), a distinct effort; noted for a follow-on.

**Box-validation caveat (explicit):** every `_solve` is box-only and NOT verified locally — exact `riemann.*` names, `num_eqn`, BC, and `problem_data` keys must be confirmed against the box's clawpack during the box-execution step (the structural tests + this template are the local guarantee). This is the same status `euler.py` already carries.

**Type consistency:** uniform `sample_configs`/`generate_sample`; `_MODULES` keys (`burgers`,`sod`,`shallow_water`) match config `module:`. Burgers/shallow-water `(1,2)`, Sod `(1,)`.

**Follow-on:** Plan 7 — special (Helmholtz, porous-medium); Plan 8 — box generation + auto-screen + survivor menu. Buckley–Leverett (custom flux) — a later round.
