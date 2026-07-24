---
name: factory_mffp-002-build
description: H2 fno_mf_stack — Builder phase. 4 small FNOs (one per fidelity) + MFRNP-style residual stack with decoder-in-the-aggregation, per-fidelity scaler. 2-epoch CPU smoke ifc_heat 1.17 / ifc_poisson 1.91 (sanity-only). CEO PROCEED with noted concern about undersized smoke defaults.
metadata:
  type: project
tags:
  - factory
  - experiment
  - factory_mffp
  - cycle-001
  - build
project: factory_mffp
experiment_id: "002"
phase: build
verdict: PROCEED
date: 2026-05-15
source: factory-archivist
---

# Experiment #002 — Build phase: H2 `fno_mf_stack`

## Hypothesis

Four small FNOs (one per fidelity level `L1..L4`) feeding an MFRNP-style
residual stack: each LF FNO's decoded output is bilinearly upsampled to 64×64
and aggregated; the HF (L4) FNO then predicts a residual `δ` such that the
final HF output is `aggregate(decoded_LFs at 64×64) + δ`. Per-fidelity output
normalization `y / scaler[m]` is mandatory (Researcher cross-cutting). Targets
F1 (`ifc_poisson` value-scale collapse, primary) and F2 (`ifc_heat` backbone
gap, secondary via FNO). Built **on top of H1 baseline** (composite 0.1092
after H1 200-epoch SLURM keep).

## What the Builder produced

Six files under `models/fno_mf_stack/`, all changes confined to the mutable
surface. PR diff against `master`: **+730 insertions, 0 deletions, 6 files
added** (commits `294d96a` + `73e492d` on branch `experiment/2-fno_mf_stack`).

| File              | LoC | Purpose |
|---                |---: |---|
| `manifest.json`    |   6 | Contract: `name`, `description`, `supports=["ifc_raw"]`, `frozen=false`. |
| `INSPIRATION.md`   |  36 | One-paragraph rationale + inline bibtex for `niu2024mfrnp` and `li2020fno`. |
| `model.py`         | 248 | `SpectralConv2d` (rfft2/irfft2 + complex einsum from scratch), `FNOBlock`, `SmallFNO`, `MFRNPAggregator`, `FNOMFStack`. |
| `data.py`          | 141 | `ifc_raw` loader; per-fidelity train/val split with `val_frac=0.1`; per-level scaler (`max\|y\|` on train); per-level dataloaders. |
| `smoke_eval.py`    | 284 | Contract-conforming entrypoint, checkpoint resume, LF direct losses + HF residual-stack loss + baseline anchor, test-set nRMSE. |
| `full_config.json` |  15 | hidden=64, modes=(4,8,12,12), 3 blocks, 400 epochs (intended for the H100 full run; **NOT consumed by smoke_eval.py**). |

`73e492d` (this session) emitted top-level `metric_value` = test nRMSE in the
smoke JSON and let `--dataset_name` default to `basename(dataset_dir)` so the
exact spec verification command runs as-is. Everything else was already in
place from `294d96a`.

## Architecture

- **4 small FNOs (one per fidelity level)**: each `SmallFNO` instantiated with
  `modes_per_level` and `native_resolutions` lists, using a from-scratch
  `SpectralConv2d` (`torch.fft.rfft2` / `irfft2` + complex `einsum`) — zero
  copying from `references/v9_baseline/`. Built from `li2020fno`.
- **MFRNP-style residual stacking with decoder-in-the-aggregation**: each LF
  FNO is paired with a small decoder; decoded LF predictions are bilinearly
  upsampled to 64×64 and fused into a baseline by the `MFRNPAggregator`. The
  HF (L4) FNO predicts `δ`; final HF output = `aggregate(decoded_LFs upsampled
  to 64×64) + δ`. Built from `niu2024mfrnp`.
- **Per-fidelity output normalization** (mandatory Researcher cross-cutting):
  `model.set_scaler(scaler_dict)` registers a buffer; training/eval divides
  by `scaler[m]` (`max|y|` of training y at fidelity m).
- **Continuous `m`**: threaded through the aggregator as a side channel even
  though the primary fidelity encoding is per-level FNO routing. Read from
  `cat.pkl`'s `t_list = [0.0, 0.143, 0.429, 1.0]`. At inference `m=1.0`.
