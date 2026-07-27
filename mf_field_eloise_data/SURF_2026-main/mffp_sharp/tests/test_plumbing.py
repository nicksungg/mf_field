import numpy as np

from mffp_sharp.pdes import cahn_hilliard, kuramoto_sivashinsky, euler


def test_ch_sample_configs_shape():
    cfg = {"eps_range": [0.02, 0.04], "mobility_range": [0.8, 1.2],
           "mean_composition_range": [-0.05, 0.05], "domain_size": 1.0}
    specs = cahn_hilliard.sample_configs(5, cfg, ndim=2, seed=0)
    assert len(specs) == 5
    for s in specs:
        assert s["ndim"] == 2 and "eps" in s and "seed" in s
    assert 2 in cahn_hilliard.NDIMS_SUPPORTED


def test_ks_sample_configs_shape():
    cfg = {"L_range": [22.0, 36.0], "ic_amplitude_range": [0.05, 0.2]}
    specs = kuramoto_sivashinsky.sample_configs(3, cfg, ndim=2, seed=1)
    assert len(specs) == 3 and all("L" in s for s in specs)


def test_euler_sample_configs_injects_gamma():
    cfg = {"jitter_frac": 0.1, "gamma": 1.4}
    specs = euler.sample_configs(4, cfg, ndim=2, seed=2)
    assert len(specs) == 4
    assert all(s["gamma"] == 1.4 and "quadrants" in s for s in specs)
    assert euler.NDIMS_SUPPORTED == (2,)


def test_registry_has_existing_modules():
    from mffp_sharp import generate
    for name in ("euler", "cahn_hilliard", "kuramoto_sivashinsky"):
        assert name in generate._MODULES


def test_generate_dataset_ch_end_to_end(tmp_path):
    from mffp_sharp import generate
    top = {
        "seed": 0, "out_dir": str(tmp_path), "n_samples_per_pde": 2, "n_figures": 0,
        "ladder": {"resolutions": [16, 32], "hf_index": 1},
        "metrics": ["rel_l2", "linf", "spectral_band"],
    }
    block = {"module": "cahn_hilliard", "ndim": 2, "output_time": 0.05,
             "sampling": {"eps_range": [0.03, 0.03], "mobility_range": [1.0, 1.0],
                          "mean_composition_range": [0.0, 0.0], "domain_size": 1.0}}
    summary = generate.generate_dataset("cahn_hilliard", block, top)
    assert summary["pde"] == "cahn_hilliard"
    assert (tmp_path / "cahn_hilliard_sample.h5").exists()
    assert 16 in summary["lf_vs_hf"]
