# Brainstormer Report — Stream `s2_beyond_copy`, Batch 3

**Stream**: s2_beyond_copy · **Batch**: 3 · **Total iterations**: 1 · **Slot filled**: 1/1
· **Reopen candidates resolved**: 0 of 0 (none exist)

## Slot

- **Category**: `mf_composition / target-normalisation repair — per-sample amplitude
  normalisation of the fidelity residual with a test-time-PREDICTED scale`
- **Card type**: `model`

### Motivation (card part 2)

B2 part 6 F10 located the root cause shared by this substrate's best and worst dataset:
the family normalises its regression target by **ONE global `max|HF-LF_up|`** over the
train split, while the per-sample residual scale spans decades — `max/median ||HF-LF_up||`
= **82379** (pfc), **13702** (helmholtz), 3.91 / 3.97 / 2.08 (allen_cahn / cahn_hilliard /
fisher_kpp); on helmholtz ONE of 400 train samples carries **89.2 %** of the MSE target
energy (effective N = **1.2**), and a single train-fitted scalar `alpha = 0.0224` turns the
4.136 failure into 0.995 (F9); on pfc the scaler is 79460x the median per-sample max, so
most targets are numerically zero and a zero-init head still emits ~1e-4 relative junk,
damaging 50/100 samples copy-LF already had exact (F6). B2 part 7 ranks the fix second of
four and names the evidence design: per-sample target normalisation is flagged by
`tools/target_scale_spread_audit.py` "as necessary on exactly pfc ... and helmholtz ... and
unnecessary on the other three — a clean 2x5 pre-registered contrast". The batch-3 search
scores exactly this construction **`preempted-but-MF-composition-open`** and settles its
one design constraint (the scale is not test-observable, so it must be predicted from
`(X, LF)`; a true-scale arm is an ORACLE). The card therefore repairs an assumption the MF
literature makes implicitly — RMFNN "does not normalize the residual at all" and merely
assumes `||F||_inf << ||Q_HF||_inf` (https://arxiv.org/html/2310.03572) — that our panel
violates by 4-5 orders of magnitude.

### Concrete config (card part 3)

New family `models_r1/s2_resid_amplitude_norm`, **vendored verbatim** from
`round1/worktrees/s2_beyond_copy/B2/models_r1/s2_lf_residual_control` at B2's build_commit
`5bf0e86c292042b3050979f5c35af538305f1152` (which itself vendors `mf_fno_transfer_film` @
`967562e2a4e3493515edab36b0fcb23655fce71f`), then renamed. **Unchanged**: FNO2d network,
`hidden_channels=64`, `n_blocks=4`, `modes_cap=12`, batch size, lr, schedule, weight decay,
grad clip, WORK_CAP=256, zero-init final 1x1 (identity-at-init proof), `max(lf_fids)` LF_up
input channel, the copy-LF seam check, the leakage tripwires, single-stage training (the
promoted arm has **no LF-pretrain stage**, `smoke_eval.py:628` — s7_loss-B1 M6 rule (4)
satisfied by construction), plain `F.mse_loss` (no gain weight; M6 rule (3) `lambda = 1`).

**The one behavioural change** — at `smoke_eval.py:223-224, 243, 289, 504` the scalar
`scaler_out = _scale(r_tr) = max|r|_train` becomes a per-sample vector:

```
s_i        = max( max_x |r_i(x)| , q25({s_j^raw}_train) )      # denominator FLOOR (s7-M6 rule 1)
target_i   = r_i / s_i                                          # training space
s_hat_i    = exp( g_phi(X_i, log max|LF_i|, log ||grad LF_i||_2, log ||LF_i||_2, log std LF_i) )
y_hat_i    = LF_up_i + s_hat_i * Delta_theta(...)               # TEST time (scale predicted)
```

`g_phi` = 2-layer MLP width 64, trained on the TRAIN split only, MSE on `log10 s`, 200
epochs, lr 1e-3, same seed, checkpointed in the same `last.pt`. Physical prior for the
features: where the residual is the registration ramp (F4: cos 0.987-0.999), `r ~ (h/2)
grad(LF)`, so `||r_i|| ~ ||grad LF_i||` is LF-computable. Precedents: DiSOL's "optional
amplitude regressor" (https://arxiv.org/html/2601.09143v1) and, in-repo, s1_poisson-B3's
condition-vector gain law (ifc_poisson 0.951 -> 0.694).

**Arms (ADR 0007; fixed promotion rank pinned BEFORE submit)**

| rank | arm (`S2B3_ARM`) | definition | role | promotable |
|---|---|---|---|---|
| — | **A0** `global_ctrl` | B2's exact path, one global `max|r|` scaler | paired control in the SAME 200-ep job (same node/seed/code_hash) + B2-continuity gate | **never** |
| **1** | **A1** `persample_pred` | per-sample maxabs + q25 floor, scale predicted by `g_phi(X, LF)` | **THE CANDIDATE — scored arm** | yes (pinned) |
| 2 | **A2** `persample_gradproxy` | same normalisation; closed-form `s_hat_i = c*||grad LF_i||_inf`, `c` by least squares in log space on train | fallback if A1 is *broken*; no extra network | yes |
| — | **A3** `ref_oracle_truescale` | A1's checkpoint re-evaluated with the TRUE per-sample `s_i` | **ORACLE** — bounds the headroom the scale predictor gives away; HF test enters ONLY this ref path | **never** (`ref_*` split, leakage-fenced) |
| — | **A4** `ref_gate_lfkeyed` | physics-free no-harm gate on A1's output: 16x16 block-mean LF signature, k=5 train neighbours, accept-model iff predicted margin < threshold calibrated on a 20 % HF-**train** holdout | D2 **measurement only** (oracle 0.3803 -> 0.2590 context); no mechanism claim | **never** (`ref_*` split) |
| — | **A5** `persample_nofloor` | A1 without the q25 floor | contract-tier screen only — audits the s7-M6 denominator-floor rule | **never** (screen) |

*Broken* := crash / non-finite metric / contract-tier 5-dataset geomean > 3.0x A0's on the
same screen run. Close calls never reorder. Screen numbers live in `build_notes` only.

**MANDATORY instrumentation (all zero-GPU, all in the card):**
1. `tools/registration_skill_split.py` on **both** arms' shipped per-run JSONs -> per
   dataset `variant_skill_vs_copylf`, `pct_copylf_error_removed_{model,best_fix}`,
   `model_skill_vs_best_fix`, `no_harm_gate_oracle_skill`, `damage_share`, and the corrected
   geomean; the card must state **what fraction of any improvement is registration vs
   genuine** (A0's reference values: pfc ~100 %, allen_cahn 97.5 %, cahn_hilliard 99.9 %,
   fisher_kpp 95.9 %, corrected geomean 10.31, free fix 0.0369).
2. `tools/target_scale_spread_audit.py` **before** (global scaler; the F10 numbers above)
   and **after** (effective N and weight spread under the floored `s_i` and under the
   PREDICTED `s_hat_i`) — the "after" numbers under `s_hat`, not under the true scale, are
   the informative ones.
3. Scale-predictor quality per dataset: Spearman `rho(s_hat, s_true)`, median
   `|log10(s_hat/s_true)|`, and the A3-minus-A1 skill gap.
4. Per-sample rel-L2 columns dumped for both arms (needed by 1 and by the gate).

**Reported-only sidecar (D3)**: the node-aligned variant-C/D/E reference column, carried
ALONGSIDE the frozen copy-LF skill, never replacing it (immutables 2-4; operator note
`docs/operator_notes/2026-07-30-benchmark-registration-note.md`).

### Recipe (card `recipe`, transcribe verbatim)

Vendor source (part 3, for the builder):
`round1/worktrees/s2_beyond_copy/B2/models_r1/s2_lf_residual_control` @ `5bf0e86c2920...`.

```json
{
  "base_family": "s2_lf_residual_control",
  "base_commit": "5bf0e86c292042b3050979f5c35af538305f1152",
  "family_dir": "models_r1/s2_resid_amplitude_norm",
  "datasets": "ext__helmholtz_2d,sharp__phase_field_crystal_2d,sharp__allen_cahn_2d,sharp__fisher_kpp_2d,sharp__cahn_hilliard",
  "epochs": 200,
  "seeds": [0],
  "env": {
    "S2B3_ARM": "persample_pred",
    "S2B3_SCORED_ARMS": "global_ctrl,persample_pred",
    "S2B3_PROMOTION_RANK": "persample_pred,persample_gradproxy",
    "S2B3_PROMOTION_RULE": "pinned_rank1_unless_broken__broken=crash|nonfinite|screen_geomean_gt_3x_global_ctrl",
    "S2B3_SCREEN_ARMS": "global_ctrl,persample_pred,persample_gradproxy,persample_nofloor",
    "S2B3_SCREEN_EPOCHS": "2",
    "S2B3_SCREEN_DATASETS": "beyond_copy5,guard",
    "S2B3_SCREEN_BROKEN_FACTOR": "3.0",
    "S2B3_TARGET_NORM": "per_sample_maxabs",
    "S2B3_SCALE_STAT": "maxabs",
    "S2B3_SCALE_FLOOR_MODE": "train_quantile",
    "S2B3_SCALE_FLOOR_Q": "0.25",
    "S2B3_SCALE_PREDICTOR": "mlp_logscale",
    "S2B3_SCALE_FEATURES": "cond,log_max_abs_lf,log_grad_l2_lf,log_l2_lf,log_std_lf",
    "S2B3_SCALE_MLP_HIDDEN": "64",
    "S2B3_SCALE_MLP_LAYERS": "2",
    "S2B3_SCALE_LOSS": "mse_log10",
    "S2B3_SCALE_LR": "1e-3",
    "S2B3_SCALE_EPOCHS": "200",
    "S2B3_REF_SPLITS": "ref_oracle_truescale,ref_gate_lfkeyed",
    "S2B3_REF_SPLITS_ARE_REF_ONLY": "1",
    "S2B3_ORACLE_TRUESCALE": "ref_only",
    "S2B3_GATE_KEY": "blockmean16_k5",
    "S2B3_GATE_HOLDOUT_FRAC": "0.2",
    "S2B3_GATE_CALIBRATION": "train_holdout_margin_quantile",
    "S2B3_REGISTRATION_SPLIT": "1",
    "S2B3_SCALE_AUDIT": "1",
    "S2B3_DUMP_PER_SAMPLE": "1",
    "S2B3_LEAKAGE_TRIPWIRE": "1",
    "S2B3_DIAG_OUT": "mffp_autoresearch_outputs/round1/s2_beyond_copy/B3/eval",
    "S2_LF_SOURCE": "dataset_lf_fidelity",
    "S2_LF_FID": "max",
    "S2_LF_CHANNELS": "max_only",
    "S2_TARGET": "residual_hf_minus_lfup",
    "S2_HEAD_INIT": "zero",
    "S2_HIDDEN": "64",
    "S2_BLOCKS": "4",
    "S2_MODES_CAP": "12",
    "S2_FLOOR_ARMS": "retr_blockmean16_k5",
    "S2_FLOOR_REQUIRED": "retr_blockmean16_k5",
    "S2_FLOOR_SIG": "16",
    "S2_FLOOR_K": "5",
    "S2_FLOOR_F6_TOL": "0.02",
    "S2_FLOOR_SPLITS_ARE_REF_ONLY": "1",
    "S2_FALLBACK_NO_TEST_LF": "champion",
    "S2_LEAKAGE_TRIPWIRE": "1"
  }
}
```

Builder notes carried by part 3: B2's `retr_s1grad_k5` / `retr_patch_k5` floors and the
`blend_trained_retrieval` path are REMOVED (their B2 numbers stand; not re-run) and
`REQUIRED_ENV` is updated to the list above; `retr_blockmean16_k5` is retained because its
F6 tolerance check (`S2_FLOOR_F6_TOL=0.02` vs B1's 0.562/0.625/0.785/1.042/1.062) is the
data-path seam guard and its signature code is reused by the A4 gate.

### Expected outcome (card part 4)

Seed 0, 200 epochs, `provisional-single-seed` (ADR 0004); all deltas against the **paired
A0 control** in the same job, with B2's part-5 numbers as the cross-check (A0 must reproduce
them within 10 % on pfc — F6's replay caveat — and 2 % elsewhere; a miss is recorded as a
rebuild-fidelity flag, not a result).

| dataset | A0 (B2) | A1 predicted | why | vs floor |
|---|---|---|---|---|
| `sharp__phase_field_crystal_2d` | 0.018360 | **0.010** (0.006-0.014) | targets stop being numerically zero (scaler was 79460x the median per-sample max), so the head is finally taught to emit ~nothing where the truth is ~nothing (removes the 9.8 % damage) AND all 400 samples contribute gradient instead of an effective handful | −45 % = 63x the rescaled seed spread 0.007180, 4.5x the 10 % pfc reproducibility band |
| `ext__helmholtz_2d` | 4.135972 | ~1.0 (0.7-1.4) | F8/F9: pure gain failure, effective N 1.2; a per-sample predicted scale subsumes the single train-fitted `alpha = 0.0224` that already reaches 0.995 | **REPORT-ONLY** (rescaled floor 0.701654; abs floor 9.694961) |
| `sharp__allen_cahn_2d` | 0.287282 | NEUTRAL, inside [0.244190, 0.330374] | spread 3.91 -> audit verdict OK; the residual is 97.5 % registration ramp, unchanged by rescaling | band = 173x the rescaled spread 0.000866 |
| `sharp__cahn_hilliard` | 0.453228 | NEUTRAL, inside [0.385244, 0.521212] | spread 3.97 -> OK; its error is a SHAPE failure on copy-LF's own tail (F11: per-sample-gain oracle removes 0.7 %) | band = 4.33x the rescaled spread 0.034667 |
| `sharp__fisher_kpp_2d` | 0.804192 | NEUTRAL, inside [0.683563, 0.924821] | spread 2.08 -> OK; its limiter is the modes_cap-12 band wall (F5: 16.8 % in-band; `sqrt(2(1-cos))` = 0.818 vs scored 0.804), not the scaler | band = 6.83x the rescaled spread 0.021973 |
| 5-dataset geomean | 0.380264 | ~0.25 | helmholtz-dominated -> not a headline | — |
| **leave-helmholtz-out geomean** | **0.20940** | **~0.18** | the honest headline (s5-B1/B2 precedent) | −14 % |

Also predicted: A3 (ORACLE) <= A1 on pfc and helmholtz, with the gap quantifying what the
predictor costs; `rho(s_hat, s_true)` >= 0.8 on the registration-dominated sets; the audit's
`effective_n_samples_of_mse` under `s_hat` rising from 1.2/400 (helmholtz) to >= 200; A4's
gate reported at ~A1's own level (its B2-measured value was worth 0.3803 -> 0.2590 on the
*unrepaired* arm, and the card predicts the repair absorbs most of that headroom — if the
gate is still worth a lot after A1, the scale lever did not fix the damage).

