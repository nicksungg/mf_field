#!/usr/bin/env python
"""condition_identifiable_rank.py -- HOW MANY DEGREES OF FREEDOM OF THE HF FIELD
DOES THE CONDITION VECTOR ACTUALLY DETERMINE?

For a condition->HF task, decompose the train HF fields into POD modes and ask,
out of fold and training-free, how many mode COEFFICIENTS the condition can
predict at all.  Then put that number next to what the same basis could hold if
the coefficients were known (the ORACLE truncation).  The two together separate
the only two failure modes a condition->field model can have:

  * COEFFICIENT-UNIDENTIFIABLE ("information-limited") -- the basis represents
    the held-out fields 1-2 decades below every condition-driven arm, but the
    condition determines only 1-3 coefficients.  More decoder capacity cannot
    help; ADR r2-0003's conditional-mean barrier, measured non-parametrically.
  * BASIS-INADEQUATE ("representation-limited") -- the ORACLE truncation is
    itself near the arm's score.  The fields are genuinely high-rank; a better
    representation is the lever.

WHY THIS EXISTS
---------------
`r2s1_direct-B1` scored a 13.7-15.9 M-parameter FiLM-spectral condition->HF
decoder against a rank-50 POD/ridge control and lost on `sharp__allen_cahn_2d`.
This probe explained why: on every panel dataset the number of POD coefficients
with 5-fold out-of-fold R^2 > 0.1 is 1-5, and past mode 1-2 the out-of-fold R^2
is NEGATIVE (the condition-conditioned regressor is worse than the coefficient's
own mean) -- while on helmholtz/pfc/cahn_hilliard/ifc_poisson a 50-mode train
basis represents the TEST fields to 0.0033-0.0672 nRMSE.  A <=156-parameter
closed-form head then matched the 15.9 M-parameter arm's panel geomean to inside
half a `min_claimable_effect`.  Run this BEFORE designing decoder capacity.

RELATION TO NEIGHBOURING TOOLS
------------------------------
* `condition_predictability_ceiling.py` (r2s4_diag-B1) measures the aleatoric
  ENERGY the condition cannot explain (k-NN / pair-difference estimators).  This
  tool measures the DIMENSION the condition can explain, and adds a scoreable
  closed-form arm at each rank -- the two answer "how much is left?" and "how
  many knobs are there?" and should agree.
* `dc_pattern_split.py` (s5_tuning-B1) has the constant-field ORACLE; this tool
  adds the CONDITION-PREDICTED DC arm (a per-sample constant field from one
  ridge), which is the scoreable version and is frequently the whole answer:
  on `sharp__phase_field_crystal_2d` a 35-parameter DC-only arm scored 0.35020
  against the DC oracle's 0.34907 and the 14.4 M-parameter decoder's 0.38403.
* `band_gain_counterfactual.py` (this card) asks whether a remaining arm-vs-arm
  gap is band calibration.  Natural order: rank -> DC -> band gains.

WHAT IT REPORTS
---------------
  modes.n_r2_gt_0.10 / _0.50    identifiable dimension count (train-side OOF)
  modes.frac_centered_variance_condition_predictable
                                sum_k max(R2_k,0) var_k / sum_k var_k
  modes.implied_floor_nrmse     sqrt(unpredictable variance / total energy) --
                                the floor of ANY `mean_field + f(cond).V` model
  rank_sweep[r].nrmse_arm       SCOREABLE closed-form rank-r arm (train-only fit)
  rank_sweep[r].nrmse_oracle    ORACLE rank-r truncation of the TEST fields
                                (consults test HF; a ceiling, never an arm score)
  dc.*                          DC energy share, DC oracle, OOF R^2 of the
                                per-sample spatial mean, and the DC-only arm
  centering.*                   ||mean field|| vs geometric-mean ||y||, and the
                                two constant predictors -- the additive-field
                                trap under a per-sample RELATIVE metric
  gate.*                        (2-D only) dominant non-DC ring, bimodality of
                                its energy share, and the OOF AUC of predicting
                                "has the pattern nucleated?" from the condition
  verdict                       COEFFICIENT_UNIDENTIFIABLE / BASIS_INADEQUATE /
                                MIXED, given --arm_nrmse.  The rule is
                                `oracle_over_arm = nrmse_oracle(--ref_rank) /
                                --arm_nrmse`: < 0.25 with <= 5 identifiable modes
                                -> unidentifiable; > 0.8 -> basis-inadequate;
                                otherwise MIXED (thresholds calibrated on the
                                r2s1-B1 panel, see the code comment)

READ IT AS
----------
* `n_r2_gt_0.10 <= ~3` with `nrmse_oracle(ref_rank) << arm` -> stop buying
  capacity; the ceiling is the condition vector, not the decoder.
* `implied_floor_nrmse` close to the arm's score -> the arm is already at the
  linear-in-basis conditional mean; the remaining error is not addressable by a
  better fit of the same hypothesis class.
* `centering.ratio_meanfield_over_geoamp >> 1` (r2s1-B1 helmholtz: 4.21) -> a
  fixed ADDITIVE field is a trap: the low-||y|| tail of a per-sample relative
  metric destroys it, and a (unit direction x amplitude) factorization is worth
  a 3.8x improvement with ZERO learned parameters.  `<< 1` (allen_cahn 0.024) ->
  the fields cancel in the mean and factorizing COSTS you.
* `gate.oof_auc ~ 1` with a bimodal ring share -> the dataset is two problems;
  score it per class before believing a pooled number.

HONESTY
-------
Everything except the two lines labelled ORACLE (`rank_sweep[].nrmse_oracle`,
`dc.oracle_nrmse`) is fitted on the TRAIN split only and consults no test
quantity; the rank-r arms and the DC-only arm are legitimately scoreable
predictors.  ORACLE rows consult test HF by construction and may only be quoted
as ceilings.

INVOCATION
----------
    source "$PROJECT_ROOT/.venv/bin/activate"
    python tools/condition_identifiable_rank.py \
        --datasets sharp__phase_field_crystal_2d,sharp__allen_cahn_2d \
        --arm_nrmse sharp__phase_field_crystal_2d=0.38403 \
        --out /path/identrank.json
    # cheaper / deeper variants
    python tools/condition_identifiable_rank.py --datasets ifc_poisson \
        --ranks 1,2,3,4 --max_modes 50 --no_gate --out /path/ip.json

Provenance: card `experiment_cards/r2s1_direct/batch_1/B1.json` part 6
(findings T1-F2/T1-F4/T1-F5, T2-F5, T3-F5/T3-F6/T3-F7); source probes
`worktrees/r2s1_direct/B1/scratchpad/reanalysis_turn_1.py` and
`.../turn3_followup_b.py`.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import yaml


def _resolve_roots():
    here = Path(__file__).resolve()
    project_root = Path(subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True,
        check=True, cwd=here.parent).stdout.strip())
    round_root = here.parents[1]
    cfg = yaml.safe_load(open(round_root / "project.yaml"))
    paths = {k: (Path(v) if os.path.isabs(v) else (project_root / v).resolve())
             for k, v in cfg["paths"].items()}
    return project_root, round_root, cfg, paths


PROJECT_ROOT, ROUND_ROOT, CFG, PATHS = _resolve_roots()
sys.path.insert(0, str(PATHS["eval_dir"]))
sys.path.insert(0, str(PATHS["factory_root"]))
from nrmse import NRMSE_DEF_HASH, nrmse                # noqa: E402
from data_adapters.loaders import load_mf_dataset      # noqa: E402

ALPHAS = np.logspace(-6, 2, 9)


# ── data (stripped view; conditions + HF only, never LF) ────────────


def load_panel(name: str, data_root: Path):
    tr = load_mf_dataset(data_root / name, "train")
    te = load_mf_dataset(data_root / name, "test")
    hf = tr["hf_fid"]
    if hf not in te["fids"]:
        hf = te["hf_fid"]
    if te["lf_fids"]:
        raise RuntimeError(f"LEAKAGE TRIPWIRE: test split exposes LF fids {te['lf_fids']}")
    n_tr = np.asarray(tr["cond_by_fid"][hf]).shape[0]
    n_te = np.asarray(te["cond_by_fid"][hf]).shape[0]
    grid = tr["grid_shape_by_fid"].get(hf)
    return {
        "cond_train": np.asarray(tr["cond_by_fid"][hf], dtype=np.float64),
        "cond_test": np.asarray(te["cond_by_fid"][hf], dtype=np.float64),
        "hf_train": np.asarray(tr["field_by_fid"][hf], dtype=np.float64).reshape(n_tr, -1),
        "hf_test": np.asarray(te["field_by_fid"][hf], dtype=np.float64).reshape(n_te, -1),
        "grid": tuple(int(g) for g in grid) if grid is not None else None,
    }


# ── condition featurisation (bias + standardized cond + random Fourier) ──


def standardizer(c):
    mu, sd = c.mean(0), c.std(0)
    return mu, np.where(sd > 0, sd, 1.0)


def rff_features(cond, mu, sd, B):
    c = (cond - mu) / sd
    if B is None or B.shape[0] == 0:
        return np.concatenate([np.ones((c.shape[0], 1)), c], axis=1)
    proj = 2.0 * np.pi * c @ B.T
    return np.concatenate([np.ones((c.shape[0], 1)), c, np.sin(proj), np.cos(proj)],
                          axis=1)


def ridge(Phi, C, alpha):
    G = Phi.T @ Phi + alpha * np.eye(Phi.shape[1])
    return np.linalg.solve(G, Phi.T @ C)


def cv_alpha(Phi, C, folds):
    if len(folds) < 2:
        return float(ALPHAS[len(ALPHAS) // 2])
    cv = []
    for a in ALPHAS:
        err = 0.0
        for f in folds:
            tr = np.setdiff1d(np.arange(Phi.shape[0]), f)
            if tr.size == 0:
                continue
            err += float(((Phi[f] @ ridge(Phi[tr], C[tr], a) - C[f]) ** 2).sum())
        cv.append(err)
    return float(ALPHAS[int(np.argmin(cv))])


def oof_predict(Phi, C, folds, alpha):
    out = np.zeros_like(C)
    for f in folds:
        tr = np.setdiff1d(np.arange(Phi.shape[0]), f)
        out[f] = Phi[f] @ ridge(Phi[tr], C[tr], alpha)
    return out


def auc(y, s):
    o = np.argsort(s)
    r = np.empty(len(s), float)
    r[o] = np.arange(1, len(s) + 1)
    n1, n0 = y.sum(), (1 - y).sum()
    if n1 == 0 or n0 == 0:
        return None
    return float((r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def dominant_ring(fields, grid):
    """Radial index holding the most non-DC energy, pooled over samples."""
    n = fields.shape[0]
    F = np.fft.fft2(fields.reshape(n, *grid), axes=(1, 2))
    ky = np.fft.fftfreq(grid[0]) * grid[0]
    kx = np.fft.fftfreq(grid[1]) * grid[1]
    KY, KX = np.meshgrid(ky, kx, indexing="ij")
    kint = np.rint(np.sqrt(KY ** 2 + KX ** 2)).astype(int)
    e = (np.abs(F) ** 2).sum(axis=0)
    prof = np.array([e[kint == k].sum() for k in range(1, int(kint.max()) + 1)])
    return int(np.argmax(prof) + 1), kint


def ring_share(fields, grid, kint, k0):
    n = fields.shape[0]
    F = np.fft.fft2(fields.reshape(n, *grid), axes=(1, 2))
    e = np.abs(F) ** 2
    m = (kint >= k0 - 1) & (kint <= k0 + 1)
    return e[:, m].sum(axis=1) / e.sum(axis=(1, 2))


# ── per-dataset probe ───────────────────────────────────────────────


def run_dataset(name, data_root, ranks, max_modes, cond_rff, seed, n_folds,
                gate, arm_nrmse, ref_rank):
    t0 = time.time()
    P = load_panel(name, data_root)
    ctr, ytr, cte, yte = P["cond_train"], P["hf_train"], P["cond_test"], P["hf_test"]
    n, d = ctr.shape
    rng = np.random.default_rng(seed + 9973)
    mu, sd = standardizer(ctr)
    B = rng.standard_normal((cond_rff, d)) if cond_rff > 0 else None
    Phi, Phi_te = rff_features(ctr, mu, sd, B), rff_features(cte, mu, sd, B)
    phi_dim = Phi.shape[1]
    folds = np.array_split(rng.permutation(n), int(min(n_folds, n)))

    mean_field = ytr.mean(axis=0)
    Yc = ytr - mean_field
    S, Vt = np.linalg.svd(Yc, full_matrices=False)[1:]
    max_rank = int(min(n - 1, ytr.shape[1]))
    mode_var = S ** 2
    tot_var = float(mode_var.sum())

    out = {"dataset": name, "n_train": n, "n_test": int(yte.shape[0]),
           "cond_dim": d, "n_cells": int(ytr.shape[1]),
           "grid": list(P["grid"]) if P["grid"] else None,
           "phi_dim": int(phi_dim), "max_rank": max_rank}

    # ── (1) per-mode out-of-fold predictability ──
    K = int(min(max_modes, max_rank))
    Ck = Yc @ Vt[:K].T
    ak = cv_alpha(Phi, Ck, folds)
    sse = ((oof_predict(Phi, Ck, folds, ak) - Ck) ** 2).sum(axis=0)
    sst = ((Ck - Ck.mean(axis=0)) ** 2).sum(axis=0)
    r2 = 1.0 - sse / np.maximum(sst, 1e-300)
    r2c = np.clip(r2, 0.0, 1.0)
    pred_var = float((r2c * mode_var[:K]).sum())
    total_energy = float((ytr ** 2).sum())
    out["modes"] = {
        "n_modes_scanned": K, "ridge_alpha": ak,
        "mode_r2_oof": r2.tolist(),
        "mode_var_share": (mode_var[:K] / max(tot_var, 1e-300)).tolist(),
        "n_r2_gt_0.10": int((r2 > 0.10).sum()),
        "n_r2_gt_0.50": int((r2 > 0.50).sum()),
        "last_mode_r2_gt_0.10": (int(np.where(r2 > 0.10)[0][-1] + 1)
                                 if (r2 > 0.10).any() else 0),
        "frac_centered_variance_condition_predictable":
            pred_var / max(tot_var, 1e-300),
        "implied_floor_nrmse": float(np.sqrt(max(tot_var - pred_var, 0.0)
                                             / max(total_energy, 1e-300))),
    }

    # ── (2) rank sweep: scoreable closed-form arm vs ORACLE truncation ──
    sweep = {}
    for r in sorted({int(min(r, max_rank)) for r in ranks if r >= 1}):
        V = Vt[:r]
        C = Yc @ V.T
        a = cv_alpha(Phi, C, folds)
        arm = mean_field + (Phi_te @ ridge(Phi, C, a)) @ V
        orc = mean_field + ((yte - mean_field) @ V.T) @ V     # ORACLE (uses test HF)
        sweep[str(r)] = {"nrmse_arm": nrmse(arm, yte), "nrmse_oracle_ORACLE": nrmse(orc, yte),
                         "ridge_alpha": a, "n_params_arm": int(phi_dim * r)}
    out["rank_sweep"] = sweep

    # ── (3) DC anatomy ──
    m_te = yte.mean(axis=1, keepdims=True)
    dc_oracle = np.broadcast_to(m_te, yte.shape).copy()
    dc_tr = ytr.mean(axis=1, keepdims=True)
    a_dc = cv_alpha(Phi, dc_tr, folds)
    oof_dc = oof_predict(Phi, dc_tr, folds, a_dc)
    dc_pred_te = Phi_te @ ridge(Phi, dc_tr, a_dc)
    out["dc"] = {
        "hf_dc_energy_share_test_mean": float(np.mean(
            (m_te[:, 0] ** 2) * yte.shape[1] / (yte ** 2).sum(axis=1))),
        "oracle_nrmse_ORACLE": nrmse(dc_oracle, yte),
        "oof_r2_spatial_mean": float(1 - ((oof_dc - dc_tr) ** 2).sum()
                                     / max(float(((dc_tr - dc_tr.mean()) ** 2).sum()), 1e-300)),
        "dc_only_arm_nrmse": nrmse(np.broadcast_to(dc_pred_te, yte.shape).copy(), yte),
        "dc_only_arm_n_params": int(phi_dim),
    }

    # ── (4) centering diagnostic (the additive-field trap) ──
    nrm = np.linalg.norm(ytr, axis=1)
    geo_amp = float(np.exp(np.mean(np.log(nrm))))
    u_mean = (ytr / nrm[:, None]).mean(axis=0)
    u_mean = u_mean / max(float(np.linalg.norm(u_mean)), 1e-300)
    out["centering"] = {
        "norm_mean_field": float(np.linalg.norm(mean_field)),
        "geometric_mean_norm": geo_amp,
        "ratio_meanfield_over_geoamp": float(np.linalg.norm(mean_field)) / max(geo_amp, 1e-300),
        "nrmse_mean_field_const": nrmse(
            np.broadcast_to(mean_field, yte.shape).copy(), yte),
        "nrmse_unitdir_x_geoamp_const": nrmse(
            np.broadcast_to(u_mean * geo_amp, yte.shape).copy(), yte),
        "test_norm_spread_max_over_min": float(np.linalg.norm(yte, axis=1).max()
                                               / max(float(np.linalg.norm(yte, axis=1).min()), 1e-300)),
    }

    # ── (5) pattern gate (2-D only) ──
    if gate and P["grid"] is not None and len(P["grid"]) == 2:
        k0, kint = dominant_ring(ytr, P["grid"])
        rs_tr = ring_share(ytr, P["grid"], kint, k0)
        rs_te = ring_share(yte, P["grid"], kint, k0)
        lab = (rs_tr > 0.1).astype(float)
        g = {"dominant_ring_k": k0,
             "train_ring_share_quantiles": {q: float(np.quantile(rs_tr, float(q)))
                                            for q in ("0.05", "0.25", "0.5", "0.75", "0.95")},
             "train_frac_above_0.1": float(lab.mean()),
             "test_frac_above_0.1": float((rs_te > 0.1).mean()),
             "corr_ring_share_vs_cond": [float(np.corrcoef(rs_tr, ctr[:, j])[0, 1])
                                         if ctr[:, j].std() > 0 else None for j in range(d)]}
        if 0 < lab.mean() < 1:
            s_rff = oof_predict(Phi, lab[:, None], folds, 1e-3)[:, 0]
            Plin = rff_features(ctr, mu, sd, None)
            s_lin = oof_predict(Plin, lab[:, None], folds, 1e-8)[:, 0]
            g["oof_auc_rff"] = auc(lab, s_rff)
            g["oof_auc_linear_cond"] = auc(lab, s_lin)
            g["class_nrmse_dc_only_ORACLEsplit"] = {
                cls: {"n": int(m.sum()),
                      "dc_only_arm": nrmse(np.broadcast_to(dc_pred_te, yte.shape)[m].copy(),
                                           yte[m]),
                      "dc_oracle_ORACLE": nrmse(dc_oracle[m], yte[m])}
                for cls, m in (("patterned", rs_te > 0.1), ("unpatterned", rs_te <= 0.1))
                if m.sum() > 0}
        out["gate"] = g

    # ── (6) verdict ──
    rr = str(int(min(ref_rank, max_rank)))
    orc_ref = sweep.get(rr, {}).get("nrmse_oracle_ORACLE")
    v = {"ref_rank": int(rr), "oracle_at_ref_rank": orc_ref,
         "arm_nrmse": arm_nrmse, "identifiable_rank": out["modes"]["n_r2_gt_0.10"]}
    if arm_nrmse and orc_ref:
        ratio = orc_ref / arm_nrmse
        v["oracle_over_arm"] = ratio
        # thresholds calibrated on the r2s1-B1 panel (card part 6, T1-F4):
        #   helmholtz 0.004 / pfc 0.074 / cahn_hilliard 0.125 / ifc_poisson 0.19
        #   -> regime A (coefficient-unidentifiable); fisher_kpp 0.99 -> regime B
        #   (basis-inadequate); allen_cahn 0.47 -> genuinely both.
        v["label"] = ("COEFFICIENT_UNIDENTIFIABLE" if ratio < 0.25 and
                      out["modes"]["n_r2_gt_0.10"] <= 5 else
                      "BASIS_INADEQUATE" if ratio > 0.8 else "MIXED")
    else:
        v["label"] = "no_arm_nrmse_given"
    out["verdict"] = v
    out["seconds"] = time.time() - t0
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--datasets", required=True, help="comma-separated dataset names")
    ap.add_argument("--out", required=True)
    ap.add_argument("--data_root", default=str(PATHS["stripped_data_root"]))
    ap.add_argument("--ranks", default="1,2,3,4,8,16,32,50")
    ap.add_argument("--ref_rank", type=int, default=50,
                    help="rank whose ORACLE truncation drives the verdict")
    ap.add_argument("--max_modes", type=int, default=200,
                    help="how many POD modes get an out-of-fold R^2")
    ap.add_argument("--cond_rff", type=int, default=16,
                    help="random Fourier features (0 = linear-in-condition only)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--no_gate", action="store_true", help="skip the pattern gate")
    ap.add_argument("--arm_nrmse", default="",
                    help="comma list `dataset=nrmse` to place an arm against the ceiling")
    args = ap.parse_args()

    arms = {}
    for kv in [x for x in args.arm_nrmse.split(",") if x.strip()]:
        k, _, v = kv.partition("=")
        arms[k.strip()] = float(v)
    ranks = [int(x) for x in args.ranks.split(",") if x.strip()]

    res = {}
    for nm in [x for x in args.datasets.split(",") if x.strip()]:
        r = run_dataset(nm, Path(args.data_root), ranks, args.max_modes,
                        args.cond_rff, args.seed, args.folds, not args.no_gate,
                        arms.get(nm), args.ref_rank)
        res[nm] = r
        print(f"[{nm}] identifiable_rank(R2>0.1)={r['modes']['n_r2_gt_0.10']} "
              f"pred_var={r['modes']['frac_centered_variance_condition_predictable']:.4f} "
              f"floor={r['modes']['implied_floor_nrmse']:.4f} "
              f"dc_share={r['dc']['hf_dc_energy_share_test_mean']:.4f} "
              f"dc_oofR2={r['dc']['oof_r2_spatial_mean']:.5f} "
              f"dc_arm={r['dc']['dc_only_arm_nrmse']:.5f} "
              f"verdict={r['verdict']['label']} ({r['seconds']:.1f}s)", flush=True)

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    json.dump({"_tool": "condition_identifiable_rank",
               "_nrmse_def_hash": NRMSE_DEF_HASH,
               "_note": "keys ending in ORACLE consult test HF and are ceilings, "
                        "never scoreable arm values",
               "results": res}, open(args.out, "w"), indent=1)
    print("wrote", args.out)


if __name__ == "__main__":
    main()
