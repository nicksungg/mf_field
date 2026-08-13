"""A2: staging manifest builder (spec D1, D12, G0).

The manifest is the campaign's identity: per-dataset file hashes + a
hub-identity tripwire, written PROVISIONAL (unsealed, no manifest_hash) —
the final identity exists only after the stripped views do (spec D12, A6).
All fixture data here is generated in-test and FIXTURE-marked; real arrays
are never committed (.gitignore excludes them anyway).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

CAMPAIGN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CAMPAIGN))

from staging.manifest import build_dataset_record, build_manifest, verify_against  # noqa: E402


def _mk_fixture_dataset(root: Path, name: str = "fixture_ds") -> Path:
    """FIXTURE: tiny npz_l dataset, deterministic content."""
    d = root / name
    d.mkdir(parents=True)
    rng = np.random.default_rng(0)
    for split in ("train", "test"):
        for lvl in (1, 2):
            n = 4 * lvl * lvl
            np.savez(d / f"{split}_l{lvl}.npz",
                     x=rng.random((3, 2)), y=rng.random((3, n)))
    (d / "meta.json").write_text(json.dumps({"FIXTURE": True, "name": name}))
    return d


@pytest.fixture()
def fixture_cfg(tmp_path):
    _mk_fixture_dataset(tmp_path)
    return {
        "data_root": str(tmp_path),
        "datasets": {"core": [{"id": "fixture_ds", "dataset_dir": "fixture_ds"}]},
    }


def test_record_is_deterministic_and_complete(fixture_cfg):
    root = Path(fixture_cfg["data_root"])
    r1 = build_dataset_record("fixture_ds", root / "fixture_ds")
    r2 = build_dataset_record("fixture_ds", root / "fixture_ds")
    assert r1 == r2
    assert r1["layout"] == "npz_l"
    assert r1["n_levels"] == 2
    assert set(r1["files"]) == {"train_l1.npz", "train_l2.npz",
                                "test_l1.npz", "test_l2.npz", "meta.json"}
    assert all(len(h) == 64 for h in r1["files"].values())
    assert len(r1["content_hash"]) == 64
    assert r1["hub_identity"] == "identical_to_hf_benchmark30"
    # top-rung cells recorded: fixture l2 has n = 4*2*2 = 16 cells
    assert r1["n_cells_top"] == 16


def test_manifest_is_provisional(fixture_cfg, tmp_path):
    m = build_manifest(fixture_cfg)
    assert m["sealed"] is False
    assert m["manifest_hash"] is None
    assert list(m["datasets"]) == ["fixture_ds"]


def test_content_hash_changes_on_byte_change(fixture_cfg):
    root = Path(fixture_cfg["data_root"])
    before = build_dataset_record("fixture_ds", root / "fixture_ds")["content_hash"]
    p = root / "fixture_ds" / "train_l1.npz"
    p.write_bytes(p.read_bytes() + b"\x00")
    after = build_dataset_record("fixture_ds", root / "fixture_ds")["content_hash"]
    assert before != after


def test_verify_against_trips_on_divergence(fixture_cfg):
    m = build_manifest(fixture_cfg)
    ok, diffs = verify_against(fixture_cfg, m)
    assert ok and diffs == []
    p = Path(fixture_cfg["data_root"]) / "fixture_ds" / "test_l2.npz"
    p.write_bytes(p.read_bytes() + b"\x00")
    ok, diffs = verify_against(fixture_cfg, m)
    assert not ok
    assert any("fixture_ds" in d for d in diffs)
