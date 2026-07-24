---
name: factory_mffp-004-build
description: H3 fno_coreg_residual (cycle-002 exp_id=4) — Builder phase. Novel hybrid extension composing H1's continuous-m basis-head (li2022ifc) with H2's MFRNP residual stack + decoder-in-the-aggregation (niu2024mfrnp). New family directory models/fno_coreg_residual/, 6 files added +939/-0, single commit 0c46f43. Pre-flight CPU smoke finite on both ifc_heat (0.5708) and ifc_poisson (0.3559) — pre-optimization values; basis-head zero-init means architecture starts as pure-H2 aggregator at epoch 0. CEO PROCEED on both Builder and Reviewer; Reviewer PASS/KEEP with all four guard sub-checks clean.
metadata:
  type: project
tags:
  - factory
  - experiment
  - factory_mffp
  - cycle-002
  - build
  - h3
  - hybrid
project: factory_mffp
experiment_id: "004"
phase: build
verdict: PROCEED
date: 2026-05-15
source: factory-archivist
---

# Experiment #004 — Build phase: H3 `fno_coreg_residual` (cycle-002 novel hybrid)

## Hypothesis

**H3: COMBINE — novel hybrid extension**. Composes the two cycle-001 family
wins as orthogonal inductive biases on the HF head:

```
y_HF = MFRNPAggregator([upsampled_decoded_LFs, m_broadcast])
     + Σ_{k=1..K} B_k(m) · h_k(x)
```

- **Base anchor** = H2's MFRNP residual stack with decoder-in-the-aggregation
  (`niu2024mfrnp`).
- **Continuous-m basis residual** = H1's per-basis coefficient functions
  `B(m) = MLP_B([m, m²])` over K learned bases `h_k(x)` (`li2022ifc`).
- **Basis-head last layer zero-initialised** so the architecture **starts as
  pure-H2 aggregator** at epoch 0, and optimisation decides how much basis
  residual to grow (per H3 spec — small/zero init as the safety mechanism).

H3 targets **F5 INVERSE_COMPLEMENTARY_FAMILIES** — the cross-family
observation that H1 dominates `ifc_heat` (0.0154) and H2 dominates
`ifc_poisson` (0.0979). H4 partially resolved F5 *within* the H2 family
(`ifc_heat` 0.0999, `ifc_poisson` 0.0596, composite 0.07719). H3 attempts
the **cross-family architectural resolution** — keep the MFRNP residual
machinery that won Poisson and **add** the per-basis continuous-m head
that won Heat.

Target (per strategist, conditional on both family wins surviving
composition): composite ~0.04, `ifc_heat` ~0.02-0.05, `ifc_poisson`
~0.04-0.10. H3 only displaces H4 as project best if composite is well
below 0.077.

## Branch + commit

- **Branch**: `experiment/4-fno_coreg_residual`.
- **Base**: master @ `198170f` (cycle-001 close + cycle-002 launcher
  improvements; H1/H2/H4 not yet merged).
- **Single new commit**: `0c46f43` — "H3: add models/fno_coreg_residual (H1
  basis-head + H2 MFRNP residual stack hybrid)".
- **Chain**: master ← H3 (`0c46f43`). H3 is a **new family directory**
  (clean re-derivation), not a branch-from-H2 capacity bump like H4 was.

## What the Builder produced

`git diff --stat master..experiment/4-fno_coreg_residual`:

| File                                          | Lines  | Purpose                                       |
|---                                            |---:    |---                                            |
| `models/fno_coreg_residual/manifest.json`     | +9     | Contract: name, supports=ifc_raw, smoke_entrypoint |
| `models/fno_coreg_residual/INSPIRATION.md`    | +41    | xing2020deepcoreg + li2022ifc + niu2024mfrnp + li2020fno inline bibtex; explicit "novel hybrid extension — no direct precedent" label |
| `models/fno_coreg_residual/model.py`          | +334   | 4 per-fidelity FNOs, FieldDecoder, MFRNPAggregator, BasisHead, per-fidelity scaler buffer |
| `models/fno_coreg_residual/data.py`           | +167   | `ifc_raw` loader, `stratified_train_val_split(val_frac=0.1)`, `compute_per_level_scaler` |
| `models/fno_coreg_residual/smoke_eval.py`     | +363   | Contract CLI; full-config sizes (NO SMOKE_DEFAULTS regression) |
| `models/fno_coreg_residual/full_config.json`  | +25    | epochs=400; Poisson HF=2/LF=0.25 loss-weight ablation behind a flag |
| **Total**                                     | **+939 / -0, 6 files** |                                       |

