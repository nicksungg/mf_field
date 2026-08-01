#!/usr/bin/env python
"""selection_set_vs_window_audit.py — does a pre-registered selection rule use the
SET its own diagnostic identifies, or only that set's CARDINALITY?

A very common shape for a training-free selection stage is:

    1. compute a per-component statistic on the train split (per-POD-mode
       out-of-fold R^2, per-band SNR, per-channel gain, ...)
    2. count how many components clear a threshold tau        -> r_sel
    3. fit the model on the LEADING r_sel components

Steps 1-2 are sound.  Step 3 silently replaces the identified SET
`{i : stat_i > tau}` by the leading WINDOW `{0 .. r_sel-1}`.  The two coincide
only when the identified components are the leading ones.  Under an
ENERGY-ordered basis (POD/SVD) they systematically do NOT coincide whenever the
predictable content is low-energy — e.g. a condition-predictable spatial mean
carrying 0.45 % of basis energy lands at mode 12 and is discarded, while two
pure-noise modes are bought.  The failure is invisible in every summary the rule
reports, because the rule reports one number (`r_sel`).

This tool reads the shipped selection diagnostics, reconstructs SET and WINDOW,
and prices the mismatch in units of the rule's OWN statistic (and, if the card
ships per-component energies, in energy share).  It is a DETECTOR: the repair
(refit on the SET and rescore) needs the family's own code and stays in the
experiment's scratchpad.

Read-only over shipped eval JSONs; no data, no training, runs in <1 s.

INPUT SCHEMA (dotted key paths, all CLI-overridable; --auto falls back to a
schema-free walk for any dict holding a numeric list whose key contains
--stat_name)
    <diag>.dataset                              dataset name
    <diag>.selection_stage.rank.mode_r2_oof     per-component statistic (list)
    <diag>.selection_stage.rank.rank_tau        threshold tau
    <diag>.selection_stage.rank.r_sel           the count the rule shipped
    <diag>.selection_stage.selected_form        (optional) the form actually fitted

Provenance: r2s1_direct-B2 mechanism turn 1
(worktrees/r2s1_direct/B2/scratchpad/reanalysis_turn_1.py SET-vs-WINDOW audit +
reanalysis_turn_1b.py cross-form check).
"""
from __future__ import annotations

import argparse
import glob as globmod
import json
import os
import sys


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


