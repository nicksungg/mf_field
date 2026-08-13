"""Staging manifest builder (spec D1, D12, G0).

Writes the campaign's identity: per-dataset file hashes plus a hub-identity
tripwire.  The manifest is PROVISIONAL here (``sealed: false``, no
``manifest_hash``): the final identity covers the stripped views too and can
only be computed after they exist (spec D12; sealing happens in the A6
preflight, not here).

``verify_against`` is the tripwire: staging re-runs it before every launch,
and any divergence between disk and the committed record fails loudly —
a local regeneration cannot silently change what "benchmark_30" means.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

HUB_IDENTITY = "identical_to_hf_benchmark30"


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def _detect_layout(dataset_dir: Path) -> str:
    if (dataset_dir / "train").is_dir():
        return "ifc_raw"
    if list(dataset_dir.glob("train_l*.npz")):
        return "npz_l"
    raise ValueError(f"{dataset_dir}: neither ifc_raw nor npz_l layout found")


def _top_rung_cells(dataset_dir: Path, layout: str) -> int:
    if layout == "npz_l":
        top = max(dataset_dir.glob("train_l*.npz"),
                  key=lambda p: int(p.stem.split("_l")[-1]))
        with np.load(top) as z:
            y = z["y"]
            return int(np.prod(y.shape[1:]))
    tops = sorted((dataset_dir / "train").iterdir())
    ys = np.load(tops[-1] / "ys.npy", mmap_mode="r")
    return int(np.prod(ys.shape[1:]))


def build_dataset_record(dataset_id: str, dataset_dir: Path) -> dict:
    dataset_dir = Path(dataset_dir)
    if not dataset_dir.is_dir():
        raise ValueError(f"{dataset_id}: dataset dir missing at {dataset_dir}")
    files = {}
    for p in sorted(dataset_dir.rglob("*")):
        if p.is_file():
            files[str(p.relative_to(dataset_dir))] = _sha256_file(p)
    content_hash = hashlib.sha256(
        "\n".join(f"{rel}\t{h}" for rel, h in sorted(files.items())).encode()
    ).hexdigest()
    layout = _detect_layout(dataset_dir)
    return {
        "dataset": dataset_id,
        "dataset_dir": str(dataset_dir),
        "layout": layout,
        "n_levels": len(list(dataset_dir.glob("train_l*.npz"))) or None,
        "n_cells_top": _top_rung_cells(dataset_dir, layout),
        "files": files,
        "content_hash": content_hash,
        "hub_identity": HUB_IDENTITY,
    }


def _iter_datasets(cfg: dict):
    root = Path(cfg["data_root"])
    for group in cfg["datasets"].values():
        for d in group:
            yield d["id"], root / d["dataset_dir"]


def build_manifest(cfg: dict) -> dict:
    return {
        "campaign": "benchmark_30",
        "sealed": False,
        "manifest_hash": None,
        "registry_revision": None,
        "stripped_view_hashes": None,
        "datasets": {ds_id: build_dataset_record(ds_id, ds_dir)
                     for ds_id, ds_dir in _iter_datasets(cfg)},
    }


def verify_against(cfg: dict, committed: dict) -> tuple[bool, list[str]]:
    """Tripwire: recompute per-dataset content hashes and diff the record."""
    diffs = []
    fresh = {ds_id: build_dataset_record(ds_id, ds_dir)
             for ds_id, ds_dir in _iter_datasets(cfg)}
    for ds_id, rec in committed["datasets"].items():
        f = fresh.get(ds_id)
        if f is None:
            diffs.append(f"{ds_id}: missing on disk")
        elif f["content_hash"] != rec["content_hash"]:
            diffs.append(f"{ds_id}: content_hash diverged from committed manifest "
                         f"({f['content_hash'][:12]} != {rec['content_hash'][:12]})")
    for ds_id in fresh:
        if ds_id not in committed["datasets"]:
            diffs.append(f"{ds_id}: on disk but absent from committed manifest")
    return (not diffs), diffs


def main() -> None:
    import argparse
    import yaml
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default=str(Path(__file__).parents[1] / "config.yaml"))
    ap.add_argument("--out", default=str(Path(__file__).parents[1] / "state/staging_manifest.json"))
    args = ap.parse_args()
    with open(args.config) as f:
        cfg = yaml.safe_load(f)
    m = build_manifest(cfg)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        json.dump(m, f, indent=1, sort_keys=True)
    print(f"provisional manifest: {len(m['datasets'])} datasets -> {out}")


if __name__ == "__main__":
    main()
