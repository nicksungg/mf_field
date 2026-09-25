"""Behavioral checks of data separation, ensemble inference and persistence."""
import json

import numpy as np
import pytest

from automf import FieldDataset, FieldPredictor
from automf.data import row_keys


def dataset():
    x = np.arange(12, dtype=float).reshape(-1, 1)
    high = np.broadcast_to(2 + x[..., None], (12, 4, 6)).copy()
    xl = np.concatenate([x[::-1], [[20.], [21.]], x[:2]])
    low = np.broadcast_to(1 + xl[..., None], (len(xl), 2, 3)).copy()
    return FieldDataset(low_fidelity=(xl, low), high_fidelity=(x, high))


class FakeBackend:
    def __init__(self, y, model_id):
        self.mean = y.mean(0)
        self.offset = int(model_id[1:]) * 0.2
        self.metadata = {"test_backend": True}

    def predict(self, x):
        return np.broadcast_to(self.mean + self.offset, (len(x), *self.mean.shape)).copy()


@pytest.fixture
def captured_backend(monkeypatch):
    from automf.backends import direct
    calls = []

    def fit(model_id, low, high, config):
        calls.append((model_id, low, high, config))
        return FakeBackend(high[1], model_id)

    monkeypatch.setattr(direct, "fit_direct", fit)
    return calls


def test_auto_reservation_removes_all_fidelity_matches_and_uses_train_statistics(captured_backend):
    data = dataset()
    predictor = FieldPredictor(models=["M1", "M7"], device="cpu").fit(data, fitting_size=3)
    selected = predictor._fitting_keys
    original_hx = data.high_fidelity[0]
    expected_hx = original_hx[[key not in selected for key in row_keys(original_hx)]]
    np.testing.assert_allclose(predictor.parameter_mean_, expected_hx.mean(0))
    assert not predictor._training_keys & selected
    assert predictor.split_info_["fitting_rows"] == 3
    for _, lows, high, _ in captured_backend:
        assert len(high[0]) == 9
        for x, _ in lows:
            reconstructed = np.round(x * predictor.parameter_scale_ + predictor.parameter_mean_)
            assert not set(row_keys(reconstructed)) & selected


def test_explicit_fitting_does_not_reach_backend_and_evaluation_never_refits(captured_backend):
    data = dataset()
    fit_x = np.array([[30.], [31.]])
    fit_y = np.broadcast_to(np.array([6., 7.])[:, None, None], (2, 4, 6)).copy()
    p = FieldPredictor(models=["M1", "M7"], device="cpu").fit(data, fitting_data=(fit_x, fit_y))
    assert all(len(high[0]) == 12 for _, _, high, _ in captured_backend)
    assert all(len(lows[0][0]) == 16 for _, lows, _, _ in captured_backend)
    query = np.array([[50.], [51.]])
    predictions, weights = p.predict(query), p.weights_.copy()
    info = p.evaluate(query, np.full((2, 4, 6), 99.))
    p.evaluate(query, np.full((2, 4, 6), -99.))
    np.testing.assert_array_equal(weights, p.weights_)
    np.testing.assert_array_equal(predictions, p.predict(query))
    assert set(info["mean_relative_l2"]) == {"M1", "M7", "selected", "inverse", "fitted"}
    assert all("fitting_relative_l2" in row for row in p.leaderboard())


def test_overlap_rejected_for_explicit_fit_and_evaluate(captured_backend):
    d = dataset()
    with pytest.raises(ValueError, match="overlaps"):
        FieldPredictor(models=["M7"]).fit(d, fitting_data=(d.high_fidelity[0][:2], d.high_fidelity[1][:2]))
    p = FieldPredictor(models=["M7"]).fit(d, fitting_size=3)
    with pytest.raises(ValueError, match="overlap"):
        p.evaluate(d.high_fidelity[0], d.high_fidelity[1])
    with pytest.raises(ValueError, match="overlap"):
        p.evaluate(np.array([[20.]]), np.ones((1, 4, 6)))


