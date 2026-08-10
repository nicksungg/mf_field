# == RE-VENDORED (round-3 card r3s2_field_reach-B2) ==========================
# SOURCE : round3/worktrees/r3s2_field_reach/B1/models_r3/r3s2_stack_ic/sidecars.py
# COMMIT : d5069a74bb63da837b89b16508ae25a2164780cc  (tip of branch
#          round3/exp-r3s2_field_reach-B1; recipe.env._vendor_source. The
#          recipe's `base_commit` 76d15c2d is a TRUNK commit that carries NO
#          models_r3/ tree at all -- see notes/handoff_experiment_builder.md.)
# SHA256 : ec62e9c4a01c3305991d7d3e29d12575a028449b2e2444a492bfba8e3b36b9ef
# STATUS : byte-identical below this header EXCEPT a clearly marked APPEND-ONLY block at the end of the file (map_smoothness).
#          Copied, never imported: score_panel.py::code_hash hashes only
#          family_dir/**/*.py, so logic outside the family dir is invisible to
#          the eval cache key.
# ROLE   : declared reuse role (a), round-2 program 5.10a -- the DC-lineage
#          corrector stays a FROZEN test-time sub-component behind a
#          condition->pseudo-LF front end. The B2 contribution is the ROUTE
#          SWITCH + budget accountant, not this code.
# ============================================================================
"""Round-3 sidecar instruments for card `r3s2_field_reach-B1`.

Each function answers one pre-registered question and NOTHING in the scoring
path reads any of them — they are recorded in the diag for the analyzer.

  `centred_gamma`            per-band centred coherence, VENDORED verbatim from
                             `round2/worktrees/r2s2_stacked/B3/models_r2/
                             r2s2_zerograd/smoke_eval.py::centred_gamma`. Under
                             r2s2-B2's STOP-EXPORT it is **directional only**:
                             knob `R3S2_CENTRED_GAMMA_SIDECAR=
                             directional_only_with_permutation_null`, so it is
                             published WITH its permutation null and an affine
                             ceiling and never as a gate or a threshold.
  `zero_gradient_ladder`     the closed-form alternative priced on the SAME
                             intermediate, out of fold, before any trained stage
                             is credited (card part 3). Rung definitions follow
                             `round2/tools/zero_gradient_stage_ladder.py`
                             (S0 raw / S1 gain / S2 lsi / S3 blend_raw /
                             S4 blend_lsi / S5 free_joint), re-expressed in-job
                             because that tool's `--family_dir` interface
                             (folds/ladders/floors modules) is a different
                             family shape.
  `ic_cos`                   how much of the readout-time field the exact IC
                             channel explains on its own (knob
                             `R3S2_IC_COS_SIDECAR=1`), against its own shuffled
                             null.
  `target_scale_spread`      the pre-flight statistics of
                             `round2/tools/target_scale_spread_audit.py`,
                             recorded ONLY (see the module note on ADR r3-0004).
"""
from __future__ import annotations

import numpy as np


# ── centred coherence (report-only, directional) ─────────────────────────


def centred_gamma(X: np.ndarray, Y: np.ndarray, grid, masks) -> list:
    # == VENDORED verbatim (body) from round2 r2s2_zerograd/smoke_eval.py ==
    """Per-band centred coherence between the intermediate and the target.

    REPORT-ONLY (r2s2-B2 STOP-EXPORT, carried into round 3 as
    `R3S2_CENTRED_GAMMA_SIDECAR=directional_only_with_permutation_null`):
    nothing in this family reads the return value, and no arm, rung or dataset
    is gated on it. It is recorded as a directional descriptor for the analyzer
    only.
    """
    H, W = int(grid[0]), int(grid[1])
    Xc = X - X.mean(axis=0, keepdims=True)
    Yc = Y - Y.mean(axis=0, keepdims=True)
    n = Xc.shape[0]
    if Xc.shape[1] != H * W:
        return []
    fx = np.fft.rfft2(Xc.reshape(n, H, W))
    fy = np.fft.rfft2(Yc.reshape(n, H, W))
    sxy = (fx * np.conj(fy)).sum(axis=0)
    sxx = (np.abs(fx) ** 2).sum(axis=0)
    syy = (np.abs(fy) ** 2).sum(axis=0)
    g2 = np.abs(sxy) ** 2 / np.maximum(sxx * syy, 1e-300)
    return [float(np.sqrt(np.clip(g2[m], 0, 1)).mean()) if np.any(m) else None
            for m in masks]


