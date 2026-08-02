#!/usr/bin/env python
"""Is this arm's headroom a PER-SAMPLE SCALE, and does it move along the design
axis? The amplitude/structure split + the global-vs-per-sample oracle-gain
ladder, read across a sweep (N_train, capacity, epochs, seed, …) rather than on
one arm.

Provenance: promoted from `r2s4_diag-B4` mechanism turn 3
(`worktrees/r2s4_diag/B4/scratchpad/reanalysis_turn_3.py`, sections C and E).
There, on ifc_poisson at N_hf = 5: a single GLOBAL oracle rescale removed
**0.19 %** of the scored error while a PER-SAMPLE oracle gain removed **65.4 %**
(skill 8.261 -> 2.858 = 5.76x the certified mce); the removable fraction rose
monotonically with N_hf (47.0 -> 65.4 %); the across-test-row dispersion ratio
was 0.492 at the best point and was HIGHER for the 4x-narrower model at every
matched n, which is what turned "conditional-mean collapse" from a
representational story into a few-sample-regularisation one.

HOW IT DIFFERS FROM THE EXISTING TOOLS
  `field_error_decomposition.py` (round-1) does the same split for ONE arm at a
  time and `gain_calibration_ceiling.py` prices the calibration ceilings on ONE
  prediction. This tool is the LADDER: it reads a whole sweep out of a multi-leg
  dump, reports every cell in the same units, and adds the two readings that only
  exist along an axis — the TREND of the removable fraction and of the dispersion
  ratio, and the matched-axis CONTRAST between two groups split by channel
  (which says whether a capacity/architecture change costs shape or scale).

WHAT IT MEASURES, per (group, axis) cell
  skill_raw                     mean per-sample rel-L2 / --ref (the round's kernel)
  amp2 / str2                   the exact orthogonal split of the SQUARED rel-L2:
                                (1-g)^2 with g = <p,y>/<y,y>, and ||p-g y||^2/||y||^2
  amplitude_share_of_sq_error   how much of the squared error is scale, not shape
  skill_after_global_gain       one oracle scalar for the whole test set
  skill_after_per_sample_gain   each sample rescaled by its own oracle gain
                                (= sqrt(1-cos^2), the STRUCTURE-only error)
  frac_removed_*                what each oracle buys, as a fraction of the score
  dispersion_ratio              ||P - mean_row(P)|| / ||Y - mean_row(Y)||: 1.0 =
                                the arm varies with the condition as much as the
                                truth, << 1 = collapsed toward the mean field
  trend.*                       Spearman of frac_removed / dispersion against the
                                axis, and whether they are monotone
  contrast.*                    (two groups) matched-axis delta split by channel

READ IT AS
  `frac_removed_per_sample` >> `frac_removed_global` -> the headroom is genuinely
  PER-SAMPLE; a global rescale, a loss reweighting or an output scaler cannot
  reach it, and the arm needs a per-sample signal (an LF field at inference, a
  calibration head on the condition vector). If the two are close, the arm is
  simply mis-scaled and one constant fixes it.
  A rising `dispersion_ratio` along a sample-count axis with a FLAT one along a
  capacity axis = the collapse is few-sample regularisation, not a
  representational limit: adding parameters will not move it.
  `contrast.amplitude_share_of_penalty` near 0 = the change cost SHAPE only.
  Every gain arm here is an ORACLE (it reads the test truth); the numbers are
  UPPER BOUNDS on what any gain-only repair could deliver, never scores.
  `channel_signs_disagree` = the two channels moved in OPPOSITE directions
  between the two groups, so no single "share of the penalty" exists; read the
  raw `delta_amp2` / `delta_str2` instead.
  The per-sample oracle is the exact minimiser of the round's metric, so
  `frac_removed_per_sample` >= 0 always. The GLOBAL scalar minimises total
  squared error, not the mean relative norm, so `frac_removed_global` can be
  slightly NEGATIVE — that is a property of the estimator, not a bug.

USAGE
  A) multi-leg dump (one npz key per leg, the r2s4-B4 shape):
  python tools/gain_channel_ladder.py \
      --legs_json <anatomy.json> --legs_path anatomy.group_A_curve \
      --preds_npz <preds_test.npz> --truth_key hf_true \
      --leg_key leg --axis_key n --group_key width --ref 0.036 \
      --metric_key test_nrmse --out ladder.json

  B) one npz per arm (the standard `preds_test.npz` shape):
  python tools/gain_channel_ladder.py \
      --arm_npz a.npz b.npz --labels n1 n5 --axis_values 1 5 \
      --pred_key pred --target_key target --ref 0.036 --out ladder.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_EVAL = Path(__file__).resolve().parent.parent / "eval"
sys.path.insert(0, str(_EVAL))
import nrmse as nrmse_mod  # noqa: E402  (the round's single metric definition)


def dotted(obj, path: str):
    cur = obj
    for part in path.split("."):
        cur = cur[int(part)] if isinstance(cur, list) else cur[part]
    return cur


def spearman(a, b) -> float:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    if a.size < 2:
        return float("nan")
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    ra -= ra.mean()
    rb -= rb.mean()
    den = np.sqrt((ra @ ra) * (rb @ rb))
    return float(ra @ rb / den) if den > 0 else float("nan")


def channels(P, Y):
    """Exact orthogonal split of the SQUARED per-sample rel-L2, plus the oracles."""
    P = np.asarray(P, dtype=np.float64)
    Y = np.asarray(Y, dtype=np.float64)
    y_n2 = (Y * Y).sum(1)
    p_n2 = (P * P).sum(1)
    rel = np.linalg.norm(P - Y, axis=1) / np.sqrt(y_n2)
    g = (P * Y).sum(1) / y_n2                        # projection of p onto y
    amp2 = (1.0 - g) ** 2
    str2 = ((P - g[:, None] * Y) ** 2).sum(1) / y_n2
    with np.errstate(invalid="ignore", divide="ignore"):
        cos = (P * Y).sum(1) / np.sqrt(p_n2 * y_n2)
    per_sample_oracle = np.sqrt(np.clip(1.0 - cos ** 2, 0.0, None))
    a_glob = float((P * Y).sum() / (P * P).sum())
    rel_glob = np.linalg.norm(a_glob * P - Y, axis=1) / np.sqrt(y_n2)
    disp = float(np.linalg.norm(P - P.mean(0, keepdims=True))
                 / np.linalg.norm(Y - Y.mean(0, keepdims=True)))
    return {"rel": rel, "amp2": amp2, "str2": str2, "gain": g,
            "oracle_per_sample": per_sample_oracle, "oracle_global": rel_glob,
            "global_scalar": a_glob, "dispersion": disp}


def cell_stats(chs, ref):
    """Aggregate a list of per-leg channel dicts into one ladder cell."""
    rel = float(np.mean([c["rel"].mean() for c in chs]))
    orc = float(np.mean([c["oracle_per_sample"].mean() for c in chs]))
    glo = float(np.mean([c["oracle_global"].mean() for c in chs]))
    a = float(np.mean([c["amp2"].mean() for c in chs]))
    s = float(np.mean([c["str2"].mean() for c in chs]))
    return {
        "n_legs": len(chs),
        "nrmse_raw": rel,
        "skill_raw": rel / ref,
        "skill_after_global_gain": glo / ref,
        "skill_after_per_sample_gain": orc / ref,
        "frac_removed_global": 1.0 - glo / rel,
        "frac_removed_per_sample": 1.0 - orc / rel,
        "mean_amp2": a, "mean_str2": s, "mean_sq_rel_l2": a + s,
        "amplitude_share_of_sq_error": a / (a + s) if (a + s) > 0 else None,
        "mean_gain_g": float(np.mean([c["gain"].mean() for c in chs])),
        "frac_samples_gain_below_1": float(np.mean([(c["gain"] < 1).mean() for c in chs])),
        "mean_global_oracle_scalar": float(np.mean([c["global_scalar"] for c in chs])),
        "dispersion_ratio": float(np.mean([c["dispersion"] for c in chs])),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    # mode A
    ap.add_argument("--legs_json", default=None)
    ap.add_argument("--legs_path", default="anatomy.group_A_curve")
    ap.add_argument("--preds_npz", default=None,
                    help="npz with one (N, n_cells) array per leg key + the truth")
    ap.add_argument("--truth_key", default="hf_true")
    ap.add_argument("--leg_key", default="leg")
    ap.add_argument("--axis_key", default="n", help="the sweep axis (e.g. n, epochs)")
    ap.add_argument("--group_key", default=None,
                    help="second factor to split on (e.g. width); optional")
    ap.add_argument("--metric_key", default=None,
                    help="per-leg metric in the dump, seam-checked against eval/nrmse.py")
    ap.add_argument("--filter", action="append", default=[], metavar="KEY=VAL")
    # mode B
    ap.add_argument("--arm_npz", nargs="*", default=[], metavar="PATH[::PRED_KEY]",
                    help="one arm per entry; append '::KEY' to pick a prediction key "
                         "inside a multi-arm npz (the target then comes from --target_key)")
    ap.add_argument("--labels", nargs="*", default=[])
    ap.add_argument("--axis_values", nargs="*", default=[])
    ap.add_argument("--group_values", nargs="*", default=[])
    ap.add_argument("--pred_key", default="pred")
    ap.add_argument("--target_key", default="target")
    # common
    ap.add_argument("--ref", type=float, required=True,
                    help="denominator converting nRMSE to the card's skill")
    ap.add_argument("--mce", type=float, default=None)
    ap.add_argument("--noise_floor_json", default=None)
    ap.add_argument("--dataset", default=None)
    ap.add_argument("--collapse_threshold", type=float, default=0.7,
                    help="dispersion_ratio below this flags COLLAPSED")
    ap.add_argument("--per_sample_threshold", type=float, default=0.30,
                    help="frac_removed_per_sample above this (with a small global "
                         "fraction) flags PER_SAMPLE_GAIN_HEADROOM")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    R = {"tool": "gain_channel_ladder.py",
         "nrmse_def_hash": nrmse_mod.NRMSE_DEF_HASH,
         "inputs": {k: v for k, v in vars(args).items()},
         "definitions": {
             "channel_split": "rel_l2_i^2 = (1-g_i)^2 + ||p_i - g_i y_i||^2/||y_i||^2, "
                              "g_i = <p_i,y_i>/<y_i,y_i>; exact and orthogonal. Lives on "
                              "the ENERGY-METRIC TWIN (mean of SQUARED rel-L2) and is "
                              "never substituted for the round's nRMSE.",
             "oracles": "per-sample gain a_i = <p_i,y_i>/<p_i,p_i> (residual rel-L2 = "
                        "sqrt(1-cos^2)) and one global scalar; BOTH read the test truth "
                        "and are upper bounds, not scores.",
             "dispersion_ratio": "||P - mean_row(P)||_F / ||Y - mean_row(Y)||_F"}}

    mce = args.mce
    if mce is None and args.noise_floor_json and args.dataset:
        mce = json.loads(Path(args.noise_floor_json).read_text())[args.dataset][
            "min_claimable_effect"]
    R["mce"] = mce

    cells = {}          # (group, axis) -> list of channel dicts
    seam = []
    if args.legs_json:
        if not args.preds_npz:
            print("FAILURE: --preds_npz is required in legs mode", file=sys.stderr)
            return 2
        raw = json.loads(Path(args.legs_json).read_text())
        legs = raw if args.legs_path in ("", ".") else dotted(raw, args.legs_path)
        for f in args.filter:
            key, val = f.split("=", 1)
            legs = [e for e in legs if str(e.get(key)) == val]
        z = np.load(args.preds_npz)
        Y = np.asarray(z[args.truth_key], dtype=np.float64)
        for e in legs:
            k = e[args.leg_key]
            if k not in z.files:
                continue
            P = np.asarray(z[k], dtype=np.float64)
            c = channels(P, Y)
            if args.metric_key and args.metric_key in e:
                seam.append(abs(float(c["rel"].mean()) - float(e[args.metric_key])))
            seam.append(abs(float(c["rel"].mean()) - nrmse_mod.nrmse(P, Y)))
            g = str(e[args.group_key]) if args.group_key else "all"
            cells.setdefault((g, str(e[args.axis_key])), []).append(c)
        R["legs"] = {"legs_after_filter": len(legs),
                     "legs_with_predictions": sum(len(v) for v in cells.values())}
    elif args.arm_npz:
        labels = args.labels or [p.split("::")[-1] if "::" in p else Path(p).stem
                                 for p in args.arm_npz]
        axis = args.axis_values or labels
        groups = args.group_values or ["all"] * len(args.arm_npz)
        if not (len(labels) == len(axis) == len(groups) == len(args.arm_npz)):
            print("FAILURE: --labels/--axis_values/--group_values must match --arm_npz",
                  file=sys.stderr)
            return 2
        for spec, lab, ax, gr in zip(args.arm_npz, labels, axis, groups):
            path, _, pkey = spec.partition("::")
            z = np.load(path)
            P = np.asarray(z[pkey or args.pred_key], dtype=np.float64)
            Y = np.asarray(z[args.target_key], dtype=np.float64)
            c = channels(P, Y)
            seam.append(abs(float(c["rel"].mean()) - nrmse_mod.nrmse(P, Y)))
            cells.setdefault((str(gr), str(ax)), []).append(c)
        R["legs"] = {"arms": labels}
    else:
        print("FAILURE: pass either --legs_json/--preds_npz or --arm_npz", file=sys.stderr)
        return 2

    if not cells:
        print("FAILURE: no cells built (no leg matched a prediction key)", file=sys.stderr)
        return 2

    # exact-identity seam, computed on one cell's first leg
    any_c = next(iter(cells.values()))[0]
    R["seam"] = {
        "max_abs_diff_recomputed_vs_declared_metric": float(max(seam)) if seam else None,
        "max_abs_violation_rel_l2sq_eq_amp_plus_str":
            float(np.abs(any_c["rel"] ** 2 - (any_c["amp2"] + any_c["str2"])).max()),
        "zero_predictor_channel_check": {"amp2": 1.0, "str2": 0.0,
                                         "implied_skill": 1.0 / args.ref},
        "note": "the recomputed per-sample mean is checked against eval/nrmse.py and, "
                "when --metric_key is given, against the dump's own number",
    }

    ladder = {}
    for (g, ax), chs in sorted(cells.items(), key=lambda kv: (kv[0][0], _num(kv[0][1]))):
        ladder.setdefault(g, {})[ax] = cell_stats(chs, args.ref)
    if mce:
        for g in ladder:
            for ax in ladder[g]:
                c = ladder[g][ax]
                c["gain_headroom_in_mce_units"] = (
                    c["skill_raw"] - c["skill_after_per_sample_gain"]) / mce
    R["ladder"] = ladder

    trend = {}
    for g, cs in ladder.items():
        axs = sorted(cs, key=_num)
        xs = [_num(a) for a in axs]
        if all(np.isfinite(xs)) and len(xs) > 1:
            fr = [cs[a]["frac_removed_per_sample"] for a in axs]
            dp = [cs[a]["dispersion_ratio"] for a in axs]
            sk = [cs[a]["skill_raw"] for a in axs]
            trend[g] = {
                "axis": axs,
                "spearman_frac_removed_per_sample_vs_axis": spearman(xs, fr),
                "spearman_dispersion_vs_axis": spearman(xs, dp),
                "spearman_skill_vs_axis": spearman(xs, sk),
                "dispersion_monotone_increasing": bool(all(
                    dp[i + 1] >= dp[i] for i in range(len(dp) - 1))),
                "frac_removed_monotone_increasing": bool(all(
                    fr[i + 1] >= fr[i] for i in range(len(fr) - 1))),
                "dispersion_range": [float(min(dp)), float(max(dp))],
            }
    R["trend"] = trend

    if len(ladder) == 2:
        (ga, ca), (gb, cb) = sorted(ladder.items())
        shared = sorted(set(ca) & set(cb), key=_num)
        con = {}
        for ax in shared:
            da = ca[ax]["mean_amp2"] - cb[ax]["mean_amp2"]
            ds = ca[ax]["mean_str2"] - cb[ax]["mean_str2"]
            disagree = bool(da * ds < 0)
            con[ax] = {
                "delta_skill_raw": ca[ax]["skill_raw"] - cb[ax]["skill_raw"],
                "delta_skill_in_mce_units":
                    ((ca[ax]["skill_raw"] - cb[ax]["skill_raw"]) / mce) if mce else None,
                "delta_amp2": da, "delta_str2": ds,
                "channel_signs_disagree": disagree,
                "amplitude_share_of_penalty":
                    None if (disagree or (da + ds) == 0) else da / (da + ds),
                "delta_dispersion_ratio":
                    ca[ax]["dispersion_ratio"] - cb[ax]["dispersion_ratio"],
            }
        R["contrast"] = {
            "definition": f"group '{ga}' minus group '{gb}' at matched axis value",
            "per_axis": con,
            "reading": "amplitude_share_of_penalty ~ 0 => the change cost SHAPE only; "
                       "~ 1 => it cost SCALE only",
        }

    # verdicts on the best (lowest skill_raw) cell of each group
    verd = {}
    for g, cs in ladder.items():
        best = min(cs, key=lambda a: cs[a]["skill_raw"])
        c = cs[best]
        vs = []
        if (c["frac_removed_per_sample"] > args.per_sample_threshold
                and c["frac_removed_per_sample"] > 5 * max(c["frac_removed_global"], 1e-9)):
            vs.append("PER_SAMPLE_GAIN_HEADROOM")
        elif c["frac_removed_global"] > args.per_sample_threshold:
            vs.append("GLOBALLY_MISCALED")
        if c["dispersion_ratio"] < args.collapse_threshold:
            vs.append("COLLAPSED_TOWARD_MEAN_FIELD")
        t = trend.get(g, {})
        if t.get("dispersion_monotone_increasing") and t.get(
                "spearman_dispersion_vs_axis", 0) > 0:
            vs.append("DISPERSION_RISES_WITH_AXIS")
        verd[g] = {"best_cell": best, "flags": vs or ["NO_FLAG"],
                   "skill_raw": c["skill_raw"],
                   "skill_after_per_sample_gain": c["skill_after_per_sample_gain"],
                   "frac_removed_per_sample": c["frac_removed_per_sample"],
                   "frac_removed_global": c["frac_removed_global"],
                   "dispersion_ratio": c["dispersion_ratio"]}
    R["verdict"] = verd

    Path(args.out).write_text(json.dumps(R, indent=2))
    print(json.dumps({"seam": R["seam"], "ladder": R["ladder"],
                      "trend": R["trend"], "contrast": R.get("contrast"),
                      "verdict": R["verdict"]}, indent=2))
    print(f"WROTE {args.out}")
    return 0


def _num(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return float("inf")


if __name__ == "__main__":
    raise SystemExit(main())
