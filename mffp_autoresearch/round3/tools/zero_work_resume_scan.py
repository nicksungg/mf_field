#!/usr/bin/env python
"""Legs whose WEIGHTS DID NOT MOVE during the run that produced their result JSON.

Provenance: promoted from `r3s4_audit-B1` mechanism turn 1
(`worktrees/r3s4_audit/B1/scratchpad/reanalysis_turn_1{,b,c}.py`, results file
sections 1-4 and 6).

Relationship to `stale_checkpoint_audit.py`
-------------------------------------------
That tool answers "is this leg STALE?" with four rules, two of which are
wall-clock proxies. Priced over 859 live legs, `train_seconds_collapsed` was the
SOLE reason on 62 legs -- every one of which had actually trained (53 were the
round's own 2-epoch contract tier, which cannot take 5 s) -- and was the sole
reason on ZERO of the 20 ground-truth stale legs. It is strictly dominated by
`ckpt_older_than_result`, because a run that trains necessarily rewrites
`last.pt`. Raising or lowering `--train-seconds-floor` cannot fix that.

This tool drops the wall-clock term entirely and reports only the NECESSARY
CONDITION for the stale-checkpoint defect, which is a fact rather than a proxy:

    executed_steps == 0     (the optimizer took no step in this run)

It is deliberately NOT a verdict. `executed_steps == 0` is normal and harmless
when the checkpoint was fitted to the SAME data the leg scored (measured: 18
`sharp__allen_cahn_2d` anchor legs, whose only intervening change was a
test-split trim). It is a contamination when the training arrays changed
(measured: 18 `sharp__phase_field_crystal_2d` anchor legs resumed from
pre-box-swap checkpoints, and the 6 `ifc_poisson` legs quarantined by
STOP-THE-LINE #2). Deciding which requires knowing whether the TRAINING data
changed -- and no timestamp can tell you: the round-3 repair copy preserved file
mtimes, so the ifc arrays' own mtimes (2026-08-03T13:04) predate the checkpoints
they invalidated. Only a content hash bound into the checkpoint can.

This tool therefore also reports DATA-BINDING COVERAGE: how many checkpoints
carry a `data_binding` / `data_sha256` / `data_hashes` block. Once families write
`state/data_hashes.json` hashes into `last.pt` (train arrays and test arrays
hashed SEPARATELY), `--verify-binding` turns the zero-work list into an exact
verdict.

Convention assumed (factory Model Family Contract): a result file `<stem>.json`
has its checkpoint directory at `ckpt_<stem>/` alongside it.

Usage
-----
  python tools/zero_work_resume_scan.py --root <outputs dir>
      [--pattern '*_e*_s*.json'] [--exclude void --exclude quarantine]
      [--read-ckpt-binding] [--data-hashes state/data_hashes.json]
      [--verify-binding] [--out scan.json] [--fail-on-zero-work]

Exit code 1 only with --fail-on-zero-work and at least one zero-work leg.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import math
import os
import re
from collections import defaultdict
from pathlib import Path

EPOCH_RE = re.compile(r"_e(\d+)_s(\d+)\.json$")
BINDING_KEYS = ("data_binding", "data_sha256", "data_hashes", "data_hash")


def find(o, k):
    if isinstance(o, dict):
        if k in o:
            return o[k]
        for v in o.values():
            g = find(v, k)
            if g is not None:
                return g
    elif isinstance(o, list):
        for v in o:
            g = find(v, k)
            if g is not None:
                return g
    return None


def ts(p):
    return _dt.datetime.fromtimestamp(os.path.getmtime(p)).strftime("%Y-%m-%dT%H:%M")


def declared_steps(d, epochs_from_name):
    """Optimizer steps the leg's own metadata declares, explicit or derived."""
    s = find(d, "steps")
    if s is not None:
        return int(s), "explicit"
    epochs = find(d, "epochs") or epochs_from_name
    spe = find(d, "steps_per_epoch")
    if epochs and spe:
        return int(epochs) * int(spe), "epochs x steps_per_epoch"
    n = find(d, "n_fit") or find(d, "n_train_hf") or find(d, "n_train_all")
    if epochs and n:
        b = find(d, "batch") or 16
        return int(epochs) * max(1, math.ceil(int(n) / int(b))), \
            f"epochs x ceil(n_fit/{b})"
    return None, "UNDERIVABLE"


