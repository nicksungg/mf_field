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


def test_committed_artifact_matches_full_regeneration():
    """r1 fix F11: the COMMITTED state/copylf_baselines.json is the artifact
    the scorer trusts — a hand-edited value must fail here.  Full 30-dataset
    regeneration (slow, ~1-2 min) compared entry-by-entry."""
    committed_path = CAMPAIGN / "state/copylf_baselines.json"
    assert committed_path.exists(), "G2 artifact missing"
    committed = json.load(open(committed_path))
    fresh = build_all()
    assert set(committed) == set(fresh), "dataset key sets differ"
    for k in fresh:
        if k.startswith("_"):
            assert committed[k] == fresh[k], f"metadata field {k} differs"
            continue
        assert set(committed[k]) == set(fresh[k]), f"{k}: entry key sets differ"
        for field in fresh[k]:
            c, f = committed[k][field], fresh[k][field]
            if isinstance(f, float):
                assert c == pytest.approx(f, rel=1e-9), \
                    f"{k}.{field}: committed {c} != regenerated {f}"
            else:
                assert c == f, f"{k}.{field}: committed {c!r} != regenerated {f!r}"


def test_campaign_floors_match_certified_for_overlap():
    """G3-fix: the campaign floors builder must reproduce the certified
    round-3 floors for every overlapping dataset (construction equivalence),
    and the committed campaign floors file must match a fresh rebuild."""
    from eval.make_floors_b30 import FLOORS_OUT, CERTIFIED, build_all
    cert = json.load(open(CERTIFIED))
    overlap = [k for k in cert if not k.startswith("_")]
    fresh = build_all(only=overlap)
    for ds in overlap:
        for arm in ("nn_condition", "train_mean", "zero"):
            # rel=1e-6: BLAS reduction-order noise across nodes (~1e-9 observed
            # on ifc_heat) stays far below it; construction changes do not.
            assert fresh[ds][arm]["nrmse"] == pytest.approx(
                cert[ds][arm]["nrmse"], rel=1e-6), \
                f"{ds}.{arm}: campaign construction diverges from certified floors"
    assert FLOORS_OUT.exists(), "committed campaign floors file missing (run make_floors_b30)"
    committed = json.load(open(FLOORS_OUT))
    for ds in overlap:
        assert committed[ds]["nn_condition"]["nrmse"] == pytest.approx(
            fresh[ds]["nn_condition"]["nrmse"], rel=1e-9)
    missing = [k for k in ("era5",) if k not in committed and k not in committed.get("_errors", {})]
    assert not missing, f"floors neither built nor errored for {missing}"


def test_family_collect_finds_campaign_floors():
    """The frozen family's own floor_arms.collect must find the campaign file
    at roots[0] (the vendored-depth quirk this fix relies on)."""
    import importlib.util
    fam = CAMPAIGN / "family/r3s2_route_b30"
    spec = importlib.util.spec_from_file_location("b30_floorlib", fam / "floor_arms.py")
    fl = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fl)
    roots = [CAMPAIGN, Path("/resnick/groups/Hippo/ezeng/mf_field")]
    got = fl.collect("poisson_generated", roots,
                     "nn_condition,train_mean,zero,affine_on_hf_train")
    assert got["nn_condition"]["nrmse"] > 0
    assert got["affine_on_hf_train"]["applicable"] is False, \
        "non-ifc datasets get the frozen not-applicable affine fallback"
    assert str(CAMPAIGN) in got["_source"]["floors_file"], \
        "the campaign floors file must win over the round-3 one (roots order)"
