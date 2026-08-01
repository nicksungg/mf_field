# Summary so far — stream `r2s2_stacked`, entering batch 3

## Where the stream stands

`r2s2_stacked` owns the lever question (program.md §4.1, §12.2): does
condition → pseudo-LF → (frozen round-1 corrector) beat direct condition→HF,
and how much is lost to pseudo-LF distribution shift?
Two cards are closed.

B1 (`experiment_cards/r2s2_stacked/batch_1/B1.json`) built the stack, landed panel geomean 14.076 against the launch anchor 23.064
(`state/anchors/r2s2_stacked.json`, best-floor panel geomean), and found the corrector worth <= 0.08 % on five of six panel columns.
It exported a coherence ELIGIBILITY GATE (`gamma_b1` with a 0.52 futility threshold).

B2 (`experiment_cards/r2s2_stacked/batch_2/B2.json`) is the round's ninth closed/registered card and it dismantles most of that.
Its part 6 interpretation records six HIGH-confidence measured findings; the two that drive batch 3 are:

- **H-STAGE**: "the condition-only stacked class on this panel collapses to a two-step recipe with ZERO gradient steps: average the real train LF solves of the k nearest conditions, then apply one closed-form spatially-invariant Wiener filter fitted on the fit fold."
  T3/F3.3 attributes the scored arm's test-side improvement over the raw intermediate as LSI/CNN/blend = 100/0/0 % (pfc), 97.0/3.0/0.0 % (cahn_hilliard), 77.1/22.9/0.0 % (fisher_kpp), 32.5/49.1/18.4 % (allen_cahn).
  In skill units the CNN buys 9.443 on allen_cahn and 0.081 / 0.000 / 0.019 elsewhere.
  The gated `LocalCorrector` was set to `alpha_nn = 0.0` by the out-of-fold calib line search on 5 of the 8 rung cells measured (part 6 surprises #1).
- **H-RULE-UNITS**: the exported coherence gate survives as a directional statistic but not as a decision rule — obeying it costs 8.8–116x the certified `min_claimable_effect` on 4/4 sharp datasets (T3/F3.7, F3.8-F3.9). STOP-EXPORT already issued in part 7 cross-stream note 1.

T3/F3.5: the trained stack still beats the best training-free out-of-fold `(k, base, lambda)` selection on all four sharp datasets by 14.126 / 2.698 / 1.868 / 0.083 skill units = 16.1x / 29.6x / 8.8x / 116.1x mce.
T3/F3.6: the fitted LSI transfer is a band-dependent shrink/sharpen (pfc bands [0.315, 0.383, 2.827, 6.897]), and a single global gain cannot reproduce it.

## The B3 decision the brainstormer owns

Part 7 `next_direction` lists: (i) promote the zero-gradient recipe (k-NN average of the train LF pool at calib-selected k* → one closed-form LSI Wiener filter) from diagnostic to a first-class SCORED panel arm;
(ii) re-run allen_cahn's gated-CNN increment at the round's 1+2-seed protocol — it alone decides whether this class needs a network;
(iii) close on B2 with the closed-form filter exported as the zero-parameter bar every other stream's learned corrector must beat.
Part 7 also forbids another ladder rung that is leave-one-out on train and no-self on test, and drops the coherence gate from the design.

## Noise-floor context (what counts as signal)

`state/noise_floor.json` (certified, `r2s4_diag-B1`, 3 seeds) gives per-dataset `min_claimable_effect` in skill units:
allen_cahn 0.8797, cahn_hilliard 0.09125, fisher_kpp 0.00071, pfc 0.21303, ifc_poisson 0.9377, helmholtz 2.9530; panel geomean mce 1.1419.
So allen_cahn's 9.443-skill-unit CNN increment is ~10.7x its mce **as a seed-spread comparison** — but B2's own concern is fold/fit noise at one fold seed and one fit, which the certified floor does not cover.
Helmholtz stays report-only (program.md §2.3 caveat, ADR r2-0004); pfc claims carry the band-limited denominator caveat.

## Prior websearch state for this stream

- `websearches/r2s2_stacked/batch_1/report.md`: D1 (condition→pseudo-LF→frozen corrector) `preempted` (Xu et al. 2023 arXiv:2310.00057; Yang et al. 2025 arXiv:2503.17941); D2 (frozen/fine-tuned/end-to-end attribution) `preempted-but-MF-composition-open`; D3 (LF as supervised bottleneck) `preempted` (Meng & Karniadakis arXiv:1903.00104; Howard et al. arXiv:2204.09157).
- `websearches/r2s2_stacked/batch_2/report.md`: D1 realisation-aware stage-1 `preempted-but-MF-composition-open`; D2a helmholtz amplitude×shape head `novel (thin)`; D2b POD+ridge on ifc_poisson `preempted` (Hesthaven & Ubbiali 2018); D3 coherence eligibility precondition `preempted-but-MF-composition-open` (FreqNO-DPS arXiv:2606.03936); D4 DPI closure claim `preempted` as principle, open as measurement.
  Standing methodological dead ends recorded there: arXiv `/pdf/` fetches are unsafe (one produced a confidently wrong summary); ScienceDirect/ResearchGate return 403; ADS abstract pages return empty bodies.
- In-repo prior websearches (cite, do not re-derive): `docs/reports/MF_Sharp_HighFreq_Report.md` line 260 already proposes *fitting the actual LF↔HF transfer kernel from training pairs (one FFT pass)* then unrolling proximal steps with the FNO as prox — the nearest in-repo neighbour to B2's closed-form Wiener stage; line 248 flags near-training-free patch-dictionary correctors.
  `docs/reports/MF_Leaderboard_Beaters_2026_Report.md` line 105 describes closed-form spectrally-shaped guidance (frequency-dependent weighting of a surrogate, no backprop); line 140 a training-free post-hoc GP FIRE source.

## Open questions this batch's search must serve

1. Is a **closed-form Wiener / LSI spectral filter as the post-processing corrector for a neural or retrieval-based PDE surrogate** published? If yes, direction (i) enters as a declared baseline, not a contribution.
2. Is there published precedent for **training-free/zero-gradient correctors beating trained ones in low-data PDE surrogate stacking**, and for **zero-parameter baselines used as evaluation bars** (direction (iii))?
3. Is the methodology of **re-running a single-cell gain under a multi-seed protocol to decide whether a learned stage is needed** (direction (ii)) an established protocol we should cite rather than invent?