## Architecture (`model.py`)

Verified line-by-line against H3 spec (`.factory/strategy/current.md` lines 185-222) by both CEO and Reviewer:

- **4 per-fidelity `FNOBackbone`** at full-config sizes: `hidden=64`,
  `modes_per_level=(4, 8, 12, 12)`, `n_blocks=3` (one block per spectral
  conv pair) — matches `li2020fno` and the H2-incumbent full config
  (model.py:104-115, smoke_eval.py:42-58). Critical non-regression: there
  is **no SMOKE_DEFAULTS** under-capacity trap (the cycle-001 H2
  anti-pattern). Smoke uses the same sizes as full config.
- **FieldDecoder** per fidelity, `decoder_hidden=32` per published MFRNP
  (model.py:118-133). Implements decoder-in-the-aggregation.
- **MFRNPAggregator** consumes `[upsampled_decoded_LFs, m_broadcast]`
  (model.py:138-161). Decoder-in-the-aggregation pattern; continuous m
  threaded into the aggregator.
- **HF head** `y = agg + Σ_{k=1..K} B_k(m) · h_k(x)` with K=10
  (model.py:312-325). **K=10** matches H1's `fno_coregionalization`.
- **BasisHead** = `MLP_B([m, m²])` — cheap MLP per H3 spec (explicitly
  NOT a neural ODE), last `Linear` weight + bias **zero-initialised**
  (model.py:166-186). Consequence: at epoch 0, `B_k(m) ≡ 0`, so
  `y_HF = agg` (pure H2 behavior). Optimisation grows the basis residual.
- **Per-fidelity output normalization** via non-learnable `scaler` buffer
  registered after train/val split, computed from training subset only
  (model.py:252-260; data.py:104-114).
- **Bilinear upsample LF→HF at 64×64** inside the model
  (model.py:308-310).
- **Continuous m** threaded into BOTH the aggregator AND the basis head
  (model.py:155-158, 319).

## Contract compliance (`manifest.json` + `smoke_eval.py`)

- `manifest.json`: name=`fno_coreg_residual`, version, supports=`["ifc_raw"]`,
  supported_datasets=`["ifc_heat", "ifc_poisson"]`, smoke_entrypoint=`smoke_eval.py`.
- `smoke_eval.py` CLI: `--epochs --dataset_dir --out --ckpt_dir --seed`
  (lines 343-351).
- Output JSON: top-level `metric_value` as **finite float** = test nRMSE
  (line 325). Both pre-flight runs produced contract-compliant JSON.
- Resume-from-ckpt scaffolding present (smoke_eval.py:217-232, 277-289) —
  matches `cycle_eval.sh` expectations.
- `lf_loss_weights` / `hf_loss_weight` exposed in `full_config.json`; the
  Poisson knob `HF=2, LF=0.25` is gated **behind a flag**, default
  uniform 1.0/1.0 in smoke (smoke_eval.py:54-56; full_config.json:20-24).

## Pre-flight CPU smoke verification

Builder ran `--epochs 2` on both target datasets:

| Dataset        | metric_value | finite | JSON top-level | Interpretation                                |
|---             |---:          |---     |---             |---                                            |
| `ifc_heat`     | **0.5708**   | ✓      | ✓              | loss-curve checkpoint, not target performance |
| `ifc_poisson`  | **0.3559**   | ✓      | ✓              | loss-curve checkpoint, not target performance |