### Expected falsification (card `expected_falsification`)

H-B3 ("the family's single global `max|HF-LF|` target scaler — not its architecture — is
what breaks the LF-residual corrector on the two datasets whose per-sample residual scale
spans decades, and replacing it by a per-sample amplitude normalisation whose test-time
scale is PREDICTED from `(X, LF)` repairs those and does nothing to the other three") is
FALSIFIED at 200 epochs / seed 0 if ANY of:
**(a) PRIMARY (pfc)** the scored arm's `sharp__phase_field_crystal_2d` skill is not
`<= 0.80 x` the paired A0 control's (`<= 0.014688` at B2's 0.018360) — 20 % relative is
**2x** the pfc score-reproducibility band (B2 F6: 6.5 % H100-vs-CPU replay, 21.9 % per
sample; "treat pfc deltas below ~10 % as non-differences") and **27.9x** the rescaled
batch-0 seed spread `0.082643/11.511001 = 0.007180`;
**(b) ASYMMETRY** any of `sharp__allen_cahn_2d` / `sharp__cahn_hilliard` /
`sharp__fisher_kpp_2d` moves by more than **+/-15 %** vs A0 — bands [0.244190, 0.330374] /
[0.385244, 0.521212] / [0.683563, 0.924821]; 15 % = **173x / 4.33x / 6.83x** the rescaled
batch-0 seed spreads 0.000866 / 0.034667 / 0.021973 — **in EITHER direction, a favourable
move included**, because a gain on the three datasets the scale audit CLEARS means the
lever is not scale-specific and the mechanism story is wrong;
**(c) SANITY (absolute noise floor)** the scored arm fails to beat the certified batch-0
champion skills by more than each dataset's `min_claimable_effect`, i.e. skill must be
`<= 10.359901` pfc (11.511001 − 1.151100), `<= 14.700664` allen_cahn (16.334071 − 1.633407),
`<= 4.980119` cahn_hilliard (5.533466 − 0.553347), `<= 3.759620` fisher_kpp
(4.177355 − 0.417735), `<= 4.122329` helmholtz (13.817290 − 9.694961);
**(d) MECHANISM (instrumented)** the pfc gain arrives WITHOUT `damage_share`
(`tools/registration_skill_split.py`, same shipped per-sample columns) falling from A0's
**0.098** to `<= 0.05`, or with `pct_copylf_error_removed_model` on the neutral three moving
by more than 2 points — either pattern means the arm bought its number by re-learning more
of the `(r-1)/2` resampling convention rather than by ceasing to damage samples copy-LF
already had exact.
`ext__helmholtz_2d` is REPORT-ONLY throughout (rescaled floor 0.701654 admits no
fine-grained claim, ADR 0002 handling); every number is `provisional-single-seed` (ADR 0004);
A3 (ORACLE, true scale) and A4 (gate) are `ref_*` splits, never leaderboard-eligible, and
the ADR-0007 screen numbers appear only in `build_notes`.
**PRE-REGISTERED WELL-FOUNDED NEGATIVE** (card part 4, quoted from
https://arxiv.org/html/2604.20061v1): *"A network trained with mean-squared error converges
to the conditional expectation ... The resulting prediction is over-smoothed by construction,
and no architecture or training procedure can recover information the coarse representation
discards."* Combined with B2 F1 (pfc's node-aligned free fix reaches 7.1e-06, i.e. the pfc
ladder carries NO fidelity gap) and F6 (its bottom decile's residual is numerical roundoff,
which per-sample normalisation would up-weight by `1/s_i^2` — the risk s7_loss-B1 M6 rule (1)
names and the q25 floor mitigates), a clean failure of leg (a) with legs (b)-(d) intact is a
RESULT — "the target-scaler defect is real but unexploitable on a degenerate ladder" — not a
failed card.

