# `common/` Dimension-Agnostic Refactor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the four `mffp_sharp/common/` modules (`ladder`, `metrics`, `io`, `visualize`) accept **1D fields** as well as 2D, so 1D PDE candidates (KdV, 1D KS, Sod, Burgers, …) can flow through the existing generate → align → metric → one-pager → HDF5 pipeline unchanged for 2D.

**Architecture:** Branch each module on `field.ndim` (1 vs 2) rather than rewriting. 2D paths are preserved byte-for-byte; 1D paths are added beside them. The only genuinely new code is a 1D one-pager (line plots instead of heatmaps). A regression task locks the 2D behavior so the refactor cannot silently change the existing Euler/CH/KS outputs.

**Tech Stack:** Python 3.9, NumPy, SciPy (`RegularGridInterpolator`, `wasserstein_distance`), h5py, scikit-image (SSIM), matplotlib (Agg). Tests via pytest.

## Global Constraints

These apply to **every** task below (copied verbatim from the spec / CLAUDE.md):

- **LF = a real coarse consistent solve, NEVER downsampled/noised HF.** (Not exercised by this refactor, but no code here may introduce a downsample-as-LF path.)
- **2D behavior must not change.** The existing 2D Euler/CH/KS pipeline output is the regression baseline; any 2D-path edit must be behavior-preserving.
- **Figure text is matplotlib mathtext** (`r"$...$"`), never bare unicode/ASCII math.
- **Fidelity labels are `LF` / `IF` / `HF`**, never "MF".
- **Python 3.9 compatible** — every module keeps `from __future__ import annotations` so `dict[int, np.ndarray]`-style hints are legal.
- **Dependencies limited to** numpy, scipy, h5py, scikit-image, matplotlib, pyyaml (no new runtime deps).
- **Light work → run locally** in the repo `.venv` (`source .venv/bin/activate`). No box/GPU needed for this plan.
- **Git discipline:** `git pull` before editing, `git add -A && git commit && git push` after each task. Commit messages end with the `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>` trailer.

---

## File Structure

| File | Responsibility | Action |
|---|---|---|
| `mffp_sharp/src/mffp_sharp/common/ladder.py` | up-interpolate LF→HF; assemble per-sample bundle | Modify `upsample_to_hf` (add 1D branch); `assemble_sample` unchanged (already maps over fields) |
| `mffp_sharp/src/mffp_sharp/common/metrics.py` | metric panel comparing two same-grid fields | Modify `spectral_band`, `_boundary_count`, `ssim` (add 1D branches); `interface_position` becomes 1D-correct via `_boundary_count` |
| `mffp_sharp/src/mffp_sharp/common/io.py` | HDF5 read/write in the deck's layout | Modify `write_dataset` (store `ndim`/`spatial_shape` attrs); `read_dataset` (expose them). Field stacking already generic. |
| `mffp_sharp/src/mffp_sharp/common/visualize.py` | one-pager review figure + radial spectrum | Modify `radial_spectrum` (1D branch); split `one_pager` into a dispatcher + `_one_pager_2d` (renamed current body) + new `_one_pager_1d`; extract shared `_header_lines` |
| `mffp_sharp/tests/` (new) | pytest suite locking 1D + 2D behavior | Create `conftest.py`, `test_ladder.py`, `test_metrics.py`, `test_io.py`, `test_visualize.py`, `test_regression_2d.py` |

**Conventions to follow (already in the codebase):**
- Cell-center coordinates on the unit domain: `_cell_centers(n) = (np.arange(n) + 0.5) / n`.
- A "bundle" is `{"raw": {res: field}, "aligned": {res: field}, "hf_res": int}` (from `ladder.assemble_sample`).
- `field` is `np.ndarray`, shape `(R,)` for 1D or `(R, R)` for 2D.

---

## Task 0: Test harness setup

**Files:**
- Create: `mffp_sharp/tests/conftest.py`
- Create: `mffp_sharp/tests/__init__.py` (empty)

**Interfaces:**
- Consumes: nothing.
- Produces: pytest fixtures `ramp_1d`, `ramp_2d`, `bundle_1d`, `bundle_2d` used by later tasks.

- [ ] **Step 1: Ensure pytest is installed in the local venv**

Run:
```bash
source .venv/bin/activate && python -c "import pytest" 2>/dev/null || pip install pytest
```
Expected: pytest importable (either already present, or installed).

- [ ] **Step 2: Create the empty package marker**

Create `mffp_sharp/tests/__init__.py` with no content (empty file).

- [ ] **Step 3: Write shared fixtures**

Create `mffp_sharp/tests/conftest.py`:

