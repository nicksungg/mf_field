# Summary so far — `s2_beyond_copy`, batch 2 (written before searching)

## Where the stream stands

Batch 1 was the spec-pre-directed diagnostic
(`experiment_cards/s2_beyond_copy/batch_1/B1.json`, status complete). Its
headline is not a metric decomposition — it is an **input** finding:

- **F14 / M1**: 0 of 27 factory families with a `smoke_eval.py` read the TEST
  split's LF field at inference (static audit with file:line evidence,
  corroborated by a runtime forward-hook audit of the certified champion
  `mf_fno_transfer_film`, whose only eval-time input tensor is `[batch, 3]` —
  the condition vector). The whole round has been comparing X-only regressors
  against an LF-using baseline (copy-LF).
- **F6 (headline)**: a **zero-parameter** rule — `copy-LF + mean of the 5
  nearest TRAIN residuals (hf - lf)`, keyed on a 16x16 block-mean signature of
  the **test LF field** — scores panel geomean skill **0.7886** vs the
  certified champion's 9.6362, i.e. below the copy-LF bar (1.0) the whole
  round is trying to clear.
- **F7**: it is the **query key**, not the correction form. The same machinery
  keyed on the condition vector X gives 1.5413; keyed on the LF field 0.7886.
  Full ladder in card part 6: 0.7790 per-sample rescale oracle / 0.7886
  kNN-in-LF k=5 / 0.8296 k=10 / 0.8361 low-passed / 1.0000 copy-LF / 1.2156
  global scalar rescale / 1.5413 kNN-in-X residual / 9.6362 champion.
- **Class partition**: Class A (residual-learnable from the LF field) =
  `sharp__phase_field_crystal_2d` 0.562, `sharp__cahn_hilliard` 0.625,
  `ext__helmholtz_2d` 0.785 (unclaimable — its noise floor is 9.695,
  `state/noise_floor.json`). Class B (residual-unlearnable at N_train=400) =
  `sharp__allen_cahn_2d` 1.000, `sharp__fisher_kpp_2d` 0.9988; copy-LF is
  near-optimal there and F13 shows neither X nor the LF field predicts the
  residual.
- **F9**: signature-resolution sweep converged by 16x16; no duplication leak
  (test->train NN distance / train->train NN distance ~ 1.0 on 4/5 datasets).

## The batch-2 candidate prescribed by part 7

Part 7 `next_direction`: build the missing family — a `models_r1/` family whose
`smoke_eval` reads `test["field_by_fid"][max(lf_fids)]`, interpolates exactly
as `round1/eval/panel_data.py::copylf_prediction`, **concatenates it as an
input channel** to the existing FiLM-FNO backbone, and predicts the residual
`hf - lf` with copy-LF added back at output. Falsification anchored on the
training-free floor: "falsified if the trained LF-input residual family does
not beat 0.79 panel-geomean on the Class-A subset."

Constraints that bind batch 2: ADR 0009 (no governing equations at test time —
so physics-residual correctors are out), ADR 0004 (strict single seed;
provisional-single-seed labels), ADR 0007 (propose 3-5 variants, screen at
contract tier), program.md §5 pre-falsified levers (WNO swap, LF low-mode
freezing, diffusion prior), and §2.1 (the scored metric is immutable).
`state/noise_floor.json` min_claimable_effect: pfc 1.151, cahn_hilliard 0.553,
allen_cahn 1.633, fisher_kpp 0.418, helmholtz 9.695.

## What prior searches already established (do not re-derive)

- `websearches/s2_beyond_copy/batch_1/report.md`: metric machinery (band-error
  decomposition, per-scale coherence, shock/interface-stratified error,
  permutation importance) is published; the *reference* (error vs the model's
  own LF input) is a named gap in arXiv:2604.20061; identity-at-init is
  generic published practice (Fixup, arXiv:1901.09321); gated MF fusion exists
  only as a scalar-output BO surrogate.
- `websearches/_scouting/2026-07-29_stream_gap_mining/report.md`: C1
  (guaranteed-fallback trust-gated MF fusion) and C2 (LF-field-keyed retrieval
  residual transfer) both graded `preempted-but-MF-composition-open`; RASR
  (arXiv:2508.09449) is the image-domain retrieval-SR neighbor; no
  retrieval-augmented neural operator found in two framings; IRNO
  (arXiv:2605.24041) and Deep Delta Learning are the delta-learning neighbors.
- In-repo `docs/reports/MF_Leaderboard_Beaters_2026_Report.md` (prior agent
  websearch) already states: "**the residual delta = u_HF - u_LF is becoming the
  standard learning target**", citing MFFM (arXiv:2605.16118, velocity network
  **conditioned on u_LF**), Bhola flow-matching operators (arXiv:2512.12749,
  "probabilistic transport from LF approximations to the HF solution manifold
  via learned residual corrections", FiLM-conditioned FNO), IRNO. In-repo
  `docs/reports/MF_FNO_CNN_Hybrid_Report.md` §5.2 warns the additive-residual
  target on sharp interfaces can be a **dipole, larger and sharper than the
  field itself**.

## Open questions this batch's search must answer

1. Is "coarse/LF field as an input channel + predict the correction" a
   published pattern in MF operator learning, and what exactly do the closest
   instances report (setting, N_hf, whether they baseline against the coarse
   field)? Expect PREEMPTED; the job is to find the precise nearest neighbors.
2. Does a nonparametric/retrieval residual transfer keyed on a **field**
   signature exist in PDE/operator learning or in weather post-processing
   (analog methods are the obvious adversarial threat)?
3. Are hybrid parametric + nearest-neighbor-residual predictors published?
4. Is the "a trained model must beat a training-free lookup" comparison
   discipline itself a published framing?