**Why these values are not the performance signal**: the basis-head last
layer is zero-initialised, so at epoch 0 the architecture **is the pure
H2 aggregator** with no basis residual contribution. The 2-epoch smoke
captures only the very start of the optimisation trajectory before the
basis residual has had time to grow. The eval gate (R4 200-epoch
`cycle_eval.sh`) is the actual decision signal.

## Hard-gate results

### Surface scope (MANDATORY)

`git diff --name-only master..experiment/4-fno_coreg_residual`:

- All 6 files under `models/fno_coreg_residual/**` ✓
- Zero touches to `data/**`, `baselines/**`, `eval/**`, `references/**`,
  `factory.md`, `README.md`, `scripts/**` ✓
- **New family directory** — no edits to sibling families
  (`models/fno_coregionalization/`, `models/fno_mf_stack/`) ✓
- Matches declared `mutable_surfaces` in `.factory/config.json`.

### Ground-truth leakage scan (MANDATORY)

`factory leakage-check --text-file <diff>`: **risk_level=medium, 7 findings**
— **all 7 documented substring-collision false-positives** (same precheck
infrastructure bug pinned in [[patterns]] across cycles 001-002 H1/H2/H4):

- `ifc_raw`, `ifc_heat`, `ifc_poisson` — dataset names that the eval contract
  **requires** (`research_constraints` in `factory.md`: "New families must
  support at least the `ifc_raw` dataset loader"; "smoke datasets are
  `ifc_heat` and `ifc_poisson`"). They appear in `manifest.json` because the
  contract mandates them.
- `description`, `frozen` — generic JSON-key strings in `manifest.json`;
  collide with common English words in `factory.md`/`README.md`.
- `001` — the literal digits "001" appear in `INSPIRATION.md` only via the
  prose phrase "cycle-001" (cycle reference), not as ground-truth-derived
  logic.

CEO confirmed: **no actual ground-truth leakage**. Architecture constants
(`hidden=64`, `modes=(4,8,12,12)`, `K=10`, `decoder_hidden=32`) all trace
to source papers and the H3 strategist spec, not test labels. No
hardcoded answers, no per-instance lookups, no constants derived from
test labels.

### Sacred Rules (all PASS)

- No deleted tests (`git diff --diff-filter=D` empty) ✓
- No fixed-surface diff lines ✓
- No secrets / credentials / external API calls ✓
- No `eval/` threshold change ✓

### Reviewer guard sub-checks (all PASS)

`factory guard --check-scope` → `clean`:

- `eval_immutable`: PASS (no touches to `eval/**`)
- `git_clean`: PASS (worktree clean at `0c46f43`)
- `experiment_branch`: PASS (`experiment/4-fno_coreg_residual`)
- `scope`: PASS (clean)

## Reviewer & CEO sign-off

- **CEO verdict on Builder** (`.factory/reviews/ceo-verdict-builder.md`,
  2026-05-15): **PROCEED**. Clean, spec-faithful implementation. Surface
  constraint check passes; leakage flag dismissed as known
  substring-collision false-positive; line-by-line spec verification
  matches the diff.
- **Reviewer verdict** (`.factory/reviews/reviewer-latest.md`,
  2026-05-15T12:47:43Z): **PASS / KEEP**. Substantive line-by-line
  spec-fidelity verification against H3 spec lines 185-222 in `model.py`,
  `smoke_eval.py`, `data.py`, `manifest.json`, `full_config.json`,
  `INSPIRATION.md`. Confirmed `model.py` is a **clean re-derivation from
  primitives** — no copy from `references/v9_baseline/`.
- **CEO ratification of Reviewer** (`.factory/reviews/ceo-verdict-reviewer.md`,
  2026-05-15): **PROCEED**. Reviewer's surface check matches CEO's
  independent `git diff --name-only` result; spec-fidelity matches CEO's
  spot-check; minor non-blocking observations (`hf_res` default vs runtime,
  `agg_anchor_weight=0.5` regularizer, `evaluate_split` defensive upsample)
  validated as non-issues.
- **Three unanimous PROCEED/PASS**. Build phase complete.

## Reviewer's non-blocking observations

- `hf_res` is hardcoded to 64 in the model constructor default but driven
  from `native_resolutions[-1]` in `smoke_eval.py:204` — consistent in
  practice.
- The aggregator anchor loss `agg_anchor_weight=0.5` is a sensible
  regulariser not strictly required by the spec but matches H2's training
  recipe and keeps the MFRNP baseline meaningful.
- `evaluate_split` upsamples pred to target if shapes mismatch
  (`smoke_eval.py:126-130`) — defensive but unused in the standard
  `ifc_raw` HF-only test path.

## Pending (R4)

- 200-epoch run via `bash scripts/cycle_eval.sh` on
  `experiment/4-fno_coreg_residual`. **Cache MUST MISS** because
  `models/fno_coreg_residual/` is a new directory (new code_hash); v9
  (under `references/`) will hit cache; H1/H2/H4 caches are unaffected.
- **R5 verdict logic**: monotonic check is `composite_after <= previous_best`.
  Comparison anchors:
  - master baseline: **1.6595** (v9 geomean)
  - cycle-001 H1 (`fno_coregionalization`): **0.10919**
  - cycle-001 H2 (`fno_mf_stack`): **0.11173**
  - cycle-002 H4 (`fno_mf_stack` v2): **0.07719** ← **project best**
- H3 only displaces H4 as project best if composite is **well below 0.077**.
- Expected precheck infrastructure false-positives at R5 — `score_direction`
  polarity, scope/fixed_surfaces empty-detail, ground_truth_leakage
  substring-collision, scope-tuple shape. Same 4 known bugs as cycles 001-002
  H1/H2/H4. CEO=KEEP-intent / factory=REVERT-bookkeeping branch-preserved
  pattern will likely apply again if H3 improves the metric.

## Cross-project pattern note

H3 is the **third pre-registered F5 INVERSE_COMPLEMENTARY_FAMILIES test**
in the project's history (cycle-001 archive already flagged the H1+H2
hybrid as "the cycle-002/003 ensemble lead"). The strategist's cycle-002
plan downgraded H3 from "structural necessity" to "**optional upside
test**" after H4 partially resolved F5 within the H2 family. H3 is a
clean stress test of whether the two family inductive biases **compose
multiplicatively** (basis residual + MFRNP aggregator both load-bearing)
versus **redundantly** (one inductive bias subsumes the other once the
H2 family is at adequate capacity). Either outcome teaches us something
about the F5 resolution geometry — see [[patterns]] §"Within-family F5
resolution".

