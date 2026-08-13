"""Contract runner: score one family across panel datasets (round 2).

Invokes the family's `smoke_eval.py` (the factory MODEL_CONTRACT CLI, unchanged)
per (dataset, seed) against the STRIPPED TEST VIEW (`stripped_data_root`, spec
§5: test LF field files are physically absent — condition-only at test is
enforced structurally), computes skill against the CORRECTED copy-LF
denominators (ADR r2-0001), caches by a hash covering ALL code that can change
the number, and raises `ScoreContractError` on any seam violation instead of
defaulting.

CLI:
  python score_panel.py --family_dir <path> --datasets <csv|panel|guard> \
      --epochs <n> --seed <n> [--out <json>] [--env KEY=VAL ...] [--no_cache]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
from pathlib import Path

from nrmse import NRMSE_DEF_HASH
from panel_data import COPYLF_DEF_HASH, load_config, repo_root


class ScoreContractError(RuntimeError):
    """A component seam violated its contract (spec §5.3: assert, don't default)."""


EVAL_DIR = Path(__file__).resolve().parent
_HASHED_EVAL_FILES = ("nrmse.py", "panel_data.py", "score_panel.py")


def _results_dir() -> Path:
    return Path(os.environ.get("ROUND2_EVAL_RESULTS", EVAL_DIR / "results"))


def _cache_dir() -> Path:
    return Path(os.environ.get("ROUND2_EVAL_CACHE", EVAL_DIR / "cache"))


def _load_baselines() -> dict:
    # SEAM (a) [benchmark30 campaign, spec D3]: the copy-LF denominators live in
    # the campaign state dir, built by eval/make_copylf_baselines_b30.py with
    # THIS vendored construction (self-consistent COPYLF_DEF_HASH).
    path = Path(__file__).resolve().parents[1] / "state" / "copylf_baselines.json"
    if not path.exists():
        raise ScoreContractError(f"copylf_baselines.json missing at {path}; run eval/make_copylf_baselines_b30.py")
    with open(path) as f:
        baselines = json.load(f)
    if baselines.get("_copylf_def_hash") != COPYLF_DEF_HASH:
        raise ScoreContractError(
            "copylf_baselines.json was computed under a different panel_data.py "
            "(reference construction changed) — re-run make_copylf_baselines.py"
        )
    return baselines


def code_hash(family_dir: Path, env: dict) -> str:
    """sha256 over every .py that can change the score + the env knobs.

    Covers: the family dir (recursive), the factory shared model code
    (models/_common), and the round eval layer itself. Fixes audit findings
    F06 (shared code invisible to cache) and the invisible-env-knob collision.
    """
    root = repo_root()
    cfg = load_config()
    h = hashlib.sha256()
    groups = [
        sorted(Path(family_dir).rglob("*.py")),
        sorted((root / cfg["paths"]["factory_root"] / "models" / "_common").glob("*.py")),
        [EVAL_DIR / name for name in _HASHED_EVAL_FILES],
    ]
    for group in groups:
        for f in group:
            h.update(str(f.name).encode())
            h.update(f.read_bytes())
    for k, v in sorted((env or {}).items()):
        h.update(f"{k}={v}".encode())
    return h.hexdigest()


def _run_one(family_dir: Path, dataset: str, epochs: int, seed: int, env: dict) -> float:
    root = repo_root()
    cfg = load_config()
    # Models are ONLY ever pointed at the stripped view (test LF physically
    # absent). The original data_root is reserved for offline references.
    data_dir = root / cfg["paths"]["stripped_data_root"] / dataset
    if not data_dir.exists():
        raise ScoreContractError(
            f"stripped-view dataset dir not found: {data_dir}; run make_stripped_view.py"
        )
    by_dir = {}
    for p in data_dir.rglob("test_l*.npz"):
        by_dir.setdefault(str(p.parent), []).append(p.name)
    leak = {d: sorted(names) for d, names in by_dir.items() if len(names) > 1}
    if leak:
        raise ScoreContractError(f"stripped view exposes LF test files: {leak}")
    smoke = Path(family_dir) / "smoke_eval.py"
    if not smoke.exists():
        raise ScoreContractError(f"family has no smoke_eval.py: {smoke}")

    out_dir = _results_dir() / Path(family_dir).name
    out_dir.mkdir(parents=True, exist_ok=True)
    out_json = out_dir / f"{dataset}_e{epochs}_s{seed}.json"
    ckpt_dir = out_dir / f"ckpt_{dataset}_e{epochs}_s{seed}"

    child_env = dict(os.environ)
    child_env.update(
        {"PYTHONHASHSEED": str(seed), "CUBLAS_WORKSPACE_CONFIG": ":4096:8"}
    )
    child_env.update(env or {})

    venv_python = root / cfg["paths"]["venv"] / "bin" / "python"
    cmd = [
        str(venv_python), str(smoke),
        "--dataset_dir", str(data_dir), "--dataset_name", dataset,
        "--epochs", str(epochs), "--out", str(out_json),
        "--ckpt_dir", str(ckpt_dir), "--seed", str(seed),
    ]
    proc = subprocess.run(cmd, env=child_env, capture_output=True, text=True)
    if proc.returncode != 0:
        raise ScoreContractError(
            f"smoke_eval failed for {Path(family_dir).name} on {dataset} "
            f"(exit {proc.returncode}):\n{proc.stderr[-2000:]}"
        )
    if not out_json.exists():
        raise ScoreContractError(f"smoke_eval exited 0 but wrote no result JSON at {out_json}")
    with open(out_json) as f:
        result = json.load(f)

    if result.get("dataset") != dataset:
        raise ScoreContractError(
            f"result JSON reports dataset {result.get('dataset')!r}, requested {dataset!r}"
        )
    return _extract_test_metric(result, dataset)


def _extract_test_metric(result: dict, dataset: str) -> tuple:
    """Return (value, split_name, metric_source) for the primary TEST split.

    The factory contract allows any split names (test_hf, test_l4, ...). We
    select the test split by preference and — the round's ONE definition —
    prefer the per-sample rel-L2 array (mean of per-sample ratios) over the
    backward-compat aggregate ratio-of-sums `nRMSE`.
    """
    splits = result.get("splits")
    if not isinstance(splits, dict) or not splits:
        raise ScoreContractError(f"result JSON has no splits for {dataset}")
    test_keys = [k for k in splits if k == "test" or k.startswith("test_")]
    if not test_keys:
        raise ScoreContractError(
            f"no test split in result JSON for {dataset}: splits={sorted(splits)}"
        )
    for preferred in ("test_hf", "test"):
        if preferred in test_keys:
            split = preferred
            break
    else:
        if len(test_keys) > 1:
            raise ScoreContractError(
                f"ambiguous test splits for {dataset}: {sorted(test_keys)}"
            )
        split = test_keys[0]
    entry = splits[split]

    per_sample = entry.get("rel_l2_per_sample")
    if per_sample:
        vals = [float(x) for x in per_sample]
        if not all(math.isfinite(v) for v in vals):
            raise ScoreContractError(f"non-finite per-sample rel-L2 for {dataset}")
        return sum(vals) / len(vals), split, "per_sample_mean"
    if "rel_l2_mean" in entry:
        value, source = float(entry["rel_l2_mean"]), "rel_l2_mean"
    elif "nRMSE" in entry:
        value, source = float(entry["nRMSE"]), "reported_nRMSE"
    else:
        raise ScoreContractError(
            f"test split {split!r} for {dataset} has neither rel_l2_per_sample, "
            f"rel_l2_mean, nor nRMSE: keys={sorted(entry)}"
        )
    if not math.isfinite(value):
        raise ScoreContractError(f"non-finite test metric for {dataset}: {value}")
    return value, split, source


def score_family(family_dir, datasets, epochs: int, seed: int, env: dict = None,
                 use_cache: bool = True) -> dict:
    family_dir = Path(family_dir)
    baselines = _load_baselines()
    chash = code_hash(family_dir, env or {})
    cache_dir = _cache_dir()
    cache_dir.mkdir(parents=True, exist_ok=True)

    per_dataset = {}
    for ds in datasets:
        if ds not in baselines:
            raise ScoreContractError(
                f"dataset {ds!r} has no entry in copylf_baselines.json — "
                "not a panel/guard dataset, or baselines are stale"
            )
        key = hashlib.sha256(f"{chash}|{ds}|{epochs}|{seed}".encode()).hexdigest()
        cache_file = cache_dir / f"{key}.json"
        if use_cache and cache_file.exists():
            with open(cache_file) as f:
                entry = json.load(f)
            if entry.get("nrmse_def_hash") != NRMSE_DEF_HASH:
                raise ScoreContractError(
                    f"cache entry for {ds} was computed under a different nRMSE definition"
                )
            if entry.get("copylf_def_hash") != COPYLF_DEF_HASH:
                raise ScoreContractError(
                    f"cache entry for {ds} was computed under a different reference construction"
                )
            value, split, source, cached = (
                entry["nRMSE"], entry["split"], entry["metric_source"], True
            )
        else:
            value, split, source = _run_one(family_dir, ds, epochs, seed, env or {})
            cached = False
            with open(cache_file, "w") as f:
                json.dump(
                    {"nRMSE": value, "split": split, "metric_source": source,
                     "dataset": ds, "epochs": epochs, "seed": seed,
                     "family": family_dir.name, "nrmse_def_hash": NRMSE_DEF_HASH,
                     "copylf_def_hash": COPYLF_DEF_HASH, "env": env or {}},
                    f,
                )
        ref = baselines[ds]["test_nrmse"]
        per_dataset[ds] = {
            "nRMSE": value,
            "skill": value / ref,
            "reference_type": baselines[ds]["reference_type"],
            "split": split,
            "metric_source": source,
            "cached": cached,
        }

    gm = math.exp(sum(math.log(d["skill"]) for d in per_dataset.values()) / len(per_dataset))
    return {
        "family": family_dir.name,
        "epochs": epochs,
        "seed": seed,
        "env": env or {},
        "nrmse_def_hash": NRMSE_DEF_HASH,
        "copylf_def_hash": COPYLF_DEF_HASH,
        "code_hash": chash,
        "per_dataset": per_dataset,
        "panel_geomean_skill": gm,
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--family_dir", required=True)
    p.add_argument("--datasets", required=True,
                   help="comma-separated names, or 'panel' / 'guard'")
    p.add_argument("--epochs", type=int, required=True)
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--out")
    p.add_argument("--env", nargs="*", default=[], metavar="KEY=VAL")
    p.add_argument("--no_cache", action="store_true")
    args = p.parse_args()

    cfg = load_config()
    if args.datasets == "panel":
        datasets = list(cfg["panel"])
    elif args.datasets == "guard":
        datasets = list(cfg["guard_set"])
    else:
        datasets = [d for d in args.datasets.split(",") if d]

    env = {}
    for item in args.env:
        if "=" not in item:
            raise SystemExit(f"--env expects KEY=VAL, got {item!r}")
        k, v = item.split("=", 1)
        env[k] = v

    res = score_family(args.family_dir, datasets, args.epochs, args.seed,
                       env=env, use_cache=not args.no_cache)
    text = json.dumps(res, indent=2, sort_keys=True)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text)
    print(text)


if __name__ == "__main__":
    main()