```python
"""Shared fixtures for the common/ refactor tests."""
import numpy as np
import pytest

from mffp_sharp.common import ladder


@pytest.fixture
def ramp_1d():
    """A smooth 1D field on a 4-cell grid (linear ramp -> exact under linear interp)."""
    return np.linspace(0.0, 3.0, 4)


@pytest.fixture
def ramp_2d():
    """A smooth 2D field on a 4x4 grid (separable ramp)."""
    x = np.linspace(0.0, 3.0, 4)
    return np.add.outer(x, x)


@pytest.fixture
def bundle_1d(ramp_1d):
    """A two-level 1D bundle (res 4 -> HF 8) via the real ladder."""
    hf = np.linspace(0.0, 3.0, 8)
    return ladder.assemble_sample({4: ramp_1d, 8: hf}, hf_res=8)


@pytest.fixture
def bundle_2d(ramp_2d):
    """A two-level 2D bundle (res 4 -> HF 8) via the real ladder."""
    x = np.linspace(0.0, 3.0, 8)
    hf = np.add.outer(x, x)
    return ladder.assemble_sample({4: ramp_2d, 8: hf}, hf_res=8)
```

- [ ] **Step 4: Verify the harness collects**

Run: `cd mffp_sharp && python -m pytest tests/ -q`
Expected: `no tests ran` (0 tests collected, no collection errors). Fixtures import cleanly — this proves `assemble_sample` already accepts a 1D dict at import time even before the `upsample_to_hf` 1D branch lands (it will fail only when *invoked*, which the next task drives).

- [ ] **Step 5: Commit**

```bash
git add mffp_sharp/tests/__init__.py mffp_sharp/tests/conftest.py
git commit -m "test: add pytest harness + 1D/2D fixtures for common refactor

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 1: `ladder.py` — 1D up-interpolation

**Files:**
- Modify: `mffp_sharp/src/mffp_sharp/common/ladder.py:22-39` (`upsample_to_hf`)
- Test: `mffp_sharp/tests/test_ladder.py`

**Interfaces:**
- Consumes: `_cell_centers(n) -> np.ndarray` (unchanged).
- Produces: `upsample_to_hf(field, hf_res, order="linear") -> np.ndarray` now accepts `field.ndim in {1, 2}`; returns a field of shape `(hf_res,)` (1D) or `(hf_res, hf_res)` (2D). `assemble_sample(raw_fields, hf_res)` unchanged in signature, now works for 1D inputs.

- [ ] **Step 1: Write the failing tests**

Create `mffp_sharp/tests/test_ladder.py`:

```python
import numpy as np

from mffp_sharp.common import ladder


def test_1d_constant_preserved():
    f = np.full(4, 2.0)
    out = ladder.upsample_to_hf(f, 8)
    assert out.shape == (8,)
    assert np.allclose(out, 2.0)


def test_1d_linear_matches_np_interp():
    f = np.linspace(0.0, 3.0, 4)
    out = ladder.upsample_to_hf(f, 8)
    src = (np.arange(4) + 0.5) / 4
    dst = (np.arange(8) + 0.5) / 8
    assert np.allclose(out, np.interp(dst, src, f))


def test_1d_identity_when_same_res():
    f = np.linspace(0.0, 3.0, 4)
    out = ladder.upsample_to_hf(f, 4)
    assert out.shape == (4,)
    assert np.allclose(out, f)


def test_1d_nearest_order():
    f = np.array([0.0, 1.0, 2.0, 3.0])
    out = ladder.upsample_to_hf(f, 8, order="nearest")
    assert out.shape == (8,)
    assert set(np.unique(out)).issubset(set(f.tolist()))


def test_2d_unchanged_constant():
    f = np.full((4, 4), 2.0)
    out = ladder.upsample_to_hf(f, 8)
    assert out.shape == (8, 8)
    assert np.allclose(out, 2.0)


def test_assemble_sample_1d():
    b = ladder.assemble_sample({4: np.linspace(0, 3, 4), 8: np.linspace(0, 3, 8)}, 8)
    assert b["aligned"][4].shape == (8,)
    assert b["aligned"][8].shape == (8,)
    assert b["raw"][4].shape == (4,)


def test_unsupported_ndim_raises():
    import pytest
    with pytest.raises(ValueError):
        ladder.upsample_to_hf(np.zeros((2, 2, 2)), 4)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd mffp_sharp && python -m pytest tests/test_ladder.py -q`
Expected: the 1D tests FAIL (current `upsample_to_hf` asserts `field.shape == (res, res)`, so a 1D field raises `AssertionError`); `test_2d_unchanged_constant` PASSES.

- [ ] **Step 3: Implement the 1D branch**

Replace `upsample_to_hf` (lines 22-39) in `mffp_sharp/src/mffp_sharp/common/ladder.py` with:

```python
def upsample_to_hf(field: np.ndarray, hf_res: int, order: str = "linear") -> np.ndarray:
    """Interpolate an LF field up onto the HF grid.

    Accepts a 1D field (length res) or a square 2D field (res x res). Uses
    cell-center coordinates on the unit domain so LF and HF share the same physical
    domain. `order` is "linear" (default) or "nearest".

    1D uses np.interp (endpoint-clamped at the boundary cell centers); 2D uses
    RegularGridInterpolator with linear extrapolation, unchanged from before.
    """
    field = np.asarray(field, dtype=np.float64)

    if field.ndim == 1:
        res = field.shape[0]
        if res == hf_res:
            return field.copy()
        src = _cell_centers(res)
        dst = _cell_centers(hf_res)
        if order == "nearest":
            idx = np.clip(np.round(dst * res - 0.5).astype(int), 0, res - 1)
            return field[idx]
        return np.interp(dst, src, field)

    if field.ndim == 2:
        res = field.shape[0]
        assert field.shape == (res, res), f"expected square field, got {field.shape}"
        if res == hf_res:
            return field.copy()
        src = (_cell_centers(res), _cell_centers(res))
        interp = RegularGridInterpolator(
            src, field, method=order, bounds_error=False, fill_value=None
        )
        yy, xx = np.meshgrid(_cell_centers(hf_res), _cell_centers(hf_res), indexing="ij")
        pts = np.stack([yy.ravel(), xx.ravel()], axis=-1)
        return interp(pts).reshape(hf_res, hf_res)

    raise ValueError(f"unsupported field.ndim={field.ndim}; expected 1 or 2")
