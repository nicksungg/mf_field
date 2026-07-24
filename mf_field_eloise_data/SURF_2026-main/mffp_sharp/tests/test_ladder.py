import numpy as np

from mffp_sharp.common import ladder


def test_1d_constant_preserved():
    f = np.full(4, 2.0)
    out = ladder.upsample_to_hf(f, 8)
    assert out.shape == (8,)
    assert np.allclose(out, 2.0)


def test_1d_linear_matches_np_interp():
    f = np.linspace(0.0, 3.0, 4)
    out = ladder.upsample_to_hf(f, 8)
    src = (np.arange(4) + 0.5) / 4
    dst = (np.arange(8) + 0.5) / 8
    assert np.allclose(out, np.interp(dst, src, f))


def test_1d_identity_when_same_res():
    f = np.linspace(0.0, 3.0, 4)
    out = ladder.upsample_to_hf(f, 4)
    assert out.shape == (4,)
    assert np.allclose(out, f)


def test_1d_nearest_order():
    f = np.array([0.0, 1.0, 2.0, 3.0])
    out = ladder.upsample_to_hf(f, 8, order="nearest")
    assert out.shape == (8,)
    assert set(np.unique(out)).issubset(set(f.tolist()))


def test_2d_unchanged_constant():
    f = np.full((4, 4), 2.0)
    out = ladder.upsample_to_hf(f, 8)
    assert out.shape == (8, 8)
    assert np.allclose(out, 2.0)


def test_assemble_sample_1d():
    b = ladder.assemble_sample({4: np.linspace(0, 3, 4), 8: np.linspace(0, 3, 8)}, 8)
    assert b["aligned"][4].shape == (8,)
    assert b["aligned"][8].shape == (8,)
    assert b["raw"][4].shape == (4,)


def test_unsupported_ndim_raises():
    import pytest
    with pytest.raises(ValueError):
        ladder.upsample_to_hf(np.zeros((2, 2, 2)), 4)
