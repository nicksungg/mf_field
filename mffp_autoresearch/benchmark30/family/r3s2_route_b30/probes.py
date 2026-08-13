# == RE-VENDORED (round-3 card r3s2_field_reach-B2) ==========================
# SOURCE : round3/worktrees/r3s2_field_reach/B1/models_r3/r3s2_stack_ic/probes.py
# COMMIT : d5069a74bb63da837b89b16508ae25a2164780cc  (tip of branch
#          round3/exp-r3s2_field_reach-B1; recipe.env._vendor_source. The
#          recipe's `base_commit` 76d15c2d is a TRUNK commit that carries NO
#          models_r3/ tree at all -- see notes/handoff_experiment_builder.md.)
# SHA256 : 37f4b2d6a594992c0c477e849fb03984c3e39a52d0bec3e5c53161e91397ee2a
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
# SOURCE : round2/worktrees/r2s2_stacked/B1/models_r2/r2s2_stack/probes.py
# COMMIT : 6b4e1d4825666e037a43675c83d9bda6289ec9d0  (recipe.env._vendor_source)
# SHA256 : 29238e4c8b944303ac0a69a12e89a4c7f5250409a6e18a072e94e59e1eb769e2
# STATUS : byte-identical below this header (the round-2 header block and the
#          body are unchanged). Copied, never imported: score_panel.py::code_hash
#          hashes only family_dir/**/*.py.
# ROLE   : declared reuse role (a), round-2 program 5.10a -- the DC-lineage
#          corrector is a frozen test-time sub-component behind a NEW
#          condition->pseudo-LF front end. The reuse IS the experiment.
# ==============================================================================
"""Training-free, PRE-REGISTERED probes P1 and P2 for card `r2s2_stacked-B1`.

Both run BEFORE any optimizer is constructed and are recorded in the diag, so
the card's falsification is decidable against numbers that no training run can
retro-fit (card part 3: "both recorded before training so the falsification is
decidable").

P1 — BC-match audit.
    ADAPTED WITH CITATION from `round2/tools/spectral_prestage_bc_audit.py`
    (itself promoted from the s4-B3 mechanism turns 1-2; its `fit_transfer` /
    `fit_alpha` semantics are classical multigrid LFA + the s6 line search —
    ZERO novelty claimed). TWO adaptations, both forced by round 2:
      (a) the tool scores its two branches on the TEST split via
          `panel_data.load_split` / `copylf_prediction`, which read the ORIGINAL
          `data_root` (test LF present). That path is illegal for family code
          (program.md §5.9, stripped test view). This adaptation runs the whole
          audit on the TRAIN split only: `T` is fit on `fit_idx`, the gain on
          `val_a`, and both branches are scored on the held-out train slice.
      (b) the LF base is the CORRECTED upsampled train LF (card Decision B),
          not the round-1 defective `zoom` path.
    Verdict semantics, ring binning and `mirror_delta_pct` are unchanged.

P2 — condition -> LF identifiability.
    ADR r2-0003's method ("L2 nearest in per-dim train-standardized condition
    space") applied to the LF FIELD instead of the HF field, which is exactly
    the quantity the ADR reports for pfc (1.148 in `train_l1.npz`) and
    fisher_kpp (0.412 in LF). Answers, training-free, whether a condition-only
    emulator can be sample-specific on this dataset at all: a large relative
    field difference between the two closest-in-condition train samples means
    the LF field is NOT a function of the condition vector, so the emulator is
    bounded by E[LF | c] and arm A5 `condmean_lf` should tie arm A2 `frozen`.
"""
from __future__ import annotations

import numpy as np

from lsi_filter import apply_transfer, fit_transfer
from local_corrector import fit_alpha, rel_l2

RING_EDGES = [0, 1, 2, 4, 8, 16, 10 ** 9]   # distance-to-boundary in cells (tool's)


def _rms(a) -> float:
    a = np.asarray(a, dtype=np.float64)
    return float(np.sqrt((a ** 2).mean())) if a.size else 0.0


def mirror_ext(a, H: int, W: int) -> np.ndarray:
    """Even-symmetric (whole-sample) extension to (2H, 2W): a NON-periodic BC."""
    f = np.asarray(a, dtype=np.float64).reshape(-1, H, W)
    f = np.concatenate([f, f[:, :, ::-1]], axis=2)
    f = np.concatenate([f, f[:, ::-1, :]], axis=1)
    return f.reshape(f.shape[0], -1)


def ring_labels(H: int, W: int) -> np.ndarray:
    yy, xx = np.meshgrid(np.arange(H), np.arange(W), indexing="ij")
    d = np.minimum(np.minimum(yy, H - 1 - yy), np.minimum(xx, W - 1 - xx))
    lab = np.zeros((H, W), dtype=int)
    for i in range(len(RING_EDGES) - 1):
        lab[(d >= RING_EDGES[i]) & (d < RING_EDGES[i + 1])] = i
    return lab.reshape(-1)


