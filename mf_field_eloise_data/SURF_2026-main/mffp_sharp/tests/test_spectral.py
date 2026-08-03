import numpy as np

from mffp_sharp.common import spectral


def test_interp_1d_constant_preserved():
    f = np.full(8, 2.5)
    out = spectral.spectral_interp(f, 16)
    assert out.shape == (16,)
    assert np.allclose(out, 2.5)


def test_interp_1d_single_mode_resampled():
    n, nf = 16, 32
    x = (np.arange(n)) / n
    f = np.sin(2 * np.pi * x)               # mode k=1, exactly representable
    out = spectral.spectral_interp(f, nf)
    xf = (np.arange(nf)) / nf
    assert np.allclose(out, np.sin(2 * np.pi * xf), atol=1e-10)


def test_interp_1d_identity_when_same():
    f = np.linspace(0, 1, 8)
    out = spectral.spectral_interp(f, 8)
    assert out.shape == (8,) and np.allclose(out, f)


def test_interp_2d_constant_preserved():
    f = np.full((8, 8), 1.25)
    out = spectral.spectral_interp(f, 16)
    assert out.shape == (16, 16)
    assert np.allclose(out, 1.25)


def test_interp_unsupported_ndim_raises():
    import pytest
    with pytest.raises(ValueError):
        spectral.spectral_interp(np.zeros((2, 2, 2)), 4)


def test_neg_laplacian_symbol_1d_nonnegative_bounded():
    s = spectral.neg_laplacian_symbol(32, 1.0 / 32, ndim=1)
    assert s.shape == (32,)
    assert s.min() >= 0.0 and np.isfinite(s).all()
    assert np.isclose(s[0], 0.0)            # k=0 mode has zero Laplacian


def test_neg_laplacian_symbol_2d_shape():
    s = spectral.neg_laplacian_symbol(16, 1.0 / 16, ndim=2)
    assert s.shape == (16, 16)
    assert s.min() >= 0.0 and np.isclose(s[0, 0], 0.0)


def _with_ic(spec, ndim, seed=0):
    from mffp_sharp.common import ic_encoding as ice
    rng = np.random.default_rng(seed)
    spec.update(zip(ice.ic_names(ndim), rng.uniform(-1, 1, ice.n_coeffs(ndim))))
    return spec


def test_ch_solve_still_runs_and_bounded():
    from mffp_sharp.pdes import cahn_hilliard as ch
    spec = _with_ic({"eps": 0.03, "mobility": 1.0, "mean_composition": 0.0,
                     "domain_size": 1.0, "seed": 0}, ndim=2)
    fields, cond, names = ch.generate_sample(spec, [16, 32], 32, output_time=0.05)
    assert set(fields) == {16, 32}
    for f in fields.values():
        assert np.isfinite(f).all()
        assert np.abs(f).max() < 5.0           # bounded; phase field stays O(1)
    assert names[:3] == ["eps", "mobility", "mean_composition"]


def test_ch_solve_deterministic():
    from mffp_sharp.pdes import cahn_hilliard as ch
    spec = _with_ic({"eps": 0.03, "mobility": 1.0, "mean_composition": 0.0,
                     "domain_size": 1.0, "seed": 7}, ndim=2, seed=7)
    a = ch.generate_sample(spec, [16, 32], 32, 0.05)[0][32]
    b = ch.generate_sample(spec, [16, 32], 32, 0.05)[0][32]
    assert np.array_equal(a, b)


def test_ks_solve_still_runs_zero_mean():
    from mffp_sharp.pdes import kuramoto_sivashinsky as ks
    spec = _with_ic({"L": 30.0, "ic_amplitude": 0.1, "seed": 1}, ndim=2, seed=1)
    fields, cond, names = ks.generate_sample(spec, [16, 32], 32, output_time=1.0)
    for f in fields.values():
        assert np.isfinite(f).all()
        assert abs(float(f.mean())) < 1e-8     # KS stores zero-mean fluctuation