def walk_for_stat(obj, stat_name):
    """Schema-free fallback: first numeric list whose key contains stat_name."""
    stack = [obj]
    while stack:
        cur = stack.pop(0)
        if isinstance(cur, dict):
            for k, v in cur.items():
                if (stat_name in k and isinstance(v, list) and len(v) >= 2
                        and all(isinstance(x, (int, float)) for x in v)):
                    return v, cur
                if isinstance(v, (dict, list)):
                    stack.append(v)
        elif isinstance(cur, list):
            stack.extend(x for x in cur if isinstance(x, (dict, list)))
    return None, None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--diag", nargs="+", required=True,
                    help="shipped diagnostic JSON path(s) or glob(s)")
    ap.add_argument("--stat_key", default="selection_stage.rank.mode_r2_oof",
                    help="dotted path to the per-component selection statistic (list)")
    ap.add_argument("--tau_key", default="selection_stage.rank.rank_tau")
    ap.add_argument("--count_key", default="selection_stage.rank.r_sel",
                    help="dotted path to the count the rule shipped (the WINDOW size)")
    ap.add_argument("--energy_key", default=None,
                    help="optional dotted path to a per-component energy share list")
    ap.add_argument("--form_key", default="selection_stage.selected_form",
                    help="optional dotted path to the form/basis actually fitted")
    ap.add_argument("--stat_form", default=None,
                    help="the form/basis the STATISTIC was computed on (read off the "
                         "code). If it differs from --form_key's value the tool raises "
                         "FORM_MISMATCH: the indices are transferred across "
                         "incommensurable decompositions")
    ap.add_argument("--tau", type=float, default=None,
                    help="override the threshold (default: read from --tau_key)")
    ap.add_argument("--dataset_key", default="dataset")
    ap.add_argument("--auto", action="store_true",
                    help="if --stat_key misses, walk the JSON for a list whose key "
                         "contains --stat_name")
    ap.add_argument("--stat_name", default="r2_oof")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)

    out = {"tool": "selection_set_vs_window_audit.py",
           "question": "does the rule fit the identified SET {i: stat_i > tau} or "
                       "the leading WINDOW {0..r_sel-1}?",
           "datasets": {}}
    any_defect = False

    for path in resolve_inputs(args.diag):
        d = load_json(path)
        ds = d.get(args.dataset_key, os.path.basename(path))
        stat = dig(d, args.stat_key)
        holder = None
        if stat is None and args.auto:
            stat, holder = walk_for_stat(d, args.stat_name)
        if stat is None:
            print("WARN %s: no statistic at '%s' (try --auto), skipped" % (path, args.stat_key))
            continue
        tau = args.tau if args.tau is not None else dig(d, args.tau_key)
        if tau is None and holder:
            tau = next((v for k, v in holder.items()
                        if "tau" in k and isinstance(v, (int, float))), None)
        r_sel = dig(d, args.count_key)
        if r_sel is None and holder:
            r_sel = next((v for k, v in holder.items()
                          if k.startswith("r_sel") and isinstance(v, int)), None)
        if tau is None or r_sel is None:
            print("WARN %s: missing tau (%s) or count (%s), skipped"
                  % (path, args.tau_key, args.count_key))
            continue

        stat = [float(x) for x in stat]
        sel_set = [i for i, v in enumerate(stat) if v > tau]
        window = list(range(int(r_sel)))
        missed = [i for i in sel_set if i not in window]        # identifiable, not fitted
        spurious = [i for i in window if i not in sel_set]      # fitted, not identifiable
        match = (sorted(sel_set) == sorted(window))
        energy = dig(d, args.energy_key) if args.energy_key else None

        rec = {
            "source": path,
            "n_components_scanned": len(stat),
            "tau": float(tau),
            "r_sel_shipped": int(r_sel),
            "identifiable_set": sel_set,
            "fitted_window": window,
            "set_equals_window": bool(match),
            "n_identifiable": len(sel_set),
            "missed_identifiable": [{"index": i, "stat": stat[i]} for i in missed],
            "spurious_fitted": [{"index": i, "stat": stat[i]} for i in spurious],
            "stat_mass_missed": float(sum(stat[i] for i in missed)),
            "stat_mass_spurious": float(sum(stat[i] for i in spurious)),
            "stat_mass_fitted_window": float(sum(stat[i] for i in window)),
            "stat_mass_identifiable_set": float(sum(stat[i] for i in sel_set)),
            "max_identifiable_index": (max(sel_set) if sel_set else None),
            "contiguous_from_zero": bool(sel_set == list(range(len(sel_set)))),
            "set_rule_would_fit": sorted(sel_set),
            "verdict": "SET_EQUALS_WINDOW" if match else "ARITY_DEFECT",
        }
        if energy and len(energy) >= max(window + sel_set + [0]) + 1:
            rec["energy_share_missed"] = float(sum(float(energy[i]) for i in missed))
            rec["energy_share_spurious"] = float(sum(float(energy[i]) for i in spurious))
        # cross-form check (the second, independent defect class)
        fitted_form = dig(d, args.form_key) if args.form_key else None
        rec["fitted_form"] = fitted_form
        rec["stat_form_declared"] = args.stat_form
        if args.stat_form and fitted_form and args.stat_form != fitted_form:
            rec["verdict"] += "+FORM_MISMATCH"
            rec["form_mismatch_note"] = (
                "statistic measured on form '%s' but the model is fitted on form '%s': "
                "component INDICES are transferred across incommensurable decompositions"
                % (args.stat_form, fitted_form))
        if not match:
            any_defect = True
        out["datasets"][ds] = rec

    # severity ranking: how much of the rule's own statistic the window throws away
    ranked = sorted(out["datasets"].items(),
                    key=lambda kv: -kv[1]["stat_mass_missed"])
    out["severity_ranking"] = [{"dataset": k, "stat_mass_missed": v["stat_mass_missed"],
                                "verdict": v["verdict"]} for k, v in ranked]
    out["any_arity_defect"] = any_defect

    print("\n=== SET vs WINDOW (rule statistic: %s, tau from %s) ===" % (args.stat_key, args.tau_key))
    hdr = "  %-32s %-6s %-26s %-16s %s" % ("dataset", "r_sel", "identifiable SET", "fitted WINDOW", "verdict")
    print(hdr)
    for ds, r in out["datasets"].items():
        print("  %-32s %-6d %-26s %-16s %s"
              % (ds, r["r_sel_shipped"],
                 str(r["identifiable_set"])[:26], str(r["fitted_window"])[:16], r["verdict"]))
    for ds, r in out["datasets"].items():
        if r["set_equals_window"]:
            continue
        print("\n  %s" % ds)
        if r["missed_identifiable"]:
            print("    identifiable but NOT fitted: " +
                  ", ".join("#%d (stat %+.4f)" % (m["index"], m["stat"])
                            for m in r["missed_identifiable"]))
        if r["spurious_fitted"]:
            print("    fitted but NOT identifiable: " +
                  ", ".join("#%d (stat %+.4f)" % (m["index"], m["stat"])
                            for m in r["spurious_fitted"]))
        print("    stat mass  window %.4f  vs  set %.4f   (missed %.4f, spurious %.4f)"
              % (r["stat_mass_fitted_window"], r["stat_mass_identifiable_set"],
                 r["stat_mass_missed"], r["stat_mass_spurious"]))
        if "form_mismatch_note" in r:
            print("    %s" % r["form_mismatch_note"])
        print("    a SET-indexed rule would fit: %s" % r["set_rule_would_fit"])

    if args.out:
        with open(args.out, "w") as fh:
            json.dump(out, fh, indent=1)
        print("\nwrote %s" % args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
