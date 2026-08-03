import numpy as np

from mffp_sharp.common import ic_encoding as ice
from mffp_sharp.pdes import kdv


def _spec(seed=0):
    s = {"delta": 0.022, "ic_amplitude": 0.5, "domain_size": 2.0, "ndim": 1, "seed": seed}
    rng = np.random.default_rng(seed)
    s.update(zip(ice.ic_names(1), rng.uniform(-1, 1, ice.n_coeffs(1))))
    return s


def test_shapes_finite():
    fields, cond, names = kdv.generate_sample(_spec(), [64, 128], 128, output_time=0.5)
    assert fields[64].shape == (64,) and fields[128].shape == (128,)
    for f in fields.values():
        assert np.isfinite(f).all()
    assert names == ["delta", "ic_amplitude"] + ice.ic_names(1) and cond.shape == (18,)


def test_soliton_propagates_at_speed_c():
    # Exact 1-soliton of u_t + 6 u u_x + delta^2 u_xxx = 0:
    #   u = (c/2) sech^2( sqrt(c)/(2 delta) (x - c t - x0) ).
    # Evolve the t=0 profile and compare to the analytic profile at t=T (no wrap).
    res, domain, delta, c, x0, T = 512, 60.0, 1.0, 1.0, 15.0, 4.0
    x = np.arange(res) * domain / res

    def soliton(t):
        xi = np.sqrt(c) / (2 * delta) * (x - c * t - x0)
        return (c / 2.0) / np.cosh(xi) ** 2

    u0 = soliton(0.0)
    got = kdv._solve(u0, delta, domain, output_time=T)
    ref = soliton(T)                       # moved c*T = 4 units, still inside [0, 60]
    assert np.max(np.abs(got - ref)) < 1e-2          # shape + speed both correct
    assert abs(got.max() - c / 2.0) < 2e-2           # amplitude preserved


def test_mass_conserved():
    res = 128
    rng = np.random.default_rng(1)
    ic = 0.5 * (2 * rng.random(res) - 1)             # matches generate_sample's IC build
    got = kdv._solve(ic, delta=0.022, domain_size=2.0, output_time=0.5)
    assert abs(float(got.mean()) - float(ic.mean())) < 1e-9


def test_stable_at_harshest_config_range():
    # The Plan-3 failure mode: must stay finite at the config's worst-case params.
    fields = kdv.generate_sample(
        {**_spec(seed=3), "delta": 0.04, "ic_amplitude": 0.7},
        [64, 128], 128, output_time=1.0)[0]
    for f in fields.values():
        assert np.isfinite(f).all() and np.abs(f).max() < 1e3


def test_only_1d_supported():
    assert kdv.NDIMS_SUPPORTED == (1,)
    import pytest
    with pytest.raises(AssertionError):
        kdv.sample_configs(2, {"delta_range": [0.02, 0.03],
                               "ic_amplitude_range": [0.4, 0.6], "domain_size": 2.0},
                           ndim=2, seed=0)


def test_deterministic():
    s = _spec(seed=7)
    a = kdv.generate_sample(s, [64, 128], 128, 0.5)[0][128]
    b = kdv.generate_sample(s, [64, 128], 128, 0.5)[0][128]
    assert np.array_equal(a, b)


def test_field_is_function_of_exported_cond_only():
    cfg = {"delta_range": [0.02, 0.03], "ic_amplitude_range": [0.4, 0.6], "domain_size": 2.0}
    spec = kdv.sample_configs(1, cfg, ndim=1, seed=7)[0]
    fields, cond, names = kdv.generate_sample(spec, [64, 128], 128, output_time=0.2)
    spec2 = dict(zip(names, cond.tolist()))
    spec2.update({"domain_size": 2.0, "ndim": 1})
    fields2, cond2, _ = kdv.generate_sample(spec2, [64, 128], 128, output_time=0.2)
    assert np.array_equal(fields[128], fields2[128])
    assert np.array_equal(cond, cond2)