## Links

- Project dashboard: [[factory_mffp]]
- Cycle strategy: [[cycle-002-strategy]]
- Cycle-001 close-out: [[cycle-001-summary]]
- Cycle-002 H4 (current project best): [[factory_mffp-003-build]],
  [[factory_mffp-003-experiment]], [[factory_mffp-003-outcome]]
- Cycle-001 H1 (basis-head provenance): [[factory_mffp-001-build]],
  [[factory_mffp-001-experiment]]
- Cycle-001 H2 (MFRNP residual stack provenance): [[factory_mffp-002-build]],
  [[factory_mffp-002-experiment]]
- Failure analysis: [[failure-analysis-cycle-002]] — F5
  INVERSE_COMPLEMENTARY_FAMILIES (the failure mode H3 targets)
- Source papers: [[li2022ifc]] (basis-head + continuous m provenance),
  [[niu2024mfrnp]] (MFRNP residual stack + decoder-in-the-aggregation
  provenance), [[li2020fno]] (spectral conv backbone),
  [[xing2020deepcoreg]] (coregionalization framing)
- Commit: `0c46f43` on branch `experiment/4-fno_coreg_residual`
- Base: master @ `198170f`
- Diff: `master..experiment/4-fno_coreg_residual`
  (+939 / -0, 6 files, all under `models/fno_coreg_residual/**`)
