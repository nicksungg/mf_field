# Single-Field Spectral Solvers (1D KS, Swift–Hohenberg, KdV) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the remaining **single real-scalar-field** spectral PDE solvers to the build set: generalize the validated Kuramoto–Sivashinsky solver to 1D (the smooth control), and add Swift–Hohenberg (pattern-former) and KdV (dispersive soliton trains), each registered as a plugin with 1D and/or 2D sample datasets.

**Architecture:** All three are Fourier pseudospectral on a periodic domain, fed the same coarse-IC-spectrally-interpolated-up consistency recipe as the existing solvers (LF is a real coarse solve, never downsampled HF). KS and Swift–Hohenberg use the semi-implicit scheme (stiff linear part implicit in Fourier, nonlinearity explicit, fresh FFT each step for Hermitian safety); KdV uses an integrating-factor (exponential) Euler step because its linear operator is purely dispersive. `np.fft.fftn`/`ifftn` let one body serve 1D and 2D. KS is *generalized in place* under a golden-fixture characterization test that pins its 2D output bit-for-bit.

**Tech Stack:** Python 3.9, NumPy (`fftn`/`ifftn`, `fft`/`ifft`), SciPy (`qmc`), h5py, matplotlib. Tests via pytest; pure-numpy solvers run locally.

## Global Constraints

These apply to **every** task (copied verbatim from the spec / CLAUDE.md):

- **LF = a real coarse *consistent* solve of the same PDE; NEVER downsampled or noised HF.** Each solver builds a coarse IC, `spectral_interp`s it up to each ladder resolution, and `_solve`s independently per level — no decimation/filtering of an HF field.
- **Same solver, same dt, same continuous IC at every fidelity — only the grid changes.**
- **Do NOT change the *behavior* of the validated KS 2D solve.** Task 1 generalizes KS to N-D, but a golden-fixture characterization test must prove the 2D output is bit-for-bit unchanged. Do not touch `cahn_hilliard`, `euler`, `allen_cahn`, `fisher_kpp` solver numerics.
- **Condition vector complete and small** (≤ ~10 scalars; solver + vector + snapshot T fully determine the field).
- **Heavy/full generation runs on the box only.** This plan is light: solver unit tests use tiny grids + short T locally. Physics validation (sharpness, bottom-rung) is deferred to the box sample round (a later plan); local tests assert structural correctness (shape, finiteness, determinism, ladder-IC consistency, dimension support, boundedness/zero-mean as applicable).
- **Python 3.9 compatible**; every module keeps `from __future__ import annotations`.
- **Dependencies limited to** numpy, scipy, h5py, scikit-image, matplotlib, pyyaml (+ pytest test-only).
- **Plugin contract (uniform across all PDE modules):** `NDIMS_SUPPORTED: tuple[int,...]`, `sample_configs(n, sampling_cfg, ndim, seed) -> list[spec]`, `generate_sample(spec, resolutions, hf_res, output_time) -> ({res: field}, cond_vec, names)`. New modules registered in `generate._MODULES`; each dataset is a config block with `module:` + `ndim:`.
- **Git discipline:** executed on feature branch `feat/single-field-spectral`; commit after each task; messages end with `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`. Prefix every python/pytest command with `source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate &&` (shell state does not persist).

**Depends on:** Plan 1 (`common/` 1D refactor) and Plan 2 (plugin registry + `common/spectral.py` with `spectral_interp`/`neg_laplacian_symbol`) — both merged.

---

## File Structure

| File | Responsibility | Action |
|---|---|---|
| `mffp_sharp/src/mffp_sharp/pdes/kuramoto_sivashinsky.py` | KS solver | **Modify** — generalize `_solve` to N-D via `fftn`; `NDIMS_SUPPORTED=(1,2)`; `generate_sample` builds ndim-shaped IC. 2D behavior pinned by golden test. |
| `mffp_sharp/src/mffp_sharp/pdes/swift_hohenberg.py` | Swift–Hohenberg solver (1D+2D) | **Create** |
| `mffp_sharp/src/mffp_sharp/pdes/kdv.py` | KdV solver (1D) | **Create** |
| `mffp_sharp/src/mffp_sharp/generate.py` | registry | **Modify** — register `swift_hohenberg`, `kdv` |
| `mffp_sharp/configs/sample.yaml` | config | **Modify** — add `kuramoto_sivashinsky_1d`, `swift_hohenberg_1d/2d`, `kdv_1d` blocks |
| `mffp_sharp/tests/fixtures/ks_2d_golden.npy` | KS 2D golden output | **Create** (captured from pre-generalization code) |
| `mffp_sharp/tests/` | unit tests | **Create** `test_ks_1d.py`, `test_swift_hohenberg.py`, `test_kdv.py` |

