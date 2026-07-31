#!/usr/bin/env python
"""LEVEL vs FLUCTUATION: decompose any shipped shrinkage curve, and find out
whether an arm contrast is a mean-field difference or a condition-response
difference — the two get averaged together in one nRMSE and can point opposite
ways.

WHY THIS EXISTS
---------------
Round 2 cards ship post-hoc shrinkage toward the arm's OWN mean field,
`P(λ) = P̄ + λ (P − P̄)`, scored on a grid of λ (r2s4-B1 made it a required
column). That curve contains strictly more than the `λ*` it is usually reduced
to. Its two ends are two different questions:

  f(0)  the LEVEL      — the own-mean broadcast: what the trunk learned that is
                          the same for every condition;
  f(1)  the RAW score  — level plus the condition-dependent FLUCTUATION.

r2s4-B2's helmholtz arms tied at the level (T0 − T1 = +0.4179 skill, T1 better
on 2/3 seeds) and separated with the opposite sign at λ = 1 (−0.8980). Reported
as one number the contrast "flips sign between the raw and the shrunk column",
which reads as a paradox; decomposed, it is one sentence: same mean field,
different (and on that dataset anti-aligned, seed-unstable) condition response.
Any card comparing arms that both ship shrinkage curves can and should run this
before interpreting a delta.

WHAT IT REPORTS  (per curve)
----------------------------
  level_lambda0, raw_lambda1, min_value, lambda_argmin        model-free
  slope_top                    ≈ mean_i‖P_i − P̄‖/‖y_i‖, the fluctuation amplitude
  eff_fluct_over_level         fluctuation size relative to the level
  eff_alignment                cos(fluctuation, y − P̄) — NEGATIVE ⇒ the
                               condition response points away from the truth
  eff_lambda_opt, fit_r2       from a sqrt-quadratic fit of f² in λ (the mean of
                               square roots is not a square root, so this is an
                               EFFECTIVE single-sample-equivalent summary; its R²
                               is always reported next to the model-free columns)

and, with `--contrast A:B`, per (file, curve):
  level_delta, raw_delta, sign_flip     sign_flip ⇒ the arms disagree about
                                        which is better at the level and at λ=1;
                                        report BOTH columns or the verdict is an
                                        artefact of where λ happened to land.

READ IT AS
----------
`|level_delta| ≪ |raw_delta|` → the change did not move the mean field; it
rescaled/reaimed the condition response. Look at `eff_alignment` and at
`slope_top`'s spread across seeds before claiming anything.
`eff_alignment ≤ 0` with `lambda_argmin = 0` → this arm's condition-dependent
part is worthless-to-harmful on this split; its raw score is decided by the
amplitude of a component that should be zero.
`lambda_argmin > 1` → the fitted deviation from the mean field is too SMALL
(MSE over-smoothing); expanding it helps. Across an N-sweep, λ* crossing 1 is
the sample-limited signature (r2s4-B2 T3-F6: cahn_hilliard 0.767 → 1.117 as
N_fit goes 20 → 320).

Curve discovery is schema-free: the tool walks each JSON and picks up every
object holding a `grid` plus one or more `*_curve` arrays of matching length, so
it works on any card that ships one, whatever the surrounding key names.

USAGE
-----
    source "$PROJECT_ROOT/.venv/bin/activate"
    python tools/shrinkage_curve_anatomy.py \
        --json '<outputs>/r2s4_diag/B2/eval/arms_ext__helmholtz_2d_e200_s*.json' \
        --contrast T0_cond_only:T1_lf_aux --curves test \
        --out /path/anatomy.json
    # skill units instead of nRMSE (uses eval/copylf_baselines.json and the
    # `dataset` key inside each JSON):
    ... --skill

Read-only, numpy only, seconds. Reads shipped JSON only — no data, no model.

Provenance: promoted from `r2s4_diag-B2` mechanism turn 2 (block A /
`curve_anatomy` in `worktrees/r2s4_diag/B2/scratchpad/reanalysis_turn_2.py`,
findings T2-F1/T2-F2) and turn 3's λ*(N) reading (T3-F6).
"""
from __future__ import annotations

import argparse
import glob
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


def curve_anatomy(grid, curve):
    """Decompose f(λ) = mean_i ‖P̄ + λ(P_i − P̄) − y_i‖ / ‖y_i‖."""
    g = np.asarray(grid, float)
    f = np.asarray(curve, float)
    out = {
        "level_lambda0": float(f[0]),
        "raw_lambda1": float(np.interp(1.0, g, f)),
        "min_value": float(f.min()),
        "lambda_argmin": float(g[int(np.argmin(f))]),
        "n_grid": int(g.size),
    }
    if g.size >= 3 and g[-1] > g[-3]:
        out["slope_top"] = float((f[-1] - f[-3]) / (g[-1] - g[-3]))
    A = np.vstack([np.ones_like(g), 2 * g, g ** 2]).T
    coef, *_ = np.linalg.lstsq(A, f ** 2, rcond=None)
    a, b, c = [float(v) for v in coef]
    resid = float(((f ** 2 - A @ coef) ** 2).sum())
    tot = float(((f ** 2 - (f ** 2).mean()) ** 2).sum())
    out["fit_r2"] = float(1 - resid / tot) if tot > 0 else None
    out["eff_a_level2"], out["eff_b_cross"], out["eff_c_fluct2"] = a, b, c
    if a > 0 and c > 0:
        out["eff_fluct_over_level"] = float(np.sqrt(c / a))
        out["eff_alignment"] = float(-b / np.sqrt(a * c))
        out["eff_lambda_opt"] = float(-b / c)
    return out


