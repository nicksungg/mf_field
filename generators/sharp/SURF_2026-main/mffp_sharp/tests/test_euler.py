import numpy as np
import pytest

from mffp_sharp.pdes import euler


def test_module_imports_without_clawpack():
    # Lazy clawpack import: the module + sample_configs work with no clawpack installed.
    assert euler.NDIMS_SUPPORTED == (2,)


def test_sample_configs_2d():
    cfg = {"jitter_frac": 0.05, "gamma": 1.4}
    specs = euler.sample_configs(4, cfg, ndim=2, seed=0)
    assert len(specs) == 4
    for s in specs:
        assert s["ndim"] == 2 and s["gamma"] == 1.4
        # four quadrant states, each (rho, u, v, p)
        assert len(s["quadrants"]) == 4 and all(len(q) == 4 for q in s["quadrants"])


def test_sample_configs_rejects_bad_ndim():
    with pytest.raises(AssertionError):
        euler.sample_configs(2, {"jitter_frac": 0.05}, ndim=1, seed=0)


def test_condition_vector_is_complete_and_small():
    # condition vector must be <=10 scalars and named (completeness convention)
    spec = euler.sample_configs(1, {"jitter_frac": 0.05, "gamma": 1.4}, ndim=2, seed=0)[0]
    cond, names = euler._condition_vector(spec["quadrants"], spec["gamma"])
    assert cond.shape == (7,) and len(names) == 7 and cond.shape[0] <= 10
    assert names == ["pTL/pTR", "pBL/pTR", "pBR/pTR",
                     "rTL/rTR", "rBL/rTR", "rBR/rTR", "gamma"]


# ---- box-only: the PyClaw solve (skips where clawpack is absent) ----

def test_solve_shapes_finite_positive_box():
    pytest.importorskip("clawpack")            # box-only (PyClaw)
    res = 32
    spec = euler.sample_configs(1, {"jitter_frac": 0.05, "gamma": 1.4}, ndim=2, seed=0)[0]
    # ladder [32, 64], HF=64: 32 uses Classic (LF), 64 uses SharpClaw (HF)
    fields, cond, names = euler.generate_sample(spec, [res, 2 * res], 2 * res,
                                                output_time=0.1)
    assert fields[res].shape == (res, res)
    assert fields[2 * res].shape == (2 * res, 2 * res)
    for f in fields.values():
        assert np.isfinite(f).all()           # no NaN/Inf
        # stored field is density rho -> must be physically positive.
        # NOTE: if WENO (HF) trips this near a strong shock, the solver needs a
        # positivity-preserving limiter -- that is a real finding, not a bad test.
        assert (f > 0.0).all()
    assert cond.shape == (7,)


def test_solve_lf_smears_relative_to_hf_box():
    pytest.importorskip("clawpack")            # box-only (PyClaw)
    res = 32
    spec = euler.sample_configs(1, {"jitter_frac": 0.05, "gamma": 1.4}, ndim=2, seed=0)[0]
    # same continuous IC, two schemes/grids; HF (SharpClaw) must be sharper than
    # LF (Classic Godunov). Compare max gradient magnitude as a sharpness proxy.
    fields, _, _ = euler.generate_sample(spec, [res, 2 * res], 2 * res, output_time=0.1)
    lf_grad = max(np.abs(np.gradient(fields[res])).max(), 1e-30)
    hf_grad = np.abs(np.gradient(fields[2 * res])).max()
    assert hf_grad > lf_grad                    # HF resolves a steeper shock than LF


def test_solve_is_deterministic_box():
    pytest.importorskip("clawpack")            # box-only (PyClaw)
    res = 32
    spec = euler.sample_configs(1, {"jitter_frac": 0.05, "gamma": 1.4}, ndim=2, seed=1)[0]
    f1, _, _ = euler.generate_sample(spec, [res], res, output_time=0.1)
    f2, _, _ = euler.generate_sample(spec, [res], res, output_time=0.1)
    assert np.allclose(f1[res], f2[res], rtol=0, atol=1e-12)