---

## Task 1: Generalize KS to 1D (golden-pinned 2D)

**Files:**
- Create: `mffp_sharp/tests/fixtures/ks_2d_golden.npy`
- Create: `mffp_sharp/tests/test_ks_1d.py`
- Modify: `mffp_sharp/src/mffp_sharp/pdes/kuramoto_sivashinsky.py` (`NDIMS_SUPPORTED`, `_solve`, `generate_sample`)
- Modify: `mffp_sharp/configs/sample.yaml` (add `kuramoto_sivashinsky_1d` block)

**Interfaces:**
- Produces: KS module now `NDIMS_SUPPORTED = (1, 2)`; `_solve(u0, L, output_time, dt)` accepts 1D or 2D `u0` (dimension via `u0.ndim`), returning the zero-mean fluctuation; `generate_sample` builds an ndim-shaped coarse IC from `spec["ndim"]`. `sample_configs` unchanged except it already passes `ndim` through. 2D output is bit-for-bit identical to before (golden-pinned).
- Consumes: `common.spectral.spectral_interp`.

- [ ] **Step 1: Capture the 2D golden fixture from the CURRENT code**

This is a characterization fixture — capture the *current* (pre-generalization) 2D KS output so the refactor can be proven behavior-preserving.

Run:
```bash
source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate && cd /Users/nicholassung/Documents/SURF_2026/mffp_sharp && mkdir -p tests/fixtures && python -c "
import numpy as np
from mffp_sharp.pdes import kuramoto_sivashinsky as ks
spec = {'L': 30.0, 'ic_amplitude': 0.1, 'ndim': 2, 'seed': 1}
fields = ks.generate_sample(spec, [16, 32], 32, output_time=2.0)[0]
np.save('tests/fixtures/ks_2d_golden.npy', np.stack([fields[16].ravel()[:64], fields[32].ravel()[:64]]))
print('saved golden, checksums:', float(fields[16].sum()), float(fields[32].sum()))
"
```
Expected: prints `saved golden, checksums: <a> <b>` and writes `tests/fixtures/ks_2d_golden.npy`. (We store the first 64 raveled entries of each level — enough to detect any numeric drift.)

- [ ] **Step 2: Write the characterization + 1D tests**

Create `mffp_sharp/tests/test_ks_1d.py`:

```python
import os

import numpy as np

from mffp_sharp.pdes import kuramoto_sivashinsky as ks

_GOLDEN = os.path.join(os.path.dirname(__file__), "fixtures", "ks_2d_golden.npy")


def test_2d_output_matches_golden():
    # The N-D generalization must not change the validated 2D solve.
    golden = np.load(_GOLDEN)
    spec = {"L": 30.0, "ic_amplitude": 0.1, "ndim": 2, "seed": 1}
    fields = ks.generate_sample(spec, [16, 32], 32, output_time=2.0)[0]
    got = np.stack([fields[16].ravel()[:64], fields[32].ravel()[:64]])
    assert np.allclose(got, golden, atol=1e-12, rtol=0)


def test_1d_shapes_and_zero_mean():
    spec = {"L": 30.0, "ic_amplitude": 0.1, "ndim": 1, "seed": 2}
    fields, cond, names = ks.generate_sample(spec, [64, 128], 128, output_time=2.0)
    assert fields[64].shape == (64,) and fields[128].shape == (128,)
    for f in fields.values():
        assert np.isfinite(f).all()
        assert abs(float(f.mean())) < 1e-8          # stores zero-mean fluctuation
    assert names == ["L", "ic_amplitude"] and cond.shape == (2,)


def test_1d_deterministic():
    spec = {"L": 28.0, "ic_amplitude": 0.1, "ndim": 1, "seed": 5}
    a = ks.generate_sample(spec, [64, 128], 128, 2.0)[0][128]
    b = ks.generate_sample(spec, [64, 128], 128, 2.0)[0][128]
    assert np.array_equal(a, b)


def test_1d_supported():
    assert ks.NDIMS_SUPPORTED == (1, 2)
    cfg = {"L_range": [22.0, 36.0], "ic_amplitude_range": [0.05, 0.2]}
    specs = ks.sample_configs(3, cfg, ndim=1, seed=0)
    assert all(s["ndim"] == 1 for s in specs)
```

