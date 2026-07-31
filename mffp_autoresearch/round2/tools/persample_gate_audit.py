#!/usr/bin/env python
"""Audit a PER-SAMPLE gate / blend: what it recovers, what it costs, and where it will fail.

Provenance: promoted from `s6_local-B2` mechanism analysis turn 3
(`worktrees/s6_local/B2/scratchpad/reanalysis_turn_3.py` + the register-turn
sensitivity check `turn3_sensitivity_check.json`). There it explained C3's score
reversal: the out-of-fold per-sample trust head reproduced its regression target at
Pearson **0.9983** on `sharp__phase_field_crystal_2d` and still scored **+21.5 %** worse
than a single global scalar, because the fit was UNWEIGHTED while the scored metric
weights a per-sample alpha error by `(||C_i||/||Y_i||)^2`, a quantity spanning **189x**
inside that one dataset.

Any card that blends two predictions per sample — a trust gate, a router, a
copy-LF-vs-model switch, a stacking weight — is making the same bet and can be audited
the same way, from shipped predictions only.

MODEL AUDITED
    pred_i = base_i + alpha_i * C_i ,      C_i = model_i - base_i
`alpha_i` is RECOVERED from the shipped gated prediction (least-squares projection per
sample), so the tool needs no access to the gate's internals.

WHAT IT REPORTS
  alpha_implied         the per-sample blend weight actually realised
  alpha_star            the per-sample optimum <R_i,C_i>/||C_i||^2, R = target - base
                        (this minimises BOTH squared and relative L2 per sample, since
                        ||Y_i|| is constant in alpha — the two do NOT differ here)
  recovery              Pearson / Spearman of alpha_implied against alpha_star
  scores                round nRMSE (eval/nrmse.py) of base, model (alpha=1), the shipped
                        gated prediction, the best global scalar, and the per-sample
                        ORACLE. `oracle_gain_vs_global` is the headroom the gate is
                        chasing; `gate_gain_vs_global` is what it delivered
  sensitivity           w_i = ||C_i||/||Y_i||, the metric's sensitivity to an alpha
                        error: p50 / p90 / max / max_over_p50, plus
                        Spearman(excess relative error, w) and the top samples' share of
                        the mean excess. A large `max_over_p50` with a positive Spearman
                        means the gate is being scored on a handful of samples and its
                        fit must be weighted by w^2
  no_harm               fraction of samples ending WORSE than `base` under the gate, at
                        alpha = 1, and at the best global scalar, with the worst ratio.
                        An "exact no-harm fallback at alpha = 0" is a CONSTRUCTION claim;
                        this is the per-sample reality

READ IT AS
  `recovery` high + `gate_gain` worse than `oracle_gain` + `sensitivity.max_over_p50`
  large  ->  the gate estimates alpha well and is being punished on a few
  high-sensitivity samples: weight the gate's fit by w^2 before touching anything else.
  `oracle_gain_vs_global` inside the dataset's certified floor  ->  there is no
  per-sample headroom to win; a global scalar is the honest choice.
  `no_harm.frac_worse_than_base_gate` >> `..._global`  ->  the gate traded the exact
  no-harm floor for headroom (say so explicitly; it is a real cost).

USAGE
  python tools/persample_gate_audit.py \
      --base_npz <copylf_or_base.npz> --model_npz <ungated_model.npz> \
      [--gated_npz <shipped_gated.npz>] \
      [--pred_key pred --target_key target] [--out audit.json]

Every npz needs a prediction array; the target is read from `--base_npz` (and checked
against the others). Arrays may be (N, H*W) or (N, H, W).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np


def _repo_root() -> Path:
    out = subprocess.run(["git", "rev-parse", "--show-toplevel"], check=True,
                         capture_output=True, text=True,
                         cwd=Path(__file__).resolve().parent)
    return Path(out.stdout.strip())


sys.path.insert(0, str(_repo_root() / "mffp_autoresearch" / "round1" / "eval"))
from nrmse import nrmse as round_nrmse  # noqa: E402


def load(path, pred_key, target_key, want_target=False):
    z = np.load(path, allow_pickle=False)
    if pred_key not in z:
        raise KeyError(f"{path}: no key {pred_key!r} (has {list(z.keys())})")
    p = np.asarray(z[pred_key], dtype=np.float64)
    p = p.reshape(p.shape[0], -1)
    t = None
    if want_target:
        if target_key not in z:
            raise KeyError(f"{path}: no key {target_key!r} (has {list(z.keys())})")
        t = np.asarray(z[target_key], dtype=np.float64)
        t = t.reshape(t.shape[0], -1)
    return p, t


def per_sample_rel(pred, target):
    return np.linalg.norm(pred - target, axis=1) / np.linalg.norm(target, axis=1)


def best_global_scalar(base, C, target, grid=41):
    cands = np.linspace(0.0, 1.5, grid)
    scores = [round_nrmse(base + a * C, target) for a in cands]
    i = int(np.argmin(scores))
    return float(cands[i]), float(scores[i])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base_npz", required=True)
    ap.add_argument("--model_npz", required=True)
    ap.add_argument("--gated_npz", default=None)
    ap.add_argument("--pred_key", default="pred")
    ap.add_argument("--target_key", default="target")
    ap.add_argument("--top_k", type=int, default=3)
    ap.add_argument("--global_alpha", type=float, default=None,
                    help="the run's OWN held-out global scalar. Supply it: without it the "
                         "tool grid-searches alpha on the TEST split, which is an oracle "
                         "reference and flatters the gate.")
    ap.add_argument("--alpha_clip", nargs=2, type=float, default=None,
                    help="clip alpha_star to [lo, hi], matching the gate's own clip "
                         "(s6_local-B2 used 0 1.5). Unclipped by default.")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    base, Y = load(a.base_npz, a.pred_key, a.target_key, want_target=True)
    model, _ = load(a.model_npz, a.pred_key, a.target_key)
    gated = base if a.gated_npz is None else load(a.gated_npz, a.pred_key, a.target_key)[0]
    if not (base.shape == model.shape == gated.shape == Y.shape):
        raise SystemExit(f"shape mismatch: base {base.shape} model {model.shape} "
                         f"gated {gated.shape} target {Y.shape}")

    C = model - base
    R = Y - base
    den = (C * C).sum(axis=1)
    a_imp = np.where(den > 1e-20, ((gated - base) * C).sum(axis=1) / np.maximum(den, 1e-20), 0.0)
    a_star = np.where(den > 1e-20, (R * C).sum(axis=1) / np.maximum(den, 1e-20), 0.0)
    if a.alpha_clip:
        a_star = np.clip(a_star, a.alpha_clip[0], a.alpha_clip[1])
    if a.global_alpha is None:
        a_glob, s_glob = best_global_scalar(base, C, Y)
        glob_src = "TEST-fitted grid search (ORACLE reference — pass --global_alpha)"
    else:
        a_glob = float(a.global_alpha)
        s_glob = round_nrmse(base + a_glob * C, Y)
        glob_src = "supplied (the run's own held-out scalar)"

    e_base = per_sample_rel(base, Y)
    e_gate = per_sample_rel(gated, Y)
    e_one = per_sample_rel(model, Y)
    e_gl = per_sample_rel(base + a_glob * C, Y)
    e_star = per_sample_rel(base + a_star[:, None] * C, Y)
    excess = e_gate - e_star
    w = np.linalg.norm(C, axis=1) / np.linalg.norm(Y, axis=1)

    from scipy.stats import spearmanr, pearsonr
    ok = (a_star.std() > 1e-14) and (a_imp.std() > 1e-14)
    top = np.argsort(-excess)[: a.top_k]
    s_gate = round_nrmse(gated, Y)
    s_star = round_nrmse(base + a_star[:, None] * C, Y)

    res = {
        "n_samples": int(base.shape[0]),
        "alpha_implied": {"mean": float(a_imp.mean()), "std": float(a_imp.std()),
                          "min": float(a_imp.min()), "max": float(a_imp.max()),
                          "frac_below_0.01": float((a_imp < 0.01).mean())},
        "alpha_star": {"mean": float(a_star.mean()), "std": float(a_star.std()),
                       "p10": float(np.percentile(a_star, 10)),
                       "p50": float(np.percentile(a_star, 50)),
                       "p90": float(np.percentile(a_star, 90)),
                       "frac_below_0.01": float((a_star < 0.01).mean())},
        "recovery": {"pearson": float(pearsonr(a_imp, a_star)[0]) if ok else None,
                     "spearman": float(spearmanr(a_imp, a_star).correlation) if ok else None},
        "scores": {"base": round_nrmse(base, Y), "model_alpha_one": round_nrmse(model, Y),
                   "gated": s_gate, "best_global_scalar": s_glob,
                   "best_global_alpha": a_glob, "global_alpha_source": glob_src,
                   "alpha_star_clip": (list(a.alpha_clip) if a.alpha_clip else None),
                   "persample_oracle": s_star,
                   "oracle_gain_vs_global_pct": 100.0 * (s_star / s_glob - 1.0),
                   "gate_gain_vs_global_pct": 100.0 * (s_gate / s_glob - 1.0),
                   "captured_fraction_of_oracle_gain":
                       (float((s_glob - s_gate) / (s_glob - s_star))
                        if abs(s_glob - s_star) > 1e-30 else None)},
        "sensitivity": {
            "definition": "w_i = ||C_i|| / ||Y_i||, the scored metric's sensitivity to a "
                          "per-sample alpha error",
            "p50": float(np.median(w)), "p90": float(np.percentile(w, 90)),
            "max": float(w.max()),
            "max_over_p50": float(w.max() / max(np.median(w), 1e-30)),
            "spearman_excess_vs_w": float(spearmanr(excess, w).correlation),
            "spearman_p": float(spearmanr(excess, w).pvalue),
            "top_samples": [{"index": int(i), "w": float(w[i]),
                             "alpha_implied": float(a_imp[i]),
                             "alpha_star": float(a_star[i]),
                             "excess_rel_err": float(excess[i]),
                             "times_mean_excess": (float(excess[i] / excess.mean())
                                                   if abs(excess.mean()) > 1e-30 else None)}
                            for i in top]},
        "no_harm": {
            "frac_worse_than_base_gate": float((e_gate > e_base).mean()),
            "frac_worse_than_base_alpha_one": float((e_one > e_base).mean()),
            "frac_worse_than_base_global": float((e_gl > e_base).mean()),
            "worst_ratio_gate_over_base": float((e_gate / e_base).max()),
            "median_ratio_gate_over_base": float(np.median(e_gate / e_base))},
    }
    sens = res["sensitivity"]
    res["verdict"] = (
        "NO_PERSAMPLE_HEADROOM" if abs(res["scores"]["oracle_gain_vs_global_pct"]) < 1.0 else
        "SENSITIVITY_LIMITED" if (res["scores"]["gate_gain_vs_global_pct"] > 0
                                  and sens["max_over_p50"] > 10) else
        "GATE_HELPS" if res["scores"]["gate_gain_vs_global_pct"] < 0 else "GATE_HURTS")

    print(json.dumps(res, indent=1))
    print(f"\nVERDICT: {res['verdict']}")
    if a.out:
        with open(a.out, "w") as fh:
            json.dump(res, fh, indent=1)
        print(f"wrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
