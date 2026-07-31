# Brainstormer Report — Stream `r2s2_stacked`, Batch 2

**Stream**: `r2s2_stacked` (lever)
**Batch**: 2
**Total iterations**: 1 (cap 5) — immutables self-check passed on the first pass
**Slot filled**: 1 / 1 (`diagnostic` card)
**Reopen candidates resolved**: 0 of 0 (none exist round-wide)

## Slot

- **Category**: `correctability_calibration / coherence-calibrated eligibility threshold for
  defect correctors + partial-coherence (DPI) closure measurement of the condition-only
  stacked class`

- **Card type**: `diagnostic` (with training — correctors are refit per ladder rung; precedent
  `r2s4_diag-B1`, a diagnostic card with training)

- **Motivation**: B1 exported a training-free precondition to the whole round (part 7
  cross-stream note 3) on the strength of three interpolation points measured with a *frozen*
  corrector, so correctability and distribution shift are confounded in every number it
  produced, and the rule's ceiling is an LSI oracle that has never been tested against the
  spatially adaptive gated CNN it is meant to gate. The websearcher's verdict makes exactly this
  the open content. **D3 — `preempted-but-MF-composition-open (cite)`**: *"FreqNO-DPS's
  diagnostic validates an ASSUMPTION OF ITS OWN FILTER (Fourier-diagonal residual covariance).
  r2s2's rule is a CALIBRATED THRESHOLD ON CORRECTOR VALUE (0.52 < gamma_b1 < 0.95 bracketed by
  the real→pseudo interpolation) plus an oracle-Wiener upper bound. No fetched source calibrates
  coherence against realised corrector value-add"* (FreqNO-DPS https://arxiv.org/html/2606.03936,
  VERIFIED: *"a prerequisite check for applying the method to any new surrogate"*,
  *"off-diagonal cross-spectral coherence diagnostic"*). **D4 — `preempted (cite)` as a
  principle; open as a measurement**: *"No fetched source states the DPI for stacked PDE
  surrogates or measures the resulting ceiling on field-valued MF benchmarks. Claim the
  measurement, cite the theorem for the principle"*
  (https://en.wikipedia.org/wiki/Data_processing_inequality). The card also answers **D1**'s
  negative prior in the design rather than around it — *"an independent sample has coherence 0
  with the test realisation in expectation"* — by scoring the empirical posterior sample
  (k = 1 nearest-condition train LF) against the conditional mean (k = all) at zero emulator
  cost, which is the only *"realisation-aware stage 1"* the stripped view (§5.9) admits; the
  expensive generative version of part-7 option (A) is dropped for the reason the websearcher
  states (ceiling ~1.6 skill units, predicted negative by three lines), and option (B) is
  dropped because `r2s1_direct-B2` is already running it on the full panel.

- **Concrete config**: new family `models_r2/r2s2_correctability` (worktree
  `worktrees/r2s2_stacked/B2`, branch `round2/exp-r2s2_stacked-B2`), condition-only at test,
  stripped view only, with tripwires `R2S2B2_REQUIRE_NO_TEST_LF=1` (raise if any test-side LF
  array is constructed) and `R2S2B2_ORACLE_LADDER_TRAIN_ONLY=1` (raise if a ladder-A rung is
  reachable from a test path). Vendored with provenance comments from
  `worktrees/r2s2_stacked/B1/models_r2/r2s2_stack` @ `6b4e1d48` (lineage `s4_router` @
  `b90d4662`): `lsi_filter.py` (closed-form Wiener `T(k)` + alpha line search **including 0**),
  `local_corrector.py::LocalCorrector` (`local_pixel_gate`, kernel 7, depth 4, width 32,
  zero-init head), `bands.py`, `periodicity.py`, `upsample.py` (per-dataset ADR r2-0001
  convention `node_aligned_periodic` / `dirichlet_node` / `legacy_cell_centred`, asserted to
  agree with `round2/eval/panel_data.py` on the TRAIN split at 1e-9 through a read-only import).
  Probe `probes/correctability_law.py` = the promoted
  `tools/surrogate_coherence_eligibility.py` adapted (identical band grid, coherence and
  oracle-Wiener formulas) plus the two modes M2 needs; promoted back via the register turn.
  **Folds** (`R2S2B2_FOLD_SEEDS=0,1,2`, identical across every rung and arm): train split →
  fit 0.70 / calib 0.15 / ladder-eval 0.15, disjoint and asserted disjoint (round 1's D3
  val_idx double-consumption caveat); `ifc_poisson` (N_hf = 5) LOO with calib/ladder-eval
  disabled below `R2S2B2_LOO_MIN_N=20` and every statistic low-n flagged.
  **Ladder A (train-side only, calibration, never on a test path)**:
  `X_t = irfft2((1-t)·F_real + t·F_mismatch)` where `F_real` is the row's own paired real train
  LF (upsampled by the dataset convention) and `F_mismatch` the real train LF of its
  nearest-condition *other* train row; `t ∈ {0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0}` — sweeps
  coherence while holding marginal amplitude statistics ~fixed.
  **Ladder B (test-legal, condition-only)**: `X_k` = mean of the real train LF fields of the k
  nearest train conditions (per-dim train-standardized L2, the `floors.json` definition),
  `k ∈ {1, 2, 4, 8, 16, 64, 256, all}`, leave-one-out on train rows; `k = 1` is the empirical
  posterior sample (part-7 option A at zero cost), `k = all` the conditional-mean LF (B1's A5).
  **Per rung, in order**: (M1a) training-free stats written BEFORE any fit — `gamma_band0..3`,
  target energy share, `input_over_target_amp`, in-sample oracle-LSI ceiling, identity nRMSE and
  the promoted rule's verdict label (the websearcher's "go/no-go before the submit", recorded as
  an in-job pre-registration); (M1b) refit closed-form LSI Wiener, fit fold → alpha on calib →
  evaluated on ladder-eval, all rungs × 3 fold seeds; (M1c) refit `LocalCorrector` at an
  **identical step budget for every rung** (`R2S2B2_CORR_STEPS_PER_EPOCH=10` ⇒ 2000 steps at
  200 epochs, 20 at contract tier) at rungs `{A:0, A:0.5, A:1.0, B:1, B:k*, B:all}`, fold seed 0;
  value-add(rung) = `1 − nRMSE(corrected)/nRMSE(intermediate)` on ladder-eval.
  **(M2) partial coherence given the condition**: conditioners `knn_oof` (k by out-of-fold
  error) and `ridge_pod16` fitted on the fit fold and applied out-of-fold to BOTH intermediate
  and HF; band coherence recomputed on the residuals; permutation null = 200 draws re-pairing
  intermediate rows within the eval fold.
  **(M3) scored arm** `test_hf` = ladder-B rung `k*` (chosen on calib) → LSI Wiener (alpha line
  search including 0) → `LocalCorrector` (zero-init gate) → out-of-fold blend
  `lambda·arm + (1−lambda)·base`, 21-point grid, base ∈ {zero, train_mean, nn_condition} chosen
  on calib; because `alpha = 0` and `lambda = 0` are in the grids the arm degrades gracefully to
  the best out-of-fold floor and `lambda*` is itself the deliverable (out-of-fold value of the
  realisation-carrying intermediate beyond the training-free floors). Reference splits (none
  beginning with `test`): `ref_k1_corrected`, `ref_kall_corrected`, `ref_k1_raw`, `ref_kall_raw`,
  `ref_rule_selected`, and the frozen floors `ref_zero`, `ref_train_mean`, `ref_nn_condition`
  seam-checked to `state/anchors/floors.json` at 1e-9, RAISING on mismatch. Guard leg
  `heat_local, fluid, sharp__sod_1d` at contract tier in a separate invocation (they populate
  the high-gamma end of the law — B1 F13 value-add 0.63/0.68 at t = 1 — and are labelled
  contract-tier). **Standing caveats carried**: `ifc_poisson` report-only for the law
  (B1 `pairing.paired_real_lf=false`, `attribution.valid=false`, `semantics_degraded=true`) but
  still scored for the panel geomean; `ext__helmholtz_2d` report-only with its zero-floor column
  3.3441; pfc claims carry the band-limited denominator and wrap-seam (deep-bulk 0.908) caveats.

- **Recipe**:

```json
{
  "base_family": "r2s2_stack",
  "base_commit": "6b4e1d4825666e037a43675c83d9bda6289ec9d0",
  "family_dir": "models_r2/r2s2_correctability",
  "datasets": "panel",
  "epochs": 200,
  "seeds": [0],
  "env": {
    "R2S2B2_LADDER_A_T": "0,0.1,0.25,0.5,0.75,0.9,1.0",
    "R2S2B2_LADDER_B_K": "1,2,4,8,16,64,256,all",
    "R2S2B2_LADDER_A_MISMATCH": "nearest_condition_other_train_row",
    "R2S2B2_LADDER_A_MIX_DOMAIN": "fourier_convex",
    "R2S2B2_LADDER_B_LOO": "1",
    "R2S2B2_NONLINEAR_RUNGS": "A:0,A:0.5,A:1.0,B:1,B:kstar,B:all",
    "R2S2B2_FOLDS": "0.70,0.15,0.15",
    "R2S2B2_FOLD_SEEDS": "0,1,2",
    "R2S2B2_NONLINEAR_FOLD_SEED": "0",
    "R2S2B2_LOO_MIN_N": "20",
    "R2S2B2_CORR_STEPS_PER_EPOCH": "10",
    "R2S2B2_KERNEL": "7",
    "R2S2B2_DEPTH": "4",
    "R2S2B2_WIDTH": "32",
    "R2S2B2_GATE_INIT": "zero",
    "R2S2B2_VARIANT": "local_pixel_gate",
    "R2S2B2_LSI_RIDGE": "0",
    "R2S2B2_ALPHA_LINESEARCH_INCLUDES_ZERO": "1",
    "R2S2B2_BAND_EDGES_FRAC": "0,0.125,0.25,0.5,1.0",
    "R2S2B2_UPSAMPLE": "corrected_by_convention",
    "R2S2B2_UPSAMPLE_ASSERT_TOL": "1e-9",
    "R2S2B2_PAD_MODE": "circular_if_periodic",
    "R2S2B2_CONDITIONER": "knn_oof,ridge_pod16",
    "R2S2B2_POD_RANK": "16",
    "R2S2B2_PERM_NULL_DRAWS": "200",
    "R2S2B2_BLEND_GRID": "21",
    "R2S2B2_BLEND_BASES": "zero,train_mean,nn_condition",
    "R2S2B2_FLOORS_JSON": "mffp_autoresearch/round2/state/anchors/floors.json",
    "R2S2B2_FLOOR_ARMS": "nn_condition,train_mean,zero",
    "R2S2B2_FLOOR_TOL": "1e-9",
    "R2S2B2_REQUIRE_NO_TEST_LF": "1",
    "R2S2B2_ORACLE_LADDER_TRAIN_ONLY": "1",
    "R2S2B2_IFC_REPORT_ONLY": "1",
    "R2S2B2_PROBE": "probes/correctability_law.py",
    "R2S2B2_DIAG_OUT": "mffp_autoresearch_outputs/round2/r2s2_stacked/B2/eval",
    "_substrate_commit": "9e10d414e35a96398f7b091bc84ddf936d88acc7",
    "_vendor_source": "worktrees/r2s2_stacked/B1/models_r2/r2s2_stack @ 6b4e1d48 (lsi_filter.py, local_corrector.py, bands.py, periodicity.py, upsample.py), itself vendored from round1/worktrees/s4_hybrid_routing/B3/models_r1/s4_router @ b90d4662; probe adapted from tools/surrogate_coherence_eligibility.py (promoted by r2s2_stacked-B1)",
    "_note": "keys prefixed _ are card directives, NOT passed to --env. score_panel.py --datasets accepts ONLY the exact keyword 'panel' or 'guard' or a comma-list of dataset NAMES, so the guard leg is a SEPARATE invocation with --datasets guard at contract tier (epochs 2, seed 0), matching round-1 and r2s2-B1 practice. --time: size from state/timing_ledger.json (r2s2_stack panel leg 20.13 min at 200ep/6 datasets with a 4.78M FNO + 5 arms); this card trains no emulator but refits ~6 small correctors per dataset, so 02:00:00 is the recommended request.",
    "_ifc_caveat": "ifc_poisson: B1 diag recorded pairing.paired_real_lf=false, max_abs_cond_deviation_lf_vs_hf=0.682 (n_hf_train=5, n_lf=20), attribution.valid=false; ladder A is NOT constructible there. The column is report-only for the coherence law and every ifc statistic carries semantics_degraded=true; it remains scored for the panel geomean.",
    "_arms": [
      {"tag": "test_hf", "rung": "B:kstar", "corrector": "lsi+local", "blend": "oof_lambda_over_best_floor_base", "role": "SCORED diagnostic instrument; lambda* = out-of-fold value of the intermediate beyond the floors"},
      {"tag": "ref_k1_corrected", "rung": "B:1", "corrector": "lsi+local", "role": "empirical posterior SAMPLE (part-7 option A at zero emulator cost)"},
      {"tag": "ref_kall_corrected", "rung": "B:all", "corrector": "lsi+local", "role": "CONDITIONAL MEAN intermediate (B1 arm A5 analogue); F2 contrast partner"},
      {"tag": "ref_k1_raw", "rung": "B:1", "corrector": "none", "role": "uncorrected sample; isolates the corrector's contribution"},
      {"tag": "ref_kall_raw", "rung": "B:all", "corrector": "none", "role": "uncorrected conditional mean"},
      {"tag": "ref_rule_selected", "rung": "per training-free verdict", "corrector": "applied only if CORRECTOR_ELIGIBLE", "role": "decision-level validation of the exported rule"},
      {"tag": "ref_zero", "rung": "-", "corrector": "none", "role": "mandatory floor arm (§2.2), seam-checked 1e-9"},
      {"tag": "ref_train_mean", "rung": "-", "corrector": "none", "role": "mandatory floor arm (§2.2), seam-checked 1e-9"},
      {"tag": "ref_nn_condition", "rung": "-", "corrector": "none", "role": "mandatory floor arm (§2.2), seam-checked 1e-9"}
    ]
  }
}
```

- **Expected outcome**:
  * **Scored `test_hf` panel geomean 15-25** — the floor band, explicitly not a champion attempt
    (anchor 23.0636; crater bound 1.5x = 34.595). `lambda* → 0` expected on pfc / allen_cahn /
    fisher_kpp (structural ceiling, ADR r2-0003); `lambda* > 0` only plausible on cahn_hilliard
    and the two learning-gap columns. Δ vs anchor: −0 to −8 skill units, i.e. at or modestly
    below the anchor, and clearly worse than B1's 14.0756 — by design, because the correctable
    signal B1's ifc column exploited is not available to a condition-only k-NN intermediate.
  * **M1 (calibration)**: value-add(gamma) monotone with the claimable crossing located to
    within one ladder step inside B1's bracket (gamma_band1 0.52 → 0.95); predicted
    `gamma* ∈ [0.80, 0.95]` for the LSI stage. Refit-vs-B1-frozen separates correctability from
    distribution shift: the refit curve should sit a few percent above the frozen curve at low
    gamma and converge as gamma → 1.
  * **M1c (the risky prediction)**: the nonlinear `LocalCorrector`'s realised value-add stays at
    or below the training-free in-sample oracle-LSI ceiling on every condition-only rung — i.e.
    the exported rule is safe. This is the clause most likely to fail (a gated CNN can fix
    spatially varying registration/edge error that an LSI filter cannot), and failing it
    corrects a round-level rule.
  * **M2 (closure)**: partial `gamma_band1` of every ladder-B rung inside its permutation-null
    band (|Δ| < 0.10) on ≥ 5/6 datasets, against real LF (ladder A, t = 0) partial
    `gamma_band1 ≥ 0.9` on the three ADR r2-0003 datasets — the D4 measurement: how much a
    genuine coarse solve carries beyond the condition, and that no condition-only intermediate
    carries any of it.
  * **M3 (option A settled on test)**: after correction, k = 1 (sample) WORSE than k = all
    (conditional mean) on ≥ 5/6 datasets, by more than the certified mce on ≥ 3.
  * **vs the noise floor** (`state/noise_floor.json`, `_provisional: false`): every test-split
    comparison is judged against the certified per-dataset `min_claimable_effect` — pfc
    **0.2130273**, allen_cahn **0.8797047**, fisher_kpp **0.0007137**, cahn_hilliard
    **0.0912454**, ifc_poisson **0.9377041**, panel geomean **1.1418668**; helmholtz
    (**2.9529916**) exceeds any effect available against its 3.3441 zero floor and is therefore
    report-only and carries no falsification weight. Train-side dimensionless quantities (F1, F3)
    use the in-job 3-fold-seed paired spread with an absolute floor (0.05 relative gain; 0.10
    coherence over a 200-draw permutation null).

- **Expected falsification** (one sentence, four clauses): H-r2s2-B2 — *"correctability of an
  intermediate is governed by its coherence with the target after the condition-predictable
  component is removed, so on this panel no condition-only intermediate is worth correcting and
  the exported training-free coherence rule is safe for nonlinear correctors"* — is FALSIFIED if
  **(F1, rule safety)** a refit `LocalCorrector`'s realised value-add on any rung the promoted
  rule labels `CORRECTOR_FUTILE` (gamma_band1 ≤ 0.52) exceeds that rung's training-free
  in-sample oracle-LSI ceiling by more than `max(3× in-job fold-seed paired spread, 0.05
  relative error reduction)` on ≥ 3 ladder cells, **or (F2, realisation-aware branch)** the k = 1
  sample arm beats the k = all conditional-mean arm on the TEST split by more than that
  dataset's certified `min_claimable_effect` (pfc 0.2130273 / allen_cahn 0.8797047 / fisher_kpp
  0.0007137 / cahn_hilliard 0.0912454 / ifc_poisson 0.9377041; helmholtz report-only at
  2.9529916) on ≥ 2 panel datasets, **or (F3, closure)** any ladder-B rung's partial coherence
  given the condition exceeds its own permutation-null 95th percentile by > 0.10 on ≥ 2 datasets
  under both conditioners, **or (F4, calibration validity)** the scored blended arm loses to its
  own out-of-fold-selected floor base by more than the certified `min_claimable_effect` on ≥ 2
  panel datasets.

