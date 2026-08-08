#!/usr/bin/env python
"""Detect result JSONs that were produced WITHOUT training (stale-checkpoint re-scores).

Provenance: promoted from r3s3_lf_value-B1 mechanism turn 2
(`worktrees/r3s3_lf_value/B1/scratchpad/reanalysis_turn_2.py` sub-probe A,
`reanalysis_turn_2_results.md` sec. A). It found that the round-3 launch
anchor's ifc_poisson cell for `r2s3_lf_train_signal-B3` was a PRE-repair model
evaluated on POST-repair data: the ADR-mandated re-score ran, but the
Model-Family-Contract requirement to resume from `<ckpt_dir>/last.pt` made it a
zero-step no-op, so the scored weights had never seen the scored data.

This defect class is invisible to every seam check the round already runs
(nrmse_def_hash, copylf_def_hash and floor seams all pass, because the
REFERENCES are recomputed live while only the WEIGHTS are stale). The
detectable signature is:

  * `<ckpt_dir>/last.pt` mtime strictly older than the result JSON's mtime
    (a real training run rewrites the checkpoint), and/or
  * `resumed_from_step` equal to the total step budget, and/or
  * `train_seconds` collapsed to a few seconds, and/or
  * the leg's own reported fit on its training rows being far worse than its
    reported training loss implies.

Any dataset swap, test-split trim or ladder repair between a checkpoint and a
re-score is enough to trigger it. Run this after ANY re-score campaign.

Convention assumed (factory Model Family Contract): a result file
`<stem>.json` has its checkpoint directory at `ckpt_<stem>/` alongside it.

Usage
-----
  python tools/stale_checkpoint_audit.py --root <outputs dir> \
      [--pattern '*_e*_s*.json'] [--data-changed-after 2026-08-05T18:33] \
      [--out audit.json] [--fail-on-stale]

Exit code 1 only with --fail-on-stale and at least one STALE leg.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
from pathlib import Path


def _find(obj, key):
    """First value for `key` anywhere in a nested dict/list."""
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for v in obj.values():
            got = _find(v, key)
            if got is not None:
                return got
    elif isinstance(obj, list):
        for v in obj:
            got = _find(v, key)
            if got is not None:
                return got
    return None


def _ts(p) -> str:
    return _dt.datetime.fromtimestamp(os.path.getmtime(p)).strftime("%Y-%m-%dT%H:%M")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", required=True, help="directory tree of result JSONs to audit")
    ap.add_argument("--pattern", default="*_e*_s*.json",
                    help="glob for per-leg result JSONs (default '*_e*_s*.json')")
    ap.add_argument("--ckpt-prefix", default="ckpt_")
    ap.add_argument("--exclude", action="append", default=["void", "quarantine", "backup"],
                    help="substring to skip; repeatable (defaults: void, quarantine, backup)")
    ap.add_argument("--data-changed-after", default=None,
                    help="ISO timestamp of a dataset swap/trim; checkpoints older than this "
                         "are reported as PRE-CHANGE even if the mtime test is inconclusive")
    ap.add_argument("--mtime-slack-seconds", type=float, default=60.0)
    ap.add_argument("--train-seconds-floor", type=float, default=5.0,
                    help="train_seconds below this is treated as 'did not train'")
    ap.add_argument("--out", default=None)
    ap.add_argument("--fail-on-stale", action="store_true")
    args = ap.parse_args(argv)

    cutoff = None
    if args.data_changed_after:
        cutoff = _dt.datetime.fromisoformat(args.data_changed_after).timestamp()

    rows = []
    for f in sorted(Path(args.root).rglob(args.pattern)):
        s = str(f)
        if any(x in s for x in args.exclude):
            continue
        try:
            d = json.load(open(f))
        except Exception as e:                                    # noqa: BLE001
            rows.append({"leg": s, "status": "UNREADABLE", "error": repr(e)})
            continue
        ck = f.parent / f"{args.ckpt_prefix}{f.stem}" / "last.pt"
        resumed = _find(d, "resumed_from_step")
        steps = _find(d, "steps")
        tsec = d.get("train_seconds", _find(d, "train_seconds"))
        gap = _find(d, "train_vs_test_gap") or {}
        reasons = []
        if ck.exists() and os.path.getmtime(ck) < os.path.getmtime(f) - args.mtime_slack_seconds:
            reasons.append("ckpt_older_than_result")
        if resumed is not None and steps is not None and resumed >= steps:
            reasons.append("resumed_at_full_budget")
        if tsec is not None and tsec < args.train_seconds_floor:
            reasons.append("train_seconds_collapsed")
        if cutoff and ck.exists() and os.path.getmtime(ck) < cutoff:
            reasons.append("ckpt_predates_data_change")
        rows.append({
            "leg": s.replace(str(Path(args.root)) + "/", ""),
            "status": "STALE" if reasons else "OK",
            "reasons": reasons,
            "resumed_from_step": resumed, "steps": steps, "train_seconds": tsec,
            "train_nRMSE_at_hf_train_conditions": gap.get("train_nRMSE_at_hf_train_conditions"),
            "test_nRMSE": gap.get("test_nRMSE"),
            "result_mtime": _ts(f),
            "ckpt_mtime": _ts(ck) if ck.exists() else None,
        })

    stale = [r for r in rows if r["status"] == "STALE"]
    print(f"# stale-checkpoint audit: {len(rows)} legs under {args.root}")
    print(f"{'status':8s}{'train_s':>10s}{'resumed':>9s}{'ckpt_mtime':>18s}{'result_mtime':>18s}  leg / reasons")
    for r in sorted(rows, key=lambda x: (x["status"] != "STALE", x["leg"])):
        ts = "-" if r.get("train_seconds") is None else f"{r['train_seconds']:.1f}"
        print(f"{r['status']:8s}{ts:>10s}{str(r.get('resumed_from_step')):>9s}"
              f"{str(r.get('ckpt_mtime')):>18s}{str(r.get('result_mtime')):>18s}  {r['leg']}")
        if r.get("reasons"):
            print(f"{'':63s}  -> {', '.join(r['reasons'])}")
    print(f"\nSTALE: {len(stale)} / {len(rows)}")

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        with open(args.out, "w") as fh:
            json.dump({"root": args.root, "pattern": args.pattern,
                       "data_changed_after": args.data_changed_after,
                       "n_legs": len(rows), "n_stale": len(stale), "legs": rows}, fh, indent=1)
        print(f"wrote {args.out}")
    return 1 if (args.fail_on_stale and stale) else 0


if __name__ == "__main__":
    raise SystemExit(main())
