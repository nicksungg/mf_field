#!/usr/bin/env python
"""Can a DIMENSIONLESS eligibility threshold be stated in this benchmark's claim units?

WHAT THIS ANSWERS
-----------------
Rules of the shape *"if the relative error reduction available is below X, the
stage is not worth building"* (coherence eligibility gates, futility thresholds,
trust gates, "value-add <= 0.08%" calibrations) are stated in a DIMENSIONLESS
unit: fraction of the arm's own error. The round's claim currency is different —
skill = nRMSE / copy-LF reference, and a claim only exists above the dataset's
certified `min_claimable_effect` (mce). Those two units are not proportional:
the conversion factor is `raw_nrmse / copylf_ref / mce`, which varies by orders
of magnitude across a panel. A threshold that looks conservative in relative
terms can therefore be hundreds of times coarser than what the benchmark can
resolve, and inconsistent between datasets by a large factor.

This tool does that conversion and the decision-cost accounting, for ANY rule,
from a small arms table. Per dataset it reports:

  * `decision_cost_skill_units`  — what OBEYING the rule costs (or saves):
        (nrmse of the arm the rule selects  -  nrmse of the arm it rejects) / ref
    and `decision_cost_over_mce`, the same in units of certified resolvability;
  * `threshold_in_skill_units`   — the dimensionless threshold priced against the
    dataset's own raw error: `threshold * raw_nrmse / ref`, and
    `threshold_over_mce`: how many minimum claimable effects the gate discards
    in one step;
  * `realised_relative_gain`     — the gain actually available, `(raw-improved)/raw`,
    and `realised_over_calibration`: how far it exceeds the number the rule's
    threshold was calibrated on;
  * panel-level `spread`: max/min of `threshold_over_mce` — the factor by which
    ONE dimensionless number means different things on different datasets.

VERDICTS (panel level, all thresholds configurable)
  `EXPRESSIBLE`        — threshold_over_mce in [1/`--coarse_factor`, `--coarse_factor`]
                         on every dataset and spread <= `--spread_factor`: the
                         dimensionless gate is a faithful proxy for the claim unit.
  `COARSE`             — threshold_over_mce > `--coarse_factor` somewhere: the gate
                         discards effects the benchmark can certify.
  `PANEL_INCONSISTENT` — spread > `--spread_factor`: the same number is a
                         different decision on different datasets.
  `MISCALIBRATED`      — some dataset has realised_over_calibration >
                         `--calibration_factor`: the rule's own calibration is
                         contradicted at its own threshold.
(Multiple verdicts can fire; all firing ones are listed.)

READ IT AS
----------
`COARSE` or `PANEL_INCONSISTENT` -> the rule cannot be exported as an ELIGIBILITY
GATE; keep it as a DIRECTIONAL predictor and price eligibility in skill units per
dataset instead. A large `decision_cost_over_mce` is the strongest form: obeying
the rule as written throws away value the round would have certified as a claim.
`MISCALIBRATED` usually means the calibration used a FROZEN component where the
decision applies to a REFIT one — i.e. the rule measured transferability, not
attainability.

INPUT (`--arms`, a JSON file)
-----------------------------
```json
{"sharp__allen_cahn_2d": {"raw_nrmse": 0.34414, "improved_nrmse": 0.30288,
                          "rule_selected_nrmse": 0.34414, "rejected_nrmse": 0.30288,
                          "statistic": 0.3508}}
```
`raw_nrmse` is the denominator the dimensionless threshold is expressed against
(the arm the rule inspects). `improved_nrmse` is what the gated stage actually
achieves. `rule_selected_nrmse` / `rejected_nrmse` are the two arms the DECISION
picks between (default: rule_selected = raw, rejected = improved). `statistic` is
optional (the rule's own statistic value, carried through for plotting).
`--copylf_json` supplies the per-dataset skill reference, `--noise_floor_json`
the certified `min_claimable_effect`; both default to this round's.

PROVENANCE
----------
`worktrees/r2s2_stacked/B2/scratchpad/reanalysis_turn_3b.py`; card
`experiment_cards/r2s2_stacked/batch_2/B2.json` part 6, findings T3/F3.7-F3.9
and interpretation H-RULE-UNITS.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROUND = TOOLS.parent


def build_parser():
    ap = argparse.ArgumentParser(
        description="price a dimensionless eligibility threshold in skill units")
    ap.add_argument("--arms", required=True,
                    help="JSON: dataset -> {raw_nrmse, improved_nrmse, "
                         "[rule_selected_nrmse, rejected_nrmse, statistic]}")
    ap.add_argument("--threshold_relative_gain", type=float, required=True,
                    help="the rule's dimensionless floor, e.g. 0.05 = 5%% relative "
                         "error reduction")
    ap.add_argument("--out", required=True)
    ap.add_argument("--rule_name", default="unnamed_rule")
    ap.add_argument("--calibration_relative_gain", type=float, default=None,
                    help="the relative value-add the rule's threshold was "
                         "calibrated on (e.g. 0.0008)")
    ap.add_argument("--coarse_factor", type=float, default=3.0,
                    help="threshold_over_mce above this -> COARSE (default 3)")
    ap.add_argument("--spread_factor", type=float, default=3.0,
                    help="max/min threshold_over_mce above this -> "
                         "PANEL_INCONSISTENT (default 3)")
    ap.add_argument("--calibration_factor", type=float, default=3.0,
                    help="realised/calibration above this -> MISCALIBRATED")
    ap.add_argument("--copylf_json", default=str(ROUND / "eval" / "copylf_baselines.json"))
    ap.add_argument("--noise_floor_json", default=str(ROUND / "state" / "noise_floor.json"))
    return ap


def main():
    args = build_parser().parse_args()
    arms = json.loads(Path(args.arms).read_text())
    copylf = json.loads(Path(args.copylf_json).read_text())
    nf = json.loads(Path(args.noise_floor_json).read_text())

    out = {"_what": "relative-gain vs skill-units decision-cost audit",
           "_tool": "tools/relative_gain_units_audit.py",
           "_rule": {"name": args.rule_name,
                     "threshold_relative_gain": args.threshold_relative_gain,
                     "calibration_relative_gain": args.calibration_relative_gain},
           "_args": vars(args),
           "datasets": {}}

    for name, a in arms.items():
        ref = float(copylf[name]["test_nrmse"])
        mce = float(nf[name]["min_claimable_effect"])
        raw = float(a["raw_nrmse"])
        imp = float(a["improved_nrmse"])
        sel = float(a.get("rule_selected_nrmse", raw))
        rej = float(a.get("rejected_nrmse", imp))
        thr_skill = args.threshold_relative_gain * raw / ref
        realised = (raw - imp) / raw if raw else float("nan")
        rec = {
            "skill_units_per_nrmse": 1.0 / ref,
            "copylf_ref_nrmse": ref,
            "min_claimable_effect": mce,
            "statistic": a.get("statistic"),
            "nrmse": {"raw": raw, "improved": imp,
                      "rule_selected": sel, "rejected": rej},
            "decision_cost_skill_units": (sel - rej) / ref,
            "decision_cost_over_mce": ((sel - rej) / ref) / mce,
            "threshold_in_skill_units": thr_skill,
            "threshold_over_mce": thr_skill / mce,
            "realised_relative_gain": realised,
            "realised_gain_skill_units": (raw - imp) / ref,
            "realised_gain_over_mce": ((raw - imp) / ref) / mce,
        }
        if args.calibration_relative_gain:
            rec["realised_over_calibration"] = realised / args.calibration_relative_gain
        out["datasets"][name] = rec
        print(f"{name:34s} thr {args.threshold_relative_gain:g} = "
              f"{thr_skill:8.3f} skill units = {rec['threshold_over_mce']:8.1f}x mce | "
              f"realised gain {100*realised:6.2f}% = "
              f"{rec['realised_gain_over_mce']:7.1f}x mce | decision cost "
              f"{rec['decision_cost_skill_units']:8.3f} skill units = "
              f"{rec['decision_cost_over_mce']:7.1f}x mce", flush=True)

    ratios = [d["threshold_over_mce"] for d in out["datasets"].values()]
    spread = max(ratios) / min(ratios) if ratios and min(ratios) > 0 else float("inf")
    verdicts = []
    if any(r > args.coarse_factor for r in ratios):
        verdicts.append("COARSE")
    if spread > args.spread_factor:
        verdicts.append("PANEL_INCONSISTENT")
    if args.calibration_relative_gain and any(
            d.get("realised_over_calibration", 0) > args.calibration_factor
            for d in out["datasets"].values()):
        verdicts.append("MISCALIBRATED")
    if not verdicts:
        verdicts = ["EXPRESSIBLE"]
    out["panel"] = {
        "threshold_over_mce_min": min(ratios) if ratios else None,
        "threshold_over_mce_max": max(ratios) if ratios else None,
        "spread_factor": spread,
        "max_decision_cost_over_mce": max(
            d["decision_cost_over_mce"] for d in out["datasets"].values()),
        "verdicts": verdicts,
        "note": ("EXPRESSIBLE means the dimensionless gate is a faithful proxy "
                 "for the claim unit on this panel; anything else means "
                 "eligibility must be priced in skill units per dataset"),
    }
    print(f"\npanel: threshold/mce {out['panel']['threshold_over_mce_min']:.1f} .. "
          f"{out['panel']['threshold_over_mce_max']:.1f} (spread {spread:.1f}x), "
          f"max decision cost {out['panel']['max_decision_cost_over_mce']:.1f}x mce "
          f"-> {' + '.join(verdicts)}")
    Path(args.out).write_text(json.dumps(out, indent=2, sort_keys=True))
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
