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


class _StubNestedSpec:
    """A module whose spec cannot be rebuilt from a flat cond (like euler's
    quadrant structure): reconstruction must degrade to witness-only, not crash."""

    @staticmethod
    def generate_sample(spec, resolutions, hf_res, output_time):
        q = spec["quadrants"]                       # KeyError when rebuilt from cond
        f = np.full((hf_res, hf_res), float(q[0][0]))
        return {hf_res: f}, np.array([float(q[0][0])]), ["rho_tr"]


def test_certify_degrades_to_witness_when_spec_not_flat():
    x, y = [], []
    for i in range(4):
        fields, cond, names = _StubNestedSpec.generate_sample(
            {"quadrants": [(1.0 + i, 0, 0, 1.0)]}, [16], 16, 1.0)
        x.append(cond)
        y.append(fields[16].ravel())
    rec = comp.certify(_StubNestedSpec, np.stack(x), np.stack(y), ["rho_tr"], {},
                       [16], 16, 1.0)
    assert rec["reconstruction"]["verdict"] == "NOT_POSSIBLE"
    assert rec["verdict"] == "UNDECIDED"           # witness clean, but not proven


def test_certify_without_module_falls_back_to_witness():
    # No generator available: the witness alone must still catch the defect.
    rng = np.random.default_rng(0)
    x = rng.random((8, 3))
    x[1] = x[0] + 1e-9
    y = rng.random((8, 64))
    with pytest.raises(comp.CompletenessError):
        comp.certify(None, x, y, ["a", "b", "c"], {}, [16], 16, 1.0)


# ---------------------------------------------------------------------------
# 2026-08-03 hardening (briefing §8.1): seed-padding and dimension inflation
# ---------------------------------------------------------------------------

class _StubSeedPadded:
    """The illegitimate 'fix': the per-sample RNG seed is exported as a condition
    dimension. Reconstruction from cond succeeds at machine precision, but the
    map through the seed dimension is a hash, not a function a model can learn."""

    @staticmethod
    def generate_sample(spec, resolutions, hf_res, output_time):
        rng = np.random.default_rng(int(spec["s"]))
        f = float(spec["a"]) + rng.random((hf_res, hf_res))
        cond = np.array([spec["a"], float(int(spec["s"]))], dtype=np.float64)
        return {hf_res: f}, cond, ["a", "s"]


def _seed_padded_dataset(n=6, seed_stride=1):
    x, y = [], []
    for i in range(n):
        fields, cond, names = _StubSeedPadded.generate_sample(
            {"a": 0.5 + 0.1 * i, "s": i * seed_stride}, [16], 16, 1.0)
        x.append(cond)
        y.append(fields[16].ravel())
    return np.stack(x), np.stack(y), ["a", "s"]


def test_probe_kills_seed_padding_dead_dim():
    # Unit seed stride: eps = 1% of the seed column's spread stays inside one
    # integer, so the field does not respond at all -> DEAD dimension.
    x, y, names = _seed_padded_dataset(seed_stride=1)
    rec = comp.reconstruction_check(_StubSeedPadded, x[0], names, {}, [16], 16, 1.0, y[0])
    assert rec["verdict"] == "COMPLETE"          # reconstruction alone is fooled
    with pytest.raises(comp.CompletenessError) as ei:
        comp.certify(_StubSeedPadded, x, y, names, {}, [16], 16, 1.0, n_reconstruct=2)
    probe = ei.value.record["continuity_probe"]
    assert any(d["name"] == "s" and d["class"] in ("DEAD", "NONSMOOTH")
               for d in probe["per_dim"])


def test_probe_kills_seed_padding_hash_dim():
    # Large seed stride: eps crosses integer boundaries, the response is O(1)
    # at both step sizes and does not shrink -> NONSMOOTH (hash-like).
    x, y, names = _seed_padded_dataset(seed_stride=1000)
    with pytest.raises(comp.CompletenessError) as ei:
        comp.certify(_StubSeedPadded, x, y, names, {}, [16], 16, 1.0, n_reconstruct=2)
    probe = ei.value.record["continuity_probe"]
    flagged = {d["name"]: d["class"] for d in probe["per_dim"]}
    assert flagged["s"] in ("NONSMOOTH", "DEAD")
    assert flagged["a"] == "SMOOTH"              # the genuine coefficient is untouched


def test_witness_relative_threshold_survives_dimension_inflation():
    # A close pair hidden in 20 dimensions: absolute distance above the fixed
    # 0.5 bound, but far below 10% of the dataset's own median pair distance.
    rng = np.random.default_rng(7)
    x = rng.normal(size=(12, 20))
    x[1] = x[0] + 0.123
    # calibrate the offset so the pair's standardized distance lands between the
    # absolute bound and the relative trip point
    w0 = comp.nearest_pair_witness(x, rng.random((12, 4)))
    x[1] = x[0] + 0.123 * (0.55 / w0["standardized_condition_distance"])
    y = rng.random((12, 64))
    w = comp.nearest_pair_witness(x, y)
    assert w["standardized_condition_distance"] > comp.WITNESS_DIST_MAX
    assert (w["standardized_condition_distance"]
            < comp.WITNESS_DIST_MEDIAN_FRAC * w["median_pair_distance"])
    with pytest.raises(comp.CompletenessError):
        comp.certify(None, x, y, [f"c{i}" for i in range(20)], {}, [16], 16, 1.0)


class _StubDeterministic:
    @staticmethod
    def generate_sample(spec, resolutions, hf_res, output_time):
        f = np.full((hf_res, hf_res), float(spec["a"]))
        return {hf_res: f}, np.array([spec["a"]], dtype=np.float64), ["a"]


def test_witness_veto_overrides_reconstruction():
    # Sample 0 reconstructs perfectly, but the dataset contains a near-identical
    # condition pair with wildly different stored fields; the witness must veto.
    x = np.array([[0.5], [0.5 + 1e-9], [0.9], [0.1]])
    y = np.stack([np.full(64, 0.5), np.full(64, 5.0),
                  np.full(64, 0.9), np.full(64, 0.1)])
    with pytest.raises(comp.CompletenessError):
        comp.certify(_StubDeterministic, x, y, ["a"], {}, [16], 16, 1.0,
                     n_reconstruct=1)
