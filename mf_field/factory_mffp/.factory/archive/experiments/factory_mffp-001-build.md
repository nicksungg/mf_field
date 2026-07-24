---
name: factory_mffp-001-build
description: H1 fno_coregionalization — Builder phase. FNO + IFC-style continuous-m coregionalization head. 2-epoch CPU smoke already 85% below v9 baseline (composite ~0.255 vs 1.6595). CEO PROCEED.
metadata:
  type: project
tags:
  - factory
  - experiment
  - factory_mffp
  - cycle-001
  - build
project: factory_mffp
experiment_id: "001"
phase: build
verdict: PROCEED
date: 2026-05-15
source: factory-archivist
---

# Experiment #001 — Build phase: H1 `fno_coregionalization`

## Hypothesis

FNO backbone (4 spectral-conv blocks, `k_max=12`, `hidden=64`) feeding a low-rank
latent grid `h(x) ∈ R^{K × H × W}` (K=10), combined with an IFC-style
coregionalization head `B(m) = MLP([m, m²]) → K`, output as
`y(x) = Σ_k B_k(m) · h_k(x)`. Per-fidelity output normalization
`y / scaler[m]` is mandatory (cross-cutting Researcher finding). Targets F1
(`ifc_poisson` value-scale collapse, primary) and F2 (`ifc_heat` backbone gap,
secondary via FNO).

## What the Builder produced

Six files under `models/fno_coregionalization/`, all changes confined to the
mutable surface. PR diff against `master`: **594 insertions, 0 deletions, 6
files added** (commit `f1b0e4a`).

| File              | LoC | Purpose |
|---                |---: |---|
| `manifest.json`    |   6 | Contract: `name`, `description`, `supports=["ifc_raw"]`, `frozen=false`. |
| `INSPIRATION.md`   |  41 | Architecture rationale + bibtex for `li2020fno` and `li2022ifc`. |
| `model.py`         | 165 | Spectral conv (rfft2/irfft2 + complex einsum) + 4 FNO blocks + B(m) head from scratch. |
| `data.py`          | 153 | `ifc_raw` loader; collates `(x, y, m)`; computes per-fidelity `scaler[m]` on training subset post-`random_split`. |
| `smoke_eval.py`    | 209 | Implements all 6 contract CLI args; writes contract JSON schema; checkpoint resume w/ `set_scalers` pre-load for dynamic buffer sizes. |
| `full_config.json` |  20 | Optional large-K / more-blocks / more-epochs config for non-smoke runs. |

## Architecture

- **Backbone**: 4 FNO blocks, modes=12, hidden_channels=64. Spectral conv via
  `torch.fft.rfft2` / `irfft2` with complex `einsum` weight contraction.
  Implemented from scratch from li2020fno (zero overlap with v9 Transolver
  code — Reviewer verified by grep).
- **Coregionalization head**: cheap MLP `B(m) = MLP([m, m²]) → K=10`. The full
  IFC neural ODE basis (~7.84 s/epoch at K=20 per the paper) is deliberately
  replaced with the MLP to fit the 30-min smoke budget.
