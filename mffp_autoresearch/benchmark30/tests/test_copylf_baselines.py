"""A7: campaign copy-LF baselines (spec D3, G2).

Two equivalence anchors:
- a FIXTURE dataset whose copy-LF nRMSE is hand-computable;
- a certified-panel dataset (sharp__cahn_hilliard) whose freshly computed
  value must equal the round-2 committed entry — proving the vendored
  construction is the round-2 construction end-to-end.
The ifc paper_bar entries must carry over verbatim (their test ships HF only).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

CAMPAIGN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CAMPAIGN))
ROUND2_BASELINES = Path("/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/round2/eval/copylf_baselines.json")

from eval.make_copylf_baselines_b30 import build_entry, build_all  # noqa: E402


def test_fixture_hand_computed(tmp_path):
    """Constant LF field c, HF target t: copy-LF pred is exactly c everywhere
    (any convention preserves constants), so nRMSE is computable by hand."""
    d = tmp_path / "fixture_ds"
    d.mkdir()
    c, t = 2.0, 3.0
    for split in ("train", "test"):
        np.savez(d / f"{split}_l1.npz", x=np.zeros((3, 2)), y=np.full((3, 16), c))
        np.savez(d / f"{split}_l2.npz", x=np.zeros((3, 2)), y=np.full((3, 64), t))
    test = {
        "fids": [1, 2], "hf_fid": 2, "lf_fids": [1],
        "field_by_fid": {1: np.full((3, 16), c), 2: np.full((3, 64), t)},
        "n_cells_by_fid": {1: 16, 2: 64},
        "grid_shape_by_fid": {1: (4, 4), 2: (8, 8)},
        "cond_by_fid": {2: np.zeros((3, 2))},
        "n_samples": 3,
    }
    entry = build_entry("heat_local", test)  # heat_local: legacy_cell (certified)
    expect = abs(c - t) / abs(t)  # nRMSE of constant-vs-constant
    assert entry["reference_type"] == "copylf"
    assert entry["test_nrmse"] == pytest.approx(expect, rel=1e-12)


def test_certified_dataset_matches_round2_committed():
    r2 = json.load(open(ROUND2_BASELINES))
    fresh = build_entry("sharp__cahn_hilliard")  # loads the real test split
    assert fresh["test_nrmse"] == pytest.approx(
        r2["sharp__cahn_hilliard"]["test_nrmse"], rel=1e-9), (
        "vendored construction must reproduce the round-2 committed copy-LF value")


def test_paper_bar_entries_carry_over():
    r2 = json.load(open(ROUND2_BASELINES))
    out = build_all(only=["ifc_heat", "ifc_poisson"])
    for ds in ("ifc_heat", "ifc_poisson"):
        assert out[ds]["reference_type"] == "paper_bar"
        assert out[ds]["test_nrmse"] == r2[ds]["test_nrmse"]


def test_output_carries_vendored_def_hash(tmp_path):
    out = build_all(only=["ifc_heat"])
    from eval import panel_data as vendored  # noqa: F401
    import importlib.util
    spec = importlib.util.spec_from_file_location("b30_pd_hashchk", CAMPAIGN / "eval/panel_data.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert out["_copylf_def_hash"] == mod.COPYLF_DEF_HASH