def find_curves(obj, path=""):
    """Yield (dotted_path, node) for every dict holding `grid` + `*_curve`."""
    if isinstance(obj, dict):
        g = obj.get("grid")
        if isinstance(g, list) and any(
                k.endswith("_curve") and isinstance(v, list) and len(v) == len(g)
                for k, v in obj.items()):
            yield path, obj
        for k, v in obj.items():
            yield from find_curves(v, f"{path}.{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from find_curves(v, f"{path}[{i}]")


def arm_name(dotted):
    parts = [p for p in dotted.split(".") if p]
    if not parts:
        return "<root>"
    if parts[-1].lower() in ("shrinkage", "shrink", "curve", "curves") and len(parts) > 1:
        return parts[-2]
    return parts[-1]


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", required=True, nargs="+",
                    help="result JSON path(s) or glob(s)")
    ap.add_argument("--curves", default="test,inner",
                    help="which `<name>_curve` keys to decompose")
    ap.add_argument("--contrast", default=None,
                    help="A:B arm names — report level/raw deltas (A minus B)")
    ap.add_argument("--skill", action="store_true",
                    help="divide by the dataset's copy-LF reference nRMSE")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    files = []
    for pat in a.json:
        files.extend(sorted(glob.glob(pat)) or ([pat] if Path(pat).exists() else []))
    if not files:
        print("[error] no JSON matched", a.json)
        return 1
    want = [c.strip() for c in a.curves.split(",") if c.strip()]
    baselines = json.load(open(PATHS["eval_dir"] / "copylf_baselines.json")) \
        if a.skill else None

    res = {"_tool": "shrinkage_curve_anatomy", "_files": files,
           "_curves": want, "_units": "skill" if a.skill else "nRMSE",
           "entries": [], "contrast": []}
    print(f"{'file':<34}{'arm':<20}{'curve':<7}{'level':>9}{'raw':>9}"
          f"{'min':>9}{'argmin':>8}{'fluct/lev':>11}{'align':>8}{'r2':>7}")
    for fp in files:
        doc = json.load(open(fp))
        ds = doc.get("dataset") or doc.get("lf_value", {}).get("dataset")
        ref = float(baselines[ds]["test_nrmse"]) if (a.skill and ds in (baselines or {})) else 1.0
        for dotted, node in find_curves(doc):
            for name in want:
                key = f"{name}_curve"
                if not isinstance(node.get(key), list):
                    continue
                an = curve_anatomy(node["grid"], np.asarray(node[key]) / ref)
                entry = {"file": os.path.basename(fp), "path": dotted,
                         "arm": arm_name(dotted), "curve": name,
                         "dataset": ds, "ref_nrmse": ref if a.skill else None,
                         "lambda_star_shipped": node.get("lambda_star"),
                         **an}
                res["entries"].append(entry)
                print(f"{os.path.basename(fp)[:33]:<34}{entry['arm'][:19]:<20}"
                      f"{name:<7}{an['level_lambda0']:>9.4f}{an['raw_lambda1']:>9.4f}"
                      f"{an['min_value']:>9.4f}{an['lambda_argmin']:>8.2f}"
                      f"{an.get('eff_fluct_over_level', float('nan')):>11.3f}"
                      f"{an.get('eff_alignment', float('nan')):>8.3f}"
                      f"{(an['fit_r2'] if an['fit_r2'] is not None else float('nan')):>7.3f}")

    if a.contrast:
        A, B = a.contrast.split(":", 1)
        idx = {(e["file"], e["arm"], e["curve"]): e for e in res["entries"]}
        print(f"\ncontrast {A} minus {B}")
        print(f"{'file':<34}{'curve':<7}{'level_delta':>13}{'raw_delta':>11}"
              f"{'|raw|/|level|':>15}  sign_flip")
        for (fp, arm, cv), e in list(idx.items()):
            if arm != A:
                continue
            other = idx.get((fp, B, cv))
            if other is None:
                continue
            ld = e["level_lambda0"] - other["level_lambda0"]
            rd = e["raw_lambda1"] - other["raw_lambda1"]
            flip = bool(ld * rd < 0)
            row = {"file": fp, "curve": cv, "dataset": e["dataset"],
                   "arm_a": A, "arm_b": B, "level_delta": float(ld),
                   "raw_delta": float(rd), "sign_flip": flip,
                   "alignment_a": e.get("eff_alignment"),
                   "alignment_b": other.get("eff_alignment"),
                   "slope_top_a": e.get("slope_top"),
                   "slope_top_b": other.get("slope_top")}
            res["contrast"].append(row)
            ratio = abs(rd) / abs(ld) if ld != 0 else float("inf")
            print(f"{fp[:33]:<34}{cv:<7}{ld:>13.4f}{rd:>11.4f}{ratio:>15.2f}"
                  f"  {'YES' if flip else '-'}")
        if res["contrast"]:
            lds = [r["level_delta"] for r in res["contrast"]]
            rds = [r["raw_delta"] for r in res["contrast"]]
            res["contrast_summary"] = {
                "n": len(lds), "mean_level_delta": float(np.mean(lds)),
                "mean_raw_delta": float(np.mean(rds)),
                "n_sign_flip": int(sum(r["sign_flip"] for r in res["contrast"])),
                "mean_sign_flip": bool(np.mean(lds) * np.mean(rds) < 0)}
            s = res["contrast_summary"]
            print(f"[summary] mean level delta {s['mean_level_delta']:+.4f} | "
                  f"mean raw delta {s['mean_raw_delta']:+.4f} | "
                  f"sign flips {s['n_sign_flip']}/{s['n']} | "
                  f"mean-level-vs-raw flip {s['mean_sign_flip']}")

    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(res, indent=1))
        print("[wrote]", a.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
