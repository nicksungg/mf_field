# == RE-VENDORED (round-3 card r3s2_field_reach-B2) ==========================
# SOURCE : round3/worktrees/r3s2_field_reach/B1/models_r3/r3s2_stack_ic/bands.py
# COMMIT : d5069a74bb63da837b89b16508ae25a2164780cc  (tip of branch
#          round3/exp-r3s2_field_reach-B1; recipe.env._vendor_source. The
#          recipe's `base_commit` 76d15c2d is a TRUNK commit that carries NO
#          models_r3/ tree at all -- see notes/handoff_experiment_builder.md.)
# SHA256 : 18527d523dec8683740d9decda88f92e9511fc49d33445027725fadc173d2ada
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
# SOURCE : round2/worktrees/r2s2_stacked/B1/models_r2/r2s2_stack/bands.py
# COMMIT : 6b4e1d4825666e037a43675c83d9bda6289ec9d0  (recipe.env._vendor_source)
# SHA256 : 76ad053d336aa513c716dd91488eb7daf753d0bb529d67377a7e64d9d5dbe67c
# STATUS : byte-identical below this header (the round-2 header block and the
#          body are unchanged). Copied, never imported: score_panel.py::code_hash
#          hashes only family_dir/**/*.py.
# ROLE   : declared reuse role (a), round-2 program 5.10a -- the DC-lineage
#          corrector is a frozen test-time sub-component behind a NEW
#          condition->pseudo-LF front end. The reuse IS the experiment.
# ==============================================================================
# ══ VENDORED (round-2 card r2s2_stacked-B1) ═════════════════════════════
# SOURCE : round1/worktrees/s4_hybrid_routing/B3/models_r1/s4_router/bands.py
# COMMIT : b90d4662cd12820b6926730d39bdb5af70bba276  (recipe.base_commit)
# SHA256 : 42b869598fcc864e50d82b14b8c184d6f56aad45e1d78c963f5ddae1c070dd73
# STATUS : byte-identical below this header. Round-1 branches are immutable
#          (program.md §5.13); the file is COPIED, never imported, because
#          `score_panel.py::code_hash` hashes only `family_dir/**/*.py` and
#          logic living outside the family dir is invisible to the cache key.
# ROLE   : declared frozen test-time sub-component (program.md §5.10a) behind a
#          new condition->pseudo-LF front end. The reuse IS the experiment.
# ══════════════════════════════════════════════════════════════════════════
"""Dyadic radial wavenumber bands — REUSED BYTE-FOR-BYTE from s2_beyond_copy-B1.

`band_masks` below is copied verbatim (docstring included) from
`mffp_autoresearch/round1/worktrees/s2_beyond_copy/B1/models_r1/
s2_copylf_forensics/forensics.py`, so that this card's per-band contribution
profile and variant-4 per-band gate sit on EXACTLY the s2-B1 band grid
(card part 3, variant 4: "edges `k_nyq * [0, 1/8, 1/4, 1/2, 1]` (s2-B1
convention)"). Do not "improve" it: cross-card comparability is the point.

`S6_BAND_EDGES_FRAC = "0,0.125,0.25,0.5,1.0"` (card recipe) is asserted against
the dyadic edges this function produces for n_bands=4 — a mismatch raises
instead of silently using a different grid.
"""
from __future__ import annotations

import numpy as np

N_BANDS = 4  # card recipe: 5 edges => 4 bands


# ── begin verbatim block from s2_copylf_forensics/forensics.py ──────────
def band_masks(grid, n_bands: int):
    """Dyadic radial wavenumber bands on the rFFT half-plane.

    Band edges are k_nyq / 2^(n_bands-1-b): for n_bands=4 the bands are
    [0, k/8), [k/8, k/4), [k/4, k/2), [k/2, inf) with k = min(H, W)/2. The
    outermost band is open-ended so the bands partition the whole half-plane
    (corner wavenumbers beyond k_nyq included) and energy shares sum to 1.
    `w` is the Parseval weight of the rFFT half-plane (1 on the DC and Nyquist
    columns, 2 elsewhere).
    """
    h, w_ = int(grid[0]), int(grid[1])
    kx = np.fft.fftfreq(h) * h
    ky = np.arange(w_ // 2 + 1, dtype=np.float64)
    kr = np.sqrt(kx[:, None] ** 2 + ky[None, :] ** 2)
    weight = np.full((h, w_ // 2 + 1), 2.0)
    weight[:, 0] = 1.0
    if w_ % 2 == 0:
        weight[:, -1] = 1.0
    k_ny = min(h, w_) / 2.0
    edges = [0.0] + [k_ny / 2.0 ** (n_bands - 1 - b) for b in range(n_bands)]
    masks = []
    for b in range(n_bands):
        if b == n_bands - 1:
            masks.append(kr >= edges[b])
        else:
            masks.append((kr >= edges[b]) & (kr < edges[b + 1]))
    return masks, weight, edges
# ── end verbatim block ──────────────────────────────────────────────────


def check_edges_env(grid, edges_frac_env: str, n_bands: int = N_BANDS) -> list:
    """Assert the recipe's `S6_BAND_EDGES_FRAC` == the s2-B1 dyadic grid.

    Returns the absolute wavenumber edges. Raises ValueError on mismatch
    (seam assertion: never silently band on a different grid).
    """
    _, _, edges = band_masks(grid, n_bands)
    k_ny = min(int(grid[0]), int(grid[1])) / 2.0
    want = [float(x) for x in edges_frac_env.split(",") if x.strip() != ""]
    got = [e / k_ny for e in edges]
    if len(want) != len(got) or any(abs(a - b) > 1e-12 for a, b in zip(want, got)):
        raise ValueError(
            f"S6_BAND_EDGES_FRAC={edges_frac_env!r} -> {want} does not match the "
            f"s2-B1 dyadic band grid {got} for grid {tuple(grid)}"
        )
    return edges


def band_error_energy(err, grid, n_bands: int = N_BANDS):
    """Per-band error energy of `err` (N, n_cells) on `grid`, Parseval-weighted.

    Same rFFT + weight convention as s2-B1's `spectral_bands`.
    """
    masks, weight, _ = band_masks(grid, n_bands)
    f = np.fft.rfft2(np.asarray(err, dtype=np.float64).reshape(-1, int(grid[0]), int(grid[1])))
    acc = (np.abs(f) ** 2 * weight).sum(axis=0)
    return [float(np.real(acc[m]).sum()) for m in masks]
