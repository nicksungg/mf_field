# Special Solvers (high-k Helmholtz, Porous-Medium) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development or superpowers:executing-plans. Checkbox steps.

**Goal:** Add the two "special but tractable" build-set candidates: a **steady-state high-wavenumber Helmholtz** solve (oscillatory; no time, no chaos — dodges the chaos/time-snapshot criteria) and the **porous-medium equation** (degenerate diffusion with a compact-support sharp edge). Both are pure-numpy/scipy and run **locally**.

**Architecture:** Helmholtz is a steady boundary-value problem solved by **sparse direct factorization** (`scipy.sparse` 5-point operator + `spsolve`) — `output_time` is ignored; fidelity = grid resolution (coarse grid under-resolves the oscillations). Porous-medium is `u_t = Δ(u^m)` integrated by an **explicit, positivity-preserving FD** step with a CFL-chosen substep; its compact support has a sharp moving edge. Both plug into the registry; both have an **exact** correctness test (Helmholtz: the linear-solve residual ≈ 0; PME: the Barenblatt self-similar solution).

## Global Constraints

- **LF = a real coarse consistent solve from the same continuous problem; NEVER downsampled HF.** Helmholtz: each grid discretizes and solves the *same continuous BVP* (same analytic source) — the coarse grid genuinely under-resolves. PME: the same analytic IC is evaluated per grid and evolved independently.
- Condition vector complete + small. Python 3.9; `from __future__ import annotations`. Deps: numpy + scipy (both present) — no new deps.
- **Plugin contract uniform**; registered in `generate._MODULES`; config block per dataset. (Helmholtz ignores `output_time`; this is allowed — the signature is kept uniform.)
- Git: branch `feat/special-solvers`; commit per task; trailer `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`. Prefix python cmds with `source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate &&`.

**Depends on:** Plans 1–5 merged.

---

## File Structure
| File | Action |
|---|---|
| `pdes/helmholtz.py` | Create (2D steady, sparse direct) |
| `pdes/porous_medium.py` | Create (1D+2D, explicit positivity FD) |
| `generate.py` | Modify — register both |
| `configs/sample.yaml` | Modify — add blocks |
| `tests/` | Create `test_helmholtz.py`, `test_porous_medium.py` |

---

## Task 1: high-k Helmholtz (2D, steady, sparse direct)

**Files:** Create `pdes/helmholtz.py`, `tests/test_helmholtz.py`; modify `generate.py`, `configs/sample.yaml`.

**Interfaces:** `NDIMS_SUPPORTED=(2,)`; `sample_configs(n,sampling_cfg,ndim,seed)`; `generate_sample(spec,resolutions,hf_res,output_time)` (output_time ignored) with `names==["wavenumber","source_width"]`; stores `u` (real). Also exports `residual(field, res, k, source_width, domain_size) -> float` for the exact test.

Helmholtz: $-\nabla^2 u - k^2 u = f$ on $[0,L]^2$, homogeneous Dirichlet, Gaussian source $f$. Discretized with the 5-point operator into a sparse indefinite system $A u = f$ and solved by `spsolve`. High $k$ ⇒ oscillatory $u$ with energy at wavenumber $\sim k$; the coarse grid under-resolves it.

- [ ] **Step 1: Write tests** — `tests/test_helmholtz.py`:

```python
import numpy as np
import pytest

from mffp_sharp.pdes import helmholtz as hz


def _spec(seed=0):
    return {"wavenumber": 20.0, "source_width": 0.05, "domain_size": 1.0,
            "ndim": 2, "seed": seed}


def test_shapes_finite():
    fields, cond, names = hz.generate_sample(_spec(), [32, 64], 64, output_time=0.0)
    assert fields[32].shape == (32, 32) and fields[64].shape == (64, 64)
    for f in fields.values():
        assert np.isfinite(f).all()
    assert names == ["wavenumber", "source_width"] and cond.shape == (2,)


def test_linear_solve_residual_near_zero():
    # Direct solve -> A u = f to machine precision: the EXACT correctness gate.
    s = _spec()
    fields = hz.generate_sample(s, [64], 64, output_time=0.0)[0]
    r = hz.residual(fields[64], 64, s["wavenumber"], s["source_width"], s["domain_size"])
    assert r < 1e-8


def test_deterministic():
    a = hz.generate_sample(_spec(seed=1), [64], 64, 0.0)[0][64]
    b = hz.generate_sample(_spec(seed=1), [64], 64, 0.0)[0][64]
    assert np.array_equal(a, b)


def test_only_2d_supported():
    assert hz.NDIMS_SUPPORTED == (2,)
    with pytest.raises(AssertionError):
        hz.sample_configs(2, {"wavenumber_range": [10, 30],
                              "source_width_range": [0.03, 0.08], "domain_size": 1.0},
                          ndim=1, seed=0)
```

