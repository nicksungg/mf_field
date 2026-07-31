#!/usr/bin/env python
"""How much of a dataset's HF field is determined by the CONDITION VECTOR at
all — a training-free aleatoric ceiling, in the round's own skill units.

Round 2 asks models to predict HF from a condition vector alone. On several
panel datasets the condition is incomplete (ADR r2-0003: the realized random IC
lives only in the fields), so a deterministic model is bounded from below by an
aleatoric barrier no architecture and no LF training signal can cross. This tool
measures that barrier from the TRAIN split only, with two independent estimators,
and reports whether a given prediction still has headroom.

Estimators (both train-only; no test field enters either)
--------------------------------------------------------
1. `loo_knn`  — for `y = f(c) + e` with aleatoric energy `S`,
   `E‖y_i − m_k(i)‖² = S(1 + 1/k) + B(k)`, `B(k) ≥ 0` the smoothing bias, so
   `Ŝ = min_k R(k)/(1 + 1/k)` is an UPPER BOUND on `S`, tight where the bias is
   negligible. Reported in per-sample rel-L2 (the round's nRMSE form) and in
   skill units.
2. `pair`     — `E‖y_i − y_j‖² = 2S + (structure growing with the condition
   distance d_ij)`; bin all train pairs by `d`, fit the two lowest bins linearly
   and extrapolate to `d = 0`.

READ IT AS
----------
* `certifier_over_knn_bound ≈ 1` → the predictor is AT the barrier: its residual
  error is information the condition does not carry, and no lever (architecture,
  LF-as-training-signal, more epochs) can recover it. A null result there is
  uninformative, not a failure.
* `certifier_over_knn_bound >> 1` → real headroom; the dataset is worth
  attacking.
* `support.verdict == "no_support"` → the nearest train pair in standardized
  condition space is far (`d_min` large) or there are too few train samples;
  BOTH estimators are extrapolations and NO aleatoric claim may be made. On the
  round-2 panel this fires on `sharp__cahn_hilliard` (d_min 2.8222, 19 condition
  dims) and `ifc_poisson` (5 train samples).
* the k-NN bound is an UPPER bound on the aleatoric level, so a predictor
  scoring BELOW it only means the bound is loose there (seen on allen_cahn and
  cahn_hilliard) — it is never evidence of a metric error.

Data: the STRIPPED view (`round2/stripped_data`) by default — this tool needs
only the condition vectors and the HF fields, never LF.

Invocation
----------
    source "$PROJECT_ROOT/.venv/bin/activate"
    python tools/condition_predictability_ceiling.py \
        --datasets PANEL --out /path/to/ceiling.json
    # place a model against the ceiling (optional, one .npy per dataset,
    # shape (n_test, n_cells), the same order the loader returns):
    python tools/condition_predictability_ceiling.py \
        --datasets sharp__fisher_kpp_2d \
        --preds sharp__fisher_kpp_2d=/path/preds_s0.npy \
        --out /path/to/ceiling.json

Provenance: card `experiment_cards/r2s4_diag/batch_1/B1.json` part 6
(findings T2-F1 … T2-F6); source probe
`worktrees/r2s4_diag/B1/scratchpad/reanalysis_turn_2.py`.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
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
import nrmse as NR                                    # noqa: E402
from data_adapters.loaders import load_mf_dataset      # noqa: E402

KS_DEFAULT = "1,2,4,8,16,32,64,128"
PAIR_CHUNK = 256          # rows of (y_i - y_j) held at once; 256x256 grids -> 0.5 GB


def load_split(name: str, data_root: Path):
    train = load_mf_dataset(data_root / name, "train")
    test = load_mf_dataset(data_root / name, "test")
    hf = train["hf_fid"]
    if hf not in test["fids"]:
        hf = test["hf_fid"]
    c_tr = np.asarray(train["cond_by_fid"][hf], dtype=np.float64)
    c_te = np.asarray(test["cond_by_fid"][hf], dtype=np.float64)
    mu, sd = c_tr.mean(0), c_tr.std(0)
    sd = np.where(sd > 0, sd, 1.0)
    Y_tr = np.asarray(train["field_by_fid"][hf], dtype=np.float64).reshape(
        c_tr.shape[0], -1)
    Y_te = np.asarray(test["field_by_fid"][hf], dtype=np.float64).reshape(
        c_te.shape[0], -1)
    return (c_tr - mu) / sd, (c_te - mu) / sd, Y_tr, Y_te


def loo_knn_curve(C, Y, ks):
    """Memory-safe LOO k-NN residual curve on TRAIN (running mean, no (n,k,D))."""
    n = C.shape[0]
    ks = [k for k in ks if k <= n - 1]
    if not ks:
        return {}, None
    kmax = max(ks)
    d2 = ((C[:, None, :] - C[None, :, :]) ** 2).sum(2)
    np.fill_diagonal(d2, np.inf)
    order = np.argsort(d2, axis=1)[:, :kmax]
    ynorm = np.linalg.norm(Y, axis=1)
    E = {k: np.zeros(n) for k in ks}
    for i in range(n):
        acc = np.zeros(Y.shape[1])
        for pos in range(kmax):
            acc += Y[order[i, pos]]
            k = pos + 1
            if k in E:
                r = Y[i] - acc / k
                E[k][i] = float(r @ r)
    out = {}
    for k in ks:
        e = E[k]
        out[k] = {
            "pooled_resid_energy": float(e.sum()),
            "rel_l2_mean": float(np.mean(np.sqrt(e) / ynorm)),
            "rel_l2_mean_debiased": float(
                np.mean(np.sqrt(e / (1.0 + 1.0 / k)) / ynorm)),
        }
    return out, min(out, key=lambda k: out[k]["rel_l2_mean_debiased"])


def pair_extrapolation(C, Y, n_bins=8, max_pairs=200000, rng_seed=0):
    n = C.shape[0]
    iu = np.triu_indices(n, 1)
    rng = np.random.default_rng(rng_seed)
    if iu[0].size > max_pairs:
        sel = rng.choice(iu[0].size, max_pairs, replace=False)
        ii, jj = iu[0][sel], iu[1][sel]
    else:
        ii, jj = iu
    if ii.size == 0:
        return {"bins": [], "d_min": None, "extrap_pair_rel_at_d0": float("nan"),
                "n_pairs_used": 0}
    d = np.linalg.norm(C[ii] - C[jj], axis=1)
    ynorm = np.linalg.norm(Y, axis=1)
    e = np.empty(d.size)
    for s in range(0, d.size, PAIR_CHUNK):
        D = Y[ii[s:s + PAIR_CHUNK]] - Y[jj[s:s + PAIR_CHUNK]]
        e[s:s + PAIR_CHUNK] = (D ** 2).sum(1)
    # ‖y_i-y_j‖ / (sqrt(2)*‖y‖) has the aleatoric per-sample rel-L2 as its d->0
    # limit (mean-of-ratios form, matching the round metric).
    rel = np.sqrt(e) / (np.sqrt(2.0) * 0.5 * (ynorm[ii] + ynorm[jj]))
    qs = np.quantile(d, np.linspace(0, 1, n_bins + 1))
    bins = []
    for b in range(n_bins):
        m = (d >= qs[b]) & ((d <= qs[b + 1]) if b == n_bins - 1 else (d < qs[b + 1]))
        if m.sum() < 5:
            continue
        bins.append({"d_mid": float(d[m].mean()), "n": int(m.sum()),
                     "mean_pair_rel": float(rel[m].mean())})
    if len(bins) >= 2:
        x0, x1 = bins[0]["d_mid"], bins[1]["d_mid"]
        y0, y1 = bins[0]["mean_pair_rel"], bins[1]["mean_pair_rel"]
        r0 = float(y0 - (y1 - y0) / (x1 - x0) * x0)
    else:
        r0 = float("nan")
    return {"bins": bins, "d_min": float(d.min()), "d_median": float(np.median(d)),
            "extrap_pair_rel_at_d0": r0, "n_pairs_used": int(d.size)}


def support_verdict(n_train, pair, cond_dim, lowest_bin_mid):
    reasons = []
    if n_train < 20:
        reasons.append(f"only {n_train} train samples")
    if pair["d_min"] is not None and pair["d_min"] > 1.0:
        reasons.append(f"nearest train pair at d={pair['d_min']:.4f} "
                       f"(standardized, cond_dim={cond_dim})")
    if lowest_bin_mid is not None and lowest_bin_mid > 1.0:
        reasons.append(f"lowest distance bin centred at d={lowest_bin_mid:.3f}")
    return ("no_support" if reasons else "supported"), reasons


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--datasets", required=True,
                    help="comma list, or PANEL / GUARD from project.yaml")
    ap.add_argument("--out", required=True)
    ap.add_argument("--data_root", default=str(PATHS["stripped_data_root"]))
    ap.add_argument("--ks", default=KS_DEFAULT)
    ap.add_argument("--n_bins", type=int, default=8)
    ap.add_argument("--max_pairs", type=int, default=200000)
    ap.add_argument("--preds", default=None,
                    help="comma list of ds=/path/to/preds.npy (n_test, n_cells)")
    args = ap.parse_args()

    if args.datasets.upper() == "PANEL":
        names = list(CFG["panel"])
    elif args.datasets.upper() == "GUARD":
        names = list(CFG["guard_set"])
    else:
        names = [s for s in args.datasets.split(",") if s]
    preds = {}
    if args.preds:
        for item in args.preds.split(","):
            k, v = item.split("=", 1)
            preds[k] = v
    baselines = json.load(open(PATHS["eval_dir"] / "copylf_baselines.json"))
    ks = [int(k) for k in args.ks.split(",")]
    data_root = Path(args.data_root)

    res = {"_tool": "condition_predictability_ceiling",
           "_nrmse_def_hash": NR.NRMSE_DEF_HASH,
           "_copylf_def_hash": baselines["_copylf_def_hash"],
           "_data_root": str(data_root), "_training_free_estimators": True,
           "datasets": {}}
    for name in names:
        C_tr, C_te, Y_tr, Y_te = load_split(name, data_root)
        ref = float(baselines[name]["test_nrmse"])
        curve, k_star = loo_knn_curve(C_tr, Y_tr, ks)
        pair = pair_extrapolation(C_tr, Y_tr, args.n_bins, args.max_pairs)
        lowest = pair["bins"][0]["d_mid"] if pair["bins"] else None
        verdict, reasons = support_verdict(C_tr.shape[0], pair, C_tr.shape[1], lowest)
        knn_rel = curve[k_star]["rel_l2_mean_debiased"] if k_star else None
        pair_rel = pair["extrap_pair_rel_at_d0"]
        d = {
            "n_train": int(C_tr.shape[0]), "n_test": int(C_te.shape[0]),
            "cond_dim": int(C_tr.shape[1]), "copylf_ref_nrmse": ref,
            "reference_type": baselines[name]["reference_type"],
            "loo_knn_curve_train": curve, "k_at_tightest_bound": k_star,
            "aleatoric_rel_l2_upper_bound_knn": knn_rel,
            "aleatoric_skill_ceiling_knn": (knn_rel / ref) if knn_rel else None,
            "pair_extrapolation": pair,
            "aleatoric_skill_ceiling_pair":
                (pair_rel / ref) if np.isfinite(pair_rel) else None,
            "support": {"verdict": verdict, "reasons": reasons},
        }
        if name in preds:
            P = np.load(preds[name]).reshape(Y_te.shape[0], -1).astype(np.float64)
            m = NR.nrmse(P, Y_te)
            d["prediction"] = {
                "path": preds[name], "test_nrmse": m, "test_skill": m / ref,
                "over_knn_bound": (m / knn_rel) if knn_rel else None,
                "over_pair_bound": (m / pair_rel) if np.isfinite(pair_rel) else None,
            }
        res["datasets"][name] = d
        pb = d["aleatoric_skill_ceiling_pair"]
        print(f"[{name}] knn ceiling "
              f"{d['aleatoric_skill_ceiling_knn']:.4f} (k={k_star}) | pair ceiling "
              f"{'n/a' if pb is None else round(pb, 4)} | support={verdict}"
              + (f" | pred skill {d['prediction']['test_skill']:.4f} "
                 f"(x{d['prediction']['over_knn_bound']:.3f} the knn bound)"
                 if name in preds else ""), flush=True)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(res, indent=1))
    print("[wrote]", args.out)


if __name__ == "__main__":
    main()
