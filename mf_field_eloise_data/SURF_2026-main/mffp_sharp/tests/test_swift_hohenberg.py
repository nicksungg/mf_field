import numpy as np

from mffp_sharp.pdes import swift_hohenberg as sh


def _spec(ndim, seed=0):
    return {"r": 0.3, "ic_amplitude": 0.1, "domain_size": 32.0, "ndim": ndim, "seed": seed}


def test_2d_shapes_finite_bounded():
    fields, cond, names = sh.generate_sample(_spec(2), [16, 32], 32, output_time=1.0)
    assert fields[16].shape == (16, 16) and fields[32].shape == (32, 32)
    for f in fields.values():
        assert np.isfinite(f).all() and np.abs(f).max() < 100.0
    assert names == ["r", "ic_amplitude"] and cond.shape == (2,)


def test_1d_shapes_finite():
    fields = sh.generate_sample(_spec(1), [64, 128], 128, output_time=1.0)[0]
    assert fields[64].shape == (64,) and fields[128].shape == (128,)
    for f in fields.values():
        assert np.isfinite(f).all()


def test_deterministic():
    a = sh.generate_sample(_spec(1, seed=3), [64, 128], 128, 1.0)[0][128]
    b = sh.generate_sample(_spec(1, seed=3), [64, 128], 128, 1.0)[0][128]
    assert np.array_equal(a, b)


def test_ladder_outputs_spectrally_consistent():
    # Near-zero T: each level solves from the SAME continuous IC, so the coarse output
    # interpolated up matches the fine output (no clip here -> tight tolerance).
    from mffp_sharp.common.spectral import spectral_interp
    fields = sh.generate_sample(_spec(2, seed=4), [16, 32], 32, output_time=1e-6)[0]
    assert np.allclose(spectral_interp(fields[16], 32), fields[32], atol=1e-3)


def test_sample_configs():
    cfg = {"r_range": [0.1, 0.5], "ic_amplitude_range": [0.05, 0.2], "domain_size": 32.0}
    specs = sh.sample_configs(3, cfg, ndim=2, seed=1)
    assert len(specs) == 3 and all(s["ndim"] == 2 for s in specs)
    assert sh.NDIMS_SUPPORTED == (1, 2)