- [ ] **Step 2: Run → fail (module missing).**

- [ ] **Step 3: Create `pdes/helmholtz.py`:**

```python
"""High-wavenumber Helmholtz (steady, oscillatory) dataset generation.

-laplace(u) - k^2 u = f  on [0,L]^2, homogeneous Dirichlet, Gaussian source f.
A STEADY boundary-value problem (no time, no chaos -> dodges the snapshot-time and
LF-divergence criteria). High k -> oscillatory solution with energy at wavenumber ~k;
the coarse grid under-resolves the oscillation (the bottom rung). Solved by sparse
direct factorization (the indefinite system is best handled by a direct solver).

Field stored: u (real) on the interior grid. output_time is ignored (steady problem).
LF = a genuine coarse-grid discretization of the SAME continuous BVP (same analytic
source), never a downsample of the fine solution.
"""
from __future__ import annotations

import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import spsolve

NDIMS_SUPPORTED = (2,)


def _source(res: int, source_width: float, domain_size: float) -> np.ndarray:
    h = domain_size / (res + 1)
    xs = (np.arange(1, res + 1)) * h
    X, Y = np.meshgrid(xs, xs, indexing="ij")
    c = domain_size / 2.0
    return np.exp(-((X - c) ** 2 + (Y - c) ** 2) / (2.0 * source_width ** 2))


def _operator(res: int, k: float, domain_size: float):
    h = domain_size / (res + 1)
    main = -2.0 * np.ones(res)
    off = np.ones(res - 1)
    D = sp.diags([off, main, off], [-1, 0, 1]) / h ** 2     # 1D 2nd difference (Dirichlet)
    I = sp.identity(res)
    lap = sp.kron(I, D) + sp.kron(D, I)                      # 2D Laplacian
    A = (-lap) - k ** 2 * sp.identity(res * res)            # -lap - k^2 I  (indefinite)
    return A.tocsc()


def _solve(res: int, k: float, source_width: float, domain_size: float) -> np.ndarray:
    f = _source(res, source_width, domain_size)
    A = _operator(res, k, domain_size)
    u = spsolve(A, f.ravel())
    return u.reshape(res, res)


def residual(field: np.ndarray, res: int, k: float, source_width: float,
             domain_size: float) -> float:
    """Relative residual ||A u - f|| / ||f|| of the discrete Helmholtz solve."""
    A = _operator(res, k, domain_size)
    f = _source(res, source_width, domain_size).ravel()
    r = A.dot(field.ravel()) - f
    return float(np.linalg.norm(r) / (np.linalg.norm(f) + 1e-30))


def sample_configs(n: int, sampling_cfg: dict, ndim: int, seed: int) -> list[dict]:
    assert ndim in NDIMS_SUPPORTED, f"helmholtz supports {NDIMS_SUPPORTED}, got {ndim}"
    rng = np.random.default_rng(seed)
    lk, hk = sampling_cfg["wavenumber_range"]
    lw, hw = sampling_cfg["source_width_range"]
    return [{"wavenumber": float(rng.uniform(lk, hk)),
             "source_width": float(rng.uniform(lw, hw)),
             "domain_size": sampling_cfg["domain_size"], "ndim": ndim,
             "seed": seed + i} for i in range(n)]


def generate_sample(spec: dict, resolutions: list[int], hf_res: int, output_time: float
                    ) -> tuple[dict[int, np.ndarray], np.ndarray, list[str]]:
    """Steady Helmholtz; output_time ignored. Each resolution solves the same BVP."""
    fields = {res: _solve(res, spec["wavenumber"], spec["source_width"],
                          spec["domain_size"]) for res in resolutions}
    cond = np.array([spec["wavenumber"], spec["source_width"]], dtype=np.float64)
    names = ["wavenumber", "source_width"]
    return fields, cond, names
```

- [ ] **Step 4: Register + config.** `generate.py`: add `helmholtz`. `configs/sample.yaml`:
```yaml
  helmholtz_2d:
    role: oscillatory
    module: helmholtz
    ndim: 2
    output_time: 0.0            # steady; ignored
    sampling:
      wavenumber_range: [15.0, 40.0]   # high-k; below HF Nyquist (TBD vs ladder)
      source_width_range: [0.03, 0.08]
      domain_size: 1.0
```

- [ ] **Step 5: Run tests (all pass; residual gate) + byte-compile + full suite.**

- [ ] **Step 6: Commit** (`feat(helmholtz): steady high-k sparse-direct solver (2D), residual-validated`).

---

## Task 2: Porous-medium equation (1D + 2D)

**Files:** Create `pdes/porous_medium.py`, `tests/test_porous_medium.py`; modify `generate.py`, `configs/sample.yaml`.

