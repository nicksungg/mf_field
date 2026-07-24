# Distinct-Paradigm Spectral Solvers (sine-Gordon, Gray–Scott, PFC) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the last three spectral build-set solvers, each of which breaks the single-real-scalar semi-implicit template in its own way: **sine-Gordon** (2nd-order in *time* — a wave equation), **Gray–Scott** (a coupled 2-field reaction-diffusion system), and **phase-field crystal / PFC** (a conserved, stiff 6th-order equation).

**Architecture:** All Fourier pseudospectral on periodic domains, fed the coarse-IC-spectrally-interpolated-up consistency recipe (LF = real coarse solve, never downsampled HF). Schemes: sine-Gordon uses **Strang kick–wave–kick** (the linear Klein–Gordon part propagated *exactly* in Fourier, the nonlinear remainder applied as velocity kicks); Gray–Scott uses **semi-implicit IMEX** (implicit diffusion per field, explicit reaction) on the 2-component state, storing the activator field; PFC uses **semi-implicit** treatment of its 6th-order linear operator with explicit cubic. Each solver carries the strongest correctness test its physics admits — an exact analytic check where one exists, an exact conserved/monotone invariant otherwise — plus a finiteness test at the config's harshest parameters (the Plan-3 lesson).

**Tech Stack:** Python 3.9, NumPy (`fftn`/`ifftn`, `fft2`/`ifft2`), SciPy (`qmc`), h5py, matplotlib. Tests via pytest; pure-numpy, runs locally.

## Global Constraints

(copied verbatim from the spec / CLAUDE.md):

- **LF = a real coarse *consistent* solve from the same continuous IC; NEVER downsampled or noised HF.** Each solver builds a coarse IC, `spectral_interp`s it up per ladder resolution, and `_solve`s independently.
- **Same solver, same dt, same continuous IC at every fidelity — only the grid changes.**
- **Condition vector complete and small** (≤ ~10 scalars; solver + vector + snapshot T fully determine the stored field — the IC realization is carried by the LF field input, as for the existing solvers).
- **Solver correctness must be validated, not assumed.** Each solver has (1) an exact check (sine-Gordon: small-amplitude Klein–Gordon dispersion `ω=√(k²+m²)`; Gray–Scott: the trivial fixed point `u≡1,v≡0` stays fixed; PFC: mass `∫ψ` conserved under the `∇²` dynamics) **and** (2) a finiteness test at the config's harshest sampled parameters. A scheme that NaNs at its own config range, or fails its exact check, is a defect — BLOCK and fix the scheme; do not loosen the test.
- **Do NOT change** the numerics of any existing validated solver.
- **Heavy/full generation runs on the box only.** This plan is light: small grids + short T locally. Physics validation (sharpness, bottom-rung, whether the chosen `(F,k)`/`r` regimes pattern as intended) is deferred to the box sample round; provisional params flagged `(TBD-box)`.
- **Python 3.9 compatible**; every module keeps `from __future__ import annotations`.
- **Dependencies limited to** numpy, scipy, h5py, scikit-image, matplotlib, pyyaml (+ pytest test-only).
- **Plugin contract (uniform):** `NDIMS_SUPPORTED`, `sample_configs(n, sampling_cfg, ndim, seed) -> list[spec]`, `generate_sample(spec, resolutions, hf_res, output_time) -> ({res: field}, cond_vec, names)`. Registered in `generate._MODULES`; config block per dataset with `module:` + `ndim:`.
- **Git discipline:** feature branch `feat/distinct-spectral`; commit after each task; messages end with `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`. Prefix every python/pytest command with `source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate &&`.

**Depends on:** Plans 1–4 (merged): `common/spectral.py` (`spectral_interp`, `neg_laplacian_symbol`), the plugin registry, dimension-agnostic `common/`.

---

## File Structure

| File | Action |
|---|---|
| `mffp_sharp/src/mffp_sharp/pdes/sine_gordon.py` | **Create** (1D+2D, Strang kick–wave–kick) |
| `mffp_sharp/src/mffp_sharp/pdes/gray_scott.py` | **Create** (2D, coupled IMEX; stores activator `v`) |
| `mffp_sharp/src/mffp_sharp/pdes/phase_field_crystal.py` | **Create** (2D, semi-implicit 6th-order) |
| `mffp_sharp/src/mffp_sharp/generate.py` | **Modify** — register the three modules |
| `mffp_sharp/configs/sample.yaml` | **Modify** — add `sine_gordon_1d/2d`, `gray_scott_2d`, `phase_field_crystal_2d` blocks |
| `mffp_sharp/tests/` | **Create** `test_sine_gordon.py`, `test_gray_scott.py`, `test_phase_field_crystal.py` |

---

## Task 1: sine-Gordon solver (1D + 2D, Strang kick–wave–kick)

**Files:**
- Create: `mffp_sharp/src/mffp_sharp/pdes/sine_gordon.py`
- Modify: `mffp_sharp/src/mffp_sharp/generate.py` (register `sine_gordon`)
- Modify: `mffp_sharp/configs/sample.yaml` (add `sine_gordon_1d/2d`)
- Test: `mffp_sharp/tests/test_sine_gordon.py`