### Prior-art verdict quoted (verbatim, `websearches/s2_beyond_copy/batch_3/report.md`)

> **(D1)** Per-sample (instance-wise) normalization of the **fidelity-residual target**,
> replacing the family's single global `max|HF−LF|` scaler, on the same `lf_resid_fno`
> substrate | **preempted-but-MF-composition-open** | DiSOL "magnitude decoupling": "We
> define a per-sample amplitude u_lim"; "u_h := U_h / u_lim, so that max_x |u_h(x)| = 1";
> "an optional amplitude regressor" — https://arxiv.org/html/2601.09143v1 (`iteration_4.md`).
> QuadNorm: per-sample stats standard in operator **feature** norm layers, "not inputs or
> targets", no global-vs-instance ablation — https://arxiv.org/html/2605.07375
> (`parallel_run_b_iterations.md`). RevIN critique: instance norm/denorm standard, time
> series only; "training ... in the normalized space yields better models" —
> https://arxiv.org/html/2603.11869 (both runs). RMFNN: MF residual scale treated globally,
> **no** training-time scaling factor, "no discussion of per-sample or instance-wise scaling
> of residuals" — https://arxiv.org/html/2310.03572 + https://ar5iv.labs.arxiv.org/html/2310.03572
> (`iteration_3.md`, `iteration_2.md`) | (i) instance-wise normalization of the **fidelity
> residual `HF−LF`** (DiSOL normalizes the solution); (ii) the **scale must be predicted from
> `(X, LF)` at test time** — it is not observable — for which DiSOL's amplitude regressor is
> the citable precedent; (iii) the **ESS diagnosis** (89.2 % of MSE energy in 1 of 400
> samples, ESS 1.2; pfc max/median per-sample ‖r‖ = 8.2e4) as the stated cause ...;
> (iv) scoring it against a node-aligned no-learning reference

