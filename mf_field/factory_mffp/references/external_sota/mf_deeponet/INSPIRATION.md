# MF-DeepONet — Multifidelity Deep Operator Networks

This benchmark wraps the official multifidelity DeepONet implementation of
**Lu et al.** (Phys. Rev. Research 4, 023210, 2022) so it can be evaluated
against this project's `ifc_raw` datasets. The model is a two-branch operator
network: a branch network encodes the input function (here: HF conditioning
vector concatenated with the flattened low-fidelity field), a trunk network
encodes the query coordinate (here: 2-D xy on the HF grid), and the output is
their inner product (`DeepONetCartesianProd` evaluates the branch sample at
every trunk coordinate). We use the *residual / stacked-branch* multifidelity
recipe from `upstream/src/poisson/deeponet_poisson.py` — train DeepONet to
predict `y_HF - upsample(y_LF)` from `concat(x, vec(y_LF))`, then add back the
upsampled LF field at inference. We build the model with `deepxde` 1.15.0
(pytorch backend) directly, mirroring upstream's `dde.Model.train` call but
adding ifc_raw data loading, per-field z-score normalization, resume support,
and the MODEL_CONTRACT JSON output. The upstream repo is Apache-2.0 licensed.

Upstream: https://github.com/lu-group/multifidelity-deeponet (commit
`983e170773fe9a6b1f89f7e323154ac35fd844a5`).

```bibtex
@article{lu2022multifidelity,
  title={Multifidelity deep neural operators for efficient learning of partial differential equations with application to fast inverse design of nanoscale heat transport},
  author={Lu, Lu and Pestourie, Raphael and Johnson, Steven G. and Romano, Giuseppe},
  journal={Physical Review Research},
  volume={4},
  number={2},
  pages={023210},
  year={2022},
  eprint={2204.09157},
  archivePrefix={arXiv}
}
```
