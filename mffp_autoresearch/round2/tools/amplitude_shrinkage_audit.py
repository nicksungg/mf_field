#!/usr/bin/env python
"""Is a predictor's excess error UNDER-CONVERGED AMPLITUDE or STRUCTURAL damage?

Provenance: promoted from `s1_poisson-B4` mechanism turn 2
(`worktrees/s1_poisson/B4/scratchpad/reanalysis_turn_2.py`). There it showed that a
3.15x spread in scored nRMSE across six training-schedule arms was a 1.44x spread in
learned structure: the cratered arms had regressed toward the across-sample mean field
(corr(log g_i, log||y_i||) = -0.91, R^2 0.82-0.84), and the shrinkage relaxed
monotonically with training budget. That reading turned an "unexplained collapse" into
"under-convergence of the conditioner's amplitude direction".

WHY IT IS NOT `field_error_decomposition.py`
--------------------------------------------
That tool answers "how much of the squared error is a per-sample gain?" (a magnitude).
This one answers "is that gain error a SHRINKAGE toward the mean?" (a direction), which
is what discriminates an under-trained model from a structurally damaged one:

  * corr(log g_i, log||y_i||) strongly NEGATIVE  -> regression to the mean: the model
    under-predicts big samples and over-predicts small ones. Almost always a budget /
    convergence problem; more steps, a better conditioner, or a per-sample calibration
    will move it.
  * corr ~ 0 with a non-trivial gain spread     -> unstructured calibration noise.
  * corr POSITIVE                               -> amplification / over-fitting of the
    amplitude channel.

Run it on several arms at once (same targets) and it also reports whether the arms share
ONE defect axis (cross-arm correlation of log g_i) or have independent residual noise.

WHAT IT PRINTS, per prediction file
  nRMSE                       the round's metric, via eval/nrmse.py
  g mean / median / std log g per-sample oracle gain g_i = <p_i,y_i>/<y_i,y_i>
  corr / slope / R2           regression of log g_i on centred log||y_i||
  amp_slope                   d log||p_i|| / d log||y_i||  (1.0 = perfect amplitude
                              response; < 1 = shrinkage)
  demeaned_beta               regression of the demeaned prediction on the demeaned
                              target (the same shrinkage seen across the whole set)
  structure_only_nRMSE        nRMSE after each sample's own oracle gain
  verdict                     SHRINKAGE / NEUTRAL / AMPLIFICATION

USAGE
  python tools/amplitude_shrinkage_audit.py \
      --pred_npz <a.npz> [<b.npz> ...] [--labels a b] \
      [--pred_key pred --target_key target] [--shrinkage_corr_threshold 0.5] \
      [--out results.json]

The npz must hold 2-D (N, n_cells) prediction and target arrays -- the layout every
round-1 family's `smoke_eval.py` writes to `preds_test.npz`.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

import numpy as np

EVAL_DIR = pathlib.Path(__file__).resolve().parents[1] / "eval"
sys.path.insert(0, str(EVAL_DIR))
import nrmse as NR  # noqa: E402


def audit_one(pred: np.ndarray, target: np.ndarray, thr: float) -> dict:
    pred = np.asarray(pred, dtype=np.float64)
    target = np.asarray(target, dtype=np.float64)
    yy = (target * target).sum(1)
    ynorm = np.sqrt(yy)
    g = (pred * target).sum(1) / yy
    if (g <= 0).any():
        raise ValueError("non-positive per-sample gain; predictions anti-correlated "
                         "with the target -- this tool assumes a working predictor")
    lg = np.log(g)
    ly = np.log(ynorm)
    lyc = ly - ly.mean()
    corr = float(np.corrcoef(lg, ly)[0, 1])
    slope = float(np.polyfit(lyc, lg - lg.mean(), 1)[0])

    lp = np.log(np.linalg.norm(pred, axis=1))
    amp_slope = float(np.polyfit(lyc, lp - lp.mean(), 1)[0])
    amp_corr = float(np.corrcoef(lyc, lp)[0, 1])

    tc = target - target.mean(0)
    pc = pred - pred.mean(0)
    beta = float((pc * tc).sum() / (tc * tc).sum())

    verdict = ("SHRINKAGE (regression toward the mean field)" if corr <= -thr else
               "AMPLIFICATION" if corr >= thr else
               "NEUTRAL (no amplitude-linked bias)")
    return {
        "n_samples": int(pred.shape[0]),
        "nRMSE": NR.nrmse(pred, target),
        "structure_only_nRMSE": NR.nrmse(pred / g[:, None], target),
        "g_mean": float(g.mean()),
        "g_median": float(np.median(g)),
        "std_log_g": float(lg.std()),
        "corr_logg_logy": corr,
        "slope_logg_logy": slope,
        "r2_logg_logy": corr ** 2,
        "amp_slope": amp_slope,
        "amp_corr": amp_corr,
        "demeaned_beta": beta,
        "verdict": verdict,
        "_log_g": lg.tolist(),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred_npz", nargs="+", required=True)
    ap.add_argument("--labels", nargs="*", default=None)
    ap.add_argument("--pred_key", default="pred")
    ap.add_argument("--target_key", default="target")
    ap.add_argument("--shrinkage_corr_threshold", type=float, default=0.5)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    labels = a.labels or [pathlib.Path(p).parent.name for p in a.pred_npz]
    if len(labels) != len(a.pred_npz):
        raise SystemExit("--labels must match --pred_npz in length")

    res, tgt0, logs = {}, None, {}
    for lab, path in zip(labels, a.pred_npz):
        z = np.load(path)
        p, t = z[a.pred_key], z[a.target_key]
        if tgt0 is None:
            tgt0 = np.asarray(t, dtype=np.float64)
            same = True
        else:
            same = bool(np.array_equal(np.asarray(t, dtype=np.float64), tgt0))
        r = audit_one(p, t, a.shrinkage_corr_threshold)
        logs[lab] = r.pop("_log_g")
        r["targets_match_first_file"] = same
        r["path"] = str(path)
        res[lab] = r

    w = max(len(l) for l in labels) + 1
    print(f"nrmse_def_hash {NR.NRMSE_DEF_HASH}\n")
    print(f"{'arm':<{w}}{'nRMSE':>11s}{'struct-only':>13s}{'std log g':>11s}"
          f"{'corr(lg,ly)':>13s}{'slope':>9s}{'amp_slope':>11s}{'dm_beta':>9s}  verdict")
    for lab in labels:
        r = res[lab]
        print(f"{lab:<{w}}{r['nRMSE']:11.6f}{r['structure_only_nRMSE']:13.6f}"
              f"{r['std_log_g']:11.4f}{r['corr_logg_logy']:13.4f}"
              f"{r['slope_logg_logy']:9.4f}{r['amp_slope']:11.4f}"
              f"{r['demeaned_beta']:9.4f}  {r['verdict']}")

    if len(labels) > 1 and all(res[l]["targets_match_first_file"] for l in labels):
        M = np.corrcoef(np.array([logs[l] for l in labels]))
        cw = max(w, 10)
        print("\ncross-arm correlation of log g_i (do the arms share ONE defect axis?)")
        print(" " * cw + "".join(f"{l:>{cw}}" for l in labels))
        for i, l in enumerate(labels):
            print(f"{l:<{cw}}" + "".join(f"{M[i, j]:{cw}.3f}"
                                         for j in range(len(labels))))
        res["_cross_arm_logg_corr"] = M.tolist()
        raw = np.array([res[l]["nRMSE"] for l in labels])
        st = np.array([res[l]["structure_only_nRMSE"] for l in labels])
        print(f"\nscored nRMSE spread {raw.max()/raw.min():.3f}x   "
              f"structure-only spread {st.max()/st.min():.3f}x")
        res["_spread"] = {"scored": float(raw.max() / raw.min()),
                          "structure_only": float(st.max() / st.min())}
    elif len(labels) > 1:
        print("\n[warn] targets differ across files -- cross-arm block skipped")

    res["_nrmse_def_hash"] = NR.NRMSE_DEF_HASH
    if a.out:
        pathlib.Path(a.out).write_text(json.dumps(res, indent=1))
        print(f"\n[wrote] {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
