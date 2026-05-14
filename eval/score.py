"""
Smoke-eval orchestrator. Discovers all model families under models/, runs each
against the smoke datasets, aggregates the per-(model, dataset) results into a
leaderboard, and emits a single JSON the factory can consume.

The factory's research target points its `run_command` at this script. Output
JSON ends up at `results/smoke_latest.json` (configurable via --out).

Composite metric (lower is better):
    composite_nRMSE = mean over datasets of (best-model-on-that-dataset's mean nRMSE)

Where the per-dataset nRMSE is averaged across all reported splits. We track
per-model results too, so the factory can see which model family won where.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def discover_models(models_dir: Path) -> list[dict]:
    families = []
    for d in sorted(models_dir.iterdir()):
        if not d.is_dir():
            continue
        manifest = d / "manifest.json"
        smoke = d / "smoke_eval.py"
        if manifest.exists() and smoke.exists():
            families.append({"path": d, "manifest": json.loads(manifest.read_text())})
        else:
            print(f"[skip] {d.name}: missing manifest.json or smoke_eval.py", file=sys.stderr)
    return families


def code_hash(family_dir: Path) -> str:
    h = hashlib.sha256()
    for p in sorted(family_dir.rglob("*.py")):
        h.update(p.relative_to(family_dir).as_posix().encode())
        h.update(p.read_bytes())
    return h.hexdigest()[:12]


def run_one(family: dict, dataset: dict, *, epochs: int, seed: int,
            timeout_s: int, ckpt_root: Path, results_root: Path,
            cache: bool) -> dict:
    fam_dir = family["path"]
    fam_name = fam_dir.name
    ds_name = dataset["name"]
    ds_dir = PROJECT_ROOT / "data" / ds_name

    ch = code_hash(fam_dir)
    tag = f"{fam_name}__{ds_name}__e{epochs}__s{seed}__{ch}"
    out_path = results_root / f"{tag}.json"
    ckpt_dir = ckpt_root / fam_name / ds_name
    ckpt_dir.mkdir(parents=True, exist_ok=True)

    if cache and out_path.exists():
        try:
            res = json.loads(out_path.read_text())
            res["_cache"] = "hit"
            return res
        except Exception:
            pass

    cmd = [
        sys.executable, str(fam_dir / "smoke_eval.py"),
        "--dataset_dir", str(ds_dir),
        "--dataset_name", ds_name,
        "--epochs", str(epochs),
        "--out", str(out_path),
        "--ckpt_dir", str(ckpt_dir),
        "--seed", str(seed),
    ]
    t0 = time.time()
    try:
        proc = subprocess.run(cmd, timeout=timeout_s, capture_output=True, text=True)
    except subprocess.TimeoutExpired:
        return {"model": fam_name, "dataset": ds_name, "error": "timeout",
                "wall_seconds": timeout_s}
    dt = time.time() - t0

    if proc.returncode != 0 or not out_path.exists():
        return {
            "model": fam_name, "dataset": ds_name,
            "error": f"exit={proc.returncode}",
            "stderr_tail": (proc.stderr or "")[-2000:],
            "wall_seconds": dt,
        }
    res = json.loads(out_path.read_text())
    res["_cache"] = "miss"
    res["wall_seconds"] = dt
    return res


def per_dataset_nrmse(res: dict) -> float | None:
    if "error" in res or "splits" not in res or not res["splits"]:
        return None
    vals = [s["nRMSE"] for s in res["splits"].values()
            if isinstance(s, dict) and isinstance(s.get("nRMSE"), (int, float))]
    if not vals:
        return None
    return sum(vals) / len(vals)


def composite(results: list[dict], datasets: list[dict]) -> dict:
    by_dataset: dict[str, list[dict]] = {ds["name"]: [] for ds in datasets}
    for r in results:
        by_dataset.setdefault(r["dataset"], []).append(r)

    leaderboard, per_ds_best = {}, []
    for ds_name, runs in by_dataset.items():
        scored = [(per_dataset_nrmse(r), r) for r in runs]
        scored = [(v, r) for v, r in scored if v is not None]
        if not scored:
            leaderboard[ds_name] = {"best": None, "n_runs": len(runs)}
            continue
        scored.sort(key=lambda x: x[0])
        best_val, best_run = scored[0]
        leaderboard[ds_name] = {
            "best": {"model": best_run["model"], "nRMSE": best_val},
            "ranked": [{"model": r["model"], "nRMSE": v} for v, r in scored],
            "n_runs": len(runs),
        }
        per_ds_best.append(best_val)

    composite_nrmse = sum(per_ds_best) / len(per_ds_best) if per_ds_best else float("inf")
    return {"composite_nRMSE": composite_nrmse, "leaderboard": leaderboard,
            "n_datasets_scored": len(per_ds_best)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(PROJECT_ROOT / "eval" / "smoke_config.json"))
    ap.add_argument("--out", default=str(PROJECT_ROOT / "results" / "smoke_latest.json"))
    ap.add_argument("--no_cache", action="store_true")
    ap.add_argument("--families", help="comma-separated subset of model families to run")
    args = ap.parse_args()

    cfg = json.loads(Path(args.config).read_text())
    models_dir = PROJECT_ROOT / "models"
    ckpt_root = PROJECT_ROOT / "checkpoints"
    results_root = PROJECT_ROOT / "results" / "raw"
    results_root.mkdir(parents=True, exist_ok=True)

    families = discover_models(models_dir)
    if args.families:
        wanted = set(args.families.split(","))
        families = [f for f in families if f["path"].name in wanted]
    if not families:
        print("ERROR: no model families discovered", file=sys.stderr); sys.exit(2)

    print(f"[score] {len(families)} model families × {len(cfg['datasets'])} datasets")
    for f in families:
        print(f"        - {f['path'].name}")

    runs: list[dict] = []
    for fam in families:
        for ds in cfg["datasets"]:
            print(f"[run]   {fam['path'].name}  ×  {ds['name']}")
            r = run_one(fam, ds,
                        epochs=ds["epochs"], seed=cfg["seed"],
                        timeout_s=cfg["per_call_timeout_seconds"],
                        ckpt_root=ckpt_root, results_root=results_root,
                        cache=not args.no_cache)
            runs.append(r)
            if "error" in r:
                print(f"[FAIL]  {fam['path'].name}/{ds['name']}: {r['error']}")
            else:
                nrmse = per_dataset_nrmse(r)
                print(f"[OK]    {fam['path'].name}/{ds['name']}  nRMSE={nrmse:.4e}  cache={r.get('_cache')}")

    summary = composite(runs, cfg["datasets"])
    payload = {
        "metric": cfg.get("primary_metric", "composite_nRMSE"),
        "metric_value": summary["composite_nRMSE"],
        "metric_lower_is_better": cfg.get("primary_metric_lower_is_better", True),
        "summary": summary,
        "runs": runs,
        "results": [{
            "name": "composite_nRMSE",
            "value": summary["composite_nRMSE"],
            "lower_is_better": True,
        }, {
            "name": "n_datasets_scored",
            "value": summary["n_datasets_scored"],
            "lower_is_better": False,
        }],
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2))

    history = PROJECT_ROOT / "results" / "history.jsonl"
    with history.open("a") as f:
        f.write(json.dumps({"ts": time.time(), **payload}) + "\n")

    print(f"\n[done] composite_nRMSE = {summary['composite_nRMSE']:.4e} "
          f"({summary['n_datasets_scored']}/{len(cfg['datasets'])} datasets)")
    print(f"[done] wrote {out}")


if __name__ == "__main__":
    main()
