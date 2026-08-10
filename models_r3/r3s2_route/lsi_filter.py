# == RE-VENDORED (round-3 card r3s2_field_reach-B2) ==========================
# SOURCE : round3/worktrees/r3s2_field_reach/B1/models_r3/r3s2_stack_ic/lsi_filter.py
# COMMIT : d5069a74bb63da837b89b16508ae25a2164780cc  (tip of branch
#          round3/exp-r3s2_field_reach-B1; recipe.env._vendor_source. The
#          recipe's `base_commit` 76d15c2d is a TRUNK commit that carries NO
#          models_r3/ tree at all -- see notes/handoff_experiment_builder.md.)
# SHA256 : d7079fef496a8e07657cb5a36eceabfcd28ab97f5cd38bccd06f23182d71bf49
# STATUS : byte-identical below this header EXCEPT a clearly marked APPEND-ONLY block at the end of the file (the LOOCV-ridge + LF-Nyquist band-limit estimator, card part 3 instrument repair).
#          Copied, never imported: score_panel.py::code_hash hashes only
#          family_dir/**/*.py, so logic outside the family dir is invisible to
#          the eval cache key.
# ROLE   : declared reuse role (a), round-2 program 5.10a -- the DC-lineage
#          corrector stays a FROZEN test-time sub-component behind a
#          condition->pseudo-LF front end. The B2 contribution is the ROUTE
#          SWITCH + budget accountant, not this code.
# ============================================================================
# == RE-VENDORED (round-3 card r3s2_field_reach-B1) ============================
# SOURCE : round2/worktrees/r2s2_stacked/B1/models_r2/r2s2_stack/lsi_filter.py
# COMMIT : 6b4e1d4825666e037a43675c83d9bda6289ec9d0  (recipe.env._vendor_source)
# SHA256 : 5d5b676f3985161ebb691e9fe6321fa3411562581bc1bdfe491aa6bc9a6e72c3
# STATUS : byte-identical below this header (the round-2 header block and the
#          body are unchanged). Copied, never imported: score_panel.py::code_hash
#          hashes only family_dir/**/*.py.
# ROLE   : declared reuse role (a), round-2 program 5.10a -- the DC-lineage
#          corrector is a frozen test-time sub-component behind a NEW
#          condition->pseudo-LF front end. The reuse IS the experiment.
# ==============================================================================
# ══ VENDORED (round-2 card r2s2_stacked-B1) ═════════════════════════════
# SOURCE : round1/worktrees/s4_hybrid_routing/B3/models_r1/s4_router/lsi_filter.py
# COMMIT : b90d4662cd12820b6926730d39bdb5af70bba276  (recipe.base_commit)
# SHA256 : eb62cd3365df9288a1093a61c80baa3d0379e9547d5cf86d8b95e74fd115b02e
# STATUS : byte-identical below this header. Round-1 branches are immutable
#          (program.md §5.13); the file is COPIED, never imported, because
#          `score_panel.py::code_hash` hashes only `family_dir/**/*.py` and
#          logic living outside the family dir is invisible to the cache key.
# ROLE   : declared frozen test-time sub-component (program.md §5.10a) behind a
#          new condition->pseudo-LF front end. The reuse IS the experiment.
# ══════════════════════════════════════════════════════════════════════════
"""The closed-form LSI defect filter `T(k)` -- card `s6_local-B2` arm `lsi_ctrl`.

**ZERO METHOD NOVELTY IS CLAIMED.** The websearcher's verdict row (i) is explicit:
"preempted as a *method*, open as a *reported baseline* ... Claim **zero method
novelty**; the contribution is the *measured floor* ... A card that says 'we
introduce an LSI defect filter' dies on sight." Local Fourier analysis of
coarse-grid defect operators is classical multigrid; the only open thing is that
no fetched source **scores** such a filter beside trained neural operators on an
MF field benchmark. This arm exists to be that scored floor and nothing else.

Construction, ADAPTED WITH CITATION from
`worktrees/s6_local/B1/scratchpad/reanalysis_turn_2.py::fit_transfer/apply_transfer`
(B1 mechanism turn 2, promoted as `tools/defect_correction_learnability.py`):

    T(k) = sum_n Rhat_n(k) conj(LFhat_n(k)) / sum_n |LFhat_n(k)|^2       (one Wiener
                                                                          transfer fn)
    C(x) = irfft2( rfft2(LF)(k) * T(k) )
    pred = LF + alpha * C,     alpha selected by the family's own `fit_alpha` on
                               `val_idx` with 0 in the candidate set

It is VENDORED into the family rather than imported from `round1/tools/`
on purpose: `score_panel.py::code_hash` hashes `family_dir/**/*.py`, so logic
living outside the family dir would be invisible to the eval cache key and could
silently poison a cached score. `tools/defect_correction_learnability.py` is
therefore cited, never imported. Note that the promoted tool defaults to
`ridge=1e-6` and a different permutation, which is why its numbers differ from
turn 2's by 1-9%; this arm runs `S6_LSI_RIDGE=0` to reproduce turn 2 exactly
(validity gate V2, `S6_LSI_F6_TOL=0.02`).

Zero trained parameters: no gradient step, no optimizer, no epoch loop. `T` is a
solved least-squares object on the SAME `fit_idx` the trained arms use (same
`torch.randperm(Ntr, generator=manual_seed(seed))` split), which is what makes
the C2 contrast paired.

References
  * classical LFA / coarse-grid defect correction: https://arxiv.org/pdf/2102.01010,
    https://arxiv.org/html/2103.09962v2, https://arxiv.org/abs/2304.02117
  * the under-comparison thesis that licenses reporting it:
    https://arxiv.org/html/2507.21269v1
"""
from __future__ import annotations

