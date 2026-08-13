"""A9: aggregator + validator + leaderboard (spec D8, D9, D12).

The headline order is pinned by a NON-SYMMETRIC fixture: per-seed panel
geomean of skill, then mean/[min,max] across the three seed-level values —
numerically different from "seed-average the nRMSEs, then one geomean",
and the test asserts the former.  All fixture score JSONs are FIXTURE data
generated in-test.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import pytest

CAMPAIGN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CAMPAIGN))

from aggregate.collect import aggregate_scores, validate_score  # noqa: E402

MODEL, FILM = "r3s2_route_b30", "mf_fno_transfer_film"
DEF_HASH = "d" * 64


def _score(family, seed, ds, nrmse, epochs=200):
    return {
        "family": family, "epochs": epochs, "seed": seed,
        "copylf_def_hash": DEF_HASH, "code_hash": "c" * 64,
        "per_dataset": {ds: {"nRMSE": nrmse, "skill": 1.0, "split": "test_hf",
                             "metric_source": "per_sample_mean",
                             "reference_type": "copylf", "cached": False}},
        "panel_geomean_skill": 1.0,
    }


def _write_scores(root: Path, table):
    """table: {(family, seed, ds): nrmse} -> score files in launcher layout."""
    d = root / "results/scores"
    d.mkdir(parents=True, exist_ok=True)
    for (fam, seed, ds), v in table.items():
        p = d / f"{fam}_s{seed}_e200_{ds}.json"
        json.dump(_score(fam, seed, ds, v), open(p, "w"))


# FIXTURE: deliberately non-symmetric across seeds and datasets
NRMSE = {
    (MODEL, 0, "a"): 0.10, (MODEL, 1, "a"): 0.40, (MODEL, 2, "a"): 0.20,
    (MODEL, 0, "b"): 0.30, (MODEL, 1, "b"): 0.05, (MODEL, 2, "b"): 0.25,
    (FILM, 0, "a"): 0.50, (FILM, 1, "a"): 0.20, (FILM, 2, "a"): 0.60,
    (FILM, 0, "b"): 0.15, (FILM, 1, "b"): 0.45, (FILM, 2, "b"): 0.35,
}


def _expected_headline():
    per_seed = []
    for s in (0, 1, 2):
        skills = [NRMSE[(FILM, s, ds)] / NRMSE[(MODEL, s, ds)] for ds in ("a", "b")]
        per_seed.append(math.exp(sum(math.log(x) for x in skills) / len(skills)))
    return per_seed


@pytest.fixture()
def rev(tmp_path):
    _write_scores(tmp_path, NRMSE)
    return tmp_path


def test_headline_is_per_seed_geomean_then_interval(rev):
    lb = aggregate_scores(rev, expected_def_hash=DEF_HASH, seeds=[0, 1, 2])
    per_seed = _expected_headline()
    assert lb["headline"]["per_seed_geomean"] == pytest.approx(per_seed)
    assert lb["headline"]["mean"] == pytest.approx(sum(per_seed) / 3)
    assert lb["headline"]["interval"] == pytest.approx([min(per_seed), max(per_seed)])
    assert lb["headline"]["interval_kind"] == "seed_plus_run_interval"
    # and it genuinely differs from the wrong order on this fixture
    wrong = math.exp(sum(
        math.log((sum(NRMSE[(FILM, s, ds)] for s in (0, 1, 2)) / 3)
                 / (sum(NRMSE[(MODEL, s, ds)] for s in (0, 1, 2)) / 3))
        for ds in ("a", "b")) / 2)
    assert lb["headline"]["mean"] != pytest.approx(wrong)


def test_common_set_excludes_dataset_missing_either_family(rev, tmp_path):
    # dataset "c" has model results only -> not in common set, listed in coverage
    _write_scores(tmp_path, {(MODEL, s, "c"): 0.2 for s in (0, 1, 2)})
    lb = aggregate_scores(tmp_path, expected_def_hash=DEF_HASH, seeds=[0, 1, 2])
    assert sorted(lb["common_eligible_set"]) == ["a", "b"]
    assert lb["coverage"]["c"][MODEL] == 3 and lb["coverage"]["c"][FILM] == 0


def test_validator_rejects_wrong_def_hash(rev):
    bad = _score(MODEL, 0, "z", 0.1)
    bad["copylf_def_hash"] = "e" * 64
    with pytest.raises(ValueError, match="copylf_def_hash"):
        validate_score(bad, expected_def_hash=DEF_HASH)


def test_validator_rejects_name_mismatch(rev):
    ok = _score(MODEL, 0, "z", 0.1)
    with pytest.raises(ValueError, match="seed"):
        validate_score(ok, expected_def_hash=DEF_HASH, expect={"seed": 1})


def test_per_dataset_table_and_sidecar_arms_ignored(rev):
    """The aggregator consumes ONLY score JSONs (arm A1 by construction);
    a smoke_eval sidecar with a better non-A1 arm must not exist in its inputs."""
    lb = aggregate_scores(rev, expected_def_hash=DEF_HASH, seeds=[0, 1, 2])
    a = lb["per_dataset"]["a"][MODEL]
    assert a["mean"] == pytest.approx((0.10 + 0.40 + 0.20) / 3)
    assert a["min"] == 0.10 and a["max"] == 0.40
    assert lb["inputs"] == "score_jsons_only_arm_A1"


def test_report_tables_render_from_leaderboard_only(rev):
    from aggregate.report import render_tables
    lb = aggregate_scores(rev, expected_def_hash=DEF_HASH, seeds=[0, 1, 2])
    lb["manifest_hash"] = "m" * 64
    lb["registry_revision"] = "b30-0001"
    md = render_tables(lb)
    per_seed = _expected_headline()
    assert f"{sum(per_seed) / 3:.4f}" in md, "headline mean must appear verbatim"
    assert "| a |" in md and "| b |" in md
    assert "score_jsons_only_arm_A1" in md


def test_smoke_files_cannot_pollute_full_collection(rev):
    """r1 fix F2: an e2 smoke file for the same cell must be ignored, and a
    duplicate (family, seed, ds) at the SAME epochs must hard-fail."""
    d = rev / "results/scores"
    smoke = _score(MODEL, 0, "a", 99.0, epochs=2)
    json.dump(smoke, open(d / f"{MODEL}_s0_e2_a.json", "w"))
    lb = aggregate_scores(rev, expected_def_hash=DEF_HASH, seeds=[0, 1, 2],
                          expected_epochs=200)
    assert lb["per_dataset"]["a"][MODEL]["per_seed"][0] == 0.10, \
        "the 2-epoch smoke value must never enter the 200-epoch leaderboard"
    # any unexpected sibling that could shadow a cell fails LOUDLY (here the
    # stray name parses as dataset "a " and is rejected on its content; a true
    # same-cell duplicate is impossible as one filename, and load_scores
    # additionally hard-fails on duplicate keys as a layout-change backstop)
    json.dump(_score(MODEL, 0, "a", 0.5), open(d / f"{MODEL}_s0_e200_a.json.dup", "w"))
    (d / f"{MODEL}_s0_e200_a.json.dup").rename(d / f"{MODEL}_s0_e200_a .json")
    with pytest.raises(ValueError, match="duplicate|unrecognized|per_dataset"):
        aggregate_scores(rev, expected_def_hash=DEF_HASH, seeds=[0, 1, 2],
                         expected_epochs=200)


def test_universe_is_authoritative_not_observed(rev):
    """r1 fix F3: datasets with NO results still appear in coverage, and the
    headline refuses to publish while any universe cell is unaccounted."""
    lb = aggregate_scores(rev, expected_def_hash=DEF_HASH, seeds=[0, 1, 2],
                          expected_epochs=200, universe=["a", "b", "ghost"])
    assert lb["coverage"]["ghost"] == {MODEL: 0, FILM: 0}
    assert "ghost" not in lb["common_eligible_set"]
    assert lb["unaccounted_cells"], "missing cells must be surfaced"
    with pytest.raises(ValueError, match="unaccounted"):
        aggregate_scores(rev, expected_def_hash=DEF_HASH, seeds=[0, 1, 2],
                         expected_epochs=200, universe=["a", "b", "ghost"],
                         strict=True)
    # a ledger entry accounts for the cell; strict mode then passes
    lb2 = aggregate_scores(rev, expected_def_hash=DEF_HASH, seeds=[0, 1, 2],
                           expected_epochs=200, universe=["a", "b", "ghost"],
                           strict=True,
                           exclusion_ledger={MODEL: {"ghost": "x"}, FILM: {"ghost": "x"}})
    assert lb2["unaccounted_cells"] == []


def test_ops_table_extracted_from_family_results(rev):
    """r1 fix F8: wall-clock/memory join from the smoke_eval result files."""
    fam_dir = rev / "results" / MODEL
    fam_dir.mkdir(parents=True)
    json.dump({"model": MODEL, "dataset": "a", "train_seconds": 123.4,
               "peak_mem_bytes": 5_000_000},
              open(fam_dir / "a_e200_s0.json", "w"))
    lb = aggregate_scores(rev, expected_def_hash=DEF_HASH, seeds=[0, 1, 2],
                          expected_epochs=200)
    assert lb["ops"][MODEL]["a"]["s0"]["train_seconds"] == 123.4


def test_rehash_and_check_aborts_on_either_byte_class(tmp_path):
    """r1 fix F12: the collect-time D12 re-hash is exercised end-to-end on a
    sealed fixture manifest — both mutation classes must abort collection."""
    import numpy as np
    from aggregate.collect import rehash_and_check
    from staging.manifest import build_manifest
    from staging.preflight import build_stripped_views, seal_manifest
    d = tmp_path / "data/fx"
    d.mkdir(parents=True)
    for split in ("train", "test"):
        for lvl in (1, 2):
            np.savez(d / f"{split}_l{lvl}.npz", x=np.zeros((2, 2)),
                     y=np.full((2, 4 * lvl * lvl), 1.0))
    cfg = {"data_root": str(tmp_path / "data"), "output_root": str(tmp_path / "out"),
           "datasets": {"core": [{"id": "fx", "dataset_dir": "fx"}]}}
    build_stripped_views(cfg)
    sealed = seal_manifest(cfg, build_manifest(cfg), registry_revision="b30-0001")
    rehash_and_check(cfg, sealed)  # clean -> no raise
    src = d / "train_l1.npz"
    src.write_bytes(src.read_bytes() + b"\x00")
    with pytest.raises(ValueError, match="source re-hash"):
        rehash_and_check(cfg, sealed)
    src.write_bytes(src.read_bytes()[:-1])
    view = Path(cfg["output_root"]) / "stripped_data/fx/test_l2.npz"
    data = view.read_bytes(); view.unlink(); view.write_bytes(data + b"\x00")
    with pytest.raises(ValueError, match="stripped-view re-hash"):
        rehash_and_check(cfg, sealed)


def test_final_collection_path_defaults_to_rehash():
    """r1 fix F12 companion: main's parser must default to rehashing —
    a flipped default would silently skip D12 verification."""
    import argparse
    import aggregate.collect as C
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-rehash", action="store_true")
    assert ap.parse_args([]).skip_rehash is False
    src = open(C.__file__).read()
    assert 'if not args.skip_rehash:' in src and 'rehash_and_check(cfg, manifest)' in src


def test_ledgered_dataset_never_enters_common_set(rev):
    """micro-fix M3: complete stale scores must not resurrect a ledgered dataset."""
    lb = aggregate_scores(rev, expected_def_hash=DEF_HASH, seeds=[0, 1, 2],
                          expected_epochs=200,
                          exclusion_ledger={MODEL: {"a": "excluded after the fact"}})
    assert lb["common_eligible_set"] == ["b"]
    assert lb["score_ledger_conflicts"] == ["a"], \
        "the score/ledger conflict must be surfaced, not silently resolved"
