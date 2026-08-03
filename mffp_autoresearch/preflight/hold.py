#!/usr/bin/env python3
"""Stop-the-line HOLD for autoresearch rounds.

A defect discovered mid-round on a mentor-owned surface (generator code, dataset
arrays, scoring instruments) is a stop-the-line event: continuing to launch batches
against a defective panel burns compute and produces cards that later have to be
retracted. Round 2 discovered four such defects in flight with no mechanism to stop.

Contract (enforced by convention, checked by the harness):
  - Any agent that finds such a defect runs `hold.py set --reason ...` IMMEDIATELY.
  - Every batch-dispatch path runs `hold.py check` first and refuses to launch on
    exit 3 (this includes cron/poll loops — a held round also stops its pollers).
  - Only the operator clears a hold (`hold.py clear --by eloise`), after deciding:
    repair + preflight re-run, waive with rationale, or close the round.

The sentinel is <state_dir>/HOLD.json; its presence IS the hold (content is audit).

Usage:
  python hold.py set   --state <round>/state --reason "ifc ladder unpaired" [--by agent-id]
  python hold.py check --state <round>/state          # exit 0 free, exit 3 held
  python hold.py clear --state <round>/state --by eloise
"""
from __future__ import annotations

import argparse
import datetime
import json
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["set", "check", "clear"])
    ap.add_argument("--state", type=Path, required=True, help="the round's state/ dir")
    ap.add_argument("--reason")
    ap.add_argument("--by", default="unattributed")
    args = ap.parse_args()
    sentinel = args.state / "HOLD.json"

    if args.cmd == "set":
        if not args.reason:
            ap.error("set requires --reason")
        record = {"reason": args.reason, "set_by": args.by,
                  "set_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}
        if sentinel.exists():                     # append, never overwrite an active hold
            prior = json.loads(sentinel.read_text())
            prior.setdefault("additional", []).append(record)
            sentinel.write_text(json.dumps(prior, indent=2) + "\n")
        else:
            args.state.mkdir(parents=True, exist_ok=True)
            sentinel.write_text(json.dumps(record, indent=2) + "\n")
        print(f"HOLD set: {args.reason}")
        return 0

    if args.cmd == "check":
        if sentinel.exists():
            print(f"HELD: {json.loads(sentinel.read_text())['reason']} — no launches")
            return 3
        print("free")
        return 0

    # clear
    if not sentinel.exists():
        print("no hold to clear")
        return 0
    record = json.loads(sentinel.read_text())
    record["cleared_by"] = args.by
    record["cleared_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    history = args.state / "HOLD_history.jsonl"
    with open(history, "a") as f:
        f.write(json.dumps(record) + "\n")
    sentinel.unlink()
    print(f"HOLD cleared by {args.by} (archived to {history.name})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
