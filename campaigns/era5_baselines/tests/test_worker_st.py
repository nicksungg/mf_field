"""Focused checks for protocol separation and the seven released arm adapters."""
from __future__ import annotations

import importlib
from pathlib import Path
import sys
from types import SimpleNamespace

import numpy as np
import pytest
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import worker_st as worker


@pytest.fixture
def tiny_data():
    generator = torch.Generator().manual_seed(11)
    torch.set_num_threads(1)
    xhf = torch.randn(10, 2, generator=generator)
    xlf = torch.randn(12, 2, generator=generator)
    pattern = torch.linspace(-0.2, 0.3, 32).reshape(1, 4, 8)
    yhf = 2.0 + xhf[:, :1, None] * pattern + xhf[:, 1:, None] * 0.05
    ylfup = 1.8 + xlf[:, :1, None] * pattern + xlf[:, 1:, None] * 0.04
    return {
        "cond_dim": 2, "grid": (4, 8), "grid_lf": (2, 4),
        "registration": "generic", "paired": False,
        "X_hf": xhf, "Y_hf": yhf, "hf_tr": np.arange(8), "hf_va": np.arange(8, 10),
        "X_lf": xlf, "Y_lf": ylfup[:, ::2, ::2], "Y_lf_up": ylfup,
        "lf_tr": np.arange(10), "lf_va": np.arange(10, 12),
        "Xtest": torch.randn(3, 2, generator=generator),
        "Ytest": torch.zeros(3, 4, 8), "Ytest_lf_up": None,
    }


def test_production_arguments_match_release(monkeypatch):
    worker.import_released()
    released = importlib.import_module("run_st")
    for model in worker.MODELS:
        monkeypatch.setattr(sys, "argv", ["run_st", "--dataset", "core/era5", "--arm", model, "--out-dir", "/tmp/unused"])
        original = released.parse()
        actual = worker.training_arguments(model)
        for key in ("seed", "pod_modes", "pod_energy", "gp_restarts", "nargp_samples", "nargp_lf_modes", "steps", "batch", "points", "hidden", "sensors", "lr", "wd", "eval_every"):
            assert getattr(actual, key) == getattr(original, key), (model, key)
        assert actual.latent == (32 if model in worker.CLASSICAL or model == "st_dmfal" else 128)


def test_query_answers_discarded(tiny_data):
    worker.discard_query_targets(tiny_data)
    assert "Ytest" not in tiny_data
    assert "Ytest_lf_up" not in tiny_data


@pytest.mark.parametrize("value", [1.0, float("nan"), float("inf")])
def test_real_or_invalid_query_targets_rejected(tiny_data, value):
    tiny_data["Ytest"][0, 0, 0] = value
    with pytest.raises(ValueError, match="zero placeholders"):
        worker.discard_query_targets(tiny_data)


def test_query_low_fidelity_answers_rejected(tiny_data):
    tiny_data["Ytest_lf_up"] = torch.ones(3, 4, 8)
    with pytest.raises(ValueError, match="low fidelity"):
        worker.discard_query_targets(tiny_data)


def test_smoke_gp_patch_restores_after_failure():
    common, classical, _ = worker.import_released()
    originals = common.fit_gp, classical.fit_gp
    with pytest.raises(RuntimeError):
        with worker.smoke_gp_iterations(common, classical, True):
            assert common.fit_gp is classical.fit_gp
            assert common.fit_gp is not originals[0]
            raise RuntimeError("intentional smoke failure")
    assert (common.fit_gp, classical.fit_gp) == originals


def test_production_gp_optimizer_not_replaced():
    common, classical, _ = worker.import_released()
    originals = common.fit_gp, classical.fit_gp
    with worker.smoke_gp_iterations(common, classical, False):
        assert (common.fit_gp, classical.fit_gp) == originals


@pytest.mark.parametrize("model", worker.MODELS)
def test_all_arms_predict_without_query_answers(tiny_data, model):
    worker.discard_query_targets(tiny_data)
    args = worker.training_arguments(model, smoke=True)
    # Synthetic integration fixture keeps the full execution paths inexpensive.
    args.hidden, args.latent, args.sensors = [8], 4, 4
    args.points, args.pod_modes = 4, 4
    pred, extra, _ = worker.fit_arm(tiny_data, args, torch.device("cpu"), smoke=True)
    assert pred.shape == (3, 4, 8)
    assert torch.isfinite(pred).all()
    assert "plugin_test_rel_l2" not in extra
    if model in worker.NEURAL:
        assert extra["selected_step"] in (1, 2)
        assert np.isfinite(extra["best_val_rel_l2"])
    if model == "st_nargp_pod":
        assert extra["plugin_test_diagnostic_omitted"] == "query answers withheld from training worker"


def test_smoke_subset_does_not_mutate_input(tiny_data):
    before = tiny_data["hf_tr"].copy()
    selected = worker.smoke_classical_data(tiny_data)
    assert selected is not tiny_data
    assert np.array_equal(tiny_data["hf_tr"], before)
    assert selected["Xtest"] is tiny_data["Xtest"]
    assert selected["grid"] == tiny_data["grid"]


def test_production_budget_cannot_be_overridden():
    with pytest.raises(SystemExit):
        worker.parse_args(["--model", "st_mfdnn", "--steps", "2"])


def test_no_query_scoring_diagnostic_remains_in_classical_source():
    source = (ROOT / "vendor" / "st_bench" / "st_classical.py").read_text()
    assert 'data["Ytest"]' not in source
    assert "plugin_test_rel_l2" not in source
