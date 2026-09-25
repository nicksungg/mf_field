"""Small CPU checks for complete M8/M9 inference and coarse-reference safety."""
import numpy as np
import pytest

torch = pytest.importorskip("torch")
cloudpickle = pytest.importorskip("cloudpickle")

from automf.backends import correctors


@pytest.fixture(autouse=True)
def single_cpu_thread():
    previous = torch.get_num_threads()
    torch.set_num_threads(1)
    yield
    torch.set_num_threads(previous)


def _toy_tables():
    x = np.array([[-1.0, 0.3], [-0.5, -0.2], [0.0, 0.1],
                  [0.5, 0.4], [1.0, -0.1], [1.5, 0.2]], dtype=np.float32)
    low_x = np.concatenate([x[[4, 1, 3, 0, 5, 2]], x[[0]], [[2.0, 0.5]]]).astype(np.float32)
    low_grid = np.linspace(0, 1, 12).reshape(3, 4)
    high_grid = np.linspace(0, 1, 35).reshape(5, 7)
    low_y = 1 + low_x[:, 0, None, None] * low_grid + low_x[:, 1, None, None]
    high_y = 1 + x[:, 0, None, None] * high_grid + x[:, 1, None, None] + 0.1 * high_grid**2
    return (low_x, low_y.astype(np.float32)), (x, high_y.astype(np.float32))


def test_identity_folds_exclude_all_lf_copies_and_group_hf_duplicates():
    # Rows are deliberately unpaired and the extra pool contains duplicate
    # identities. Positional split code would leak in this construction.
    low = np.array([[2.0], [0.0], [1.0], [0.0], [4.0], [3.0]])
    high = np.array([[0.0], [1.0], [2.0], [3.0], [0.0]])
    folds = correctors._coarse_folds(low, high, 3, seed=29)
    assigned = {}
    for fold, (train, held) in enumerate(folds):
        assert set(low[train, 0]).isdisjoint(high[held, 0])
        assert 4 in train  # Extra LF-only input is always available.
        for row in held:
            assigned[int(row)] = fold
    assert sorted(assigned) == list(range(len(high)))
    assert assigned[0] == assigned[4]
    assert correctors._row_keys(np.array([[0.0]])) == correctors._row_keys(np.array([[-0.0]]))


def test_oof_references_never_predict_inputs_used_to_fit_that_member(monkeypatch):
    low = np.array([[2.0], [0.0], [1.0], [0.0], [4.0], [3.0]])
    high = np.array([[0.0], [1.0], [2.0], [3.0], [0.0]])
    trained = []

    class AssertUnseenMember:
        def __init__(self, train_x, seed):
            self.identities = set(correctors._row_keys(train_x))
            self.value = seed / 1000

        def predict(self, query):
            assert self.identities.isdisjoint(correctors._row_keys(query))
            return np.full((len(query), 2, 3), self.value, dtype=np.float32)

    def fake_fit(x, y, config, seed, hetero):
        trained.append((len(x), hetero))
        return AssertUnseenMember(x, seed)

    monkeypatch.setattr(correctors, "_fit_coarse_member", fake_fit)
    ensemble, references = correctors._fit_coarse_ensemble(
        low, np.ones((len(low), 2, 3), dtype=np.float32), high,
        {"coarse_folds": 3, "coarse_members": 4, "seed": 7},
    )
    assert len(trained) == 12
    assert len(ensemble.members) == 4
    assert ensemble.metadata["inference_fold"] == 0
    assert ensemble.metadata["members_per_reference"] == ensemble.metadata["inference_member_count"]
    assert ensemble.metadata["variants"] == ["plain", "plain", "hetero", "hetero"]
    assert np.isfinite(references).all()
    np.testing.assert_array_equal(references[0], references[4])
    for fold in ensemble.metadata["folds"]:
        assert set(fold["lf_training_identity_hashes"]).isdisjoint(fold["hf_held_out_identity_hashes"])


def test_both_architectures_train_predict_native_grid_and_roundtrip(monkeypatch):
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)
    low, high = _toy_tables()
    config = {"epochs": 1, "corrector_epochs": 1, "batch_size": 3,
              "seed": 11, "device": "auto", "width": 8, "blocks": 1,
              "modes": 2, "coarse_members": 2, "coarse_folds": 2,
              "correction_steps": 1}
    fitted = correctors.fit_correctors(["M8", "M9"], [low], high, config)
    assert fitted["M8"].coarse is fitted["M9"].coarse
    assert isinstance(fitted["M8"].network, correctors.TransolverCorr)
    assert isinstance(fitted["M9"].network, correctors.ConvNeXtUNet)
    query = np.array([[-0.7, 0.2], [0.4, -0.4]], dtype=np.float32)
    for model in fitted.values():
        pred = model.predict(query)
        assert pred.shape == (2, 5, 7)
        assert np.isfinite(pred).all()
        assert model.predict(query[:0]).shape == (0, 5, 7)
        assert all(parameter.device.type == "cpu" for parameter in model.network.parameters())
        assert all(parameter.device.type == "cpu" for member in model.coarse.members
                   for parameter in member.network.parameters())
        assert model.metadata["registration"] == "cell-centered bilinear"
        assert model.metadata["coarse"]["variants"] == ["plain", "hetero"]
    restored = cloudpickle.loads(cloudpickle.dumps(fitted))
    assert restored["M8"].coarse is restored["M9"].coarse
    for model_id in fitted:
        np.testing.assert_allclose(restored[model_id].predict(query), fitted[model_id].predict(query), rtol=1e-6)


