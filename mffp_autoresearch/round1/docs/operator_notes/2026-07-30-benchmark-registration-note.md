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

## Addendum (2026-07-30, s7_loss-B1 mechanism analysis): the zero predictor beats the champion on helmholtz

A second panel-fragility datum, independent of the registration defect.
`tools/field_error_decomposition.py` + `tools/collapse_set_attribution.py`
on s7-B1's artifacts show the all-zeros field has helmholtz skill 3.035 vs
the seed-0 champion's 18.826 (6.20x better), and substituting zero for the
champion's helmholtz prediction alone moves its seed-0 panel geomean 7.1022
→ 5.2397 (a bigger improvement than any objective-level change tested this
round). The champion overshoots amplitude 3.1x; s7-B1's relative-loss arm
undershoots 21x and "wins" the same way the zero field does. Implication
for benchmark design: a dataset where the zero predictor dominates all
trained models contributes only amplitude-calibration noise to a geomean
leaderboard; helmholtz should stay report-only (ADR 0002 handling) or gain
a zero-predictor floor column in the next revision. This is the 5th
independent amplitude/normalization data point this round.

## Addendum 2 (2026-07-30, s2_beyond_copy-B2 mechanism analysis): the registration defect eats a full model win

s2-B2's LF-residual model scored 5-dataset beyond-copy geomean skill
0.380264 — and the mechanism analysis shows it is registration repair, not
physics: learned-correction ∩ registration-field fractions 0.975-0.9987 on
allen_cahn/cahn_hilliard, ~100% on pfc; Spearman(registration share, model
share) = 0.90 across datasets. Against a node-aligned denominator the same
model's geomean flips to 10.31, while the FREE zero-parameter fix achieves
0.0369. The card's falsification clause could not have fired: on 4/5
datasets it compared two predictors of the same artifact. Two additional
scaler defects surfaced by the same analysis (tools/
target_scale_spread_audit.py): (a) helmholtz — one of 400 train samples
carries 89.2% of MSE energy under the family's global target scaler
(effective N = 1.2); a single train-fitted scalar turns skill 4.14 into
0.995; (b) pfc — the global scaler is 7.9e4x the median per-sample max, so
targets are numerically zero and the model emits a noise floor 8206x the
truth. Consequence for round-1 reads: EVERY sharp-panel win must now be
decomposed with tools/registration_skill_split.py before interpretation,
and batch-3 cards must pre-register falsification against corrected
references (the C/D/E variants), not copylf_baselines.json.

## Addendum 2 (2026-07-30, s2_beyond_copy-B2 mechanism analysis): trained wins on the sharp panel are re-learned registration

Direct field-projection evidence (tools/registration_skill_split.py, 16
samples/dataset, CPU replay of the scored checkpoints): the LF-residual
model's learned correction is cos 0.987-0.999 with the analytic
registration ramp at amplitude 0.996-1.004 on allen_cahn/cahn_hilliard.
Per-dataset registration share of the "win": pfc ~100% (no fidelity gap
exists), allen_cahn 97.5%, cahn_hilliard 99.9%, fisher_kpp 95.9%. Scored
against the node-aligned reference the run's geomean flips 0.380 → 10.31,
and the zero-parameter free fix alone scores 0.0369 — 10.3x better than
the trained model. The round's amplitude/normalization theme now has a
proximate cause: the family normalizes targets by one global max|HF−LF|;
on helmholtz ONE of 400 training samples carries 89.2% of the MSE energy
(effective N = 1.2), and a single train-fitted scalar α=0.0224 turns the
4.14 failure into 0.995. Between-rounds fix list gains: per-sample target
normalization alongside the reference re-registration. Round-1 metric
stays frozen; contrasts remain valid; win claims on the sharp panel must
be read as registration-dominated.