- **Prior-art verdict quoted** (verbatim from `websearches/r2s2_stacked/batch_2/report.md`):
  * **D3** — *"`preempted-but-MF-composition-open (cite)`"*; *"FreqNO-DPS's diagnostic validates
    an ASSUMPTION OF ITS OWN FILTER (Fourier-diagonal residual covariance). r2s2's rule is a
    CALIBRATED THRESHOLD ON CORRECTOR VALUE (0.52 < gamma_b1 < 0.95 bracketed by the real→pseudo
    interpolation) plus an oracle-Wiener upper bound. No fetched source calibrates coherence
    against realised corrector value-add."* Citations: FreqNO-DPS
    https://arxiv.org/html/2606.03936 (VERIFIED: *"prerequisite check for applying the method to
    any new surrogate"*, *"off-diagonal cross-spectral coherence diagnostic"*); SCP metric
    https://arxiv.org/pdf/2509.23074; in-repo coherence<0.7 cutoff
    `docs/reports/MF_Sharp_HighFreq_Report.md` 226/295/336.
  * **D4** — *"`preempted (cite)` as a principle; open as a measurement"*; *"No fetched source
    states the DPI for stacked PDE surrogates or measures the resulting ceiling on field-valued
    MF benchmarks. Claim the measurement, cite the theorem for the principle."* Citations: DPI
    https://en.wikipedia.org/wiki/Data_processing_inequality,
    https://people.ece.cornell.edu/zivg/ECE_5630_Lectures7.pdf,
    https://theses.eurasip.org/document/information-loss-in-deterministic-systems/; end-to-end >
    staged: CALM-PDE https://arxiv.org/abs/2505.12944, MFFM https://arxiv.org/html/2605.16118
    (VERIFIED).
  * **D1** (why the generative version of option A is dropped, quoted as instructed) —
    *"`preempted-but-MF-composition-open (cite)`: the exact topology (parameter → *sampled* LF
    realisation → corrector trained on real coarse solves) and a coherence-threshold acceptance
    criterion appear in no fetched source. But the outcome is predicted negative by three lines:
    K-sample mean = conditional mean; an independent sample has coherence 0 with the test
    realisation in expectation; DPI."*

