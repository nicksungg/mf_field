"""TRAIN-side LF rungs lifted to the HF grid under the ADR r2-0001 conventions.

Card `r2s3_lf_train_signal-B3` `recipe.env._seam_asserts` item (3), verbatim:

    the LF lift used by `ref_linear_mf` is verified against the eval-layer
    copy-LF convention per dataset (max_abs_diff 0.0 expected, RAISE on
    mismatch).

WHAT B3 CHANGED: nothing in this file. B2 used `lift_rung_to_hf_grid` for TWO
consumers — the deleted null-penalty target `Theta_LF` and the `ref_linear_mf`
reference arm. Only the first consumer is gone; the lift itself, the
conventions and the 1e-9 assert are vendored byte-for-byte (modulo the
`R2S3B2_` -> `R2S3B3_` docstring prefix) from
`worktrees/r2s3_lf_train_signal/B2/models_r2/r2s3_null_supply/lf_reference.py`
(commit 945ee65a1f47460db2cf892e0e8ead1248b58aeb).

PROVENANCE. `_legacy_cell_centred_up`, `_node_aligned_periodic_up`,
`_dirichlet_node_up`, the three dataset-classification sets and
`copylf_prediction_vendored` are a byte-faithful transcription of
`mffp_autoresearch/round2/eval/panel_data.py` at the round-2 substrate commit
9e10d414e35a96398f7b091bc84ddf936d88acc7 (the card's `recipe.base_commit`).
They are VENDORED rather than only imported because the card asks for an
agreement ASSERT rather than an assumption; `verify_against_eval` performs it
by importing the eval module read-only and comparing on the TRAIN split.
The eval layer is never written to (program.md §5 immutable 3). The same
vendoring pattern (and the same verification call) is the precedent set by
`r2s4_diag-B2`'s `lf_reference.py`.

`lift_rung_to_hf_grid` is the ONE addition on top of the transcription: the
eval-layer function only ever lifts `max(lf_fids)` truncated to the HF row
count, while this card fits an affine law on a rung's FULL row set (400 LF
conditions where only 5 HF rows exist — the card's coverage regime). It uses
the identical per-dataset `up_fn`, so the two agree by construction on the
rows they share; the 1e-9 assert covers exactly that.

WHY THIS IS NOT AN LF LEAK. Everything here is applied to the **train** split
of the stripped view, where LF rungs are present by design (round 2's question
is "how much does LF help when it is available only at training time"). The
**test** split of the stripped view physically contains no LF file, and no
caller in this family passes a test-split dict.
"""
from __future__ import annotations

import numpy as np
from scipy.ndimage import map_coordinates, zoom

# ADR r2-0001 classification — copied verbatim from eval/panel_data.py.
#
# CARD `r3s3_lf_value-B3` DELTA vs the base family's copy (the ONE functional
# change in this file, and it is forced): ADR r3-0005 (ratified 2026-08-10)
# amended `eval/panel_data.py` with `SPECTRAL_RUNG_DATASETS` — pfc's scored cell
# is L1(32^2) -> L3(128^2) under an EXACT band-limited (FFT zero-pad) lift,
# because the crystalline fields are band-limited below L2's Nyquist and a
# linear lift's own error (~0.07) would dominate the true gap (~0.012). B2's
# vendored copy predates that amendment and still classified pfc as
# `node_aligned_periodic`; this card RUNS pfc, and the seam assert
# (`verify_against_eval`, tol 1e-9) caught it on the first pfc smoke of this
# build with `max abs diff 1.400141e-01`. Registration-of-lifts (round-2 §12 /
# ADR r2-0004) requires the model-side lift to BE the eval layer's, so
# `_spectral_zeropad_up` below is vendored verbatim from
# `eval/panel_data.py::_spectral_zeropad_up` and pfc is reclassified. The seam
# assert is what adjudicates the transcription, per leg, at 1e-9.
SPECTRAL_RUNG_DATASETS = {"sharp__phase_field_crystal_2d": 1}
PERIODIC_NODE_DATASETS = {
    "sharp__allen_cahn_2d",
    "sharp__fisher_kpp_2d",
    "sharp__cahn_hilliard",
}
DIRICHLET_NODE_DATASETS = {"ext__helmholtz_2d"}
LEGACY_CELL_DATASETS = {"heat_local", "fluid", "sharp__sod_1d", "ifc_poisson", "ifc_heat"}