import numpy as np


def fit_transfer(LF: np.ndarray, R: np.ndarray, grid, ridge: float = 0.0) -> np.ndarray:
    """One LSI transfer function `T(k)` mapping LF -> R, least squares over samples.

    `ridge = 0` reproduces B1 turn 2 bit-for-bit (the F6 numbers V2 gates on).
    """
    H, W = int(grid[0]), int(grid[1])
    fl = np.fft.rfft2(np.asarray(LF, dtype=np.float64).reshape(-1, H, W))
    fr = np.fft.rfft2(np.asarray(R, dtype=np.float64).reshape(-1, H, W))
    num = (fr * np.conj(fl)).sum(axis=0)
    den = (np.abs(fl) ** 2).sum(axis=0)
    if float(ridge) != 0.0:
        den = den + float(ridge) * float(den.max() if den.size else 0.0)
    return np.where(den > 1e-20, num / np.maximum(den, 1e-20), 0.0)


def apply_transfer(LF: np.ndarray, T: np.ndarray, grid) -> np.ndarray:
    """`irfft2( rfft2(LF) * T )` for (N, HW) fields -> (N, HW)."""
    H, W = int(grid[0]), int(grid[1])
    LF = np.asarray(LF, dtype=np.float64)
    fl = np.fft.rfft2(LF.reshape(-1, H, W))
    return np.fft.irfft2(fl * T[None, :, :], s=(H, W)).reshape(LF.shape[0], -1)


def band_mean_abs(T: np.ndarray, masks) -> list:
    """Per-band mean |T(k)| -- the diagnostic B1 F7 reported (band gain profile)."""
    a = np.abs(np.asarray(T))
    return [float(a[m].mean()) if np.any(m) else float("nan") for m in masks]


def pack_transfer(T: np.ndarray) -> dict:
    """Checkpoint-safe representation (torch.save handles plain numpy arrays)."""
    T = np.asarray(T)
    return {"real": np.real(T).astype(np.float64), "imag": np.imag(T).astype(np.float64),
            "shape": list(T.shape)}


def unpack_transfer(payload: dict) -> np.ndarray:
    return np.asarray(payload["real"], dtype=np.float64) + 1j * np.asarray(
        payload["imag"], dtype=np.float64)


