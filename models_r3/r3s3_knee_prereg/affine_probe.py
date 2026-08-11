"""HF-design null space + the min-norm affine reference arm.

PROVENANCE. Vendored from this stream's own round-2 family
`models_r2/r2s3_coverage_panel/affine_probe.py` (branch
`round2/exp-r2s3_lf_train_signal-B3`, commit
dfcd46c6b51b5fe0bd533b9c670a7cdbf9d13830). `_design`, `design_null` and
`min_norm_hfonly` are byte-identical to that file; verify with

    git show dfcd46c6:models_r2/r2s3_coverage_panel/affine_probe.py

WHAT THIS CARD (`r3s3_lf_value-B1`) DELETES relative to the base. The base's
`recipe.env.R2S3B3_REF_ARMS` listed `linear_mf`; this card's
`recipe.env.R3S3B3_REF_ARMS` does NOT
(`nn_condition_n5,train_mean_n5,zero,linear_hfonly,affine_on_hf_train,
nn_condition_full,train_mean_full`). No leg can therefore request the
linear/affine MF channel, so the machinery that existed only to serve it is
gone rather than left as unreachable code:

  * `ALPHAS` / `RESID_ALPHAS`, `ridge_fit`, `ridge_apply`, `loo_rel_residual`,
    `select_alpha`, `scale_fit` — the ridge/LOO primitives;
  * `rung_affinity` / `reference_rung` — the per-rung LOO ladder and the frozen
    rung-selection rule for `splits.ref_linear_mf`;
  * `linear_mf_channel` — the `c * A(cond) + R(cond)` channel itself;
  * `oracle_null_block` — the `_ORACLE` recovery-cosine block, whose only input
    was `rung_laws` from `linear_mf_channel`.

Nothing deleted here fed a trained arm, a scored split or a selection in the
base either (they were reported instruments and one cited baseline split), so
the A0/A1 reproduction seam against the certified anchor is unaffected: the
trained path never touched this module beyond `design_null`.

The `linear_mf` estimator remains available to the round as the registered probe
`mffp_autoresearch/round2/tools/affine_ladder_voi.py`, which this card's
pre-flight step runs directly on `sharp__cahn_hilliard` (card part 3, "B4's
named probes") instead of restating it in-family.

Everything below is TRAINING-FREE and runs once per leg in `prepare()` /
`reference_arms()`.
"""
from __future__ import annotations

import numpy as np


def _design(X: np.ndarray) -> np.ndarray:
    X = np.asarray(X, dtype=np.float64)
    return np.concatenate([X, np.ones((X.shape[0], 1))], axis=1)


# ── the HF design's null space ──

def design_null(X_hf: np.ndarray, rank_tol: float) -> dict:
    """SVD of `[X_hf, 1]`; the null directions the N_hf rows cannot resolve.

    Returns the augmented null basis (rows of V^T past the numerical rank) and
    its condition-space part, unit-normalised. REPORTED ONLY in this card, as in
    the base: `m` is the affine coverage deficit the card's part 2 quotes
    (measured 2026-08-07 at N_hf = 5: 14 pfc / 15 ac / 46 fk / 15 ch /
    1 ifc_poisson / 0 ifc_heat), and no arm reads it. A basis vector whose
    condition-space part vanishes is dropped; the count is reported.
    """
    Xd = _design(X_hf)
    U, S, Vt = np.linalg.svd(Xd, full_matrices=True)
    smax = float(S.max()) if S.size else 0.0
    rank = int(np.sum(S > rank_tol * max(smax, 1e-300)))
    null_aug = Vt[rank:]                       # (m, d+1)
    dirs, dropped = [], 0
    for u in null_aug:
        u_c = u[:-1]
        nrm = float(np.linalg.norm(u_c))
        if nrm < 1e-12:
            dropped += 1
            continue
        dirs.append(u_c / nrm)
    V = np.asarray(dirs, dtype=np.float64).reshape(len(dirs), Xd.shape[1] - 1)
    return {
        "design_shape": [int(Xd.shape[0]), int(Xd.shape[1])],
        "singular_values": [float(s) for s in S],
        "rank_tol": float(rank_tol),
        "numerical_rank": rank,
        "m_null_dim": int(null_aug.shape[0]),
        "n_cond_space_directions": int(V.shape[0]),
        "n_dropped_zero_cond_part": int(dropped),
        "null_directions_augmented": null_aug.tolist(),
        "cond_directions": V,                  # (m', d) unit rows, numpy
    }


# ── the non-trained linear reference arms ──

def min_norm_hfonly(X_hf: np.ndarray, Y_hf: np.ndarray, X_te: np.ndarray) -> np.ndarray:
    """`ref_linear_hfonly`: min-norm affine fit on the N_hf rows, via `pinv`.

    With a rank-deficient design this is the row-space projection of the true
    law: the HF-only INFORMATION LIMIT at any capacity
    (`tools/affine_ladder_voi.py` A3 `min_norm_pinv`).
    """
    W = np.linalg.pinv(_design(X_hf)) @ np.asarray(Y_hf, dtype=np.float64)
    return _design(np.asarray(X_te, dtype=np.float64)) @ W


def affine_on_hf_train(X_hf: np.ndarray, Y_hf: np.ndarray, X_te: np.ndarray) -> np.ndarray:
    """`ref_affine_on_hf_train`: the ANCHOR-FILE estimator, via `lstsq`.

    NEW IN THIS CARD. program.md (round 3) §2 "Affine-floor rule" makes this a
    MANDATORY reported arm next to every ifc number:

        ifc_poisson's condition->HF map is EXACTLY affine on the repaired rows
        (oracle-affine residual 5.4e-16), and on ifc_heat a 6-dof affine fit on
        the 5 HF train rows already beats the paper bar (nRMSE 0.0709, skill
        0.96). Every card reporting an ifc number therefore reports the fitted
        `affine_on_hf_train` floor next to it.

    It is a byte-faithful transcription of `affine_fit` in
    `mffp_autoresearch/round3/tools/make_round3_anchors.py` — `np.linalg.lstsq`
    on `[X, 1]` with `rcond=None` (min-norm when underdetermined) — so the
    in-run number is comparable to the frozen anchor value that
    `refs.seam_check_anchor_affine` checks it against.

    Mathematically this is the same map as `min_norm_hfonly`; the two are kept
    as SEPARATE arms because `recipe.env.R3S3B3_REF_ARMS` lists both, and
    because they carry different provenance (`tools/affine_ladder_voi.py` A3
    `pinv` vs the anchor file's `lstsq`). Their agreement is reported as
    `gate_report.affine_estimator_agreement` — a live check that the two
    published definitions of "the affine floor" have not drifted apart.
    """
    D = _design(X_hf)
    W, *_ = np.linalg.lstsq(D, np.asarray(Y_hf, dtype=np.float64), rcond=None)
    return _design(np.asarray(X_te, dtype=np.float64)) @ W