And for the non-promotable arms:

> **(D2)** Per-sample **no-harm trust gate** ... | **preempted (cite)** at protocol/mechanism
> level ... **Do not claim the gate as a mechanism** — claim the measurement (oracle geomean
> 0.3803 → 0.2590; helmholtz 4.136 → 0.675) and cite 2603.14623 for the calibration recipe

> **(D3)** Report the node-aligned (variant C/D/E) **registration-corrected reference** as a
> secondary column ... | **novel** as a benchmark-hygiene finding — but diagnostic/reporting
> only; the round-1 metric is frozen (program.md §5 immutables 2-4)

> **(D4)** Tail-aware / hard-sample reweighting of the residual objective ... | **preempted
> (cite), with a published NEGATIVE result — treat as pre-falsified-adjacent** ...
> **This is the reason to prefer D1 (normalize) over D4 (reweight).**

D4 appears in NO arm. D5 (`modes_cap`) is left to s5_tuning's audited knob F22.

### Cross-stream separation from s5_tuning-B2 (required statement)

s5-B2's `MFFP_TARGET_SCALER=zscore` is a per-**DATASET** affine (mean/std over the whole
train split) on the LF-blind champion `mf_fno_transfer_film` over the 6-dataset panel. It
moved `ext__helmholtz_2d` 13.817 -> 5.766 and `ifc_poisson` 1.566 -> 1.185 (beyond its
0.240 floor) and left all four sharp sets INSIDE their floors (pfc 11.511 -> 11.216,
allen_cahn 16.334 -> 16.643, cahn_hilliard 5.533 -> 5.458, fisher_kpp 4.177 -> 4.219).
This card's lever is per-**SAMPLE**, on the fidelity-residual target, on the LF-consuming
`lf_resid_fno` substrate, over the 5 beyond-copy sets. **Distinguishing result pattern**:
a per-dataset scaler *cannot* move pfc (the defect there is within-dataset spread, 8.24e4),
so — pfc moves >= 20 % => the effect is genuinely per-sample and the two findings are
distinct levers; — only helmholtz moves and pfc does not => both streams have found the same
dataset-level amplitude channel (already reported by s5) and s2 adds no new lever; — all
five move => leg (b) fires and neither story survives. **Composition, not collision**:
disjoint substrates, disjoint dataset sets, disjoint knob namespaces (`S2B3_*` vs
`MFFP_TARGET_SCALER`), so a merged follow-up card is literally the product
`MFFP_TARGET_SCALER=zscore` x `S2B3_TARGET_NORM=per_sample_maxabs`; nothing here forecloses
that, and the per-sample block is written as an env-switchable target-normalisation module
so s5 can lift it.

