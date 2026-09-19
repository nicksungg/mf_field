# MFRNP — Multi-Fidelity Residual Neural Processes

This benchmark wraps the official implementation of **MFRNP** (Niu et al.,
ICML 2024) so it can be evaluated against this project's `ifc_raw` datasets.
MFRNP is a hierarchical neural-process model: at each fidelity level it learns
a latent context distribution from `(x, y)` pairs, and the final prediction is
the sum of (a) the highest-fidelity decoder output and (b) an ensemble of
lower-fidelity residual decoders (upsampled to the HF resolution). We use the
upstream `MultiFidelityModel` (`upstream/model/Model.py`) directly and lift
only the parts of `upstream/model/supervisor.py` that we need for a minimal
training/eval loop (skipping `ray` and `wandb`). Inputs/outputs are flattened
per-level to match MFRNP's flat-vector API and z-scored with the upstream
`StandardScaler`. The upstream repo is MIT-licensed.

Upstream: https://github.com/Rose-STL-Lab/MFRNP (commit
`614590a4ae7e0c9f2d0cc194640b0c41b7116a70`).

```bibtex
@inproceedings{niu2024mfrnp,
  title={Multi-Fidelity Residual Neural Processes for Scalable Surrogate Modeling},
  author={Niu, Ruijia and Wu, Dongxia and Kim, Kai and Ma, Yi-An and Watson-Parris, Duncan and Yu, Rose},
  booktitle={International Conference on Machine Learning (ICML)},
  year={2024},
  eprint={2402.18846},
  archivePrefix={arXiv}
}
```
