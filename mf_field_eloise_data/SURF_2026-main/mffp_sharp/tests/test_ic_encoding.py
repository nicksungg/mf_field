import numpy as np
import pytest

from mffp_sharp.common import ic_encoding as ice


def _coeffs(ndim, seed=0):
    rng = np.random.default_rng(seed)
    return rng.uniform(-1, 1, ice.n_coeffs(ndim))


def test_n_coeffs_is_16_for_both_ndims():
    # 1D: modes 1..K1D, cos+sin -> 2*K1D; 2D: (kx,ky) in 0..M2D-1 minus DC, cos+sin.
    assert ice.n_coeffs(1) == 2 * ice.K1D == 16
    assert ice.n_coeffs(2) == 2 * (ice.M2D * ice.M2D - 1) == 16


def test_ic_names_and_ranges_ordering():
    for ndim in (1, 2):
        names = ice.ic_names(ndim)
        assert names == [f"ic_c{j}" for j in range(16)]
        ranges = ice.ic_ranges(ndim)
        assert list(ranges) == names
        assert all(ranges[n] == (-1.0, 1.0) for n in names)


def test_coeffs_from_spec_roundtrip():
    c = _coeffs(2, seed=3)
    spec = {name: c[j] for j, name in enumerate(ice.ic_names(2))}
    spec["unrelated"] = 99.0
    assert np.array_equal(ice.coeffs_from_spec(spec, 2), c)


def test_determinism():
    for ndim, fn in ((1, ice.ic_1d), (2, ice.ic_2d)):
        c = _coeffs(ndim)
        assert np.array_equal(fn(c, 64, 0.1), fn(c, 64, 0.1))


def test_normalization_max_abs_equals_scale():
    for ndim, fn in ((1, ice.ic_1d), (2, ice.ic_2d)):
        for scale in (0.1, 0.5, 0.9):
            u = fn(_coeffs(ndim, seed=1), 64, scale)
            assert np.isclose(np.max(np.abs(u)), scale, rtol=1e-9)


def test_ic_1d_band_limited_and_zero_mean():
    u = ice.ic_1d(_coeffs(1, seed=2), 128, 0.5)
    uh = np.fft.fft(u)
    live = np.zeros(128, bool)
    for k in range(1, ice.K1D + 1):
        live[k] = live[128 - k] = True
    assert np.all(np.abs(uh[~live]) < 1e-10 * np.max(np.abs(uh)))
    assert abs(u.mean()) < 1e-12  # no DC mode -> zero mean


def test_ic_2d_band_limited():
    f = ice.ic_2d(_coeffs(2, seed=4), 64, 0.1)
    fh = np.fft.fft2(f)
    fi = (np.fft.fftfreq(64) * 64).astype(int)
    KX, KY = np.meshgrid(fi, fi, indexing="ij")
    live = (np.abs(KX) < ice.M2D) & (np.abs(KY) < ice.M2D)
    assert np.all(np.abs(fh[~live]) < 1e-10 * np.max(np.abs(fh)))


def test_build_ic_dispatches_on_ndim():
    c1, c2 = _coeffs(1, seed=5), _coeffs(2, seed=5)
    assert np.array_equal(ice.build_ic(c1, 64, 0.2, 1), ice.ic_1d(c1, 64, 0.2))
    assert np.array_equal(ice.build_ic(c2, 64, 0.2, 2), ice.ic_2d(c2, 64, 0.2))
    assert ice.build_ic(c1, 64, 0.2, 1).shape == (64,)
    assert ice.build_ic(c2, 64, 0.2, 2).shape == (64, 64)


def test_matches_generate_learnable_reference():
    # The construction must stay byte-identical to the validated generate_learnable.py
    # math (which the existing cahn_hilliard benchmark's reconstruction certificate pins).
    c = _coeffs(2, seed=6)
    xs = 2 * np.pi * np.arange(32) / 32
    X, Y = np.meshgrid(xs, xs, indexing="ij")
    modes = [(a, b) for a in range(3) for b in range(3) if not (a == 0 and b == 0)]
    f = np.zeros((32, 32))
    idx = 0
    for (kx, ky) in modes:
        f += c[idx] * np.cos(kx * X + ky * Y) + c[idx + 1] * np.sin(kx * X + ky * Y)
        idx += 2
    ref = f / (np.max(np.abs(f)) + 1e-12) * 0.1
    assert np.array_equal(ice.ic_2d(c, 32, 0.1), ref)
