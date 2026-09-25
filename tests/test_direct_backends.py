"""CPU checks for the public adapters and scientific input contract."""
import importlib.util
import subprocess
import sys

import cloudpickle
import numpy as np
import pytest

from automf.backends.direct import fit_direct


@pytest.fixture
def tables():
    rng = np.random.default_rng(12)
    x = rng.uniform(-1, 1, (8, 2))
    xl = rng.uniform(-1, 1, (11, 2))
    pattern = np.linspace(-0.5, 0.5, 80).reshape(8, 10)
    high = (x, 1 + x[:, 0, None, None] + x[:, 1, None, None] * pattern)
    low = (xl, 0.9 + xl[:, 0, None, None] + xl[:, 1, None, None] * pattern[::2, ::2])
    return [low], high


@pytest.fixture
def cpu_threads():
    torch = pytest.importorskip("torch")
    original = torch.get_num_threads()
    torch.set_num_threads(1)
    yield torch
    torch.set_num_threads(original)


def config():
    return dict(epochs=1, batch_size=4, width=8, blocks=1, modes=2,
                coarse_members=2, device="cpu", gp_restarts=1, gp_maxiter=30)


def test_m7_has_no_torch_import():
    # Installing base dependencies must suffice, regardless of torch's presence.
    code = """
import sys
class BlockTorch:
    def find_spec(self, fullname, path=None, target=None):
        if fullname == 'torch' or fullname.startswith('torch.'):
            raise RuntimeError('Unexpected torch import')
sys.meta_path.insert(0, BlockTorch())
import numpy as np
from automf.backends.direct import fit_direct
x = np.arange(4.).reshape(-1, 1)
y = np.full((4, 2, 3), 7.)
m = fit_direct('M7', [], (x, y), {})
np.testing.assert_equal(m.predict(np.array([[5.]])), 7.)
"""
    subprocess.run([sys.executable, "-c", code], check=True, capture_output=True, text=True)


def test_pod_gp_generalizes_rank_one_field():
    x = np.linspace(-1, 1, 16)[:, None]
    pattern = np.array([[1., 2., 3.], [-1., 0., 1.]])
    y = 2 + np.sin(x[:, 0, None, None]) * pattern
    model = fit_direct("M7", [], (x, y), {"gp_restarts": 1})
    query = np.array([[-0.35], [0.65]])
    target = 2 + np.sin(query[:, 0, None, None]) * pattern
    error = np.linalg.norm(model.predict(query) - target)
    mean_error = np.linalg.norm(y.mean(0) - target)
    assert error < mean_error / 10
    assert model.metadata["pod_modes"] == 1
    assert model.metadata["low_fidelity_used"] is False


@pytest.mark.parametrize("model_id", ["M1", "M2", "M3", "M4", "M5", "M7"])
def test_unpaired_rectangular_fit_and_portable_roundtrip(model_id, tables, cpu_threads):
    low, high = tables
    model = fit_direct(model_id, low, high, config())
    query = np.array([[0.15, -0.2], [-0.5, 0.4]])
    predicted = model.predict(query)
    assert predicted.shape == (2, 8, 10)
    assert np.isfinite(predicted).all()
    restored = cloudpickle.loads(cloudpickle.dumps(model))
    np.testing.assert_allclose(restored.predict(query), predicted)
    assert model.predict(query[:0]).shape == (0, 8, 10)
    assert model.metadata["exact_archived_benchmark_replay"] is False
    assert model.metadata["fitting_labels_used"] is False
    assert model.metadata["evaluation_labels_used"] is False
    if model_id in {"M1", "M2", "M3", "M5"}:
        assert next(model.model.parameters()).device.type == "cpu"