def bc_audit_trainonly(LF_tr, Y_tr, grid, fit_idx, val_idx, ridge: float = 0.0,
                       wrap_ratio_max=None, tol: float = 1.25) -> dict:
    """P1: periodic vs mirror-extended LSI pre-stage, TRAIN SPLIT ONLY.

    `LF_tr` is the CORRECTED upsampled REAL train LF on the HF working grid;
    `Y_tr` the HF train field. `T` is fit on `fit_idx`, the scalar gain on
    `val_idx` (a slice `T` never saw), and both branches are scored on
    `val_idx`. No test array is touched anywhere in this function.
    """
    H, W = int(grid[0]), int(grid[1])
    if H < 2 or W < 2:
        return {"skipped": f"not a 2-D grid ({H}, {W}); the BC audit is 2-D only"}
    if not len(fit_idx) or not len(val_idx):
        return {"skipped": "empty fit or val slice"}
    fit_idx = np.ascontiguousarray(fit_idx)
    val_idx = np.ascontiguousarray(val_idx)
    LF_tr = np.asarray(LF_tr, dtype=np.float64)
    Y_tr = np.asarray(Y_tr, dtype=np.float64)
    R = Y_tr - LF_tr
    n = LF_tr.shape[0]

    verdict = ("non-periodic (degenerate denominator)" if wrap_ratio_max is None
               else ("periodic" if float(wrap_ratio_max) <= float(tol) else "non-periodic"))
    out = {"scored_on": "train val slice (no test array touched)",
           "n_fit": int(len(fit_idx)), "n_val": int(len(val_idx)),
           "ridge": float(ridge), "verdict": verdict,
           "wrap_ratio_hf_max": (None if wrap_ratio_max is None else float(wrap_ratio_max)),
           "tol": float(tol), "branches": {}}

    lab = ring_labels(H, W)
    nb = len(RING_EDGES) - 1
    R_val = R[val_idx]
    den_ring = np.array([float((R_val[:, lab == b] ** 2).mean()) for b in range(nb)])

    for name in ("periodic", "mirror"):
        if name == "periodic":
            T = fit_transfer(LF_tr[fit_idx], R[fit_idx], (H, W), ridge=ridge)
            C = apply_transfer(LF_tr, T, (H, W))
        else:
            He, We = 2 * H, 2 * W
            T = fit_transfer(mirror_ext(LF_tr[fit_idx], H, W),
                             mirror_ext(R[fit_idx], H, W), (He, We), ridge=ridge)
            C = apply_transfer(mirror_ext(LF_tr, H, W), T, (He, We)
                               ).reshape(-1, He, We)[:, :H, :W].reshape(n, -1)
        a, _, _, _ = fit_alpha(R[val_idx], C[val_idx], LF_tr[val_idx], Y_tr[val_idx],
                               include_zero=True)
        res = R[val_idx] - a * C[val_idx]
        prof = [float((res[:, lab == b] ** 2).mean()) for b in range(nb)]
        den = float((R[val_idx] ** 2).sum())
        out["branches"][name] = {
            "alpha": float(a),
            "rel_l2_prestage_val": rel_l2(LF_tr[val_idx] + a * C[val_idx], Y_tr[val_idx]),
            "resid_frac": (float((res ** 2).sum() / den) if den > 0 else None),
            "ring_profile_resid_frac": [(p / d if d > 0 else float("nan"))
                                        for p, d in zip(prof, den_ring)],
        }
    p, m = out["branches"]["periodic"], out["branches"]["mirror"]
    base = p["rel_l2_prestage_val"]
    out["mirror_delta_pct"] = (100.0 * (m["rel_l2_prestage_val"] - base) / base
                               if base > 0 else None)
    out["ring_edges"] = RING_EDGES[:-1] + ["inf"]
    out["ring_npix"] = [int((lab == b).sum()) for b in range(nb)]
    out["reading"] = (
        "mirror_delta_pct < 0 => the periodic pre-stage leaks at the boundary; > 0 => the "
        "periodic BC was correct, do not repair it; ~0 with a large resid_frac under BOTH "
        "extensions => the pre-stage's problem is fit quality, gate it off (alpha -> 0).")
    return out


def cond_lf_identifiability(X: np.ndarray, LF_native: np.ndarray) -> dict:
    """P2: ADR r2-0003's nearest-condition method applied to the LF field.

    Returns the closest-in-standardized-condition train pair, its relative LF
    field difference, and the distribution of the same statistic over every
    sample's nearest neighbour.
    """
    X = np.asarray(X, dtype=np.float64)
    F = np.asarray(LF_native, dtype=np.float64).reshape(X.shape[0], -1)
    n = X.shape[0]
    if n < 2:
        return {"skipped": f"need >= 2 train samples, got {n}"}
    sd = X.std(axis=0)
    Z = (X - X.mean(axis=0)) / np.where(sd > 0, sd, 1.0)
    d2 = ((Z[:, None, :] - Z[None, :, :]) ** 2).sum(axis=2)
    np.fill_diagonal(d2, np.inf)
    dist = np.sqrt(d2)
    nn = dist.argmin(axis=1)
    nn_dist = dist[np.arange(n), nn]
    den = np.maximum(np.linalg.norm(F, axis=1), 1e-12)
    rel = np.linalg.norm(F - F[nn], axis=1) / den
    i = int(np.argmin(nn_dist))
    return {
        "method": ("ADR r2-0003: L2 nearest in per-dim train-standardized condition "
                   "space, applied to the LF field on its native grid"),
        "n_train": int(n), "cond_dim": int(X.shape[1]),
        "closest_pair": {"i": i, "j": int(nn[i]),
                         "standardized_cond_distance": float(nn_dist[i]),
                         "relative_lf_field_difference": float(rel[i])},
        "nn_rel_lf_diff": {"median": float(np.median(rel)), "mean": float(rel.mean()),
                           "p10": float(np.percentile(rel, 10)),
                           "p90": float(np.percentile(rel, 90))},
        "nn_cond_distance": {"min": float(nn_dist.min()),
                             "median": float(np.median(nn_dist))},
        "reading": ("a LARGE relative_lf_field_difference at a SMALL standardized "
                    "condition distance means the LF field is not a function of the "
                    "condition vector: the emulator is bounded by E[LF|c] and arm A5 "
                    "`condmean_lf` should tie arm A2 `frozen` (ADR r2-0003)."),
    }
