"""
Launcher for external-SOTA benchmark sweeps.

Mirrors eval/launch_full.py but discovers families under
references/external_sota/<name>/ (one level deeper than what eval/score.py
walks). Uses eval/score.py:run_one for the actual eval so wrappers behave
identically to in-tree families.

Two roles:
  --plan         Print N (size of array) and the (family, dataset) list, exit.
                 Use this to compute --array=0-(N-1) for sbatch.
  --array_index  Run one (family, dataset) pair from the plan.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "eval"))
from score import run_one  # noqa: E402

EXTERNAL_DIR = PROJECT_ROOT / "references" / "external_sota"


def discover_external_families(root: Path = EXTERNAL_DIR) -> list[dict]:
    families = []
    for d in sorted(root.iterdir()) if root.exists() else []:
        if not d.is_dir():
            continue
        manifest = d / "manifest.json"
        smoke = d / "smoke_eval.py"
        if manifest.exists() and smoke.exists():
            families.append({"path": d, "manifest": json.loads(manifest.read_text())})
    return families


def build_plan(families_csv: str, cfg: dict, available: dict) -> list[tuple[str, str, int]]:
    if families_csv.strip().lower() == "all":
        fams = sorted(available.keys())
    else:
        fams = [f.strip() for f in families_csv.split(",") if f.strip()]
    for fam in fams:
        if fam not in available:
            sys.exit(f"unknown external family: {fam} (available: {sorted(available)})")
    return [(fam, ds["name"], ds["epochs"]) for fam in fams for ds in cfg["datasets"]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--families", default="all",
                    help="CSV of family names under references/external_sota/, or 'all'.")
    ap.add_argument("--config", default=str(PROJECT_ROOT / "eval" / "full_config_ifc_raw.json"),
                    help="Same config schema as eval/full_config*.json.")
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--array_index", type=int, default=None)
    args = ap.parse_args()

    cfg = json.loads(Path(args.config).read_text())
    available = {f["path"].name: f for f in discover_external_families()}
    plan = build_plan(args.families, cfg, available)

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
    family = available[fam_name]
    ds_cfg = next(d for d in cfg["datasets"] if d["name"] == ds_name)
    results_root = PROJECT_ROOT / "results" / "raw_external_sota"
    results_root.mkdir(parents=True, exist_ok=True)
    ckpt_root = PROJECT_ROOT / "checkpoints" / "external_sota"

    t0 = time.time()
    res = run_one(family, ds_cfg, epochs=epochs, seed=cfg["seed"],
                  timeout_s=cfg["per_call_timeout_seconds"],
                  ckpt_root=ckpt_root, results_root=results_root, cache=True)
    print(f"[{fam_name}/{ds_name}] {time.time()-t0:.0f}s -> {json.dumps(res)[:300]}")


if __name__ == "__main__":
    main()
