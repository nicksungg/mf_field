import numpy as np

from mffp_sharp.pdes import fisher_kpp as fk


def _spec(ndim, seed=0):
    return {"D": 1e-4, "r": 10.0, "domain_size": 1.0, "ndim": ndim, "seed": seed}


def test_2d_shapes_finite_and_bounded():
    fields, cond, names = fk.generate_sample(_spec(2), [16, 32], 32, output_time=0.02)
    assert fields[16].shape == (16, 16) and fields[32].shape == (32, 32)
    for f in fields.values():
        assert np.isfinite(f).all()
        assert f.min() >= -1e-6 and f.max() <= 1.0 + 1e-6     # logistic stays in [0,1]
    assert names == ["D", "r"] and cond.shape == (2,)


def test_1d_shapes_finite():
    fields = fk.generate_sample(_spec(1), [32, 64], 64, output_time=0.02)[0]
    assert fields[32].shape == (32,) and fields[64].shape == (64,)
    for f in fields.values():
        assert np.isfinite(f).all()


def test_deterministic():
    a = fk.generate_sample(_spec(1, seed=2), [32, 64], 64, 0.02)[0][64]
    b = fk.generate_sample(_spec(1, seed=2), [32, 64], 64, 0.02)[0][64]
    assert np.array_equal(a, b)


def test_sample_configs():
    cfg = {"D_range": [1e-4, 1e-3], "r_range": [5.0, 20.0], "domain_size": 1.0}
    specs = fk.sample_configs(3, cfg, ndim=2, seed=1)
    assert len(specs) == 3 and all(s["ndim"] == 2 for s in specs)
    assert fk.NDIMS_SUPPORTED == (1, 2)


def test_ladder_outputs_spectrally_consistent():
    # Near-zero T: each level solves from the SAME continuous IC (coarse IC spectrally
    # interpolated up). The [0,1] clip in _solve corrupts only the high-k overshoots that
    # band-limited interpolation of a white-noise IC produces (ringing to >1 / <0) and that
    # the coarse grid cannot represent anyway -- so the coarse-resolvable BULK matches very
    # tightly even though a few overshoot points get clipped. (A full-amplitude white-noise
    # IC vs a smoother seed is a TBD-box physics-design choice; see ledger.)
    from mffp_sharp.common.spectral import spectral_interp
    fields = fk.generate_sample(_spec(2, seed=4), [16, 32], 32, output_time=1e-6)[0]
    diff = np.abs(spectral_interp(fields[16], 32) - fields[32])
    assert np.median(diff) < 1e-3            # bulk is essentially exact (~1e-7)
    assert (diff < 1e-2).mean() > 0.9        # >90% of points agree; clip touches only a few