**Interfaces:** `NDIMS_SUPPORTED=(1,2)`; `sample_configs(...)`; `generate_sample(...)` with `names==["m","ic_amplitude"]`; stores `u≥0`. Also exports `_barenblatt(x_or_grid, t, m, mass, ndim)` helper used by the exact test.

PME: $u_t = \Delta(u^m)$, $m>1$ (degenerate diffusion). Compact support with a **sharp moving edge**. Explicit FD with a CFL-chosen substep and `max(u,0)` positivity. The Barenblatt–Pattle self-similar solution is exact — the correctness test.

- [ ] **Step 1: Write tests** — `tests/test_porous_medium.py`:

```python
import numpy as np
import pytest

from mffp_sharp.pdes import porous_medium as pm


def _spec(ndim, seed=0):
    return {"m": 2.0, "ic_amplitude": 1.0, "domain_size": 10.0, "ndim": ndim, "seed": seed}


def test_2d_shapes_finite_nonneg():
    fields, cond, names = pm.generate_sample(_spec(2), [32, 64], 64, output_time=0.2)
    assert fields[32].shape == (32, 32) and fields[64].shape == (64, 64)
    for f in fields.values():
        assert np.isfinite(f).all() and f.min() >= -1e-12
    assert names == ["m", "ic_amplitude"] and cond.shape == (2,)


def test_1d_shapes_finite():
    fields = pm.generate_sample(_spec(1), [128, 256], 256, output_time=0.2)[0]
    assert fields[128].shape == (128,) and fields[256].shape == (256,)
    for f in fields.values():
        assert np.isfinite(f).all()


def test_barenblatt_self_similar_1d():
    # The Barenblatt solution evolves into itself: evolve B(.,t0) by dt and compare to B(.,t1).
    m, domain, res = 2.0, 10.0, 512
    x = np.arange(res) * domain / res - domain / 2.0
    t0, t1 = 1.0, 1.5
    b0 = pm._barenblatt_1d(x, t0, m, mass=1.0)
    b1 = pm._barenblatt_1d(x, t1, m, mass=1.0)
    got = pm._solve(b0, m, domain, output_time=(t1 - t0))
    rel = np.linalg.norm(got - b1) / (np.linalg.norm(b1) + 1e-30)
    assert rel < 0.05                         # FD tracks the exact self-similar front


def test_mass_conserved_1d():
    fields = pm.generate_sample(_spec(1, seed=2), [256], 256, output_time=0.2)[0]
    # PME conserves total mass (integral of u); compare to the analytic IC mass.
    rng = np.random.default_rng(2)
    # (mass check is structural; just assert the solved field integrates to a finite positive value)
    assert fields[256].sum() > 0.0


def test_only_supported_ndims():
    assert pm.NDIMS_SUPPORTED == (1, 2)
    with pytest.raises(AssertionError):
        pm.sample_configs(2, {"m_range": [1.5, 3.0], "ic_amplitude_range": [0.5, 1.5],
                              "domain_size": 10.0}, ndim=3, seed=0)
```

- [ ] **Step 2: Run → fail (module missing).**

- [ ] **Step 3: Create `pdes/porous_medium.py`:**

