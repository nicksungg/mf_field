import numpy as np

from mffp_sharp.common import ic_encoding as ice
from mffp_sharp.pdes import nls


def _spec(seed=0):
    s = {"nonlinearity": -0.5, "ic_amplitude": 0.3, "domain_size": 40.0,
         "ndim": 1, "seed": seed}
    rng = np.random.default_rng(seed)
    s.update(zip(ice.ic_names(1), rng.uniform(-1, 1, ice.n_coeffs(1))))
    return s


def test_shapes_finite_real_intensity():
    fields, cond, names = nls.generate_sample(_spec(), [64, 128], 128, output_time=1.0)
    assert fields[64].shape == (64,) and fields[128].shape == (128,)
    for f in fields.values():
        assert np.isfinite(f).all()
        assert np.isrealobj(f) and f.min() >= 0.0      # stored field is |u|^2 >= 0
    assert names == ["nonlinearity", "ic_amplitude"] + ice.ic_names(1)
    assert cond.shape == (18,)


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
        {**_spec(seed=4), "nonlinearity": -1.0, "ic_amplitude": 0.5},
        [64, 128], 128, output_time=2.0)[0]
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


def test_field_is_function_of_exported_cond_only():
    cfg = {"nonlinearity_range": [-1.0, -0.2], "ic_amplitude_range": [0.2, 0.5],
           "domain_size": 40.0}
    spec = nls.sample_configs(1, cfg, ndim=1, seed=7)[0]
    fields, cond, names = nls.generate_sample(spec, [64, 128], 128, output_time=0.5)
    spec2 = dict(zip(names, cond.tolist()))
    spec2.update({"domain_size": 40.0, "ndim": 1})
    fields2, cond2, _ = nls.generate_sample(spec2, [64, 128], 128, output_time=0.5)
    assert np.array_equal(fields[128], fields2[128])
    assert np.array_equal(cond, cond2)