```

(Note: the old code cast inside the 2D branch via `field.astype(np.float64)`; the cast is now done once up front, so the 2D numerics are identical.)

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd mffp_sharp && python -m pytest tests/test_ladder.py -q`
Expected: all 7 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add mffp_sharp/src/mffp_sharp/common/ladder.py mffp_sharp/tests/test_ladder.py
git commit -m "feat(ladder): 1D up-interpolation via np.interp; 2D path preserved

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 2: `metrics.py` — 1D metric branches

**Files:**
- Modify: `mffp_sharp/src/mffp_sharp/common/metrics.py:29-50` (`spectral_band`), `:76-89` (`ssim`), `:104-110` (`_boundary_count`)
- Test: `mffp_sharp/tests/test_metrics.py`

**Interfaces:**
- Consumes: nothing new.
- Produces: `spectral_band`, `interface_position`, `conservation`, `rel_l2`, `linf`, `wasserstein1`, `ssim`, `evaluate` all accept 1D **or** 2D fields. `ssim` returns `nan` for 1D (skip, per spec). `_boundary_count(mask)` handles 1D and 2D. `rel_l2/linf/conservation/wasserstein1` are already dimension-agnostic (`.ravel()`/`.mean()`) — no change.

- [ ] **Step 1: Write the failing tests**

Create `mffp_sharp/tests/test_metrics.py`:

```python
import numpy as np

from mffp_sharp.common import metrics


def test_spectral_band_1d_identical_is_zero():
    ref = np.sin(np.linspace(0, 4 * np.pi, 64))
    assert metrics.spectral_band(ref, ref) == 0.0


def test_spectral_band_1d_nonzero_for_difference():
    ref = np.sin(np.linspace(0, 4 * np.pi, 64))
    pred = np.zeros_like(ref)
    v = metrics.spectral_band(pred, ref)
    assert np.isfinite(v) and v > 0.0


def test_spectral_band_2d_unchanged():
    rng = np.random.default_rng(0)
    ref = rng.standard_normal((16, 16))
    assert metrics.spectral_band(ref, ref) == 0.0


def test_boundary_count_1d():
    mask = np.array([False, False, True, True])
    assert metrics._boundary_count(mask) == 1


def test_boundary_count_2d_unchanged():
    mask = np.zeros((4, 4), dtype=bool)
    mask[2:, :] = True
    assert metrics._boundary_count(mask) == 4


def test_interface_position_1d_zero_when_identical():
    ref = np.array([0.0, 0.0, 1.0, 1.0])
    assert metrics.interface_position(ref, ref) == 0.0


def test_interface_position_1d_positive_when_shifted():
    ref = np.array([0.0, 0.0, 1.0, 1.0])
    pred = np.array([0.0, 1.0, 1.0, 1.0])
    assert metrics.interface_position(pred, ref) > 0.0


def test_ssim_1d_returns_nan():
    ref = np.linspace(0, 1, 32)
    assert np.isnan(metrics.ssim(ref, ref))


def test_evaluate_1d_panel_runs():
    ref = np.sin(np.linspace(0, 4 * np.pi, 64))
    pred = 0.9 * ref
    out = metrics.evaluate(pred, ref, ["rel_l2", "linf", "spectral_band",
                                       "interface_position", "conservation", "ssim"])
    assert set(out) == {"rel_l2", "linf", "spectral_band",
                        "interface_position", "conservation", "ssim"}
    assert np.isnan(out["ssim"])
    assert out["rel_l2"] > 0.0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd mffp_sharp && python -m pytest tests/test_metrics.py -q`
Expected: 1D tests touching `spectral_band` (uses `fft2` → wrong for 1D), `_boundary_count` (indexes `m[:-1, :]` → `IndexError` on 1D), and `ssim` (skimage SSIM on 1D → raises) FAIL; 2D tests PASS.

- [ ] **Step 3a: Make `spectral_band` dimension-agnostic**

Replace `spectral_band` (lines 29-50) with:

