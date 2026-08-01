# Summary so far — `r2s1_direct`, entering batch 3

## Where the stream stands (state files)

Anchor (`state/anchors/r2s1_direct.json`): best-floor panel geomean **23.0636**
(per-dataset best floors: helmholtz 3.3441 zero, pfc 59.8118 mean, allen_cahn
269.1959 NN, fisher_kpp 11.9931 mean, cahn_hilliard 23.1803 NN, ifc_poisson
10.0549 NN). Certified per-dataset `min_claimable_effect` (mce) from
`state/noise_floor.json` (r2s4-B1, family `r2s4_cert_min`, 3 seeds): helmholtz
2.9530, pfc 0.2130, allen_cahn 0.8797, fisher_kpp 0.00071, cahn_hilliard
0.09125, ifc_poisson 0.9377; panel geomean mce 1.1419. **Any claim inside these
bands is noise, not signal.**

## The two completed cards

`experiment_cards/r2s1_direct/batch_1/B1.json` (status `complete`) —
`r2s1_cond_decoder`, ~1.4e7-parameter FiLM condition->field decoder plus an
identifiability certificate. Panel geomean 19.6444; beat the frozen floors on
all six cells, but the pass/fail was decided *inside* the 1.1419 panel mce.
Part 7 `next_direction`: "Stop buying decoder capacity in this stream; spend B2
on IDENTIFICATION and CALIBRATION." Load-bearing measurements: only 1-5 POD
modes per dataset have out-of-fold R^2 > 0.1 from the condition; a
~156-parameter closed-form head matched the 1.6e7-parameter arm to 0.52x mce;
out-of-fold band calibration drove every non-DC gain to zero on every sharp
dataset; a per-sample constant field (~35 params) beat the 1.4e7 decoder on pfc.

`experiment_cards/r2s1_direct/batch_2/B2.json` (status `complete`) —
`r2s1_selected_form`: training-free selected output parameterization + Wiener
band gains + floor blend. The card's hypothesis is not what the run falsified;
**the instrument was**. Part 7 names three defects: (i) the post-hoc floor-blend
payoff is a closed-form monotone function of rho (arm-error <-> base-error
correlation), so a closed-form head that *is* the `dc_only` base (rho = 1.0000
on allen_cahn, RMS residual 1.01e-6) cannot be paid while a decoder at rho
0.69-0.78 collects 8.13 skill -- a comparison decided at that stage is a
decorrelation verdict, not an accuracy verdict; (ii) the selection rule used the
*cardinality* of the identifiable set and then fit the leading energy window --
worth 5.62x mce on cahn_hilliard, because the condition-predictable direction is
0.45% of basis energy and lands at modes 12-13; (iii) the Wiener band stage was
a 40-sample calibration-fold overfit that COST 0.098 skill (least-squares-optimal
band-3 gain is a SHRINK to 0.64, not the [0,2]-edge value the grid picked).
One positive transfer: on allen_cahn a **per-mode out-of-fold-selected quadratic
map** (10 fitted parameters) beat a 1.59e7-parameter FiLM decoder by 23.64x mce
at 99.2% of its mode set's oracle ceiling, with the blend standing down
(lambda = 1.00).

## Open questions carried into batch 3

1. Is `sharp__cahn_hilliard`'s residual +0.7803 skill (8.55x mce) a real
   capacity benefit (H2: decoder spatial inductive bias reaching modes 2-3,
   20.6% of basis energy at OOF R^2 <= 0.035)? **Currently untestable** -- B2
   shipped no checkpoints and no `preds_test.npz`.
2. Is per-mode OOF map selection over a bank the right closed-form rung, and
   must arms be scored BEFORE any shared post-hoc stage?
3. Are pfc / fisher_kpp **dead cells** in this view (0 of 30 leading POD
   coefficients identifiable out of fold after DC removal; oracle blend
   lambda = 0.00 on both)? B2 part 7 item 5 says score 3 datasets, not 6.

## Prior-art position inherited (cite, do not re-derive)

`websearches/r2s1_direct/batch_1/report.md`: FiLM/modulated conditioned decoders
**preempted**; POD/RB coefficient regression (POD-NN / PCA-Net / RB-DeepONet)
**preempted**; conditional-mean-barrier certification
**preempted-but-MF-composition-open**. `websearches/r2s1_direct/batch_2/report.md`:
band-gain calibration = non-causal Wiener filter, **preempted**; training-free
output-form selection and the standing ~10^2-parameter closed-form control arm
**preempted-but-MF-composition-open**; identifiable-rank truncation left
UNRESOLVED, to be treated as presumed prior art. In-repo prior websearches
(`docs/reports/MF_Leaderboard_Beaters_2026_Report.md`,
`docs/reports/MF_Sharp_HighFreq_Report.md`) carry Lanthaler et al.
(arXiv:2210.01074) -- linear-reconstruction operators are provably inefficient
for discontinuous solution operators, which bounds every fixed-POD-basis arm on
4 of 6 panel datasets.

## What batch 3 must check (none prior-art-checked before this loop)

(A) per-mode out-of-fold model-family selection over a candidate bank for
reduced-basis coefficient regression; (B) the evaluation-protocol claim that a
shared post-hoc baseline-blend stage converts an accuracy comparison into a
decorrelation comparison (closed form in rho); (C) predictability-ordered (not
energy-ordered) output-basis / identified-SET indexing.