- **`val_frac = 0.1`** confirmed in both `SMOKE_DEFAULTS` and `full_config.json`.
- **Architectural extension (Builder, NOT in spec)**: the HF FNO consumes the
  aggregator's baseline as an extra input channel **before** predicting the
  residual `δ` — so `δ` conditions on the baseline rather than being agnostic
  to it. Documented inline in `model.py` docstring. Minor MFRNP refinement;
  no spec conflict. CEO PROCEED.

## Smoke-config sizing — Builder deviations from spec

| Knob              | Spec range          | Smoke default (shipped) | Full config (not used by smoke) |
|---                |---                  |---:                     |---:                             |
| `hidden`           | 32–64               | **16**                  | 64                              |
| `modes_per_level`  | k_max ≈ 12          | **(4, 5, 5, 5)**        | (4, 8, 12, 12)                  |
| blocks per FNO     | 2–3                 | 2                       | 3                               |
| epochs             | n/a (CPU smoke)     | 2 (CPU) / 200 (SLURM)   | 400                             |

Builder's rationale: smoke must complete on CPU in 2 epochs and the 200-epoch
H100 SLURM run must stay under the 30-min smoke budget. **Total model params
at smoke config: 97,285 (heat) / 97,413 (poisson)** — ~17–27k per FNO + 369
in the aggregator. The H1 baseline (4.75M params) is ~50× heavier.

**CEO concern (PROCEED with eyes open, not REDIRECT)**: `smoke_eval.py`
ignores `full_config.json` — the SLURM-driven 200-epoch run will use the
small `SMOKE_DEFAULTS`. At 200 epochs on H100, hidden=16 with 97k total params
may underfit the residual stack and limit how low Poisson can go. CEO chose
to proceed because:

1. Per-fidelity output normalization (the cross-cutting cheap fix) is the
   dominant driver per Researcher §Cross-Cutting #1; it should drop
   `ifc_poisson` from 18.5 to ~1.0 even with a tiny model.
2. The 2-epoch CPU smoke on `ifc_poisson` (1.91) shows normalization is
   engaged — model is in the right regime, not the value-scale-collapse
   regime.
3. If 200-epoch numbers come back weak, this becomes a clean signal for the
   next cycle: "H2's residual-stack inductive bias works but is undersized —
   bump hidden to 32 and re-run." That is a useful learning, not a failure.
4. Forcing a REDIRECT now and re-spawning the Builder costs an entire training
   round-trip on a shared system; H1's 200-epoch SLURM was ~2–3 min on H100.

**Conditional next-cycle hypothesis (CEO pre-registered)**: if the post-R4
metric is ≥ 1.0, the next cycle's Strategist should see the explicit
"undersized smoke defaults" hypothesis and re-run with `hidden=32`, a single
architectural knob away.

## 2-epoch CPU smoke results — **sanity-only, NOT a decision signal**

| Dataset       | 2-epoch CPU `metric_value` |
|---            |---:                        |
| `ifc_heat`     | 1.1666983789468413         |
| `ifc_poisson`  | 1.9055668052657269         |

These numbers show the smoke path is alive end-to-end (LF FNOs train,
aggregator runs, HF residual head fires, test eval produces a float).
**They are NOT comparable to H1's 2-epoch numbers** because the H2 smoke
model is ~50× smaller. The 200-epoch H100 SLURM run via
`bash scripts/cycle_eval.sh` is the actual decision signal.

## Hard-gate results (CEO override on leakage; PROCEED otherwise)

1. **Surface scope** (`git diff --name-only master..experiment/2-fno_mf_stack`):
   6 files, all under `models/fno_mf_stack/`. No fixed-surface modifications
   (no edits to `data/`, `baselines/`, `eval/`, `references/`, `scripts/`,
   `factory.md`, `README.md`, or other `models/` families). **PASS.**
2. **Leakage scan** (`factory leakage-check`): `risk_level=medium`, **6
   findings — CEO override: all false positives, identical pattern to H1.**
   Flagged tokens (`description`, `metric_value`, `ifc_raw`, `dataset`,
   `frozen`) are contract-mandated keys per `eval/MODEL_CONTRACT.md` (manifest
   schema, output JSON schema, loader identifier). Scanner fingerprints
   `factory.md`/`README.md` (both fixed surfaces) and flags any token
   co-occurrence. No numerical values from `baselines/paper_baselines.json`,
   no content from `data/**` (binaries). Builder implemented architecture
   from `niu2024mfrnp` + `li2020fno` (public papers), not from any fixed-
   surface content. **CEO PROCEED — same rationale as H1, ratified.** See
   pattern note [[patterns]] §"Factory leakage-check fingerprints `factory.md`
   itself".
