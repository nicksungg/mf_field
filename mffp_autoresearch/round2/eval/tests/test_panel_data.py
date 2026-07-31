import numpy as np
import pytest
import sys, pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from panel_data import copylf_prediction, load_split


def _fake(lf_grid, hf_grid, n=3):
    rng = np.random.default_rng(0)
    lf = rng.normal(size=(n, lf_grid[0] * lf_grid[1]))
    hf = rng.normal(size=(n, hf_grid[0] * hf_grid[1]))
    return {
        "fids": [1, 2],
        "hf_fid": 2,
        "lf_fids": [1],
        "field_by_fid": {1: lf, 2: hf},
        "grid_shape_by_fid": {1: lf_grid, 2: hf_grid},
    }


def test_copylf_shape_and_identity_when_grids_match():
    d = _fake((8, 8), (8, 8))
    np.testing.assert_allclose(copylf_prediction(d), d["field_by_fid"][1])


def test_copylf_upsamples_to_hf_grid():
    d = _fake((8, 8), (16, 16))
    assert copylf_prediction(d).shape == (3, 256)


def test_copylf_constant_field_is_exact_under_interpolation():
    d = _fake((8, 8), (16, 16))
    d["field_by_fid"][1][:] = 7.0
    np.testing.assert_allclose(copylf_prediction(d), 7.0)


def test_copylf_uses_highest_lf_fidelity():
    d = _fake((8, 8), (16, 16))
    d["fids"] = [1, 2, 3]
    d["lf_fids"] = [1, 2]
    d["hf_fid"] = 3
    d["field_by_fid"][3] = d["field_by_fid"].pop(2)
    d["grid_shape_by_fid"] = {1: (4, 4), 2: (8, 8), 3: (16, 16)}
    d["field_by_fid"][2] = np.full((3, 64), 5.0)
    d["field_by_fid"][1] = np.zeros((3, 16))
    np.testing.assert_allclose(copylf_prediction(d), 5.0)  # l2, not l1


def test_copylf_1d_path_when_grid_unknown():
    # sod_1d shape: 1-D signals whose lengths are not all perfect squares, so
    # the loader reports grid None for at least one fidelity -> 1-D interpolation.
    rng = np.random.default_rng(1)
    d = {
        "fids": [1, 2], "hf_fid": 2, "lf_fids": [1],
        "field_by_fid": {1: rng.normal(size=(4, 32)), 2: rng.normal(size=(4, 128))},
        "grid_shape_by_fid": {1: None, 2: None},
    }
    pred = copylf_prediction(d)
    assert pred.shape == (4, 128)
    d["field_by_fid"][1][:] = 3.0
    np.testing.assert_allclose(copylf_prediction(d), 3.0)


def test_copylf_1d_path_when_only_one_grid_inferred():
    # sod_1d l2 has 64 cells -> loader wrongly infers (8, 8); HF l3 (128) is None.
    # The 1-D path must engage whenever EITHER grid is unknown.
    d = {
        "fids": [2, 3], "hf_fid": 3, "lf_fids": [2],
        "field_by_fid": {2: np.full((4, 64), 2.0), 3: np.zeros((4, 128))},
        "grid_shape_by_fid": {2: (8, 8), 3: None},
    }
    np.testing.assert_allclose(copylf_prediction(d), 2.0)


def test_copylf_raises_on_misalignment():
    d2 = _fake((8, 8), (16, 16))
    d2["field_by_fid"][1] = d2["field_by_fid"][1][:2]
    with pytest.raises(ValueError):
        copylf_prediction(d2)


def test_real_1d_guard_dataset():
    d = load_split("sharp__sod_1d", "test")
    pred = copylf_prediction(d)
    hf = d["field_by_fid"][d["hf_fid"]]
    assert pred.shape == hf.shape == (100, 128)


def test_real_dataset_loads_and_predicts():  # touches benchmark_42 via factory symlinks
    d = load_split("ext__helmholtz_2d", "test")
    pred = copylf_prediction(d)
    hf = d["field_by_fid"][d["hf_fid"]]
    assert pred.shape == hf.shape == (100, 9216)
