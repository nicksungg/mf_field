import numpy as np

from mffp_sharp.pdes import sine_gordon as sg


def _spec(ndim, seed=0):
    return {"m": 1.0, "ic_amplitude": 0.1, "domain_size": 40.0, "ndim": ndim, "seed": seed}


def test_2d_shapes_finite():
    fields, cond, names = sg.generate_sample(_spec(2), [16, 32], 32, output_time=1.0)
    assert fields[16].shape == (16, 16) and fields[32].shape == (32, 32)
    for f in fields.values():
        assert np.isfinite(f).all()
    assert names == ["m", "ic_amplitude"] and cond.shape == (2,)


def test_1d_shapes_finite():
    fields = sg.generate_sample(_spec(1), [64, 128], 128, output_time=1.0)[0]
    assert fields[64].shape == (64,) and fields[128].shape == (128,)
    for f in fields.values():
        assert np.isfinite(f).all()


def test_small_amplitude_klein_gordon_dispersion():
    # Small amplitude -> nonlinearity negligible -> exact standing wave at omega=sqrt(k0^2+m^2):
    #   u(x,t) = A cos(k0 x) cos(omega t),  starting from rest.
    res, domain, m, A = 256, 40.0, 0.5, 1e-3
    x = np.arange(res) * domain / res
    n0 = 4                                   # integer mode index on the periodic domain
    k0 = 2 * np.pi * n0 / domain
    omega = np.sqrt(k0 ** 2 + m ** 2)
    T = 1.0
    u0 = A * np.cos(k0 * x)
    got = sg._solve(u0, m, domain, output_time=T)
    ref = A * np.cos(k0 * x) * np.cos(omega * T)
    assert np.max(np.abs(got - ref)) < 1e-2 * A     # relative to amplitude


def test_energy_conserved():
    # sine-Gordon conserves E = integral[ 1/2 u_t^2 + 1/2 |grad u|^2 + m^2 (1 - cos u) ].
    # We start from rest; check E(T) ~ E(0) via the solver's energy helper.
    res, domain, m = 256, 40.0, 1.0
    rng = np.random.default_rng(0)
    u0 = 0.3 * (2 * rng.random(res) - 1)
    e0 = sg._energy(u0, np.zeros_like(u0), m, domain)
    uT, vT = sg._solve_with_velocity(u0, m, domain, output_time=2.0)
    eT = sg._energy(uT, vT, m, domain)
    assert abs(eT - e0) < 1e-2 * abs(e0)


def test_stable_at_harshest_config_range():
    fields = sg.generate_sample(
        {"m": 2.0, "ic_amplitude": 1.0, "domain_size": 40.0, "ndim": 1, "seed": 3},
        [64, 128], 128, output_time=2.0)[0]
    for f in fields.values():
        assert np.isfinite(f).all() and np.abs(f).max() < 1e3


def test_only_supported_ndims():
    assert sg.NDIMS_SUPPORTED == (1, 2)
    import pytest
    with pytest.raises(AssertionError):
        sg.sample_configs(2, {"m_range": [0.5, 2.0], "ic_amplitude_range": [0.1, 1.0],
                              "domain_size": 40.0}, ndim=3, seed=0)
