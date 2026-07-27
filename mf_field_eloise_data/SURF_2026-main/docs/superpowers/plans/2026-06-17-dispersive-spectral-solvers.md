# Dispersive Spectral Solvers (KdV via IF-RK4, NLS via split-step) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the two canonical *dispersive* spectral PDE solvers to the build set — Korteweg–de Vries (KdV) and the nonlinear Schrödinger equation (NLS) — each with a numerically robust exponential/split-step scheme and validated against its **exact soliton solution**, not just smoke tests.

**Architecture:** Both are Fourier pseudospectral on a periodic 1D domain, fed the coarse-IC-spectrally-interpolated-up consistency recipe (LF = real coarse solve, never downsampled HF). KdV uses **integrating-factor RK4** (IF-RK4 — the linear dispersion handled exactly via `exp(L·dt)`, RK4 on the nonlinearity; the canonical Trefethen "p27"/`kursiv` scheme). NLS uses **Strang split-step** (linear dispersion exact in Fourier, nonlinear phase rotation exact in real space). NLS's field is complex; we store the real **intensity** `|u|²` (the physically observable, T-determined field that carries the sharp soliton/wavepacket peaks).

**Why this supersedes Plan 3's KdV:** Plan 3 specified integrating-factor *Euler*, which is too weakly stable — it produced NaNs at the config's own sampling range, and the unit tests (a benign T/amplitude subset) masked it. This plan fixes both: IF-RK4 (vastly larger stability region) **and** tests that (a) check the exact soliton solution and (b) assert finiteness at the config's *harshest* parameters.

**Tech Stack:** Python 3.9, NumPy (`fft`/`ifft`, complex arrays), SciPy (`qmc`), h5py, matplotlib. Tests via pytest; pure-numpy, runs locally.

## Global Constraints

These apply to **every** task (copied verbatim from the spec / CLAUDE.md):

- **LF = a real coarse *consistent* solve from the same continuous IC; NEVER downsampled or noised HF.** Each solver builds a coarse IC, `spectral_interp`s it up per ladder resolution, and `_solve`s independently — no decimation/filtering of an HF field.
- **Same solver, same dt, same continuous IC at every fidelity — only the grid changes.**
- **Condition vector complete and small** (≤ ~10 scalars; solver + vector + snapshot T fully determine the stored field).
- **Solver correctness must be validated, not assumed.** Each solver has (1) an exact-soliton test (the scheme must propagate/preserve the known analytic solution) and (2) a finiteness test at the config's harshest sampled parameters. Provisional dt/ranges/T are flagged `(TBD-box)`, but a scheme that NaNs at its own config range is a defect, not a tuning question.
- **Do NOT change** the numerics of any existing validated solver.
- **Heavy/full generation runs on the box only.** This plan is light: tiny grids + short T locally, plus the soliton tests (which use moderate `res=256` but short T — still sub-second).
- **Python 3.9 compatible**; every module keeps `from __future__ import annotations`.
- **Dependencies limited to** numpy, scipy, h5py, scikit-image, matplotlib, pyyaml (+ pytest test-only).
- **Plugin contract (uniform):** `NDIMS_SUPPORTED`, `sample_configs(n, sampling_cfg, ndim, seed) -> list[spec]`, `generate_sample(spec, resolutions, hf_res, output_time) -> ({res: field}, cond_vec, names)`. Registered in `generate._MODULES`; config block per dataset with `module:` + `ndim:`.
- **Git discipline:** executed on feature branch `feat/dispersive-spectral`; commit after each task; messages end with `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`. Prefix every python/pytest command with `source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate &&`.

**Depends on:** Plans 1–3 (merged): `common/spectral.py` (`spectral_interp`), the plugin registry, the dimension-agnostic `common/`.

---

## File Structure