# ══════════════════════════════════════════════════════════════════════════
# CARD s4_hybrid_routing-B3 -- APPEND-ONLY BLOCK.
#
# Everything ABOVE this line is byte-identical to
# `s6_local-B2 models_r1/s6_local_repair/lsi_filter.py` @ caff5c97 (sha256-16
# `09a4973741594718`), verified before edit and pinned in `manifest.json`.
# Nothing above is modified: `fit_transfer` / `apply_transfer` must stay
# bit-for-bit what validity gate V2 reproduces.
#
# WHAT B3 ADDS (card part 3 edit (1), the D3 leg -- the card's one genuinely
# open surface per the prior-art verdict:
#   "Nobody fits a |k|-dependent LSI transfer function to the fidelity gap and
#    then trains a corrector on ITS residual, and nobody reports the
#    zero-parameter filter as a scored floor beside the trained model.")
#
# The filter is PROMOTED FROM SIDECAR TO PRE-STAGE. `prestage()` below builds
# exactly ONE object, used identically by every arm that needs it:
#
#     C_LSI = alpha_LSI * (T (*) LF),
#       T        solved on `fit_idx` ONLY (never val, never test)
#       alpha_LSI selected by the family's own `fit_alpha` on `val_idx` with 0
#                 in the candidate set -- the SAME protocol, on the SAME split,
#                 that the scored `lsi_alone` arm uses
#
# so that `LF + C_LSI` IS the `lsi_alone` arm's scored prediction, exactly.
# That identity is what makes the router's library members the scored arms
# themselves (validity gate V4) rather than near-copies of them.
#
# BUILDER NOTE ON `alpha_LSI` (recorded, not hidden). The card writes the
# cleaned target as "R - C_LSI" without saying whether the pre-stage carries a
# gain. Reading it as unit gain would (a) make `dc_cleaned`'s base differ from
# the `lsi_alone` arm the router routes to, breaking V4 and the C1 no-harm
# comparison, and (b) put `dc_cleaned` at nRMSE ~2.175 on `ext__helmholtz_2d`
# where the closed-form filter is actively harmful (s6-B2 measured
# `nrmse_LSI_transfer_only` 2.175003954086328 vs copy-LF 0.3294501260438018),
# i.e. it would fail the card's own screen no-harm directive. So the pre-stage
# is the SCORED LSI BRANCH, gain included. `alpha_LSI` is a single scalar fitted
# on `val_idx`; the corrector then trains on `fit_idx`, which is disjoint from
# it. The dependency is disclosed in the diag as
# `prestage.alpha_provenance` and in `notes/handoff_experiment_builder.md`.
# ══════════════════════════════════════════════════════════════════════════


def prestage(LF_tr, R, fit_idx, val_idx, Y_tr, grid, ridge, fit_alpha_fn) -> dict:
    """Fit the LSI pre-stage. Returns T, `alpha_LSI`, and the val diagnostics.

    LF_tr, R, Y_tr : (Ntr, HW) float64 -- copy-LF field, raw residual Y - LF, truth
    fit_idx        : the slice `T` is solved on (the trained arms' training slice)
    val_idx        : the held-out slice `alpha_LSI` is selected on
    fit_alpha_fn   : `local_corrector.fit_alpha` (line search containing 0)

    `rho_lsi_val = 1 - ||R - alpha C||^2 / ||R||^2` on `val_idx` is the statistic
    the card's routing RULE reads (`S4R_RULE_STAT=one_minus_rho_lsi_val`). It is
    RECORDED here and computed in-run -- never transcribed from s6-B2 -- so the
    rule table in card part 4 is a genuine prediction, not a restatement.
    """
    T = fit_transfer(LF_tr[fit_idx], R[fit_idx], grid, ridge=float(ridge))
    C_raw_tr = apply_transfer(LF_tr, T, grid)             # (Ntr, HW), gain 1
    alpha = alpha_ls = 0.0
    val_rel_base = val_rel_gated = float("nan")
    rho = 0.0
    if len(val_idx):
        alpha, alpha_ls, val_rel_base, val_rel_gated = fit_alpha_fn(
            R[val_idx], C_raw_tr[val_idx], LF_tr[val_idx], Y_tr[val_idx],
            include_zero=True)
        den = float((R[val_idx] ** 2).sum())
        rho = (float(1.0 - ((R[val_idx] - alpha * C_raw_tr[val_idx]) ** 2).sum() / den)
               if den > 0 else 0.0)
    return {
        "T": T,
        "C_raw_train": C_raw_tr,
        "alpha_lsi": float(alpha),
        "alpha_lsi_ls": float(alpha_ls),
        "rho_lsi_val": float(rho),
        "one_minus_rho_lsi_val": float(1.0 - rho),
        "val_rel_base": float(val_rel_base),
        "val_rel_gated": float(val_rel_gated),
        "n_fit": int(len(fit_idx)),
        "n_val": int(len(val_idx)),
        "ridge": float(ridge),
        "alpha_provenance": (
            "fit_alpha (line search containing 0) on val_idx -- the SAME protocol "
            "and split the scored `lsi_alone` arm uses, so LF + C_LSI IS that arm's "
            "prediction (validity gate V4). T itself is solved on fit_idx only."),
    }