- [ ] **Step 3: Run tests — golden passes on current code, 1D fails**

Run: `source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate && cd /Users/nicholassung/Documents/SURF_2026/mffp_sharp && python -m pytest tests/test_ks_1d.py -q`
Expected: `test_2d_output_matches_golden` PASSES (golden captured from current code); the three 1D tests FAIL — `sample_configs` asserts `ndim in (2,)` so `ndim=1` raises `AssertionError`, and `generate_sample` builds a 2D IC.

- [ ] **Step 4: Generalize the KS module to N-D**

In `mffp_sharp/src/mffp_sharp/pdes/kuramoto_sivashinsky.py`:

(a) Change `NDIMS_SUPPORTED = (2,)` to `NDIMS_SUPPORTED = (1, 2)`.

(b) Replace `_solve` (the whole function body) with this dimension-aware version (mathematically identical to the original for 2D — `fftn`==`fft2`, the per-axis sums reproduce `KX²+KY²` and `-0.5(ux²+uy²)`, the mask reproduces `MX & MY`):

```python
def _solve(u0: np.ndarray, L: float, output_time: float, dt: float = _DT) -> np.ndarray:
    """Semi-implicit Fourier KS solve from initial field u0 (1D or 2D); return u - <u>."""
    res = u0.shape[0]
    ndim = u0.ndim
    k1 = 2 * np.pi * np.fft.fftfreq(res, d=L / res)
    ks_axes = np.meshgrid(*([k1] * ndim), indexing="ij")   # per-axis wavenumber arrays
    k2 = sum(kk ** 2 for kk in ks_axes)
    k4 = k2 ** 2
    fi = np.fft.fftfreq(res) * res
    keep1 = np.abs(fi) <= res / 3.0                         # 2/3-rule de-alias (quadratic)
    mask = np.logical_and.reduce(np.meshgrid(*([keep1] * ndim), indexing="ij"))
    nsteps = int(np.ceil(output_time / dt))
    dt = output_time / nsteps
    denom = 1.0 / dt + k4                                   # implicit biharmonic (-k^4 damping)
    u = u0.astype(np.float64).copy()
    for _ in range(nsteps):
        uh = np.fft.fftn(u)                                # FRESH each step -> stays Hermitian
        grad2 = sum(np.real(np.fft.ifftn(1j * kk * uh)) ** 2 for kk in ks_axes)
        nl = -0.5 * grad2
        nlh = np.fft.fftn(nl) * mask
        uh_new = (uh * (1.0 / dt + k2) + nlh) / denom
        u = np.real(np.fft.ifftn(uh_new))
    return u - u.mean()                                     # store zero-mean fluctuation
```

(c) In `generate_sample`, replace the IC line
`ic_coarse = spec["ic_amplitude"] * (2 * rng.random((res_min, res_min)) - 1)`
with an ndim-shaped IC:
```python
    ndim = int(spec["ndim"])
    ic_coarse = spec["ic_amplitude"] * (2 * rng.random((res_min,) * ndim) - 1)
```
(Place the `ndim = int(spec["ndim"])` line just after `res_min = min(resolutions)`.)

- [ ] **Step 5: Add the 1D KS config block**

In `mffp_sharp/configs/sample.yaml`, add under `pdes:` (the 1D KS resolves the "2D-KS is non-standard" knob; 1D KS is textbook):
```yaml
  kuramoto_sivashinsky_1d:
    role: smooth_control
    module: kuramoto_sivashinsky
    ndim: 1
    output_time: 15.0           # tracking window (same rationale as 2D KS; TBD-box)
    sampling:
      L_range: [22.0, 100.0]    # 1D ladder (64/128/256) resolves larger L (TBD)
      ic_amplitude_range: [0.05, 0.2]
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate && cd /Users/nicholassung/Documents/SURF_2026/mffp_sharp && python -m pytest tests/test_ks_1d.py -q`
Expected: all 4 PASS (golden still matches → 2D bit-preserved; 1D works).

