# Summary so far — stream `s2_beyond_copy`, batch 1

## The question this stream owns

`project.yaml streams[1]`: *"why does every fusion mechanism lose to copy-LF on the
five sharp-2D panel datasets?"* Round-1 success criterion 2 (program.md §1) is at
least one model with **skill < 1** on each of the five beyond-copy panel datasets;
at round start **zero** models achieve this on **any** of them.

## Current numeric state

Copy-LF test nRMSE, read from `mffp_autoresearch/round1/eval/copylf_baselines.json`
(`_nrmse_def_hash d3d0ade9...`, `_split test`, G2 PASS per `state/gates.md`):

| dataset | copy-LF nRMSE | best-zoo nRMSE (provisional prior, program.md §2.3) | skill |
|---|---|---|---|
| `ext__helmholtz_2d` | 0.32945 | 0.478 | 1.45 |
| `sharp__phase_field_crystal_2d` | 0.04478 | 0.349 | 7.8 |
| `sharp__allen_cahn_2d` | 0.01615 | 0.245 | 15.1 |
| `sharp__fisher_kpp_2d` | 0.06263 | 0.247 | 3.9 |
| `sharp__cahn_hilliard` | 0.08766 | 0.180 | 2.1 |

Two structural observations that frame the diagnostic. (1) The skill ordering
tracks how *small* copy-LF error is, not how sharp the PDE is: the datasets where
LF is already excellent (allen_cahn 0.016, phase_field_crystal 0.045) are exactly
where models are worst (15.1x, 7.8x). (2) Best-zoo absolute nRMSE is remarkably
**flat** across the five (0.18-0.48) while copy-LF spans 20x - consistent with
models predicting from the condition vector and largely *ignoring* the LF field,
rather than with a fusion mechanism that degrades gracefully.

## State of the round

- `state/gates.md`: G1 PASS, G2 PASS, **G3 PENDING**, G4 PENDING.
- **`state/anchors/s2_beyond_copy.json` and `state/noise_floor.json` do not exist
  yet** - batch 0 is queued on SLURM (verified: `state/anchors/` is an empty
  directory). Consequence for this batch: no certified per-dataset noise floor is
  available, so the batch-1 card must either (a) be a diagnostic whose
  falsification clause is *structural* (a ratio/localization statement, not a
  small numeric delta), or (b) carry its own within-measurement error bars. Per
  program.md §12.2 batch 1 **is** pre-directed to be a diagnostic card, so (a)
  applies. The anchor is fixed by definition anyway: **skill 1.0 = copy-LF**
  (§12.2), not a batch-0 measurement.
- `experiment_cards/` holds only `SCHEMA.md`; no s2 cards exist.
- No prior websearch for this stream (`websearches/` contains only
  `s5_tuning/batch_1/`). N = 1, so there is no `batch_0/report.md` to inherit.

## What the two in-repo literature reports already establish

`docs/reports/MF_Sharp_HighFreq_Report.md` (2026-07-02) is a prior websearch by
another agent and is cited, not re-derived. It names three *a priori* walls:
§0.1 the **12-mode spectral wall** (Fourier coefficients of a discontinuity decay
as k^-1, so a 12-mode backbone has a rel-L2 floor no training removes; panel grids
are 96^2-128^2); §0.2 **additive-residual misalignment** - when LF mispositions a
feature, `HF - LF` is a dipole *sharper than the field*, making residual learning
strictly harder than direct prediction; §0.3 **MSE/rel-L2 structurally prefer
blur**. Its §0.4 audit adds the sharpest fact for this stream: *the current
winners never consume the LF field at inference* (transfer families are pure
`X -> field`; MF lives only in the pretraining schedule). That single fact would
explain flat best-zoo nRMSE across a 20x copy-LF range - and it is a *diagnosable*
claim.

`docs/reports/MF_Leaderboard_Beaters_2026_Report.md` (2026-07-13) adds: frequency-
blind fusion re-imports LF spectral bias, so **per-frequency-band trust weighting**
is the field's current answer (N7.2); and the residual `delta = u_HF - u_LF` is the
2025-26 standard learning target (IRNO 2605.24041, MFFM 2605.16118).

## Open questions this batch's search must serve

1. **Diagnostic methodology.** What are the published, citable ways to decompose a
   field-prediction error so that "we lose to our own input" is localized? Candidates
   to check: radially-binned per-wavenumber band error E(k) (APEBench), LF/HF
   cross-spectral **coherence** vs k, displacement/amplitude (DAS-style optical-flow)
   decomposition, interface-distance-stratified error maps.
2. **Is "learned fusion underperforms its own low-fidelity input" a *named*,
   documented phenomenon** with a published diagnosis, or is the project the first to
   report it? §13.3 warns the novelty record is 0-for-4.
3. **Identity-preservation guarantees.** Is there published work on architectures that
   *cannot* do worse than copying the LF input (identity init, skip-to-output, gated
   residual, hard low-band constraint)? This is the natural batch-2 mechanism and the
   diagnostic should be designed to discriminate among its variants.
4. **Data-defect branch.** §12.2 warns: if the diagnostic finds LF/HF misalignment
   that looks like a dataset defect, the honest output is a bug report to the mentor.
   Search should surface how the MF literature distinguishes *solver-legitimate*
   LF-HF decorrelation from a pairing/normalization bug.