def convention_for(dataset_name: str) -> str:
    if dataset_name in SPECTRAL_RUNG_DATASETS:
        return "spectral_zeropad_rung1"
    if dataset_name in PERIODIC_NODE_DATASETS:
        return "node_aligned_periodic"
    if dataset_name in DIRICHLET_NODE_DATASETS:
        return "dirichlet_node"
    if dataset_name in LEGACY_CELL_DATASETS:
        return "legacy_cell_centred"
    raise SystemExit(
        f"dataset {dataset_name!r} has no ADR r2-0001 reference convention assigned; "
        "classify it in eval/panel_data.py first (an ADR decision, not a default)")


def _legacy_cell_centred_up(lf2d: np.ndarray, hf_grid: tuple) -> np.ndarray:
    """Round-1 convention: cell-centred bilinear zoom, clamp-extended edges."""
    factors = (hf_grid[0] / lf2d.shape[0], hf_grid[1] / lf2d.shape[1])
    return zoom(lf2d, factors, order=1, grid_mode=True, mode="nearest")


def _node_aligned_periodic_up(lf2d: np.ndarray, hf_grid: tuple) -> np.ndarray:
    """Variant C: HF pixel (k,l) samples LF index (k/r0, l/r1), periodic wrap."""
    h, w = lf2d.shape
    H, W = hf_grid
    if H % h or W % w:
        raise ValueError(f"variant C requires a nested grid, got {h, w} -> {H, W}")
    coords = np.meshgrid(
        np.arange(H, dtype=np.float64) * (h / H),
        np.arange(W, dtype=np.float64) * (w / W),
        indexing="ij",
    )
    return map_coordinates(lf2d, coords, order=1, mode="grid-wrap")


def _spectral_zeropad_up(lf2d: np.ndarray, hf_grid: tuple) -> np.ndarray:
    """ADR r3-0005: exact band-limited (FFT zero-pad) lift for node-periodic
    band-limited fields. Vendored verbatim (2-D branch) from
    `mffp_sharp.common.spectral.spectral_interp` — the function the ADR's
    acceptance measurements used — so reference and measurement share bytes.
    """
    n_c = lf2d.shape[0]
    H, W = hf_grid
    if H != W or lf2d.shape[0] != lf2d.shape[1]:
        raise ValueError(f"spectral lift requires square grids, got {lf2d.shape} -> {hf_grid}")
    if (H - n_c) % 2:
        raise ValueError(f"spectral lift requires even padding, got {n_c} -> {H}")
    if H == n_c:
        return lf2d.astype(np.float64).copy()
    F = np.fft.fftshift(np.fft.fft2(lf2d))
    pad = (H - n_c) // 2
    Fp = np.zeros((H, W), dtype=complex)
    Fp[pad:pad + n_c, pad:pad + n_c] = F
    out = np.fft.ifft2(np.fft.ifftshift(Fp)) * (H / n_c) ** 2
    return np.real(out)


def _dirichlet_node_up(lf2d: np.ndarray, hf_grid: tuple) -> np.ndarray:
    """Variant E: interior-node Dirichlet grids x_j=(j+1)/(n+1) (helmholtz)."""
    h, w = lf2d.shape
    H, W = hf_grid
    jj = (np.arange(H, dtype=np.float64) + 1.0) * (h + 1) / (H + 1) - 1.0
    ll = (np.arange(W, dtype=np.float64) + 1.0) * (w + 1) / (W + 1) - 1.0
    coords = np.meshgrid(jj, ll, indexing="ij")
    return map_coordinates(lf2d, coords, order=1, mode="nearest")


def _up_fn(dataset_name: str):
    return {
        "spectral_zeropad_rung1": _spectral_zeropad_up,
        "node_aligned_periodic": _node_aligned_periodic_up,
        "dirichlet_node": _dirichlet_node_up,
        "legacy_cell_centred": _legacy_cell_centred_up,
    }[convention_for(dataset_name)]


def lift_rung_to_hf_grid(field_flat: np.ndarray, lf_grid, hf_grid,
                         dataset_name: str) -> np.ndarray:
    """(N, prod(lf_grid)) -> (N, prod(hf_grid)) under the dataset's convention.

    Grid-free (1-D / unknown-shape) inputs take the legacy 1-D path, exactly as
    `eval/panel_data.py::copylf_prediction` does.
    """
    lf = np.asarray(field_flat, dtype=np.float64)
    n = lf.shape[0]
    if lf_grid is None or hf_grid is None:
        n_hf_cells = int(np.prod(hf_grid)) if hf_grid is not None else lf.shape[1]
        if lf.shape[1] == n_hf_cells:
            return lf
        factor = n_hf_cells / lf.shape[1]
        out = np.empty((n, n_hf_cells), dtype=np.float64)
        for i in range(n):
            up = zoom(lf[i], factor, order=1, grid_mode=True, mode="nearest")
            if up.shape != (n_hf_cells,):
                raise ValueError(
                    f"1-D interpolation produced {up.shape}, expected {(n_hf_cells,)}")
            out[i] = up
        return out
    lf_grid = (int(lf_grid[0]), int(lf_grid[1]))
    hf_grid = (int(hf_grid[0]), int(hf_grid[1]))
    if lf_grid == hf_grid:
        return lf
    up_fn = _up_fn(dataset_name)
    out = np.empty((n, hf_grid[0] * hf_grid[1]), dtype=np.float64)
    for i in range(n):
        up = up_fn(lf[i].reshape(lf_grid), hf_grid)
        if up.shape != hf_grid:
            raise ValueError(f"interpolation produced {up.shape}, expected {hf_grid}")
        out[i] = up.ravel()
    return out


