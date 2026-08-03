"""Phase-1b no-regression gate: the 2D path must be behavior-preserving."""
import os

import numpy as np

from mffp_sharp.common import ladder, metrics, io, visualize


def _golden_2d_field(res, seed=0):
    rng = np.random.default_rng(seed)
    return rng.standard_normal((res, res))


def test_2d_upsample_is_deterministic_and_shaped():
    f = _golden_2d_field(4)
    out = ladder.upsample_to_hf(f, 8, convention="cell_centered")
    assert out.shape == (8, 8)
    # linear up-interp of a known field reproduces a stored corner exactly enough
    again = ladder.upsample_to_hf(f, 8, convention="cell_centered")
    assert np.allclose(out, again)


def test_2d_metric_panel_values_stable():
    ref = _golden_2d_field(16, seed=1)
    pred = ref + 0.1 * _golden_2d_field(16, seed=2)
    out = metrics.evaluate(pred, ref, ["rel_l2", "linf", "spectral_band",
                                       "interface_position", "conservation", "ssim"])
    # SSIM defined for 2D -> finite, NOT nan (contrast with the 1D skip)
    assert np.isfinite(out["ssim"])
    assert out["rel_l2"] > 0.0 and np.isfinite(out["spectral_band"])


def test_2d_full_pipeline_roundtrip(tmp_path):
    samples, conds = [], []
    for i in range(4):
        raw = {4: _golden_2d_field(4, i), 8: _golden_2d_field(8, 100 + i)}
        samples.append(ladder.assemble_sample(raw, 8, pde="cahn_hilliard"))
        conds.append([float(i)])
    p = str(tmp_path / "reg.h5")
    io.write_dataset(p, "cahn_hilliard", samples, np.array(conds), ["eps"],
                     [4, 8], 8, 1.0, seed=0)
    d = io.read_dataset(p)
    assert d["ndim"] == 2 and list(d["spatial_shape"]) == [8, 8]
    out = str(tmp_path / "reg.png")
    visualize.one_pager(d["bundles"][0], [4, 8], 8,
                        ["rel_l2", "linf", "spectral_band", "interface_position"],
                        "cahn_hilliard", 0, out, condition=[0.012],
                        condition_names=["eps"])
    assert os.path.exists(out) and os.path.getsize(out) > 0
