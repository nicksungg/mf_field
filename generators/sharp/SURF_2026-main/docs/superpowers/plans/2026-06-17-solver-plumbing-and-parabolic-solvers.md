# Solver Registration Plumbing + Parabolic Spectral Solvers Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up the generic PDE-plugin registration (so new solvers register without editing `generate.py`'s control flow), share the band-limited spectral helpers (1D+2D), and add the first two new dimension-aware solver modules — **Allen–Cahn** and **Fisher–KPP** — each producing both 1D and 2D sample datasets.

**Architecture:** Each PDE module is a self-contained plugin exposing `sample_configs(n, sampling_cfg, ndim, seed) -> list[spec]` and `generate_sample(spec, resolutions, hf_res, output_time) -> ({res: field}, cond_vec, names)`. `generate.py` resolves modules from a `_MODULES` registry keyed by a config `module:` field, so adding a solver = add a module + a config block. The two new solvers clone the validated Cahn–Hilliard semi-implicit Fourier scheme (implicit discrete-Laplacian stiff part, explicit nonlinearity, fresh-FFT-each-step Hermitian safety) but use `np.fft.fftn`/`ifftn` so one body serves 1D and 2D.

**Tech Stack:** Python 3.9, NumPy (`fftn`/`ifftn`), SciPy (`qmc` Latin-hypercube), h5py, matplotlib. Tests via pytest. Pure-numpy solvers run locally; PyClaw is NOT used in this plan.

## Global Constraints

These apply to **every** task (copied verbatim from the spec / CLAUDE.md):

