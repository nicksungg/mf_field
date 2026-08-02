#!/usr/bin/env python
"""condition_scalar_channel_ladder.py — ROUND-2 probe.

QUESTION
    Is a trained stage's measured gain actually a PER-SAMPLE SCALAR that a
    closed-form regression on the CONDITION VECTOR already delivers?

    Any `condition -> field` arm's prediction splits, per sample, into
      * a LEVEL channel      : the spatial mean  a_i = mean(P_i)
      * a FLUCTUATION channel: the demeaned field  f_i = P_i - a_i, whose
        only per-sample scalar is its GAIN against the truth.
    This probe replaces ONE channel at a time with a condition-only estimate,
    puts the field back together, and RESCORES with the round's own metric, so
    every number is in the card's units (skill = nRMSE / copy-LF reference,
    and multiples of the certified `min_claimable_effect`).

    Estimators, all fitted on the FIT fold with hyper-parameters selected on
    the held-out CALIB fold (never on test):
      S0 identity                (= the arm itself; gain 0 by construction)
      S1 fit-fold constant offset (level) / constant mean (gain)
      S2 ridge, linear in the standardised condition vector
      S3 ridge, quadratic (z, z^2, pairwise cross terms)
      S4 k-NN in the standardised condition space (k selected on calib)
      S5 ridge on the condition PLUS the arm's own scalar
         (the affine-in-condition modulation a FiLM-conditioned head expresses)
      OR ORACLE, the test-truth scalar (a labelled ceiling, uses HF)

READ IT AS
    `S2/S3 gain >> measured trained-stage gain`  -> the trained stage was
        solving a closed-form scalar regression, badly. Report the closed-form
        arm, not the network.
    `S* gains all <= 0 while ORACLE is large`    -> that channel's headroom is
        CONDITION-UNREACHABLE: a genuine information ceiling for a
        condition-only class, not a lazy optimiser.
    `ORACLE small`                               -> the channel does not exist
        on this dataset (check the target's DC energy share first).

RELATION TO EXISTING TOOLS
    `dc_pattern_split.py` splits DC vs pattern descriptively (constant-field
    oracle); `residual_gain_learnability.py` asks whether the GAIN channel
    alone is condition-learnable under the round-1 metric. This probe covers
    BOTH channels, uses the fit/calib protocol of a stacked family, substitutes
    and RE-SCORES in round-2 skill/mce units, and prices the result directly
    against a MEASURED trained-stage increment.

INPUT (one .npz bundle; arrays are (N, n_cells) fields and (N, d) conditions)
    required: pred_train, hf_train, cond_train, pred_test, hf_test, cond_test
    optional: fit_idx, calib_idx  (int index arrays into the TRAIN rows; if
              absent they are drawn from --fold_seed / --fracs)

INVOCATION
    python tools/condition_scalar_channel_ladder.py \
        --bundle /path/to/arm_bundle.npz \
        --copylf_ref 0.0017807662982691156 \
        --mce 0.8797047 \
        --measured_gain 9.2305 \
        --fold_seed 0 --out /path/to/out.json

Provenance: r2s2_stacked-B3 mechanism turn 2
(`worktrees/r2s2_stacked/B3/scratchpad/reanalysis_turn_2.py`).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

TOOLS = Path(__file__).resolve().parent
EVAL_DIR = TOOLS.parent / "eval"
if str(EVAL_DIR) not in sys.path:
    sys.path.insert(0, str(EVAL_DIR))
from nrmse import nrmse  # noqa: E402

LAMBDAS = [1e-6, 1e-4, 1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0]
KNN_KS = [1, 2, 3, 5, 8, 12, 20, 32]


# ------------------------------------------------------------------ regressors
def ridge_fit(Zf, tf, lam):
    """Ridge with an UNPENALISED intercept: centre both, solve, restore."""
    zm, tm = Zf.mean(axis=0), tf.mean()
    Zc = Zf - zm
    w = np.linalg.solve(Zc.T @ Zc + lam * np.eye(Zc.shape[1]), Zc.T @ (tf - tm))
    return {"w": w, "zm": zm, "tm": tm}


def ridge_apply(mdl, Z):
    return (Z - mdl["zm"]) @ mdl["w"] + mdl["tm"]


def ridge_select(Zf, tf, Zc_, tc_):
    best, best_lam, best_mse = None, None, np.inf
    for lam in LAMBDAS:
        try:
            m = ridge_fit(Zf, tf, lam)
        except np.linalg.LinAlgError:
            continue
        mse = float(np.mean((ridge_apply(m, Zc_) - tc_) ** 2))
        if mse < best_mse:
            best, best_lam, best_mse = m, lam, mse
    if best is None:
        raise RuntimeError("every ridge lambda failed to solve")
    return best, best_lam


def knn_predict(Zpool, tpool, Zq, k):
    d = ((Zq[:, None, :] - Zpool[None, :, :]) ** 2).sum(axis=2)
    idx = np.argsort(d, axis=1)[:, :k]
    return tpool[idx].mean(axis=1)


def knn_select(Zf, tf, Zc_, tc_):
    best_k, best_mse = None, np.inf
    for k in KNN_KS:
        if k > Zf.shape[0]:
            continue
        mse = float(np.mean((knn_predict(Zf, tf, Zc_, k) - tc_) ** 2))
        if mse < best_mse:
            best_k, best_mse = k, mse
    return best_k


def quad_features(Z):
    d = Z.shape[1]
    cols = [Z, Z ** 2]
    for i in range(d):
        for j in range(i + 1, d):
            cols.append((Z[:, i] * Z[:, j])[:, None])
    return np.concatenate(cols, axis=1)


def r2(hat, true):
    ss = float(((true - true.mean()) ** 2).sum())
    return float(1.0 - ((np.asarray(hat) - true) ** 2).sum() / max(ss, 1e-300))


def make_folds(n, fold_seed, fracs):
    rng = np.random.default_rng(int(fold_seed))
    perm = rng.permutation(n)
    n_fit = int(round(fracs[0] * n))
    n_cal = int(round(fracs[1] * n))
    if min(n_fit, n_cal, n - n_fit - n_cal) < 1:
        raise SystemExit(f"fold sizes from {fracs} on n={n} contain an empty fold")
    return np.sort(perm[:n_fit]), np.sort(perm[n_fit:n_fit + n_cal])


# -------------------------------------------------------------------- channels
def run_channel(channel, P_tr, Y_tr, P_te, Y_te, Zl_tr, Zl_te, Zq_tr, Zq_te,
                fit, cal, ref, mce, measured):
    a_tr, a_te = P_tr.mean(axis=1), P_te.mean(axis=1)
    m_tr, m_te = Y_tr.mean(axis=1), Y_te.mean(axis=1)
    fa_te = P_te - a_te[:, None]

    if channel == "level":
        t_tr, t_te = m_tr, m_te
        base_tr, base_te = a_tr, a_te

        def rebuild(hat):
            return P_te - a_te[:, None] + hat[:, None]
    else:
        fa_tr = P_tr - a_tr[:, None]
        fy_tr, fy_te = Y_tr - m_tr[:, None], Y_te - m_te[:, None]
        t_tr = (fa_tr * fy_tr).sum(axis=1) / np.maximum((fa_tr ** 2).sum(axis=1), 1e-300)
        t_te = (fa_te * fy_te).sum(axis=1) / np.maximum((fa_te ** 2).sum(axis=1), 1e-300)
        base_tr, base_te = np.ones_like(t_tr), np.ones_like(t_te)

        def rebuild(hat):
            return a_te[:, None] + hat[:, None] * fa_te

    preds, meta = {"S0_identity": base_te}, {}
    if channel == "level":
        preds["S1_const_bias"] = base_te + float(np.mean(t_tr[fit] - base_tr[fit]))
    else:
        preds["S1_const_mean"] = np.full_like(base_te, float(np.mean(t_tr[fit])))
    mdl, lam = ridge_select(Zl_tr[fit], t_tr[fit], Zl_tr[cal], t_tr[cal])
    preds["S2_ridge_cond_lin"] = ridge_apply(mdl, Zl_te)
    meta["S2_lambda"] = lam
    mdl3, lam3 = ridge_select(Zq_tr[fit], t_tr[fit], Zq_tr[cal], t_tr[cal])
    preds["S3_ridge_cond_quad"] = ridge_apply(mdl3, Zq_te)
    meta["S3_lambda"], meta["S3_nfeat"] = lam3, int(Zq_tr.shape[1])
    kk = knn_select(Zl_tr[fit], t_tr[fit], Zl_tr[cal], t_tr[cal])
    preds["S4_knn_cond"] = knn_predict(Zl_tr[fit], t_tr[fit], Zl_te, kk)
    meta["S4_k"] = kk
    Z5t = np.concatenate([Zl_tr, base_tr[:, None]], axis=1)
    Z5e = np.concatenate([Zl_te, base_te[:, None]], axis=1)
    mdl5, lam5 = ridge_select(Z5t[fit], t_tr[fit], Z5t[cal], t_tr[cal])
    preds["S5_ridge_cond_plus_own"] = ridge_apply(mdl5, Z5e)
    meta["S5_lambda"] = lam5
    preds["OR_ORACLE_test_truth"] = t_te

    n_arm = float(nrmse(P_te, Y_te))
    rows = {k: float(nrmse(rebuild(np.asarray(v, dtype=np.float64)), Y_te))
            for k, v in preds.items()}
    orc = (n_arm - rows["OR_ORACLE_test_truth"]) / ref
    return {
        "arm_skill": n_arm / ref,
        "skill": {k: v / ref for k, v in rows.items()},
        "gain_vs_arm_skill_units": {k: (n_arm - v) / ref for k, v in rows.items()},
        "gain_over_mce": {k: (n_arm - v) / ref / mce for k, v in rows.items()},
        "share_of_measured_gain": {
            k: ((n_arm - v) / ref / measured if measured not in (None, 0) else None)
            for k, v in rows.items()},
        "share_of_ORACLE_captured": {
            k: ((n_arm - v) / ref / orc if abs(orc) > 1e-12 else None)
            for k, v in rows.items()},
        "scalar_heldout_R2_on_test": {k: r2(v, t_te) for k, v in preds.items()},
        "scalar_stats": {"target_sd_test": float(t_te.std()),
                         "target_mean_test": float(t_te.mean()),
                         "identity_R2_test": r2(base_te, t_te)},
        "hyperparams": meta,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[2])
    ap.add_argument("--bundle", required=True,
                    help=".npz with pred_train/hf_train/cond_train/"
                         "pred_test/hf_test/cond_test (+ optional fit_idx/calib_idx)")
    ap.add_argument("--copylf_ref", type=float, required=True,
                    help="the dataset's copy-LF (or paper-bar) nRMSE denominator")
    ap.add_argument("--mce", type=float, required=True,
                    help="the dataset's certified min_claimable_effect, in skill units")
    ap.add_argument("--measured_gain", type=float, default=None,
                    help="optional: a measured trained-stage increment to price against")
    ap.add_argument("--fold_seed", type=int, default=0)
    ap.add_argument("--fracs", default="0.70,0.15,0.15")
    ap.add_argument("--channels", default="level,fluct_gain")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    z = np.load(args.bundle)
    need = ["pred_train", "hf_train", "cond_train", "pred_test", "hf_test", "cond_test"]
    missing = [k for k in need if k not in z]
    if missing:
        raise SystemExit(f"bundle is missing required arrays: {missing}")
    P_tr = np.asarray(z["pred_train"], dtype=np.float64).reshape(z["pred_train"].shape[0], -1)
    Y_tr = np.asarray(z["hf_train"], dtype=np.float64).reshape(z["hf_train"].shape[0], -1)
    P_te = np.asarray(z["pred_test"], dtype=np.float64).reshape(z["pred_test"].shape[0], -1)
    Y_te = np.asarray(z["hf_test"], dtype=np.float64).reshape(z["hf_test"].shape[0], -1)
    X_tr = np.asarray(z["cond_train"], dtype=np.float64)
    X_te = np.asarray(z["cond_test"], dtype=np.float64)

    if "fit_idx" in z and "calib_idx" in z:
        fit = np.asarray(z["fit_idx"], dtype=np.int64)
        cal = np.asarray(z["calib_idx"], dtype=np.int64)
        fold_source = "bundle"
    else:
        fracs = [float(x) for x in args.fracs.split(",")]
        fit, cal = make_folds(P_tr.shape[0], args.fold_seed, fracs)
        fold_source = f"derived(fold_seed={args.fold_seed}, fracs={args.fracs})"
    if np.intersect1d(fit, cal).size:
        raise SystemExit("fit and calib folds overlap")

    mu = X_tr.mean(axis=0)
    sd = X_tr.std(axis=0)
    sd = np.where(sd > 0, sd, 1.0)
    Zl_tr, Zl_te = (X_tr - mu) / sd, (X_te - mu) / sd
    Zq_tr, Zq_te = quad_features(Zl_tr), quad_features(Zl_te)

    out = {"_tool": "condition_scalar_channel_ladder.py",
           "_provenance_card": "r2s2_stacked-B3 turn 2",
           "bundle": str(args.bundle), "fold_source": fold_source,
           "copylf_ref_nrmse": args.copylf_ref, "mce": args.mce,
           "measured_gain": args.measured_gain,
           "n_train": int(P_tr.shape[0]), "n_test": int(P_te.shape[0]),
           "n_cells": int(P_te.shape[1]), "cond_dim": int(X_tr.shape[1]),
           "n_fit": int(fit.size), "n_calib": int(cal.size),
           "hf_dc_energy_share": float((Y_te.mean(axis=1) ** 2).sum() * Y_te.shape[1]
                                       / max((Y_te ** 2).sum(), 1e-300)),
           "channels": {}}
    for ch in [c.strip() for c in args.channels.split(",") if c.strip()]:
        if ch not in ("level", "fluct_gain"):
            raise SystemExit(f"unknown channel {ch!r}")
        out["channels"][ch] = run_channel(ch, P_tr, Y_tr, P_te, Y_te,
                                          Zl_tr, Zl_te, Zq_tr, Zq_te,
                                          fit, cal, args.copylf_ref, args.mce,
                                          args.measured_gain)

    # verdicts
    verd = {}
    for ch, rec in out["channels"].items():
        g = {k: v for k, v in rec["gain_vs_arm_skill_units"].items()
             if k not in ("S0_identity", "OR_ORACLE_test_truth")}
        best_k = max(g, key=g.get)
        orc = rec["gain_vs_arm_skill_units"]["OR_ORACLE_test_truth"]
        if orc <= args.mce:
            v = "CHANNEL_ABSENT"
        elif g[best_k] <= 0:
            v = "CONDITION_UNREACHABLE"
        elif args.measured_gain and g[best_k] > args.measured_gain:
            v = "CLOSED_FORM_BEATS_MEASURED_GAIN"
        elif g[best_k] > args.mce:
            v = "CONDITION_REACHABLE"
        else:
            v = "SUB_MCE"
        verd[ch] = {"verdict": v, "best_estimator": best_k,
                    "best_gain_skill_units": g[best_k],
                    "best_gain_over_mce": g[best_k] / args.mce,
                    "oracle_gain_skill_units": orc}
    out["verdicts"] = verd
    Path(args.out).write_text(json.dumps(out, indent=1))
    print(json.dumps(verd, indent=1))
    print("wrote", args.out)


if __name__ == "__main__":
    main()