def test_weights_are_fixed_across_inputs_and_grid_cells(captured_backend, tmp_path):
    p = FieldPredictor(path=tmp_path / "predictor", models=["M1", "M7"], device="cpu").fit(dataset())
    x = np.array([[40.], [41.]])
    members = p.predict_models(x)
    expected = sum(w * members[m] for m, w in zip(p.model_ids, p.weights_))
    np.testing.assert_allclose(p.predict(x), expected)
    np.testing.assert_allclose(p.weights_.sum(), 1)
    loaded = FieldPredictor.load(tmp_path / "predictor")
    np.testing.assert_array_equal(loaded.predict(x), p.predict(x))
    assert loaded.predict(np.empty((0, 1))).shape == (0, 4, 6)
    with pytest.raises(FileExistsError):
        FieldPredictor(path=tmp_path / "predictor", models=["M7"]).fit(dataset())


def test_no_fit_before_predict():
    with pytest.raises(RuntimeError, match="fit"):
        FieldPredictor(models="M7").predict(np.zeros((2, 3)))


def test_directory_manifest_accepts_flat_fields_and_multiple_unpaired_levels(tmp_path):
    x = np.arange(10.).reshape(5, 2)
    np.savez(tmp_path / "low.npz", x=x[:3], y=np.ones((3, 6)))
    np.savez(tmp_path / "middle.npz", x=x[:4], y=np.ones((4, 4, 6)))
    np.savez(tmp_path / "high.npz", x=x, y=np.ones((5, 8, 9)))
    (tmp_path / "dataset.json").write_text(json.dumps({
        "low_fidelity": [{"path": "low.npz", "grid_shape": [2, 3]}, {"path": "middle.npz"}],
        "high_fidelity": {"path": "high.npz"}}))
    loaded = FieldDataset.from_directory(tmp_path)
    assert loaded.low_fidelity[0][1].shape == (3, 2, 3)
    assert loaded.describe()["high_fidelity"]["grid"] == [8, 9]


def test_m7_predictions_do_not_depend_on_unused_low_fidelity_data():
    d = dataset()
    p = FieldPredictor(models=["M7"]).fit(d, fitting_size=3, hyperparameters={"gp_restarts": 1, "gp_maxiter": 15})
    changed = FieldDataset(low_fidelity=(np.array([[1000.], [2000.]]), np.zeros((2, 2, 3))),
                           high_fidelity=d.high_fidelity)
    q = FieldPredictor(models=["M7"]).fit(changed, fitting_size=3, hyperparameters={"gp_restarts": 1, "gp_maxiter": 15})
    x = np.array([[4.25], [7.75]])
    np.testing.assert_array_equal(p.predict(x), q.predict(x))


def test_array_like_pair_and_multiple_levels_have_the_same_interpretation():
    d = dataset()
    low_lists = [a.tolist() for a in d.low_fidelity[0]]
    from_lists = FieldDataset(low_fidelity=low_lists, high_fidelity=d.high_fidelity)
    from_levels = FieldDataset(low_fidelity=[low_lists, low_lists], high_fidelity=d.high_fidelity)
    assert len(from_lists.low_fidelity) == 1
    assert len(from_levels.low_fidelity) == 2
    np.testing.assert_array_equal(from_lists.low_fidelity[0][1], d.low_fidelity[0][1])


def test_constant_hf_parameter_does_not_explode_lf_inputs(captured_backend):
    d = dataset()
    hx, hy = d.high_fidelity
    lx, ly = d.low_fidelity[0]
    data = FieldDataset(low_fidelity=(np.c_[lx, np.ones(len(lx))], ly),
                        high_fidelity=(np.c_[hx, np.zeros(len(hx))], hy))
    p = FieldPredictor(models=["M1"], device="cpu").fit(data, fitting_size=3)
    assert p.parameter_scale_[1] == 1.0
    np.testing.assert_array_equal(captured_backend[0][1][0][0][:, 1], 1.0)


@pytest.mark.parametrize("overrides", [{"coarse_folds": 1}, {"width": 10}])
def test_corrector_config_rejected_before_any_training(overrides, captured_backend):
    with pytest.raises(ValueError, match="M8/M9"):
        FieldPredictor(models=["M1", "M8"]).fit(dataset(), hyperparameters=overrides)
    assert not captured_backend


@pytest.mark.parametrize("overrides", [{"epochs": 0}, {"gp_energy": 2}, {"typo_epochs": 10}])
def test_bad_config_fails_before_training(overrides, captured_backend):
    with pytest.raises(ValueError):
        FieldPredictor(models=["M7"]).fit(dataset(), hyperparameters=overrides)
    assert not captured_backend
