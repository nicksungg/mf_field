#!/usr/bin/env python
"""paired_arm_displacement.py -- did my change move the learned FUNCTION, and toward the truth?

Promoted from `worktrees/s5_tuning/B2/scratchpad/reanalysis_turn_2.py` (block B) +
`reanalysis_turn_3.py` (block B) + `reanalysis_turn_3b.py`; provenance card
`experiment_cards/s5_tuning/batch_2/B2.json` part 6, findings F3, F8, F9, F10, F13, F15.

WHY THIS EXISTS
---------------
A card's score delta answers "did the number move?". It does not answer "did the model
change?", and on the round's panel those two are nearly uncorrelated:

* `ifc_poisson` -- the only claimable win s5-B2 recorded -- came from a **3.5 %** move of
  the learned function.
* `sharp__phase_field_crystal_2d` moved its function **42.5 %**, and *toward the truth*
  (cos with the control's error 0.539, 95 % of samples improving in direction), for a
  2.2 % nRMSE change that is 4.6x inside its floor.
* `sharp__allen_cahn_2d` moved 2.6 % with cos **-0.013** and 46 % of samples improving --
  a coin-flip re-roll, i.e. genuinely inert.

Reading only the skill delta, all three look like "no effect". They are three different
situations, and only this decomposition separates them:
inert knob / knob acts but the dataset cannot cash it / knob acts and pays.
It also splits a score gain into the part any oracle per-sample rescale would have given
for free (AMPLITUDE) and the part that is new field content -- on `ext__helmholtz_2d`
s5-B2's headline 3.40x nRMSE ratio was **91.6 % amplitude**, 1.108x real.

WHAT IT REPORTS (per dataset, from two arms' `preds_test.npz`)
-------------------------------------------------------------
| key | meaning |
|---|---|
| `pred_displacement_rel` | `\|\|pred_arm - pred_ctrl\|\| / \|\|pred_ctrl\|\|` -- how far the function moved |
| `pred_cosine_arm_vs_control` | 1 == same function |
| `cos_displacement_vs_control_error_{mean,median}` | did it move DOWN the error? (+1 = straight down) |
| `random_cos_baseline` | `sqrt(2/(pi n))` -- what an unrelated re-roll would score |
| `frac_samples_moved_toward_truth` | ~0.5 == re-roll, ~1.0 == systematic |
| `optimal_step_along_displacement_median` | how far along `d` the best point is (1.0 == the arm stopped exactly there) |
| `displacement_dc_share` / `_pattern_share` | did the LEVEL or the PATTERN move? |
| `amplitude_share_of_log_gain` | fraction of the log nRMSE gain an oracle per-sample rescale would already give |
| `nrmse_{control,arm}`, `nrmse_after_optimal_rescale_*`, `corr_demeaned_*`, `pred_rms_over_target_rms_*` | the paired anatomy |
| `verdict` | `INERT` / `MOVED_NOT_TOWARD_TRUTH` / `MOVED_TOWARD_TRUTH_UNCASHED` / `MOVED_AND_PAID` |

HOW TO READ IT
--------------
* `INERT` -> the knob did not change the function; a null result is about the KNOB.
* `MOVED_NOT_TOWARD_TRUTH` -> the knob re-rolled non-informative content; suspect a flat
  basin, and do not conclude anything about the knob's direction.
* `MOVED_TOWARD_TRUTH_UNCASHED` -> the knob helps but the dataset's headroom (or the
  round's floor) is too small to show it; a null result here is about the DATASET, and the
  knob may be worth carrying into a family that can cash it.
* `MOVED_AND_PAID` -> read `amplitude_share_of_log_gain` before claiming pattern: a high
  share means the win is calibration, which an oracle rescale would have given for free.
* Cross-check `corr_demeaned` and the level-only ceiling with `tools/dc_pattern_split.py`.

INVOKE
------
  source "$PROJECT_ROOT/.venv/bin/activate"
  # explicit pair of npz files
  python tools/paired_arm_displacement.py --out disp.json \
      --pair ifc_poisson=/abs/arm/preds_test.npz,/abs/control/preds_test.npz
  # ... repeatable; or point at two directories holding ckpt_<ds>_*/**/preds_test.npz
  python tools/paired_arm_displacement.py --datasets PANEL --out disp.json \
      --arm_root  /abs/outputs/<stream>/B2/eval/results/<arm>/<family> \
      --ctrl_root /abs/control/dir [--toward_truth_cos 0.1] [--inert_disp 0.05]

Both npz files must carry `pred` and `target` (the round's `preds_test.npz` contract).
Targets are asserted equal; if one side has fewer samples (a paired SUBSET regen) the
other is truncated to match and `paired_subset` is set. Pure numpy, CPU, seconds.
All nRMSE values come from `round1/eval/nrmse.py`; the `nrmse_def_hash` is echoed.
"""
from __future__ import annotations

