import numpy as np

from mffp_sharp.pdes import nls


def _spec(seed=0):
    return {"nonlinearity": -0.5, "ic_amplitude": 0.3, "domain_size": 40.0,
            "ndim": 1, "seed": seed}


def test_shapes_finite_real_intensity():
    fields, cond, names = nls.generate_sample(_spec(), [64, 128], 128, output_time=1.0)
    assert fields[64].shape == (64,) and fields[128].shape == (128,)
    for f in fields.values():
        assert np.isfinite(f).all()
        assert np.isrealobj(f) and f.min() >= 0.0      # stored field is |u|^2 >= 0
    assert names == ["nonlinearity", "ic_amplitude"] and cond.shape == (2,)


def test_bright_soliton_intensity_stationary():
    # Focusing NLS (g=1) bright soliton u=sech(x) e^{it/2}: |u|^2 = sech^2(x) is STATIONARY.
    res, domain, T = 512, 40.0, 2.0
    x = np.arange(res) * domain / res - domain / 2.0
    u0 = 1.0 / np.cosh(x)                              # sech(x), real IC
    u = nls._solve(u0.astype(np.complex128), nonlinearity=1.0,
                   domain_size=domain, output_time=T)
    intensity = np.abs(u) ** 2
    assert np.max(np.abs(intensity - 1.0 / np.cosh(x) ** 2)) < 1e-2


def test_mass_conserved():
    # NLS conserves integral of |u|^2.
    res, domain, T = 256, 40.0, 2.0
    x = np.arange(res) * domain / res - domain / 2.0
    u0 = 1.0 / np.cosh(x)
    u = nls._solve(u0.astype(np.complex128), nonlinearity=-0.5, domain_size=domain,
                   output_time=T)
    assert abs(float((np.abs(u) ** 2).mean()) - float((u0 ** 2).mean())) < 1e-6


def test_stable_at_harshest_config_range():
    fields = nls.generate_sample(
        {"nonlinearity": -1.0, "ic_amplitude": 0.5, "domain_size": 40.0,
         "ndim": 1, "seed": 4}, [64, 128], 128, output_time=2.0)[0]
    for f in fields.values():
        assert np.isfinite(f).all() and f.max() < 1e3


def test_only_1d_supported():
    assert nls.NDIMS_SUPPORTED == (1,)
    import pytest
    with pytest.raises(AssertionError):
        nls.sample_configs(2, {"nonlinearity_range": [-1.0, -0.2],
                               "ic_amplitude_range": [0.2, 0.5], "domain_size": 40.0},
                           ndim=2, seed=0)


def test_deterministic():
    s = _spec(seed=7)
    a = nls.generate_sample(s, [64, 128], 128, 1.0)[0][128]
    b = nls.generate_sample(s, [64, 128], 128, 1.0)[0][128]
    assert np.array_equal(a, b)