def _affine_fit_predict(Xc: np.ndarray, Y: np.ndarray) -> np.ndarray:
    """Min-norm least-squares affine map condition -> field, in-sample.

    Same estimator class as the certified `affine_on_hf_train` floor
    (launch_anchors.json): `[X, 1] B ~ Y` via `lstsq`. In-sample by design — it
    is used as a CEILING for the coherence statistic, not as a prediction arm.
    """
    A = np.concatenate([np.asarray(Xc, dtype=np.float64),
                        np.ones((Xc.shape[0], 1))], axis=1)
    B, *_ = np.linalg.lstsq(A, np.asarray(Y, dtype=np.float64), rcond=None)
    return A @ B


def centred_gamma_block(X_inter: np.ndarray, Y: np.ndarray, cond: np.ndarray,
                        grid, masks, seed: int, n_perm: int = 8) -> dict:
    """`centred_gamma` + its permutation null + the affine ceiling.

    The permutation null re-runs the SAME statistic with the target rows shuffled
    against the intermediate, which destroys the pairing and leaves only the
    finite-sample floor of the estimator. The affine ceiling is the coherence an
    in-sample affine condition->field map reaches on the same rows — the level
    at which "coherent" means "linear in the condition" and nothing more.
    Publishing both next to the statistic is the round-2 zero-information-null
    rule; the DIRECTION (above/below its own null) is all this sidecar claims.
    """
    obs = centred_gamma(X_inter, Y, grid, masks)
    if not obs:
        return {"status": "skipped (intermediate is not on the working grid)"}
    rng = np.random.default_rng(int(seed))
    n = int(Y.shape[0])
    perms = []
    for _ in range(int(n_perm)):
        p = rng.permutation(n)
        perms.append(centred_gamma(X_inter, Y[p], grid, masks))
    arr = np.asarray([[np.nan if v is None else v for v in row] for row in perms],
                     dtype=np.float64)
    null_mean = [float(v) for v in np.nanmean(arr, axis=0)]
    null_max = [float(v) for v in np.nanmax(arr, axis=0)]
    ceiling = centred_gamma(_affine_fit_predict(cond, Y), Y, grid, masks)
    direction = [None if (o is None) else ("above_null" if o > m else "at_or_below_null")
                 for o, m in zip(obs, null_max)]
    return {
        "gamma_per_band": obs,
        "permutation_null_mean": null_mean,
        "permutation_null_max": null_max,
        "n_permutations": int(n_perm),
        "affine_ceiling_per_band": ceiling,
        "direction_vs_null": direction,
        "read_as": ("DIRECTIONAL ONLY (r2s2-B2 stop-export). No threshold, no gate, "
                    "no magnitude claim: report whether a band sits above its own "
                    "permutation null and where it sits relative to the affine "
                    "ceiling. Nothing in the scoring path reads this."),
    }


# ── the zero-gradient closed-form ladder ─────────────────────────────────


def _rel_nrmse(pred: np.ndarray, target: np.ndarray, nrmse_fn) -> float:
    return float(nrmse_fn(np.asarray(pred, dtype=np.float64),
                          np.asarray(target, dtype=np.float64)))