### Immutables self-check — **pass (10/10)**

1. **Data read-only** — the card reads `benchmark_42` splits exclusively through
   `round1/eval/panel_data.py::load_split` / `copylf_prediction` (the vendored family's
   existing call sites); no generator is invoked, N_hf per dataset is whatever the split
   ships, and the family's existing tripwire (`smoke_eval.py:484-489`) hard-stops unless the
   LF fidelity's native grid is strictly coarser than HF, so LF can never be downsampled HF.
2. **Panel + guard set fixed** — `recipe.datasets` is byte-identical to B2's five-dataset
   string and to `state/anchors/s2_beyond_copy.json.datasets`; the guard set enters only via
   `S2B3_SCREEN_DATASETS=beyond_copy5,guard` at contract tier, the same legs B2 ran.
3. **Eval layer / spec untouched** — every deliverable lives in
   `<worktree>/models_r1/s2_resid_amplitude_norm/` + `scripts/`; scoring is invoked through
   `round1/eval/score_panel.py` unmodified; the two analysis tools
   (`registration_skill_split.py`, `target_scale_spread_audit.py`) already exist in
   `round1/tools/` (promoted by B2 part 6) and are read-only callers of `panel_data.py`.
4. **One nRMSE definition** — the scored path is `score_panel.py` -> `eval/nrmse.py`; the
   family already asserts `copylf_baselines.json["_nrmse_def_hash"] == NRMSE_DEF_HASH` and
   hard-stops otherwise (`smoke_eval.py:492-494`). The training loss changes (MSE in a
   per-sample-normalised space) — explicitly permitted by §5 "training loss is free; the
   SCORED metric is not".