Then byte-compile + full suite:
Run: `source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate && cd /Users/nicholassung/Documents/SURF_2026/mffp_sharp && python -m compileall src/mffp_sharp -q && echo OK && python -m pytest tests/ -q`
Expected: `OK`; all prior + new tests PASS.

- [ ] **Step 7: Commit**

```bash
cd /Users/nicholassung/Documents/SURF_2026
git add mffp_sharp/src/mffp_sharp/pdes/kuramoto_sivashinsky.py mffp_sharp/configs/sample.yaml mffp_sharp/tests/test_ks_1d.py mffp_sharp/tests/fixtures/ks_2d_golden.npy
git commit -m "feat(ks): generalize to N-D (1D+2D); golden-pin 2D output unchanged

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 2: Swift–Hohenberg solver (1D + 2D)

**Files:**
- Create: `mffp_sharp/src/mffp_sharp/pdes/swift_hohenberg.py`
- Modify: `mffp_sharp/src/mffp_sharp/generate.py` (register `swift_hohenberg`)
- Modify: `mffp_sharp/configs/sample.yaml` (add `swift_hohenberg_1d/2d` blocks)
- Test: `mffp_sharp/tests/test_swift_hohenberg.py`

**Interfaces:**
- Consumes: `common.spectral.spectral_interp`, `common.sampling.latin_hypercube`.
- Produces: `NDIMS_SUPPORTED = (1, 2)`; `sample_configs(n, sampling_cfg, ndim, seed)`; `generate_sample(...)` with `names == ["r", "ic_amplitude"]`. Fields finite and bounded (the cubic nonlinearity saturates the pattern amplitude).

Swift–Hohenberg: $\partial_t u = r\,u - (1+\nabla^2)^2 u - u^3$. Pattern-former with a spectral *peak* at the characteristic wavenumber $k=1$ (banding/stripes). Linear symbol in Fourier $L(k) = r - (1-k^2)^2$ (continuous $k$; SH patterns are smooth and well-resolved). Semi-implicit: implicit linear ($1/dt - L$ in the denominator — bounded below by $1/dt - r$, so requires $dt < 1/r$), explicit cubic, fresh FFT each step, 2/3-rule de-alias. `fftn`/`ifftn` serve 1D and 2D.

- [ ] **Step 1: Write the failing tests**

Create `mffp_sharp/tests/test_swift_hohenberg.py`:

```python
import numpy as np

from mffp_sharp.pdes import swift_hohenberg as sh


def _spec(ndim, seed=0):
    return {"r": 0.3, "ic_amplitude": 0.1, "domain_size": 32.0, "ndim": ndim, "seed": seed}


def test_2d_shapes_finite_bounded():
    fields, cond, names = sh.generate_sample(_spec(2), [16, 32], 32, output_time=1.0)
    assert fields[16].shape == (16, 16) and fields[32].shape == (32, 32)
    for f in fields.values():
        assert np.isfinite(f).all() and np.abs(f).max() < 100.0
    assert names == ["r", "ic_amplitude"] and cond.shape == (2,)


def test_1d_shapes_finite():
    fields = sh.generate_sample(_spec(1), [64, 128], 128, output_time=1.0)[0]
    assert fields[64].shape == (64,) and fields[128].shape == (128,)
    for f in fields.values():
        assert np.isfinite(f).all()


def test_deterministic():
    a = sh.generate_sample(_spec(1, seed=3), [64, 128], 128, 1.0)[0][128]
    b = sh.generate_sample(_spec(1, seed=3), [64, 128], 128, 1.0)[0][128]
    assert np.array_equal(a, b)


def test_ladder_outputs_spectrally_consistent():
    # Near-zero T: each level solves from the SAME continuous IC, so the coarse output
    # interpolated up matches the fine output (no clip here -> tight tolerance).
    from mffp_sharp.common.spectral import spectral_interp
    fields = sh.generate_sample(_spec(2, seed=4), [16, 32], 32, output_time=1e-6)[0]
    assert np.allclose(spectral_interp(fields[16], 32), fields[32], atol=1e-3)


