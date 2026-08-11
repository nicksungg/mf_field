# == RE-VENDORED (round-3 card r3s2_field_reach-B2) ==========================
# SOURCE : round3/worktrees/r3s2_field_reach/B1/models_r3/r3s2_stack_ic/upsample.py
# COMMIT : d5069a74bb63da837b89b16508ae25a2164780cc  (tip of branch
#          round3/exp-r3s2_field_reach-B1; recipe.env._vendor_source. The
#          recipe's `base_commit` 76d15c2d is a TRUNK commit that carries NO
#          models_r3/ tree at all -- see notes/handoff_experiment_builder.md.)
# SHA256 : 57d3b822473d8f781687842168ea38f46e87e0a0949068a61d2da3a162de6f4c
# STATUS : byte-identical below this header.
#          Copied, never imported: score_panel.py::code_hash hashes only
#          family_dir/**/*.py, so logic outside the family dir is invisible to
#          the eval cache key.
# ROLE   : declared reuse role (a), round-2 program 5.10a -- the DC-lineage
#          corrector stays a FROZEN test-time sub-component behind a
#          condition->pseudo-LF front end. The B2 contribution is the ROUTE
#          SWITCH + budget accountant, not this code.
# ============================================================================
# == RE-VENDORED (round-3 card r3s2_field_reach-B1) ============================
# SOURCE : round2/worktrees/r2s2_stacked/B1/models_r2/r2s2_stack/upsample.py
# COMMIT : 6b4e1d4825666e037a43675c83d9bda6289ec9d0  (recipe.env._vendor_source)
# SHA256 : 233caa28be6a9c164355b80dda09893dd66bab4b5d92bf01daff3636da02059a
# STATUS : byte-identical below this header (the round-2 header block and the
#          body are unchanged). Copied, never imported: score_panel.py::code_hash
#          hashes only family_dir/**/*.py.
# ROLE   : declared reuse role (a), round-2 program 5.10a -- the DC-lineage
#          corrector is a frozen test-time sub-component behind a NEW
#          condition->pseudo-LF front end. The reuse IS the experiment.
# ==============================================================================
# ══ VENDORED (round-2 card r2s2_stacked-B1) ═════════════════════════════
# SOURCE : mffp_autoresearch/round2/eval/panel_data.py @ substrate 9e10d414
#          (`_legacy_cell_centred_up`, `_node_aligned_periodic_up`,
#           `_dirichlet_node_up`, PERIODIC_NODE_DATASETS / DIRICHLET_NODE_DATASETS
#           / LEGACY_CELL_DATASETS, and the `copylf_prediction` keying logic)
# STATUS : the three interpolators below are byte-identical to the eval layer's;
#          only the module scaffolding around them is new.
# WHY VENDORED, NOT IMPORTED : `score_panel.py::code_hash` hashes
#          `family_dir/**/*.py` plus the three eval files; logic reached by an
#          import from anywhere else would be invisible to the cache key and
#          could silently poison a cached score (the reason recorded verbatim in
#          `s4_router/lsi_filter.py`'s docstring). The eval layer stays byte-
#          untouched (program.md §5.3) — this file never writes to it.
# ══════════════════════════════════════════════════════════════════════════
"""The CORRECTED (ADR r2-0001) LF -> HF-grid upsampler, keyed per dataset.

Card `r2s2_stacked-B1` Decision B: the emulator predicts the LF field on the LF
rung's NATIVE grid; this module lifts it to the HF working grid under EXACTLY
the convention `round2/eval/panel_data.py` uses to build the scored copy-LF
denominator. That is round 1's never-applied "corrector-input wrap-seam fix":
round-1 correctors saw a base field upsampled by
`zoom(..., grid_mode=True, mode="nearest")`, which carries both a (r-1)/2
half-cell registration defect and a clamp-extended wrap seam.

Conventions (ADR r2-0001, unchanged here):
  * nested periodic pseudo-spectral datasets -> variant C, node-aligned bilinear
    with periodic wrap (HF pixel k samples LF index k/r exactly);
  * `ext__helmholtz_2d` -> variant E, Dirichlet interior-node map;
  * everything else (non-nested guards, 1-D signals) -> the round-1 legacy
    cell-centred path, certified consistent for those datasets by the audit.

An unclassified named 2-D dataset RAISES: convention assignment is an ADR
decision, never a default (spec §5.3 assert-don't-default).
"""
from __future__ import annotations

