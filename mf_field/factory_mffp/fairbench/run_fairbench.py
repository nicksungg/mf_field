"""Fair benchmark launcher: 9 model families x 15 non-chin_chun datasets.

Every family's smoke_eval.py now (a) evaluates the FULL HF test field on a
common 256-capped working grid and (b) writes, via data_adapters.metrics.
finalize_and_write, the per-sample relative-L2 array + 95% bootstrap CI +
aggregate nRMSE + n_params + train_seconds + eval latency + peak GPU mem.

This launcher just invokes each (family, dataset) smoke_eval as a subprocess
(so wrappers stay identical to how the factory runs them) and caches the JSON
under results/raw_fairbench/. Roles:
  --plan         print N and the (family, dataset) list (for sbatch --array)
  --array_index  run one (family, dataset) pair from the plan

It deliberately lives outside the factory's fixed surfaces (eval/, scripts/).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# family name -> directory holding manifest.json + smoke_eval.py
FAMILIES = {
    "fno_mf_stack":                "models/fno_mf_stack",
    "fno_coregionalization":       "models/fno_coregionalization",
    "fno_coreg_residual":          "models/fno_coreg_residual",
    "transolver_residual":         "models/transolver_residual",
    "transolver_attention_fusion": "models/transolver_attention_fusion",
    "v9_baseline":                 "references/v9_baseline",
    "mf_deeponet":                 "references/external_sota/mf_deeponet",
    "mfrnp":                       "references/external_sota/mfrnp",
    "d_mfd":                       "references/external_sota/d_mfd",
}

DATASETS = [
    "ifc_heat", "ifc_poisson", "poisson_local", "heat_local", "fluid",
    "era5", "pm_test", "advection_diffusion_generated", "allen_cahn_generated",
    "burgers_generated", "burgers_param_generated", "darcy_generated",
    "heat_generated", "lid_driven_cavity_generated", "poisson_generated",
]


def build_plan(families, datasets):
    return [(fam, ds) for fam in families for ds in datasets]


def code_hash(family_dir: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(family_dir.rglob("*.py")):
        if "__pycache__" in p.parts or "upstream" in p.parts:
            continue
        h.update(p.relative_to(family_dir).as_posix().encode())
        h.update(p.read_bytes())
    return h.hexdigest()[:12]


def run_one(fam: str, ds: str, epochs: int, seed: int, py: str,
            results_root: Path, ckpt_root: Path, cache: bool) -> dict:
    fam_dir = ROOT / FAMILIES[fam]
    smoke = fam_dir / "smoke_eval.py"
    ds_dir = ROOT / "data" / ds
    ch = code_hash(fam_dir)
    tag = f"{fam}__{ds}__e{epochs}__s{seed}__{ch}"
    out_path = results_root / f"{tag}.json"
    ckpt_dir = ckpt_root / fam / ds
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    if cache and out_path.exists():
        try:
            r = json.loads(out_path.read_text()); r["_cache"] = "hit"; return r
        except Exception:
            pass
    cmd = [py, str(smoke),
           "--dataset_dir", str(ds_dir), "--dataset_name", ds,
           "--epochs", str(epochs), "--out", str(out_path),
           "--ckpt_dir", str(ckpt_dir), "--seed", str(seed)]
    print(f"[run] {fam} x {ds} (epochs={epochs}, hash={ch})", flush=True)
    t0 = time.time()
    proc = subprocess.run(cmd, cwd=str(ROOT))
    dt = time.time() - t0
    if proc.returncode != 0 or not out_path.exists():
        return {"model": fam, "dataset": ds, "error": f"exit={proc.returncode}",
                "wall_seconds": dt}
    r = json.loads(out_path.read_text()); r["_cache"] = "miss"; r["wall_seconds"] = dt
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--array_index", type=int, default=None)
    ap.add_argument("--epochs", type=int, default=2500)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--families", default=",".join(FAMILIES))
    ap.add_argument("--no_cache", action="store_true")
    args = ap.parse_args()

    fams = [f.strip() for f in args.families.split(",") if f.strip() in FAMILIES]
    plan = build_plan(fams, DATASETS)

    if args.plan:
        print(f"N={len(plan)}")
        for i, (fam, ds) in enumerate(plan):
            print(f"  [{i:3d}] {fam:30s} {ds}")
        return
    if args.array_index is None:
        sys.exit("either --plan or --array_index required")
    if not (0 <= args.array_index < len(plan)):
        sys.exit(f"array_index {args.array_index} out of range [0,{len(plan)})")

    fam, ds = plan[args.array_index]
    py = sys.executable
    results_root = ROOT / "results" / "raw_fairbench"; results_root.mkdir(parents=True, exist_ok=True)
    ckpt_root = ROOT / "checkpoints" / "fairbench"
    r = run_one(fam, ds, args.epochs, args.seed, py, results_root, ckpt_root,
                cache=not args.no_cache)
    print(f"[{fam}/{ds}] -> {json.dumps(r)[:300]}")


if __name__ == "__main__":
    main()