def test_sample_configs():
    cfg = {"r_range": [0.1, 0.5], "ic_amplitude_range": [0.05, 0.2], "domain_size": 32.0}
    specs = sh.sample_configs(3, cfg, ndim=2, seed=1)
    assert len(specs) == 3 and all(s["ndim"] == 2 for s in specs)
    assert sh.NDIMS_SUPPORTED == (1, 2)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate && cd /Users/nicholassung/Documents/SURF_2026/mffp_sharp && python -m pytest tests/test_swift_hohenberg.py -q`
Expected: FAIL — module `swift_hohenberg` doesn't exist.

- [ ] **Step 3: Create `pdes/swift_hohenberg.py`**

```python
"""Swift-Hohenberg (pattern-former, spectral PEAK) dataset generation.

Swift-Hohenberg:  d u/dt = r u - (1 + laplace)^2 u - u^3.
Forms striped/hexagonal patterns with a characteristic wavenumber k=1; its spectrum
is a PEAK at k~1 (not a power law or knee), which is exactly the form-agnostic case
the energy-above-cutoff screen is designed to handle. Tagged 'distinct (pattern)'.

SOLVER: semi-implicit Fourier (same family as KS / Cahn-Hilliard):
  - the linear operator L(k) = r - (1 - k^2)^2 is treated IMPLICITLY (it can be
    positive near k^2=1 -> pattern growth; implicit handling stays stable). Uses the
    CONTINUOUS k^2 (SH patterns are smooth and well-resolved, like KS);
  - the cubic -u^3 is explicit, 2/3-rule de-aliased;
  - fresh FFT each step (Hermitian-safe); np.fft.fftn/ifftn serve 1D and 2D.
Stability needs dt < 1/r (so the implicit denom 1/dt - L stays positive); _DT is
conservative. SAME dt at every resolution.

IC: small band-limited random field on the coarsest grid, spectrally interpolated up
-> identical continuous IC per level (patterns grow from the SAME seed everywhere).

Field stored: u at fixed output time T (pattern developed).
"""
from __future__ import annotations

import numpy as np

from ..common.spectral import spectral_interp
from ..common.sampling import latin_hypercube

NDIMS_SUPPORTED = (1, 2)

# Fixed timestep, same at every resolution. Needs dt < 1/r; conservative. (TBD-box.)
_DT = 0.05


def _solve(u0: np.ndarray, r: float, domain_size: float, output_time: float,
           dt: float = _DT) -> np.ndarray:
    """Semi-implicit Fourier Swift-Hohenberg solve from u0 (1D or 2D); return u."""
    res = u0.shape[0]
    ndim = u0.ndim
    k1 = 2 * np.pi * np.fft.fftfreq(res, d=domain_size / res)
    k_axes = np.meshgrid(*([k1] * ndim), indexing="ij")
    k2 = sum(kk ** 2 for kk in k_axes)
    Lsym = r - (1.0 - k2) ** 2                              # linear operator symbol
    fi = np.fft.fftfreq(res) * res
    keep1 = np.abs(fi) <= res / 3.0                         # 2/3-rule de-alias (cubic)
    mask = np.logical_and.reduce(np.meshgrid(*([keep1] * ndim), indexing="ij"))
    nsteps = int(np.ceil(output_time / dt))
    dt = output_time / nsteps
    denom = 1.0 / dt - Lsym                                 # implicit linear (>0 if dt<1/r)
    u = u0.astype(np.float64).copy()
    for _ in range(nsteps):
        uh = np.fft.fftn(u)                                # FRESH each step -> Hermitian
        nlh = np.fft.fftn(u ** 3) * mask                   # explicit cubic, de-aliased
        uh_new = (uh * (1.0 / dt) - nlh) / denom
        u = np.real(np.fft.ifftn(uh_new))
    return u


def sample_configs(n: int, sampling_cfg: dict, ndim: int, seed: int) -> list[dict]:
    """Draw n Swift-Hohenberg condition specs (Latin-hypercube over r / ic_amplitude)."""
    assert ndim in NDIMS_SUPPORTED, f"swift_hohenberg supports {NDIMS_SUPPORTED}, got {ndim}"
    draws = latin_hypercube(
        {"r": tuple(sampling_cfg["r_range"]),
         "ic_amplitude": tuple(sampling_cfg["ic_amplitude_range"])}, n, seed)
    return [{"r": draws["r"][i], "ic_amplitude": draws["ic_amplitude"][i],
             "domain_size": sampling_cfg["domain_size"], "ndim": ndim,
             "seed": seed + i} for i in range(n)]


