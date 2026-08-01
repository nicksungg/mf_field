#!/usr/bin/env python
"""blend_decorrelation_payoff.py — what a post-hoc floor-BLEND stage actually pays,
and which arm class it pays.

A post-hoc stage of the form

    pred_final = lambda * pred_arm + (1 - lambda) * base           lambda in [0, 1]

is usually shipped as a FAIRNESS device (identical code path for every arm).
It is not one.  Under the aggregate-norm two-member ensemble model

    c(lambda)^2 = lambda^2 a^2 + (1-lambda)^2 b^2 + 2 lambda (1-lambda) rho a b
        a = c(1) = the arm alone (post whatever earlier stages ran)
        b = c(0) = the base alone
        rho     = correlation of the arm's error with the base's

the stage's payoff  min(a, b) - c_min  is a MONOTONE function of rho at fixed
(a, b): it pays an arm exactly in proportion to how DECORRELATED that arm's
errors are from the closed-form base.  Two arm classes can differ in rho by
construction (a closed-form condition-regression head can BE the closed-form
base, rho = 1, unpayable; a trained network sits at rho ~ 0.7 and collects),
so a comparison decided at this stage is a rho verdict, not an accuracy
verdict.

This tool fits the single free parameter rho per (dataset, arm, base) from the
calibration blend SURFACE the card already shipped (typically a 21-point
lambda grid -> 21 constraints for 1 parameter), reports the fit residual so
the aggregate-norm approximation is auditable, applies the closed form on the
test side, and runs the equal-rho counterfactual between two named arms.

Everything is read-only over shipped eval JSONs: no data loading, no
retraining, no checkpoints.  Runs in seconds.

INPUT SCHEMA (all key names are CLI-overridable)
    <diag>.dataset                                  dataset name
    <diag>.blend_full[arm].cal_table[base]          list of nRMSE, one per lambda
    <diag>.blend_full[arm].lambda_grid              the lambda values
    <diag>.blend_full[arm].{selected_base,selected_lambda,n_cal}
    <diag>.arm_table[arm].{nrmse_wiener,nrmse_wiener_blend,blend_base,blend_lambda}
    <diag>.arm_nrmse[<base_key_prefix><base>]       test nRMSE of each base

If a card ships the surface under different key names, pass --blend_key /
--cal_table_key / --arm_table_key / --arm_nrmse_key / --arm_post_field /
--final_field / --base_key_prefix.  Nothing else is assumed.

Provenance: r2s1_direct-B2 mechanism turn 3
(worktrees/r2s1_direct/B2/scratchpad/reanalysis_turn_3.py).
"""
from __future__ import annotations

import argparse
import glob as globmod
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROUND_ROOT = os.path.dirname(HERE)
DEF_COPYLF = os.path.join(ROUND_ROOT, "eval", "copylf_baselines.json")
DEF_FLOOR = os.path.join(ROUND_ROOT, "state", "noise_floor.json")


# ----------------------------------------------------------------- model ----
def c_model(lam, a, b, rho):
    lam = np.asarray(lam, dtype=float)
    v = lam ** 2 * a ** 2 + (1.0 - lam) ** 2 * b ** 2 + 2.0 * lam * (1.0 - lam) * rho * a * b
    return np.sqrt(np.maximum(v, 0.0))


def fit_rho(lams, cs, a, b, n_grid=20001):
    """Least squares over rho on a dense bounded grid (1-D, cheap, robust)."""
    grid = np.linspace(-1.0, 1.0, n_grid)[:, None]
    lam = np.asarray(lams, dtype=float)[None, :]
    v = lam ** 2 * a ** 2 + (1.0 - lam) ** 2 * b ** 2 + 2.0 * lam * (1.0 - lam) * grid * a * b
    r = np.sqrt(np.mean((np.sqrt(np.maximum(v, 0.0)) - np.asarray(cs, float)[None, :]) ** 2, axis=1))
    i = int(np.argmin(r))
    return float(grid[i, 0]), float(r[i])