- **Immutables self-check**: **pass (11/11)** — 8 §5 immutables plus the three round-2 extras
  (noise-floor clearance, not-a-pre-falsified-lever, floor arms), each with positive evidence in
  [iteration_1.md](iteration_1.md) §"Immutables self-check". Nothing flagged; no revision, hence
  no `iteration_2.md`.

- **Anchor reference**: `null` (program.md §4.5 / §12 — null for all four round-2 streams; the
  own-stream anchor 23.063616857615774 is implicit).

- **Source iteration**: [iteration_1.md](iteration_1.md)

## Reopen candidates

| Candidate | Verdict (retry/drop) | Eased conditions | Source iteration |
|---|---|---|---|
| (none — `grep -rl '"reopen_candidate": true' experiment_cards/` returns nothing round-wide; `r2s2_stacked-B1` carries `reopen_candidate: false`) | n/a | n/a | [iteration_1.md](iteration_1.md) |

## Skipped slot

Not applicable — the slot is filled. Two alternatives were explicitly rejected with reasons
recorded in [iteration_1.md](iteration_1.md): part-7 option (A) in its generative form (the
stripped view exposes only the condition, so no admissible stage 1 conditions on anything the
conditional mean lacks; cahn_hilliard's binding defect is sampling, which §5.11 forbids fixing
with more data; ceiling ~1.6 skill units) and part-7 option (B) (already in flight as
`r2s1_direct-B2`, which runs the closed-form condition→HF head and the capacity ladder on the
full panel including the ifc POD+ridge head).

## Summary table

| Slot | Category | One-liner | Status |
|---|---|---|---|
| 1 | `correctability_calibration` | Two training-free intermediate ladders (oracle spectral mix; test-legal k-NN-in-condition LF) with the corrector **refit at every rung at a matched budget**: calibrates the exported coherence threshold against realised corrector value-add, stress-tests the rule against a nonlinear corrector, measures the DPI closure as partial coherence given the condition, and settles part-7 option (A) on the test split at zero emulator cost. | filled (`diagnostic`) |