def test_allpairs_never_misaligns_parameter_and_target_rows(monkeypatch, tables, cpu_threads):
    from automf.backends import direct
    low, high = tables
    middle_x = np.array([[8., 9.], [10., 11.], [12., 13.]])
    middle_y = np.broadcast_to(middle_x[:, 0, None, None], (3, 4, 5)).copy()
    calls = []

    def capture(model, X, Y, *args, **kwargs):
        calls.append((np.array(X), np.array(Y)))
        return {}

    monkeypatch.setattr(direct, "_train_network", capture)
    model = fit_direct("M2", low + [(middle_x, middle_y)], high, config())
    X, Y = calls[0]
    np.testing.assert_equal(X[:3, :2], middle_x)
    np.testing.assert_allclose(Y[:3], middle_x[:, 0, None, None] * np.ones((3, 8, 10)))
    for start in (3, 3 + len(high[0])):
        np.testing.assert_equal(X[start:start + len(high[0]), :2], high[0])
        np.testing.assert_allclose(Y[start:start + len(high[0])], high[1], rtol=1e-6)
    assert model.metadata["low_fidelity_used"] is True


def test_m6_retrieval_uses_only_supplied_training_table(tables, cpu_threads):
    from automf.backends.direct import RetrievalPredictor, _resize
    torch = cpu_threads

    class ZeroResidual(torch.nn.Module):
        def forward(self, inputs):
            branch, trunk = inputs
            return torch.zeros((len(branch), len(trunk)))

    low, high = tables
    reference_x, reference_y = low[0]
    branch_width = 2 + np.prod(reference_y.shape[1:])
    predictor = RetrievalPredictor(
        ZeroResidual(), reference_x, reference_y, np.zeros(branch_width),
        np.ones(branch_width), 0., 1., np.zeros((80, 2), np.float32),
        (8, 10), 2, 4, {})
    indices = [2, 7]
    np.testing.assert_allclose(predictor.predict(reference_x[indices]),
                               _resize(reference_y[indices], (8, 10)))


@pytest.mark.skipif(importlib.util.find_spec("deepxde") is None, reason="DeepXDE is optional")
def test_m6_actual_network(tables, cpu_threads):
    low, high = tables
    model = fit_direct("M6", low, high, config())
    output = model.predict(high[0][:2])
    assert output.shape == (2, 8, 10)
    assert np.isfinite(output).all()
    np.testing.assert_allclose(cloudpickle.loads(cloudpickle.dumps(model)).predict(high[0][:2]), output)


@pytest.mark.skipif(importlib.util.find_spec("deepxde") is None, reason="DeepXDE is optional")
def test_all_nine_fresh_process_load_preserves_default_device(tmp_path, tables, cpu_threads):
    from automf import FieldDataset, FieldPredictor
    low, high = tables
    dataset = FieldDataset(low_fidelity=low, high_fidelity=high)
    predictor = FieldPredictor(models="all", device="cpu").fit(
        dataset, presets="smoke", epochs=1, fitting_size=2,
        hyperparameters={"gp_restarts": 1, "gp_maxiter": 10})
    query = np.array([[0.15, -0.2], [-0.5, 0.4]])
    expected = predictor.predict_models(query)
    with (tmp_path / "all_models.pkl").open("wb") as stream:
        cloudpickle.dump(predictor, stream)
    np.savez(tmp_path / "expected.npz", query=query, **expected)
    # Raw cloudpickle deliberately bypasses FieldPredictor.load's additional
    # guard, ensuring M6 itself does not cause eager DeepXDE imports on restore.
    code = """
import sys
from pathlib import Path
import cloudpickle
import numpy as np
import torch
torch.set_num_threads(1)
assert 'deepxde' not in sys.modules
before = torch.get_default_device()
root = Path(sys.argv[1])
with (root / 'all_models.pkl').open('rb') as stream:
    model = cloudpickle.load(stream)
assert torch.get_default_device() == before
with np.load(root / 'expected.npz') as expected:
    actual = model.predict_models(expected['query'])
    for model_id, prediction in actual.items():
        np.testing.assert_allclose(prediction, expected[model_id], rtol=1e-6, atol=1e-7)
assert torch.get_default_device() == before
"""
    result = subprocess.run([sys.executable, "-c", code, str(tmp_path)],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("model_id", ["M1", "M2", "M3", "M4", "M5", "M6"])
def test_multifidelity_backends_reject_missing_low_data(model_id, tables):
    with pytest.raises(ValueError, match="low fidelity"):
        fit_direct(model_id, [], tables[1], config())