- **LF = a real coarse *consistent* solve of the same PDE, on a coarser grid. NEVER downsampled or noised HF.** Every new solver MUST solve independently at each ladder resolution from the *same continuous IC* (coarse IC spectrally interpolated up), exactly as Cahn–Hilliard/KS do. No solver may produce LF by decimating/filtering an HF field.
- **Same solver, same dt, same continuous IC at every fidelity — only the grid changes.** (Consistency requirement; the dyadic ladder is 32→64→128 for 2D, and the deck's 1D convention 64→128→256 — resolutions come from config, do not hardcode.)
- **Condition vector must be complete and small** (≤ ~10 scalars; solver + vector + snapshot T fully determine the field).
- **Do NOT change the numerics of the validated solvers** (`cahn_hilliard._solve`, `kuramoto_sivashinsky._solve`, `euler._solve`). They were validated on the box 2026-06-15; this plan only adds plugin wrappers around them and factors out a character-identical helper.
- **Heavy/full generation runs on the box only.** This plan is light: solver *unit* tests use tiny grids + short T and run locally in `.venv`. Physics validation (is it actually sharp? bottom-rung?) happens in the box sample round (a later plan) per the compute policy — local tests assert structural correctness (shape, finiteness, determinism, ladder-IC consistency, dimension support), not physical sharpness.
- **Python 3.9 compatible**; every module keeps `from __future__ import annotations`.
- **Dependencies limited to** numpy, scipy, h5py, scikit-image, matplotlib, pyyaml (+ pytest test-only).
- **Figure text is matplotlib mathtext** (`r"$...$"`), never bare unicode; fidelity labels are `LF`/`IF`/`HF`, never "MF".
- **Git discipline:** `git pull` before editing; this is executed on a feature branch (`feat/solver-plumbing-parabolic`); commit after each task; commit messages end with `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`. Run commands with `source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate &&` prefixed (shell state does not persist between invocations).

**Depends on:** Plan 1 (`common/` dimension-agnostic refactor) — merged. `ladder`/`metrics`/`io`/`visualize` already accept 1D fields.

---

## File Structure

| File | Responsibility | Action |
|---|---|---|
| `mffp_sharp/src/mffp_sharp/common/spectral.py` | shared band-limited interp (1D+2D) + discrete −Laplacian symbol | **Create** |
| `mffp_sharp/src/mffp_sharp/pdes/cahn_hilliard.py` | CH solver (validated) | **Modify** — import `spectral_interp` from `common.spectral`, delete local copy; add `sample_configs`. `_solve` numerics unchanged. |
| `mffp_sharp/src/mffp_sharp/pdes/kuramoto_sivashinsky.py` | KS solver (validated) | **Modify** — import `spectral_interp`, delete local copy; add `sample_configs`. `_solve` numerics unchanged. |
| `mffp_sharp/src/mffp_sharp/pdes/euler.py` | Euler solver (box-only) | **Modify** — add `sample_configs`; read `gamma` from spec. `_solve` unchanged. |
| `mffp_sharp/src/mffp_sharp/pdes/allen_cahn.py` | Allen–Cahn solver (1D+2D) | **Create** |
| `mffp_sharp/src/mffp_sharp/pdes/fisher_kpp.py` | Fisher–KPP solver (1D+2D) | **Create** |
| `mffp_sharp/src/mffp_sharp/generate.py` | CLI generator | **Modify** — `_MODULES` registry + generic dataset loop driven by config `module:`/`ndim:` |
| `mffp_sharp/configs/sample.yaml` | sample-round config | **Modify** — add `module:`/`ndim:` to existing blocks; add allen_cahn_1d/2d + fisher_kpp_1d/2d blocks |
| `mffp_sharp/tests/` | unit tests | **Create** `test_spectral.py`, `test_allen_cahn.py`, `test_fisher_kpp.py`, `test_plumbing.py` |

**Plugin contract (every PDE module satisfies):**
```
NDIMS_SUPPORTED : tuple[int, ...]              # e.g. (1, 2) or (2,)
sample_configs(n, sampling_cfg, ndim, seed) -> list[spec dict]   # each spec carries "ndim" + "seed"
generate_sample(spec, resolutions, hf_res, output_time) -> ({res: field}, cond_vec: np.ndarray, names: list[str])
```
(This refines the spec's "`sample_<pde>_configs` in `sampling.py`" to a module-local `sample_configs`, keeping each plugin self-contained. Generic `latin_hypercube` stays in `common.sampling`.)

---

## Task 1: `common/spectral.py` — shared band-limited helpers

**Files:**
- Create: `mffp_sharp/src/mffp_sharp/common/spectral.py`
- Modify: `mffp_sharp/src/mffp_sharp/pdes/cahn_hilliard.py:45-55` (delete local `_spectral_interp`, import shared)
- Modify: `mffp_sharp/src/mffp_sharp/pdes/kuramoto_sivashinsky.py:40-50` (same)
- Test: `mffp_sharp/tests/test_spectral.py`

**Interfaces:**
- Produces:
  - `spectral_interp(field, n_fine) -> np.ndarray` — exact band-limited (zero-pad) interpolation of a periodic field to length/side `n_fine`; accepts 1D or 2D; `n_fine == n` returns a float64 copy; requires `(n_fine - n)` even (true for the dyadic ladder).
  - `neg_laplacian_symbol(res, h, ndim) -> np.ndarray` — discrete 5-point −Laplacian Fourier symbol (≥0, bounded; the consistent-coarse-solve symbol CH uses), shape `(res,)` for 1D or `(res, res)` for 2D.
- Consumes: nothing.
- CH/KS now import `spectral_interp` from here; their `_solve` is unchanged.

- [ ] **Step 1: Write the failing tests**

Create `mffp_sharp/tests/test_spectral.py`:

```python
import numpy as np

from mffp_sharp.common import spectral


def test_interp_1d_constant_preserved():
    f = np.full(8, 2.5)
    out = spectral.spectral_interp(f, 16)
    assert out.shape == (16,)
    assert np.allclose(out, 2.5)


def test_interp_1d_single_mode_resampled():
    n, nf = 16, 32
    x = (np.arange(n)) / n
    f = np.sin(2 * np.pi * x)               # mode k=1, exactly representable
    out = spectral.spectral_interp(f, nf)
    xf = (np.arange(nf)) / nf
    assert np.allclose(out, np.sin(2 * np.pi * xf), atol=1e-10)


def test_interp_1d_identity_when_same():
    f = np.linspace(0, 1, 8)
    out = spectral.spectral_interp(f, 8)
    assert out.shape == (8,) and np.allclose(out, f)


def test_interp_2d_constant_preserved():
    f = np.full((8, 8), 1.25)
    out = spectral.spectral_interp(f, 16)
    assert out.shape == (16, 16)
    assert np.allclose(out, 1.25)


def test_interp_unsupported_ndim_raises():
    import pytest
    with pytest.raises(ValueError):
        spectral.spectral_interp(np.zeros((2, 2, 2)), 4)


def test_neg_laplacian_symbol_1d_nonnegative_bounded():
    s = spectral.neg_laplacian_symbol(32, 1.0 / 32, ndim=1)
    assert s.shape == (32,)
    assert s.min() >= 0.0 and np.isfinite(s).all()
    assert np.isclose(s[0], 0.0)            # k=0 mode has zero Laplacian


def test_neg_laplacian_symbol_2d_shape():
    s = spectral.neg_laplacian_symbol(16, 1.0 / 16, ndim=2)
    assert s.shape == (16, 16)
    assert s.min() >= 0.0 and np.isclose(s[0, 0], 0.0)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate && cd /Users/nicholassung/Documents/SURF_2026/mffp_sharp && python -m pytest tests/test_spectral.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'mffp_sharp.common.spectral'`.

- [ ] **Step 3: Create `common/spectral.py`**

```python
"""Shared spectral helpers used by the Fourier-spectral PDE solvers.

Both Cahn-Hilliard and KS need the SAME band-limited up-interpolation so every
ladder level solves the identical continuous IC; it was duplicated in both solver
modules. Factored here and extended to 1D for the 1D spectral candidates. Also
provides the discrete (5-point) -Laplacian Fourier symbol that the semi-implicit
schemes diagonalize against (bounded -> no Gibbs blow-up on under-resolved coarse
grids; this is what makes the coarse solve a CONSISTENT solve, not an artifact).
"""
from __future__ import annotations

import numpy as np


def spectral_interp(field: np.ndarray, n_fine: int) -> np.ndarray:
    """Exact band-limited (zero-pad) interpolation of a periodic field to n_fine.

    1D -> length n_fine; 2D -> (n_fine, n_fine). `n_fine == n` returns a float64
    copy. Requires (n_fine - n) even (true for the dyadic ladder). Mirrors the
    original CH/KS 2D routine and applies the analogous 1D zero-pad.
    """
    field = np.asarray(field)
    if field.ndim == 1:
        n_c = field.shape[0]
        if n_fine == n_c:
            return field.astype(np.float64).copy()
        F = np.fft.fftshift(np.fft.fft(field))
        pad = (n_fine - n_c) // 2
        Fp = np.zeros(n_fine, dtype=complex)
        Fp[pad:pad + n_c] = F
        out = np.fft.ifft(np.fft.ifftshift(Fp)) * (n_fine / n_c)
        return np.real(out)
    if field.ndim == 2:
        n_c = field.shape[0]
        if n_fine == n_c:
            return field.astype(np.float64).copy()
        F = np.fft.fftshift(np.fft.fft2(field))
        pad = (n_fine - n_c) // 2
        Fp = np.zeros((n_fine, n_fine), dtype=complex)
        Fp[pad:pad + n_c, pad:pad + n_c] = F
        out = np.fft.ifft2(np.fft.ifftshift(Fp)) * (n_fine / n_c) ** 2
        return np.real(out)
    raise ValueError(f"unsupported field.ndim={field.ndim}; expected 1 or 2")


def neg_laplacian_symbol(res: int, h: float, ndim: int) -> np.ndarray:
    """Discrete (5-point) -Laplacian Fourier symbol: >= 0, bounded.

    Returns shape (res,) for ndim=1 or (res, res) for ndim=2. This is the same
    symbol Cahn-Hilliard diagonalizes against; using it (rather than the continuous
    k^2) keeps the coarse-grid solve bounded and consistent.
    """
    fr = np.fft.fftfreq(res)
    cx = np.cos(2 * np.pi * fr)
    if ndim == 1:
        return (2.0 / h ** 2) * (1.0 - cx)
    if ndim == 2:
        MX, MY = np.meshgrid(cx, cx, indexing="ij")
        return (2.0 / h ** 2) * (2.0 - MX - MY)
    raise ValueError(f"unsupported ndim={ndim}; expected 1 or 2")
```

- [ ] **Step 4: Point CH and KS at the shared helper**

In `mffp_sharp/src/mffp_sharp/pdes/cahn_hilliard.py`: delete the local `def _spectral_interp(...)` (lines 45-55) and add an import near the top (after `import numpy as np`):
```python
from ..common.spectral import spectral_interp
```
Then in `generate_sample`, change the call `_spectral_interp(ic_coarse, res)` to `spectral_interp(ic_coarse, res)`.

Do the identical change in `mffp_sharp/src/mffp_sharp/pdes/kuramoto_sivashinsky.py` (delete its `_spectral_interp` at lines 40-50, add the same import, update the call in `generate_sample`).

- [ ] **Step 5: Add a behavior-preservation test for CH/KS solves**

Append to `mffp_sharp/tests/test_spectral.py`:

```python
def test_ch_solve_still_runs_and_bounded():
    from mffp_sharp.pdes import cahn_hilliard as ch
    spec = {"eps": 0.03, "mobility": 1.0, "mean_composition": 0.0,
            "domain_size": 1.0, "seed": 0}
    fields, cond, names = ch.generate_sample(spec, [16, 32], 32, output_time=0.05)
    assert set(fields) == {16, 32}
    for f in fields.values():
        assert np.isfinite(f).all()
        assert np.abs(f).max() < 5.0           # bounded; phase field stays O(1)
    assert names == ["eps", "mobility", "mean_composition"]


def test_ch_solve_deterministic():
    from mffp_sharp.pdes import cahn_hilliard as ch
    spec = {"eps": 0.03, "mobility": 1.0, "mean_composition": 0.0,
            "domain_size": 1.0, "seed": 7}
    a = ch.generate_sample(spec, [16, 32], 32, 0.05)[0][32]
    b = ch.generate_sample(spec, [16, 32], 32, 0.05)[0][32]
    assert np.array_equal(a, b)


def test_ks_solve_still_runs_zero_mean():
    from mffp_sharp.pdes import kuramoto_sivashinsky as ks
    spec = {"L": 30.0, "ic_amplitude": 0.1, "seed": 1}
    fields, cond, names = ks.generate_sample(spec, [16, 32], 32, output_time=1.0)
    for f in fields.values():
        assert np.isfinite(f).all()
        assert abs(float(f.mean())) < 1e-8     # KS stores zero-mean fluctuation
```

- [ ] **Step 6: Run the suite**

Run: `source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate && cd /Users/nicholassung/Documents/SURF_2026/mffp_sharp && python -m pytest tests/test_spectral.py -q`
Expected: all PASS (the helper works; CH/KS still solve, bounded, deterministic, zero-mean).

Then the full suite (no regression from the refactor):
Run: `source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate && cd /Users/nicholassung/Documents/SURF_2026/mffp_sharp && python -m pytest tests/ -q`
Expected: all prior Plan-1 tests + the new ones PASS.

- [ ] **Step 7: Commit**

```bash
cd /Users/nicholassung/Documents/SURF_2026
git add mffp_sharp/src/mffp_sharp/common/spectral.py mffp_sharp/src/mffp_sharp/pdes/cahn_hilliard.py mffp_sharp/src/mffp_sharp/pdes/kuramoto_sivashinsky.py mffp_sharp/tests/test_spectral.py
git commit -m "feat(spectral): shared band-limited interp (1D+2D) + neg-Laplacian symbol; CH/KS reuse it

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 2: Generic registration plumbing in `generate.py`

**Files:**
- Modify: `mffp_sharp/src/mffp_sharp/generate.py` (replace `_specs_for` + `generate_pde` dispatch with a registry + config-driven loop)
- Modify: `mffp_sharp/src/mffp_sharp/pdes/cahn_hilliard.py`, `kuramoto_sivashinsky.py`, `euler.py` (add `sample_configs` + `NDIMS_SUPPORTED`; euler reads `gamma` from spec)
- Modify: `mffp_sharp/configs/sample.yaml` (add `module:` + `ndim:` to the three existing blocks)
- Test: `mffp_sharp/tests/test_plumbing.py`

**Interfaces:**
- Consumes: `common.sampling.latin_hypercube`; `common.spectral` (already wired).
- Produces:
  - Each existing module gains `NDIMS_SUPPORTED` and `sample_configs(n, sampling_cfg, ndim, seed) -> list[dict]`.
  - `generate.py` exposes `_MODULES: dict[str, module]` and `generate_dataset(name, block, top) -> summary`, iterating `top["pdes"]` (keyed by dataset name; each block has `module`, `ndim`, `output_time`, `sampling`).
  - `euler.generate_sample(spec, resolutions, hf_res, output_time)` now reads `spec.get("gamma", GAMMA)` (no `gamma=` kwarg needed); `sample_euler_configs` is wrapped by `euler.sample_configs`, which injects `gamma` and `ndim` into each spec.

- [ ] **Step 1: Write the failing tests**

Create `mffp_sharp/tests/test_plumbing.py`:

```python
import numpy as np

from mffp_sharp.pdes import cahn_hilliard, kuramoto_sivashinsky, euler


def test_ch_sample_configs_shape():
    cfg = {"eps_range": [0.02, 0.04], "mobility_range": [0.8, 1.2],
           "mean_composition_range": [-0.05, 0.05], "domain_size": 1.0}
    specs = cahn_hilliard.sample_configs(5, cfg, ndim=2, seed=0)
    assert len(specs) == 5
    for s in specs:
        assert s["ndim"] == 2 and "eps" in s and "seed" in s
    assert 2 in cahn_hilliard.NDIMS_SUPPORTED


def test_ks_sample_configs_shape():
    cfg = {"L_range": [22.0, 36.0], "ic_amplitude_range": [0.05, 0.2]}
    specs = kuramoto_sivashinsky.sample_configs(3, cfg, ndim=2, seed=1)
    assert len(specs) == 3 and all("L" in s for s in specs)


def test_euler_sample_configs_injects_gamma():
    cfg = {"jitter_frac": 0.1, "gamma": 1.4}
    specs = euler.sample_configs(4, cfg, ndim=2, seed=2)
    assert len(specs) == 4
    assert all(s["gamma"] == 1.4 and "quadrants" in s for s in specs)
    assert euler.NDIMS_SUPPORTED == (2,)


def test_registry_has_existing_modules():
    from mffp_sharp import generate
    for name in ("euler", "cahn_hilliard", "kuramoto_sivashinsky"):
        assert name in generate._MODULES


def test_generate_dataset_ch_end_to_end(tmp_path):
    from mffp_sharp import generate
    top = {
        "seed": 0, "out_dir": str(tmp_path), "n_samples_per_pde": 2, "n_figures": 0,
        "ladder": {"resolutions": [16, 32], "hf_index": 1},
        "metrics": ["rel_l2", "linf", "spectral_band"],
    }
    block = {"module": "cahn_hilliard", "ndim": 2, "output_time": 0.05,
             "sampling": {"eps_range": [0.03, 0.03], "mobility_range": [1.0, 1.0],
                          "mean_composition_range": [0.0, 0.0], "domain_size": 1.0}}
    summary = generate.generate_dataset("cahn_hilliard", block, top)
    assert summary["pde"] == "cahn_hilliard"
    assert (tmp_path / "cahn_hilliard_sample.h5").exists()
    assert 16 in summary["lf_vs_hf"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate && cd /Users/nicholassung/Documents/SURF_2026/mffp_sharp && python -m pytest tests/test_plumbing.py -q`
Expected: FAIL — `sample_configs`/`NDIMS_SUPPORTED`/`generate._MODULES`/`generate.generate_dataset` don't exist yet.

- [ ] **Step 3a: Add `sample_configs` + `NDIMS_SUPPORTED` to Cahn–Hilliard**

In `mffp_sharp/src/mffp_sharp/pdes/cahn_hilliard.py`, add near the top (after `from ..common.spectral import spectral_interp`):
```python
from ..common.sampling import latin_hypercube

NDIMS_SUPPORTED = (2,)
```
and add this function (above `generate_sample`):
```python
def sample_configs(n: int, sampling_cfg: dict, ndim: int, seed: int) -> list[dict]:
    """Draw n Cahn-Hilliard condition specs (Latin-hypercube over eps/mobility/mean)."""
    assert ndim in NDIMS_SUPPORTED, f"cahn_hilliard supports {NDIMS_SUPPORTED}, got {ndim}"
    draws = latin_hypercube(
        {"eps": tuple(sampling_cfg["eps_range"]),
         "mobility": tuple(sampling_cfg["mobility_range"]),
         "mean_composition": tuple(sampling_cfg["mean_composition_range"])}, n, seed)
    return [{"eps": draws["eps"][i], "mobility": draws["mobility"][i],
             "mean_composition": draws["mean_composition"][i],
             "domain_size": sampling_cfg["domain_size"], "ndim": ndim,
             "seed": seed + i} for i in range(n)]
```

- [ ] **Step 3b: Add `sample_configs` + `NDIMS_SUPPORTED` to KS**

In `mffp_sharp/src/mffp_sharp/pdes/kuramoto_sivashinsky.py`, add near the top:
```python
from ..common.sampling import latin_hypercube

NDIMS_SUPPORTED = (2,)
```
and add (above `generate_sample`):
```python
def sample_configs(n: int, sampling_cfg: dict, ndim: int, seed: int) -> list[dict]:
    """Draw n KS condition specs (Latin-hypercube over L / ic_amplitude)."""
    assert ndim in NDIMS_SUPPORTED, f"kuramoto_sivashinsky supports {NDIMS_SUPPORTED}, got {ndim}"
    draws = latin_hypercube(
        {"L": tuple(sampling_cfg["L_range"]),
         "ic_amplitude": tuple(sampling_cfg["ic_amplitude_range"])}, n, seed)
    return [{"L": draws["L"][i], "ic_amplitude": draws["ic_amplitude"][i],
             "ndim": ndim, "seed": seed + i} for i in range(n)]
```

- [ ] **Step 3c: Add `sample_configs` + `NDIMS_SUPPORTED` to Euler; read gamma from spec**

In `mffp_sharp/src/mffp_sharp/pdes/euler.py`, add (after `from __future__ ...`/imports and the `GAMMA = 1.4` line):
```python
from ..common.sampling import sample_euler_configs

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
```
Then change `generate_sample`'s signature from
`def generate_sample(spec, resolutions, hf_res, output_time, gamma=GAMMA):` to
`def generate_sample(spec, resolutions, hf_res, output_time):` and, as its first line, set
`gamma = spec.get("gamma", GAMMA)`. The rest of the body is unchanged (it already uses `gamma`).

- [ ] **Step 3d: Replace the dispatch in `generate.py` with a registry loop**

In `mffp_sharp/src/mffp_sharp/generate.py`:

Replace the `_PDES` dict (lines 26-30) with:
```python
from .pdes import euler, cahn_hilliard, kuramoto_sivashinsky

_MODULES = {
    "euler": euler,
    "cahn_hilliard": cahn_hilliard,
    "kuramoto_sivashinsky": kuramoto_sivashinsky,
}
```
Delete `_specs_for` (lines 33-50) entirely. Replace `generate_pde` (lines 53-102) with `generate_dataset`:
```python
def generate_dataset(name: str, block: dict, top: dict) -> dict:
    """Generate one dataset's sample batch; return a metric summary for review.

    `name` is the dataset name (output filename + figure label). `block` is its
    config: {module, ndim, output_time, sampling}.
    """
    mod = _MODULES[block["module"]]
    resolutions = top["ladder"]["resolutions"]
    hf_res = resolutions[top["ladder"]["hf_index"]]
    n = top["n_samples_per_pde"]
    seed = top["seed"]
    T = block["output_time"]
    ndim = int(block.get("ndim", 2))

    specs = mod.sample_configs(n, block["sampling"], ndim, seed)
    samples, conds, names = [], [], None
    per_lf_metrics = {res: [] for res in resolutions if res != hf_res}

    for i, spec in enumerate(specs):
        raw, cond, names = mod.generate_sample(spec, resolutions, hf_res, T)
        bundle = ladder.assemble_sample(raw, hf_res)
        samples.append(bundle)
        conds.append(cond)
        hf = bundle["aligned"][hf_res]
        for res in per_lf_metrics:
            per_lf_metrics[res].append(
                metrics.evaluate(bundle["aligned"][res], hf, top["metrics"]))
        print(f"  [{name}] sample {i+1}/{n} done", flush=True)

    os.makedirs(top["out_dir"], exist_ok=True)
    out_path = os.path.join(top["out_dir"], f"{name}_sample.h5")
    io.write_dataset(out_path, name, samples, np.array(conds), names,
                     resolutions, hf_res, T, seed)

    n_figs = min(int(top.get("n_figures", 3)), n)
    if n_figs > 0:
        fig_dir = os.path.join(top["out_dir"], "figures")
        os.makedirs(fig_dir, exist_ok=True)
        for i in range(n_figs):
            try:
                visualize.one_pager(samples[i], resolutions, hf_res, top["metrics"],
                                    block["module"], i,
                                    os.path.join(fig_dir, f"{name}_sample{i}.png"),
                                    condition=conds[i], condition_names=names)
            except Exception as e:
                print(f"  [{name}] figure {i} failed: {e}", flush=True)

    summary = {"pde": name, "out_path": out_path, "hf_res": hf_res, "n": n,
               "lf_vs_hf": {res: {m: float(np.mean([d[m] for d in rows]))
                                  for m in top["metrics"]}
                            for res, rows in per_lf_metrics.items()}}
    return summary
```
Update `main()` (and `replot_pde`): replace references to `_PDES`/`generate_pde` with the config-driven loop. The new `main` body:
```python
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--pde", default="all")
    args = ap.parse_args()
    with open(args.config) as f:
        top = yaml.safe_load(f)
    names = list(top["pdes"]) if args.pde == "all" else [args.pde]
    summaries = []
    for name in names:
        print(f"=== generating {name} ===", flush=True)
        summaries.append(generate_dataset(name, top["pdes"][name], top))
    sum_path = os.path.join(top["out_dir"], "sample_summary.json")
    with open(sum_path, "w") as f:
        json.dump(summaries, f, indent=2)
    print(f"\nwrote {sum_path}")
    for s in summaries:
        print(f"  {s['pde']}:")
        for res, m in s["lf_vs_hf"].items():
            print(f"    res {res:>3} vs HF: rel_l2={m.get('rel_l2'):.4f} "
                  f"linf={m.get('linf'):.4f} spectral_band={m.get('spectral_band'):.4f}")


if __name__ == "__main__":
    main()
```
(Remove the now-unused `--replot`/`replot_pde` path and the `from .common import sampling` import if it is no longer referenced — `sampling` is now used only inside the pde modules. Leave the other `from .common import ...` imports.)

- [ ] **Step 3e: Add `module:`/`ndim:` to the existing config blocks**

In `mffp_sharp/configs/sample.yaml`, add to each of the `euler`, `cahn_hilliard`, `kuramoto_sivashinsky` blocks (alongside `role:`):
```yaml
    module: euler          # (or cahn_hilliard / kuramoto_sivashinsky)
    ndim: 2
```
For `euler`, also move `gamma: 1.4` *into* the `sampling:` sub-block (so `sample_configs` reads it from `sampling_cfg`), i.e. add `gamma: 1.4` under `sampling:` and keep or remove the top-level `gamma` (the loop no longer reads it).

- [ ] **Step 4: Run tests to verify they pass**

Run: `source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate && cd /Users/nicholassung/Documents/SURF_2026/mffp_sharp && python -m pytest tests/test_plumbing.py -q`
Expected: all 5 PASS.

Then byte-compile + full suite:
Run: `source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate && cd /Users/nicholassung/Documents/SURF_2026/mffp_sharp && python -m compileall src/mffp_sharp -q && echo OK && python -m pytest tests/ -q`
Expected: `OK`, all tests PASS.

- [ ] **Step 5: Commit**

```bash
cd /Users/nicholassung/Documents/SURF_2026
git add mffp_sharp/src/mffp_sharp/generate.py mffp_sharp/src/mffp_sharp/pdes/*.py mffp_sharp/configs/sample.yaml mffp_sharp/tests/test_plumbing.py
git commit -m "feat(generate): registry-driven plugin loop; sample_configs per PDE module

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 3: Allen–Cahn solver (1D + 2D)

**Files:**
- Create: `mffp_sharp/src/mffp_sharp/pdes/allen_cahn.py`
- Modify: `mffp_sharp/src/mffp_sharp/generate.py` (register `allen_cahn` in `_MODULES`)
- Modify: `mffp_sharp/configs/sample.yaml` (add `allen_cahn_1d` + `allen_cahn_2d` blocks)
- Test: `mffp_sharp/tests/test_allen_cahn.py`

**Interfaces:**
- Consumes: `common.spectral.spectral_interp`, `common.spectral.neg_laplacian_symbol`, `common.sampling.latin_hypercube`.
- Produces: `NDIMS_SUPPORTED = (1, 2)`; `sample_configs(n, sampling_cfg, ndim, seed)`; `generate_sample(spec, resolutions, hf_res, output_time) -> ({res: field}, cond, names)` with `names == ["eps", "mobility", "mean_composition"]`. Fields are shape `(res,)` (1D) or `(res, res)` (2D).

Allen–Cahn: $\partial_t u = M\big(\varepsilon^2\nabla^2 u - (u^3 - u)\big)$. Single non-conserved phase field; interfaces of width $\sim\varepsilon$ between $u=\pm1$. Semi-implicit Fourier (clone of CH): implicit stiff diffusion $-M\varepsilon^2$(−Laplacian symbol), explicit reaction $-M(u^3-u)$, fresh FFT each step (Hermitian-safe), discrete-Laplacian symbol (consistent coarse solve). `np.fft.fftn`/`ifftn` serve 1D and 2D with one body.

- [ ] **Step 1: Write the failing tests**

Create `mffp_sharp/tests/test_allen_cahn.py`:

```python
import numpy as np

from mffp_sharp.pdes import allen_cahn as ac


def _spec(ndim, seed=0):
    return {"eps": 0.05, "mobility": 1.0, "mean_composition": 0.0,
            "domain_size": 1.0, "ndim": ndim, "seed": seed}


def test_2d_fields_shapes_and_finite():
    fields, cond, names = ac.generate_sample(_spec(2), [16, 32], 32, output_time=0.05)
    assert set(fields) == {16, 32}
    assert fields[16].shape == (16, 16) and fields[32].shape == (32, 32)
    for f in fields.values():
        assert np.isfinite(f).all() and np.abs(f).max() < 5.0
    assert names == ["eps", "mobility", "mean_composition"]
    assert cond.shape == (3,)


def test_1d_fields_shapes_and_finite():
    fields, cond, names = ac.generate_sample(_spec(1), [32, 64], 64, output_time=0.05)
    assert fields[32].shape == (32,) and fields[64].shape == (64,)
    for f in fields.values():
        assert np.isfinite(f).all()


def test_ladder_shares_one_continuous_ic():
    # The coarse IC spectrally interpolated up == the IC the finer level starts from,
    # so a near-zero output_time leaves the fields ~equal up to interpolation.
    fields = ac.generate_sample(_spec(2, seed=3), [16, 32], 32, output_time=1e-6)[0]
    from mffp_sharp.common.spectral import spectral_interp
    assert np.allclose(spectral_interp(fields[16], 32), fields[32], atol=1e-3)


def test_deterministic():
    a = ac.generate_sample(_spec(1, seed=5), [32, 64], 64, 0.05)[0][64]
    b = ac.generate_sample(_spec(1, seed=5), [32, 64], 64, 0.05)[0][64]
    assert np.array_equal(a, b)


def test_sample_configs():
    cfg = {"eps_range": [0.02, 0.05], "mobility_range": [1.0, 1.0],
           "mean_composition_range": [-0.1, 0.1], "domain_size": 1.0}
    specs = ac.sample_configs(4, cfg, ndim=1, seed=0)
    assert len(specs) == 4 and all(s["ndim"] == 1 for s in specs)
    assert ac.NDIMS_SUPPORTED == (1, 2)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate && cd /Users/nicholassung/Documents/SURF_2026/mffp_sharp && python -m pytest tests/test_allen_cahn.py -q`
Expected: FAIL — module `allen_cahn` doesn't exist.

- [ ] **Step 3: Create `pdes/allen_cahn.py`**

```python
"""Allen-Cahn (sharp interface, NON-conserved phase field) dataset generation.

Allen-Cahn:  d u/dt = M ( eps^2 * laplace(u) - (u^3 - u) ).
Thin interfaces of width ~eps between u = +/-1. Unlike Cahn-Hilliard the order
parameter is NOT conserved (the bulk relaxes to the nearer well), and the PDE is
2nd order, so it is milder than CH. Tagged 'near-CH' in the build set.

SOLVER: semi-implicit Fourier, cloned from the validated Cahn-Hilliard scheme:
  - the stiff diffusion -M eps^2 (-laplace) is treated IMPLICITLY, diagonalized by
    FFT against the DISCRETE 5-point -laplacian symbol (bounded -> consistent on the
    under-resolved coarse grid, no Gibbs blow-up);
  - the reaction -M(u^3 - u) is explicit;
  - the field is re-FFT'd from the real state each step (stays Hermitian).
np.fft.fftn/ifftn serve 1D and 2D with one body. SAME dt at every resolution.

dt is provisional (validate stability across the ladder on the box). IC: band-limited
random field on the coarsest grid, spectrally interpolated up so every ladder level
solves the IDENTICAL continuous IC.

Field stored: u at fixed output time T.
"""
from __future__ import annotations

import numpy as np

from ..common.spectral import spectral_interp, neg_laplacian_symbol
from ..common.sampling import latin_hypercube

NDIMS_SUPPORTED = (1, 2)

# Fixed timestep, same at every resolution. Conservative; 1st order in dt. (TBD-box.)
_DT = 1.0e-3


def _solve(u0: np.ndarray, eps: float, mobility: float, domain_size: float,
           output_time: float, dt: float = _DT) -> np.ndarray:
    """Semi-implicit Fourier Allen-Cahn solve from u0 (1D or 2D); return u."""
    res = u0.shape[0]
    h = domain_size / res
    mlap = neg_laplacian_symbol(res, h, u0.ndim)          # >= 0, bounded
    nsteps = int(np.ceil(output_time / dt))
    dt = output_time / nsteps                              # land exactly on T
    denom = 1.0 / dt + mobility * eps ** 2 * mlap          # implicit diffusion
    u = u0.astype(np.float64).copy()
    for _ in range(nsteps):
        uh = np.fft.fftn(u)                               # FRESH each step -> Hermitian
        reaction = mobility * (u ** 3 - u)                # explicit double-well force
        uh_new = (uh * (1.0 / dt) - np.fft.fftn(reaction)) / denom
        u = np.real(np.fft.ifftn(uh_new))
    return u


def sample_configs(n: int, sampling_cfg: dict, ndim: int, seed: int) -> list[dict]:
    """Draw n Allen-Cahn condition specs (Latin-hypercube over eps/mobility/mean)."""
    assert ndim in NDIMS_SUPPORTED, f"allen_cahn supports {NDIMS_SUPPORTED}, got {ndim}"
    draws = latin_hypercube(
        {"eps": tuple(sampling_cfg["eps_range"]),
         "mobility": tuple(sampling_cfg["mobility_range"]),
         "mean_composition": tuple(sampling_cfg["mean_composition_range"])}, n, seed)
    return [{"eps": draws["eps"][i], "mobility": draws["mobility"][i],
             "mean_composition": draws["mean_composition"][i],
             "domain_size": sampling_cfg["domain_size"], "ndim": ndim,
             "seed": seed + i} for i in range(n)]


def generate_sample(spec: dict, resolutions: list[int], hf_res: int, output_time: float
                    ) -> tuple[dict[int, np.ndarray], np.ndarray, list[str]]:
    """Generate one Allen-Cahn sample across the fidelity ladder (1D or 2D)."""
    ndim = int(spec["ndim"])
    res_min = min(resolutions)
    rng = np.random.default_rng(spec["seed"])
    shape = (res_min,) * ndim
    ic_coarse = spec["mean_composition"] + 0.1 * (2 * rng.random(shape) - 1)
    fields = {
        res: _solve(spectral_interp(ic_coarse, res), spec["eps"], spec["mobility"],
                    spec["domain_size"], output_time)
        for res in resolutions
    }
    cond = np.array([spec["eps"], spec["mobility"], spec["mean_composition"]],
                    dtype=np.float64)
    names = ["eps", "mobility", "mean_composition"]
    return fields, cond, names
```

- [ ] **Step 4: Register the module and add config blocks**

In `mffp_sharp/src/mffp_sharp/generate.py`, add `allen_cahn` to imports and `_MODULES`:
```python
from .pdes import euler, cahn_hilliard, kuramoto_sivashinsky, allen_cahn
```
```python
    "allen_cahn": allen_cahn,
```
In `mffp_sharp/configs/sample.yaml`, add two blocks under `pdes:`:
```yaml
  allen_cahn_2d:
    role: interface
    module: allen_cahn
    ndim: 2
    output_time: 0.5            # T: interfaces formed, pre-full-relaxation (TBD-box)
    sampling:
      eps_range: [0.02, 0.05]   # provisional; couple to ladder in sample round (TBD)
      mobility_range: [0.5, 1.5]
      mean_composition_range: [-0.1, 0.1]
      domain_size: 1.0
  allen_cahn_1d:
    role: interface
    module: allen_cahn
    ndim: 1
    output_time: 0.5
    sampling:
      eps_range: [0.01, 0.03]   # 1D ladder (64/128/256) resolves finer eps (TBD)
      mobility_range: [0.5, 1.5]
      mean_composition_range: [-0.1, 0.1]
      domain_size: 1.0
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate && cd /Users/nicholassung/Documents/SURF_2026/mffp_sharp && python -m pytest tests/test_allen_cahn.py -q`
Expected: all 5 PASS.

Then confirm the dataset runs end-to-end through the registry (1D + 2D) and the full suite is green:
Run: `source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate && cd /Users/nicholassung/Documents/SURF_2026/mffp_sharp && python -c "from mffp_sharp import generate; import tempfile,os; d=tempfile.mkdtemp(); top={'seed':0,'out_dir':d,'n_samples_per_pde':2,'n_figures':0,'ladder':{'resolutions':[16,32],'hf_index':1},'metrics':['rel_l2','linf','spectral_band']}; b1={'module':'allen_cahn','ndim':1,'output_time':0.05,'sampling':{'eps_range':[0.02,0.02],'mobility_range':[1.0,1.0],'mean_composition_range':[0.0,0.0],'domain_size':1.0}}; print(generate.generate_dataset('allen_cahn_1d',b1,top)['pde']); print(os.path.exists(os.path.join(d,'allen_cahn_1d_sample.h5')))" && python -m pytest tests/ -q`
Expected: prints `allen_cahn_1d` then `True`; full suite PASS.

- [ ] **Step 6: Commit**

```bash
cd /Users/nicholassung/Documents/SURF_2026
git add mffp_sharp/src/mffp_sharp/pdes/allen_cahn.py mffp_sharp/src/mffp_sharp/generate.py mffp_sharp/configs/sample.yaml mffp_sharp/tests/test_allen_cahn.py
git commit -m "feat(allen_cahn): dimension-aware semi-implicit Fourier solver (1D+2D)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 4: Fisher–KPP solver (1D + 2D)

**Files:**
- Create: `mffp_sharp/src/mffp_sharp/pdes/fisher_kpp.py`
- Modify: `mffp_sharp/src/mffp_sharp/generate.py` (register `fisher_kpp`)
- Modify: `mffp_sharp/configs/sample.yaml` (add `fisher_kpp_1d` + `fisher_kpp_2d` blocks)
- Test: `mffp_sharp/tests/test_fisher_kpp.py`

**Interfaces:**
- Consumes: `common.spectral.spectral_interp`, `common.spectral.neg_laplacian_symbol`, `common.sampling.latin_hypercube`.
- Produces: `NDIMS_SUPPORTED = (1, 2)`; `sample_configs(n, sampling_cfg, ndim, seed)`; `generate_sample(...)` with `names == ["D", "r"]`. Field values stay in approximately `[0, 1]` (KPP saturates at the carrying capacity `u=1`).

Fisher–KPP: $\partial_t u = D\nabla^2 u + r\,u(1-u)$. Sharp invasion fronts of width $\sim\sqrt{D/r}$, speed $2\sqrt{Dr}$, between the unstable state $u=0$ and stable $u=1$. Semi-implicit Fourier: implicit diffusion $-D$(−Laplacian symbol), explicit logistic reaction $r\,u(1-u)$. The reaction keeps $u\in[0,1]$ for small dt; clip to `[0,1]` after each step as a safety net (documented).

- [ ] **Step 1: Write the failing tests**

Create `mffp_sharp/tests/test_fisher_kpp.py`:

```python
import numpy as np

from mffp_sharp.pdes import fisher_kpp as fk


def _spec(ndim, seed=0):
    return {"D": 1e-4, "r": 10.0, "domain_size": 1.0, "ndim": ndim, "seed": seed}


def test_2d_shapes_finite_and_bounded():
    fields, cond, names = fk.generate_sample(_spec(2), [16, 32], 32, output_time=0.02)
    assert fields[16].shape == (16, 16) and fields[32].shape == (32, 32)
    for f in fields.values():
        assert np.isfinite(f).all()
        assert f.min() >= -1e-6 and f.max() <= 1.0 + 1e-6     # logistic stays in [0,1]
    assert names == ["D", "r"] and cond.shape == (2,)


def test_1d_shapes_finite():
    fields = fk.generate_sample(_spec(1), [32, 64], 64, output_time=0.02)[0]
    assert fields[32].shape == (32,) and fields[64].shape == (64,)
    for f in fields.values():
        assert np.isfinite(f).all()


def test_deterministic():
    a = fk.generate_sample(_spec(1, seed=2), [32, 64], 64, 0.02)[0][64]
    b = fk.generate_sample(_spec(1, seed=2), [32, 64], 64, 0.02)[0][64]
    assert np.array_equal(a, b)


def test_sample_configs():
    cfg = {"D_range": [1e-4, 1e-3], "r_range": [5.0, 20.0], "domain_size": 1.0}
    specs = fk.sample_configs(3, cfg, ndim=2, seed=1)
    assert len(specs) == 3 and all(s["ndim"] == 2 for s in specs)
    assert fk.NDIMS_SUPPORTED == (1, 2)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate && cd /Users/nicholassung/Documents/SURF_2026/mffp_sharp && python -m pytest tests/test_fisher_kpp.py -q`
Expected: FAIL — module `fisher_kpp` doesn't exist.

- [ ] **Step 3: Create `pdes/fisher_kpp.py`**

```python
"""Fisher-KPP (sharp traveling front) dataset generation.

Fisher-KPP:  d u/dt = D * laplace(u) + r * u (1 - u).
Invasion fronts of width ~sqrt(D/r) and speed 2 sqrt(D r) between the unstable
state u=0 and the stable carrying capacity u=1. Small D/r -> thin (sharp) front;
the LF coarse grid under-resolves it (bottom rung). Tagged 'semi-distinct'.

SOLVER: semi-implicit Fourier (same family as Cahn-Hilliard/Allen-Cahn):
  - implicit diffusion -D (-laplace), diagonalized against the DISCRETE -laplacian
    symbol (bounded -> consistent coarse solve);
  - explicit logistic reaction r u(1-u);
  - fresh FFT each step (Hermitian-safe); np.fft.fftn/ifftn serve 1D and 2D.
The logistic reaction keeps u in [0,1] for small dt; we clip to [0,1] after each
step as a safety net against round-off excursions. SAME dt at every resolution.

dt is provisional (validate on the box). IC: band-limited random field in [0,1] on
the coarsest grid, spectrally interpolated up -> identical continuous IC per level.

Field stored: u at fixed output time T (front developed, pre-domain-fill).
"""
from __future__ import annotations

import numpy as np

from ..common.spectral import spectral_interp, neg_laplacian_symbol
from ..common.sampling import latin_hypercube

NDIMS_SUPPORTED = (1, 2)

# Fixed timestep, same at every resolution. Conservative; 1st order in dt. (TBD-box.)
_DT = 1.0e-4


def _solve(u0: np.ndarray, D: float, r: float, domain_size: float,
           output_time: float, dt: float = _DT) -> np.ndarray:
    """Semi-implicit Fourier Fisher-KPP solve from u0 (1D or 2D); return u in [0,1]."""
    res = u0.shape[0]
    h = domain_size / res
    mlap = neg_laplacian_symbol(res, h, u0.ndim)          # >= 0, bounded
    nsteps = int(np.ceil(output_time / dt))
    dt = output_time / nsteps                              # land exactly on T
    denom = 1.0 / dt + D * mlap                            # implicit diffusion
    u = np.clip(u0.astype(np.float64), 0.0, 1.0).copy()
    for _ in range(nsteps):
        uh = np.fft.fftn(u)                               # FRESH each step -> Hermitian
        reaction = r * u * (1.0 - u)                      # explicit logistic
        uh_new = (uh * (1.0 / dt) + np.fft.fftn(reaction)) / denom
        u = np.clip(np.real(np.fft.ifftn(uh_new)), 0.0, 1.0)
    return u


def sample_configs(n: int, sampling_cfg: dict, ndim: int, seed: int) -> list[dict]:
    """Draw n Fisher-KPP condition specs (Latin-hypercube over D / r)."""
    assert ndim in NDIMS_SUPPORTED, f"fisher_kpp supports {NDIMS_SUPPORTED}, got {ndim}"
    draws = latin_hypercube(
        {"D": tuple(sampling_cfg["D_range"]),
         "r": tuple(sampling_cfg["r_range"])}, n, seed)
    return [{"D": draws["D"][i], "r": draws["r"][i],
             "domain_size": sampling_cfg["domain_size"], "ndim": ndim,
             "seed": seed + i} for i in range(n)]


def generate_sample(spec: dict, resolutions: list[int], hf_res: int, output_time: float
                    ) -> tuple[dict[int, np.ndarray], np.ndarray, list[str]]:
    """Generate one Fisher-KPP sample across the fidelity ladder (1D or 2D)."""
    ndim = int(spec["ndim"])
    res_min = min(resolutions)
    rng = np.random.default_rng(spec["seed"])
    shape = (res_min,) * ndim
    ic_coarse = 0.5 + 0.5 * (2 * rng.random(shape) - 1)   # random in [0,1]
    fields = {
        res: _solve(spectral_interp(ic_coarse, res), spec["D"], spec["r"],
                    spec["domain_size"], output_time)
        for res in resolutions
    }
    cond = np.array([spec["D"], spec["r"]], dtype=np.float64)
    names = ["D", "r"]
    return fields, cond, names
```

- [ ] **Step 4: Register the module and add config blocks**

In `mffp_sharp/src/mffp_sharp/generate.py`, add `fisher_kpp` to imports and `_MODULES`:
```python
from .pdes import euler, cahn_hilliard, kuramoto_sivashinsky, allen_cahn, fisher_kpp
```
```python
    "fisher_kpp": fisher_kpp,
```
In `mffp_sharp/configs/sample.yaml`, add under `pdes:`:
```yaml
  fisher_kpp_2d:
    role: front
    module: fisher_kpp
    ndim: 2
    output_time: 0.05           # T: front developed, pre-domain-fill (TBD-box)
    sampling:
      D_range: [1.0e-4, 1.0e-3] # small D/r -> thin front; couple to ladder (TBD)
      r_range: [5.0, 20.0]
      domain_size: 1.0
  fisher_kpp_1d:
    role: front
    module: fisher_kpp
    ndim: 1
    output_time: 0.05
    sampling:
      D_range: [1.0e-5, 1.0e-4]
      r_range: [5.0, 20.0]
      domain_size: 1.0
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate && cd /Users/nicholassung/Documents/SURF_2026/mffp_sharp && python -m pytest tests/test_fisher_kpp.py -q`
Expected: all 4 PASS.

Then byte-compile + full suite:
Run: `source /Users/nicholassung/Documents/SURF_2026/.venv/bin/activate && cd /Users/nicholassung/Documents/SURF_2026/mffp_sharp && python -m compileall src/mffp_sharp -q && echo OK && python -m pytest tests/ -q`
Expected: `OK`; full suite PASS.

- [ ] **Step 6: Commit and push**

```bash
cd /Users/nicholassung/Documents/SURF_2026
git add mffp_sharp/src/mffp_sharp/pdes/fisher_kpp.py mffp_sharp/src/mffp_sharp/generate.py mffp_sharp/configs/sample.yaml mffp_sharp/tests/test_fisher_kpp.py
git commit -m "feat(fisher_kpp): dimension-aware semi-implicit Fourier solver (1D+2D)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
git push
```

---

## Self-Review

**1. Spec coverage** (against the spec's "Plugin contract", refactor table, and build set):
- Plugin contract (`generate_sample` + per-PDE config sampler) → Tasks 2–4 (refined to module-local `sample_configs`; deviation noted below). ✓
- `generate.py`/`sampling.py` "thread ndim" (Plan-1 self-review deferred this here) → Task 2 (config `ndim:` + spec `ndim` + dimension-aware solvers). ✓
- Shared spectral helper for 1D candidates → Task 1. ✓
- Build-set spectral solvers: **Allen–Cahn (B2)** → Task 3; **Fisher–KPP (B3)** → Task 4. ✓
- **Remaining build-set solvers are explicitly out of scope for this plan** (see "Scope / follow-on plans"). This is intentional, not a gap — each remaining group is a distinct solver-design effort, not a clone.

**2. Placeholder scan:** No "TBD"/"add error handling"/"write tests for the above". Provisional *physical* parameter ranges are flagged `(TBD-box)` in config (matching the existing repo convention of validating ranges in the box sample round) — these are data values to validate, not missing code. Every code step has complete code; every run step has a command + expected output.

**3. Type consistency:** `sample_configs(n, sampling_cfg, ndim, seed)` and `generate_sample(spec, resolutions, hf_res, output_time)` signatures are identical across all four modules and the `generate.generate_dataset` caller. `spectral_interp(field, n_fine)` / `neg_laplacian_symbol(res, h, ndim)` names and arities are stable from Task 1 onward. `_MODULES` keys (`euler`, `cahn_hilliard`, `kuramoto_sivashinsky`, `allen_cahn`, `fisher_kpp`) match the config `module:` values. Condition-vector `names` lists are fixed per module.

**Deviation from spec (intentional, flagged for the executor's controller):** the spec's plugin-contract line says "`sample_<pde>_configs(...)` in `sampling.py`." This plan instead puts `sample_configs` *in each PDE module* (importing the generic `latin_hypercube` from `common.sampling`), so each plugin is self-contained and `sampling.py` doesn't accrete per-PDE knowledge. If the controller prefers the literal spec, move the four `sample_configs` into `sampling.py` as `sample_<name>_configs` and have `generate.py` dispatch by name — but the module-local form is the cleaner registry design.

**Scope / follow-on plans (each a distinct effort, NOT a clone of this template):**
- **Plan 3 — remaining spectral solvers:** 1D KS (needs the validated 2D KS generalized to `fftn` + a 2D-output checksum-pin regression), Swift–Hohenberg (parabolic, single-field — closest to this plan), KdV (dispersive → integrating-factor/ETDRK), sine-Gordon (2nd-order in *time* → Strang-split leapfrog), NLS (complex field → split-step Fourier), Gray–Scott (coupled 2-field → ETDRK4 per The Well), phase-field crystal (stiff 6th-order). Group the homogeneous ones; the structurally-different ones each get their own task.
- **Plan 4 — PyClaw/WENO solvers (box-only):** Burgers, 1D Sod, shallow-water dam-break (PDEBench `gen_radial_dam_break` recipe), Buckley–Leverett. These clone `euler.py` and can only be validated on the box (clawpack); local tests cover `sample_configs`/registration only.
- **Plan 5 — special:** high-$k$ Helmholtz (steady-state sparse direct solve — dodges the time-stepping template entirely), porous-medium equation (degenerate, positivity-preserving FD).
- **Plan 6 — box sample generation + auto-screen + survivor menu** (the original Phase 3–5; heavy, box-only): run all built datasets, apply the sharpness screen (energy-above-cutoff floor + sharpness coordinate $s$ + LF–HF gap), emit one-pagers, hand Nicholas the ranked survivors.