import argparse
import glob
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
R1 = HERE.parent
sys.path.insert(0, str(R1 / "eval"))
import nrmse as NR  # noqa: E402
from panel_data import load_config  # noqa: E402


def _resolve(names: str):
    if names in ("PANEL", "GUARD"):
        cfg = load_config()
        return list(cfg["panel"] if names == "PANEL" else cfg["guard_set"])
    return [d for d in names.split(",") if d]


def _find(root, ds):
    hits = sorted(glob.glob(str(pathlib.Path(root) / f"ckpt_{ds}*" / "**" / "preds_test.npz"),
                            recursive=True))
    if not hits:
        raise FileNotFoundError(f"no ckpt_{ds}*/**/preds_test.npz under {root}")
    return hits[0]


def _anatomy(P, T):
    den = np.linalg.norm(T, axis=1)
    rel = np.linalg.norm(P - T, axis=1) / den
    pm, tm = P.mean(axis=1), T.mean(axis=1)
    Pd, Td = P - pm[:, None], T - tm[:, None]
    corr = ((Pd * Td).sum(axis=1)
            / (np.linalg.norm(Pd, axis=1) * np.linalg.norm(Td, axis=1) + 1e-30))
    alpha = (P * T).sum(axis=1) / ((P ** 2).sum(axis=1) + 1e-30)
    rel_a = np.linalg.norm(alpha[:, None] * P - T, axis=1) / den
    return {"nrmse": float(rel.mean()), "corr_demeaned": float(corr.mean()),
            "nrmse_after_optimal_rescale": float(rel_a.mean()),
            "alpha_median": float(np.median(alpha)),
            "pred_rms_over_target_rms": float(
                np.sqrt((P ** 2).mean()) / max(np.sqrt((T ** 2).mean()), 1e-300))}


