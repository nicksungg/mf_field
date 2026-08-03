import os

import numpy as np

from mffp_sharp.common import ladder, visualize


def test_radial_spectrum_1d_shape_and_dc():
    f = np.sin(np.linspace(0, 4 * np.pi, 64))
    sp = visualize.radial_spectrum(f)
    assert sp.shape == (64 // 2 + 1,)
    # a pure sine has near-zero DC component
    assert sp[0] < sp.max()


def test_radial_spectrum_2d_unchanged():
    rng = np.random.default_rng(0)
    f = rng.standard_normal((16, 16))
    sp = visualize.radial_spectrum(f)
    assert sp.ndim == 1 and sp.shape[0] >= 8


def test_one_pager_1d_writes_png(tmp_path):
    raw = {4: np.linspace(0, 1, 4), 8: np.sin(np.linspace(0, 2 * np.pi, 8))}
    b = ladder.assemble_sample(raw, 8, pde="kuramoto_sivashinsky")
    out = str(tmp_path / "onepager_1d.png")
    visualize.one_pager(b, [4, 8], 8, ["rel_l2", "linf", "spectral_band",
                        "interface_position"], "kuramoto_sivashinsky", 0, out,
                        condition=[7.0, 0.1], condition_names=["L", "ic_amplitude"])
    assert os.path.exists(out) and os.path.getsize(out) > 0


def test_one_pager_2d_writes_png(tmp_path):
    x = np.linspace(0, 1, 4)
    xh = np.linspace(0, 1, 8)
    raw = {4: np.add.outer(x, x), 8: np.add.outer(xh, xh)}
    b = ladder.assemble_sample(raw, 8, pde="cahn_hilliard")
    out = str(tmp_path / "onepager_2d.png")
    visualize.one_pager(b, [4, 8], 8, ["rel_l2", "linf", "spectral_band",
                        "interface_position"], "cahn_hilliard", 0, out,
                        condition=[0.012, 1.0, 0.0],
                        condition_names=["eps", "mobility", "mean_composition"])
    assert os.path.exists(out) and os.path.getsize(out) > 0
