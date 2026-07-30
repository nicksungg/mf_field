# BENCHMARK NOTE FOR THE MENTOR — copy-LF reference misregistration (round 1)

**Status: confirmed in closed form** (s3_warp-B1 mechanism analysis,
2026-07-30; tool: tools/registration_audit.py; full evidence in
experiment_cards/s3_warp/batch_1/B1.json parts 5-6 and
worktrees/s3_warp/B1/scratchpad/reanalysis_turn_*.md).

## The defect

`eval/panel_data.py::copylf_prediction` (and the generator-side
`mffp_sharp/common/ladder.py::upsample_to_hf`) use scipy zoom's
**cell-centred** convention (`grid_mode=True`) on fields that are **node
samples** (LF node j coincides physically with HF node 2j on the dyadic
ladders). Result: the copy-LF reference is misregistered by a fixed
**(r-1)/2 HF cells** — half a cell at ratio 2 — on the entire sharp panel.
On helmholtz (non-nested 24/96 Dirichlet interior-node grids) the same
defect appears as a zero-mean ±1.5-cell stretch instead.

Evidence (no optimiser anywhere): (1) exact coordinate map on a synthetic
index ramp — deviation 0.0; (2) the data's own answer — nRMSE(LF vs
HF[::2,::2]) is 5-100,000x smaller than vs cell means; the generators' own
spectral_interp satisfies up[::2,::2]==coarse to 8.9e-16; (3) closed-form
Lucas-Kanade on real test data: median shift (+0.50,+0.50) on all sharp
sets; (4) helmholtz's recorded displacement contains the predicted ramp.

## Consequences

1. **The round's skill denominator is inflated 2.0-8.6x on the sharp
   panel.** A ZERO-PARAMETER fixed shift reaches skill 0.12 (allen_cahn) to
   0.50 (cahn_hilliard). Node-aligned band-limited upsampling reaches
   **7.1e-06 on phase_field_crystal_2d — that dataset has NO fidelity gap
   at all** under a correct reference (its solver uses a
   resolution-independent continuous symbol). No sharp HF field carries
   energy above the LF band.
2. **Model results need reinterpretation, not retraction**: every FAILURE
   claim survives (and worsens — the models failed to beat an artificially
   weak reference). s6-B1's celebrated corrector (skill 0.2346) is 87-98%
   explained as learning the analytic half-cell phase ramp; its genuine
   contribution is the remainder (largest on cahn_hilliard, which stays
   LSI-refractory at 0.44). All cross-arm CONTRASTS within cards remain
   valid (shared reference cancels).
3. **Companion defects** (same call): the mode="nearest" wrap seam on
   periodic domains (s6-B2's finding, 0.1-0.7% — two orders smaller); and,
   separately recorded earlier, helmholtz's HF test fields are two-FFT
   reproducible from the condition vector (s3_testtime-B1).

## Recommended fixes (BETWEEN rounds — the round-1 metric stays frozen for
internal consistency; §2.1-2.2 immutable)

- One patch fixing both `upsample_to_hf` and `copylf_prediction` to the
  node-aligned convention (band-limited for spectral solvers), shipped with
  the wrap-seam fix.
- Re-baseline copy-LF and the noise floors under the corrected reference
  before round 2.
- phase_field_crystal_2d needs a redesign (coarser LF or a
  resolution-DEPENDENT symbol) — under a correct reference it is trivial.
- Consider whether the paper-bar comparisons for the sharp datasets in any
  external reporting should quote both references.

Round-1 practice from here: cards may carry a registration-corrected
reference ALONGSIDE the frozen skill (as s3_warp-B2 will), never replacing it.
