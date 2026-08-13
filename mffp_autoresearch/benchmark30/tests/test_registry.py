"""A5: convention registry extension (spec D4, ADR 0001).

Three guards:
(i)  coverage — every 2-D campaign dataset resolves in BOTH vendored
     registries; unknown names still raise (fail-closed, ADR r2-0001);
(ii) cross-copy equality for NEWLY classified IDs only — the pre-existing
     pfc divergence (family PERIODIC_NODE vs eval SPECTRAL_RUNG, ADR r3-0005)
     is deliberately exempt (spec D4);
(iii) synthetic upsample semantics per convention, on synthetic fields only.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest
import yaml

CAMPAIGN = Path(__file__).resolve().parents[1]


def _load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def eval_registry():
    return _load_module("b30_panel_data", CAMPAIGN / "eval/panel_data.py")


@pytest.fixture(scope="module")
def family_registry():
    return _load_module("b30_upsample", CAMPAIGN / "family/r3s2_route_b30/upsample.py")


@pytest.fixture(scope="module")
def campaign_ids():
    with open(CAMPAIGN / "config.yaml") as f:
        cfg = yaml.safe_load(f)
    return [d["id"] for g in cfg["datasets"].values() for d in g]


ONE_D = {"sharp__sod_1d", "sharp__burgers_1d", "sharp__shallow_water_1d",
         "sharp__porous_medium_1d", "allen_cahn_generated"}

# the sole intentional pre-existing cross-copy divergence (spec D4, ADR r3-0005)
PREEXISTING_EXEMPT = {"sharp__phase_field_crystal_2d"}


def _convention(mod, name):
    sets = {"periodic_node": mod.PERIODIC_NODE_DATASETS,
            "dirichlet_node": mod.DIRICHLET_NODE_DATASETS,
            "legacy_cell": mod.LEGACY_CELL_DATASETS}
    hits = [c for c, s in sets.items() if name in s]
    return hits[0] if len(hits) == 1 else hits


def test_every_2d_campaign_dataset_classified_in_both(eval_registry, family_registry, campaign_ids):
    for name in campaign_ids:
        if name in ONE_D:
            continue
        for mod, label in ((eval_registry, "eval"), (family_registry, "family")):
            if label == "eval" and name in PREEXISTING_EXEMPT:
                continue  # pfc rides the SPECTRAL_RUNG override in the eval copy (ADR r3-0005)
            conv = _convention(mod, name)
            assert isinstance(conv, str), \
                f"{name} not uniquely classified in {label} registry (got {conv})"


def test_unknown_dataset_still_raises(family_registry):
    with pytest.raises(ValueError, match="no reference convention"):
        family_registry.resolve_convention("no_such_dataset_xyz")


def test_new_ids_agree_across_copies(eval_registry, family_registry, campaign_ids):
    disagreements = []
    for name in campaign_ids:
        if name in ONE_D or name in PREEXISTING_EXEMPT:
            continue
        e, f = _convention(eval_registry, name), _convention(family_registry, name)
        if e != f:
            disagreements.append((name, e, f))
    assert not disagreements, f"cross-copy convention disagreements: {disagreements}"


def test_preexisting_pfc_divergence_preserved(eval_registry, family_registry):
    assert "sharp__phase_field_crystal_2d" in family_registry.PERIODIC_NODE_DATASETS
    assert "sharp__phase_field_crystal_2d" not in eval_registry.PERIODIC_NODE_DATASETS
    assert eval_registry.SPECTRAL_RUNG_DATASETS == {"sharp__phase_field_crystal_2d": 1}


# --- (iii) synthetic semantics, spec D4: synthetic fields only, never real data ---

def test_periodic_node_exact_at_shared_nodes(family_registry):
    rng = np.random.default_rng(0)
    lf = rng.random((8, 8))
    up = family_registry._node_aligned_periodic_up(lf, (32, 32))
    assert np.allclose(up[::4, ::4], lf), "variant C must be exact at shared nodes"


def test_periodic_node_rejects_non_nested(family_registry):
    with pytest.raises(ValueError, match="nested"):
        family_registry._node_aligned_periodic_up(np.zeros((24, 24)), (64, 64))


def test_dirichlet_node_interior_mapping(family_registry):
    """Variant E's certified contract: exact at SHARED interior nodes and linear
    within the LF node span; the outermost HF band clamps (mode="nearest") —
    that edge behaviour is part of the frozen implementation, not a defect."""
    n, N = 31, 63  # nested interior-node grids: X[2j+1] == x[j]
    x = (np.arange(n) + 1.0) / (n + 1)
    lf = np.outer(x, np.ones(n))
    up = family_registry._dirichlet_node_up(lf, (N, N))
    X = (np.arange(N) + 1.0) / (N + 1)
    assert np.allclose(up[1::2, 0], x, atol=1e-12), \
        "variant E must be exact at shared interior nodes"
    interior = slice(1, N - 1)  # HF nodes inside [x_0, x_{n-1}]
    assert np.allclose(up[interior, 0], X[interior], atol=1e-12), \
        "variant E must reproduce a linear field within the LF node span"


def test_legacy_cell_shape_and_constant_preservation(family_registry):
    up = family_registry._legacy_cell_centred_up(np.full((8, 8), 3.25), (32, 32))
    assert up.shape == (32, 32)
    assert np.allclose(up, 3.25)


def test_campaign_classification_counts(eval_registry, campaign_ids):
    """Pin the ADR's totals: 12 legacy + 3 dirichlet + 1 periodic NEW 2-D IDs."""
    orig_periodic = {"sharp__allen_cahn_2d", "sharp__fisher_kpp_2d", "sharp__cahn_hilliard"}
    orig_dirichlet = {"ext__helmholtz_2d"}
    orig_legacy = {"heat_local", "fluid", "sharp__sod_1d", "ifc_poisson", "ifc_heat"}
    new_p = eval_registry.PERIODIC_NODE_DATASETS - orig_periodic
    new_d = eval_registry.DIRICHLET_NODE_DATASETS - orig_dirichlet
    new_l = eval_registry.LEGACY_CELL_DATASETS - orig_legacy
    assert new_p == {"sharp__porous_medium_2d"}
    assert new_d == {"poisson_generated", "darcy_generated", "sharp__helmholtz_2d"}
    assert len(new_l) == 12 and "era5" in new_l and "ext__cahn_hilliard_2d" in new_l
    assert set(campaign_ids) - ONE_D <= (
        eval_registry.PERIODIC_NODE_DATASETS | eval_registry.DIRICHLET_NODE_DATASETS
        | eval_registry.LEGACY_CELL_DATASETS | {"sharp__phase_field_crystal_2d"})
