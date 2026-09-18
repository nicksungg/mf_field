import numpy as np
import pytest

from mffp_sharp.pdes import cahn_hilliard as ch


def test_sample_configs_2d():
    cfg = {"eps_range": [0.01, 0.02], "mobility_range": [1.0, 1.0],
           "mean_composition_range": [-0.1, 0.1], "domain_size": 1.0}
    specs = ch.sample_configs(4, cfg, ndim=2, seed=0)
    assert len(specs) == 4
    for s in specs:
        assert s["ndim"] == 2
        assert {"eps", "mobility", "mean_composition", "domain_size"} <= set(s)


def test_sample_configs_rejects_bad_ndim():
    cfg = {"eps_range": [0.01, 0.02], "mobility_range": [1.0, 1.0],
           "mean_composition_range": [-0.1, 0.1], "domain_size": 1.0}
    with pytest.raises(AssertionError):
        ch.sample_configs(2, cfg, ndim=1, seed=0)


def test_mass_is_conserved():
    # Cahn-Hilliard is a CONSERVATIVE PDE: total mass (mean composition) is invariant.
    # The semi-implicit Fourier scheme leaves the k=0 mode untouched, so the mean is
    # preserved to ~machine precision. This is the exact-invariant correctness check
    # (the value assertion the end-to-end plumbing test lacked).
    res = 32
    rng = np.random.default_rng(0)
    c0 = 0.2 + 0.1 * (2 * rng.random((res, res)) - 1)
    out = ch._solve(c0, eps=0.02, mobility=1.0, domain_size=1.0, output_time=20 * ch._DT)
    assert np.isfinite(out).all()
    assert abs(out.mean() - c0.mean()) < 1e-9


def test_solution_stays_bounded():
    # The stiff 4th-order term is the one that blew up py-pde's explicit integrator;
    # the semi-implicit scheme must stay bounded (phase field near [-1, 1], no blow-up).
    res = 32
    rng = np.random.default_rng(1)
    c0 = 0.1 * (2 * rng.random((res, res)) - 1)
    out = ch._solve(c0, eps=0.02, mobility=1.0, domain_size=1.0, output_time=50 * ch._DT)
    assert np.isfinite(out).all()
    assert np.abs(out).max() < 2.0


def test_generate_sample_ladder_and_determinism():
    cfg = {"eps_range": [0.02, 0.02], "mobility_range": [1.0, 1.0],
           "mean_composition_range": [0.0, 0.0], "domain_size": 1.0}
    spec = ch.sample_configs(1, cfg, ndim=2, seed=3)[0]
    f1, cond, names = ch.generate_sample(spec, [16, 32], 32, output_time=20 * ch._DT)
    f2, _, _ = ch.generate_sample(spec, [16, 32], 32, output_time=20 * ch._DT)
    assert f1[16].shape == (16, 16) and f1[32].shape == (32, 32)
    assert names == ["eps", "mobility", "mean_composition"]
    for r in (16, 32):
        assert np.array_equal(f1[r], f2[r])     # same IC + deterministic solve
