---
name: cycle-006-summary
description: Cycle-006 close-out — H1 (only hypothesis) verdict REVERT. MFRNP Poisson recipe + K=20 did NOT transfer cross-architecture to fno_coreg_residual. Heat -13% as architectural side effect; Poisson +3.6%. Project best unchanged (cycle-005 H2 @ 0.029357). NEW pattern — cross-architecture recipe portability not guaranteed.
metadata:
  type: project
tags:
  - factory
  - factory_mffp
  - cycle-006
  - close-out
  - revert
project: factory_mffp
cycle: cycle-006
date: 2026-06-02
source: factory-archivist
verdict: revert
---

# Cycle-006 close-out — REVERT

## Headline
composite_nRMSE **0.029357 → 0.04196** (apparent regression). Estimated true composite if `fno_coregionalization` were runnable: **~0.02988** (essentially flat). Project best unchanged at 0.029357 (cycle-005 H2).

## H1 (only hypothesis)
Port MFRNP (HF=2.0, LF=0.25) Poisson reweighting + K=10→20 onto `fno_coreg_residual`.

- **Heat:** 0.03519 → 0.03059 (**−13.1%** — incidental positive from K=20 / b_hidden=128 architectural bump, NOT the loss recipe)
- **Poisson:** 0.05556 → 0.05756 (**+3.6%** — recipe did NOT transfer cleanly cross-architecture)
- **Branch preserved:** `experiment/8-fno_coreg_residual-mfrnp-poisson-recipe` @ `59b741f`

## NEW cross-cycle pattern
**Cross-architecture recipe portability is NOT guaranteed**, even when the receiving architecture has a related structure. The cycle-003 prediction ("shares structural family → recipe should transfer") was wrong. Cite-grounded reasoning produced false confidence: a citation that a recipe works on one architecture is not evidence it works on another, even within the same family. Recipes are coupled to *both* PDE-class *and* architecture.

## Operator action required
`experiment/7` committed tree is **broken** — `fno_coregionalization` constructor signature mismatch. The dirty `model.py` that was load-bearing for the cycle-005 H2 baseline (composite 0.029357) was **wiped** by `git reset --hard` during clean isolation. Without reconstruction, the cycle-005 baseline cannot be reproduced from committed tree, and every future cycle's composite measurement is suspect.

## Separable finding (future cycle)
**K=20 + b_hidden=128 architectural bump alone** (decoupled from the loss recipe) gave the −13% Heat win on `fno_coreg_residual`. Worth isolating as a standalone cycle-007 hypothesis — bank the architectural lever, drop the loss-reweighting bundle.

## Builder redirect lesson
`git add <named-file>` is **insufficient** when the working tree is pre-dirty. Named-file staging silently leaves co-modified load-bearing files unstaged (or, conversely, `git reset --hard` to clean the tree wipes uncommitted dependencies). Builders must either (i) pre-clean working tree at session start, or (ii) use `git checkout HEAD -- <file>` before staging, and always verify `git status` after staging covers the dependency closure of the change.

## Links
- Experiment note: [[cycle-006-exp-8]]
- Patterns updated: [[patterns]] §"Cross-architecture recipe portability is NOT guaranteed"
- Project dashboard: [[factory_mffp]]
