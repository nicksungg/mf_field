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