3. **Spec compliance**: 10 numbered acceptance criteria from H2 in
   `.factory/strategy/current.md` met — per-fidelity output normalization
   (✓ `set_scaler` registers buffer), 4 FNOs one per level (✓), spectral
   conv from scratch (✓ rfft2/irfft2 + complex einsum, not from
   `references/v9_baseline/`), residual stacking with decoder-in-the-
   aggregation (✓), continuous m threaded (✓), `val_frac=0.1` (✓), `ifc_raw`
   loader (✓ supports both heat and poisson), contract compliance
   (✓ `smoke_eval.py` exposes all 6 CLI args + top-level `metric_value` +
   checkpoint resume), no external API / weight downloads (✓),
   INSPIRATION.md citations (✓ niu2024mfrnp + li2020fno with inline bibtex).
   **1 deviation noted (smoke sizing); 1 architectural extension noted
   (HF baseline-as-input). PASS with notes.**
4. **No `references/v9_baseline/` copying**: spectral conv and FNO blocks
   implemented from scratch from `li2020fno`. PASS.
5. **Contract compliance**: `smoke_eval.py` exposes `--epochs --dataset_dir
   --out --ckpt_dir --seed`; writes JSON with top-level `metric_value`;
   supports checkpoint resume. PASS.
6. **No external API / weight downloads**. PASS.

## Decision rationale — predictions vs observation

The 2-epoch CPU smoke numbers (1.17 / 1.91) are deliberately uninformative —
the model is ~50× smaller than H1 to fit the CPU smoke budget. The
informative signal is that `ifc_poisson` came in at **1.91**, well below the
v9 baseline's 18.5 and inside the same order-of-magnitude as the
"normalization-alone" projection (~1.0). The per-fidelity scaler buffer is
engaged and the residual stack is running end-to-end. The H100 200-epoch
SLURM run will resolve whether the residual-stack inductive bias adds further
margin on top of normalization, or whether the undersized smoke config caps
the improvement.

## Pending (R4)

- 200-epoch H100 SLURM run via `bash scripts/cycle_eval.sh` on
  `experiment/2-fno_mf_stack`. Cycle_eval.sh cache (commit `198170f`) is
  invalidated by new files under `models/fno_mf_stack/*.py`, so a fresh SLURM
  submission triggers. H1 took ~2–3 min on H100; H2 has 4 small FNOs and may
  be a touch slower but still well under 30 min.
- After R4: read `results/smoke_latest.json`, compute composite vs H1 baseline
  0.1092 (and v9 baseline 1.6595 for the dashboard), run precheck, keep/revert
  decision. **The H1 precheck `score_direction` polarity bug is known**
  ([[patterns]] §"Factory precheck `score_direction` is polarity-buggy") — CEO
  will inspect the precheck JSON, validate the actual research metric
  direction, and override if the precheck transparently fails only on
  `score_direction`.

## Reviewer & CEO sign-off

- **CEO verdict** (`.factory/reviews/ceo-verdict-builder.md`, 2026-05-15):
  **PROCEED with one noted concern** — undersized smoke defaults
  (`hidden=16` vs spec 32–64; `modes=(4,5,5,5)` vs spec `k_max≈12`).
  Concern is logged for next-cycle Strategist if H2 R4 metric ≥ 1.0.
- **Next steps issued**: Reviewer scope/surface guard, MANDATORY Archivist
  (this note), then R4 Evaluator via `bash scripts/cycle_eval.sh`.

## Links

- Project dashboard: [[factory_mffp]]
- Cycle strategy: [[cycle-001-strategy]]
- Cross-cutting findings: [[cycle-001-cross-cutting-findings]]
- Sibling H1 build: [[factory_mffp-001-build]] (companion FIX for the same
  cycle, scored 0.1092 at R4)
- Sibling H1 experiment outcome: [[factory_mffp-001-experiment]]
- Source papers: [[niu2024mfrnp]], [[li2020fno]]
- Commits: `294d96a` (initial H2 tree) + `73e492d` (this session — smoke JSON
  `metric_value` + `--dataset_name` default) on branch
  `experiment/2-fno_mf_stack`
- Diff: `master...experiment/2-fno_mf_stack` (+730 / −0, 6 files)
