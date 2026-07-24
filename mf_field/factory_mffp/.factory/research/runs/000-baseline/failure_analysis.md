# Baseline Failure Analysis — cycle 000-baseline

**Cycle:** 000-baseline
**Source:** v9_baseline (kept in `references/v9_baseline/`, used as reference implementation only).
**Run status:** PASS — `composite_nRMSE = 1.6595` (geomean of per-dataset test nRMSE on `ifc_heat`, `ifc_poisson`), 2 datasets scored.
**Mode of analysis:** Manual / aggregate. The Failure-Analyst agent was deliberately not spawned this cycle:
- (a) the baseline is a clean PASS with no per-instance failure rows to classify;
- (b) the aggregate composite has no "instance" axis — only per-dataset/per-split nRMSE;
- (c) prior failure_analyst invocations on this same baseline timed out at the default 300 s (events 06:21–06:26Z, 07:39Z) — wrapper cold-start cost (the launcher pre-warmup fix is in working tree but uncommitted).

This stub is the CEO's manual aggregate-level analysis, which is the right level for an aggregate metric anyway.

## Per-dataset breakdown (from `results/smoke_latest.json`)

| dataset      | model        | test nRMSE | best_val nRMSE | train_s | params  | paper geomean | beats_paper |
| ------------ | ------------ | ----------:| --------------:| -------:| -------:| -------------:| -----------:|
| ifc_heat     | v9_baseline  |   0.14883  |       0.05245  |   65.5  | 409 255 | _null_ (todo) | false       |
| ifc_poisson  | v9_baseline  |  18.50344  |       1.36508  |    5.0  | 409 767 | _null_ (todo) | false       |

Composite (geomean) = √(0.14883 · 18.50344) = **1.6595**.

## Dominant failure modes

### F1 — **`ifc_poisson` test generalization collapse** (~95 % of composite penalty)
- Test nRMSE (18.5) is ~13.6× the best validation nRMSE (1.37). Validation itself is already ~10× higher than what the paper-quality baseline reaches on the related `poisson_local` dataset (~0.007–0.054 for IFC / MFRNP at L2–L5). The test number is therefore not just a bad model — it's a generalization or distribution-shift catastrophe layered on top of an under-fit model.
- Suspected causes (CEO best guesses; literature pass should confirm):
  1. **Distribution shift between val and test splits.** Test set may be OOD (e.g., different forcing parameters, different fidelity level, larger geometry) and v9's transolver+gated-soft-prior is not transferring.
  2. **Loss / normalization mismatch.** A model trained with one normalization on inputs/outputs and evaluated under a different effective normalization can produce arbitrarily large nRMSE on test.
  3. **Under-training on the smoke schedule.** Smoke config trains very briefly (5 s on ifc_poisson — extremely short). v9 may be far from converged for `ifc_poisson` even on its own val split.
  4. **The model architecture (Transolver-style pointwise gated fusion with soft prior) may simply not be well-matched to ifc_poisson's PDE structure**, especially for OOD generalization. Coregionalization-style models (IFC), residual stacking (MFRNP), and PINN-augmented losses all reach 1–2 orders of magnitude lower nRMSE on the related `poisson_local` dataset in the literature.

### F2 — **`ifc_heat` is in-range but ~30× worse than the paper SOTA on the related `heat_local`** (~5 % of composite penalty by magnitude, but still a large gap)
- Test nRMSE 0.149 vs paper-baseline geomean on `heat_local` ≈ 0.004–0.012 (li2022ifc / niu2024mfrnp).
- This dataset is far better-behaved than `ifc_poisson` (val 0.052 → test 0.149, only ~3× gap), but the absolute number still loses to the paper bar by ~one order of magnitude.

### F3 — **No `paper` numbers in `baselines/paper_baselines.json` for `ifc_heat` or `ifc_poisson`** (meta-failure)
- Their `splits` dict is empty, so `vs_paper.beats_paper` is forced to `false` regardless of how good the model is. We need the Researcher to fetch the per-fidelity / per-split paper numbers from li2022ifc (NeurIPS 2022, arXiv:2207.00678) and propose appending them to `baselines/paper_baselines.json`.
- Status note: `baselines/` is a **fixed surface**. The Researcher can only *suggest* numbers; a human owner has to commit them. This is fine — flag it in the Researcher's output.

## Failure distribution (by share of composite penalty)

- F1 — `ifc_poisson` test collapse: ≈ 95 % of the composite (the entry 18.5 dominates the geomean).
- F2 — `ifc_heat` gap to SOTA: ≈ 5 % of composite penalty in absolute terms, but the *modeling lessons* (better backbone, better MF fusion) carry over directly to F1 too.
- F3 — Missing paper numbers in `baselines/`: not a numeric failure, but a meta-blocker for `n_datasets_beating_paper` to ever go above 0.

## Suggested intervention surfaces (all within `models/**` — the only mutable surface)

The fix must be a **new model family** under `models/<name>/` per `factory.md` Guards. Concretely, the Strategist should pick from `.factory/strategy/backlog.md`'s `<backbone> × <MF concept>` matrix. Most promising for F1 specifically:

1. **`fno_coregionalization`** — FNO backbone (much better for PDE solution operators like Poisson than transolver's pointwise attention) + IFC-style latent coregionalization across fidelities (li2022ifc, the *source* paper for `ifc_poisson`). Best matched to the dataset and to closing F1.
2. **`fno_mf_stack`** — FNO + MFRNP-style residual stacking (niu2024mfrnp). Also a known SOTA on `poisson_local` (~0.007–0.018).
3. **`transolver_residual`** — Keep transolver but switch from gated-soft-prior to a *hard* residual (predict HF − LF). Cheaper smoke pass; lets us isolate "is the MF-fusion the bug, or the backbone?".
4. **`siren_film_fidelity`** — fidelity-conditioned SIREN with FiLM. Very different inductive bias from v9; useful diversity even if it loses.

The Strategist should prefer (1) **fno_coregionalization** first — it is the literature-matched method for this exact dataset family. (2) and (3) are cheaper exploration; (4) is pure diversity.

## What the Researcher needs to confirm

- **Paper numbers** for `ifc_heat` / `ifc_poisson` from li2022ifc (per-fidelity tables) — propose appended rows for `baselines/paper_baselines.json` (CEO/user will commit).
- **What the IFC test split actually is** — read the source paper's protocol so the strategist knows if the gap is OOD-shift or just under-training. (Probably documented in li2022ifc §experiments.)
- **FNO / IFC reference code** for shape / loss conventions (so the Builder can implement `fno_coregionalization` from scratch without copying `references/v9_baseline/`).
- **State of papers_summary.csv** — file appears not present at repo root despite `factory.md` referring to it. Researcher should locate or create it under wherever it actually lives, and add a FIRE row + 2024–2026 MF field-prediction rows.

## Status
PROCEED to R1.5 (Researcher).
