import numpy as np
import pytest
import sys, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from nrmse import nrmse, skill, panel_geomean, bootstrap_ci, NRMSE_DEF_HASH


def test_nrmse_zero_for_perfect_prediction():
    y = np.random.default_rng(0).normal(size=(5, 64))
    assert nrmse(y, y) == pytest.approx(0.0)


def test_nrmse_one_for_zero_prediction():
    y = np.random.default_rng(0).normal(size=(5, 64))
    assert nrmse(np.zeros_like(y), y) == pytest.approx(1.0)


def test_nrmse_is_mean_of_per_sample_ratios():
    y = np.ones((2, 4))
    p = y.copy()
    p[1] *= 3.0  # sample errors: 0 and 2
    assert nrmse(p, y) == pytest.approx(1.0)


def test_nrmse_rejects_shape_mismatch_and_nan():
    y = np.ones((2, 4))
    with pytest.raises(ValueError):
        nrmse(np.ones((2, 5)), y)
    bad = y.copy()
    bad[0, 0] = np.nan
    with pytest.raises(ValueError):
        nrmse(bad, y)


def test_skill_and_geomean():
    assert skill(0.05, 0.10) == pytest.approx(0.5)
    with pytest.raises(ValueError):
        skill(0.05, 0.0)
    assert panel_geomean({"a": 0.25, "b": 4.0}) == pytest.approx(1.0)
    with pytest.raises(ValueError):
        panel_geomean({})


def test_bootstrap_ci_brackets_mean_and_is_deterministic():
    vals = [0.10, 0.12, 0.11]
    m, lo, hi = bootstrap_ci(vals)
    assert lo <= m <= hi and m == pytest.approx(np.mean(vals))
    assert bootstrap_ci(vals) == bootstrap_ci(vals)


def test_def_hash_is_stable_sha256():
    assert len(NRMSE_DEF_HASH) == 64