import numpy as np
from scipy.ndimage import map_coordinates, zoom

# ── begin verbatim block from round2/eval/panel_data.py ──────────────────
PERIODIC_NODE_DATASETS = {
    "sharp__phase_field_crystal_2d",
    "sharp__allen_cahn_2d",
    "sharp__fisher_kpp_2d",
    "sharp__cahn_hilliard",
}
DIRICHLET_NODE_DATASETS = {"ext__helmholtz_2d"}
LEGACY_CELL_DATASETS = {"heat_local", "fluid", "sharp__sod_1d", "ifc_poisson", "ifc_heat"}


def _legacy_cell_centred_up(lf2d: np.ndarray, hf_grid: tuple) -> np.ndarray:
    """Round-1 convention: cell-centred bilinear zoom, clamp-extended edges."""
    factors = (hf_grid[0] / lf2d.shape[0], hf_grid[1] / lf2d.shape[1])
    return zoom(lf2d, factors, order=1, grid_mode=True, mode="nearest")


def _node_aligned_periodic_up(lf2d: np.ndarray, hf_grid: tuple) -> np.ndarray:
    """Variant C: HF pixel (k,l) samples LF index (k/r0, l/r1), periodic wrap.

    Exact at shared nodes: up[::r0, ::r1] == lf bit-for-bit when nested.
    """
    h, w = lf2d.shape
    H, W = hf_grid
    if H % h or W % w:
        raise ValueError(f"variant C requires a nested grid, got {h,w} -> {H,W}")
    coords = np.meshgrid(
        np.arange(H, dtype=np.float64) * (h / H),
        np.arange(W, dtype=np.float64) * (w / W),
        indexing="ij",
    )
    return map_coordinates(lf2d, coords, order=1, mode="grid-wrap")


def _dirichlet_node_up(lf2d: np.ndarray, hf_grid: tuple) -> np.ndarray:
    """Variant E: interior-node Dirichlet grids x_j=(j+1)/(n+1) (helmholtz)."""
    h, w = lf2d.shape
    H, W = hf_grid
    jj = (np.arange(H, dtype=np.float64) + 1.0) * (h + 1) / (H + 1) - 1.0
    ll = (np.arange(W, dtype=np.float64) + 1.0) * (w + 1) / (W + 1) - 1.0
    coords = np.meshgrid(jj, ll, indexing="ij")
    return map_coordinates(lf2d, coords, order=1, mode="nearest")
# ── end verbatim block ───────────────────────────────────────────────────


CONVENTION_BY_FN = {
    _node_aligned_periodic_up: "node_aligned_periodic",
    _dirichlet_node_up: "dirichlet_node",
    _legacy_cell_centred_up: "legacy_cell_centred",
}


def resolve_convention(dataset_name: str):
    """Return (upsample_fn, convention_name) for `dataset_name`. Raises if unknown."""
    if dataset_name in PERIODIC_NODE_DATASETS:
        fn = _node_aligned_periodic_up
    elif dataset_name in DIRICHLET_NODE_DATASETS:
        fn = _dirichlet_node_up
    elif dataset_name in LEGACY_CELL_DATASETS:
        fn = _legacy_cell_centred_up
    else:
        raise ValueError(
            f"dataset {dataset_name!r} has no reference convention assigned "
            "(ADR r2-0001): classify it in round2/eval/panel_data.py before using it")
    return fn, CONVENTION_BY_FN[fn]