def test_held_out_lf_labels_do_not_influence_fold_scaling_or_reference():
    low, high = _toy_tables()
    config = {"epochs": 1, "batch_size": 3, "seed": 19, "device": "cpu",
              "width": 8, "blocks": 1, "modes": 2, "coarse_folds": 2,
              "coarse_members": 2}
    before, references_before = correctors._fit_coarse_ensemble(low[0], low[1], high[0], config)
    fold = before.metadata["folds"][0]
    used_rows = set(fold["lf_training_rows"])
    poisoned_y = low[1].copy()
    excluded_rows = [i for i in range(len(low[0])) if i not in used_rows]
    assert excluded_rows
    poisoned_y[excluded_rows] = 1e6
    after, references_after = correctors._fit_coarse_ensemble(low[0], poisoned_y, high[0], config)
    held_rows = fold["hf_reference_rows"]
    np.testing.assert_array_equal(references_before[held_rows], references_after[held_rows])
    expected_scale = float(np.abs(low[1][fold["lf_training_rows"]]).max())
    assert all(member.scale == expected_scale for member in before.members + after.members)
    for earlier, later in zip(before.members, after.members):
        for name, value in earlier.network.state_dict().items():
            torch.testing.assert_close(value, later.network.state_dict()[name], rtol=0, atol=0)


def test_cpu_predictors_ignore_process_default_device_after_loading():
    low, high = _toy_tables()
    config = {"epochs": 1, "batch_size": 3, "seed": 13, "device": "cpu",
              "width": 8, "blocks": 1, "modes": 2, "coarse_members": 1,
              "coarse_folds": 2, "correction_steps": 1}
    fitted = correctors.fit_correctors(["M8", "M9"], [low], high, config)
    query = np.array([[0.4, -0.4]], dtype=np.float32)
    expected = {key: model.predict(query) for key, model in fitted.items()}
    serialized = cloudpickle.dumps(fitted)
    # DeepXDE may set this global default on import/unpickling. Meta reproduces
    # the device mismatch even on CI workers without a GPU.
    devices = ["meta"] + (["cuda"] if torch.cuda.is_available() else [])
    previous = torch.get_default_device()
    try:
        for device in devices:
            torch.set_default_device(device)
            restored = cloudpickle.loads(serialized)
            for key, model in restored.items():
                np.testing.assert_allclose(model.predict(query), expected[key], rtol=1e-6)
                assert all(parameter.device.type == "cpu" for parameter in model.network.parameters())
    finally:
        torch.set_default_device(previous)


def test_requested_unavailable_cuda_has_a_clear_error(monkeypatch):
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)
    assert str(correctors._device({"device": "auto"})) == "cpu"
    with pytest.raises(ValueError, match="cannot access CUDA"):
        correctors._device({"device": "cuda"})


def test_unpaired_low_inputs_are_supported():
    low, high = _toy_tables()
    # Distinct LF inputs remain usable, with no claim that rows are paired.
    low = (low[0] + 10.0, low[1])
    folds = correctors._coarse_folds(low[0], high[0], 2, seed=1)
    assert all(len(train) == len(low[0]) for train, _ in folds)


def test_insufficient_coarse_training_data_fails_before_training():
    with pytest.raises(ValueError, match="no LF training rows"):
        correctors._coarse_folds(np.array([[0.0], [0.0]]), np.array([[0.0], [1.0]]), 2, seed=1)
    with pytest.raises(ValueError, match="at least two distinct"):
        correctors._coarse_folds(np.array([[0.0], [1.0]]), np.array([[0.0], [0.0]]), 2, seed=1)


def test_invalid_configuration_does_not_silently_change_model_size():
    low, high = _toy_tables()
    with pytest.raises(ValueError, match="multiple of 8"):
        correctors.fit_correctors(["M8"], [low], high, {"width": 12})
    with pytest.raises(ValueError, match="at least one low fidelity"):
        correctors.fit_correctors(["M9"], [], high, {})
    with pytest.raises(ValueError, match="correction_steps must"):
        correctors.fit_correctors(["M9"], [low], high, {"correction_steps": 0})
