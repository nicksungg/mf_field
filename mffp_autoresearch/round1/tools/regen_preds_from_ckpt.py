#!/usr/bin/env python
"""Recover a control arm's test predictions from a checkpoint that shipped without them.

Provenance: promoted from `s5_tuning-B1` mechanism turn 1
(`worktrees/s5_tuning/B1/scratchpad/regen_cap12_preds.py`).

WHY THIS EXISTS
---------------
Paired mechanism analysis needs BOTH arms' `preds_test.npz`. Cards routinely add the
prediction dump to their own family while the control they are compared against (a
batch-0 anchor run, an ADR-0005 same-hardware recert, another stream's champion)
shipped only `last.pt`. Retraining the control to recover its predictions is
expensive and re-rolls hardware/precision noise.

This tool instead points a family entrypoint that DOES dump predictions at the
control's checkpoint. Contract families resume from `<ckpt_dir>/last.pt`, so a
finished checkpoint makes `smoke_eval.py` skip training and run the eval path only.
The checkpoint is copied into a scratch working directory: the source artifacts under
`${OUTPUTS_ROOT}` are never written to.

MANDATORY SEAM CHECK
--------------------
With `--verify_json <official result JSON>` the tool compares its regenerated score
against the control's officially recorded one, on the ROUND'S metric — the per-sample
mean `splits.<split>.rel_l2_mean` (`eval/score_panel.py:154`), NOT the family JSON's
legacy ratio-of-sums `nRMSE` field (they differ by 3x on `ext__helmholtz_2d`). It also
reports `train_seconds`: a value that is not ~0 means the checkpoint did NOT satisfy
the resume branch and the run RETRAINED, which invalidates the regeneration.

No number produced here should enter a card: the official result JSON stays the source
of truth for scores. The regenerated predictions are for structural decomposition.

USAGE
-----
  python tools/regen_preds_from_ckpt.py \
      --family_dir <worktree>/models_r1/<family> \
      --dataset_dir "$FACTORY_ROOT/data/<ds>" --dataset_name <ds> \
      --ckpt "$OUTPUTS_ROOT/recert/.../ckpt_<ds>_e200_s0/last.pt" \
      --workdir <scratch>/cap12_infer --epochs 200 --seed 0 \
      [--env MFFP_MODES_CAP=12] [--verify_json <official>.json] [--out seam.json]

The family entrypoint must (a) accept the contract CLI
(`--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`), (b) resume from
`<ckpt_dir>/last.pt`, and (c) dump `<ckpt_dir>/preds_test.npz`. `--env` knobs must
reproduce the CONTROL's configuration, not the arm's (e.g. the control's `modes_cap`),
otherwise the checkpoint will fail its shape check and the family will silently train
from scratch — which the `train_seconds` report catches.

COST NOTE. On a contended login node (`nproc` 1) a 100-sample 256x256 FNO forward can
exceed a 20-minute analysis cap. Use `--timeout` and fall back to a sample-first
subset or a GPU if it fires.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def pick_split(splits: dict) -> str:
    for k in ("test_hf", "test", "test_lf"):
        if k in splits:
            return k
    return sorted(splits)[0]


def metric(entry: dict) -> tuple[float, str]:
    """The round's metric, in score_panel.py's precedence order."""
    per = entry.get("rel_l2_per_sample")
    if isinstance(per, list) and per:
        return float(sum(per) / len(per)), "per_sample_mean"
    if "rel_l2_mean" in entry:
        return float(entry["rel_l2_mean"]), "rel_l2_mean"
    if "nRMSE" in entry:
        return float(entry["nRMSE"]), "reported_nRMSE(legacy ratio-of-sums)"
    raise KeyError(f"no usable metric key in split entry: {sorted(entry)}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--family_dir", required=True)
    ap.add_argument("--dataset_dir", required=True)
    ap.add_argument("--dataset_name", required=True)
    ap.add_argument("--ckpt", required=True, help="the control's last.pt")
    ap.add_argument("--workdir", required=True, help="scratch dir; the ckpt is copied here")
    ap.add_argument("--epochs", type=int, required=True,
                    help="must equal the control's epochs (it is part of the resume key)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--env", action="append", default=[], metavar="K=V",
                    help="env knob reproducing the CONTROL's config; repeatable")
    ap.add_argument("--verify_json", default=None, help="the control's official result JSON")
    ap.add_argument("--timeout", type=int, default=1100, help="seconds (default 1100)")
    ap.add_argument("--force", action="store_true", help="re-run even if preds already exist")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    fam = Path(args.family_dir).resolve()
    entry = fam / "smoke_eval.py"
    if not entry.exists():
        raise SystemExit(f"no smoke_eval.py in {fam}")
    work = Path(args.workdir).resolve() / f"ckpt_{args.dataset_name}"
    work.mkdir(parents=True, exist_ok=True)
    if not (work / "last.pt").exists():
        shutil.copy2(args.ckpt, work / "last.pt")
    out_json = work / f"{args.dataset_name}_regen.json"

    if args.force or not (work / "preds_test.npz").exists():
        env = dict(os.environ)
        for kv in args.env:
            if "=" not in kv:
                ap.error(f"--env must be K=V, got {kv!r}")
            k, v = kv.split("=", 1)
            env[k] = v
        cmd = [sys.executable, str(entry), "--dataset_dir", args.dataset_dir,
               "--dataset_name", args.dataset_name, "--epochs", str(args.epochs),
               "--out", str(out_json), "--ckpt_dir", str(work), "--seed", str(args.seed)]
        print("[run]", " ".join(cmd), flush=True)
        try:
            r = subprocess.run(cmd, env=env, timeout=args.timeout,
                               capture_output=True, text=True)
        except subprocess.TimeoutExpired:
            raise SystemExit(f"TIMEOUT after {args.timeout}s -- use a subset or a GPU")
        sys.stdout.write(r.stdout[-4000:])
        if r.returncode != 0:
            sys.stderr.write(r.stderr[-4000:])
            raise SystemExit(f"entrypoint failed (rc={r.returncode})")

    j = json.loads(out_json.read_text())
    sp = pick_split(j["splits"])
    value, source = metric(j["splits"][sp])
    res = {"dataset": args.dataset_name, "split": sp, "metric_source": source,
           "regenerated": value, "preds": str(work / "preds_test.npz"),
           "train_seconds": j.get("train_seconds"),
           "resume_clean": (j.get("train_seconds") is not None
                            and float(j["train_seconds"]) < 5.0),
           "env": args.env, "family_dir": str(fam)}
    if args.verify_json:
        o = json.loads(Path(args.verify_json).read_text())
        osp = sp if sp in o["splits"] else pick_split(o["splits"])
        ov, osrc = metric(o["splits"][osp])
        res.update(official=ov, official_split=osp, official_metric_source=osrc,
                   rel_delta=abs(value - ov) / ov if ov else None)
        res["seam_ok"] = res["rel_delta"] is not None and res["rel_delta"] < 1e-3
    print(json.dumps(res, indent=1))
    if not res["resume_clean"]:
        print("[WARN] train_seconds is not ~0: the checkpoint did NOT resume and the run "
              "RETRAINED. These predictions are not the control's.", file=sys.stderr)
    if args.verify_json and not res.get("seam_ok"):
        print("[WARN] seam check outside 1e-3 relative -- investigate before using.",
              file=sys.stderr)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(res, indent=1))
        print(f"[wrote] {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
