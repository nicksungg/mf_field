#!/usr/bin/env python
"""Is a paired A-vs-B effect CLAIMABLE, and does the answer depend on how the threshold is read?

Provenance: promoted from `r2s3_lf_train_signal-B3` mechanism turn 1
(`worktrees/r2s3_lf_train_signal/B3/scratchpad/reanalysis_turn_1.py`), where a
card's falsification clause sat exactly on a knife edge: `max(mce, in-job range)`
gave 3/6 datasets passing (FALSIFIED) and `mce` alone gave exactly 5/6
(CONFIRMED at the minimum margin).

WHY THIS EXISTS
---------------
A matched-arm card measures an effect across REPEATED SPLITS (HF-subset draws,
folds, restarts) and then asks whether the effect clears a certified constant.
Two different variance components are in play and cards routinely conflate them:

  (a) TEST-SAMPLE variance — conditional on one split, is the effect real over
      the test distribution? Paired per-sample bootstrap answers this.
  (b) SPLIT variance — would you get the effect again with a different draw of
      the training rows? Only the repeated splits answer this.

A certified `min_claimable_effect` imported from a seed-spread protocol usually
contains NEITHER of these in the right proportion: r2s3-B3's constant came from 3
TRAINING SEEDS of a full-data model and was 825x smaller than the split-to-split
range of the control arm it was applied to. Reading the threshold as that
constant alone silently prices the dominant noise source at zero.

This tool measures both components and recounts the verdict under SEVEN
threshold readings, so the knife edge becomes an observation instead of an
adjudication:

  verbatim_max_mce_spread    effect > max(mce, max-min range of the effect)
  mce_only                   effect > mce
  paired_se_over_splits      effect > max(mce, 1.96 * SE of the split-mean),
                             SE from the range via the control-chart d2 factor
  persample_ci_excludes_zero paired per-sample bootstrap CI excludes 0 AND
                             effect > mce
  median_stat_verbatim       same as verbatim but on a per-sample MEDIAN score
  worst_split_vs_mce         effect > mce on EVERY split (the well-posed
                             conservative gate: no coupling between the effect
                             and its own dispersion)
  log_effect_vs_own_range    the same comparison in log-score units, i.e. the
                             native units of a geometric-mean panel metric

READ IT AS
----------
All readings agree -> the verdict is robust, quote it and move on. Readings that
PRICE split variance disagree with those that do not -> the card is measuring a
variance-reduction effect and the gate inherits the CONTROL's instability; report
both and prefer `worst_split_vs_mce`, which prices the same conservatism without
making the threshold a function of the treatment's own success. A `mce` that is
orders of magnitude below the observed split range is a provenance smell: check
which axis the constant was certified on.

INPUTS
------
Per-leg result JSONs written by `eval/score_panel.py` (or any JSON carrying a
per-sample relative-L2 array at `splits.<split>.rel_l2_per_sample`). One leg per
(arm, split); legs of the same arm must share the same test set and order.

USAGE
-----
  source "$PROJECT_ROOT/.venv/bin/activate"
  python tools/effect_threshold_readings.py --dataset sharp__cahn_hilliard \\
      --arm A0_nolf=<outputs>/results_ch_A0_d0/<fam>/<ds>_e200_s0.json,\\
<outputs>/results_ch_A0_d1/<fam>/<ds>_e200_s0.json,\\
<outputs>/results_ch_A0_d2/<fam>/<ds>_e200_s0.json \\
      --arm A1_lf_cov=<...d0>,<...d1>,<...d2> \\
      --contrast A0_nolf:A1_lf_cov --mce 0.0912453532 --out readings.json

`--mce` may instead be read from a noise-floor file with
`--noise_floor <path> --mce_key min_claimable_effect`. The score denominator
comes from `state/anchors/floors.json` unless `--skill_denominator` is given.
Pure numpy; runs on the login node in seconds.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROUND_ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROUND_ROOT / "eval"))
from nrmse import NRMSE_DEF_HASH            # noqa: E402
from affine_ladder_voi import skill_denominator   # noqa: E402

D2 = {2: 1.12838, 3: 1.69257, 4: 2.05875, 5: 2.32593, 6: 2.53441,
      7: 2.70436, 8: 2.84720, 9: 2.97003, 10: 3.07751}


def _per_sample(path, split):
    j = json.loads(Path(path).read_text())
    sp = j.get("splits", {}).get(split)
    if sp is None:
        raise SystemExit(f"{path}: no splits.{split}")
    v = sp.get("rel_l2_per_sample")
    if v is None:
        raise SystemExit(f"{path}: splits.{split} has no rel_l2_per_sample "
                         f"(keys {sorted(sp)})")
    return np.asarray(v, dtype=np.float64), j


def _arm(spec, split):
    name, paths = spec.split("=", 1)
    legs = [p for p in paths.split(",") if p]
    arrs, metas = [], []
    for p in legs:
        a, j = _per_sample(p, split)
        arrs.append(a)
        metas.append({"path": p,
                      "nrmse_def_hash": j.get("nrmse_def_hash"),
                      "copylf_def_hash": j.get("copylf_def_hash")})
    n = {len(a) for a in arrs}
    if len(n) != 1:
        raise SystemExit(f"{name}: legs disagree on n_test {sorted(n)}")
    return name, np.stack(arrs), metas


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--arm", action="append", required=True,
                    help="NAME=leg.json[,leg.json...] (one leg per split)")
    ap.add_argument("--contrast", required=True, help="A:B — the effect is A minus B")
    ap.add_argument("--split", default="test_hf")
    ap.add_argument("--mce", type=float, default=None)
    ap.add_argument("--noise_floor", default=None)
    ap.add_argument("--mce_key", default="min_claimable_effect")
    ap.add_argument("--skill_denominator", type=float, default=None)
    ap.add_argument("--n_boot", type=int, default=20000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    D, dsrc = skill_denominator(a.dataset, a.skill_denominator)
    if a.mce is not None:
        mce, msrc = float(a.mce), "cli"
    elif a.noise_floor:
        nf = json.loads(Path(a.noise_floor).read_text())
        if a.dataset not in nf:
            raise SystemExit(f"{a.noise_floor} has no entry for {a.dataset}")
        mce, msrc = float(nf[a.dataset][a.mce_key]), a.noise_floor
    else:
        raise SystemExit("pass --mce or --noise_floor")

    arms, metas = {}, {}
    for s in a.arm:
        nm, stack, meta = _arm(s, a.split)
        arms[nm], metas[nm] = stack, meta
    ka, kb = a.contrast.split(":")
    for k in (ka, kb):
        if k not in arms:
            raise SystemExit(f"--contrast names {k}, which is not an --arm")
    A, B = arms[ka], arms[kb]
    if A.shape != B.shape:
        raise SystemExit(f"arms disagree in shape: {A.shape} vs {B.shape}")
    n_split, n_test = A.shape

    sA, sB = A.mean(1) / D, B.mean(1) / D           # per-split score
    rA, rB = np.median(A, 1) / D, np.median(B, 1) / D
    eff, eff_med = sA - sB, rA - rB
    rng = np.random.default_rng(a.seed)

    out = {
        "_tool": "effect_threshold_readings.py",
        "_nrmse_def_hash": NRMSE_DEF_HASH,
        "dataset": a.dataset, "split": a.split, "contrast": a.contrast,
        "n_splits": int(n_split), "n_test": int(n_test),
        "skill_denominator": D, "skill_denominator_source": dsrc,
        "certified_mce": mce, "certified_mce_source": msrc,
        "arm_legs": metas,
        "per_split_score": {ka: sA.tolist(), kb: sB.tolist()},
        "per_split_effect": eff.tolist(),
        "per_split_effect_median_stat": eff_med.tolist(),
        "effect_mean": float(eff.mean()),
        "sign_consistent_splits": int((eff > 0).sum()),
    }
    # ---- split-variance component ------------------------------------------
    if n_split > 1:
        d2 = D2.get(n_split, np.sqrt(2 * np.log(n_split)))  # crude fallback
        rngE = float(eff.max() - eff.min())
        sd = rngE / d2
        se = sd / np.sqrt(n_split)
        out["split_variance"] = {
            "spread_maxmin_effect": rngE,
            "d2_factor": d2,
            "sd_hat_from_range": float(sd),
            "se_of_split_mean": float(se),
            "t_effect_over_se": float(eff.mean() / se) if se else None,
            "spread_maxmin_score": {ka: float(sA.max() - sA.min()),
                                    kb: float(sB.max() - sB.min())},
            "cv_score": {ka: float(sA.std(ddof=1) / sA.mean()),
                         kb: float(sB.std(ddof=1) / sB.mean())},
            "arm_instability_ratio_a_over_b": float(
                (sA.max() - sA.min()) / max(sB.max() - sB.min(), 1e-12)),
            "spread_maxmin_effect_median_stat": float(eff_med.max() - eff_med.min()),
        }
        log_eff = np.log(sA) - np.log(sB)
        out["log_units"] = {
            "per_split_log_effect": log_eff.tolist(),
            "log_effect_mean": float(log_eff.mean()),
            "log_effect_spread_maxmin": float(log_eff.max() - log_eff.min()),
            "abs_effect_range_over_mean": float(rngE / abs(eff.mean())) if eff.mean() else None,
        }
    # ---- test-sample variance component ------------------------------------
    delta = (A - B) / D
    dbar = delta.mean(0)
    idx = rng.integers(0, n_test, size=(a.n_boot, n_test))
    boot = dbar[idx].mean(1)
    lo, hi = float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))
    out["persample_paired"] = {
        "effect": float(dbar.mean()), "ci95": [lo, hi],
        "excludes_zero": bool(lo > 0 or hi < 0),
        "frac_samples_b_better": float((dbar > 0).mean()),
        "se_over_test_samples": float(dbar.std(ddof=1) / np.sqrt(n_test)),
        "per_split": [{"split": i, "effect": float(delta[i].mean()),
                       "frac_samples_b_better": float((delta[i] > 0).mean())}
                      for i in range(n_split)],
    }
    # ---- the seven readings -------------------------------------------------
    e, em = float(eff.mean()), float(eff_med.mean())
    sp = out.get("split_variance", {})
    R = {}
    R["verbatim_max_mce_spread"] = (e, max(mce, sp.get("spread_maxmin_effect", 0.0)))
    R["mce_only"] = (e, mce)
    R["paired_se_over_splits"] = (e, max(mce, 1.96 * sp["se_of_split_mean"])
                                  if sp else mce)
    R["median_stat_verbatim"] = (em, max(mce, sp.get("spread_maxmin_effect_median_stat", 0.0)))
    R["worst_split_vs_mce"] = (float(eff.min()), mce)
    if "log_units" in out:
        R["log_effect_vs_own_range"] = (out["log_units"]["log_effect_mean"],
                                        out["log_units"]["log_effect_spread_maxmin"])
    readings = {k: {"statistic": v[0], "threshold": v[1],
                    "pass": bool(v[0] > 0 and v[0] > v[1])} for k, v in R.items()}
    readings["persample_ci_excludes_zero"] = {
        "statistic": e, "threshold": mce,
        "pass": bool(lo > 0 and e > mce)}
    out["readings"] = readings
    out["readings_agree"] = len({r["pass"] for r in readings.values()}) == 1
    out["n_readings_pass"] = int(sum(r["pass"] for r in readings.values()))
    out["mce_over_observed_split_range"] = (
        float(mce / sp["spread_maxmin_effect"]) if sp.get("spread_maxmin_effect") else None)

    print(f"== {a.dataset}  {a.contrast}  ({n_split} splits x {n_test} test samples) ==")
    print(f"  per-split effect {np.round(eff, 4).tolist()}   mean {e:.4f}"
          f"   sign-consistent {int((eff > 0).sum())}/{n_split}")
    if sp:
        print(f"  split range {sp['spread_maxmin_effect']:.4f}  sd_hat {sp['sd_hat_from_range']:.4f}"
              f"  SE(mean) {sp['se_of_split_mean']:.4f}  t {sp['t_effect_over_se']:.2f}")
        print(f"  arm instability (max-min score) {ka} {sp['spread_maxmin_score'][ka]:.4f} vs "
              f"{kb} {sp['spread_maxmin_score'][kb]:.4f}  -> {sp['arm_instability_ratio_a_over_b']:.1f}x")
    print(f"  certified mce {mce:.6g} ({msrc})"
          + (f"  = {out['mce_over_observed_split_range']:.3g} x the observed split range"
             if out["mce_over_observed_split_range"] else ""))
    print(f"  per-sample paired effect {dbar.mean():.4f}  CI95 [{lo:.4f}, {hi:.4f}]"
          f"  excl0 {out['persample_paired']['excludes_zero']}")
    print("  readings:")
    for k, r in readings.items():
        print(f"    {k:28s} stat {r['statistic']:12.4f}  thr {r['threshold']:12.4f}  "
              f"{'PASS' if r['pass'] else 'FAIL'}")
    print(f"  ALL READINGS AGREE: {out['readings_agree']}  "
          f"({out['n_readings_pass']}/{len(readings)} pass)")

    if a.out:
        Path(a.out).write_text(json.dumps(out, indent=1))
        print("wrote", a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
