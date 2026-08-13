#!/usr/bin/env python
"""subset_geomean_unit_audit.py — is a panel-geomean delta being read against a
bar calibrated on a DIFFERENT cell subset, and does the verdict survive a change
of denominator?

Provenance: `r3s2_field_reach-B2` mechanism turn 3. That card's headline route
delta was affirmative on the 5-cell panel and 0-of-5 claimable per cell, and its
part-5 reconciliation ("the win survives restriction to the claimable cells,
-1.8464 vs the 0.7624 bar") turned out to be an artefact: the 3-cell geomean was
read against a bar calibrated on 5 cells. In copy-LF units that reads 2.42x the
bar; under ADR r3-0006's film denominator the SAME statement reads 0.35x. The
5-cell verdict, by contrast, is exactly unit-invariant (2.13x in both).

WHY THIS IS A REAL TRAP. The panel score is a geometric mean of per-cell skills,
so its LEVEL depends on which cells are in it. A skill-unit delta therefore is
NOT comparable across cell subsets, and any re-denomination (ADR r3-0006:
`skill_film = skill_copylf * c_ds`) rescales different subsets by different
factors. Per-CELL verdicts are safe — a cell's delta and its `tau_rel` share the
same `c_ds` — but every subset-level number needs this check.

WHAT IT REPORTS
  * per-cell `log(arm/ref)` and each cell's exact SHARE of the panel delta
    (log space is the additive, scale-free unit for a geomean);
  * for every requested subset: the delta and `|delta| / bar` in each unit
    system, and a `UNIT_DEPENDENT` / `UNIT_INVARIANT` verdict;
  * `SUBSET_BAR_MISMATCH` whenever a subset differs from the bar's calibration
    panel, with the exact rescaling factor `geomean(c over subset) /
    geomean(c over panel)`. The calibration panel is read from the bar's own
    anchor file (`--bar-calibration-json`, key `_panel_geomean.panel`) or an
    explicit `--bar-panel` -- NEVER from `--panel`, which is the headline
    panel being decomposed and can itself mismatch the bar (ADR r3-0008: the
    declared-panel comparison blessed a six-cell panel against a five-cell
    bar). With no calibration source every verdict is
    `UNVERIFIED_BAR_CALIBRATION`;
  * optionally, per-cell `|delta| / (1.5 tau_rel)` with an explicit assertion
    that those ratios are unit-invariant.

RUN IT on any card whose headline is a panel/subset geomean delta, and on every
batch-2 card before its numbers are re-expressed in film units.

Input modes (both give the same report):
  (1) `--skills-json FILE` : {"ARM": {"DATASET": [per-seed skills]}}
  (2) `--diag-root DIR --arms A,B --refs ds=v,...` : reads a dotted nRMSE key out
      of per-(dataset, seed) result/diag JSONs and divides by the reference.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np


def geo(v):
    return float(np.exp(np.mean(np.log(np.asarray(v, dtype=float)))))


def dotted(obj, key):
    for k in key.split("."):
        obj = obj[k]
    return obj


def cellset(label, cells):
    """A cell list that may carry a verdict: non-empty, no duplicates.
    An empty or duplicate-bearing list is a hard error — an empty calibration
    list is falsy-but-not-None and would otherwise read OK against an empty
    subset while the console said UNVERIFIED (Codex review, 2026-08-12)."""
    cells = [c.strip() for c in cells if c.strip()]
    if not cells:
        raise SystemExit(f"{label}: empty cell list")
    dupes = sorted({c for c in cells if cells.count(c) > 1})
    if dupes:
        raise SystemExit(f"{label}: duplicate cells {dupes}")
    return cells


def kv(spec):
    out = {}
    for part in str(spec).split(","):
        if part.strip() == "":
            continue
        k, v = part.split("=")
        out[k.strip()] = float(v)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--skills-json", default=None)
    ap.add_argument("--diag-root", default=None)
    ap.add_argument("--diag-pattern", default="diag_{ds}_e200_s{seed}.json")
    ap.add_argument("--nrmse-key", default="arms.{arm}.nrmse")
    ap.add_argument("--arms", default=None, help="ARM,REF (exactly two, in that order)")
    ap.add_argument("--refs", default=None, help="ds=refnrmse,... (mode 2)")
    ap.add_argument("--refs-json", default=None, help="{ds: refnrmse} (mode 2)")
    ap.add_argument("--seeds", default="0,1,2")
    ap.add_argument("--panel", required=True,
                    help="comma-list of the cells of the HEADLINE panel (the "
                         "geomean being decomposed) — not the bar's calibration "
                         "set, which comes from --bar-calibration-json/--bar-panel")
    ap.add_argument("--subset", action="append", default=[],
                    help="NAME=a,b,c — repeatable; the panel is added automatically")
    ap.add_argument("--bar", type=float, required=True,
                    help="the decision bar in the SAME units as --skills (e.g. "
                         "1.5 x the certified panel seed_mce)")
    ap.add_argument("--bar-calibration-json", default=None,
                    help="anchor file the bar came from (e.g. noise_floor.json); "
                         "its _panel_geomean.panel is the set the bar was "
                         "calibrated on")
    ap.add_argument("--bar-panel", default=None,
                    help="comma-list of the cells the BAR was calibrated on, for "
                         "a bar with no anchor file; must agree with "
                         "--bar-calibration-json when both are given")
    ap.add_argument("--denominator-json", default=None,
                    help="ADR r3-0006 film_denominator.json (per-dataset c_ds)")
    ap.add_argument("--tau", default=None, help="ds=tau_rel,... for the per-cell check")
    ap.add_argument("--unit-tol", type=float, default=0.01,
                    help="relative change in |delta|/bar above which a subset is "
                         "reported UNIT_DEPENDENT")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    panel = cellset("--panel", a.panel.split(","))
    seeds = [int(s) for s in a.seeds.split(",") if s.strip()]

    subsets = {"panel": panel}
    for s in a.subset:
        nm, cells = s.split("=")
        if nm in subsets:
            raise SystemExit(
                f"--subset {nm}: name already taken "
                "('panel' is reserved for the declared --panel)")
        subsets[nm] = cellset(f"--subset {nm}", cells.split(","))

    # ── the bar's true calibration set (never the declared --panel) ──────
    bar_panel = None
    if a.bar_calibration_json:
        bar_panel = cellset(
            "--bar-calibration-json _panel_geomean.panel",
            json.load(open(a.bar_calibration_json))["_panel_geomean"]["panel"])
    if a.bar_panel:
        explicit = cellset("--bar-panel", a.bar_panel.split(","))
        if bar_panel is not None and sorted(explicit) != sorted(bar_panel):
            raise SystemExit(
                "--bar-panel disagrees with --bar-calibration-json: "
                f"{sorted(explicit)} vs {sorted(bar_panel)}")
        bar_panel = explicit

    # ── skills ───────────────────────────────────────────────────────────
    if a.skills_json:
        S = json.load(open(a.skills_json))
        arms = list(S.keys())
        if a.arms:
            arms = [s.strip() for s in a.arms.split(",")]
        arm, ref = arms[0], arms[1]
        sk = {(w, ds, i): S[w][ds][i] for w in (arm, ref) for ds in S[w]
              for i in range(len(S[w][ds]))}
        seeds = list(range(len(S[arm][panel[0]])))
    else:
        if not (a.diag_root and a.arms and (a.refs or a.refs_json)):
            raise SystemExit("mode 2 needs --diag-root, --arms and --refs/--refs-json")
        arm, ref = [s.strip() for s in a.arms.split(",")]
        R = kv(a.refs) if a.refs else json.load(open(a.refs_json))
        sk = {}
        for ds in dict.fromkeys(c for cells in subsets.values() for c in cells):
            for i, seed in enumerate(seeds):
                f = Path(a.diag_root) / a.diag_pattern.format(ds=ds, seed=seed)
                obj = json.load(open(f))
                for w in (arm, ref):
                    sk[(w, ds, i)] = dotted(obj, a.nrmse_key.format(arm=w)) / R[ds]

    n_seed = len(seeds)

    c_ds = None
    if a.denominator_json:
        c_ds = {k: v["c_ds"] for k, v in
                json.load(open(a.denominator_json))["datasets"].items()}

    rep = {"_tool": "subset_geomean_unit_audit.py", "_args": vars(a),
           "arm": arm, "ref": ref, "bar": a.bar,
           "bar_calibration_panel": bar_panel,
           "bar_calibration_source": (
               a.bar_calibration_json if a.bar_calibration_json
               else "--bar-panel" if a.bar_panel else None)}

    # ── log-space decomposition of the panel delta ───────────────────────
    logs = {ds: [float(np.log(sk[(arm, ds, i)] / sk[(ref, ds, i)]))
                 for i in range(n_seed)] for ds in panel}
    tot = float(np.mean([np.mean(logs[ds]) for ds in panel]))
    rep["log_space"] = {
        "panel_log_delta_per_cell": tot,
        "per_cell_log_delta": {ds: float(np.mean(logs[ds])) for ds in panel},
        "per_cell_share_of_panel_delta": {
            ds: float(np.mean(logs[ds]) / (len(panel) * tot)) for ds in panel},
        "_note": ("log(arm/ref) is additive over the geomean, so these shares are "
                  "exact and scale-free; they are the only cross-subset-comparable "
                  "form of the delta."),
    }

    # ── per-subset, per-unit-system ──────────────────────────────────────
    gc_panel = geo([c_ds[d] for d in panel]) if c_ds else None
    rep["subsets"] = {}
    for nm, cells in subsets.items():
        a1 = float(np.mean([geo([sk[(arm, d, i)] for d in cells])
                            for i in range(n_seed)]))
        a3 = float(np.mean([geo([sk[(ref, d, i)] for d in cells])
                            for i in range(n_seed)]))
        entry = {"cells": cells, "arm_geomean": a1, "ref_geomean": a3,
                 "delta": a1 - a3, "delta_over_bar": abs(a1 - a3) / a.bar,
                 "log_delta_per_cell": float(
                     np.mean([np.mean([float(np.log(sk[(arm, d, i)] / sk[(ref, d, i)]))
                                       for i in range(n_seed)]) for d in cells]))}
        if c_ds:
            gc = geo([c_ds[d] for d in cells])
            entry["geomean_c_subset"] = gc
            entry["geomean_c_panel"] = gc_panel
            entry["rescale_vs_panel"] = gc / gc_panel
            entry["delta_alt_units"] = (a1 - a3) * gc
            entry["bar_alt_units"] = a.bar * gc_panel
            entry["delta_over_bar_alt_units"] = abs(a1 - a3) * gc / (a.bar * gc_panel)
            rel = abs(entry["delta_over_bar_alt_units"] - entry["delta_over_bar"]) / max(
                entry["delta_over_bar"], 1e-300)
            entry["unit_verdict"] = ("UNIT_INVARIANT" if rel <= a.unit_tol
                                     else "UNIT_DEPENDENT")
            entry["unit_relative_change"] = rel
            entry["crosses_bar_between_unit_systems"] = bool(
                (entry["delta_over_bar"] >= 1.0) != (entry["delta_over_bar_alt_units"] >= 1.0))
        if bar_panel is None:
            entry["bar_calibration_verdict"] = "UNVERIFIED_BAR_CALIBRATION"
        else:
            entry["bar_calibration_verdict"] = (
                "OK" if sorted(cells) == sorted(bar_panel)
                else "SUBSET_BAR_MISMATCH")
            if c_ds and all(d in c_ds for d in bar_panel):
                entry["rescale_vs_bar_calibration"] = (
                    gc / geo([c_ds[d] for d in bar_panel]))
        rep["subsets"][nm] = entry

    # ── per-cell ratios (unit-invariant by construction) ─────────────────
    if a.tau:
        tau = kv(a.tau)
        rep["per_cell"] = {}
        for ds in panel:
            d = float(np.mean([sk[(arm, ds, i)] - sk[(ref, ds, i)]
                               for i in range(n_seed)]))
            e = {"delta": d, "bar_1p5_tau": 1.5 * tau[ds],
                 "delta_over_bar": abs(d) / (1.5 * tau[ds])}
            if c_ds:
                e["delta_alt_units"] = d * c_ds[ds]
                e["bar_alt_units"] = 1.5 * tau[ds] * c_ds[ds]
                e["delta_over_bar_alt_units"] = abs(d * c_ds[ds]) / (
                    1.5 * tau[ds] * c_ds[ds])
                e["unit_verdict"] = ("UNIT_INVARIANT"
                                     if abs(e["delta_over_bar_alt_units"]
                                            - e["delta_over_bar"]) <= 1e-9
                                     else "UNIT_DEPENDENT")
            rep["per_cell"][ds] = e

    # ── console ──────────────────────────────────────────────────────────
    print(f"arm={arm}  ref={ref}  bar={a.bar}  seeds={n_seed}")
    print("bar calibration: " + (",".join(bar_panel) if bar_panel else
                                 "UNVERIFIED (pass --bar-calibration-json or --bar-panel)"))
    print("\nper-cell share of the panel delta (log space):")
    for ds in panel:
        print(f"  {ds:28s} log(arm/ref) {rep['log_space']['per_cell_log_delta'][ds]:+.5f}"
              f"   share {100*rep['log_space']['per_cell_share_of_panel_delta'][ds]:6.1f}%")
    print(f"  panel log delta per cell = {tot:+.5f}")
    print("\nsubsets:")
    for nm, e in rep["subsets"].items():
        line = (f"  {nm:18s} delta {e['delta']:+9.4f}  |delta|/bar "
                f"{e['delta_over_bar']:5.2f}x  logdelta/cell "
                f"{e['log_delta_per_cell']:+.5f}  [{e['bar_calibration_verdict']}]")
        if c_ds:
            line += (f"\n    {'':16s} ALT UNITS delta {e['delta_alt_units']:+9.5f}  "
                     f"|delta|/bar {e['delta_over_bar_alt_units']:5.2f}x  "
                     f"rescale vs panel {e['rescale_vs_panel']:.4f}  "
                     f"-> {e['unit_verdict']}"
                     + ("  *** VERDICT FLIPS ACROSS UNIT SYSTEMS ***"
                        if e["crosses_bar_between_unit_systems"] else ""))
        print(line)
    if a.tau:
        print("\nper-cell (unit-invariant by construction):")
        for ds, e in rep["per_cell"].items():
            print(f"  {ds:28s} delta {e['delta']:+9.4f}  |delta|/(1.5 tau) "
                  f"{e['delta_over_bar']:5.2f}x"
                  + (f"  [{e['unit_verdict']}]" if c_ds else ""))
    if a.out:
        Path(a.out).write_text(json.dumps(rep, indent=1))
        print("\nwrote", a.out)


if __name__ == "__main__":
    main()
