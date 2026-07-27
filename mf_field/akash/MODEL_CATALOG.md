# akash MF-FNO model catalog

15 new multi-fidelity Fourier Neural Operator families, each a candidate to beat the benchmark
winner `mf_fno_transfer_film` (geomean rel-L2 **0.0082**). Every family is **contract-compatible**
(`factory_mffp/eval/MODEL_CONTRACT.md`): `manifest.json` + `model.py` + `smoke_eval.py`, reusing the
shared backbone (`akash/common/backbone.py`) and fair-eval plumbing (`akash/common/mffp.py` →
`load_mf_dataset`, `resolve_grid`, `finalize_and_write`, 256-cap working grid, SMOKE hyperparams).
The *spectral backbone is identical across all families*, so each isolates its **new MF mechanism**.

**Scope:** these are *created + smoke-validated only* (smoke = 8–30 epochs on `ifc_heat`, far from a
real result). Benchmarking on the expanded dataset suite is owned by the user.

## How to run / register

```bash
cd /orcd/data/faez/001/nick/mf_field
factory_mffp/.venv/bin/python akash/models/<family>/smoke_eval.py \
  --dataset_dir factory_mffp/data/<dataset> --dataset_name <dataset> \
  --epochs <N> --out out.json --ckpt_dir ck/ --seed 0
```
Each writes the standard JSON (per-sample rel-L2 + bootstrap CI + params/latency/mem). They follow the
same CLI/resume contract as the in-tree families, so they drop into the existing `eval/score.py`-style
harness — point it at `akash/models/` or symlink the family dirs under `factory_mffp/models/`.

## Important data fact (validated)
`ifc_heat` test split is **HF-only** (`fids=[64]`) and train fidelities are **NOT sample-aligned**
(independent conds per fidelity, counts 100/50/20/5). Families needing test-LF or aligned LF/HF pairs
fall back gracefully (documented per family). Datasets that *do* expose aligned fids / test-LF will
exercise the richer paths.

## Families

### Tier S — core bets (generalize the winner; can't regress below FiLM)
| Family | Principle | Paper | Key extra metric |
|---|---|---|---|
| `mf_fno_hyperfilm` | Hypernetwork FiLM on `[X, task-context c, fidelity f]` (CAVIA-style + POSEIDON lead-time). `--null` reduces to FiLM. | POSEIDON, FiLM, MAML/CAVIA | null vs full nRMSE (reduction check) |
| `mf_fno_allpairs` | Train on **every** (src→tgt) fidelity pair, FiLM on `[X, f_src, f_tgt]`; O(L²) data amplification. | POSEIDON all2all | — |
| `mf_fno_spectral` | LF fixes **low** Fourier modes (frozen after pretrain); HF learns only the **high** band. FNO-native MF. | li2020fno | frozen-low-band byte-equal assert |
| `mf_fno_richardson` | Continuous-fidelity operator `G(X,f)`; extrapolate the discretization-error trend to super-fidelity. | POSEIDON, Richardson | `superfidelity_nRMSE` |

### Tier A — strong / novel
| Family | Principle | Paper | Key extra metric |
|---|---|---|---|
| `mf_fno_ptr` | Test-time PDE-residual refinement: K field-space gradient steps post-prediction. Wraps any model. | NITO | `nRMSE_pre_refine` (placeholder residual) |
| `mf_fno_diffprior` | PDE-native autoencoder prior + conditional latent DDIM `[X, z_lf]→z_hf`. Free UQ. Exports `ae.pt`. | OAT, LDM, DPS | `uq_mean_std` |
| `mf_fno_foundation` | BPOM set-encoder → fixed embedding (handles cond_dim 1–16); cross-dataset pretrain via `pretrain_all.py`. | NITO/OAT BPOM, POSEIDON | demo covered 8 datasets |
| `mf_fno_lora` | Pretrain LF, freeze, HF-finetune low-rank adapters only (~0.15% params). Adapter norm = LF→HF gap. | LoRA | `adapter_norm`, `pct_params_trained` |

### Tier B — wacky / cheap experiments
| Family | Principle | Key extra metric |
|---|---|---|
| `mf_fno_modeelastic` | Nested Fourier-mode dropout → one "anytime-fidelity" net | `elastic_nRMSE_by_k` |
| `mf_fno_residfid` | PDE-residual self-supervised auxiliary loss (placeholder Laplacian) | `final_train_resid_magnitude` |
| `mf_fno_selfdistill` | Pseudo-HF labels from LF model bootstrap HF-finetune | real vs pseudo counts |
| `mf_fno_latentaffine` | Tests "HF ≈ LF + constant latent direction" (reuses `diffprior/ae.pt`) | `shift_direction_consistency` (≈0.79 on ifc_heat → weak) |
| `mf_fno_incontext` | In-context operator learning, **no finetune** (DeepSets support set) | — |
| `mf_fno_pdesymbol` | FiLM on `[X, learned PDE-id embedding]` (cross-dataset value) | — |
| `mf_fno_cvblend` | Control-variate inference blend of LF+HF models | `cv_beta` |

## Notes
- Smoke nRMSE (~0.12–0.14 on ifc_heat at 8–30 epochs, 5 HF samples) is **not** comparable to the
  0.0082 benchmark — these are integration checks. Run at full budget to rank them.
- `mf_fno_ptr` and `mf_fno_residfid` ship a **placeholder** Laplacian-smoothness residual; the true
  governing-PDE residual needs each dataset's source/operator (not shipped in this data copy). The
  residual registry is structured to drop real operators in later.
- `mf_fno_diffprior` / `mf_fno_latentaffine` generative paths underperform on tiny-magnitude Poisson
  fields and tiny HF sets — expected; they're candidates with UQ, not yet contenders.
- Reduction checks confirmed: `mf_fno_hyperfilm --null` ≈ winner; `mf_fno_spectral` low band frozen
  byte-for-byte; `mf_fno_lora` zero-init adapters start == LF model.