def prestage_correction(LF, T, alpha, grid):
    """`alpha * (T (*) LF)` for any (N, HW) copy-LF field -- train or test."""
    import numpy as _np
    C = apply_transfer(LF, T, grid)
    return _np.asarray(alpha, dtype=_np.float64) * C


# ══════════════════════════════════════════════════════════════════════════
# CARD r3s2_field_reach-B2 — APPEND-ONLY BLOCK.
#
# Everything ABOVE this line is byte-identical to the B1 file (sha256 recorded
# in the RE-VENDORED header and in `_vendor_manifest.json`). `fit_transfer` /
# `apply_transfer` are NOT touched: arm `A5_stack_ic_unreg` is the literal B1
# replay and must reproduce the stream anchor 12.9556 bit-for-bit-ish, which is
# G2 leg (iv). The repair below is a NEW estimator beside the old one, never a
# replacement of it.
#
# ── WHAT THIS BLOCK IS, AND WHAT IT IS NOT ───────────────────────────────
# It is an INSTRUMENT REPAIR carried as an ACCEPTANCE GATE (card G2), not a
# contribution. The prior-art verdict E1 is explicit: ridge + band-limiting of a
# Wiener/deconvolution operator is `preempted (cite)`, "usable ONLY as an
# instrument repair, never as a contribution", and "Presenting ridge/band-limiting
# as the *idea* is a rebadge". The only open thing is the MEASUREMENT: that this
# stack's whole panel-level 3-seed spread was attributable to an unregularised
# band above the LF Nyquist. Nothing here claims method novelty.
#
# Preemption citations (recipe / card part 3):
#   * arXiv:1810.08360 — LOOCV selection of a Tikhonov/ridge coefficient.
#   * arXiv:1511.07030 — shrinkage rationale at very low sample support
#                        (n_fit = 3 on the ifc cells).
#   * arXiv:2606.03936 — per-band weighting of a frozen operator.
#
# ── THE TWO REPAIRS (recipe `env`, verbatim) ─────────────────────────────
# `S6_LSI_BANDLIMIT=lf_nyquist_from_ladder`, `S6_LSI_BANDLIMIT_MODE=zero_above_kcut`,
# `S6_LSI_KCUT_SOURCE=ladder_shape_ratio_adr_r2_0001`:
#     k_cut = k_Nyq_HF * N_LF / N_HF,  k_Nyq_HF = min(H, W) / 2
#   computed from the ACTUAL ladder shapes (the registered HF working grid and
#   the LF rung's native grid), and T(k) is set to exactly 0 on the radial
#   wavenumber ring `kr >= k_cut`. The upsampled pseudo-LF carries no independent
#   power at or above its own Nyquist ring, so a Wiener ratio there is a 0/0
#   whose magnitude is decided by the fit fold — B1 measured |T| band-4 = 66.219
#   on ifc_poisson seed 2 from n_fit = 3, and a 15x scored-nRMSE swing with it.
#
#   BUILDER NOTE ON `>=` vs `>` (recorded, not hidden). "zero_above_kcut" does
#   not say whether the k_cut ring itself is kept. This block zeroes `kr >= k_cut`
#   (the ring INCLUDED) because (a) the Nyquist ring is exactly the aliasing ring,
#   where the coarse solve's content is least trustworthy, and (b) the family's
#   dyadic band grid (`bands.band_masks`) puts band 4 at `kr >= k_ny_HF / 2`,
#   which for a 2x ladder IS `kr >= k_cut`, so the `>=` convention makes band 4
#   exactly 0 and therefore makes G2 leg (iii) — "band-mean |T| > 1 on any scored
#   cell" — a decidable check on bands 1-3 rather than a boundary argument. The
#   convention is recorded in the diag as `lsi_repair.bandlimit.ring_convention`.
#
# `S6_LSI_RIDGE=loocv`, `S6_LSI_RIDGE_GRID=0,1e-6,1e-4,1e-3,1e-2,1e-1`,
# `S6_LSI_RIDGE_SELECT=loocv_on_fit_fold_only`, `S6_LEAKAGE_TRIPWIRE=1`:
#   exact leave-one-out CV over the ROWS OF THE FIT FOLD ONLY. The estimator is
#   linear in per-row FFT accumulators, so the LOO refit is exact and closed
#   form: subtract row i's contribution from the numerator/denominator sums and
#   re-apply the ridge with THAT SUBSET's own `den.max()` — which is exactly what
#   `fit_transfer` would return if called on `fit_idx \ {i}`. There is no
#   approximation and no val/test array is touched (the caller passes fit-fold
#   rows only; `loocv_row_ids` is recorded so the tripwire is auditable).
#   Ties are broken toward the SMALLEST ridge (grid order, `np.argmin`), i.e.
#   toward least shrinkage, so the selector cannot manufacture regularisation
#   that the fold does not pay for.
# ══════════════════════════════════════════════════════════════════════════