def one(arm_npz, ctrl_npz, toward_cos, inert_disp, paid_ratio):
    a, c = np.load(arm_npz), np.load(ctrl_npz)
    Pa, Ta = np.asarray(a["pred"], np.float64), np.asarray(a["target"], np.float64)
    Pc, Tc = np.asarray(c["pred"], np.float64), np.asarray(c["target"], np.float64)
    subset = Pa.shape[0] != Pc.shape[0]
    n = min(Pa.shape[0], Pc.shape[0])
    Pa, Ta, Pc, Tc = Pa[:n], Ta[:n], Pc[:n], Tc[:n]
    seam = float(np.abs(Ta - Tc).max() / max(np.abs(Tc).max(), 1e-300))
    if seam > 1e-9:
        return {"error": f"target seam mismatch (rel {seam:.3e}) -- not a paired comparison"}

    d = Pa - Pc          # displacement of the learned function
    e = Tc - Pc          # the control's own error (the direction "toward the truth")
    ncell = Tc.shape[1]
    cos = ((d * e).sum(axis=1)
           / (np.linalg.norm(d, axis=1) * np.linalg.norm(e, axis=1) + 1e-30))
    step = (d * e).sum(axis=1) / ((d ** 2).sum(axis=1) + 1e-30)
    d_dc = d.mean(axis=1)
    d_pat = d - d_dc[:, None]
    A, C = _anatomy(Pa, Tc), _anatomy(Pc, Tc)
    ratio = C["nrmse"] / max(A["nrmse"], 1e-300)
    ratio_a = C["nrmse_after_optimal_rescale"] / max(A["nrmse_after_optimal_rescale"], 1e-300)
    disp = float(np.linalg.norm(d) / max(np.linalg.norm(Pc), 1e-300))
    out = {
        "arm_npz": str(arm_npz), "ctrl_npz": str(ctrl_npz),
        "n_test_used": int(n), "n_cells": int(ncell), "paired_subset": bool(subset),
        "target_seam_rel_max": seam,
        "pred_displacement_rel": disp,
        "pred_displacement_over_target_norm": float(
            np.linalg.norm(d) / max(np.linalg.norm(Tc), 1e-300)),
        "pred_cosine_arm_vs_control": float(
            (Pa * Pc).sum() / max(np.linalg.norm(Pa) * np.linalg.norm(Pc), 1e-300)),
        "random_cos_baseline": float(np.sqrt(2.0 / (np.pi * ncell))),
        "cos_displacement_vs_control_error_mean": float(cos.mean()),
        "cos_displacement_vs_control_error_median": float(np.median(cos)),
        "frac_samples_moved_toward_truth": float((cos > 0).mean()),
        "optimal_step_along_displacement_median": float(np.median(step)),
        "displacement_over_control_error_norm": float(
            np.linalg.norm(d) / max(np.linalg.norm(e), 1e-300)),
        "displacement_dc_share": float(((d_dc ** 2) * ncell).sum()
                                       / max((d ** 2).sum(), 1e-300)),
        "displacement_pattern_share": float((d_pat ** 2).sum() / max((d ** 2).sum(), 1e-300)),
        "nrmse_control_round_metric": NR.nrmse(Pc, Tc),
        "nrmse_arm_round_metric": NR.nrmse(Pa, Tc),
        "nrmse_ratio_control_over_arm": ratio,
        "nrmse_ratio_after_optimal_rescale": ratio_a,
        "amplitude_share_of_log_gain": (float((np.log(ratio) - np.log(ratio_a)) / np.log(ratio))
                                        if abs(np.log(max(ratio, 1e-300))) > 1e-6 else None),
        "arm": A, "control": C,
    }
    moved = disp > inert_disp
    toward = out["cos_displacement_vs_control_error_mean"] > toward_cos
    paid = ratio > paid_ratio
    out["verdict"] = ("MOVED_AND_PAID" if paid else
                      "INERT" if not moved else
                      "MOVED_NOT_TOWARD_TRUTH" if not toward else
                      "MOVED_TOWARD_TRUTH_UNCASHED")
    out["verdict_note"] = (f"'paid' is the crude threshold nRMSE_ctrl/nRMSE_arm > "
                           f"{paid_ratio} -- the real arbiter is the dataset's own "
                           "min_claimable_effect in state/noise_floor.json.")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--pair", action="append", default=[],
                    help="name=ARM_NPZ,CTRL_NPZ (repeatable)")
    ap.add_argument("--datasets", help="PANEL | GUARD | comma list (needs --arm_root/--ctrl_root)")
    ap.add_argument("--arm_root")
    ap.add_argument("--ctrl_root")
    ap.add_argument("--toward_truth_cos", type=float, default=0.1)
    ap.add_argument("--inert_disp", type=float, default=0.05)
    ap.add_argument("--paid_ratio", type=float, default=1.10,
                    help="nRMSE_ctrl/nRMSE_arm above which the move is called PAID; the dataset's own min_claimable_effect is the real arbiter")
    a = ap.parse_args()

    jobs = []
    for spec in a.pair:
        name, paths = spec.split("=", 1)
        arm, ctrl = paths.split(",", 1)
        jobs.append((name, arm, ctrl))
    if a.datasets:
        if not (a.arm_root and a.ctrl_root):
            ap.error("--datasets needs --arm_root and --ctrl_root")
        for ds in _resolve(a.datasets):
            try:
                jobs.append((ds, _find(a.arm_root, ds), _find(a.ctrl_root, ds)))
            except FileNotFoundError as exc:
                jobs.append((ds, None, str(exc)))
    if not jobs:
        ap.error("nothing to do: pass --pair and/or --datasets")

    out = {"tool": "paired_arm_displacement.py", "nrmse_def_hash": NR.NRMSE_DEF_HASH,
           "thresholds": {"toward_truth_cos": a.toward_truth_cos,
                          "inert_disp": a.inert_disp,
                          "paid_ratio": a.paid_ratio},
           "datasets": {}}
    for name, arm, ctrl in jobs:
        if arm is None:
            out["datasets"][name] = {"error": ctrl}
            continue
        try:
            out["datasets"][name] = one(arm, ctrl, a.toward_truth_cos,
                                        a.inert_disp, a.paid_ratio)
        except Exception as exc:                     # noqa: BLE001
            out["datasets"][name] = {"error": f"{type(exc).__name__}: {exc}"}
    pathlib.Path(a.out).write_text(json.dumps(out, indent=1))
    for ds, r in out["datasets"].items():
        if "error" in r:
            print(f"{ds:34s} ERROR {r['error']}")
            continue
        print(f"{ds:34s} disp={r['pred_displacement_rel']:6.3f} "
              f"cos={r['cos_displacement_vs_control_error_mean']:+6.3f} "
              f"(rand {r['random_cos_baseline']:.4f}) "
              f"toward={r['frac_samples_moved_toward_truth']:.2f} "
              f"nRMSE {r['nrmse_control_round_metric']:.5f}->{r['nrmse_arm_round_metric']:.5f}  "
              f"{r['verdict']}")
    print("WROTE", a.out)


if __name__ == "__main__":
    main()