def lam_star(a, b, rho):
    den = a ** 2 + b ** 2 - 2.0 * rho * a * b
    if den <= 0:
        return float("nan")
    return float((b ** 2 - rho * a * b) / den)


def c_min(a, b, rho):
    den = a ** 2 + b ** 2 - 2.0 * rho * a * b
    if den <= 0:
        return float("nan")
    return float(a * b * np.sqrt(max(1.0 - rho ** 2, 0.0)) / np.sqrt(den))


def c_min_clipped(a, b, rho, lo=0.0, hi=1.0):
    """c_min with lambda restricted to the shipped grid range (the achievable one)."""
    ls = lam_star(a, b, rho)
    ls = hi if ls != ls else min(hi, max(lo, ls))
    return float(c_model([ls], a, b, rho)[0]), float(ls)


def implied_rho(a, b, lam, final):
    if lam is None or final is None or not (0.0 < lam < 1.0):
        return None
    num = final ** 2 - lam ** 2 * a ** 2 - (1.0 - lam) ** 2 * b ** 2
    den = 2.0 * lam * (1.0 - lam) * a * b
    if den == 0:
        return None
    return float(num / den)


# ------------------------------------------------------------------ io -----
def load_json(p):
    with open(p) as fh:
        return json.load(fh)


def resolve_inputs(patterns):
    out = []
    for pat in patterns:
        hits = sorted(globmod.glob(pat))
        if not hits and os.path.exists(pat):
            hits = [pat]
        out.extend(hits)
    if not out:
        raise SystemExit("no diag JSONs matched: %r" % (patterns,))
    return out


def dig(obj, dotted, default=None):
    cur = obj
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur


# ---------------------------------------------------------------- main -----
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--diag", nargs="+", required=True,
                    help="shipped diagnostic JSON path(s) or glob(s), one per dataset")
    ap.add_argument("--arms", default=None,
                    help="comma-separated arm names to report (default: all arms in the blend block)")
    ap.add_argument("--bases", default=None,
                    help="comma-separated base names (default: all bases in the cal table)")
    ap.add_argument("--counterfactual", default=None,
                    help="ARM:REF_ARM:BASE — sweep rho for ARM's own (a, b) and report "
                         "what ARM would have scored at REF_ARM's measured rho, against "
                         "REF_ARM's shipped final")
    ap.add_argument("--rho_sweep", default="0.999,0.99,0.95,0.9,0.85,0.8,0.7,0.6,0.5,0.3,0.0",
                    help="extra rho values for the counterfactual curve")
    ap.add_argument("--skill", action="store_true",
                    help="also report skill units (nRMSE / copy-LF reference)")
    ap.add_argument("--copylf", default=DEF_COPYLF, help="copy-LF baseline JSON for --skill")
    ap.add_argument("--noise_floor", default=DEF_FLOOR,
                    help="noise-floor JSON supplying per-dataset min_claimable_effect (mce)")
    # --- schema knobs -------------------------------------------------------
    ap.add_argument("--dataset_key", default="dataset")
    ap.add_argument("--blend_key", default="blend_full")
    ap.add_argument("--cal_table_key", default="cal_table")
    ap.add_argument("--lambda_grid_key", default="lambda_grid")
    ap.add_argument("--arm_table_key", default="arm_table")
    ap.add_argument("--arm_nrmse_key", default="arm_nrmse")
    ap.add_argument("--arm_post_field", default="nrmse_wiener",
                    help="arm_table field holding the arm ALONE (a), post earlier stages")
    ap.add_argument("--final_field", default="nrmse_wiener_blend",
                    help="arm_table field holding the shipped post-blend score")
    ap.add_argument("--base_field", default="blend_base")
    ap.add_argument("--lambda_field", default="blend_lambda")
    ap.add_argument("--base_key_prefix", default="ref_",
                    help="prefix mapping a cal-table base name to its arm_nrmse key")
    ap.add_argument("--collinear_tau", type=float, default=0.99,
                    help="rho at or above which an arm is called COLLINEAR (unpayable)")
    ap.add_argument("--base_dominated_tau", type=float, default=0.25,
                    help="shipped lambda at or below which the reported score is the BASE")
    ap.add_argument("--out", default=None, help="write the full result JSON here")
    args = ap.parse_args(argv)

    arms_filter = [a for a in args.arms.split(",") if a] if args.arms else None
    bases_filter = [b for b in args.bases.split(",") if b] if args.bases else None

    copylf = load_json(args.copylf) if (args.skill and os.path.exists(args.copylf)) else {}
    floors = load_json(args.noise_floor) if os.path.exists(args.noise_floor) else {}

    out = {
        "tool": "blend_decorrelation_payoff.py",
        "model": "c(lam)^2 = lam^2 a^2 + (1-lam)^2 b^2 + 2 lam (1-lam) rho a b; "
                 "a = c(1) (arm alone), b = c(0) (base); rho fitted by least squares "
                 "on the shipped calibration lambda grid",
        "inputs": [],
        "datasets": {},
    }

    for path in resolve_inputs(args.diag):
        d = load_json(path)
        ds = d.get(args.dataset_key, os.path.basename(path))
        out["inputs"].append({"path": path, "dataset": ds})
        blend = d.get(args.blend_key, {})
        if not blend:
            print("WARN %s: no '%s' block, skipped" % (path, args.blend_key))
            continue
        k_skill = None
        if args.skill and ds in copylf and copylf[ds].get("test_nrmse"):
            k_skill = 1.0 / float(copylf[ds]["test_nrmse"])
        mce = dig(floors, "%s.min_claimable_effect" % ds)

        rec = {"source": path, "skill_per_nrmse": k_skill, "mce_skill_units": mce,
               "arms": {}, "test_side": {}}

        for arm, entry in sorted(blend.items()):
            if arms_filter and arm not in arms_filter:
                continue
            ct = entry.get(args.cal_table_key, {})
            lams = entry.get(args.lambda_grid_key)
            if not ct or not lams:
                continue
            lams = np.asarray(lams, dtype=float)
            arec = {"shipped_selected_base": entry.get("selected_base"),
                    "shipped_selected_lambda": entry.get("selected_lambda"),
                    "n_cal": entry.get("n_cal"), "bases": {}}
            for base, curve in sorted(ct.items()):
                if bases_filter and base not in bases_filter:
                    continue
                cs = np.asarray(curve, dtype=float)
                if cs.shape != lams.shape:
                    continue
                a, b = float(cs[-1]), float(cs[0])
                rho, resid = fit_rho(lams, cs, a, b)
                cc, lc = c_min_clipped(a, b, rho, float(lams.min()), float(lams.max()))
                arec["bases"][base] = {
                    "a_arm_cal_nrmse": a,
                    "b_base_cal_nrmse": b,
                    "rho_fit": rho,
                    "fit_rms_resid_nrmse": resid,
                    "fit_rms_resid_rel_to_a": (resid / a) if a else None,
                    "lambda_star_pred": lam_star(a, b, rho),
                    "lambda_star_clipped": lc,
                    "lambda_argmin_on_cal_curve": float(lams[int(np.argmin(cs))]),
                    "c_min_pred_nrmse": c_min(a, b, rho),
                    "c_min_clipped_nrmse": cc,
                    "c_min_on_cal_curve": float(cs.min()),
                    "payoff_nrmse_units": float(min(a, b) - cc),
                    "collinear_unpayable": bool(rho >= args.collinear_tau),
                }
            rec["arms"][arm] = arec

        # ---------------- test side on the shipped picks --------------------
        at = d.get(args.arm_table_key, {})
        an = d.get(args.arm_nrmse_key, {})
        rec["base_test_nrmse"] = {
            k[len(args.base_key_prefix):]: v for k, v in an.items()
            if k.startswith(args.base_key_prefix)
        }
        for arm, e in sorted(at.items()):
            if arms_filter and arm not in arms_filter:
                continue
            base = e.get(args.base_field)
            a = e.get(args.arm_post_field)
            lam = e.get(args.lambda_field)
            f = e.get(args.final_field)
            b = an.get("%s%s" % (args.base_key_prefix, base)) if base else None
            if a is None or b is None:
                continue
            rho_cal = dig(rec, "arms.%s.bases.%s.rho_fit" % (arm, base))
            t = {"base": base, "shipped_lambda": lam,
                 "a_arm_test_nrmse": a, "b_base_test_nrmse": b,
                 "final_shipped_nrmse": f,
                 "rho_fit_on_calibration_fold": rho_cal,
                 "rho_implied_on_test": implied_rho(a, b, lam, f)}
            if f is not None:
                t["payoff_actual_test_nrmse_units"] = float(min(a, b) - f)
                if k_skill:
                    t["payoff_actual_test_skill_units"] = float((min(a, b) - f) * k_skill)
                    if mce:
                        t["payoff_actual_mce_multiples"] = float((min(a, b) - f) * k_skill / mce)
            if rho_cal is not None:
                cc, lc = c_min_clipped(a, b, rho_cal)
                t["c_min_pred_test_nrmse_at_rho_cal"] = cc
                t["lambda_star_pred_test_at_rho_cal"] = lc
                t["payoff_pred_test_nrmse_units"] = float(min(a, b) - cc)
            # verdict
            v = []
            if rho_cal is not None and rho_cal >= args.collinear_tau:
                v.append("COLLINEAR_WITH_BASE")
            if lam is not None and lam <= args.base_dominated_tau:
                v.append("BASE_DOMINATED")
            if not v:
                v.append("ENSEMBLE_ACTIVE")
            t["verdict"] = "+".join(v)
            rec["test_side"][arm] = t

        # worst fit residual, the audit number for the aggregate-norm model
        worst, where = 0.0, None
        for arm, arec in rec["arms"].items():
            for base, br in arec["bases"].items():
                v = br.get("fit_rms_resid_rel_to_a") or 0.0
                if v > worst:
                    worst, where = v, "%s/%s" % (arm, base)
        rec["fit_quality"] = {"worst_rel_rms_resid": worst, "where": where}
        out["datasets"][ds] = rec

    # ------------------------------ counterfactual --------------------------
    if args.counterfactual:
        try:
            arm_c, ref_c, base_c = args.counterfactual.split(":")
        except ValueError:
            raise SystemExit("--counterfactual must be ARM:REF_ARM:BASE")
        cfs = {}
        for ds, rec in out["datasets"].items():
            ta = rec["test_side"].get(arm_c)
            tr = rec["test_side"].get(ref_c)
            rho_a = dig(rec, "arms.%s.bases.%s.rho_fit" % (arm_c, base_c))
            rho_r = dig(rec, "arms.%s.bases.%s.rho_fit" % (ref_c, base_c))
            b = rec.get("base_test_nrmse", {}).get(base_c)
            if ta is None or tr is None or rho_a is None or rho_r is None or b is None:
                continue
            a = ta["a_arm_test_nrmse"]
            k = rec["skill_per_nrmse"] or 1.0
            mce = rec["mce_skill_units"]
            rho_r_test = tr.get("rho_implied_on_test")
            rows = []
            for label, rho in [("arm_own_rho", rho_a), ("ref_rho_calfit", rho_r),
                               ("ref_rho_test_implied", rho_r_test)]:
                if rho is None:
                    continue
                cc, lc = c_min_clipped(a, b, rho)
                rows.append({"label": label, "rho": rho, "lambda_star_clipped": lc,
                             "final_nrmse": cc, "final_skill": cc * k})
            curve = []
            for rho in [float(x) for x in args.rho_sweep.split(",") if x.strip()]:
                cc, lc = c_min_clipped(a, b, rho)
                curve.append({"rho": rho, "lambda_star_clipped": lc,
                              "final_nrmse": cc, "final_skill": cc * k})
            ref_final = tr.get("final_shipped_nrmse")
            cf = {"arm": arm_c, "ref_arm": ref_c, "base": base_c,
                  "a_arm_test_nrmse": a, "b_base_test_nrmse": b,
                  "rho_arm_calfit": rho_a, "rho_ref_calfit": rho_r,
                  "rho_ref_test_implied": rho_r_test,
                  "ref_shipped_final_nrmse": ref_final,
                  "ref_shipped_final_skill": (ref_final * k) if ref_final is not None else None,
                  "arm_shipped_final_skill": (ta.get("final_shipped_nrmse") or 0.0) * k,
                  "arm_alone_skill": a * k, "ref_alone_skill": tr["a_arm_test_nrmse"] * k,
                  "at_rho": rows, "rho_curve": curve}
            if ref_final is not None:
                for r in rows:
                    r["delta_vs_ref_shipped_skill"] = ref_final * k - r["final_skill"]
                    if mce:
                        r["delta_mce_multiples"] = (ref_final * k - r["final_skill"]) / mce
            cfs[ds] = cf
        out["counterfactual"] = cfs

    # -------------------------------- console -------------------------------
    print("\n=== fit quality of the 1-parameter ensemble model (per dataset) ===")
    for ds, rec in out["datasets"].items():
        print("  %-32s worst rel RMS resid %.4g   (%s)"
              % (ds, rec["fit_quality"]["worst_rel_rms_resid"], rec["fit_quality"]["where"]))

    print("\n=== rho(arm error, base error), calibration-fold fit ===")
    for ds, rec in out["datasets"].items():
        for arm, t in sorted(rec["test_side"].items()):
            r = t["rho_fit_on_calibration_fold"]
            print("  %-30s %-18s base=%-12s lam=%-5s rho_cal=%s rho_test=%s  payoff=%+.5f nRMSE  %s"
                  % (ds, arm, t["base"],
                     ("%.2f" % t["shipped_lambda"]) if t["shipped_lambda"] is not None else "n/a",
                     ("%+.4f" % r) if r is not None else "  n/a ",
                     ("%+.4f" % t["rho_implied_on_test"]) if t.get("rho_implied_on_test") is not None else "  n/a ",
                     t.get("payoff_actual_test_nrmse_units", float("nan")), t["verdict"]))

    if args.counterfactual and out.get("counterfactual"):
        print("\n=== counterfactual: %s at %s's rho, vs %s's shipped final ==="
              % (arm_c, ref_c, ref_c))
        for ds, cf in out["counterfactual"].items():
            print("  %s" % ds)
            print("    a(arm)=%.6f b(base)=%.6f rho_arm=%+.4f rho_ref=%+.4f (test %s)"
                  % (cf["a_arm_test_nrmse"], cf["b_base_test_nrmse"], cf["rho_arm_calfit"],
                     cf["rho_ref_calfit"],
                     ("%+.4f" % cf["rho_ref_test_implied"]) if cf["rho_ref_test_implied"] is not None else "n/a"))
            for r in cf["at_rho"]:
                extra = ""
                if "delta_vs_ref_shipped_skill" in r:
                    extra = "  delta vs ref shipped %+.4f skill" % r["delta_vs_ref_shipped_skill"]
                    if "delta_mce_multiples" in r:
                        extra += " (%.2fx mce)" % r["delta_mce_multiples"]
                print("    %-22s rho=%+.4f lam*=%.3f -> %.6f nRMSE / %.4f skill%s"
                      % (r["label"], r["rho"], r["lambda_star_clipped"], r["final_nrmse"],
                         r["final_skill"], extra))

    if args.out:
        with open(args.out, "w") as fh:
            json.dump(out, fh, indent=1)
        print("\nwrote %s" % args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