def zero_gradient_ladder(X_tr: np.ndarray, X_te: np.ndarray, Y_tr: np.ndarray,
                         Y_te: np.ndarray, base_tr: np.ndarray, base_te: np.ndarray,
                         grid, fit_idx, calib_idx, lsi_fit, lsi_apply,
                         fit_alpha, nrmse_fn, ridge: float = 0.0) -> dict:
    """Price the closed-form alternative on the SAME intermediate, out of fold.

    `X_*` is the intermediate (the pseudo-LF field on the HF working grid),
    `base_*` a training-free base field (the train-mean HF field) that the blend
    rungs mix against. Every selection is made on `calib_idx` — a train slice
    the transfer function was NOT fitted on — and every number is then read on
    TEST. No gradient step is taken anywhere in this function.

    Rungs (`round2/tools/zero_gradient_stage_ladder.py`):
      S0 raw        the intermediate itself                     0 parameters
      S1 gain       a* . X,   a* on calib                       1 selection
      S2 lsi        X + alpha . (T (*) X), T closed-form on fit,
                    alpha out of fold on calib                  0 gradient steps
      S3 blend_raw  lam . X  + (1-lam) . base   on calib        1 selection
      S4 blend_lsi  lam . S2 + (1-lam) . base   on calib        1 selection
      S5 free_joint joint (a, lam) grid on calib                2 selections
    """
    fit_idx = np.asarray(fit_idx, dtype=np.int64)
    calib_idx = np.asarray(calib_idx, dtype=np.int64)
    out = {"n_fit": int(fit_idx.size), "n_calib": int(calib_idx.size),
           "selection_split": "train calib slice (disjoint from the T fit slice)",
           "evaluated_on": "test"}

    def _sel_scalar(cands, make):
        best, best_v = None, np.inf
        for c in cands:
            v = _rel_nrmse(make(c, calib_idx), Y_tr[calib_idx], nrmse_fn)
            if np.isfinite(v) and v < best_v:
                best, best_v = c, v
        return best, float(best_v)

    # S0
    out["S0_raw"] = {"test_nrmse": _rel_nrmse(X_te, Y_te, nrmse_fn), "n_selections": 0}

    # S1 gain: closed-form least-squares gain on calib, plus a small guard grid
    num = float((X_tr[calib_idx] * Y_tr[calib_idx]).sum())
    den = float((X_tr[calib_idx] ** 2).sum())
    a_ls = num / den if den > 0 else 1.0
    grid_a = sorted({1.0, float(a_ls)} | {round(0.1 * i, 3) for i in range(1, 21)})
    a_star, a_calib = _sel_scalar(grid_a, lambda a, ix: a * X_tr[ix])
    out["S1_gain"] = {"a_star": float(a_star), "a_lstsq_on_calib": float(a_ls),
                      "calib_nrmse": a_calib, "n_selections": 1,
                      "test_nrmse": _rel_nrmse(a_star * X_te, Y_te, nrmse_fn)}

    # S2 lsi: T on the fit slice, alpha out of fold on calib (line search incl. 0)
    R_fit = Y_tr[fit_idx] - X_tr[fit_idx]
    T = lsi_fit(X_tr[fit_idx], R_fit, grid, ridge=ridge)
    C_tr = lsi_apply(X_tr, T, grid)
    C_te = lsi_apply(X_te, T, grid)
    alpha, alpha_ls, _, _ = fit_alpha(Y_tr[calib_idx] - X_tr[calib_idx], C_tr[calib_idx],
                                      X_tr[calib_idx], Y_tr[calib_idx], include_zero=True)
    S2_tr = X_tr + float(alpha) * C_tr
    S2_te = X_te + float(alpha) * C_te
    out["S2_lsi"] = {"alpha": float(alpha), "alpha_linesearch": float(alpha_ls),
                     "n_gradient_steps": 0,
                     "test_nrmse": _rel_nrmse(S2_te, Y_te, nrmse_fn)}

    # S3 / S4 blends against the training-free base
    lam_grid = [round(0.05 * i, 3) for i in range(21)]
    l3, l3c = _sel_scalar(lam_grid, lambda l, ix: l * X_tr[ix] + (1 - l) * base_tr[ix])
    out["S3_blend_raw"] = {"lambda_star": float(l3), "calib_nrmse": l3c,
                           "n_selections": 1,
                           "test_nrmse": _rel_nrmse(l3 * X_te + (1 - l3) * base_te,
                                                    Y_te, nrmse_fn)}
    l4, l4c = _sel_scalar(lam_grid, lambda l, ix: l * S2_tr[ix] + (1 - l) * base_tr[ix])
    out["S4_blend_lsi"] = {"lambda_star": float(l4), "calib_nrmse": l4c,
                           "n_selections": 1,
                           "test_nrmse": _rel_nrmse(l4 * S2_te + (1 - l4) * base_te,
                                                    Y_te, nrmse_fn)}

    # S5 free joint (a, lam) on calib
    best, best_v = (1.0, 1.0), np.inf
    for a in grid_a:
        Xa_c = a * X_tr[calib_idx]
        for l in lam_grid:
            v = _rel_nrmse(l * Xa_c + (1 - l) * base_tr[calib_idx],
                           Y_tr[calib_idx], nrmse_fn)
            if np.isfinite(v) and v < best_v:
                best, best_v = (a, l), v
    a5, l5 = best
    out["S5_free_joint"] = {"a_star": float(a5), "lambda_star": float(l5),
                            "calib_nrmse": float(best_v), "n_selections": 2,
                            "test_nrmse": _rel_nrmse(l5 * (a5 * X_te) + (1 - l5) * base_te,
                                                     Y_te, nrmse_fn)}
    out["base_field"] = "train-mean HF field over the fit slice (training-free)"
    out["read_as"] = ("if a trained arm does not beat the best of S0-S5 by a certified "
                      "margin, the trained stage earned nothing on this intermediate — "
                      "price the closed form FIRST (card part 3).")
    return out


