"""A1: campaign config contract (spec §6, D5, D6, D7, D10).

The config is the single machine-readable statement of the campaign: the 30
dataset IDs with their on-disk locations, the frozen seed/epoch protocol, and
the certified B2 recipe env captured VERBATIM (spec D5) — verified here against
the card file itself, never restated by hand.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

CAMPAIGN = Path(__file__).resolve().parents[1]
REPO = Path("/resnick/groups/Hippo/ezeng/mf_field")
B2_CARD = REPO / "mffp_autoresearch/round3/experiment_cards/r3s2_field_reach/batch_2/B2.json"

EXPECTED_GROUPS = {"core": 11, "ext": 6, "sharp": 13}
PREFLIGHT_KNOB = "R3S2_TARGET_SCALER_PREFLIGHT"
PREFLIGHT_VALUE = "not_applicable_no_helmholtz_no_pfc_in_datasets"


@pytest.fixture(scope="module")
def cfg() -> dict:
    p = CAMPAIGN / "config.yaml"
    assert p.exists(), f"campaign config missing at {p}"
    with open(p) as f:
        return yaml.safe_load(f)


def test_thirty_unique_datasets(cfg):
    ids = [d["id"] for g in cfg["datasets"].values() for d in g]
    assert len(ids) == 30
    assert len(set(ids)) == 30
    for group, n in EXPECTED_GROUPS.items():
        assert len(cfg["datasets"][group]) == n, f"{group} should have {n} datasets"


def test_every_dataset_dir_exists(cfg):
    root = Path(cfg["data_root"])
    assert root.is_dir()
    missing = [d["id"] for g in cfg["datasets"].values() for d in g
               if not (root / d["dataset_dir"]).is_dir()]
    assert not missing, f"dataset dirs missing on disk: {missing}"


def test_era5_dataset_dir_is_the_nested_subdir(cfg):
    era5 = next(d for d in cfg["datasets"]["core"] if d["id"] == "era5")
    assert era5["dataset_dir"] == "era5/era5_train_test"


def test_protocol_frozen(cfg):
    assert cfg["seeds"] == [0, 1, 2]
    assert cfg["epochs"] == {"smoke": 2, "full": 200}
    assert cfg["retry_cap"] == 3


def test_slurm_knobs(cfg):
    s = cfg["slurm"]
    assert s["partition"] == "gpu"
    assert s["gres"] == "gpu:nvidia_h200:1"
    assert s["mail_user"] == "ezeng@caltech.edu"
    assert s["mail_type"] == "END,FAIL"


def test_recipe_env_verbatim_from_b2_card(cfg):
    card_env = json.load(open(B2_CARD))["recipe"]["env"]
    assert cfg["recipe_env"] == card_env, (
        "recipe_env must be the certified B2 card env block VERBATIM (spec D5); "
        "regenerate config from the card rather than editing knobs")


def test_preflight_knob_exact_historical_string(cfg):
    assert cfg["recipe_env"][PREFLIGHT_KNOB] == PREFLIGHT_VALUE


def test_families_declared(cfg):
    fams = cfg["families"]
    assert set(fams) == {"r3s2_route_b30", "mf_fno_transfer_film"}
    film = REPO / fams["mf_fno_transfer_film"]
    assert (film / "smoke_eval.py").exists()
