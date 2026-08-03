"""The generation CLI must run the completeness gate and record its verdict."""
import numpy as np

from mffp_sharp import generate
from mffp_sharp.pdes import fisher_kpp as fk


def test_generate_dataset_records_complete_verdict(tmp_path):
    top = {"seed": 3, "out_dir": str(tmp_path), "n_samples_per_pde": 3, "n_figures": 0,
           "ladder": {"resolutions": [8, 16], "hf_index": 1},
           "metrics": ["rel_l2"]}
    block = {"module": "fisher_kpp", "ndim": 2, "output_time": 5 * fk._DT,
             "sampling": {"D_range": [1e-4, 1e-3], "r_range": [5.0, 20.0],
                          "domain_size": 1.0}}
    summary = generate.generate_dataset("fisher_kpp_2d", block, top)
    cc = summary["condition_completeness"]
    assert cc["verdict"] == "COMPLETE"
    assert cc["reconstruction"]["rel_L2_max"] < 1e-12