```python
def spectral_band(pred: np.ndarray, ref: np.ndarray, low_frac: float = 0.5) -> float:
    """High-wavenumber error as a fraction of the field's TOTAL spectral energy.

    Zeroes the lowest `low_frac` of (radial) wavenumbers and measures the L2 error in
    the remaining high band, normalized by the *total* energy of the reference.
    Works for 1D (fft) and 2D (fft2) fields.
    """
    pred = np.asarray(pred)
    ref = np.asarray(ref)
    n = ref.shape[0]
    if ref.ndim == 1:
        kr = np.abs(np.fft.fftfreq(n))
        fft = np.fft.fft
    elif ref.ndim == 2:
        ky = np.fft.fftfreq(n)[:, None]
        kx = np.fft.fftfreq(n)[None, :]
        kr = np.sqrt(ky**2 + kx**2)
        fft = np.fft.fft2
    else:
        raise ValueError(f"unsupported ndim={ref.ndim}; expected 1 or 2")

    mask = kr >= (low_frac * kr.max())            # keep high band only
    Fp = fft(pred) * mask
    Fr = fft(ref) * mask
    num = np.linalg.norm((Fp - Fr).ravel())
    den = np.linalg.norm(fft(ref).ravel()) + 1e-30   # TOTAL energy, not high-band
    return float(num / den)
```

- [ ] **Step 3b: Make `_boundary_count` dimension-agnostic**

Replace `_boundary_count` (lines 104-110) with:

```python
def _boundary_count(mask: np.ndarray) -> int:
    """Count cells on the boundary of a boolean mask (4-neighbour in 2D, 2-neighbour in 1D)."""
    m = np.asarray(mask)
    if m.ndim == 1:
        diff = np.zeros_like(m)
        diff[:-1] |= m[:-1] ^ m[1:]
        return int(diff.sum())
    diff = np.zeros_like(m)
    diff[:-1, :] |= m[:-1, :] ^ m[1:, :]
    diff[:, :-1] |= m[:, :-1] ^ m[:, 1:]
    return int(diff.sum())
```

(`interface_position` is unchanged — it calls `_boundary_count` and `np.logical_xor(...).sum()`, both now 1D-safe.)

- [ ] **Step 3c: Skip SSIM for non-2D fields**

Replace the body of `ssim` (lines 76-89) with:

```python
def ssim(pred: np.ndarray, ref: np.ndarray) -> float:
    """Structural similarity (1 = identical). Returns 1 - SSIM as an error.

    SSIM is defined via 2D windows; for 1D (or other non-2D) fields we return NaN so
    the panel still runs. Uses scikit-image if available; otherwise a NaN sentinel.
    """
    ref = np.asarray(ref)
    pred = np.asarray(pred)
    if ref.ndim != 2:
        return float("nan")
    try:
        from skimage.metrics import structural_similarity as _ssim
    except Exception:
        return float("nan")
    data_range = float(ref.max() - ref.min()) or 1.0
    val = _ssim(ref, pred, data_range=data_range)
    return float(1.0 - val)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd mffp_sharp && python -m pytest tests/test_metrics.py -q`
Expected: all tests PASS.

- [ ] **Step 5: Commit**

```bash
git add mffp_sharp/src/mffp_sharp/common/metrics.py mffp_sharp/tests/test_metrics.py
git commit -m "feat(metrics): 1D branches for spectral_band/_boundary_count; SSIM skips 1D

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 3: `io.py` — generic shape attrs + round-trip

**Files:**
- Modify: `mffp_sharp/src/mffp_sharp/common/io.py:43-67` (`write_dataset` attrs), `:79-93` (`read_dataset` return)
- Test: `mffp_sharp/tests/test_io.py`

**Interfaces:**
- Consumes: bundles in `{"raw", "aligned", "hf_res"}` shape (from `ladder.assemble_sample`).
- Produces: `write_dataset(...)` writes two new attrs — `ndim` (int) and `spatial_shape` (list[int]) — inferred from the HF aligned field of the first sample. `read_dataset(path)` returns a dict that additionally contains `"ndim"` and `"spatial_shape"`. Field datasets are written `[N, *spatial]` (already generic via `np.stack`).

- [ ] **Step 1: Write the failing tests**

Create `mffp_sharp/tests/test_io.py`:

```python
import numpy as np

from mffp_sharp.common import io, ladder


def _make_samples(ndim, n=3):
    samples, conds = [], []
    for i in range(n):
        if ndim == 1:
            raw = {4: np.linspace(0, 1, 4) + i, 8: np.linspace(0, 1, 8) + i}
        else:
            x = np.linspace(0, 1, 4) + i
            xh = np.linspace(0, 1, 8) + i
            raw = {4: np.add.outer(x, x), 8: np.add.outer(xh, xh)}
        samples.append(ladder.assemble_sample(raw, 8))
        conds.append([float(i), 0.5])
    return samples, np.array(conds)