**Interfaces:**
- Consumes: `common.spectral.spectral_interp`, `common.sampling.latin_hypercube`.
- Produces: `NDIMS_SUPPORTED = (1, 2)`; `sample_configs(n, sampling_cfg, ndim, seed)`; `generate_sample(...)` with `names == ["m", "ic_amplitude"]`; `_solve(u0, m, domain_size, output_time, dt) -> np.ndarray` (returns `u` at T; starts from rest `u_t=0`).

sine-Gordon: $u_{tt} = \nabla^2 u - m^2 \sin u$. Split into the linear Klein–Gordon part $u_{tt}=\nabla^2 u - m^2 u$ (propagated **exactly** in Fourier with $\omega=\sqrt{k^2+m^2}$) and the nonlinear remainder $u_{tt} = -m^2(\sin u - u)$ (velocity kick). Strang: half-kick, full wave step, half-kick. In the small-amplitude limit the kick vanishes and the scheme reduces to the exact Klein–Gordon propagator — the correctness test.

- [ ] **Step 1: Write the failing tests**

Create `mffp_sharp/tests/test_sine_gordon.py`:

```python
import numpy as np

from mffp_sharp.pdes import sine_gordon as sg


def _spec(ndim, seed=0):
    return {"m": 1.0, "ic_amplitude": 0.1, "domain_size": 40.0, "ndim": ndim, "seed": seed}


def test_2d_shapes_finite():
    fields, cond, names = sg.generate_sample(_spec(2), [16, 32], 32, output_time=1.0)
    assert fields[16].shape == (16, 16) and fields[32].shape == (32, 32)
    for f in fields.values():
        assert np.isfinite(f).all()
    assert names == ["m", "ic_amplitude"] and cond.shape == (2,)


def test_1d_shapes_finite():
    fields = sg.generate_sample(_spec(1), [64, 128], 128, output_time=1.0)[0]
    assert fields[64].shape == (64,) and fields[128].shape == (128,)
    for f in fields.values():
        assert np.isfinite(f).all()


def test_small_amplitude_klein_gordon_dispersion():
    # Small amplitude -> nonlinearity negligible -> exact standing wave at omega=sqrt(k0^2+m^2):
    #   u(x,t) = A cos(k0 x) cos(omega t),  starting from rest.
    res, domain, m, A = 256, 40.0, 0.5, 1e-3
    x = np.arange(res) * domain / res
    n0 = 4                                   # integer mode index on the periodic domain
    k0 = 2 * np.pi * n0 / domain
    omega = np.sqrt(k0 ** 2 + m ** 2)
    T = 1.0
    u0 = A * np.cos(k0 * x)
    got = sg._solve(u0, m, domain, output_time=T)
    ref = A * np.cos(k0 * x) * np.cos(omega * T)
    assert np.max(np.abs(got - ref)) < 1e-2 * A     # relative to amplitude


def test_energy_conserved():
    # sine-Gordon conserves E = integral[ 1/2 u_t^2 + 1/2 |grad u|^2 + m^2 (1 - cos u) ].
    # We start from rest; check E(T) ~ E(0) via the solver's energy helper.
    res, domain, m = 256, 40.0, 1.0
    rng = np.random.default_rng(0)
    u0 = 0.3 * (2 * rng.random(res) - 1)
    e0 = sg._energy(u0, np.zeros_like(u0), m, domain)
    uT, vT = sg._solve_with_velocity(u0, m, domain, output_time=2.0)
    eT = sg._energy(uT, vT, m, domain)
    assert abs(eT - e0) < 1e-2 * abs(e0)


def test_stable_at_harshest_config_range():
    fields = sg.generate_sample(
        {"m": 2.0, "ic_amplitude": 1.0, "domain_size": 40.0, "ndim": 1, "seed": 3},
        [64, 128], 128, output_time=2.0)[0]
    for f in fields.values():
        assert np.isfinite(f).all() and np.abs(f).max() < 1e3


def test_only_supported_ndims():
    assert sg.NDIMS_SUPPORTED == (1, 2)
    import pytest
    with pytest.raises(AssertionError):
        sg.sample_configs(2, {"m_range": [0.5, 2.0], "ic_amplitude_range": [0.1, 1.0],
                              "domain_size": 40.0}, ndim=3, seed=0)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate && cd /Users/nicholassung/Documents/SURF_2026/mffp_sharp && python -m pytest tests/test_sine_gordon.py -q`
Expected: FAIL — module doesn't exist.

- [ ] **Step 3: Create `pdes/sine_gordon.py`**

