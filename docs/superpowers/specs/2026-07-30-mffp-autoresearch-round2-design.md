# MFFP Autoresearch Round 2 — Design: Condition-Vector → HF Prediction

Date: 2026-07-30
Status: approved by Eloise (section-by-section); **launch is gated on Eloise's explicit go — do not start round 2 without it.**
Prior spec: `2026-07-28-mffp-autoresearch-design.md` (round 1). Round 2 inherits round 1's
pipeline, card format, agents, cron orchestration, and `tools/` library unless this spec says otherwise.

## 1. Motivation

Round 1 predicted HF fields from LF (coarse-solve) fields plus a condition vector. Two
deployment realities motivate round 2:

1. Companies often provide historical simulation *data* but no callable physics solver, so a
   model that needs a fresh LF solve at test time cannot be deployed.
2. Even where a solver exists, condition→HF inference skips the solver call entirely and is
   therefore faster.

Round 2 asks: **how well can models predict the HF field from the condition vector alone at
test time, and how much does LF data — available only during training — help?**

## 2. Test-time regime (decided)

**LF at train only.** Models may use LF fields freely during training (pretraining,
distillation, pseudo-LF emulation). At test time they receive **only the condition vector**.
This matches the company scenario literally (data handed over, no solver) and keeps
`ifc_poisson` viable (5 HF but 70 lower-fidelity train samples).

The rejected alternatives, for the record: "no LF anywhere" (on ifc_poisson that is 5
training samples total — the round would measure overfitting) and "both as paired arms"
(doubles compute; the value-of-LF question is instead handled by r2s4 diagnostics).

## 3. Metric (decided)

- Per-sample rel-L2 nRMSE; same panel geomean and cratered/guard rules as round 1.
- **Skill = nRMSE(model) / nRMSE(copy-LF)**, unchanged from round 1. The copy-LF
  denominator is computed **offline** from stored test LF fields, which models never see.
  Reading: skill < 1 means the no-solver model beats actually running the LF solver and
  copying its output — the headline deployment claim.
- Mandatory floor arms on every relevant card: **nearest-neighbor in condition space**
  (predict the HF train field whose condition vector is closest) and the **zero/mean
  predictor** (round 1's helmholtz lesson: the champion lost to the zero predictor there).
- All reference numbers (copy-LF denominators, NN floors, zero/mean floors) are computed
  once from the full untouched datasets and frozen in `round2/state/anchors/` **before any
  experiment runs**.
- Prerequisite: the round-1 registration ((r−1)/2 half-cell) and wrap-seam reference fixes
  must land first and floors be re-certified — they change every copy-LF denominator
  (round 1 measured 2.0–8.6× inflation).

## 4. Data (decided)

- **Panel, guard set, and all dataset files unchanged and byte-identical** to round 1.
  Panel: helmholtz, pfc, allen_cahn, fisher_kpp, cahn_hilliard, ifc_poisson. Guard:
  heat_local, fluid, sharp__sod_1d.
- **No new HF data** — few-HF is the benchmark's premise and comparability with round 1
  and the paper bars must hold.
- **No LF-only pools** (considered, rejected by Eloise): round 2 runs entirely on the
  existing 400 aligned train samples per sharp dataset (5/20/50 ladder on ifc_poisson).
- Grounding facts verified 2026-07-30: in the sharp npz layout, `x` at every fidelity level
  *is* the complete condition vector (2–19 dims; each `meta.json` certifies the field is a
  learnable function of it), and `ifc_poisson`'s `Xs.npy` is a 5-dim condition vector. No
  data work is needed to run condition→HF experiments.

## 5. Contract and enforcement (decided)

- Model contract unchanged: `smoke_eval.py` CLI signature, result-JSON schema, checkpoint
  resume from `last.pt`, cache keys, card format, reviewer/no-SLURM process rules.
- **Stripped test view.** The evaluation harness materializes, per dataset, a test-split
  view containing only condition vectors (`x` arrays / `Xs.npy`); test LF field files are
  physically absent. Train files remain complete. "No LF at test" is therefore enforced
  structurally — a model cannot read what is not there.
- **Round-2 novelty guarantee** (Eloise's requirement that round-2 models differ from
  round-1 models):
  1. Structural: round-1 families take an LF field as forward input; pointed at the
     stripped view they cannot run at all. Every round-2 family must implement a new
     condition→field pathway (a parametric surrogate/decoder — a different architecture
     class from round 1's field-to-field correctors).
  2. Reviewer check: every review answers "is this family a rebadge of any round-1
     family?" — new `INSPIRATION.md`, new forward signature required.
  3. Declared-reuse-only: a round-1 model may appear **only** in one of two explicitly
     declared roles — (a) a frozen test-time sub-component behind a new
     condition→pseudo-LF front end (the r2s2 design, where the reuse *is* the experiment),
     or (b) a training-time-only teacher for distillation (r2s3), never present at test.
- New working directory `mffp_autoresearch/round2/` mirroring `round1/` (program.md, cards,
  state, worktrees, brainstormer/, tools/ seeded from round 1's library).

## 6. Streams (decided — 4, focused)

1. **`r2s1_direct`** — condition→HF architectures built from scratch: FiLM-conditioned FNO
   decoders, DeepONet-style branch–trunk, spectral/implicit decoders. Floor arms (NN,
   zero/mean) mandatory.
2. **`r2s2_stacked`** — Eloise's stacking proposal as B1: train a FiLM-FNO **pseudo-LF
   emulator** (condition → LF field) on LF data, feed the best round-1 corrector (s6 DC
   lineage, panel geomean ≈ 0.19). Arms: frozen corrector / fine-tuned corrector /
   end-to-end, to separate emulator error from distribution shift (the round-1 corrector
   was trained on *real* LF; pseudo-LF is off-distribution for it).
3. **`r2s3_lf_train_signal`** — LF as training-only signal: distillation from LF-consuming
   teachers, LF-pretrain→HF-finetune (round 1's revin_lf two-scaler finding feeds in),
   auxiliary multi-fidelity losses. Uses the existing 400 aligned samples only.
4. **`r2s4_diag`** — diagnostics: value-of-LF accounting (matched architectures with and
   without LF training signal), overfitting anatomy at N_hf = 5, floor certification
   including a standing zero-predictor column, reuse of round 1's unified
   normalization-eligibility rule and drift-class rule.

Scale rationale: the round-2 question is narrower than round 1's open exploration; four
sharper streams at roughly half of round 1's compute.

## 7. Timing (decided)

1. Close round 1: ROUTER (s4-B3) batch → round report → top-3 seed confirms (operator
   decision).
2. Land the denominator-affecting reference fixes (registration, wrap-seam); re-certify
   floors and spreads.
3. Prepare `round2/` scaffolding (program.md, anchors, stripped-view harness) — allowed
   before launch.
4. **Launch only when Eloise says so.** No cron, no websearcher dispatch, no SLURM for
   round 2 before her explicit go.

## 8. Out of scope

- New HF generation; LF-only pool generation (both rejected above).
- Changing the panel, guard set, or paper bars.
- Any modification to round-1 results, cards, or state.
- Guarded surfaces per repo CLAUDE.md (`data/`, `baselines/`, `eval/`, `references/`,
  `scripts/`, `factory.md`, `akash/**`) remain untouched; the stripped test view is built
  by round-2 harness code in `round2/`, not by editing the factory eval layer.