| File | Responsibility | Action |
|---|---|---|
| `mffp_sharp/src/mffp_sharp/pdes/kdv.py` | KdV solver (1D, IF-RK4) | **Create** (Plan 3's IF-Euler version was reverted) |
| `mffp_sharp/src/mffp_sharp/pdes/nls.py` | NLS solver (1D, split-step; stores `|u|²`) | **Create** |
| `mffp_sharp/src/mffp_sharp/generate.py` | registry | **Modify** — register `kdv`, `nls` |
| `mffp_sharp/configs/sample.yaml` | config | **Modify** — add `kdv_1d`, `nls_1d` blocks |
| `mffp_sharp/tests/` | unit tests | **Create** `test_kdv.py`, `test_nls.py` |

---

## Task 1: KdV solver (1D, IF-RK4, soliton-validated)

**Files:**
- Create: `mffp_sharp/src/mffp_sharp/pdes/kdv.py`
- Modify: `mffp_sharp/src/mffp_sharp/generate.py` (register `kdv`)
- Modify: `mffp_sharp/configs/sample.yaml` (add `kdv_1d` block)
- Test: `mffp_sharp/tests/test_kdv.py`

**Interfaces:**
- Consumes: `common.spectral.spectral_interp`, `common.sampling.latin_hypercube`.
- Produces: `NDIMS_SUPPORTED = (1,)`; `sample_configs(n, sampling_cfg, ndim, seed)`; `generate_sample(...)` with `names == ["delta", "ic_amplitude"]`; `_solve(u0, delta, domain_size, output_time, dt) -> np.ndarray` (real). KdV conserves the spatial mean (k=0 mode untouched).

KdV: $\partial_t u + 6\,u\,u_x + \delta^2 u_{xxx} = 0$. Exact 1-soliton $u(x,t) = \tfrac{c}{2}\,\mathrm{sech}^2\!\big(\tfrac{\sqrt c}{2\delta}(x - c t - x_0)\big)$, traveling at speed $c$. In Fourier $\hat u_t = L\hat u + g\cdot\widehat{u^2}$ with linear $L = i\,\delta^2 k^3$ and $g = -3 i k$ (from $-6uu_x = -3(u^2)_x$). IF-RK4 integrates $L$ exactly and applies RK4 to the nonlinearity (`E = e^{L\,dt/2}`, `E2 = e^{L\,dt}`).

- [ ] **Step 1: Write the failing tests** (incl. the exact-soliton + config-range-stability tests)

Create `mffp_sharp/tests/test_kdv.py`:

```python
import numpy as np

from mffp_sharp.pdes import kdv


def _spec(seed=0):
    return {"delta": 0.022, "ic_amplitude": 0.5, "domain_size": 2.0, "ndim": 1, "seed": seed}


def test_shapes_finite():
    fields, cond, names = kdv.generate_sample(_spec(), [64, 128], 128, output_time=0.5)
    assert fields[64].shape == (64,) and fields[128].shape == (128,)
    for f in fields.values():
        assert np.isfinite(f).all()
    assert names == ["delta", "ic_amplitude"] and cond.shape == (2,)


def test_soliton_propagates_at_speed_c():
    # Exact 1-soliton of u_t + 6 u u_x + delta^2 u_xxx = 0:
    #   u = (c/2) sech^2( sqrt(c)/(2 delta) (x - c t - x0) ).
    # Evolve the t=0 profile and compare to the analytic profile at t=T (no wrap).
    res, domain, delta, c, x0, T = 512, 60.0, 1.0, 1.0, 15.0, 4.0
    x = np.arange(res) * domain / res

    def soliton(t):
        xi = np.sqrt(c) / (2 * delta) * (x - c * t - x0)
        return (c / 2.0) / np.cosh(xi) ** 2

    u0 = soliton(0.0)
    got = kdv._solve(u0, delta, domain, output_time=T)
    ref = soliton(T)                       # moved c*T = 4 units, still inside [0, 60]
    assert np.max(np.abs(got - ref)) < 1e-2          # shape + speed both correct
    assert abs(got.max() - c / 2.0) < 2e-2           # amplitude preserved


def test_mass_conserved():
    res = 128
    rng = np.random.default_rng(1)
    ic = 0.5 * (2 * rng.random(res) - 1)             # matches generate_sample's IC build
    got = kdv._solve(ic, delta=0.022, domain_size=2.0, output_time=0.5)
    assert abs(float(got.mean()) - float(ic.mean())) < 1e-9


def test_stable_at_harshest_config_range():
    # The Plan-3 failure mode: must stay finite at the config's worst-case params.
    fields = kdv.generate_sample(
        {"delta": 0.04, "ic_amplitude": 0.7, "domain_size": 2.0, "ndim": 1, "seed": 3},
        [64, 128], 128, output_time=1.0)[0]
    for f in fields.values():
        assert np.isfinite(f).all() and np.abs(f).max() < 1e3


def test_only_1d_supported():
    assert kdv.NDIMS_SUPPORTED == (1,)
    import pytest
    with pytest.raises(AssertionError):
        kdv.sample_configs(2, {"delta_range": [0.02, 0.03],
                               "ic_amplitude_range": [0.4, 0.6], "domain_size": 2.0},
                           ndim=2, seed=0)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate && cd /Users/nicholassung/Documents/SURF_2026/mffp_sharp && python -m pytest tests/test_kdv.py -q`
Expected: FAIL — module `kdv` doesn't exist.

- [ ] **Step 3: Create `pdes/kdv.py`**

```python
"""Korteweg-de Vries (dispersive soliton trains) dataset generation.

KdV:  d u/dt + 6 u u_x + delta^2 u_xxx = 0.
A smooth IC disperses into a train of solitons; the high-wavenumber content comes
from the narrow soliton peaks (dispersion, not jumps). Tagged 'distinct (dispersion)'.
1D only (2D KP-II deferred).

SOLVER: integrating-factor RK4 (IF-RK4), the canonical Trefethen 'p27'/kursiv scheme.
In Fourier the linear part is purely dispersive,
  u_hat_t = L u_hat + g * (u^2)_hat,   L = i*delta^2*k^3,   g = -3 i k  (= -6 u u_x),
so the linear operator is integrated EXACTLY via E = exp(L*dt/2), E2 = exp(L*dt), and
the quadratic nonlinearity is advanced with 4th-order Runge-Kutta in the
integrating-factor variable, 2/3-rule de-aliased. (A first-order IF-Euler step is too
weakly stable here and blows up at realistic amplitudes; RK4 has a far larger stability
region.) Fresh real-space FFT each substep keeps the state Hermitian (stays real). KdV
conserves the integral of u, so the spatial mean (k=0 mode) is preserved exactly.

IC: band-limited random field on the coarsest grid, spectrally interpolated up ->
identical continuous IC per level. Field stored: u at fixed output time T.
"""
from __future__ import annotations

import numpy as np

from ..common.spectral import spectral_interp
from ..common.sampling import latin_hypercube

NDIMS_SUPPORTED = (1,)

# Fixed timestep, same at every resolution. IF-RK4 is stable at far larger dt than
# IF-Euler; this is conservative. (TBD-box.)
_DT = 1.0e-3


def _solve(u0: np.ndarray, delta: float, domain_size: float, output_time: float,
           dt: float = _DT) -> np.ndarray:
    """Integrating-factor RK4 Fourier KdV solve from u0 (1D); return u (real)."""
    res = u0.shape[0]
    k = 2 * np.pi * np.fft.fftfreq(res, d=domain_size / res)
    Lsym = 1j * delta ** 2 * k ** 3                        # linear dispersive operator
    fi = np.fft.fftfreq(res) * res
    mask = np.abs(fi) <= res / 3.0                         # 2/3-rule de-alias (quadratic)
    g = -3.0j * k                                          # nonlinear prefactor
    nsteps = int(np.ceil(output_time / dt))
    dt = output_time / nsteps
    E = np.exp(dt * Lsym / 2.0)
    E2 = np.exp(dt * Lsym)

    def Nl(vh):
        u = np.real(np.fft.ifft(vh))
        return g * (np.fft.fft(u ** 2) * mask)

    v = np.fft.fft(u0.astype(np.float64))
    for _ in range(nsteps):
        a = Nl(v)
        b = Nl(E * (v + 0.5 * dt * a))
        c = Nl(E * v + 0.5 * dt * b)
        d = Nl(E2 * v + dt * E * c)
        v = E2 * v + dt * (E2 * a + 2.0 * E * (b + c) + d) / 6.0
    return np.real(np.fft.ifft(v))


def sample_configs(n: int, sampling_cfg: dict, ndim: int, seed: int) -> list[dict]:
    """Draw n KdV condition specs (Latin-hypercube over delta / ic_amplitude)."""
    assert ndim in NDIMS_SUPPORTED, f"kdv supports {NDIMS_SUPPORTED}, got {ndim}"
    draws = latin_hypercube(
        {"delta": tuple(sampling_cfg["delta_range"]),
         "ic_amplitude": tuple(sampling_cfg["ic_amplitude_range"])}, n, seed)
    return [{"delta": draws["delta"][i], "ic_amplitude": draws["ic_amplitude"][i],
             "domain_size": sampling_cfg["domain_size"], "ndim": ndim,
             "seed": seed + i} for i in range(n)]


def generate_sample(spec: dict, resolutions: list[int], hf_res: int, output_time: float
                    ) -> tuple[dict[int, np.ndarray], np.ndarray, list[str]]:
    """Generate one KdV sample across the fidelity ladder (1D)."""
    res_min = min(resolutions)
    rng = np.random.default_rng(spec["seed"])
    ic_coarse = spec["ic_amplitude"] * (2 * rng.random(res_min) - 1)
    fields = {
        res: _solve(spectral_interp(ic_coarse, res), spec["delta"], spec["domain_size"],
                    output_time)
        for res in resolutions
    }
    cond = np.array([spec["delta"], spec["ic_amplitude"]], dtype=np.float64)
    names = ["delta", "ic_amplitude"]
    return fields, cond, names
```

- [ ] **Step 4: Register + add config block**

In `mffp_sharp/src/mffp_sharp/generate.py`, add `kdv` to imports and `_MODULES`:
```python
from .pdes import euler, cahn_hilliard, kuramoto_sivashinsky, allen_cahn, fisher_kpp, swift_hohenberg, kdv
```
```python
    "kdv": kdv,
```
In `mffp_sharp/configs/sample.yaml`, add under `pdes:`:
```yaml
  kdv_1d:
    role: dispersive
    module: kdv
    ndim: 1
    output_time: 1.0            # T: soliton train developed (TBD-box)
    sampling:
      delta_range: [0.015, 0.04]   # dispersion; classic Zabusky-Kruskal ~0.022 (TBD)
      ic_amplitude_range: [0.3, 0.7]
      domain_size: 2.0
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate && cd /Users/nicholassung/Documents/SURF_2026/mffp_sharp && python -m pytest tests/test_kdv.py -q`
Expected: all 5 PASS — in particular `test_soliton_propagates_at_speed_c` (scheme is correct) and `test_stable_at_harshest_config_range` (no NaN at the worst-case params, the Plan-3 regression).

Then byte-compile + full suite:
Run: `source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate && cd /Users/nicholassung/Documents/SURF_2026/mffp_sharp && python -m compileall src/mffp_sharp -q && echo OK && python -m pytest tests/ -q`
Expected: `OK`; full suite PASS.

- [ ] **Step 6: Commit**

```bash
cd /Users/nicholassung/Documents/SURF_2026
git add mffp_sharp/src/mffp_sharp/pdes/kdv.py mffp_sharp/src/mffp_sharp/generate.py mffp_sharp/configs/sample.yaml mffp_sharp/tests/test_kdv.py
git commit -m "feat(kdv): IF-RK4 Fourier solver (1D), soliton- and config-range-validated

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 2: NLS solver (1D, split-step, soliton-validated)

**Files:**
- Create: `mffp_sharp/src/mffp_sharp/pdes/nls.py`
- Modify: `mffp_sharp/src/mffp_sharp/generate.py` (register `nls`)
- Modify: `mffp_sharp/configs/sample.yaml` (add `nls_1d` block)
- Test: `mffp_sharp/tests/test_nls.py`

**Interfaces:**
- Consumes: `common.spectral.spectral_interp`, `common.sampling.latin_hypercube`.
- Produces: `NDIMS_SUPPORTED = (1,)`; `sample_configs(n, sampling_cfg, ndim, seed)`; `generate_sample(...)` with `names == ["nonlinearity", "ic_amplitude"]`; the stored field is the real **intensity** `|u|²`. `_solve(u0, nonlinearity, domain_size, output_time, dt) -> np.ndarray` returns the **complex** field `u`; `generate_sample` stores `np.abs(u)**2`.

NLS: $i\,u_t + \tfrac12 u_{xx} + g\,|u|^2 u = 0$ ($g>0$ focusing, $g<0$ defocusing). Strang split-step: linear half-step (exact in Fourier, propagator $e^{-i k^2 \tau/2}$), nonlinear full-step (exact phase rotation $e^{i g |u|^2 dt}$, since $|u|$ is invariant under the nonlinear sub-flow), linear half-step. Exact bright soliton (focusing, $g=1$): $u=\mathrm{sech}(x)\,e^{it/2}$, so the **intensity** $|u|^2=\mathrm{sech}^2(x)$ is *stationary* — the correctness test. For data we use defocusing/sub-critical $g$ (no collapse; oscillatory wavepackets). Stored field is $|u|^2$ (real, carries the sharp peaks). 1D only (2D NLS deferred).

- [ ] **Step 1: Write the failing tests**

Create `mffp_sharp/tests/test_nls.py`:

```python
import numpy as np

from mffp_sharp.pdes import nls


def _spec(seed=0):
    return {"nonlinearity": -0.5, "ic_amplitude": 0.3, "domain_size": 40.0,
            "ndim": 1, "seed": seed}


def test_shapes_finite_real_intensity():
    fields, cond, names = nls.generate_sample(_spec(), [64, 128], 128, output_time=1.0)
    assert fields[64].shape == (64,) and fields[128].shape == (128,)
    for f in fields.values():
        assert np.isfinite(f).all()
        assert np.isrealobj(f) and f.min() >= 0.0      # stored field is |u|^2 >= 0
    assert names == ["nonlinearity", "ic_amplitude"] and cond.shape == (2,)


def test_bright_soliton_intensity_stationary():
    # Focusing NLS (g=1) bright soliton u=sech(x) e^{it/2}: |u|^2 = sech^2(x) is STATIONARY.
    res, domain, T = 512, 40.0, 2.0
    x = np.arange(res) * domain / res - domain / 2.0
    u0 = 1.0 / np.cosh(x)                              # sech(x), real IC
    u = nls._solve(u0.astype(np.complex128), nonlinearity=1.0,
                   domain_size=domain, output_time=T)
    intensity = np.abs(u) ** 2
    assert np.max(np.abs(intensity - 1.0 / np.cosh(x) ** 2)) < 1e-2


def test_mass_conserved():
    # NLS conserves integral of |u|^2.
    res, domain, T = 256, 40.0, 2.0
    x = np.arange(res) * domain / res - domain / 2.0
    u0 = 1.0 / np.cosh(x)
    u = nls._solve(u0.astype(np.complex128), nonlinearity=-0.5, domain_size=domain,
                   output_time=T)
    assert abs(float((np.abs(u) ** 2).mean()) - float((u0 ** 2).mean())) < 1e-6


def test_stable_at_harshest_config_range():
    fields = nls.generate_sample(
        {"nonlinearity": -1.0, "ic_amplitude": 0.5, "domain_size": 40.0,
         "ndim": 1, "seed": 4}, [64, 128], 128, output_time=2.0)[0]
    for f in fields.values():
        assert np.isfinite(f).all() and f.max() < 1e3


def test_only_1d_supported():
    assert nls.NDIMS_SUPPORTED == (1,)
    import pytest
    with pytest.raises(AssertionError):
        nls.sample_configs(2, {"nonlinearity_range": [-1.0, -0.2],
                               "ic_amplitude_range": [0.2, 0.5], "domain_size": 40.0},
                           ndim=2, seed=0)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate && cd /Users/nicholassung/Documents/SURF_2026/mffp_sharp && python -m pytest tests/test_nls.py -q`
Expected: FAIL — module `nls` doesn't exist.

- [ ] **Step 3: Create `pdes/nls.py`**

```python
"""Nonlinear Schrodinger (dispersive oscillatory wavepackets) dataset generation.

NLS:  i u_t + (1/2) u_xx + g |u|^2 u = 0   (g>0 focusing, g<0 defocusing).
High-wavenumber content comes from narrow soliton peaks (focusing) or oscillatory
wavepackets (defocusing) -- dispersion, not jumps. Tagged 'distinct'. For data we
use defocusing / sub-critical g (no collapse); the solver is validated on the exact
focusing bright soliton. 1D only (2D NLS deferred). The field is complex; we store
the real INTENSITY |u|^2 (the observable, T-determined field carrying the sharp peaks).

SOLVER: Strang split-step Fourier -- each sub-flow is solved EXACTLY:
  - linear half-step: u_t = (i/2) u_xx -> multiply u_hat by exp(-i k^2 (dt/2) / 2);
  - nonlinear full-step: u_t = i g |u|^2 u -> |u| is invariant, so u *= exp(i g |u|^2 dt);
  - linear half-step again.
Mass (integral of |u|^2) is conserved. SAME dt at every resolution.

IC: band-limited random real field on the coarsest grid, spectrally interpolated up ->
identical continuous IC per level. Field stored: |u(.,T)|^2.
"""
from __future__ import annotations

import numpy as np

from ..common.spectral import spectral_interp
from ..common.sampling import latin_hypercube

NDIMS_SUPPORTED = (1,)

# Fixed timestep, same at every resolution. Split-step is unconditionally stable on the
# linear part; dt bounds nonlinear phase accuracy. Conservative. (TBD-box.)
_DT = 1.0e-3


def _solve(u0: np.ndarray, nonlinearity: float, domain_size: float, output_time: float,
           dt: float = _DT) -> np.ndarray:
    """Strang split-step Fourier NLS solve from u0 (1D); return COMPLEX u."""
    res = u0.shape[0]
    k = 2 * np.pi * np.fft.fftfreq(res, d=domain_size / res)
    nsteps = int(np.ceil(output_time / dt))
    dt = output_time / nsteps
    lin_half = np.exp(-1j * (k ** 2) / 2.0 * (dt / 2.0))   # half linear-step propagator
    u = u0.astype(np.complex128).copy()
    for _ in range(nsteps):
        u = np.fft.ifft(np.fft.fft(u) * lin_half)          # half linear
        u = u * np.exp(1j * nonlinearity * np.abs(u) ** 2 * dt)   # full nonlinear (exact)
        u = np.fft.ifft(np.fft.fft(u) * lin_half)          # half linear
    return u


def sample_configs(n: int, sampling_cfg: dict, ndim: int, seed: int) -> list[dict]:
    """Draw n NLS condition specs (Latin-hypercube over nonlinearity / ic_amplitude)."""
    assert ndim in NDIMS_SUPPORTED, f"nls supports {NDIMS_SUPPORTED}, got {ndim}"
    draws = latin_hypercube(
        {"nonlinearity": tuple(sampling_cfg["nonlinearity_range"]),
         "ic_amplitude": tuple(sampling_cfg["ic_amplitude_range"])}, n, seed)
    return [{"nonlinearity": draws["nonlinearity"][i],
             "ic_amplitude": draws["ic_amplitude"][i],
             "domain_size": sampling_cfg["domain_size"], "ndim": ndim,
             "seed": seed + i} for i in range(n)]


def generate_sample(spec: dict, resolutions: list[int], hf_res: int, output_time: float
                    ) -> tuple[dict[int, np.ndarray], np.ndarray, list[str]]:
    """Generate one NLS sample across the fidelity ladder (1D). Stored field = |u|^2."""
    res_min = min(resolutions)
    rng = np.random.default_rng(spec["seed"])
    ic_coarse = spec["ic_amplitude"] * (2 * rng.random(res_min) - 1)
    fields = {
        res: np.abs(_solve(spectral_interp(ic_coarse, res).astype(np.complex128),
                           spec["nonlinearity"], spec["domain_size"], output_time)) ** 2
        for res in resolutions
    }
    cond = np.array([spec["nonlinearity"], spec["ic_amplitude"]], dtype=np.float64)
    names = ["nonlinearity", "ic_amplitude"]
    return fields, cond, names
```

- [ ] **Step 4: Register + add config block**

In `mffp_sharp/src/mffp_sharp/generate.py`, add `nls` to imports and `_MODULES`:
```python
from .pdes import euler, cahn_hilliard, kuramoto_sivashinsky, allen_cahn, fisher_kpp, swift_hohenberg, kdv, nls
```
```python
    "nls": nls,
```
In `mffp_sharp/configs/sample.yaml`, add under `pdes:`:
```yaml
  nls_1d:
    role: dispersive
    module: nls
    ndim: 1
    output_time: 2.0            # T: wavepacket structure developed (TBD-box)
    sampling:
      nonlinearity_range: [-1.0, -0.2]   # defocusing / sub-critical (no collapse) (TBD)
      ic_amplitude_range: [0.2, 0.5]
      domain_size: 40.0
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate && cd /Users/nicholassung/Documents/SURF_2026/mffp_sharp && python -m pytest tests/test_nls.py -q`
Expected: all 5 PASS — in particular `test_bright_soliton_intensity_stationary` (split-step is correct) and `test_stable_at_harshest_config_range`.

Then end-to-end through the registry + byte-compile + full suite:
Run: `source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate && cd /Users/nicholassung/Documents/SURF_2026/mffp_sharp && python -c "from mffp_sharp import generate; import tempfile,os; d=tempfile.mkdtemp(); top={'seed':0,'out_dir':d,'n_samples_per_pde':2,'n_figures':0,'ladder':{'resolutions':[64,128],'hf_index':1},'metrics':['rel_l2','linf','spectral_band']}; b={'module':'nls','ndim':1,'output_time':1.0,'sampling':{'nonlinearity_range':[-0.5,-0.5],'ic_amplitude_range':[0.3,0.3],'domain_size':40.0}}; print(generate.generate_dataset('nls_1d',b,top)['pde'])" && python -m compileall src/mffp_sharp -q && echo OK && python -m pytest tests/ -q`
Expected: prints `nls_1d`; `OK`; full suite PASS.

- [ ] **Step 6: Commit and push**

```bash
cd /Users/nicholassung/Documents/SURF_2026
git add mffp_sharp/src/mffp_sharp/pdes/nls.py mffp_sharp/src/mffp_sharp/generate.py mffp_sharp/configs/sample.yaml mffp_sharp/tests/test_nls.py
git commit -m "feat(nls): split-step Fourier solver (1D, stores |u|^2), bright-soliton-validated

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
git push
```

---

## Self-Review

**1. Spec coverage** (build-set, dispersive/oscillatory items):
- **C3 KdV (1D)** → Task 1, now with a stable IF-RK4 scheme (supersedes the reverted Plan-3 IF-Euler). ✓
- **C2 NLS (1D, defocusing/sub-critical)** → Task 2. ✓
- **Deferred to Plan 5** (each a further distinct paradigm): C4 sine-Gordon (2nd-order in *time* → Strang/leapfrog on a 2-field system), B4 Gray–Scott (coupled reaction-diffusion → ETDRK4 on a 2-component system), B6 phase-field crystal (stiff 6th-order). 2D KP-II / 2D NLS also deferred. Intentional, not a gap.

**2. Placeholder scan:** No "TBD"/"add error handling"/"write tests for the above". Provisional physical params flagged `(TBD-box)`. Every code step is complete; every run step has a command + expected output.

**3. Type consistency:** `sample_configs(n, sampling_cfg, ndim, seed)` + `generate_sample(spec, resolutions, hf_res, output_time)` uniform with all other modules and the `generate.generate_dataset` caller. `_MODULES` keys (`kdv`, `nls`) match config `module:` values. Both `NDIMS_SUPPORTED = (1,)`, correctly rejecting ndim=2 (tested). KdV stores real `u`; NLS stores real `|u|²` (the complex field lives only inside `_solve`).

**Lesson applied from Plan 3 (KdV revert):** every solver here carries (a) an **exact-soliton correctness test** (KdV traveling soliton; NLS bright-soliton stationary intensity) and (b) a **finiteness test at the config's harshest sampled parameters** — the two checks whose absence let the Plan-3 IF-Euler KdV NaN slip through. During execution, if either soliton test fails, the scheme is wrong: BLOCK and fix the scheme, do not loosen the test.

**Scope / follow-on:** Plan 5 — sine-Gordon, Gray–Scott, phase-field crystal (each a distinct stepping paradigm: 2nd-order-time, coupled-system ETDRK4, stiff 6th-order). Plan 6 — PyClaw/WENO (box-only): Burgers, Sod, shallow-water, Buckley–Leverett. Plan 7 — special: Helmholtz, porous-medium. Plan 8 — box sample generation + auto-screen + survivor menu for Nicholas.