```python
"""sine-Gordon (kinks + breathers; dispersive, 2nd-order in TIME) dataset generation.

sine-Gordon:  u_tt = laplace(u) - m^2 sin(u).
A nonlinear wave equation (second order in time) supporting kinks and breathers;
high-wavenumber content from steep kink fronts / breather oscillations. Distinct from
the parabolic/dispersive first-order solvers. 1D+2D.

SOLVER: Strang split-step on the (u, u_t) state ('kick-wave-kick'):
  - the LINEAR Klein-Gordon part u_tt = laplace(u) - m^2 u is propagated EXACTLY in
    Fourier with omega = sqrt(k^2 + m^2):
        u_hat(t) = u_hat cos(wt) + v_hat sin(wt)/w,
        v_hat(t) = -u_hat w sin(wt) + v_hat cos(wt)       (w-> dt limit at k=0,m=0);
  - the NONLINEAR remainder u_tt = -m^2 (sin u - u) is applied as a half velocity kick
    on each side. In the small-amplitude limit the kick vanishes -> exact Klein-Gordon.
np.fft.fftn/ifftn serve 1D and 2D. Starts from rest (u_t=0). Energy is conserved.

IC: band-limited random field on the coarsest grid, spectrally interpolated up ->
identical continuous IC per level. Field stored: u at fixed output time T.
"""
from __future__ import annotations

import numpy as np

from ..common.spectral import spectral_interp
from ..common.sampling import latin_hypercube

NDIMS_SUPPORTED = (1, 2)

# Fixed timestep, same at every resolution. (TBD-box.)
_DT = 5.0e-3


def _omega(res: int, domain_size: float, m: float, ndim: int) -> np.ndarray:
    k1 = 2 * np.pi * np.fft.fftfreq(res, d=domain_size / res)
    k_axes = np.meshgrid(*([k1] * ndim), indexing="ij")
    k2 = sum(kk ** 2 for kk in k_axes)
    return np.sqrt(k2 + m ** 2)


def _step_arrays(omega: np.ndarray, dt: float):
    cwt = np.cos(omega * dt)
    swt = np.sin(omega * dt)
    sinc = np.where(omega > 0, swt / np.where(omega > 0, omega, 1.0), dt)  # sin(wt)/w
    return cwt, swt, sinc


def _solve_with_velocity(u0: np.ndarray, m: float, domain_size: float,
                         output_time: float, dt: float = _DT):
    """Strang kick-wave-kick; return (u, v=u_t) at T. Starts from rest."""
    res = u0.shape[0]
    ndim = u0.ndim
    omega = _omega(res, domain_size, m, ndim)
    nsteps = int(np.ceil(output_time / dt))
    dt = output_time / nsteps
    cwt, swt, sinc = _step_arrays(omega, dt)
    u = u0.astype(np.float64).copy()
    v = np.zeros_like(u)
    for _ in range(nsteps):
        v = v - m ** 2 * (np.sin(u) - u) * (dt / 2.0)          # half kick
        uh = np.fft.fftn(u); vh = np.fft.fftn(v)               # full linear wave step
        uh_new = uh * cwt + vh * sinc
        vh_new = -uh * omega * swt + vh * cwt
        u = np.real(np.fft.ifftn(uh_new)); v = np.real(np.fft.ifftn(vh_new))
        v = v - m ** 2 * (np.sin(u) - u) * (dt / 2.0)          # half kick
    return u, v


def _solve(u0: np.ndarray, m: float, domain_size: float, output_time: float,
           dt: float = _DT) -> np.ndarray:
    """Return u at T (drops the velocity)."""
    return _solve_with_velocity(u0, m, domain_size, output_time, dt)[0]


def _energy(u: np.ndarray, v: np.ndarray, m: float, domain_size: float) -> float:
    """E = mean[ 1/2 v^2 + 1/2 |grad u|^2 + m^2 (1 - cos u) ] (per-cell, domain-normalized)."""
    res = u.shape[0]
    ndim = u.ndim
    k1 = 2 * np.pi * np.fft.fftfreq(res, d=domain_size / res)
    k_axes = np.meshgrid(*([k1] * ndim), indexing="ij")
    uh = np.fft.fftn(u)
    grad2 = np.zeros_like(u)
    for kk in k_axes:
        grad2 = grad2 + np.real(np.fft.ifftn(1j * kk * uh)) ** 2
    dens = 0.5 * v ** 2 + 0.5 * grad2 + m ** 2 * (1.0 - np.cos(u))
    return float(dens.mean())


def sample_configs(n: int, sampling_cfg: dict, ndim: int, seed: int) -> list[dict]:
    """Draw n sine-Gordon condition specs (Latin-hypercube over m / ic_amplitude)."""
    assert ndim in NDIMS_SUPPORTED, f"sine_gordon supports {NDIMS_SUPPORTED}, got {ndim}"
    draws = latin_hypercube(
        {"m": tuple(sampling_cfg["m_range"]),
         "ic_amplitude": tuple(sampling_cfg["ic_amplitude_range"])}, n, seed)
    return [{"m": draws["m"][i], "ic_amplitude": draws["ic_amplitude"][i],
             "domain_size": sampling_cfg["domain_size"], "ndim": ndim,
             "seed": seed + i} for i in range(n)]


def generate_sample(spec: dict, resolutions: list[int], hf_res: int, output_time: float
                    ) -> tuple[dict[int, np.ndarray], np.ndarray, list[str]]:
    """Generate one sine-Gordon sample across the fidelity ladder (1D or 2D)."""
    ndim = int(spec["ndim"])
    res_min = min(resolutions)
    rng = np.random.default_rng(spec["seed"])
    ic_coarse = spec["ic_amplitude"] * (2 * rng.random((res_min,) * ndim) - 1)
    fields = {
        res: _solve(spectral_interp(ic_coarse, res), spec["m"], spec["domain_size"],
                    output_time)
        for res in resolutions
    }
    cond = np.array([spec["m"], spec["ic_amplitude"]], dtype=np.float64)
    names = ["m", "ic_amplitude"]
    return fields, cond, names
```