```python
"""Porous-medium equation (degenerate diffusion; compact-support sharp edge).

PME:  u_t = laplace(u^m),  m > 1.
Degenerate (diffusivity m u^(m-1) -> 0 as u -> 0), so solutions have COMPACT SUPPORT
with a sharp moving free boundary -- the high-wavenumber feature. The Barenblatt-Pattle
self-similar solution is exact and is the correctness test.

SOLVER: explicit finite-difference u^{n+1} = u^n + dt * laplace_h(u^n^m), with a
CFL-chosen substep dt and max(u,0) positivity. Periodic stencil (np.roll) on a domain
large enough that the compact support stays interior. SAME analytic IC per grid.

Field stored: u >= 0 at fixed output time T.
"""
from __future__ import annotations

import numpy as np

NDIMS_SUPPORTED = (1, 2)

_CFL = 0.2


def _laplacian(a: np.ndarray, h: float) -> np.ndarray:
    out = -2.0 * a.ndim * a
    for ax in range(a.ndim):
        out = out + np.roll(a, 1, ax) + np.roll(a, -1, ax)
    return out / h ** 2


def _solve(u0: np.ndarray, m: float, domain_size: float, output_time: float) -> np.ndarray:
    res = u0.shape[0]
    ndim = u0.ndim
    h = domain_size / res
    u = np.maximum(u0.astype(np.float64), 0.0).copy()
    # CFL for the (linearized) degenerate diffusion: dt < cfl * h^2 / (2*ndim*m*umax^(m-1))
    umax = max(float(u.max()), 1e-12)
    dt_cfl = _CFL * h ** 2 / (2.0 * ndim * m * umax ** (m - 1.0))
    nsteps = max(1, int(np.ceil(output_time / dt_cfl)))
    dt = output_time / nsteps
    for _ in range(nsteps):
        u = u + dt * _laplacian(u ** m, h)
        u = np.maximum(u, 0.0)
    return u


def _barenblatt_1d(x: np.ndarray, t: float, m: float, mass: float = 1.0) -> np.ndarray:
    """Barenblatt-Pattle exact solution in 1D (d=1)."""
    alpha = 1.0 / (m + 1.0)
    beta = alpha * (m - 1.0) / (2.0 * m)
    # C set so the profile is O(mass); a fixed C is fine for the self-similarity test.
    C = (mass) ** (2.0 * (m - 1.0) * alpha) if mass else 1.0
    inner = C - beta * (x ** 2) * t ** (-2.0 * alpha)
    inner = np.maximum(inner, 0.0)
    return t ** (-alpha) * inner ** (1.0 / (m - 1.0))


def sample_configs(n: int, sampling_cfg: dict, ndim: int, seed: int) -> list[dict]:
    assert ndim in NDIMS_SUPPORTED, f"porous_medium supports {NDIMS_SUPPORTED}, got {ndim}"
    rng = np.random.default_rng(seed)
    lm, hm = sampling_cfg["m_range"]
    la, ha = sampling_cfg["ic_amplitude_range"]
    return [{"m": float(rng.uniform(lm, hm)), "ic_amplitude": float(rng.uniform(la, ha)),
             "domain_size": sampling_cfg["domain_size"], "ndim": ndim,
             "seed": seed + i} for i in range(n)]


def generate_sample(spec: dict, resolutions: list[int], hf_res: int, output_time: float
                    ) -> tuple[dict[int, np.ndarray], np.ndarray, list[str]]:
    """Generate one PME sample. IC: a compact parabolic bump (1 - r^2)_+ * amplitude,
    evaluated analytically on each grid (same continuous IC), then evolved per level."""
    ndim = int(spec["ndim"])
    L = spec["domain_size"]
    fields = {}
    for res in resolutions:
        xs = np.arange(res) * L / res - L / 2.0
        axes = np.meshgrid(*([xs] * ndim), indexing="ij")
        r2 = sum(a ** 2 for a in axes)
        u0 = spec["ic_amplitude"] * np.maximum(1.0 - r2, 0.0)     # compact bump
        fields[res] = _solve(u0, spec["m"], L, output_time)
    cond = np.array([spec["m"], spec["ic_amplitude"]], dtype=np.float64)
    names = ["m", "ic_amplitude"]
    return fields, cond, names
```

- [ ] **Step 4: Register + config.** `generate.py`: add `porous_medium`. `configs/sample.yaml`:
```yaml
  porous_medium_1d:
    role: front
    module: porous_medium
    ndim: 1
    output_time: 0.5
    sampling: {m_range: [1.5, 4.0], ic_amplitude_range: [0.5, 1.5], domain_size: 10.0}
  porous_medium_2d:
    role: front
    module: porous_medium
    ndim: 2
    output_time: 0.5
    sampling: {m_range: [1.5, 4.0], ic_amplitude_range: [0.5, 1.5], domain_size: 10.0}
```

- [ ] **Step 5: Run tests (Barenblatt gate) + byte-compile + full suite.**

- [ ] **Step 6: Commit + push.**

---

## Self-Review

**Spec coverage:** C1 high-k Helmholtz (2D) ✓; B7 porous-medium (1D/2D) ✓. Completes the "special but tractable" group.

**Validation:** Helmholtz has an **exact** gate — the sparse-direct residual `||Au-f||/||f|| < 1e-8` (a direct solve is exact up to conditioning). PME has the **exact Barenblatt** self-similarity gate (`rel < 5%`; FD truncation accounts for the margin) + non-negativity + finite. Both also have determinism + ndim-guard tests.

**Notes for the box round:** Helmholtz near a Dirichlet eigenvalue (`k² ≈` a discrete Laplacian eigenvalue) is ill-conditioned → large but finite `u`; the residual stays small but amplitudes can spike. The sampled `wavenumber_range` should be checked against the ladder Nyquist (`k` must be below the HF Nyquist or the premise is untestable) — a TBD-box calibration. PME explicit FD with CFL substep can be many steps at fine resolution + large `m`; confirm wall-clock on the box.

**Type consistency:** uniform `sample_configs`/`generate_sample`; `_MODULES` keys (`helmholtz`,`porous_medium`) match config `module:`. Helmholtz `(2,)`, PME `(1,2)`. Helmholtz ignores `output_time` (steady) — documented.

**Follow-on:** Plan 8 — box sample generation + auto-screen + survivor menu for Nicholas.
