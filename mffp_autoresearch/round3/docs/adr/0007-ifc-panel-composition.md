# ADR r3-0007 (RATIFIED): scored-panel status of the two ifc datasets

**Status: RATIFIED 2026-08-10 — operator (Eloise) chose OPTION C** ("c"): `ifc_poisson` demoted to report-only, `ifc_heat` retained as a scored cell with its disclosures.
Raised by the operator 2026-08-10 ("not sure if we should keep those two datasets") after the batch-2 audit evidence; drafted, emailed, and decided the same day.
Execution (same day): scored panel = pfc, allen_cahn_2d, fisher_kpp_2d, cahn_hilliard, ifc_heat; ifc_poisson artifacts remain audited and reported; the option-C mean-removed check on film's ifc_heat win runs as a follow-up with an operator alert if offset-dominated (option B then becomes the live fallback).
The batch-3 registration hold lifts with this ratification.

## Question

Should `ifc_poisson` and `ifc_heat` remain scored cells of the round-3 panel, or be demoted to report-only (the treatment pfc received under ADR r3-0004 while its cell was defective)?

## Evidence on file (all measured; sources cited)

**ifc_poisson — the task is closed-form.**
The condition→HF map is EXACTLY affine: the oracle-affine residual is 5.4e-16 (r3s4-B2 turn 3, degeneracy audit 2026-08-05).
A scored cell there measures "did you fit a 6-parameter linear formula from 5 examples", not field prediction.
r3s2-B2 classifies it CLOSED_FORM_TASK / scalar-gain; its condition design matrix is rank-deficient (5/6, documented min-norm pick).
The certified film baseline scores 1.23 in copy-LF units on it — no learned model has beaten copy-LF on this cell all round.
D3's uncertainty machinery also collapses on it for structural reasons (per-row dispersion CV 0.0012 because discretisation error is condition-independent on an affine task).

**ifc_heat — degenerate in structure, but the round's one genuine learned win.**
Level-dominated: rel-L2 on its near-uniform fields is dominated by the constant offset (`[[rel-l2-is-level-dominated]]`; the fisher_kpp analogue showed a 35× gap between raw and mean-removed).
Only 5 HF train rows, so every fitted statistic is fold-fragile — the affine floor moves from 0.96 (beats the paper bar) to a leave-one-out mean of 1.85 (does not), fold sd ~10.9 tau (r3s4-B2 turn 2A).
BUT: the certified film-transfer baseline scores **0.49** in copy-LF units on ifc_heat — the only cell in the round where a learned model beats copy-LF, the paper bar, and the affine floor **even at the floor's fold-worst**.
Open check before that win is fully trusted: the mean-removed skill (is the win field structure, or offset calibration?). Cheap to compute; queued as an execution step of this ADR.

**Both cells:** floor-disqualified for every field arm r3s2 produced; the mandatory affine-floor disclosure is the least stable quantity in the audit (fold-catastrophic, see above); the F1 tolerance work had to declare the affine arm non-adjudicable.

**Robustness of decisions already made:** the ADR r3-0006 denominator choice does NOT depend on this ADR — film remains the best certified baseline on either panel (U-Net panel ratio 1.0285 on 6 datasets, 1.0092 on sharp-4; film best in both).

**Independent corroboration (added 2026-08-10, r3s3-B3 brainstorm):** designing the batch-3 knee card, the brainstormer pre-declared both ifc cells NON-ADJUDICABLE on pure arithmetic — clearing their certified film-unit noise floors (tau_rel 0.3359 / 0.5627) would require effect ratios of 0.4–0.8 against physical effects of order 0.025–0.03 nRMSE.
Independent of this ADR's structural arguments, the ifc cells cannot host a registerable claim for that card class at current noise levels.

## Panel arithmetic under each option (computed from certified anchors, no new jobs)

| quantity (copy-LF units) | 6-ds panel (today) | sharp-4 panel | 5-ds (drop poisson only) |
|---|---|---|---|
| best training-free floor geomean | 38.84 | 132.27 | computed at execution |
| film-transfer geomean | 18.69 | 91.82 | computed at execution |
| U-Net / film panel ratio | 1.0285 | 1.0092 | computed at execution |

(The large sharp-4 numbers are a units effect — the ifc cells have small skills that pull the geomean down — not a difficulty change.)

## Options

- **Option A — keep both scored** (status quo + the disclosures already installed: affine fold-range, level-domination caveat, non-adjudicable affine arm).
  Cheapest; keeps panel diversity (the only non-periodic, non-sharp solver cells).
  Cost: two of six scored cells cannot cleanly adjudicate model claims, and every panel statement carries their caveats forever.
- **Option B — demote both to report-only.**
  Clean panel (4 sharp cells, all with working floors and honest denominators); ifc numbers stay visible in every report.
  Cost: throws away the round's only strong learned win (film on ifc_heat) as a scored result, and narrows the benchmark's claim scope to periodic pseudo-spectral tasks.
- **Option C — demote `ifc_poisson` only; keep `ifc_heat` scored with its disclosures. (recommended)**
  Removes the cell that is closed-form by measurement (nothing to learn beyond linearity, and nothing has ever beaten copy-LF there) while keeping the cell where a learned model demonstrably wins.
  Execution includes the mean-removed check on film's ifc_heat win; if that check shows the win is offset-only, the operator is alerted and B becomes the live option.

Round-4 note under any option: regenerate the ifc pair with ≥40 HF train rows and a non-degenerate condition design, then readmit; the defect is the instance, not the physics.

## Interaction with the open affine-floor question

If B is chosen, the affine-floor rule question is MOOT for scored claims (no scored ifc cells).
If A or C, the recommendation on file stands: keep the rule, disclose the fold range (option A of that question); the floor-definition change (fold-averaged) is not needed once poisson — the worse offender — is report-only.

## Execution plan (on decision; ~half a day, no GPU)

1. Amend panel composition in `tools/make_round3_anchors.py` (explicit list, per the SHARP4 lesson) + rebuild anchors through the stale gate; G3 re-certify.
2. Recompute `film_denominator.json` / `unet_baseline.json` panel aggregates on the new composition (per-dataset cells unchanged).
3. Preflight re-scope; gates.md + program.md §2 updated; figures re-rendered; professor-update artifact redeployed.
4. Release the batch-3 registration hold; brainstormers register clauses on the decided panel in film units.
5. Option C only: mean-removed skill check on film's ifc_heat cells; alert operator if offset-dominated.