- [ ] **Step 4: Register + add config blocks**

In `generate.py`, add to the `from .pdes import ...` line and `_MODULES`:
```python
    "sine_gordon": sine_gordon,
```
(add `sine_gordon` to the import list too). In `configs/sample.yaml`, add under `pdes:`:
```yaml
  sine_gordon_2d:
    role: dispersive
    module: sine_gordon
    ndim: 2
    output_time: 5.0            # T (TBD-box)
    sampling:
      m_range: [0.5, 2.0]
      ic_amplitude_range: [0.3, 1.5]
      domain_size: 40.0
  sine_gordon_1d:
    role: dispersive
    module: sine_gordon
    ndim: 1
    output_time: 5.0
    sampling:
      m_range: [0.5, 2.0]
      ic_amplitude_range: [0.3, 1.5]
      domain_size: 40.0
```

- [ ] **Step 5: Run tests; byte-compile; full suite**

Run: `source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate && cd /Users/nicholassung/Documents/SURF_2026/mffp_sharp && python -m pytest tests/test_sine_gordon.py -q`
Expected: all 6 PASS — especially `test_small_amplitude_klein_gordon_dispersion` (wave propagator correct) and `test_energy_conserved` (full Strang scheme correct).

Run: `source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate && cd /Users/nicholassung/Documents/SURF_2026/mffp_sharp && python -m compileall src/mffp_sharp -q && echo OK && python -m pytest tests/ -q`
Expected: `OK`; full suite PASS.

- [ ] **Step 6: Commit**

```bash
cd /Users/nicholassung/Documents/SURF_2026
git add mffp_sharp/src/mffp_sharp/pdes/sine_gordon.py mffp_sharp/src/mffp_sharp/generate.py mffp_sharp/configs/sample.yaml mffp_sharp/tests/test_sine_gordon.py
git commit -m "feat(sine_gordon): Strang kick-wave-kick solver (1D+2D), dispersion- and energy-validated

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 2: Gray–Scott solver (2D, coupled IMEX)

**Files:**
- Create: `mffp_sharp/src/mffp_sharp/pdes/gray_scott.py`
- Modify: `mffp_sharp/src/mffp_sharp/generate.py` (register `gray_scott`)
- Modify: `mffp_sharp/configs/sample.yaml` (add `gray_scott_2d`)
- Test: `mffp_sharp/tests/test_gray_scott.py`

**Interfaces:**
- Consumes: `common.spectral.spectral_interp`, `common.spectral.neg_laplacian_symbol`, `common.sampling.latin_hypercube`.
- Produces: `NDIMS_SUPPORTED = (2,)`; `sample_configs(n, sampling_cfg, ndim, seed)`; `generate_sample(...)` with `names == ["F", "k_rate"]`; the stored field is the **activator** `v`. `_solve(u0, v0, Du, Dv, F, k_rate, domain_size, output_time, dt) -> (u, v)`.

Gray–Scott: $u_t = D_u\nabla^2 u - uv^2 + F(1-u)$, $v_t = D_v\nabla^2 v + uv^2 - (F+k)v$. Coupled reaction-diffusion producing spots/stripes/worms (The Well's 6 Pearson regimes). Semi-implicit IMEX per field: implicit diffusion via the discrete −Laplacian symbol (`denom = 1/dt + D·mlap`), explicit reaction. The uniform state $u\equiv1, v\equiv0$ is an exact fixed point — the correctness test.

- [ ] **Step 1: Write the failing tests**

Create `mffp_sharp/tests/test_gray_scott.py`:

```python
import numpy as np

from mffp_sharp.pdes import gray_scott as gs


def _spec(seed=0):
    return {"F": 0.029, "k_rate": 0.057, "Du": 2e-5, "Dv": 1e-5,
            "domain_size": 2.0, "ndim": 2, "seed": seed}


def test_shapes_finite():
    fields, cond, names = gs.generate_sample(_spec(), [32, 64], 64, output_time=10.0)
    assert fields[32].shape == (32, 32) and fields[64].shape == (64, 64)
    for f in fields.values():
        assert np.isfinite(f).all()
    assert names == ["F", "k_rate"] and cond.shape == (2,)


def test_trivial_fixed_point_stays_fixed():
    # u == 1, v == 0 everywhere is an exact steady state: reactions vanish, nothing moves.
    res = 64
    u0 = np.ones((res, res)); v0 = np.zeros((res, res))
    u, v = gs._solve(u0, v0, 2e-5, 1e-5, F=0.029, k_rate=0.057,
                     domain_size=2.0, output_time=50.0)
    assert np.max(np.abs(u - 1.0)) < 1e-8
    assert np.max(np.abs(v)) < 1e-8


