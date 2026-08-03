import numpy as np
import pytest

from mffp_sharp.common import completeness as comp
from mffp_sharp.pdes import fisher_kpp as fk

_CFG = {"D_range": [1e-4, 1e-3], "r_range": [5.0, 20.0], "domain_size": 1.0}
_CONST = {"domain_size": 1.0, "ndim": 2}
_T = 5 * fk._DT


def _fk_dataset(n=6):
    specs = fk.sample_configs(n, _CFG, ndim=2, seed=0)
    x, y, names = [], [], None
    for s in specs:
        fields, cond, names = fk.generate_sample(s, [8, 16], 16, _T)
        x.append(cond)
        y.append(fields[16].ravel())
    return np.stack(x), np.stack(y), names


def test_witness_flags_synthetic_incomplete():
    # Two samples with near-identical conditions but O(1)-different fields: the
    # witness must surface that pair with a small distance and a large rel diff.
    rng = np.random.default_rng(0)
    x = rng.random((8, 3))
    x[1] = x[0] + 1e-9
    y = rng.random((8, 64))
    w = comp.nearest_pair_witness(x, y)
    assert sorted(w["closest_pair"]) == [0, 1]
    assert w["standardized_condition_distance"] < 1e-6
    assert w["relative_field_difference"] > 0.1


class _StubOldBehavior:
    """A module reproducing the pre-fix defect: the field depends on an
    unexported per-sample seed, so reconstruction from cond alone fails."""

    @staticmethod
    def generate_sample(spec, resolutions, hf_res, output_time):
        rng = np.random.default_rng(int(spec.get("seed", 0)))
        f = rng.random((hf_res, hf_res))
        return {hf_res: f}, np.array([spec["a"]], dtype=np.float64), ["a"]


def _stub_dataset(n=4):
    x, y = [], []
    for i in range(n):
        fields, cond, names = _StubOldBehavior.generate_sample(
            {"a": 0.5 + 0.01 * i, "seed": i}, [16], 16, 1.0)
        x.append(cond)
        y.append(fields[16].ravel())
    return np.stack(x), np.stack(y), ["a"]


def test_reconstruction_check_complete_for_fixed_module():
    x, y, names = _fk_dataset(2)
    rec = comp.reconstruction_check(fk, x[0], names, _CONST, [8, 16], 16, _T, y[0])
    assert rec["verdict"] == "COMPLETE"
    assert rec["rel_L2"] < 1e-12


def test_certify_complete_for_fixed_module():
    x, y, names = _fk_dataset(6)
    rec = comp.certify(fk, x, y, names, _CONST, [8, 16], 16, _T, n_reconstruct=2)
    assert rec["verdict"] == "COMPLETE"
    assert rec["reconstruction"]["rel_L2_max"] < 1e-12
    assert "witness" in rec


def test_certify_raises_on_incomplete():
    x, y, names = _stub_dataset()
    with pytest.raises(comp.CompletenessError):
        comp.certify(_StubOldBehavior, x, y, names, {}, [16], 16, 1.0, n_reconstruct=2)


def test_certify_declared_stochastic_records_without_raising():
    x, y, names = _stub_dataset()
    rec = comp.certify(_StubOldBehavior, x, y, names, {}, [16], 16, 1.0,
                       n_reconstruct=2, declared_stochastic=True)
    assert rec["verdict"] == "STOCHASTIC_DECLARED"
    assert rec["reconstruction"]["verdict"] == "NOT_REPRODUCED"


def test_certify_without_module_falls_back_to_witness():
    # No generator available: the witness alone must still catch the defect.
    rng = np.random.default_rng(0)
    x = rng.random((8, 3))
    x[1] = x[0] + 1e-9
    y = rng.random((8, 64))
    with pytest.raises(comp.CompletenessError):
        comp.certify(None, x, y, ["a", "b", "c"], {}, [16], 16, 1.0)
