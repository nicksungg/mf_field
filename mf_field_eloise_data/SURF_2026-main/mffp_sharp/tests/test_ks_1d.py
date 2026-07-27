import os

import numpy as np

from mffp_sharp.pdes import kuramoto_sivashinsky as ks

_GOLDEN = os.path.join(os.path.dirname(__file__), "fixtures", "ks_2d_golden.npy")


def test_2d_output_matches_golden():
    # The N-D generalization must not change the validated 2D solve.
    golden = np.load(_GOLDEN)
    spec = {"L": 30.0, "ic_amplitude": 0.1, "ndim": 2, "seed": 1}
    fields = ks.generate_sample(spec, [16, 32], 32, output_time=2.0)[0]
    got = np.stack([fields[16].ravel()[:64], fields[32].ravel()[:64]])
    assert np.allclose(got, golden, atol=1e-12, rtol=0)


def test_1d_shapes_and_zero_mean():
    spec = {"L": 30.0, "ic_amplitude": 0.1, "ndim": 1, "seed": 2}
    fields, cond, names = ks.generate_sample(spec, [64, 128], 128, output_time=2.0)
    assert fields[64].shape == (64,) and fields[128].shape == (128,)
    for f in fields.values():
        assert np.isfinite(f).all()
        assert abs(float(f.mean())) < 1e-8          # stores zero-mean fluctuation
    assert names == ["L", "ic_amplitude"] and cond.shape == (2,)


def test_1d_deterministic():
    spec = {"L": 28.0, "ic_amplitude": 0.1, "ndim": 1, "seed": 5}
    a = ks.generate_sample(spec, [64, 128], 128, 2.0)[0][128]
    b = ks.generate_sample(spec, [64, 128], 128, 2.0)[0][128]
    assert np.array_equal(a, b)


def test_1d_supported():
    assert ks.NDIMS_SUPPORTED == (1, 2)
    cfg = {"L_range": [22.0, 36.0], "ic_amplitude_range": [0.05, 0.2]}
    specs = ks.sample_configs(3, cfg, ndim=1, seed=0)
    assert all(s["ndim"] == 1 for s in specs)