def ckpt_binding(ck_path):
    """Read a data-binding block out of a checkpoint, if the family writes one."""
    try:
        import torch
        d = torch.load(ck_path, map_location="cpu", weights_only=False)
    except Exception as e:                                        # noqa: BLE001
        return {"status": "UNREADABLE", "error": repr(e)[:160]}
    if not isinstance(d, dict):
        return {"status": "ABSENT"}
    for k in BINDING_KEYS:
        v = find(d, k)
        if v is not None:
            return {"status": "PRESENT", "key": k, "value": v}
    return {"status": "ABSENT",
            "top_level_keys": [k for k in d if k not in ("model", "opt", "sched",
                                                         "best_state", "gen")]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", required=True)
    ap.add_argument("--pattern", default="*_e*_s*.json")
    ap.add_argument("--ckpt-prefix", default="ckpt_")
    ap.add_argument("--exclude", action="append",
                    default=["void", "quarantine", "backup", "stale_ckpt"])
    ap.add_argument("--read-ckpt-binding", action="store_true",
                    help="torch.load every checkpoint of a zero-work leg to report "
                         "data-binding coverage (slow: checkpoints are ~25 MB)")
    ap.add_argument("--data-hashes", default=None,
                    help="state/data_hashes.json; with --verify-binding, compare")
    ap.add_argument("--verify-binding", action="store_true")
    ap.add_argument("--mtime-slack-seconds", type=float, default=60.0)
    ap.add_argument("--out", default=None)
    ap.add_argument("--fail-on-zero-work", action="store_true")
    args = ap.parse_args(argv)

    hashes = json.load(open(args.data_hashes)) if args.data_hashes else None

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
        if find(d, "train_seconds") is None and find(d, "steps") is None:
            continue                                              # not a training leg
        m = EPOCH_RE.search(f.name)
        steps, how = declared_steps(d, int(m.group(1)) if m else None)
        resumed = find(d, "resumed_from_step") or 0
        executed = (steps - resumed) if steps is not None else None
        ck = f.parent / f"{args.ckpt_prefix}{f.stem}" / "last.pt"
        ck_exists = ck.exists()
        dmt = (os.path.getmtime(ck) - os.path.getmtime(f)) if ck_exists else None
        if executed is None:
            status = "UNDERIVABLE"
        elif executed == 0:
            status = "ZERO_WORK"
        elif ck_exists and dmt is not None and dmt < -args.mtime_slack_seconds:
            status = "CKPT_NOT_REWRITTEN"      # trained? then why is last.pt older
        elif not ck_exists:
            status = "NO_CKPT"
        else:
            status = "WORK_DONE"
        rec = {"leg": s.replace(str(Path(args.root)) + "/", ""),
               "model": d.get("model"), "dataset": d.get("dataset"),
               "status": status, "declared_steps": steps, "steps_source": how,
               "resumed_from_step": resumed, "executed_steps": executed,
               "train_seconds": find(d, "train_seconds"),
               "result_mtime": ts(f), "ckpt_mtime": ts(ck) if ck_exists else None,
               "ckpt_minus_result_seconds": dmt}
        if args.read_ckpt_binding and ck_exists and status in ("ZERO_WORK",
                                                               "CKPT_NOT_REWRITTEN"):
            rec["ckpt_data_binding"] = ckpt_binding(ck)
            if args.verify_binding and hashes and \
                    rec["ckpt_data_binding"].get("status") == "PRESENT":
                cur = (hashes.get("datasets", {}).get(d.get("dataset"), {}) or {}).get("sha256")
                got = rec["ckpt_data_binding"]["value"]
                got = got.get(d.get("dataset")) if isinstance(got, dict) else got
                rec["binding_matches_current_data"] = bool(cur and got and cur == got)
        rows.append(rec)

    zw = [r for r in rows if r.get("status") == "ZERO_WORK"]
    nr = [r for r in rows if r.get("status") == "CKPT_NOT_REWRITTEN"]
    ud = [r for r in rows if r.get("status") == "UNDERIVABLE"]

    print(f"# zero-work resume scan: {len(rows)} training legs under {args.root}")
    print(f"  ZERO_WORK          {len(zw):4d}  (executed_steps == 0)")
    print(f"  CKPT_NOT_REWRITTEN {len(nr):4d}  (steps executed, but last.pt older than the result)")
    print(f"  UNDERIVABLE        {len(ud):4d}  (no step/epoch metadata -- instrument blind spot)")
    print(f"  WORK_DONE / NO_CKPT{len(rows)-len(zw)-len(nr)-len(ud):4d}\n")

    if zw or nr:
        by = defaultdict(list)
        for r in zw + nr:
            by[(r["status"], r["model"], r["dataset"])].append(r)
        print(f"{'status':20s}{'model':26s}{'dataset':32s}{'n':>4s}  ckpt_mtime range")
        for k in sorted(by):
            v = by[k]
            mts = sorted(x["ckpt_mtime"] or "-" for x in v)
            print(f"{k[0]:20s}{str(k[1])[:26]:26s}{str(k[2])[:32]:32s}{len(v):>4d}  "
                  f"{mts[0]} .. {mts[-1]}")
        print("\n  -> ZERO_WORK is NOT a verdict. It is contamination only if the TRAINING")
        print("     arrays changed between the checkpoint and the score. Timestamps cannot")
        print("     decide that (the round-3 repair copy preserved file mtimes); a data")
        print("     hash bound into the checkpoint can. Coverage below.")

    if args.read_ckpt_binding:
        cov = defaultdict(int)
        for r in zw + nr:
            cov[r.get("ckpt_data_binding", {}).get("status", "NOT_READ")] += 1
        print(f"\n  checkpoint data-binding coverage on flagged legs: {dict(cov)}")
        if args.verify_binding:
            mism = [r for r in zw + nr if r.get("binding_matches_current_data") is False]
            print(f"  legs whose binding MISMATCHES the current data: {len(mism)}")
            for r in mism:
                print(f"     {r['leg']}")

    if ud:
        fams = defaultdict(int)
        for r in ud:
            fams[r["model"]] += 1
        print(f"\n  UNDERIVABLE by family (these families expose no step/epoch metadata, "
              f"so this instrument cannot see them): {dict(fams)}")

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        json.dump({"root": args.root, "pattern": args.pattern, "n_legs": len(rows),
                   "n_zero_work": len(zw), "n_ckpt_not_rewritten": len(nr),
                   "n_underivable": len(ud), "legs": rows}, open(args.out, "w"), indent=1)
        print(f"\nwrote {args.out}")
    return 1 if (args.fail_on_zero_work and zw) else 0


if __name__ == "__main__":
    raise SystemExit(main())