def generate_sample(spec: dict, resolutions: list[int], hf_res: int, output_time: float
                    ) -> tuple[dict[int, np.ndarray], np.ndarray, list[str]]:
    """Generate one Swift-Hohenberg sample across the fidelity ladder (1D or 2D)."""
    ndim = int(spec["ndim"])
    res_min = min(resolutions)
    rng = np.random.default_rng(spec["seed"])
    ic_coarse = spec["ic_amplitude"] * (2 * rng.random((res_min,) * ndim) - 1)
    fields = {
        res: _solve(spectral_interp(ic_coarse, res), spec["r"], spec["domain_size"],
                    output_time)
        for res in resolutions
    }
    cond = np.array([spec["r"], spec["ic_amplitude"]], dtype=np.float64)
    names = ["r", "ic_amplitude"]
    return fields, cond, names
```

- [ ] **Step 4: Register + add config blocks**

In `mffp_sharp/src/mffp_sharp/generate.py`, add to imports and `_MODULES`:
```python
from .pdes import euler, cahn_hilliard, kuramoto_sivashinsky, allen_cahn, fisher_kpp, swift_hohenberg
```
```python
    "swift_hohenberg": swift_hohenberg,
```
In `mffp_sharp/configs/sample.yaml`, add under `pdes:`:
```yaml
  swift_hohenberg_2d:
    role: pattern
    module: swift_hohenberg
    ndim: 2
    output_time: 50.0           # T: pattern developed (TBD-box)
    sampling:
      r_range: [0.1, 0.6]       # above pattern threshold r>0; dt<1/r (TBD)
      ic_amplitude_range: [0.05, 0.2]
      domain_size: 32.0
  swift_hohenberg_1d:
    role: pattern
    module: swift_hohenberg
    ndim: 1
    output_time: 50.0
    sampling:
      r_range: [0.1, 0.6]
      ic_amplitude_range: [0.05, 0.2]
      domain_size: 64.0
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate && cd /Users/nicholassung/Documents/SURF_2026/mffp_sharp && python -m pytest tests/test_swift_hohenberg.py -q`
Expected: all 5 PASS.

Then end-to-end through the registry + byte-compile + full suite:
Run: `source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate && cd /Users/nicholassung/Documents/SURF_2026/mffp_sharp && python -c "from mffp_sharp import generate; import tempfile,os; d=tempfile.mkdtemp(); top={'seed':0,'out_dir':d,'n_samples_per_pde':2,'n_figures':0,'ladder':{'resolutions':[16,32],'hf_index':1},'metrics':['rel_l2','linf','spectral_band']}; b={'module':'swift_hohenberg','ndim':2,'output_time':1.0,'sampling':{'r_range':[0.3,0.3],'ic_amplitude_range':[0.1,0.1],'domain_size':32.0}}; print(generate.generate_dataset('swift_hohenberg_2d',b,top)['pde'])" && python -m compileall src/mffp_sharp -q && echo OK && python -m pytest tests/ -q`
Expected: prints `swift_hohenberg_2d`; `OK`; full suite PASS.

- [ ] **Step 6: Commit**

```bash
cd /Users/nicholassung/Documents/SURF_2026
git add mffp_sharp/src/mffp_sharp/pdes/swift_hohenberg.py mffp_sharp/src/mffp_sharp/generate.py mffp_sharp/configs/sample.yaml mffp_sharp/tests/test_swift_hohenberg.py
git commit -m "feat(swift_hohenberg): semi-implicit Fourier pattern-former (1D+2D)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 3: KdV solver (1D, integrating-factor) — ⚠️ DEFERRED TO PLAN 4

