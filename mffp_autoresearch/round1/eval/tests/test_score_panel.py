import json
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from score_panel import ScoreContractError, score_family

FAKE = pathlib.Path(__file__).resolve().parent / "fake_family"

# Two datasets with copylf reference + the paper_bar one.
DS2 = ["ext__helmholtz_2d", "sharp__cahn_hilliard"]


@pytest.fixture()
def isolated_dirs(tmp_path, monkeypatch):
    monkeypatch.setenv("ROUND1_EVAL_CACHE", str(tmp_path / "cache"))
    monkeypatch.setenv("ROUND1_EVAL_RESULTS", str(tmp_path / "results"))
    return tmp_path


def test_happy_path_scores_and_geomean(isolated_dirs):
    res = score_family(FAKE, DS2, epochs=2, seed=0)
    baselines = json.load(open(pathlib.Path(__file__).resolve().parents[1] / "copylf_baselines.json"))
    for ds in DS2:
        expected = 0.5 / baselines[ds]["test_nrmse"]
        assert res["per_dataset"][ds]["nRMSE"] == pytest.approx(0.5)
        assert res["per_dataset"][ds]["skill"] == pytest.approx(expected)
        assert res["per_dataset"][ds]["cached"] is False
    import math
    expected_gm = math.exp(
        sum(math.log(res["per_dataset"][d]["skill"]) for d in DS2) / len(DS2)
    )
    assert res["panel_geomean_skill"] == pytest.approx(expected_gm)
    assert len(res["nrmse_def_hash"]) == 64
    assert len(res["code_hash"]) == 64


def test_paper_bar_dataset_scores(isolated_dirs):
    res = score_family(FAKE, ["ifc_poisson"], epochs=2, seed=0)
    assert res["per_dataset"]["ifc_poisson"]["skill"] == pytest.approx(0.5 / 0.036)


def test_cache_hits_and_env_knob_invalidates(isolated_dirs):
    r1 = score_family(FAKE, DS2[:1], epochs=2, seed=0)
    assert r1["per_dataset"][DS2[0]]["cached"] is False
    r2 = score_family(FAKE, DS2[:1], epochs=2, seed=0)
    assert r2["per_dataset"][DS2[0]]["cached"] is True
    # env knob changes the key AND the value
    r3 = score_family(FAKE, DS2[:1], epochs=2, seed=0, env={"FAKE_NRMSE": "0.25"})
    assert r3["per_dataset"][DS2[0]]["cached"] is False
    assert r3["per_dataset"][DS2[0]]["nRMSE"] == pytest.approx(0.25)


def test_cache_invalidates_on_code_change(isolated_dirs, tmp_path):
    import shutil

    fam = tmp_path / "fam_copy"
    shutil.copytree(FAKE, fam)
    r1 = score_family(fam, DS2[:1], epochs=2, seed=0)
    assert r1["per_dataset"][DS2[0]]["cached"] is False
    (fam / "extra_module.py").write_text("# new code\n")
    r2 = score_family(fam, DS2[:1], epochs=2, seed=0)
    assert r2["per_dataset"][DS2[0]]["cached"] is False


@pytest.mark.parametrize("mode", ["missing_key", "wrong_dataset", "nan"])
def test_contract_violations_raise(isolated_dirs, mode):
    with pytest.raises(ScoreContractError):
        score_family(FAKE, DS2[:1], epochs=2, seed=0, env={"FAKE_BREAK": mode})


def test_unknown_dataset_raises(isolated_dirs):
    with pytest.raises(ScoreContractError):
        score_family(FAKE, ["not_a_dataset"], epochs=2, seed=0)


def test_test_hf_split_with_per_sample_array_preferred(isolated_dirs):
    # Factory families (via data_adapters.metrics.finalize_and_write) emit
    # splits.test_hf with BOTH an aggregate ratio-of-sums nRMSE and the
    # per-sample rel-L2 array. The round's definition is the per-sample MEAN,
    # so the array must win over the aggregate.
    res = score_family(FAKE, DS2[:1], epochs=2, seed=0,
                       env={"FAKE_MODE": "factory_style"})
    entry = res["per_dataset"][DS2[0]]
    assert entry["nRMSE"] == pytest.approx(0.3)  # mean([0.2, 0.4]), NOT 0.9
    assert entry["metric_source"] == "per_sample_mean"
    assert entry["split"] == "test_hf"


def test_plain_test_split_falls_back_to_reported_nrmse(isolated_dirs):
    res = score_family(FAKE, DS2[:1], epochs=2, seed=0)
    entry = res["per_dataset"][DS2[0]]
    assert entry["metric_source"] == "reported_nRMSE"
    assert entry["split"] == "test"


def test_no_test_split_raises(isolated_dirs):
    with pytest.raises(ScoreContractError):
        score_family(FAKE, DS2[:1], epochs=2, seed=0,
                     env={"FAKE_MODE": "ood_only"})