# ── how much does the exact IC field explain on its own? ─────────────────


def ic_cos(ic_up: np.ndarray, Y: np.ndarray, ic_up_shuffled: np.ndarray = None) -> dict:
    """Mean-removed cosine between the synthesised IC channel (lifted to the HF
    grid) and the readout-time HF field, with the shuffled-IC null beside it.

    The IC is the state at t=0 and the target is the state at the readout time,
    so this is NOT expected to be large; it is the honest statement of how much
    of the field the exact initial condition carries forward, and it is the
    quantity that makes the E1-vs-E1n contrast interpretable.
    """
    def _cos(A, B):
        Ac = np.asarray(A, dtype=np.float64) - np.asarray(A, dtype=np.float64).mean(axis=0, keepdims=True)
        Bc = np.asarray(B, dtype=np.float64) - np.asarray(B, dtype=np.float64).mean(axis=0, keepdims=True)
        na = np.linalg.norm(Ac, axis=1)
        nb = np.linalg.norm(Bc, axis=1)
        ok = (na > 0) & (nb > 0)
        if not np.any(ok):
            return None
        c = (Ac[ok] * Bc[ok]).sum(axis=1) / (na[ok] * nb[ok])
        return {"mean": float(np.mean(c)), "median": float(np.median(c)),
                "abs_mean": float(np.mean(np.abs(c))), "n": int(ok.sum())}
    out = {"observed": _cos(ic_up, Y),
           "note": ("centred per-sample cosine between the exact synthesised IC field "
                    "and the HF field at the readout time, TRAIN rows only")}
    if ic_up_shuffled is not None:
        out["shuffled_ic_null"] = _cos(ic_up_shuffled, Y)
    return out


# ── target-scale pre-flight (RECORDED; VOID for claim purposes) ──────────


def target_scale_spread(Y_tr: np.ndarray, LF_up_tr: np.ndarray) -> dict:
    """The statistics of `round2/tools/target_scale_spread_audit.py`, recorded.

    ADR r3-0004 makes `sharp__phase_field_crystal_2d` REPORT-ONLY and voids the
    recipe's pfc target-scaler pre-flight (`R3S2_TARGET_SCALER_PREFLIGHT=
    pfc_per_sample_if_outlier_dominated`) for claim purposes. This family
    therefore MEASURES the spread on every dataset and CHANGES NOTHING: the
    residual scaler stays the single global `max|HF - LF_up|` of the base family
    on every cell, so no dataset's estimator differs from any other's.
    """
    R = np.asarray(Y_tr, dtype=np.float64) - np.asarray(LF_up_tr, dtype=np.float64)
    per = np.abs(R).max(axis=1)
    nrm = np.linalg.norm(R, axis=1)
    e = nrm ** 2
    tot = float(e.sum())
    order = np.argsort(e)[::-1]
    k5 = max(1, int(round(0.05 * e.size)))
    med = float(np.median(per)) if per.size else 0.0
    scaler = float(per.max()) if per.size else 0.0
    return {
        "resid_norm_max_over_median": (float(nrm.max() / np.median(nrm))
                                       if np.median(nrm) > 0 else None),
        "resid_norm_p99_over_median": (float(np.percentile(nrm, 99) / np.median(nrm))
                                       if np.median(nrm) > 0 else None),
        "scaler_global_max": scaler,
        "scaler_over_median_per_sample_max": (scaler / med) if med > 0 else None,
        "energy_share_top1": (float(e[order[0]] / tot) if tot > 0 else None),
        "energy_share_top5pct": (float(e[order[:k5]].sum() / tot) if tot > 0 else None),
        "effective_n_samples_of_mse": (float(tot ** 2 / float((e ** 2).sum()))
                                       if float((e ** 2).sum()) > 0 else None),
        "median_normalised_target_max": (med / scaler) if scaler > 0 else None,
        "applied": False,
        "status": ("RECORDED ONLY. The recipe's pfc-conditional per-sample scaler is "
                   "VOID under ADR r3-0004 (pfc is report-only, its scored cell is "
                   "task-void); the global scaler is used on every dataset so no cell "
                   "carries a different estimator."),
    }


