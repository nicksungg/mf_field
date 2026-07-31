# Summary so far — `r2s1_direct`, batch 2

## Where the stream stands after B1

`experiment_cards/r2s1_direct/batch_1/B1.json` (status `complete`, family
`r2s1_cond_decoder`, 200 epochs, seed 0, `provisional-single-seed`) shipped a
from-scratch condition→HF decoder (RFF→MLP→16×16 latent, 4 FiLM-modulated
spectral blocks, unit-direction × predicted-amplitude factorization,
out-of-fold blend onto {zero, train_mean, nn_condition}). Result (part 5):
panel geomean skill **19.6444** vs the frozen launch anchor **23.0636**
(`state/anchors/r2s1_direct.json`, best-floor geomean, deterministic, no CI) —
-14.8%. It beat the best training-free floor on all 6 panel datasets
(helmholtz 3.1043 vs 3.3441 zero; pfc 52.03 vs 59.81; allen_cahn 244.43 vs
269.20; fisher_kpp 11.584 vs 11.993; cahn_hilliard 12.843 vs 23.180;
ifc_poisson 9.785 vs 10.055).

**But the falsification leg fired**: the card demanded <= 19.60 and scored
19.6444, and part 7 records that a **~150-parameter closed-form head under the
identical protocol scores 19.0553** — both inside the certified
`min_claimable_effect` band of 1.1419 (`state/noise_floor.json`, now CERTIFIED
by r2s4-B1, family `r2s4_cert_min`, 3 seeds). So the geomean pass/fail was
decided by noise, and **capacity bought almost nothing**.

## The B1 mechanism findings that frame batch 2

From `7_gap_and_future` / `cross_stream_notes` of the B1 card:

1. **Identifiability, not capacity, is the binding constraint.** Condition-
   identifiable POD rank (out-of-fold R^2 > 0.1) is helmholtz 5, pfc 2,
   allen_cahn 1, fisher_kpp 1, cahn_hilliard 3, ifc_poisson 1. r2s2-B1 found
   the same ladder on the *LF* fields; r2s4-B1's aleatoric barrier agrees.
2. **Out-of-fold per-band gain calibration (shrinkage) is where the gains
   came from.** Under the per-sample relative-L2 score, calibration drives all
   non-DC band gains to zero on every sharp dataset and applies ~4x uniform
   shrink on helmholtz. r2s4-B1's shrinkage oracle returned lambda*=0 on helmholtz.
3. **A ~35-parameter DC-only ridge (per-sample constant field) beat the 14.4 M
   decoder on pfc** (0.35020 vs 0.38403) and sits at the DC oracle to 6e-6 on
   the patterned class.
4. **Model form should be chosen by training-free statistics**: the centering
   ratio ||mean field|| / geomean||y|| says unit-direction x amplitude is worth
   3.82x on helmholtz and costs 1.8x on allen_cahn.
5. **The one unexplained capacity benefit is `sharp__cahn_hilliard`** (decoder
   0.53686 vs band-calibrated tiny head 0.55990 = 0.5511 skill, 6.0x that
   dataset's min_claimable_effect 0.09125). Three candidate explanations:
   genuine representation value / arm-set artifact / rank starvation (r<=3).
6. **pfc is two datasets** (44/100 test samples patterned, class predictable
   at out-of-fold AUC 0.9998) — per-class scoring required before any pfc claim.

Promoted tools available: `tools/condition_identifiable_rank.py`,
`tools/band_gain_counterfactual.py` (plus `tools/gain_calibration_ceiling.py`,
`tools/amplitude_shrinkage_audit.py`, `tools/dc_pattern_split.py`).

## Constraints carried in

ADR r2-0003: on pfc / fisher_kpp / allen_cahn the condition vector is
incomplete (random IC lives only in the fields) -> deterministic condition→HF is
a conditional-mean estimator; skill→1 unreachable. program.md §5.11: no new HF
data. §2.1/§5: one nRMSE definition, eval layer byte-frozen (distributional
metrics can only be secondary). §5.10: novelty guarantee / rebadge check;
§13.3: 0-for-4 novelty record, recall is not citation.

## Batch-1 prior-art verdict to build on

`websearches/r2s1_direct/batch_1/report.md`: D1 FiLM/modulation-conditioned
spectral decoder = **preempted** (ModAFNO etc.); D2 condition→fixed-basis
coefficients (POD-NN/PCA-Net/RB-DeepONet) = **preempted**; D3 identifiability
certification where the omitted driver is a stored coarse solve =
**preempted-but-MF-composition-open** (arXiv:2605.28076 conditional-mean
barrier; REALM arXiv:2512.18595 shows floor arms are not standard practice).
Lanthaler arXiv:2210.01074 (via `docs/reports/MF_Sharp_HighFreq_Report.md:180`)
bounds any linear-reconstruction arm on discontinuous operators.
`docs/reports/MF_Leaderboard_Beaters_2026_Report.md:32,102` carries FreqNO-DPS
(arXiv:2606.03936): frequency-calibrated weighting, not fusion, removes
spectral bias — the nearest published relative of finding (2).
r2s4_diag batch-2's D3 row (`websearches/r2s4_diag/batch_2/report.md`) already
found that published post-hoc surrogate calibrators rescale *variance/interval
width*, not the point prediction — this batch must test whether that still
holds at *spectral-band* resolution.

## Open questions batch 2 must search against

- Is **out-of-fold per-spectral-band gain calibration** of a field surrogate's
  point prediction published?
- Is **training-free, statistic-driven selection of the output
  parameterization** (centering form x rank) published for parametric PDE
  surrogates?
- Is "**beat a ~10^2-parameter closed-form head before claiming capacity**"
  established practice / a published benchmark protocol?
- Is **regime/class-conditional prediction and scoring** on a mixed-regime
  parametric PDE dataset published?