def test_deterministic():
    a = gs.generate_sample(_spec(seed=2), [64], 64, 10.0)[0][64]
    b = gs.generate_sample(_spec(seed=2), [64], 64, 10.0)[0][64]
    assert np.array_equal(a, b)


def test_stable_at_config_range():
    # A representative Pearson regime over a longer time must stay finite & bounded in [0,1.5].
    fields = gs.generate_sample(
        {"F": 0.058, "k_rate": 0.065, "Du": 2e-5, "Dv": 1e-5,
         "domain_size": 2.0, "ndim": 2, "seed": 4}, [32, 64], 64, output_time=50.0)[0]
    for f in fields.values():
        assert np.isfinite(f).all() and f.min() >= -1e-6 and f.max() < 1.5


def test_only_2d_supported():
    assert gs.NDIMS_SUPPORTED == (2,)
    import pytest
    with pytest.raises(AssertionError):
        gs.sample_configs(2, {"F_range": [0.02, 0.06], "k_rate_range": [0.05, 0.07],
                              "Du": 2e-5, "Dv": 1e-5, "domain_size": 2.0}, ndim=1, seed=0)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate && cd /Users/nicholassung/Documents/SURF_2026/mffp_sharp && python -m pytest tests/test_gray_scott.py -q`
Expected: FAIL — module doesn't exist.

- [ ] **Step 3: Create `pdes/gray_scott.py`**

```python
"""Gray-Scott (coupled reaction-diffusion; many sharp spots/stripes) dataset generation.

Gray-Scott:  u_t = Du laplace(u) - u v^2 + F (1 - u)
             v_t = Dv laplace(v) + u v^2 - (F + k) v.
A coupled 2-field system whose self-replicating spots / worms / stripes carry sharp
high-wavenumber structure (The Well's 6 canonical Pearson (F,k) regimes). Distinct
mechanism: multi-front pattern formation. 2D. The stored field is the ACTIVATOR v.

SOLVER: semi-implicit IMEX (same family as Allen-Cahn / Fisher-KPP, on a 2-field state):
  - implicit diffusion per field via the discrete -Laplacian symbol (bounded ->
    consistent coarse solve): denom_u = 1/dt + Du*mlap, denom_v = 1/dt + Dv*mlap;
  - explicit reaction (-u v^2 + F(1-u)) and (u v^2 - (F+k) v);
  - fresh FFT each step. SAME dt at every resolution.

IC (The Well style): u=1, v=0 background with a central perturbed square (u=0.5, v=0.25)
plus small noise, built on the coarsest grid and spectrally interpolated up so every
ladder level seeds the SAME continuous IC. Field stored: v at fixed output time T.
"""
from __future__ import annotations

import numpy as np

from ..common.spectral import spectral_interp, neg_laplacian_symbol
from ..common.sampling import latin_hypercube

NDIMS_SUPPORTED = (2,)

_DT = 1.0  # GS is mild with tiny diffusivities; dt~1 is standard. (TBD-box.)


def _solve(u0: np.ndarray, v0: np.ndarray, Du: float, Dv: float, F: float, k_rate: float,
           domain_size: float, output_time: float, dt: float = _DT):
    """Semi-implicit IMEX Gray-Scott solve from (u0, v0); return (u, v)."""
    res = u0.shape[0]
    h = domain_size / res
    mlap = neg_laplacian_symbol(res, h, 2)
    nsteps = int(np.ceil(output_time / dt))
    dt = output_time / nsteps
    denom_u = 1.0 / dt + Du * mlap
    denom_v = 1.0 / dt + Dv * mlap
    u = u0.astype(np.float64).copy()
    v = v0.astype(np.float64).copy()
    for _ in range(nsteps):
        uvv = u * v * v
        ru = -uvv + F * (1.0 - u)
        rv = uvv - (F + k_rate) * v
        uh = (np.fft.fft2(u) * (1.0 / dt) + np.fft.fft2(ru)) / denom_u
        vh = (np.fft.fft2(v) * (1.0 / dt) + np.fft.fft2(rv)) / denom_v
        u = np.real(np.fft.ifft2(uh))
        v = np.real(np.fft.ifft2(vh))
    return u, v


def sample_configs(n: int, sampling_cfg: dict, ndim: int, seed: int) -> list[dict]:
    """Draw n Gray-Scott condition specs (Latin-hypercube over F / k_rate)."""
    assert ndim in NDIMS_SUPPORTED, f"gray_scott supports {NDIMS_SUPPORTED}, got {ndim}"
    draws = latin_hypercube(
        {"F": tuple(sampling_cfg["F_range"]),
         "k_rate": tuple(sampling_cfg["k_rate_range"])}, n, seed)
    return [{"F": draws["F"][i], "k_rate": draws["k_rate"][i],
             "Du": sampling_cfg["Du"], "Dv": sampling_cfg["Dv"],
             "domain_size": sampling_cfg["domain_size"], "ndim": ndim,
             "seed": seed + i} for i in range(n)]