def copylf_prediction_vendored(data: dict, dataset_name: str) -> np.ndarray:
    """Byte-faithful transcription of `eval/panel_data.py::copylf_prediction`.

    Used ONLY by `verify_against_eval` (the 1e-9 seam assert the card asks for);
    the training path calls `lift_rung_to_hf_grid` per rung instead.
    """
    hf_fid = data["hf_fid"]
    if not data["lf_fids"]:
        raise ValueError("no LF fidelities present")
    lf_fid = max(data["lf_fids"])

    lf = np.asarray(data["field_by_fid"][lf_fid], dtype=np.float64)
    hf = np.asarray(data["field_by_fid"][hf_fid], dtype=np.float64)
    lf_grid = data["grid_shape_by_fid"].get(lf_fid)
    hf_grid = data["grid_shape_by_fid"].get(hf_fid)
    n_hf = hf.shape[0]
    if lf.shape[0] < n_hf:
        raise ValueError(
            f"LF has fewer samples than HF ({lf.shape[0]} < {n_hf}); "
            "index alignment violated")
    lf = lf[:n_hf]  # index-aligned truncation (repo convention: aligned/nested)

    if lf_grid is None or hf_grid is None:
        if lf.shape[1] == hf.shape[1]:
            return lf
        factor = hf.shape[1] / lf.shape[1]
        out = np.empty((n_hf, hf.shape[1]), dtype=np.float64)
        for i in range(n_hf):
            up = zoom(lf[i], factor, order=1, grid_mode=True, mode="nearest")
            if up.shape != (hf.shape[1],):
                raise ValueError(
                    f"1-D interpolation produced {up.shape}, expected {(hf.shape[1],)}")
            out[i] = up
        return out

    if tuple(lf_grid) == tuple(hf_grid):
        return lf

    up_fn = _up_fn(dataset_name)
    out = np.empty((n_hf, hf_grid[0] * hf_grid[1]), dtype=np.float64)
    for i in range(n_hf):
        up = up_fn(lf[i].reshape(lf_grid), tuple(hf_grid))
        if up.shape != tuple(hf_grid):
            raise ValueError(f"interpolation produced {up.shape}, expected {tuple(hf_grid)}")
        out[i] = up.ravel()
    return out


def verify_against_eval(train_data: dict, dataset_name: str, eval_dir,
                        tol: float = 1e-9) -> dict:
    """Assert the vendored lift == `eval/panel_data.copylf_prediction` (TRAIN split).

    READ-ONLY import of the round eval layer; nothing is written there. Raises
    on disagreement (card: "vendored with a 1e-9 train-split agreement assert").
    """
    import sys
    from pathlib import Path

    eval_dir = str(Path(eval_dir))
    if eval_dir not in sys.path:
        sys.path.insert(0, eval_dir)
    import panel_data  # noqa: E402  (read-only)

    vendored = copylf_prediction_vendored(train_data, dataset_name)
    ref = np.asarray(panel_data.copylf_prediction(train_data, dataset_name),
                     dtype=np.float64)
    if ref.shape != vendored.shape:
        raise SystemExit(
            f"vendored lift shape {vendored.shape} != eval {ref.shape} on {dataset_name}")
    max_abs = float(np.abs(ref - vendored).max()) if vendored.size else 0.0
    if not (max_abs <= tol):
        raise SystemExit(
            f"vendored lift disagrees with eval/panel_data.py on {dataset_name} "
            f"(max abs diff {max_abs:.6e} > tol {tol:g})")
    return {
        "verified_against": "eval/panel_data.py::copylf_prediction (TRAIN split, read-only)",
        "max_abs_diff": max_abs,
        "tol": float(tol),
        "convention": convention_for(dataset_name),
        "copylf_def_hash": panel_data.COPYLF_DEF_HASH,
        "eval_dir": eval_dir,
    }