# ══════════════════════════════════════════════════════════════════════════
# CARD r3s2_field_reach-B2 — APPEND-ONLY BLOCK. Everything above is byte-identical
# to the B1 file (sha256 in `_vendor_manifest.json`).
#
# THE E3 INSTRUMENT: a model-free map-smoothness sidecar on all five scored cells
# (card part 3, `R3S2B2_MAP_SMOOTHNESS_SIDECAR=1`). E3's prior-art verdict leaves
# open only "the **paired** application ... used PROSPECTIVELY to rule a cell
# off-limits for capacity spending", so this card declares BEFORE the run that
# `sharp__cahn_hilliard` is approximability-limited (ratio 0.980) and therefore
# that the ROUTE is not a binding constraint there (falsification clause G3).
# For the declaration to be prospective the statistic has to be re-measured
# in-job on every cell, on the same rows the arms see.
#
# ESTIMATOR PROVENANCE: identical arithmetic to
# `round3/tools/task_linearity_audit.py::audit` (nearest-neighbour-in-standardised-
# condition relative field difference, median, over a random-pair baseline). That
# tool is CITED, never imported — `score_panel.py::code_hash` hashes only
# `family_dir/**/*.py`, so logic living outside the family dir is invisible to
# the eval cache key. Nothing here reads a model, a gradient, or a checkpoint.
# ══════════════════════════════════════════════════════════════════════════


def map_smoothness(Y: np.ndarray, C: np.ndarray, max_rows: int = 128,
                   rng_seed: int = 0) -> dict:
    """`nn / random` median relative field difference — high => non-smooth map.

    Y : (N, HW) fields, C : (N, d) condition vectors, same rows, same order.
    `map_smoothness_ratio` near 1 means a nearest neighbour in condition space is
    no more informative about the field than a random other sample, i.e. the
    condition->field map is not resolvable at the available sampling density and
    the limit is APPROXIMABILITY, not information.
    """
    Y = np.asarray(Y, dtype=np.float64)
    C = np.asarray(C, dtype=np.float64)
    n = int(min(int(max_rows), Y.shape[0]))
    if n < 3:
        return {"n": int(n), "applicable": False,
                "reason": "fewer than 3 rows: nearest-neighbour statistic undefined"}
    Y, C = Y[:n], C[:n]
    Cs = (C - C.mean(axis=0)) / (C.std(axis=0) + 1e-12)
    D = ((Cs[:, None, :] - Cs[None, :, :]) ** 2).sum(-1)
    np.fill_diagonal(D, np.inf)
    j = D.argmin(axis=1)
    den = np.linalg.norm(Y, axis=1)
    nn_rel = float(np.median(np.linalg.norm(Y - Y[j], axis=1) / den))
    perm = np.random.default_rng(int(rng_seed)).permutation(n)
    rand_rel = float(np.median(np.linalg.norm(Y - Y[perm], axis=1) / den))
    ratio = (nn_rel / rand_rel) if rand_rel else None
    return {
        "n": int(n), "applicable": True, "cond_dim": int(C.shape[1]),
        "nn_cond_rel_field_diff_median": nn_rel,
        "random_pair_rel_field_diff_median": rand_rel,
        "map_smoothness_ratio": ratio,
        "mean_removed_variance_fraction": float(
            (((Y - Y.mean(axis=0, keepdims=True)) ** 2).sum()) / max((Y ** 2).sum(), 1e-300)),
        "non_smooth_flag": bool(ratio is not None and ratio > 0.95),
        "smoothness_tol": 0.95,
        "estimator": ("same arithmetic as round3/tools/task_linearity_audit.py::audit "
                      "(cited, never imported); rng_seed fixes the random-pair "
                      "permutation"),
        "rng_seed": int(rng_seed),
    }
