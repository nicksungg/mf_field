import h5py
import numpy as np

from mffp_sharp.common import io, ladder


def _make_samples(ndim, n=3):
    samples, conds = [], []
    for i in range(n):
        if ndim == 1:
            raw = {4: np.linspace(0, 1, 4) + i, 8: np.linspace(0, 1, 8) + i}
        else:
            x = np.linspace(0, 1, 4) + i
            xh = np.linspace(0, 1, 8) + i
            raw = {4: np.add.outer(x, x), 8: np.add.outer(xh, xh)}
        samples.append(ladder.assemble_sample(raw, 8, pde="sod" if ndim == 1 else "euler"))
        conds.append([float(i), 0.5])
    return samples, np.array(conds)


def test_roundtrip_1d(tmp_path):
    samples, cond = _make_samples(1)
    p = str(tmp_path / "d1.h5")
    io.write_dataset(p, "toy1d", samples, cond, ["a", "b"], [4, 8], 8, 1.0, seed=0)
    d = io.read_dataset(p)
    assert d["ndim"] == 1
    assert list(d["spatial_shape"]) == [8]
    assert d["bundles"][0]["aligned"][8].shape == (8,)
    assert d["bundles"][0]["raw"][4].shape == (4,)
    assert np.allclose(d["condition"], cond)


def test_roundtrip_2d(tmp_path):
    samples, cond = _make_samples(2)
    p = str(tmp_path / "d2.h5")
    io.write_dataset(p, "toy2d", samples, cond, ["a", "b"], [4, 8], 8, 1.0, seed=0)
    d = io.read_dataset(p)
    assert d["ndim"] == 2
    assert list(d["spatial_shape"]) == [8, 8]
    assert d["bundles"][0]["aligned"][8].shape == (8, 8)


def test_read_backward_compat_missing_attrs(tmp_path):
    """A file written before ndim/spatial_shape attrs existed still reads (defaults)."""
    samples, cond = _make_samples(2)
    p = str(tmp_path / "old.h5")
    io.write_dataset(p, "legacy", samples, cond, ["a", "b"], [4, 8], 8, 1.0, seed=0)
    # Simulate an old file: strip the attrs this task introduced.
    with h5py.File(p, "a") as f:
        del f.attrs["ndim"]
        del f.attrs["spatial_shape"]
    d = io.read_dataset(p)
    assert d["ndim"] == 2
    assert list(d["spatial_shape"]) == [8, 8]
