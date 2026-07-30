# Summary so far — Stream `s2_beyond_copy`, Batch 3

All paths relative to `mffp_autoresearch/round1/` unless absolute.

## 1. Websearch findings + prior-art verdict

Source: `websearches/s2_beyond_copy/batch_3/report.md` (merged from two concurrent
invocations; `report_merged_backup.md` identical; every URL resolves in
`iteration_{1..5}.md` + `parallel_run_b_iterations.md`). Five directions were scored:

- **D1 — per-sample normalization of the fidelity-residual TARGET on the same
  `lf_resid_fno` substrate: `preempted-but-MF-composition-open`.** DiSOL magnitude
  decoupling ("We define a per-sample amplitude u_lim"; "u_h := U_h / u_lim, so that
  max_x |u_h(x)| = 1"; "an optional amplitude regressor", https://arxiv.org/html/2601.09143v1)
  normalizes the **solution**; QuadNorm per-sample stats are operator **feature**-layer
  norms, "not inputs or targets" (https://arxiv.org/html/2605.07375); the canonical MF
  residual formulation (RMFNN, https://arxiv.org/html/2310.03572) "does not normalize the
  residual at all". Open: (i) instance-wise normalization of `HF-LF`; (ii) the scale must
  be **predicted from `(X, LF)`** at test time (not observable -> a true-scale arm is an
  ORACLE); (iii) the ESS diagnosis as stated cause; (iv) scoring vs a node-aligned reference.
- **D2 — per-sample no-harm trust gate: `preempted (cite)`** (routing safety
  https://arxiv.org/html/2603.14623; no-harm Def. 3 accept-else-return-baseline
  https://arxiv.org/html/2606.07153, whose certificate is a PDE residual -> ADR 0009 bars it
  for us). Instruction: "Include it, if at all, as a cheap non-promotable screening arm
  under ADR 0007 whose contribution is the *measurement* (oracle 0.3803 -> 0.2590)".
- **D3 — node-aligned reference column: `novel`** as benchmark hygiene, but "diagnostic/
  reporting only; the round-1 metric is frozen".
- **D4 — tail reweighting: preempted WITH a fetched negative** (density-inverse weighting
  raised test max error 76.63 K -> 96.72 K, https://arxiv.org/html/2605.16078). Do not propose.
- **D5 — `modes_cap`: not searched** by either run -> §12.5 audited knob F22, not this card.
- **Cross-cutting caution** (https://arxiv.org/html/2604.20061v1): "A network trained with
  mean-squared error converges to the conditional expectation ... over-smoothed by
  construction, and no architecture or training procedure can recover information the
  coarse representation discards" -> B3 **must pre-register a well-founded negative**.

## 2. §12.2 conventions (verbatim, program.md:379-397)

> ### 12.2 `s2_beyond_copy` (gap)
>
> - **Anchor: skill 1.0 = copy-LF.** The five datasets and their copy-LF test
>   nRMSE: helmholtz_2d 0.3295, phase_field_crystal_2d 0.0448, allen_cahn_2d
>   0.0162, fisher_kpp_2d 0.0626, cahn_hilliard 0.0877. Best zoo skills range
>   1.45–15.1 (§2.3) — every model DESTROYS LF information it was handed.
> - **Batch 1 is a diagnostic card** (pre-directed by the spec): localize where
>   and how models lose to copy-LF — per-frequency-band error vs copy-LF,
>   spatial error maps vs interface distance, error vs LF-HF residual magnitude.
>   Falsification framing: "the failure is concentrated in X" is falsified if
>   the error excess is spatially/spectrally uniform.
> - Candidate mechanisms for later batches (from the two literature reports):
>   additive-residual misalignment (the residual `HF-LF` is interface-hugging
>   and models blur it), rel-L2 blur preference, normalization destroying
>   amplitude structure, `modes_cap = 12` spectral wall on 96²–128² grids.
> - **Warning**: if the diagnostic finds LF/HF misalignment that looks like a
>   data defect, the honest output is a dataset bug report to the mentor, not a
>   model (spec §12).

Anchor (`state/anchors/s2_beyond_copy.json`): `value: 1.0`, `anchor_type: copylf_bar`,
`provisional: false`. Noise floor (`state/noise_floor.json`, `min_claimable_effect` in
absolute skill units on the batch-0 champion scale): pfc **1.151100**, allen_cahn
**1.633407**, cahn_hilliard **0.553347**, fisher_kpp **0.417735**, helmholtz **9.694961**
(-> report-only, ADR 0002 handling per the operator note).

## 3. Within-stream prior cards

**B1** (`experiment_cards/s2_beyond_copy/batch_1/B1.json`, diagnostic, complete): 0/27
factory families read the test-split LF field at inference (F14); a zero-parameter
`copy-LF + mean of 5 nearest train residuals` keyed on a 16x16 block-mean LF signature
reaches geomean **0.7886** vs the champion 9.6362 (F6); training-free lookups are
`do_not_promote`.

**B2** (batch_2/B2.json, model, complete; family `models_r1/s2_lf_residual_control`,
worktree `worktrees/s2_beyond_copy/B2`, build_commit `5bf0e86c2920...`; arm `lf_resid_fno`,
200 ep, seed 0). Scored skills: pfc **0.018360**, allen_cahn **0.287282**, cahn_hilliard
**0.453228**, fisher_kpp **0.804192**, helmholtz **4.135972** -> 5-dataset geomean
**0.380264**. Falsification verdict "confirmed" — but part 6 dismantles it:

- **F1/F2/F3**: copy-LF denominator is misregistered by the analytic `(r-1)/2` cells;
  the best zero-parameter fix removes 100.00 % (pfc) / 88.97 % (allen_cahn) / 79.37 %
  (fisher_kpp) / 53.69 % (cahn_hilliard) / 9.23 % (helmholtz) of copy-LF error; against
  that denominator the arm geomean flips **0.380 -> 10.31** and the free fix scores 0.0369.
- **F4**: the learned correction projects on the analytic registration field with cos
  0.9873 / 0.9993 at amplitude 0.996 / 0.986 (allen_cahn / cahn_hilliard) -> 97.5 % / 99.9 %
  of what 200 epochs produced is the zero-parameter resampling fix.
- **F5**: fisher_kpp shortfall is FNO band truncation — only 16.8 % of its true residual
  is below `modes_cap=12`; `sqrt(2(1-cos))` predicts 0.818 vs the scored 0.804.
- **F6**: pfc copy-LF is already exact on the easy decile (rel-L2 2.6e-08); the arm is
  WORSE than copy-LF on 50/100 samples; the pfc score is reproducible only to 6.5 %
  (21.9 % per sample) on CPU replay of the same checkpoint.
- **F8/F9**: helmholtz never fit its own train split (train skill 8.36 > test 3.29); one
  train-fitted global scalar `alpha = 0.0224` turns 4.136 into **0.995** — a pure gain failure.
- **F10 (the root cause)**: the family normalises the regression target by ONE global
  `max|HF-LF_up|` over the train split. Per-sample residual-scale spread (max/median):
  pfc **82379**, helmholtz **13702**, allen_cahn 3.91, cahn_hilliard 3.97, fisher_kpp 2.08.
  On helmholtz ONE of 400 train samples carries **89.2 %** of the MSE target energy
  (effective N = 1.2); on pfc the scaler is 79460x the median per-sample max, so most
  targets are numerically zero.
- **F12**: a per-sample no-harm gate (oracle) would give geomean **0.2590** (helmholtz
  4.136 -> 0.675); 83.7 % of the arm helmholtz error and 9.8 % of its pfc error is damage
  inflicted on top of copy-LF.
- **Part 7 next_direction** ranks exactly: (1) registration-corrected reported column,
  (2) **per-sample target normalisation** ("a clean 2x5 pre-registered contrast"),
  (3) the trust gate, (4) `modes_cap` last.
- Promoted tools: `tools/registration_skill_split.py`, `tools/target_scale_spread_audit.py`.

## 4. Cross-stream cards touching this stream

- **`docs/operator_notes/2026-07-30-benchmark-registration-note.md`** (both addenda):
  round-1 metric stays frozen; "batch-3 cards must pre-register falsification against
  corrected references (the C/D/E variants)" *as a carried column, never replacing the
  frozen skill*; "EVERY sharp-panel win must now be decomposed with
  `tools/registration_skill_split.py` before interpretation".
- **s5_tuning-B2** (analyzing; `MFFP_TARGET_SCALER=zscore`, a per-**dataset** affine on the
  LF-blind champion): helmholtz 13.817 -> 5.766 (inside its 9.695 floor), ifc_poisson 1.566
  -> 1.185 (beyond its 0.240 floor), and the four sharp sets all **inside** their floors
  (pfc 11.511 -> 11.216, allen_cahn 16.334 -> 16.643, cahn_hilliard 5.533 -> 5.458,
  fisher_kpp 4.177 -> 4.219). A per-dataset scaler moves the helmholtz/poisson amplitude
  channel and nothing sharp.
- **s7_loss-B1** (complete): a per-**sample**-normalised *objective* on the solution with
  gain weight lambda=4 CRATERED allen_cahn/helmholtz. Design rule M6: "(1) spread >= ~10 ->
  do not use it **without a denominator floor**; ... (3) the explicit gain weight lambda
  must be <= 1 ...; (4) never apply it to the LF-pretrain stage of a transfer". Also M5:
  5 independent amplitude/normalisation data points this round.
- **s1_poisson-B3** (analyzing): a per-sample multiplicative gain predicted from the
  condition vector improved ifc_poisson skill 0.951 -> 0.694 — in-repo evidence that a
  per-sample amplitude *predictor* is learnable from `(X, ...)`.
- **s6_local-B1**: local ConvNeXt corrector, geomean 0.2346 (pfc 0.030, allen_cahn 0.0805,
  fisher_kpp 0.0951, cahn_hilliard 0.4686, helmholtz **1.000** — its held-out scalar chose
  0, i.e. pure copy-LF); operator note: 87-98 % explained as the half-cell phase ramp.

## 5. Reopen candidates

None. No card in `experiment_cards/**` carries `reopen_candidate: true` (checked
programmatically across all 16 cards). Nothing to resolve.

## 6. What is UNKNOWN

1. **Is the target scaler causal, or just correlated with the two hard datasets?** F10 is
   an audit of the objective, not an intervention. Nobody has run the same substrate with
   the scaler changed. The 2x5 asymmetry (`target_scale_spread_audit.py` flags pfc and
   helmholtz, clears the other three) is a *prediction* the round has never tested.
2. **Is the per-sample residual scale predictable from `(X, LF)`?** Unmeasured. The
   mechanism gives a strong prior: where the residual is the registration ramp,
   `r ~ (h/2) grad(LF)`, so `||r_i|| ~ ||grad LF_i||` — computable from LF alone. s1-B3
   shows a condition-vector gain law is learnable elsewhere; nothing measures it here. The
   ORACLE (true-scale) minus predicted-scale gap is the missing number.
3. **How much of the pfc ~10 % damage budget is reachable?** The F12 gate oracle removes
   only 9.8 % of the arm pfc error, and F6 says pfc deltas below ~10 % are non-differences.
   So a pfc win must come mostly from *better shape fitting under a better-conditioned
   objective*, not from damage removal — and whether the conditioning gain exists is unknown.
4. **Does per-sample normalisation DESTROY the datasets it is supposed to leave alone?**
   s7-B1 M6 says a per-sample denominator silently re-weights samples by `1/s_i^2`; on pfc
   that is a 6.8e9 weight span, and the bottom decile "residual" is numerical roundoff.
   The needed but untested mitigation is a denominator floor. Its right value is unknown;
   only the audit tool (zero GPU, train split) can bound it before submit.
5. **Is anything left after registration?** B2 part 7 open question — "Is there ANY dataset
   on this panel where an LF-consuming operator beats a node-aligned reference?" — is
   unanswered, and https://arxiv.org/html/2604.20061v1 gives an a-priori reason for NO
   wherever HF carries no out-of-band energy (already proven for pfc). Any B3 gain must be
   split registration-vs-genuine before it means anything.
6. **Whether helmholtz can be moved by anything but a scalar.** F9 alpha=0.0224 and
   s6-B1 gate-selects-0 both reach ~1.0 for free; the report-only status (floor 9.695)
   means the dataset cannot carry a claim either way. Unknown: whether a *predicted
   per-sample* scale beats the single fitted scalar there — measurable, unclaimable.
7. **Whether `modes_cap` interacts.** fisher_kpp 16.8 % in-band fraction (F5) means the
   band cap, not the scaler, limits it — so fisher_kpp is a NEUTRAL prediction here and an
   F22 (s5) question later. Untested interaction: does per-sample normalisation change the
   in-band share the network can spend its 12 modes on?