> **Status: NOT shipped in this plan (reverted during execution).** The integrating-factor
> *Euler* scheme specified below proved too weakly stable: it produced NaNs at the config's own
> sampling range (T=1.0, amplitude 0.7) and was stable only for a benign subset (T=0.5, amp=0.5),
> which the unit tests happened to use — masking the instability. KdV genuinely needs a
> higher-order exponential integrator (ETDRK4 / IF-RK4, per Kassam–Trefethen / the real "p27"
> scheme), which is the distinct-paradigm class Plan 4 is for. **KdV is moved to Plan 4.** The
> task spec is retained below for reference, but the IF-Euler `_solve` must NOT be used as-is.



**Files:**
- Create: `mffp_sharp/src/mffp_sharp/pdes/kdv.py`
- Modify: `mffp_sharp/src/mffp_sharp/generate.py` (register `kdv`)
- Modify: `mffp_sharp/configs/sample.yaml` (add `kdv_1d` block)
- Test: `mffp_sharp/tests/test_kdv.py`

**Interfaces:**
- Consumes: `common.spectral.spectral_interp`, `common.sampling.latin_hypercube`.
- Produces: `NDIMS_SUPPORTED = (1,)`; `sample_configs(n, sampling_cfg, ndim, seed)`; `generate_sample(...)` with `names == ["delta", "ic_amplitude"]`. Fields finite; KdV conserves mass (the spatial mean is preserved to high accuracy).

KdV: $\partial_t u + 6\,u\,u_x + \delta^2 u_{xxx} = 0$, i.e. $\partial_t u = \delta^2 u_{xxx}\cdot(-1)\ldots$ — in Fourier $\hat u_t = i\,\delta^2 k^3\,\hat u - 3 i k\,\widehat{u^2}$. The linear part is purely dispersive (imaginary symbol), so a semi-implicit real denominator is inappropriate; use an **integrating factor** $E = e^{i\,\delta^2 k^3\,dt}$ (exact on the linear part) with explicit Euler on the nonlinearity (the canonical Trefethen "p27" pseudospectral KdV). 2/3-rule de-alias the quadratic; fresh FFT each step keeps it Hermitian/real. 1D only (KP-II 2D deferred).

- [ ] **Step 1: Write the failing tests**

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


def test_mass_conserved():
    # KdV conserves the integral of u; the spatial mean should barely move.
    fields = kdv.generate_sample(_spec(seed=1), [128], 128, output_time=0.5)[0]
    f = fields[128]
    # compare mean of the solved field to the mean of the IC by re-deriving the IC
    rng = np.random.default_rng(1)
    ic = 0.5 * (2 * rng.random(128) - 1)               # matches generate_sample's IC build
    assert abs(float(f.mean()) - float(ic.mean())) < 1e-6


def test_deterministic():
    a = kdv.generate_sample(_spec(seed=3), [128], 128, 0.5)[0][128]
    b = kdv.generate_sample(_spec(seed=3), [128], 128, 0.5)[0][128]
    assert np.array_equal(a, b)


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
1D only here (2D KP-II is deferred).

SOLVER: Fourier pseudospectral with an INTEGRATING FACTOR (exponential time-stepping;
the canonical Trefethen 'p27' scheme). In Fourier the linear part is purely dispersive,
  u_hat_t = i*delta^2*k^3*u_hat - 3 i k * (u^2)_hat,
so a real semi-implicit denominator is inappropriate; instead the linear operator is
integrated EXACTLY via E = exp(i*delta^2*k^3*dt), and the quadratic nonlinearity is
explicit Euler, 2/3-rule de-aliased:
  u_hat^{n+1} = E * ( u_hat^n + dt * (-3 i k (u^2)_hat) ).
Fresh FFT from the real state each step keeps it Hermitian (stays real). KdV conserves
the integral of u (mass), so the spatial mean is preserved. SAME dt at every resolution.