LOOCV_RIDGE_GRID_RECIPE = (0.0, 1e-6, 1e-4, 1e-3, 1e-2, 1e-1)


def parse_ridge_grid(spec) -> list:
    """`S6_LSI_RIDGE_GRID` csv -> sorted-as-written list of floats."""
    if isinstance(spec, (list, tuple)):
        vals = list(spec)
    else:
        vals = [s for s in str(spec).split(",") if s.strip() != ""]
    out = [float(v) for v in vals]
    if not out:
        raise ValueError(f"empty ridge grid {spec!r}")
    if any(v < 0 for v in out):
        raise ValueError(f"negative ridge in {spec!r}")
    return out


def kcut_from_ladder(lf_grid, hf_grid) -> dict:
    """`k_cut = k_Nyq_HF * N_LF/N_HF` from the ACTUAL ladder shapes.

    `N_LF/N_HF` is the per-axis cell-count ratio; on every panel cell the ladder
    is isotropic (H == W, h == w) so `k_cut` reduces to `min(h, w) / 2`, i.e. the
    LF rung's own Nyquist expressed in HF-grid wavenumber index units. The
    anisotropic form is kept general and the two forms are cross-recorded.
    """
    H, W = int(hf_grid[0]), int(hf_grid[1])
    h, w = int(lf_grid[0]), int(lf_grid[1])
    k_ny_hf = min(H, W) / 2.0
    ratio = min(h, w) / float(min(H, W))
    k_cut = k_ny_hf * ratio
    return {
        "k_nyquist_hf": float(k_ny_hf),
        "n_lf_over_n_hf_per_axis": float(ratio),
        "k_cut": float(k_cut),
        "k_nyquist_lf_direct": float(min(h, w) / 2.0),
        "isotropic_ladder": bool(H == W and h == w),
        "hf_grid": [H, W], "lf_grid": [h, w],
        "source": "S6_LSI_KCUT_SOURCE=ladder_shape_ratio_adr_r2_0001",
    }


