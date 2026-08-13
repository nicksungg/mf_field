"""A6: stripped views + LF-free audit + manifest sealing (spec D3, D6-G1, D12).

Fixture-driven: a tiny npz_l dataset (FIXTURE, generated in-test) is stripped,
audited, and sealed.  The sealing test proves BOTH byte classes (source and
stripped view) alter `manifest_hash`, and that downstream consumers refuse an
unsealed manifest.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

CAMPAIGN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CAMPAIGN))

from staging.manifest import build_manifest  # noqa: E402
from staging.preflight import (  # noqa: E402
    audit_stripped_view, build_stripped_views, require_sealed, seal_manifest,
)


def _mk_fixture_dataset(root: Path, name: str = "fixture_ds") -> Path:
    d = root / name
    d.mkdir(parents=True)
    rng = np.random.default_rng(1)
    for split in ("train", "test"):
        for lvl in (1, 2):
            n = 4 * lvl * lvl
            np.savez(d / f"{split}_l{lvl}.npz",
                     x=rng.random((3, 2)), y=rng.random((3, n)))
    (d / "meta.json").write_text(json.dumps({"FIXTURE": True}))
    return d


@pytest.fixture()
def env(tmp_path):
    _mk_fixture_dataset(tmp_path / "data")
    cfg = {
        "data_root": str(tmp_path / "data"),
        "output_root": str(tmp_path / "out"),
        "datasets": {"core": [{"id": "fixture_ds", "dataset_dir": "fixture_ds"}]},
    }
    return cfg, tmp_path


def test_stripped_view_drops_lf_test_only(env):
    cfg, tmp = env
    views = build_stripped_views(cfg)
    v = views["fixture_ds"]
    names = {p.name for p in Path(v).iterdir()}
    assert "test_l2.npz" in names and "test_l1.npz" not in names, \
        "test split must keep ONLY the top fidelity"
    assert {"train_l1.npz", "train_l2.npz", "meta.json"} <= names, \
        "train ladder and metadata must remain complete"


def test_audit_passes_clean_and_catches_planted_leak(env):
    cfg, tmp = env
    views = build_stripped_views(cfg)
    report = audit_stripped_view("fixture_ds", Path(views["fixture_ds"]))
    assert report["lf_free"] is True
    # plant a leak: restore the stripped LF test file inside the view
    leak = Path(views["fixture_ds"]) / "test_l1.npz"
    leak.symlink_to(Path(cfg["data_root"]) / "fixture_ds/test_l1.npz")
    with pytest.raises((SystemExit, RuntimeError), match="STRIPPING FAILED|LF"):
        audit_stripped_view("fixture_ds", Path(views["fixture_ds"]))


def test_seal_covers_both_byte_classes_and_downstream_refuses_unsealed(env):
    cfg, tmp = env
    build_stripped_views(cfg)
    m = build_manifest(cfg)
    with pytest.raises(Exception, match="unsealed|sealed"):
        require_sealed(m)
    sealed = seal_manifest(cfg, m, registry_revision="b30-0001")
    assert sealed["sealed"] is True and len(sealed["manifest_hash"]) == 64
    require_sealed(sealed)  # no raise
    h0 = sealed["manifest_hash"]

    # class 1: source byte change
    src = Path(cfg["data_root"]) / "fixture_ds/train_l1.npz"
    src.write_bytes(src.read_bytes() + b"\x00")
    m2 = build_manifest(cfg)
    h1 = seal_manifest(cfg, m2, registry_revision="b30-0001")["manifest_hash"]
    assert h1 != h0, "source byte change must alter manifest_hash"

    # class 2: stripped-view-only change (replace a symlink with altered bytes)
    view_file = Path(cfg["output_root"]) / "stripped_data/fixture_ds/test_l2.npz"
    data = view_file.read_bytes()
    view_file.unlink()
    view_file.write_bytes(data + b"\x00")
    h2 = seal_manifest(cfg, build_manifest(cfg), registry_revision="b30-0001")["manifest_hash"]
    assert h2 != h1, "stripped-view byte change must alter manifest_hash"

    # registry revision is part of the identity
    h3 = seal_manifest(cfg, build_manifest(cfg), registry_revision="b30-9999")["manifest_hash"]
    assert h3 != h2, "registry revision must alter manifest_hash"
