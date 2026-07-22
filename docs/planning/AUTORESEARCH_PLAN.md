# Autoresearch Plan — Summary

**Status:** proposal, for a go/no-go decision. Not a spec.
**Date:** 2026-07-22
**Goal:** find a model family that beats the current leaderboard incumbent, using an autonomous research loop rather than hand-designed candidates.

---

## 1. What "beat FNO" actually means here

The target needs restating before anything else, because "beat FNO" is ambiguous in this repo.

The incumbent is not plain FNO.
It is `mf_fno_transfer_film` — Elo 1820, median relative-L2 0.0154, 4.77M params — an FNO backbone with transfer pretraining and FiLM conditioning.

22 of the 30 benchmarked families are FNO-backboned, and the entire top 10 is FNO+transfer or FNO+FIRE variants of each other.
So the loop is not searching for "something other than FNO."
It is searching for *what to attach to an FNO*.

The top 2 also disagree by metric: `mf_fno_pinn_transfer` is #2 by Elo (1799) but has the best median relL2 in the zoo (0.0122).
Any autonomous loop needs one objective, decided up front, or it will oscillate between these two.

---

## 2. Objective

Rank by **Elo plus median relative-L2, both with confidence intervals**, weighted toward high-frequency datasets.

Two properties matter:

- **CIs are mandatory, not decoration.** A proposal is accepted only if it beats the incumbent by more than run-to-run noise. Without this the loop cannot distinguish a real win from a lucky seed, so it will accept noise indefinitely and never converge.
- **Sharpness weighting.** Per-dataset weight derived from the fraction of HF-residual spectral energy sitting above the FNO's retained modes. High-frequency PDEs are where the incumbent is weakest and where a hybrid backbone could plausibly help; uniform weighting over all datasets dilutes exactly the signal we care about.

This replaces the `composite_nRMSE` target currently declared in `factory.md`, which is a geomean over *best-model-per-dataset* and therefore rewards a family that wins one dataset and blows up elsewhere.

---

## 3. Search space

The loop may propose along three axes:

| Axis | Examples |
|---|---|
| **FNO hybrids** | FNO↔WNO dual-basis, FNO↔CNN parallel or residual branch |
| **Training protocol** | `modes_cap`, loss function, schedule, normalization, cross-fitting |
| **Conditioning representation** | DINO features, LF summary statistics, multi-resolution stacks, geometry encodings |

FNO stays as a component in every proposal.
Full backbone replacement is out of scope.

Pure fusion-mechanism variants are also out of scope — that is the space the existing 30 families already occupy, and it looks mined out.

---

## 4. Four phases

**Phase 0 — fix the harness.**
The audit found three defects that would corrupt any autonomous loop: no variance estimate (F05), 11 families training on a loss that is not the scored metric (F19), and the backbone not actually held constant despite the protocol claiming it is (F23), plus three coexisting definitions of nRMSE (F01).
A loop launched on top of these hill-climbs artifacts.
This phase is a prerequisite, not a contribution.

**Phase 1 — spectral diagnostic. No training.**
Compute each dataset's HF-residual energy spectrum and locate it relative to `modes_cap` (currently 12 everywhere except `fno_coregionalization`) and the working-grid Nyquist (`WORK_CAP = 256`).

This single computation returns two things:

- the per-dataset sharpness weights that Phase 2's objective needs;
- a direct answer to whether spectral truncation is the bottleneck at all.

If the sharp datasets' energy sits *above* the working-grid Nyquist, no hybrid backbone can recover it, and Phase 2's whole premise collapses — worth knowing for near-zero GPU cost.
Note F04 separately: `era5` and `pm_test` are currently scored against a *downsampled* target, so for those two the ceiling is a scoring artifact rather than a modeling limit.

**Phase 2 — the loop, scoped by Phase 1.**
Batched fan-out: propose N families in parallel → **prior-art check each** → implement survivors → smoke-eval → adversarially verify apparent wins.
Smoke config stays as-is (`ifc_heat` + `ifc_poisson`) since the budget is modest.

**Phase 3 — promote.**
Smoke survivors go to the full benchmark via the SLURM array.

---

## 5. The prior-art gate

Every proposal gets a literature check *before* implementation, not after.

This is the single highest-value component and it comes from direct experience: all three NEW_MODELS.md candidates were pre-empted by published work discovered only after write-up.

- Candidate A (diffusion refiner) — Bhola 2512.12749 / MFFM / CorrDiff.
- Candidate B (FNO↔WNO blend) — WLNO, near-exact.
- Candidate C (cycle-consistency fusion) — Kim 2021, near-exact.

The FNO→CNN hybrid was likewise pre-empted by Park 2507.06133 and SINO.

An autonomous loop with no novelty check will regenerate these on repeat and spend the entire budget doing it.
Note that this cuts against part of the approved search space: FNO↔WNO and FNO↔CNN hybrids are *already known* to be prior art as architectures.
Their surviving novelty is the multi-fidelity composition, so the loop must be told to propose MF *compositions* of these hybrids, not the hybrids themselves.

---

## 6. Engine

Recommendation: reuse the existing `factory ceo . --mode research` loop for persistence and cycle bookkeeping, but generate Phase 2 proposals as structured batch fan-outs rather than one-at-a-time CEO improvisation.

The factory loop already has the cycle scaffolding, SLURM integration, guards, and result caching.
Rebuilding that is wasted effort.
What it lacks is a good proposal step and a novelty gate, which is what the fan-out adds.

---

## 7. Is this a good idea?

**Phases 0 and 1: yes, unconditionally.**
They are worth doing whether or not the autonomous loop ever runs.
Phase 0 is fixing known defects in a benchmark whose results are currently being reported.
Phase 1 is a cheap, training-free measurement that answers the project's central open question and may well pre-empt months of modeling work.

**Phase 2: conditional.** Three honest risks:

1. **The space may be saturated.** 30 families, and the top 10 are variants of one idea. If the remaining headroom is small, an autonomous loop on a modest budget will spend it rediscovering rank-8-to-rank-12 territory.
2. **Novelty is the binding constraint, not accuracy.** Recent history is 4 for 4 on candidates that were architecturally sound and already published. Automation makes generation faster; it does not make novelty checking better. The gate in §5 is a partial mitigation, not a solution.
3. **Modest budget versus CI-gated acceptance are in tension.** Requiring a win to exceed its confidence interval means multi-seed runs, which multiplies cost per proposal. The loop will evaluate fewer candidates than an ungated one — that is correct, but it should be a conscious trade, not a surprise.

**Suggested decision:** commit to Phases 0 and 1 now.
Re-evaluate Phase 2 once Phase 1 reports, since its result determines whether hybrid backbones are worth searching over at all.

---

## 8. Known unknowns

- Dataset count is inconsistent in the repo itself (`model/README.md` says 15, `CLAUDE.md` says 17) — resolve before defining the objective (U02).
- Only 21 of 30 families are present in this checkout (U03), so the leaderboard cannot be fully reproduced locally.
- `model/README.md` leaderboard numbers are taken as given and have not been re-derived (U06).