def radial_k(grid) -> "np.ndarray":
    """`|k|` on the rFFT half-plane, in the SAME index units `bands.band_masks`
    uses (kx = fftfreq(H)*H, ky = 0..W//2), so `k_cut` and the dyadic band edges
    are directly comparable."""
    H, W = int(grid[0]), int(grid[1])
    kx = np.fft.fftfreq(H) * H
    ky = np.arange(W // 2 + 1, dtype=np.float64)
    return np.sqrt(kx[:, None] ** 2 + ky[None, :] ** 2)


def bandlimit_mask(grid, k_cut: float) -> "np.ndarray":
    """True where `T` is forced to zero (`kr >= k_cut`; see the `>=` note above)."""
    return radial_k(grid) >= float(k_cut)


def _accumulators(LF: np.ndarray, R: np.ndarray, grid):
    H, W = int(grid[0]), int(grid[1])
    fl = np.fft.rfft2(np.asarray(LF, dtype=np.float64).reshape(-1, H, W))
    fr = np.fft.rfft2(np.asarray(R, dtype=np.float64).reshape(-1, H, W))
    return fl, fr


def _solve(num, den_raw, ridge: float, zero_mask=None):
    """The EXACT arithmetic of `fit_transfer`, factored so the LOO path and the
    full-fold path cannot drift apart."""
    den = den_raw
    if float(ridge) != 0.0:
        den = den_raw + float(ridge) * float(den_raw.max() if den_raw.size else 0.0)
    T = np.where(den > 1e-20, num / np.maximum(den, 1e-20), 0.0)
    if zero_mask is not None:
        T = np.where(zero_mask, 0.0, T)
    return T


def fit_transfer_regularised(LF: np.ndarray, R: np.ndarray, grid, ridge_grid,
                             k_cut=None, row_ids=None) -> dict:
    """LOOCV-ridged, optionally band-limited LSI transfer function.

    LF, R    : (n_fit, HW) — FIT-FOLD ROWS ONLY. The caller is responsible for
               slicing; `row_ids` is recorded verbatim so `S6_LEAKAGE_TRIPWIRE`
               can be audited from the diag.
    ridge_grid : the candidate coefficients (recipe `S6_LSI_RIDGE_GRID`).
    k_cut    : None -> no band-limit; else zero `T` on `kr >= k_cut`.

    Returns the fitted `T` plus the full selection record. `ridge_grid` of a
    single value degenerates to a plain ridged fit with the LOO curve recorded.
    """
    H, W = int(grid[0]), int(grid[1])
    LF = np.asarray(LF, dtype=np.float64).reshape(-1, H * W)
    R = np.asarray(R, dtype=np.float64).reshape(-1, H * W)
    n = int(LF.shape[0])
    if n < 1:
        raise ValueError("fit_transfer_regularised needs at least one fit row")
    grid_vals = parse_ridge_grid(ridge_grid)
    zero_mask = None if k_cut is None else bandlimit_mask(grid, k_cut)

    fl, fr = _accumulators(LF, R, grid)
    num_all = (fr * np.conj(fl)).sum(axis=0)
    den_all = (np.abs(fl) ** 2).sum(axis=0)

    if n >= 2:
        sse = np.zeros(len(grid_vals), dtype=np.float64)
        for i in range(n):
            num_i = num_all - fr[i] * np.conj(fl[i])
            den_i = den_all - np.abs(fl[i]) ** 2
            for j, lam in enumerate(grid_vals):
                T_i = _solve(num_i, den_i, lam, zero_mask)
                pred = np.fft.irfft2(fl[i] * T_i, s=(H, W)).reshape(-1)
                sse[j] += float(((R[i] - pred) ** 2).sum())
        j_star = int(np.argmin(sse))          # ties -> smallest ridge (grid order)
        loo_curve = [float(v) for v in sse]
        selected_by = "exact_leave_one_out_on_fit_fold"
    else:
        # One fit row: LOO is undefined (the held-out fit is empty). Refuse to
        # invent a curve; take the LARGEST shrinkage in the grid and say so.
        sse = None
        j_star = len(grid_vals) - 1
        loo_curve = None
        selected_by = "n_fit_eq_1_loo_undefined_max_shrinkage_taken"
    lam_star = float(grid_vals[j_star])
    T = _solve(num_all, den_all, lam_star, zero_mask)

    return {
        "T": T,
        "ridge": lam_star,
        "ridge_grid": [float(v) for v in grid_vals],
        "loo_sse_by_ridge": loo_curve,
        "selected_by": selected_by,
        "n_fit": n,
        "loocv_row_ids": (None if row_ids is None
                          else [int(v) for v in np.asarray(row_ids).ravel()]),
        "bandlimit": (None if k_cut is None else {
            "k_cut": float(k_cut),
            "ring_convention": "zero where kr >= k_cut (the k_cut ring INCLUDED)",
            "n_zeroed_modes": int(zero_mask.sum()),
            "n_modes_total": int(zero_mask.size),
            "frac_zeroed": float(zero_mask.mean()),
        }),
        "max_abs_T": float(np.abs(T).max()) if T.size else float("nan"),
        "note": ("instrument repair (card G2), NOT a contribution — see the "
                 "APPEND-ONLY block header and INSPIRATION.md."),
    }


def assert_bandlimited(T: np.ndarray, grid, k_cut: float, tol: float = 0.0) -> dict:
    """Validity gate: `T` is exactly zero on `kr >= k_cut`."""
    m = bandlimit_mask(grid, k_cut)
    worst = float(np.abs(np.asarray(T)[m]).max()) if np.any(m) else 0.0
    if worst > tol:
        raise ValueError(
            f"band-limit gate: |T| = {worst!r} above k_cut = {k_cut!r} (tol {tol})")
    return {"max_abs_T_above_kcut": worst, "n_modes_above_kcut": int(m.sum()),
            "k_cut": float(k_cut), "pass": True}