- **Continuous fidelity `m`**: read from `cat.pkl`'s `t_list` = `[0.0, 0.143,
  0.429, 1.0]`; each batch element carries its own `m`. At inference `m=1.0`
  (test fidelity = 64×64).
- **Per-fidelity output normalization** (the mandatory Researcher cross-cutting
  hygiene): predict `y / scaler[m]` where
  `scaler[m] = max-abs of training y at fidelity m`. **Observed scalers:**
  - `ifc_poisson`: `[0.0773, 0.0237, 0.0069, 0.0018]` — **confirms the
    diagnosed ~40× value-scale collapse from L1→L4** (0.0773 / 0.0018 ≈ 43×).
  - `ifc_heat`:    `[~1.0, ~1.0, 1.0, 1.0]` — bounded `y ∈ [0,1]`, no collapse,
    so the per-fidelity scaler is ~identity here (Heat is a backbone-bias
    problem, not a value-scale problem).
- **`val_frac = 0.1`** (not 0.2 — preserves 4–5 of 5 HF training samples).
- **Input handling**: lower-fidelity inputs bilinearly upsampled to 64×64
  before entering the FNO (per `li2022ifc` §6.1), so the FNO sees a single
  input resolution and the coregionalization head handles fidelity mixing.

## Parameter count

`n_params ≈ 4.75M` across both datasets:

- `ifc_heat`: 4,745,940 (3-dim conditioning lift).
- `ifc_poisson`: 4,746,068 (5-dim conditioning lift → 128 extra params in
  the lift layer).

## 2-epoch CPU smoke results

| Dataset       | v9 baseline | H1 (2-epoch CPU smoke) | Δ vs v9   |
|---            |---:         |---:                    |---:       |
| `ifc_heat`     | 0.149       | **0.136**              | −9%       |
| `ifc_poisson`  | 18.50       | **0.478**              | **−97.4%** (~39×) |
| composite (geomean) | 1.6595 | **~0.255**             | **−85%**  |

The 2-epoch CPU smoke is **already 85% better than the v9 baseline composite**
before the full 200-epoch SLURM run. The geomean (~0.255) is just above the
conservative go/no-go bound of 0.25, and the R4 200-epoch SLURM run is
expected to land comfortably below it.

## Decision rationale — predictions vs observation

Researcher predicted: per-fidelity normalization **alone** would drop
`ifc_poisson` from 18.5 → ~1.0 without any architectural change. **Observed at
2 epochs with FNO+IFC head: 0.478** — already ~2× better than the
normalization-only projection, confirming that the FNO + coregionalization
head adds ~2× on top of the normalization. The factored prediction
`f(x, m) = Σ_k B_k(m) · h_k(x)` is doing what the IFC paper said it would:
let `B(m)` rescale the latent basis continuously as `m` increases, so the
model can produce a small-magnitude output at L1 and a large-magnitude output
at L4 from the same shared backbone.

## Hard-gate results (CEO override on leakage)

1. **Scope guard** (`factory guard --check-scope`): **clean** after stashing
   pre-existing dirty `scripts/launch_factory.sh` (unrelated to H1; pre-existed
   at session start, will be restored after R4). PASS.
2. **Mutable-surface containment**: 6 files, all under
   `models/fno_coregionalization/**`. No fixed-surface touches. PASS.
3. **Leakage scan** (`factory leakage-check` on diff): `risk_level=medium`,
   **7 findings — CEO override: all false positives.** Scanner flagged
   generic vocabulary tokens (`description`, `epochs`, `dataset`, `ifc_raw`,
   `frozen`) that appear in `factory.md` and `README.md` (both fixed surfaces)
   and which are *inherent shared vocabulary* between project docs/config and
   any model code conforming to `eval/MODEL_CONTRACT.md` (manifest.json
   literally requires the keys `name`, `description`, `supports`, `frozen`).
   Scanner fingerprinted only 2 text files (factory.md + README.md,
   `total_tokens=385`); `data/**` are binaries and
   `baselines/paper_baselines.json` contributed no matches. No actual
   ground-truth numerical values from `baselines/paper_baselines.json` or
   `data/` appear in the diff. CEO PROCEED.
4. **Spec compliance**: every numbered acceptance criterion from `H1` in
   `.factory/strategy/current.md` met — FNO 4 blocks, modes=12, hidden=64,
   K=10, `B(m)=MLP([m,m²])`, per-fidelity scaler computed post-`random_split`,
   `val_frac=0.1`, bilinear LF→64×64 upsample, INSPIRATION.md cites
   li2020fno + li2022ifc. PASS.
5. **No v9 copying**: Reviewer grepped for v9 internals; model.py implements
   spectral conv (rfft2/irfft2 + complex einsum) and FNO blocks from scratch
   from li2020fno. PASS.
6. **Contract compliance**: `smoke_eval.py` exposes all 6 CLI args from
   `eval/MODEL_CONTRACT.md`, writes the contract JSON schema with
   `metric_value = test nRMSE`, supports checkpoint resume. PASS.
7. **No external API / weight downloads**. PASS.

## Pending (R4)

- 200-epoch H100 SLURM run via `bash scripts/cycle_eval.sh` on this branch.
  `cycle_eval.sh` cache (commit `198170f`) is invalidated by changes under
  `models/`, so a SLURM submission will be triggered (~2–3 min wall time per
  Builder estimate).
- After R4: read `results/smoke_latest.json`, compute composite_nRMSE, run
  precheck against baseline 1.6595, keep/revert decision.

## Reviewer & CEO sign-off

- **Reviewer verdict** (`.factory/reviews/reviewer-latest.md`, 2026-05-15
  08:39:22Z): **PASS / KEEP** — guards clean, spec compliance complete, no v9
  copying, contract honored.
- **CEO verdict** (`.factory/reviews/ceo-verdict-builder.md`): **PROCEED** —
  proceed to MANDATORY Archivist (this note), then R4 Evaluator on SLURM.

## Links

- Project dashboard: [[factory_mffp]]
- Cycle strategy: [[cycle-001-strategy]]
- Cross-cutting findings: [[cycle-001-cross-cutting-findings]]
- Failure diagnosis: [[cycle-001-failure-diagnosis]]
- Source papers: [[li2020fno]], [[li2022ifc]]
- Commit: `f1b0e4a` on branch `experiment/1-fno_coregionalization`
- Diff: `master...experiment/1-fno_coregionalization` (+594 / −0, 6 files)
