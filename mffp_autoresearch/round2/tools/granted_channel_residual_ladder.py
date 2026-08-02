#!/usr/bin/env python
"""granted_channel_residual_ladder.py — ROUND-2 probe.

QUESTION
    GRANT an arm the best closed-form per-sample scalar channel it can have.
    Is there a SECOND channel left, or is the rest field-structured and out of
    reach for a condition-only class?

    Step 1  B := arm with its per-sample spatial mean replaced by a condition
            regression fitted on the FIT fold (lambda on CALIB). This is the
            channel `condition_scalar_channel_ladder.py` prices; here it is
            simply granted for free.
    Step 2  E := HF - B. A POD basis {phi_r} of E is built on the FIT ROWS
            ONLY (thin SVD), so the dictionary is train-side and legal.
    Step 3  Two nested ladders on the test split, per rank R:
              PRED_R   = B + sum_{r<=R} chat_r phi_r   (chat_r a fit-fold
                         condition regression, lambda on calib)
              ORACLE_R = B + sum_{r<=R} ctrue_r phi_r  (test-truth coefficients)
            ORACLE says the KNOB EXISTS in a train-side field basis; PRED says
            the CONDITION VECTOR CAN TURN IT.

    Optional blocks:
      --grid H W        radial band anatomy of E vs the arm's error vs HF
                        (edges 0/.125/.25/.5/1 x k_max), which says whether
                        what remains is still the band the arm operates in.
      lf_train in the   LF-POOL OBTAINABILITY, measured on the HELD-OUT TRAIN
      bundle            rows only (never on test LF — round-2 immutable 9
                        forbids reading the unstripped test view): is the
                        granted channel, and the unreachable fluctuation,
                        available from the sample's own PAIRED LF field?

READ IT AS
    ORACLE large + PRED flat/negative + every mode held-out R^2 <= 0
        -> CONDITION_UNREACHABLE: an information ceiling, not a capacity gap.
        Check the LF block: if the paired LF carries it, the ceiling is the
        REGIME (no LF at test), not the architecture.
    ORACLE large + compact modal spectrum + PRED positive
        -> a real second channel; a coefficient head is worth building.
    Modal spectrum near-white AND fit-basis captures little test-residual
    energy -> there is no compact dictionary to address at all; do not
        propose a low-rank head.

RELATION TO EXISTING TOOLS
    `condition_identifiable_rank.py` measures per-POD-mode condition R^2 of the
    HF FIELD in absolute terms. This probe is the SEQUENTIAL form: it runs on
    the residual left AFTER a granted scalar law on a specific arm, so it
    answers "is there a SECOND channel" rather than "is there a channel", and
    it adds the train-rows-only LF-obtainability block.

INPUT (one .npz bundle)
    required: pred_train, hf_train, cond_train, pred_test, hf_test, cond_test
    optional: fit_idx, calib_idx, eval_idx  (int index arrays into TRAIN rows)
    optional: lf_train  (paired LF fields on the TRAIN rows, on the HF grid)

INVOCATION
    python tools/granted_channel_residual_ladder.py \
        --bundle /path/to/arm_bundle.npz \
        --copylf_ref 0.0017807662982691156 --mce 0.8797047 \
        --ranks 1,2,4,8,16,32,64 --grid 256 256 \
        --fold_seed 0 --out /path/to/out.json

Provenance: r2s2_stacked-B3 mechanism turn 3
(`worktrees/r2s2_stacked/B3/scratchpad/reanalysis_turn_3_v2.py`).
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


def ridge_fit(Zf, tf, lam):
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
    n_fit, n_cal = int(round(fracs[0] * n)), int(round(fracs[1] * n))
    if min(n_fit, n_cal, n - n_fit - n_cal) < 1:
        raise SystemExit(f"fold sizes from {fracs} on n={n} contain an empty fold")
    return (np.sort(perm[:n_fit]), np.sort(perm[n_fit:n_fit + n_cal]),
            np.sort(perm[n_fit + n_cal:]))


def band_energy(F, grid, n_bands=4):
    """Per-band energy on the DYADIC radial grid, Parseval-weighted rFFT.

    Same convention as the round's `s2_copylf_forensics` banding (edges
    k_nyq / 2^(n_bands-1-b), outermost band open-ended), so the shares are
    directly comparable with every other round-2 band probe.
    """
    H, W = int(grid[0]), int(grid[1])
    kx = np.fft.fftfreq(H) * H
    ky = np.arange(W // 2 + 1, dtype=np.float64)
    kr = np.sqrt(kx[:, None] ** 2 + ky[None, :] ** 2)
    weight = np.full((H, W // 2 + 1), 2.0)
    weight[:, 0] = 1.0
    if W % 2 == 0:
        weight[:, -1] = 1.0
    k_ny = min(H, W) / 2.0
    edges = [0.0] + [k_ny / 2.0 ** (n_bands - 1 - b) for b in range(n_bands)]
    masks = [(kr >= edges[b]) if b == n_bands - 1
             else ((kr >= edges[b]) & (kr < edges[b + 1])) for b in range(n_bands)]
    f = np.fft.rfft2(np.asarray(F, dtype=np.float64).reshape(-1, H, W))
    acc = (np.abs(f) ** 2 * weight).sum(axis=0)
    return [float(np.real(acc[m]).sum()) for m in masks]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[2])
    ap.add_argument("--bundle", required=True)
    ap.add_argument("--copylf_ref", type=float, required=True)
    ap.add_argument("--mce", type=float, required=True)
    ap.add_argument("--ranks", default="1,2,4,8,16,32,64")
    ap.add_argument("--grid", nargs=2, type=int, default=None,
                    metavar=("H", "W"), help="enable the band-anatomy block")
    ap.add_argument("--fold_seed", type=int, default=0)
    ap.add_argument("--fracs", default="0.70,0.15,0.15")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    z = np.load(args.bundle)
    need = ["pred_train", "hf_train", "cond_train", "pred_test", "hf_test", "cond_test"]
    missing = [k for k in need if k not in z]
    if missing:
        raise SystemExit(f"bundle is missing required arrays: {missing}")

    def flat(k):
        a = np.asarray(z[k], dtype=np.float64)
        return a.reshape(a.shape[0], -1)
    P_tr, Y_tr, P_te, Y_te = flat("pred_train"), flat("hf_train"), flat("pred_test"), flat("hf_test")
    X_tr = np.asarray(z["cond_train"], dtype=np.float64)
    X_te = np.asarray(z["cond_test"], dtype=np.float64)

    if all(k in z for k in ("fit_idx", "calib_idx")):
        fit = np.asarray(z["fit_idx"], dtype=np.int64)
        cal = np.asarray(z["calib_idx"], dtype=np.int64)
        lev = (np.asarray(z["eval_idx"], dtype=np.int64) if "eval_idx" in z
               else np.setdiff1d(np.arange(P_tr.shape[0]), np.union1d(fit, cal)))
        fold_source = "bundle"
    else:
        fracs = [float(x) for x in args.fracs.split(",")]
        fit, cal, lev = make_folds(P_tr.shape[0], args.fold_seed, fracs)
        fold_source = f"derived(fold_seed={args.fold_seed}, fracs={args.fracs})"

    ref, mce = args.copylf_ref, args.mce
    mu = X_tr.mean(axis=0)
    sd = X_tr.std(axis=0)
    sd = np.where(sd > 0, sd, 1.0)
    Zq_tr, Zq_te = quad_features((X_tr - mu) / sd), quad_features((X_te - mu) / sd)

    # ---- step 1: grant the condition level law ----
    m_tr, m_te = Y_tr.mean(axis=1), Y_te.mean(axis=1)
    a_tr, a_te = P_tr.mean(axis=1), P_te.mean(axis=1)
    mdl, lam = ridge_select(Zq_tr[fit], m_tr[fit], Zq_tr[cal], m_tr[cal])
    mhat_tr, mhat_te = ridge_apply(mdl, Zq_tr), ridge_apply(mdl, Zq_te)
    B_tr = P_tr - a_tr[:, None] + mhat_tr[:, None]
    B_te = P_te - a_te[:, None] + mhat_te[:, None]
    n_arm, n_B = float(nrmse(P_te, Y_te)), float(nrmse(B_te, Y_te))

    out = {"_tool": "granted_channel_residual_ladder.py",
           "_provenance_card": "r2s2_stacked-B3 turn 3",
           "_no_test_lf_read": True,
           "bundle": str(args.bundle), "fold_source": fold_source,
           "copylf_ref_nrmse": ref, "mce": mce,
           "n_train": int(P_tr.shape[0]), "n_test": int(P_te.shape[0]),
           "n_cells": int(P_te.shape[1]), "cond_dim": int(X_tr.shape[1]),
           "n_fit": int(fit.size), "n_calib": int(cal.size), "n_eval": int(lev.size),
           "granted_level_law": {
               "arm_skill": n_arm / ref, "B_skill": n_B / ref,
               "gain_skill_units": (n_arm - n_B) / ref,
               "gain_over_mce": (n_arm - n_B) / ref / mce,
               "heldout_R2_on_test": r2(mhat_te, m_te), "lambda": lam}}

    # ---- step 2: POD of the granted residual on FIT ROWS ONLY ----
    ranks = [int(x) for x in args.ranks.split(",")]
    E_tr, E_te = Y_tr - B_tr, Y_te - B_te
    U, sv, Vt = np.linalg.svd(E_tr[fit], full_matrices=False)
    max_rank = int(min(max(ranks), Vt.shape[0]))
    Phi = Vt[:max_rank]
    tot = float((sv ** 2).sum())
    C_tr, C_te = E_tr @ Phi.T, E_te @ Phi.T
    C_hat = np.zeros_like(C_te)
    mode_r2 = []
    for r in range(max_rank):
        m_, _ = ridge_select(Zq_tr[fit], C_tr[fit, r], Zq_tr[cal], C_tr[cal, r])
        C_hat[:, r] = ridge_apply(m_, Zq_te)
        mode_r2.append(r2(C_hat[:, r], C_te[:, r]))
    e_tot = float((E_te ** 2).sum())

    ladder = {}
    for R in ranks:
        if R > max_rank:
            continue
        np_ = float(nrmse(B_te + C_hat[:, :R] @ Phi[:R], Y_te))
        no_ = float(nrmse(B_te + C_te[:, :R] @ Phi[:R], Y_te))
        ladder[str(R)] = {
            "pred_skill": np_ / ref, "oracle_skill": no_ / ref,
            "pred_gain_vs_B_skill_units": (n_B - np_) / ref,
            "oracle_gain_vs_B_skill_units": (n_B - no_) / ref,
            "pred_gain_vs_B_over_mce": (n_B - np_) / ref / mce,
            "oracle_gain_vs_B_over_mce": (n_B - no_) / ref / mce,
            "pred_share_of_oracle": (n_B - np_) / max(n_B - no_, 1e-300),
            "test_residual_energy_captured_by_fitbasis":
                float((C_te[:, :R] ** 2).sum() / max(e_tot, 1e-300))}
    out["rank_ladder"] = ladder
    out["mode_heldout_R2"] = mode_r2            # ALL modes up to max_rank
    out["n_modes_with_positive_heldout_R2"] = int(sum(x > 0 for x in mode_r2))
    out["mode_fit_energy_share"] = (sv[:max_rank] ** 2 / max(tot, 1e-300)).tolist()
    out["max_rank"] = max_rank

    # ---- optional band anatomy ----
    if args.grid is not None:
        H, W = args.grid
        if H * W != P_te.shape[1]:
            raise SystemExit(f"--grid {H}x{W} != n_cells {P_te.shape[1]}")
        eY = np.array(band_energy(Y_te, (H, W)))
        eE = np.array(band_energy(E_te, (H, W)))
        eA = np.array(band_energy(Y_te - P_te, (H, W)))
        out["bands"] = {
            "edges_frac": [0, 0.125, 0.25, 0.5, 1.0],
            "hf_energy_share": (eY / eY.sum()).tolist(),
            "arm_error_energy_share": (eA / eA.sum()).tolist(),
            "granted_residual_energy_share": (eE / eE.sum()).tolist(),
            "arm_band_relative_error": np.sqrt(eA / np.maximum(eY, 1e-300)).tolist(),
            "B_band_relative_error": np.sqrt(eE / np.maximum(eY, 1e-300)).tolist()}

    # ---- optional LF-pool obtainability, TRAIN ROWS ONLY ----
    if "lf_train" in z:
        LF = np.asarray(z["lf_train"], dtype=np.float64)
        LF = LF.reshape(LF.shape[0], -1)
        if LF.shape != Y_tr.shape:
            raise SystemExit(f"lf_train {LF.shape} must match hf_train {Y_tr.shape} "
                             "(upsample the LF onto the HF grid first)")
        dc = LF.mean(axis=1)
        mdl_lf, _ = ridge_select(dc[fit][:, None], m_tr[fit], dc[cal][:, None], m_tr[cal])
        mhat_lf = ridge_apply(mdl_lf, dc[:, None])

        def cos_stats(F):
            fp = F[lev] - F[lev].mean(axis=1, keepdims=True)
            fy = Y_tr[lev] - m_tr[lev][:, None]
            c = (fp * fy).sum(axis=1) / np.maximum(
                np.sqrt((fp ** 2).sum(axis=1) * (fy ** 2).sum(axis=1)), 1e-300)
            return float(np.median(c)), float(np.mean(c))
        f_lf = LF - dc[:, None]
        gamma = float((f_lf[fit] * (Y_tr - m_tr[:, None])[fit]).sum()
                      / max((f_lf[fit] ** 2).sum(), 1e-300))
        n_cf = float(nrmse((mhat_tr[:, None] + gamma * f_lf)[lev], Y_tr[lev]))
        n_a = float(nrmse(P_tr[lev], Y_tr[lev]))
        n_lf = float(nrmse(LF[lev], Y_tr[lev]))
        cl_med, cl_mean = cos_stats(LF)
        ca_med, ca_mean = cos_stats(P_tr)
        out["lf_obtainability_trainrows"] = {
            "_scope": "held-out TRAIN rows only; no test LF is read (round-2 "
                      "immutable 9). Absolute skills use the TEST-split copy-LF "
                      "denominator, so only the ratio fields are denominator-free.",
            "n_eval_rows": int(lev.size),
            "level_from_own_LF_DC_heldout_R2": r2(mhat_lf[lev], m_tr[lev]),
            "level_from_condition_heldout_R2": r2(mhat_tr[lev], m_tr[lev]),
            "median_cos_fluct_LF_vs_HF": cl_med, "mean_cos_fluct_LF_vs_HF": cl_mean,
            "median_cos_fluct_arm_vs_HF": ca_med, "mean_cos_fluct_arm_vs_HF": ca_mean,
            "counterfactual_LF_arm_skillunits": n_cf / ref,
            "arm_skillunits_same_rows": n_a / ref,
            "raw_LF_skillunits_same_rows": n_lf / ref,
            "ratio_arm_over_LF_arm": n_a / max(n_cf, 1e-300),
            "ratio_arm_over_raw_LF": n_a / max(n_lf, 1e-300),
            "gamma_global": gamma}

    # ---- verdict ----
    top = str(max(int(k) for k in ladder)) if ladder else None
    best_pred = max(v["pred_gain_vs_B_skill_units"] for v in ladder.values()) if ladder else 0.0
    orc_top = ladder[top]["oracle_gain_vs_B_skill_units"] if top else 0.0
    cap_top = ladder[top]["test_residual_energy_captured_by_fitbasis"] if top else 0.0
    if orc_top <= mce:
        verdict = "NO_SECOND_CHANNEL"
    elif best_pred <= 0:
        verdict = ("CONDITION_UNREACHABLE_NO_DICTIONARY" if cap_top < 0.5
                   else "CONDITION_UNREACHABLE_DICTIONARY_EXISTS")
    elif best_pred > mce:
        verdict = "SECOND_CHANNEL_REACHABLE"
    else:
        verdict = "SUB_MCE"
    out["verdict"] = {
        "verdict": verdict, "best_pred_gain_skill_units": best_pred,
        "best_pred_gain_over_mce": best_pred / mce,
        "oracle_gain_at_top_rank_over_mce": orc_top / mce,
        "max_mode_heldout_R2": float(max(mode_r2)) if mode_r2 else None,
        "test_residual_energy_captured_at_top_rank": cap_top}
    Path(args.out).write_text(json.dumps(out, indent=1))
    print(json.dumps(out["verdict"], indent=1))
    print("wrote", args.out)


if __name__ == "__main__":
    main()
