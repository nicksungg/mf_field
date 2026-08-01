# Summary so far — `r2s3_lf_train_signal`, entering batch 4

## Stream question and where it stands

The stream owns program.md §12.3: *how much does LF, available only during
training, help a condition→HF model?* Launch anchor (`state/anchors/r2s3_lf_train_signal.json`):
best-floor panel geomean **23.0636**, `anchor_type: best_floor_panel_geomean`,
`provisional: false`.
Per-dataset best floors: helmholtz 3.3441 (zero), ifc_poisson 10.0549 (NN),
allen_cahn 269.196 (NN), cahn_hilliard 23.1803 (NN), fisher_kpp 11.9931 (mean),
pfc 59.8118 (mean).

B3 (`experiment_cards/r2s3_lf_train_signal/batch_3/B3.json`) is closed
complete/registered. Its part 7 gives the operative state:

- The **affine-coverage hypothesis (clauses F1/F2) is falsified robustly** —
  5 of 7 defensible threshold readings agree, and F2 additionally fails under
  the gain-calibrated split.
- Under the operative threshold the ±LF effect is claimable on **exactly 3/6
  panel datasets** — ifc_poisson (+5.98), `sharp__cahn_hilliard` (+14.78),
  `sharp__fisher_kpp_2d` (+1.31) — with **explicitly unequal evidentiary
  strength**: ch passes 7/7 readings; ifc has a single native draw so no
  split-variance term is computable (an mce-only pass by construction); fk
  collapses to 0.919 against its own 0.947 range once gain is calibrated and
  additionally *loses to a 3-draw no-LF ensemble*.
- **Mechanism (part 6, T2-4/T2-5, M1)**: LF's train-time value is dominantly a
  **per-sample amplitude/gain calibration channel** — oracle-correcting only
  the per-sample gain collapses the no-LF arm's allen_cahn draw-range from
  726.06 to 22.63 skill units (**96.9%** of the draw-range), and the same
  oracle collapses draw ranges 1.5–73× on every dataset. LF pins output
  **scale, not the learned map**: three LF-trained allen_cahn models score
  within 0.41 skill units of each other while sitting 100.5 skill units apart
  in function space (inter-draw cosine 0.9485).
- **A 3-draw no-LF ensemble beats the LF arm exactly where LF does not pay**
  (fisher_kpp, pfc) — but it currently sees 15 HF rows and 3× compute, i.e. it
  is *not budget-matched*.
- Capacity is not the binding constraint: a zero-parameter 12-mode truncation
  of the true HF test field scores skill 0.09 (pfc) / 0.64 (ch), inside the
  family's own mode cap, while trained arms sit at ~60 and ~12.6.

## Candidate B4 directions from B3 part 7 (ranked there)

(a) **Is the gain channel LF-FREE-recoverable?** A condition-conditioned
per-sample gain/amplitude head fitted on the same 5 HF rows — training-free
probe on shipped prediction dumps first (`tools/residual_gain_learnability.py`,
also `tools/gain_calibration_ceiling.py`, `tools/band_gain_counterfactual.py`,
`tools/relative_gain_units_audit.py` exist). Decisive for whether the LF
headline survives.
(b) **Budget-matched pricing of the no-LF ensemble alternative** on ch and ifc.
(c) **Repaired claimability protocol** for draw-heteroscedastic effects:
worst-split gate, axis-appropriate variance constant, ≥5 draws (n=3 cannot
reach p<0.05 by any sign-based test).
Explicit do-not: no more LF-supply engineering on fisher_kpp or pfc.

## Threshold constants in play (`state/noise_floor.json`, certified, non-provisional)

`min_claimable_effect`: ifc 0.93770, ch 0.09125, fk 0.00071, ac 0.87970,
pfc 0.21303, hz 2.95299; panel geomean 1.14187. Source: `r2s4_diag-B1`,
family `r2s4_cert_min`, 3 **training seeds** at the **full 400-row split** —
B3 T1-3 records the axis mismatch: on allen_cahn the constant is 0.8797 while
the card's dominant noise source (HF-subset draw) moves 726.06 units (825×).
Any claim inside that constant, or inside the anchor's CI, is noise.

## Prior websearch state for this stream

- `batch_3/report.md` verdicts: **P1** panel-completion ±LF contrast =
  `preempted-but-MF-composition-open` (https://arxiv.org/html/2511.01830v1
  MF scaling laws; https://arxiv.org/html/2408.17075v1 functional-output MF
  survey+benchmark) with five named open items — condition-vector-only test
  input, N_hf≈5, certified claimability threshold, copy-LF denominator,
  condition-completeness-varying panel. **P2** coverage story = `preempted`.
  **P3** three-channel taxonomy = `preempted-but-MF-composition-open`.
  **P4** amplitude-corrected null penalty = `preempted`. **P5** gated/adaptive
  LF loss = `preempted`.
- Three independent misses across batches 1–3: "LF at training, no solver at
  inference" is not a named academic regime; no retrieved work uses a
  copy-the-LF-solution denominator for a condition-only surrogate; no
  rank/coverage training-free predictor of auxiliary-data value.
- In-repo prior websearches (cite, don't re-derive):
  `docs/reports/MF_Leaderboard_Beaters_2026_Report.md` line 46 —
  `mf_fno_transfer_film` IS LF-pretrain→HF-finetune (the stream's mandatory
  declared baseline, §12.3); `docs/reports/MF_Sharp_HighFreq_Report.md`
  §"displacement + amplitude" — three communities converged on decomposing
  field error into displacement + amplitude and fixing displacement first
  (Hoffman 1995; Keil & Craig 2009; Francom et al. arXiv:2305.08834), and
  PDE-Refiner's per-mode MSE ∝ amplitude² argument (arXiv:2308.05732).
  These are the nearest in-repo neighbours to direction (a) and must be
  re-checked against the *condition→field, few-HF* framing, not re-derived.

## Open questions this batch must retrieve against

1. Are per-sample **amplitude/scale/gain calibration heads** predicted from a
   scalar condition vector published for few-shot PDE/operator surrogates?
2. Is **output-norm / energy calibration** from parameters a named technique
   (and does anyone report it as an alternative to auxiliary low-fidelity
   data)?
3. **Deep ensembles vs auxiliary/multi-fidelity data** as competing
   variance-reduction routes at tiny N — has anyone priced them
   budget-matched?
4. **Claimability / significance protocols for split-heteroscedastic paired
   comparisons** in ML benchmarks (worst-split gates, per-split variance,
   minimum number of resamples).