def generate_sample(spec: dict, resolutions: list[int], hf_res: int, output_time: float
                    ) -> tuple[dict[int, np.ndarray], np.ndarray, list[str]]:
    """Generate one Gray-Scott sample across the fidelity ladder (2D). Stored field = v."""
    res_min = min(resolutions)
    rng = np.random.default_rng(spec["seed"])
    u0c = np.ones((res_min, res_min))
    v0c = np.zeros((res_min, res_min))
    s = max(2, res_min // 8)
    a, b = res_min // 2 - s, res_min // 2 + s
    u0c[a:b, a:b] = 0.5
    v0c[a:b, a:b] = 0.25
    u0c += 0.01 * (2 * rng.random((res_min, res_min)) - 1)
    v0c += 0.01 * (2 * rng.random((res_min, res_min)) - 1)
    fields = {}
    for res in resolutions:
        u0 = spectral_interp(u0c, res)
        v0 = spectral_interp(v0c, res)
        _, v = _solve(u0, v0, spec["Du"], spec["Dv"], spec["F"], spec["k_rate"],
                      spec["domain_size"], output_time)
        fields[res] = v
    cond = np.array([spec["F"], spec["k_rate"]], dtype=np.float64)
    names = ["F", "k_rate"]
    return fields, cond, names
```

- [ ] **Step 4: Register + add config block**

In `generate.py` add `gray_scott` to imports and `_MODULES` (`"gray_scott": gray_scott,`). In `configs/sample.yaml`, add under `pdes:`:
```yaml
  gray_scott_2d:
    role: pattern
    module: gray_scott
    ndim: 2
    output_time: 2000.0         # T: pattern developed (TBD-box; GS evolves slowly)
    sampling:
      F_range: [0.018, 0.058]   # spans Pearson regimes (spots..worms) (TBD)
      k_rate_range: [0.051, 0.065]
      Du: 2.0e-5
      Dv: 1.0e-5
      domain_size: 2.0
```

- [ ] **Step 5: Run tests; byte-compile; full suite**

Run: `source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate && cd /Users/nicholassung/Documents/SURF_2026/mffp_sharp && python -m pytest tests/test_gray_scott.py -q`
Expected: all 5 PASS — especially `test_trivial_fixed_point_stays_fixed` (reaction terms correct).

Run: `source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate && cd /Users/nicholassung/Documents/SURF_2026/mffp_sharp && python -m compileall src/mffp_sharp -q && echo OK && python -m pytest tests/ -q`
Expected: `OK`; full suite PASS.

- [ ] **Step 6: Commit**

```bash
cd /Users/nicholassung/Documents/SURF_2026
git add mffp_sharp/src/mffp_sharp/pdes/gray_scott.py mffp_sharp/src/mffp_sharp/generate.py mffp_sharp/configs/sample.yaml mffp_sharp/tests/test_gray_scott.py
git commit -m "feat(gray_scott): coupled IMEX reaction-diffusion solver (2D), fixed-point-validated

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 3: phase-field crystal (PFC) solver (2D, semi-implicit 6th-order)

**Files:**
- Create: `mffp_sharp/src/mffp_sharp/pdes/phase_field_crystal.py`
- Modify: `mffp_sharp/src/mffp_sharp/generate.py` (register `phase_field_crystal`)
- Modify: `mffp_sharp/configs/sample.yaml` (add `phase_field_crystal_2d`)
- Test: `mffp_sharp/tests/test_phase_field_crystal.py`

**Interfaces:**
- Consumes: `common.spectral.spectral_interp`, `common.sampling.latin_hypercube`.
- Produces: `NDIMS_SUPPORTED = (2,)`; `sample_configs(n, sampling_cfg, ndim, seed)`; `generate_sample(...)` with `names == ["r", "mean_density"]`; `_solve(psi0, r, domain_size, output_time, dt) -> np.ndarray`. **Mass `∫ψ` is conserved** (the `∇²` prefactor leaves the `k=0` mode untouched) — the correctness test.

PFC: $\partial_t \psi = \nabla^2\!\big[(r + (1+\nabla^2)^2)\psi + \psi^3\big]$. Conserved, stiff 6th-order; forms a periodic crystalline lattice (a spectral peak at $|k|=1$). In Fourier the linear symbol is $L(k) = -k^2\big(r + (1-k^2)^2\big)$; semi-implicit: implicit linear (`denom = 1/dt - L = 1/dt + k^2(r+(1-k^2)^2)`), explicit cubic term $\nabla^2(\psi^3) = -k^2\widehat{\psi^3}$, 2/3-rule de-aliased.

- [ ] **Step 1: Write the failing tests**

Create `mffp_sharp/tests/test_phase_field_crystal.py`:

```python
import numpy as np

from mffp_sharp.pdes import phase_field_crystal as pfc


def _spec(seed=0):
    return {"r": -0.25, "mean_density": -0.3, "ic_amplitude": 0.05,
            "domain_size": 32.0, "ndim": 2, "seed": seed}


def test_shapes_finite_bounded():
    fields, cond, names = pfc.generate_sample(_spec(), [32, 64], 64, output_time=5.0)
    assert fields[32].shape == (32, 32) and fields[64].shape == (64, 64)
    for f in fields.values():
        assert np.isfinite(f).all() and np.abs(f).max() < 1e2
    assert names == ["r", "mean_density"] and cond.shape == (2,)


def test_mass_conserved():
    # The leading laplacian makes PFC conservative: the spatial mean is preserved.
    res = 64
    rng = np.random.default_rng(1)
    psi0 = -0.3 + 0.05 * (2 * rng.random((res, res)) - 1)
    out = pfc._solve(psi0, r=-0.25, domain_size=32.0, output_time=5.0)
    assert abs(float(out.mean()) - float(psi0.mean())) < 1e-9


def test_deterministic():
    a = pfc.generate_sample(_spec(seed=2), [64], 64, 5.0)[0][64]
    b = pfc.generate_sample(_spec(seed=2), [64], 64, 5.0)[0][64]
    assert np.array_equal(a, b)


def test_ladder_outputs_spectrally_consistent():
    from mffp_sharp.common.spectral import spectral_interp
    fields = pfc.generate_sample(_spec(seed=4), [32, 64], 64, output_time=1e-6)[0]
    assert np.allclose(spectral_interp(fields[32], 64), fields[64], atol=1e-3)


def test_only_2d_supported():
    assert pfc.NDIMS_SUPPORTED == (2,)
    import pytest
    with pytest.raises(AssertionError):
        pfc.sample_configs(2, {"r_range": [-0.4, -0.1], "mean_density_range": [-0.4, -0.2],
                               "ic_amplitude": 0.05, "domain_size": 32.0}, ndim=1, seed=0)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate && cd /Users/nicholassung/Documents/SURF_2026/mffp_sharp && python -m pytest tests/test_phase_field_crystal.py -q`
Expected: FAIL — module doesn't exist.

- [ ] **Step 3: Create `pdes/phase_field_crystal.py`**

```python
"""Phase-field crystal (PFC; periodic sharp lattice, conserved, stiff 6th order).

PFC:  d psi/dt = laplace[ (r + (1 + laplace)^2) psi + psi^3 ].
A conserved dynamics whose ground state is a crystalline lattice with characteristic
wavenumber |k|=1 -> a spectral PEAK. 6th-order and stiff. Distinct mechanism: periodic
sharp lattice. 2D. Field stored: psi at fixed output time T.

SOLVER: semi-implicit Fourier. In Fourier the linear symbol is
  L(k) = -k^2 (r + (1 - k^2)^2),
treated IMPLICITLY (denom = 1/dt - L), with the cubic term laplace(psi^3) = -k^2 psi3_hat
explicit and 2/3-rule de-aliased; fresh FFT each step. The leading laplacian leaves the
k=0 mode untouched, so the spatial mean (mass) is conserved exactly. SAME dt at every
resolution.

IC: mean_density + small band-limited noise on the coarsest grid, spectrally interpolated
up -> identical continuous IC per level. (Continuous k^2; PFC patterns are smooth/resolved.)
"""
from __future__ import annotations

import numpy as np

from ..common.spectral import spectral_interp
from ..common.sampling import latin_hypercube

NDIMS_SUPPORTED = (2,)

_DT = 0.1  # (TBD-box.)


def _solve(psi0: np.ndarray, r: float, domain_size: float, output_time: float,
           dt: float = _DT) -> np.ndarray:
    """Semi-implicit Fourier PFC solve from psi0 (2D); return psi."""
    res = psi0.shape[0]
    k1 = 2 * np.pi * np.fft.fftfreq(res, d=domain_size / res)
    KX, KY = np.meshgrid(k1, k1, indexing="ij")
    k2 = KX ** 2 + KY ** 2
    Lsym = -k2 * (r + (1.0 - k2) ** 2)                 # linear operator symbol
    fi = np.fft.fftfreq(res) * res
    keep1 = np.abs(fi) <= res / 3.0
    mask = np.logical_and.reduce(np.meshgrid(keep1, keep1, indexing="ij"))
    nsteps = int(np.ceil(output_time / dt))
    dt = output_time / nsteps
    denom = 1.0 / dt - Lsym                             # implicit linear
    psi = psi0.astype(np.float64).copy()
    for _ in range(nsteps):
        ph = np.fft.fft2(psi)
        nlh = -k2 * (np.fft.fft2(psi ** 3) * mask)     # laplace(psi^3) = -k^2 psi3_hat
        ph_new = (ph * (1.0 / dt) + nlh) / denom
        psi = np.real(np.fft.ifft2(ph_new))
    return psi


def sample_configs(n: int, sampling_cfg: dict, ndim: int, seed: int) -> list[dict]:
    """Draw n PFC condition specs (Latin-hypercube over r / mean_density)."""
    assert ndim in NDIMS_SUPPORTED, f"phase_field_crystal supports {NDIMS_SUPPORTED}, got {ndim}"
    draws = latin_hypercube(
        {"r": tuple(sampling_cfg["r_range"]),
         "mean_density": tuple(sampling_cfg["mean_density_range"])}, n, seed)
    return [{"r": draws["r"][i], "mean_density": draws["mean_density"][i],
             "ic_amplitude": sampling_cfg["ic_amplitude"],
             "domain_size": sampling_cfg["domain_size"], "ndim": ndim,
             "seed": seed + i} for i in range(n)]


def generate_sample(spec: dict, resolutions: list[int], hf_res: int, output_time: float
                    ) -> tuple[dict[int, np.ndarray], np.ndarray, list[str]]:
    """Generate one PFC sample across the fidelity ladder (2D)."""
    res_min = min(resolutions)
    rng = np.random.default_rng(spec["seed"])
    ic_coarse = spec["mean_density"] + spec["ic_amplitude"] * (
        2 * rng.random((res_min, res_min)) - 1)
    fields = {
        res: _solve(spectral_interp(ic_coarse, res), spec["r"], spec["domain_size"],
                    output_time)
        for res in resolutions
    }
    cond = np.array([spec["r"], spec["mean_density"]], dtype=np.float64)
    names = ["r", "mean_density"]
    return fields, cond, names
```

- [ ] **Step 4: Register + add config block**

In `generate.py` add `phase_field_crystal` to imports and `_MODULES` (`"phase_field_crystal": phase_field_crystal,`). In `configs/sample.yaml`, add under `pdes:`:
```yaml
  phase_field_crystal_2d:
    role: pattern
    module: phase_field_crystal
    ndim: 2
    output_time: 200.0          # T: lattice developed (TBD-box)
    sampling:
      r_range: [-0.4, -0.1]     # r<0 for patterns (TBD)
      mean_density_range: [-0.4, -0.2]
      ic_amplitude: 0.05
      domain_size: 32.0
```

- [ ] **Step 5: Run tests; byte-compile; full suite**

Run: `source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate && cd /Users/nicholassung/Documents/SURF_2026/mffp_sharp && python -m pytest tests/test_phase_field_crystal.py -q`
Expected: all 5 PASS — especially `test_mass_conserved` (the conservative `∇²` structure).

Run: `source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate && cd /Users/nicholassung/Documents/SURF_2026/mffp_sharp && python -m compileall src/mffp_sharp -q && echo OK && python -m pytest tests/ -q`
Expected: `OK`; full suite PASS.

- [ ] **Step 6: Commit and push**

```bash
cd /Users/nicholassung/Documents/SURF_2026
git add mffp_sharp/src/mffp_sharp/pdes/phase_field_crystal.py mffp_sharp/src/mffp_sharp/generate.py mffp_sharp/configs/sample.yaml mffp_sharp/tests/test_phase_field_crystal.py
git commit -m "feat(pfc): semi-implicit 6th-order phase-field-crystal solver (2D), mass-conserving

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
git push
```

---

## Self-Review

**1. Spec coverage** (build-set, remaining spectral items):
- **C4 sine-Gordon (1D/2D)** → Task 1. ✓
- **B4 Gray–Scott (2D)** → Task 2. ✓
- **B6 phase-field crystal (2D)** → Task 3. ✓
- **This completes the spectral build set.** Remaining build-set items are PyClaw/WENO (box-only) and the special pair — see follow-on.

**2. Placeholder scan:** No "TBD"/"add error handling"/"write tests for the above". Provisional physical params flagged `(TBD-box)`. Every code step complete; every run step has a command + expected output.

**3. Type consistency:** `sample_configs(n, sampling_cfg, ndim, seed)` + `generate_sample(spec, resolutions, hf_res, output_time)` uniform with all modules and the `generate.generate_dataset` caller. `_MODULES` keys (`sine_gordon`, `gray_scott`, `phase_field_crystal`) match config `module:` values. `NDIMS_SUPPORTED`: sine-Gordon `(1,2)`, Gray–Scott `(2,)`, PFC `(2,)` — all guard-tested. sine-Gordon's `_solve`/`_solve_with_velocity`/`_energy`/`_omega`/`_step_arrays` helper names are internal and referenced consistently by the tests.

**Validation strategy (Plan-3 lesson applied, scaled to each PDE's physics):** sine-Gordon gets an **exact** small-amplitude Klein–Gordon dispersion test + an energy-conservation test; Gray–Scott gets an **exact** trivial-fixed-point test (`u≡1,v≡0` stays fixed) + bounded-stability; PFC gets an **exact** mass-conservation test + ladder-IC consistency. Every solver also has a finiteness/boundedness test at the config range. During execution, a failing exact test means the scheme is wrong — BLOCK and fix the scheme, never loosen the test.

**Known design notes for the box round (flag to Nicholas):** Gray–Scott and PFC evolve slowly, so their `output_time` (2000 / 200) implies many steps — confirm wall-clock on the box and tune dt. Gray–Scott stores only the activator `v` (the standard visualized field); if Nicholas wants both `u` and `v` that is an io/2-channel change. PFC and Gray–Scott have no closed-form solution, so the box sample round is where their *physical* sharpness/regime correctness is judged (the local tests only guarantee the scheme integrates the equation faithfully).

**Scope / follow-on:** Plan 6 — PyClaw/WENO (box-only): Burgers, Sod, shallow-water (PDEBench `gen_radial_dam_break`), Buckley–Leverett. Plan 7 — special: high-$k$ Helmholtz (steady sparse solve), porous-medium. Plan 8 — box sample generation + auto-screen (energy-above-cutoff floor + sharpness coordinate $s$ + LF–HF gap) + survivor menu for Nicholas.
