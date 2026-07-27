"""
Launcher for full-benchmark array jobs.

Two roles:
  --plan        Print N (size of array) and the (family, dataset) list, then exit.
                Use this to compute --array=0-(N-1) for sbatch.
  --array_index Run one (family, dataset) pair from the plan. This is what each
                array task does inside run_full.sbatch.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "eval"))
from score import run_one, discover_models, code_hash  # noqa: E402


def build_plan(families_csv: str, cfg: dict) -> list[tuple[str, str, int]]:
    fams = [f.strip() for f in families_csv.split(",") if f.strip()]
    return [(fam, ds["name"], ds["epochs"]) for fam in fams for ds in cfg["datasets"]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--families", default="v9_baseline")
    ap.add_argument("--config", default=str(PROJECT_ROOT / "eval" / "full_config.json"))
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--array_index", type=int, default=None)
    args = ap.parse_args()

    cfg = json.loads(Path(args.config).read_text())
    plan = build_plan(args.families, cfg)

    if args.plan:
        print(f"N={len(plan)}")
        for i, (fam, ds, ep) in enumerate(plan):
            print(f"  [{i:3d}] {fam:24s} {ds:32s} epochs={ep}")
        return

    if args.array_index is None:
        sys.exit("either --plan or --array_index required")
    if not (0 <= args.array_index < len(plan)):
        sys.exit(f"array_index {args.array_index} out of range [0, {len(plan)})")

    fam_name, ds_name, epochs = plan[args.array_index]
    families = {f["path"].name: f for f in discover_models(PROJECT_ROOT / "models")}
    if fam_name not in families:
        sys.exit(f"unknown family: {fam_name}")
    family = families[fam_name]

    ds_cfg = next(d for d in cfg["datasets"] if d["name"] == ds_name)
    results_root = PROJECT_ROOT / "results" / "raw_full"
    results_root.mkdir(parents=True, exist_ok=True)
    ckpt_root = PROJECT_ROOT / "checkpoints" / "full"

    t0 = time.time()
    res = run_one(family, ds_cfg, epochs=epochs, seed=cfg["seed"],
                  timeout_s=cfg["per_call_timeout_seconds"],
                  ckpt_root=ckpt_root, results_root=results_root, cache=True)
    print(f"[{fam_name}/{ds_name}] {time.time()-t0:.0f}s -> {json.dumps(res)[:300]}")


if __name__ == "__main__":
    main()