IC: band-limited random field on the coarsest grid, spectrally interpolated up ->
identical continuous IC per level. Field stored: u at fixed output time T.
"""
from __future__ import annotations

import numpy as np

from ..common.spectral import spectral_interp
from ..common.sampling import latin_hypercube

NDIMS_SUPPORTED = (1,)

# Fixed timestep, same at every resolution. Explicit nonlinear part -> small. (TBD-box.)
_DT = 1.0e-4


def _solve(u0: np.ndarray, delta: float, domain_size: float, output_time: float,
           dt: float = _DT) -> np.ndarray:
    """Integrating-factor Fourier KdV solve from u0 (1D); return u."""
    res = u0.shape[0]
    k = 2 * np.pi * np.fft.fftfreq(res, d=domain_size / res)
    fi = np.fft.fftfreq(res) * res
    mask = np.abs(fi) <= res / 3.0                          # 2/3-rule de-alias (quadratic)
    nsteps = int(np.ceil(output_time / dt))
    dt = output_time / nsteps
    E = np.exp(1j * delta ** 2 * k ** 3 * dt)               # exact linear (dispersive) factor
    u = u0.astype(np.float64).copy()
    for _ in range(nsteps):
        uh = np.fft.fft(u)                                 # FRESH each step -> stays Hermitian
        nl = -3.0 * 1j * k * (np.fft.fft(u ** 2) * mask)   # -(6 u u_x) = -3 (u^2)_x
        uh_new = E * (uh + dt * nl)
        u = np.real(np.fft.ifft(uh_new))
    return u


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

In `mffp_sharp/src/mffp_sharp/generate.py`, add to imports and `_MODULES`:
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
Expected: all 4 PASS (note: `test_mass_conserved` confirms the integrating-factor scheme preserves the mean).

Then byte-compile + full suite:
Run: `source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate && cd /Users/nicholassung/Documents/SURF_2026/mffp_sharp && python -m compileall src/mffp_sharp -q && echo OK && python -m pytest tests/ -q`
Expected: `OK`; full suite PASS.

- [ ] **Step 6: Commit and push**

```bash
cd /Users/nicholassung/Documents/SURF_2026
git add mffp_sharp/src/mffp_sharp/pdes/kdv.py mffp_sharp/src/mffp_sharp/generate.py mffp_sharp/configs/sample.yaml mffp_sharp/tests/test_kdv.py
git commit -m "feat(kdv): integrating-factor Fourier solver (1D, dispersive soliton trains)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
git push
```

---

## Self-Review

**1. Spec coverage** (build-set spectral template, remaining items):
- **E3 1D KS** → Task 1 (KS generalized to 1D, golden-pinned). ✓
- **B5 Swift–Hohenberg (1D/2D)** → Task 2. ✓
- **C3 KdV (1D)** → Task 3 **DEFERRED to Plan 4** (IF-Euler too unstable; needs ETDRK4/IF-RK4). KP-II 2D also deferred.
- **Deferred to Plan 4** (each a distinct stepping paradigm, NOT this single-real-field template): C2 NLS (complex field → split-step Fourier), C4 sine-Gordon (2nd-order in *time* → Strang/leapfrog), B4 Gray–Scott (coupled 2-field → ETDRK4), B6 phase-field crystal (stiff 6th-order). Intentional, not a gap.

**2. Placeholder scan:** No "TBD"/"add error handling"/"write tests for the above". Provisional *physical* params (dt, ranges, T) are flagged `(TBD-box)` per the repo convention (validated in the box sample round) — data values, not missing code. Every code step has complete code; every run step has a command + expected output.

**3. Type consistency:** `sample_configs(n, sampling_cfg, ndim, seed)` + `generate_sample(spec, resolutions, hf_res, output_time)` uniform across all three new/edited modules and the `generate.generate_dataset` caller. `_MODULES` keys (`swift_hohenberg`, `kdv`) match config `module:` values. KdV `NDIMS_SUPPORTED = (1,)` correctly rejects ndim=2 (tested). KS `NDIMS_SUPPORTED` widens to `(1, 2)`; its golden test pins the 2D path.

**Key risk + mitigation:** Task 1 edits a *validated* solver (KS). The golden-fixture characterization test (captured from the pre-edit code, asserted to `atol=1e-12`) is the guard — if the N-D generalization changes the 2D numerics at all, `test_2d_output_matches_golden` fails. The generalization is designed to be bit-identical (`fftn`==`fft2`; per-axis sums reproduce `KX²+KY²` and `-0.5(ux²+uy²)`; `logical_and.reduce` reproduces `MX & MY`).

**Scope / follow-on:** Plan 4 — structurally-distinct spectral solvers (**KdV** via ETDRK4/IF-RK4, NLS, sine-Gordon, Gray–Scott, PFC). Plan 5 — PyClaw/WENO (box-only). Plan 6 — special (Helmholtz, porous-medium). Plan 7 — box sample generation + auto-screen + survivor menu.