5. **Contract CLI fixed** — `smoke_eval.py` keeps the 6-arg signature
   (`--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`); every new behaviour is
   reached through the `S2B3_*` env knobs listed above, all of which are in `recipe.env` and
   therefore in the cache key.
6. **Seeds {0,1,2} and tier epochs fixed** — `seeds: [0]` (ADR 0004 strict single seed),
   `epochs: 200` (smoke tier), screen at `S2B3_SCREEN_EPOCHS=2` (contract tier); the scale
   predictor shares the same `--seed` and the same 200-epoch budget; no full-tier run.
7. **Guarded factory surfaces untouched** — the base is vendored by COPY out of the B2
   worktree (`worktrees/s2_beyond_copy/B2/models_r1/...`), which is round-1 territory, not
   `factory_root/{eval,baselines,references,scripts,data}`, not `factory.md`, not
   `mf_field/akash/**`; the only factory import is the read-only
   `data_adapters/loaders.py` path the family already uses.
8. **Checkpoint-resume** — the family's existing periodic `<ckpt_dir>/last.pt` save/restore
   is retained and extended to carry `(arm, stage, epochs_target, grid)` plus the scale
   predictor's weights and the frozen `q25` floor, so a preempted job resumes both networks
   from one file.
9. **Falsification threshold vs the noise floor (all cited datasets)** — pfc: 20 % relative
   = 27.9x the rescaled seed spread `0.082643/11.511001 = 0.007180` and 2x the 10 % pfc
   reproducibility band; allen_cahn: 15 % = 173x `0.014150/16.334071 = 0.000866`;
   cahn_hilliard: 15 % = 4.33x `0.191827/5.533466 = 0.034667`; fisher_kpp: 15 % = 6.83x
   `0.091789/4.177355 = 0.021973`; leg (c) uses the raw `min_claimable_effect` values
   1.151100 / 1.633407 / 0.553347 / 0.417735 / 9.694961 in absolute skill units;
   `ext__helmholtz_2d` carries NO numeric claim (its rescaled floor is 0.701654 = 70 %).