def upsample_fields(lf_flat: np.ndarray, lf_grid, hf_grid, dataset_name: str) -> np.ndarray:
    """(N, prod(lf_grid)) -> (N, prod(hf_grid)) under the dataset's convention.

    1-D fields (H == 1 on both grids) take the legacy 1-D `zoom` path, which is
    exactly what `panel_data.copylf_prediction` does for `sharp__sod_1d`.
    """
    lf = np.asarray(lf_flat, dtype=np.float64)
    lg = (int(lf_grid[0]), int(lf_grid[1]))
    hg = (int(hf_grid[0]), int(hf_grid[1]))
    n = lf.shape[0]
    if lg == hg:
        return lf.reshape(n, -1).copy()

    if lg[0] == 1 and hg[0] == 1:                       # 1-D signal: legacy path
        out = np.empty((n, hg[1]), dtype=np.float64)
        factor = hg[1] / lg[1]
        for i in range(n):
            up = zoom(lf[i].reshape(lg[1]), factor, order=1, grid_mode=True, mode="nearest")
            if up.shape != (hg[1],):
                raise ValueError(f"1-D interpolation produced {up.shape}, expected {(hg[1],)}")
            out[i] = up
        return out

    up_fn, _ = resolve_convention(dataset_name)
    out = np.empty((n, hg[0] * hg[1]), dtype=np.float64)
    for i in range(n):
        u = up_fn(lf[i].reshape(lg), hg)
        if u.shape != hg:
            raise ValueError(f"interpolation produced {u.shape}, expected {hg}")
        out[i] = u.ravel()
    return out


# ══ APPEND-ONLY BLOCK (round-3 card r3s2_field_reach-B3) ═════════════════
# NOTHING ABOVE THIS LINE IS EDITED. The block below adds the ADR r3-0005
# spectral (FFT zero-pad) lift and re-keys `sharp__phase_field_crystal_2d` to
# it, so this family's base field is built by the SAME operator that builds the
# scored copy-LF denominator.
#
# SOURCE : mffp_autoresearch/round2/eval/panel_data.py::_spectral_zeropad_up and
#          ::SPECTRAL_RUNG_DATASETS, VERBATIM (that function is itself vendored
#          in the eval layer from mffp_sharp.common.spectral.spectral_interp,
#          the function the ADR's acceptance measurements used).
# WHY     : ADR r3-0005 (ratified 2026-08-10) re-pointed pfc's scored cell to
#          rung 1 with an exact spectral reference (0.012358); the rung override
#          and the lift are INSEPARABLE per the ADR. The B2 body above still
#          keys pfc to the node-aligned bilinear lift, which was the pre-ADR
#          scored cell -- a DIFFERENT cell. `rung_lift.tripwire` asserts the
#          agreement with panel_data.py bit-for-bit at runtime, on real rows.
# WHY NOT EDITED IN PLACE : the verbatim block's provenance header must stay
#          true; an append + rebind keeps the vendored bytes auditable.
# ══════════════════════════════════════════════════════════════════════════

# panel_data.py, verbatim
SPECTRAL_RUNG_DATASETS = {"sharp__phase_field_crystal_2d": 1}


def _spectral_zeropad_up(lf2d: np.ndarray, hf_grid: tuple) -> np.ndarray:
    """ADR r3-0005: exact band-limited (FFT zero-pad) lift for node-periodic
    band-limited fields. Vendored verbatim (2-D branch) from
    `mffp_sharp.common.spectral.spectral_interp` -- the function the ADR's
    acceptance measurements used -- so reference and measurement share bytes.
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


CONVENTION_BY_FN[_spectral_zeropad_up] = "spectral_zeropad"
_resolve_convention_pre_adr_r3_0005 = resolve_convention


def resolve_convention(dataset_name: str):                       # noqa: F811
    """`panel_data.copylf_prediction`'s keying order, post-ADR r3-0005:
    SPECTRAL_RUNG first, then the pre-ADR chain unchanged."""
    if dataset_name in SPECTRAL_RUNG_DATASETS:
        return _spectral_zeropad_up, CONVENTION_BY_FN[_spectral_zeropad_up]
    return _resolve_convention_pre_adr_r3_0005(dataset_name)
