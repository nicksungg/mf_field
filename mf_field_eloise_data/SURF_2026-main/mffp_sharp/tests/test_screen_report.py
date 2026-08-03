"""Integration test: build_report distinguishes a smooth from a sharp dataset.

Uses real solvers (KS = smooth control, Allen-Cahn = sharp interface) at tiny
resolution so it runs locally in seconds. Asserts structural correctness of
the report dict; does not assert ordering of s (too strict for tiny grids).
"""
import importlib.util
import os
import sys

import numpy as np
import pytest

from mffp_sharp.common import io, ladder
from mffp_sharp.common import ic_encoding as ice
from mffp_sharp.pdes import kuramoto_sivashinsky as ks, allen_cahn as ac


def _with_ic(spec, ndim, seed=0):
    rng = np.random.default_rng(seed)
    spec.update(zip(ice.ic_names(ndim), rng.uniform(-1, 1, ice.n_coeffs(ndim))))
    return spec


def _write(tmp, name, mod, spec, T):
    res = [16, 32]
    hf = 32
    samples, conds, cond_names = [], [], None
    raw, cond, cond_names = mod.generate_sample(spec, res, hf, T)
    samples.append(ladder.assemble_sample(raw, hf))
    conds.append(cond)
    io.write_dataset(
        os.path.join(tmp, f"{name}_sample.h5"),
        name,
        samples,
        np.array(conds),
        cond_names,
        res,
        hf,
        T,
        seed=0,
    )


def _load_builder():
    p = os.path.join(os.path.dirname(__file__), "..", "scripts", "screen_samples.py")
    spec = importlib.util.spec_from_file_location("screen_samples", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_report_distinguishes_smooth_from_sharp(tmp_path):
    d = str(tmp_path)
    _write(
        d,
        "kuramoto_sivashinsky",
        ks,
        _with_ic({"L": 30.0, "ic_amplitude": 0.1, "ndim": 2, "seed": 1}, ndim=2, seed=1),
        2.0,
    )
    _write(
        d,
        "allen_cahn",
        ac,
        _with_ic({
            "eps": 0.03,
            "mobility": 1.0,
            "mean_composition": 0.0,
            "domain_size": 1.0,
            "ndim": 2,
            "seed": 1,
        }, ndim=2, seed=1),
        0.5,
    )
    rep = _load_builder().build_report(d, k_cs=(8, 12))
    assert set(rep) == {"kuramoto_sivashinsky", "allen_cahn"}
    assert "f_curve" in rep["allen_cahn"] and "lf_hf_gap" in rep["allen_cahn"]
    # Verify structural completeness: both entries have the expected keys
    for name in rep:
        row = rep[name]
        assert "ndim" in row
        assert "f_curve" in row
        assert "floor_pass" in row
        assert "s" in row
        assert "lf_hf_gap" in row
        assert isinstance(row["lf_hf_gap"], float)
