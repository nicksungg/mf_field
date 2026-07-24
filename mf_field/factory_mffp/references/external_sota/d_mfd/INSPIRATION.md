# D-MFD (Disentangled Multi-Fidelity Deep Bayesian Active Learning)

We wrap the 2-fidelity variant of Wu et al.'s D-MFD model
(`upstream/dmfdal_2f/model/pytorch/model.py`) as a multi-fidelity surrogate
baseline. The upstream code is built around an active learning loop that
selects new query points and re-trains the surrogate each cycle; here we
strip that loop away and use only the surrogate forward pass. The model is a
deep latent-variable Neural Process: per level it factors the encoder into a
local branch (level-specific information) and a global branch (cross-level
shared information), then Bayesian-aggregates the per-sample latent
distributions into a per-level posterior `z` and decodes back to the
field. We train with NLL + KLD losses on both fidelities; the global-
distribution regularizer (which requires LF/HF data paired over the same
inputs) is dropped because the IFC datasets do not provide paired data
across fidelities. nRMSE is computed in raw units on the HF test split.

```bibtex
@inproceedings{wu2023disentangled,
  title={Disentangled Multi-Fidelity Deep Bayesian Active Learning},
  author={Wu, Dongxia and Niu, Ruijia and Chinazzi, Matteo and Vespignani, Alessandro and Ma, Yi-An and Yu, Rose},
  booktitle={International Conference on Machine Learning},
  year={2023},
  organization={PMLR},
  note={arXiv:2305.04392}
}
```