10. **Not a pre-falsified lever** — nearest §5 entry is **LF low-mode freezing**
    (`mf_fno_spectral`, "worst on sharp"): that lever manipulates which spectral BANDS the
    model may use; this card changes only the amplitude by which the residual target is
    normalised, holds `modes_cap = 12` fixed at the B2/champion value, and touches no band.
    The WNO backbone swap (no backbone change here) and the diffusion prior (no generative
    component) are unrelated. Adjacent in-repo negative, cited and differentiated in part 3:
    s7_loss-B1's per-sample-normalised *objective* cratered allen_cahn/helmholtz — this card
    differs by (i) normalising the residual TARGET, not the loss, (ii) `lambda = 1` (no gain
    weight, the ingredient s7-B1 M1 proved pathological), (iii) a q25 denominator FLOOR
    (s7-M6 rule 1), (iv) no LF-pretrain stage (s7-M6 rule 4). Also NOT proposed: D4
    reweighting (fetched negative, https://arxiv.org/html/2605.16078).

- **Anchor reference**: `null` (gap stream; program.md §4.5 — the own-stream anchor
  `skill 1.0 = copy-LF` is implicit).
- **Source iteration**: [iteration_1.md](iteration_1.md)

## Reopen candidates

| Candidate | Verdict (retry/drop) | Eased conditions | Source iteration |
|---|---|---|---|
| *(none — no card in `experiment_cards/**` carries `reopen_candidate: true`)* | n/a | n/a | [iteration_1.md](iteration_1.md) |

## Skipped slot

None — the slot is filled.

## Summary table

| Slot | Category | One-liner | Status |
|---|---|---|---|
| B3 | `mf_composition / target-normalisation repair` | Per-sample amplitude normalisation of the fidelity-residual target on the frozen `lf_resid_fno` substrate, with the test-time scale PREDICTED from `(X, LF)`, pre-registered as a 2x5 asymmetry (pfc primary; helmholtz report-only; allen_cahn / cahn_hilliard / fisher_kpp NEUTRAL), with an ORACLE true-scale headroom column and a non-promotable no-harm-gate column | filled |