def test_roundtrip_1d(tmp_path):
    samples, cond = _make_samples(1)
    p = str(tmp_path / "d1.h5")
    io.write_dataset(p, "toy1d", samples, cond, ["a", "b"], [4, 8], 8, 1.0, seed=0)
    d = io.read_dataset(p)
    assert d["ndim"] == 1
    assert list(d["spatial_shape"]) == [8]
    assert d["bundles"][0]["aligned"][8].shape == (8,)
    assert d["bundles"][0]["raw"][4].shape == (4,)
    assert np.allclose(d["condition"], cond)


def test_roundtrip_2d(tmp_path):
    samples, cond = _make_samples(2)
    p = str(tmp_path / "d2.h5")
    io.write_dataset(p, "toy2d", samples, cond, ["a", "b"], [4, 8], 8, 1.0, seed=0)
    d = io.read_dataset(p)
    assert d["ndim"] == 2
    assert list(d["spatial_shape"]) == [8, 8]
    assert d["bundles"][0]["aligned"][8].shape == (8, 8)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd mffp_sharp && python -m pytest tests/test_io.py -q`
Expected: `test_roundtrip_1d` and `test_roundtrip_2d` FAIL at `d["ndim"]` with `KeyError` (the attrs and read-side keys don't exist yet). The 1D *field* round-trip itself already works (stacking is generic) — only the new metadata is missing.

- [ ] **Step 3a: Write the new attrs in `write_dataset`**

In `mffp_sharp/src/mffp_sharp/common/io.py`, immediately after the existing line
`f.attrs["condition_names"] = [s.encode() for s in condition_names]` (line 50), add:

```python
        hf0 = np.asarray(samples[0]["aligned"][hf_res])
        f.attrs["ndim"] = int(hf0.ndim)
        f.attrs["spatial_shape"] = list(hf0.shape)
```

- [ ] **Step 3b: Expose them in `read_dataset`**

In `read_dataset`, inside the `with h5py.File(path, "r") as f:` block, after the line
`hf_res = int(f.attrs["hf_res"])` (line 80), add:

```python
        ndim = int(f.attrs.get("ndim", 2))
        spatial_shape = list(f.attrs.get("spatial_shape", [hf_res, hf_res]))
```

Then change the final `return` (lines 92-93) to include them:

```python
    return {"resolutions": resolutions, "hf_res": hf_res, "condition_names": names,
            "condition": condition, "bundles": bundles,
            "ndim": ndim, "spatial_shape": spatial_shape}
```

(The `.get(..., default)` calls keep `read_dataset` backward-compatible with any HDF5 written before this task.)

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd mffp_sharp && python -m pytest tests/test_io.py -q`
Expected: both tests PASS.

- [ ] **Step 5: Commit**

```bash
git add mffp_sharp/src/mffp_sharp/common/io.py mffp_sharp/tests/test_io.py
git commit -m "feat(io): store/read ndim + spatial_shape attrs; 1D field round-trip

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 4: `visualize.py` — 1D one-pager

**Files:**
- Modify: `mffp_sharp/src/mffp_sharp/common/visualize.py:45-55` (`radial_spectrum`), `:58-162` (`one_pager`)
- Test: `mffp_sharp/tests/test_visualize.py`

**Interfaces:**
- Consumes: a bundle from `ladder.assemble_sample`; `metrics.evaluate`.
- Produces:
  - `radial_spectrum(field) -> np.ndarray` accepts 1D (returns `|rfft|**2`, indexed by integer wavenumber `0..n//2`) or 2D (unchanged azimuthal average).
  - `one_pager(bundle, resolutions, hf_res, metric_names, pde, sample_idx, out_path, condition=None, condition_names=None) -> None` dispatches on the HF field's `ndim`: 2D → existing layout (now `_one_pager_2d`), 1D → new line-plot layout (`_one_pager_1d`). Both write a PNG to `out_path`.
  - `_header_lines(pde, sample_idx, resolutions, hf_res, aligned, metric_names, condition, condition_names) -> list[str]` shared suptitle builder.

- [ ] **Step 1: Write the failing tests**

Create `mffp_sharp/tests/test_visualize.py`:

```python
import os

import numpy as np

from mffp_sharp.common import ladder, visualize


def test_radial_spectrum_1d_shape_and_dc():
    f = np.sin(np.linspace(0, 4 * np.pi, 64))
    sp = visualize.radial_spectrum(f)
    assert sp.shape == (64 // 2 + 1,)
    # a pure sine has near-zero DC component
    assert sp[0] < sp.max()


def test_radial_spectrum_2d_unchanged():
    rng = np.random.default_rng(0)
    f = rng.standard_normal((16, 16))
    sp = visualize.radial_spectrum(f)
    assert sp.ndim == 1 and sp.shape[0] >= 8


def test_one_pager_1d_writes_png(tmp_path):
    raw = {4: np.linspace(0, 1, 4), 8: np.sin(np.linspace(0, 2 * np.pi, 8))}
    b = ladder.assemble_sample(raw, 8)
    out = str(tmp_path / "onepager_1d.png")
    visualize.one_pager(b, [4, 8], 8, ["rel_l2", "linf", "spectral_band",
                        "interface_position"], "kuramoto_sivashinsky", 0, out,
                        condition=[7.0, 0.1], condition_names=["L", "ic_amplitude"])
    assert os.path.exists(out) and os.path.getsize(out) > 0


def test_one_pager_2d_writes_png(tmp_path):
    x = np.linspace(0, 1, 4)
    xh = np.linspace(0, 1, 8)
    raw = {4: np.add.outer(x, x), 8: np.add.outer(xh, xh)}
    b = ladder.assemble_sample(raw, 8)
    out = str(tmp_path / "onepager_2d.png")
    visualize.one_pager(b, [4, 8], 8, ["rel_l2", "linf", "spectral_band",
                        "interface_position"], "cahn_hilliard", 0, out,
                        condition=[0.012, 1.0, 0.0],
                        condition_names=["eps", "mobility", "mean_composition"])
    assert os.path.exists(out) and os.path.getsize(out) > 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd mffp_sharp && python -m pytest tests/test_visualize.py -q`
Expected: `test_radial_spectrum_1d_shape_and_dc` FAILS (`fft2` on 1D raises) and `test_one_pager_1d_writes_png` FAILS (imshow of a 1D array / shape errors); the two 2D tests PASS.

- [ ] **Step 3a: Add the 1D branch to `radial_spectrum`**

Replace `radial_spectrum` (lines 45-55) with:

```python
def radial_spectrum(field: np.ndarray) -> np.ndarray:
    """Power spectrum vs wavenumber.

    1D: |rfft|**2, indexed by integer wavenumber 0..n//2.
    2D: azimuthally-averaged PSD vs radial wavenumber (unchanged).
    """
    field = np.asarray(field)
    if field.ndim == 1:
        return np.abs(np.fft.rfft(field)) ** 2
    F = np.fft.fftshift(np.fft.fft2(field))
    psd = np.abs(F) ** 2
    n = field.shape[0]
    cy, cx = n // 2, n // 2
    y, x = np.indices((n, n))
    r = np.hypot(x - cx, y - cy).astype(int)
    tbin = np.bincount(r.ravel(), psd.ravel())
    counts = np.bincount(r.ravel())
    return tbin / np.maximum(counts, 1)
```

- [ ] **Step 3b: Extract the shared header builder**

In `mffp_sharp/src/mffp_sharp/common/visualize.py`, add this function just above `def one_pager(...)` (line 58). It is the existing header logic (lines 140-159) lifted verbatim into a reusable helper that returns the suptitle lines:

```python
def _header_lines(pde, sample_idx, resolutions, hf_res, aligned, metric_names,
                  condition, condition_names) -> list[str]:
    """Build the suptitle lines shared by the 1D and 2D one-pagers."""
    res_min = min(resolutions)
    lf_res = [r for r in resolutions if r != hf_res]
    pretty = _PDE_NAME.get(pde, pde)
    lines = [f"{pretty}  —  sample {sample_idx}"
             f"    (LF / IF / HF = low / intermediate / high fidelity)"]
    eq = _PDE_EQUATION.get(pde)
    if eq:
        lines.append(f"PDE:  {eq}")
    if condition is not None and condition_names is not None and len(condition_names):
        pairs = [f"{_COND_LABEL.get(n, n)}={float(v):.3g}"
                 for n, v in zip(condition_names, np.ravel(condition))]
        for c in range(0, len(pairs), 4):
            prefix = "condition vector:  " if c == 0 else " " * 19
            lines.append(prefix + "    ".join(pairs[c:c + 4]))
    if lf_res:
        m = _metrics.evaluate(aligned[res_min], aligned[hf_res], metric_names)
        shown = [k for k in _CURATED if k in m]
        errline = "    ".join(f"{_METRIC_LABEL.get(k, k)}={m[k]:.3g}" for k in shown)
        lines.append(f"coarsest LF ({res_min}^2) vs HF ({hf_res}^2) error:")
        lines.append(errline)
        lines.append(f"(full {len(m)}-metric panel in sample_summary.json)")
    return lines
```

- [ ] **Step 3c: Turn `one_pager` into a dispatcher and rename the 2D body**

Rename the existing `def one_pager(...)` (line 58) to `def _one_pager_2d(...)` (keep its full body **unchanged** except delete the header-building tail, lines 137-159, and replace it with a call to the shared helper). Concretely, the tail of `_one_pager_2d` (everything from the `# Header:` comment through the `fig.suptitle(...)` call) becomes:

```python
    # Header: shared suptitle (pretty name + ladder + curated LF-vs-HF panel).
    lines = _header_lines(pde, sample_idx, resolutions, hf_res, aligned,
                          metric_names, condition, condition_names)
    fig.suptitle("\n".join(lines), fontsize=9)

    fig.savefig(out_path, dpi=110)
    plt.close(fig)
```

Then add the new dispatcher and 1D renderer **above** `_one_pager_2d`:

```python
def one_pager(bundle: dict, resolutions: list[int], hf_res: int, metric_names: list[str],
              pde: str, sample_idx: int, out_path: str,
              condition=None, condition_names=None) -> None:
    """Write a one-pager PNG for a single sample bundle.

    Dispatches on field dimensionality: 1D fields get line-plot panels, 2D fields
    get the heatmap layout. Both show the LF/IF/HF fields, the HF-LF residual, the
    radial/1D power spectrum, and a curated LF-vs-HF metric line in the header.
    """
    hf = bundle["aligned"][hf_res]
    if np.asarray(hf).ndim == 1:
        _one_pager_1d(bundle, resolutions, hf_res, metric_names, pde, sample_idx,
                      out_path, condition, condition_names)
    else:
        _one_pager_2d(bundle, resolutions, hf_res, metric_names, pde, sample_idx,
                      out_path, condition, condition_names)


def _one_pager_1d(bundle, resolutions, hf_res, metric_names, pde, sample_idx,
                  out_path, condition, condition_names) -> None:
    """1D one-pager: overlaid fields, residual lines, and the power spectrum."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    aligned = bundle["aligned"]
    raw = bundle["raw"]
    hf = aligned[hf_res]
    res_min = min(resolutions)
    lf_res = [r for r in resolutions if r != hf_res]

    fig, axes = plt.subplots(1, 3, figsize=(16.0, 5.0), constrained_layout=True)

    # Panel 0: native-resolution fields, each on its own cell-center x-axis.
    for res in resolutions:
        xr = (np.arange(res) + 0.5) / res
        tag = "HF" if res == hf_res else "LF" if res == res_min else "IF"
        axes[0].plot(xr, raw[res], marker="o", ms=3, label=f"{tag} ({res})")
    axes[0].set_title("solution field (native resolution)", fontsize=10)
    axes[0].set_xlabel("x (unit domain)")
    axes[0].set_ylabel("u")
    axes[0].legend(fontsize=8)

    # Panel 1: HF - LF residual per LF level, on the shared HF grid.
    xh = (np.arange(hf_res) + 0.5) / hf_res
    for res in lf_res:
        lftag = "LF" if res == res_min else "IF"
        axes[1].plot(xh, hf - aligned[res], label=f"HF - {lftag} ({res})")
    axes[1].axhline(0.0, color="gray", lw=0.8, ls=":")
    axes[1].set_title("error vs HF (on shared grid)", fontsize=10)
    axes[1].set_xlabel("x (unit domain)")
    axes[1].set_ylabel("error")
    axes[1].legend(fontsize=8)

    # Panel 2: power spectrum (log-log); annotate the HF power-law slope on k in [5,40].
    for res in resolutions:
        sp = radial_spectrum(aligned[res])
        kk = np.arange(1, len(sp))
        axes[2].loglog(kk, sp[1:], label=f"{res}")
    axes[2].axvline(res_min // 2, color="gray", ls=":", lw=1)
    hf_sp = radial_spectrum(hf)
    kk2 = np.arange(1, len(hf_sp))
    band = (kk2 >= 5) & (kk2 <= min(40, len(hf_sp) - 1)) & (hf_sp[1:] > 0)
    if band.sum() >= 3:
        slope = float(np.polyfit(np.log(kk2[band]), np.log(hf_sp[1:][band]), 1)[0])
        kref = np.array([5.0, float(min(40, len(hf_sp) - 1))])
        axes[2].loglog(kref, hf_sp[5] * (kref / 5) ** slope, "k--", lw=1.5, alpha=0.85,
                       label=f"HF decay slope ~ {slope:.1f}")
    axes[2].set_title("power spectrum (log-log)", fontsize=10)
    axes[2].set_xlabel("wavenumber (log)  ->  finer scales")
    axes[2].set_ylabel("power (log)")
    axes[2].legend(fontsize=8, title="grid (solid) / HF fit (dashed)")

    lines = _header_lines(pde, sample_idx, resolutions, hf_res, aligned,
                          metric_names, condition, condition_names)
    fig.suptitle("\n".join(lines), fontsize=9)
    fig.savefig(out_path, dpi=110)
    plt.close(fig)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd mffp_sharp && python -m pytest tests/test_visualize.py -q`
Expected: all 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add mffp_sharp/src/mffp_sharp/common/visualize.py mffp_sharp/tests/test_visualize.py
git commit -m "feat(visualize): 1D one-pager (line plots) + shared header; 2D layout preserved

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Task 5: Regression gate — 2D pipeline unchanged (Phase 1b)

**Files:**
- Test: `mffp_sharp/tests/test_regression_2d.py`

**Interfaces:**
- Consumes: `ladder`, `metrics`, `io`, `visualize` (post-refactor).
- Produces: a golden-value test proving the 2D path (ladder → metrics → io → visualize) is behavior-preserving, plus a byte-compile check of the whole package. This is the Phase-1b no-regression gate.

- [ ] **Step 1: Write the regression test**

Create `mffp_sharp/tests/test_regression_2d.py`:

```python
"""Phase-1b no-regression gate: the 2D path must be behavior-preserving."""
import numpy as np

from mffp_sharp.common import ladder, metrics, io, visualize


def _golden_2d_field(res, seed=0):
    rng = np.random.default_rng(seed)
    return rng.standard_normal((res, res))


def test_2d_upsample_is_deterministic_and_shaped():
    f = _golden_2d_field(4)
    out = ladder.upsample_to_hf(f, 8)
    assert out.shape == (8, 8)
    # linear up-interp of a known field reproduces a stored corner exactly enough
    again = ladder.upsample_to_hf(f, 8)
    assert np.allclose(out, again)


def test_2d_metric_panel_values_stable():
    ref = _golden_2d_field(16, seed=1)
    pred = ref + 0.1 * _golden_2d_field(16, seed=2)
    out = metrics.evaluate(pred, ref, ["rel_l2", "linf", "spectral_band",
                                       "interface_position", "conservation", "ssim"])
    # SSIM defined for 2D -> finite, NOT nan (contrast with the 1D skip)
    assert np.isfinite(out["ssim"])
    assert out["rel_l2"] > 0.0 and np.isfinite(out["spectral_band"])


def test_2d_full_pipeline_roundtrip(tmp_path):
    samples, conds = [], []
    for i in range(4):
        raw = {4: _golden_2d_field(4, i), 8: _golden_2d_field(8, 100 + i)}
        samples.append(ladder.assemble_sample(raw, 8))
        conds.append([float(i)])
    p = str(tmp_path / "reg.h5")
    io.write_dataset(p, "cahn_hilliard", samples, np.array(conds), ["eps"],
                     [4, 8], 8, 1.0, seed=0)
    d = io.read_dataset(p)
    assert d["ndim"] == 2 and list(d["spatial_shape"]) == [8, 8]
    out = str(tmp_path / "reg.png")
    visualize.one_pager(d["bundles"][0], [4, 8], 8,
                        ["rel_l2", "linf", "spectral_band", "interface_position"],
                        "cahn_hilliard", 0, out, condition=[0.012],
                        condition_names=["eps"])
    import os
    assert os.path.exists(out) and os.path.getsize(out) > 0
```

- [ ] **Step 2: Run the regression test**

Run: `cd mffp_sharp && python -m pytest tests/test_regression_2d.py -q`
Expected: all 3 tests PASS (the refactor preserved 2D behavior; SSIM is finite for 2D, the 2D one-pager renders).

- [ ] **Step 3: Byte-compile the whole package (no import regressions)**

Run: `cd mffp_sharp && python -m compileall src/mffp_sharp -q && echo OK`
Expected: prints `OK` with no compile errors.

- [ ] **Step 4: Run the full suite**

Run: `cd mffp_sharp && python -m pytest tests/ -q`
Expected: every test from Tasks 0-5 PASSES (1D + 2D).

- [ ] **Step 5: Commit**

```bash
git add mffp_sharp/tests/test_regression_2d.py
git commit -m "test: Phase-1b 2D no-regression gate (ladder/metrics/io/visualize)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
git push
```

---

## Self-Review

**1. Spec coverage** (against the refactor table, spec §"Prerequisite"):
- `ladder.py` "relax assert; 1D → np.interp, 2D → existing" → **Task 1** ✓
- `metrics.py` "branch fft↔fft2; radial |k| in 1D; ssim 1D-or-skip" → **Task 2** ✓
- `io.py` "store ndim/shape attr; write [N,*spatial]; read generic" → **Task 3** ✓ (stacking was already generic; attrs added)
- `visualize.py` "1D one-pager line plots; shared spectrum code" → **Task 4** ✓
- `generate.py`/`sampling.py` "thread ndim" → **deferred to the solver-modules plan**, because nothing in `generate.py` is dimension-specific today (the solver returns the field shape; `io` infers `ndim` from it). The Phase-1b regression (Task 5) confirms `generate.py`'s dependencies are unbroken. *No 1D PDE is registered until the solver plan, so there is nothing for `generate.py` to thread yet — folding it there avoids a dead-code change here.*
- Phase-1b no-regression (spec workflow table) → **Task 5** ✓

**2. Placeholder scan:** No "TBD"/"add error handling"/"write tests for the above" — every code step shows complete code; every run step shows the command and expected result. ✓

**3. Type consistency:** `upsample_to_hf(field, hf_res, order)` signature unchanged across tasks; `_boundary_count`/`spectral_band`/`ssim`/`radial_spectrum` keep their names and arities; `one_pager` keeps its exact public signature (dispatcher), with `_one_pager_1d`/`_one_pager_2d`/`_header_lines` as new internals; `read_dataset` adds keys without removing any. ✓

**Scope note:** This is plan 1 of 3. **Plan 2** (solver modules — the ~16 build-set PDEs, fanned out by template; includes the `generate.py`/`sampling.py`/`configs` threading of `ndim` and new-PDE registration) depends on the finalized API from this plan. **Plan 3** (box sample generation + auto-screen + survivor menu) depends on Plan 2. Authoring 2 and 3 in full detail is deferred until this lands so they target the real, tested interfaces rather than a predicted one.
