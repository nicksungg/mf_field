# iteration_1 — s6_local-B2 design

## 1. Design context considered

**Unknowns driving the design** (summary_so_far section 6): items 1-8. The three that decide the
shape: (a) the target residual `R` has essentially uniform boundary density (1.024-1.045), so F10's
45-81% boundary error concentration is a model handicap, not a hard region; (b) the four sharp
datasets are on proper periodic grids (wrap-continuity ratio 0.99-1.02) while the guard set is not
(2.6-16.5), so circular padding can be switched on by a *data-driven* criterion; (c) at B1's skill
levels the certified floors must be read relatively.

**Prior-art verdict** (websearches/s6_local/batch_2/report.md, ## Prior-art verdict): row (iii) is
the only open surface — "A **data-driven, physics-free, per-SAMPLE scalar, fitted out-of-fold,
deciding whether a FIELD-VALUED defect corrector is applied at all, with the scored copy-LF field as
the exact fallback** appears in no fetched source." Rows (i), (ii), (iv) are preempted and become a
scored control, a cited bug fix, and a one-sentence protocol note respectively. Row (v) is a control.

**Immutables block (program.md section 5, verbatim, held in view throughout)**

> 1. **Data is read-only.** `benchmark_42/**` and `factory_root/data/**` untouched; no regeneration,
>    no extra HF samples; N_hf per dataset fixed; LF is always the real coarse solve (never
>    downsampled HF — repo law).
> 2. **The panel and guard set are fixed** for the round (section 2.3).
> 3. **The eval layer is byte-untouched during the round.** No agent edits `round1/eval/`,
>    `project.yaml`, `program.md`, ADRs, or subagent prompts. Blocked? Write `state/blocked.md` and
>    auto-skip (it is a log, not a queue).
> 4. **One nRMSE definition** (section 2.1).
> 5. **Contract CLI fixed**: families expose the factory `smoke_eval.py` signature; env knobs allowed
>    ONLY if recorded in the card `recipe` (they enter the cache key).
> 6. **Seeds {0,1,2} and per-tier epoch budgets fixed** (section 2.4).
> 7. **Guarded factory surfaces never edited**: `factory_root/{eval,baselines,references,scripts,data}/`,
>    `factory.md`, `mf_field/akash/**`.
> 8. **Checkpoint-resume mandatory**: training resumes from `<ckpt_dir>/last.pt` (the SLURM partition
>    can preempt).

Pre-falsified levers (section 5): WNO backbone swap; LF low-mode freezing (`mf_fno_spectral`);
diffusion prior for point accuracy. Nearest to this card: **LF low-mode freezing** — see item (10) of
the self-check.

**Anchor and floors.** `anchor_reference = "s6_local-B1"` (batch->=2 policy in the task brief;
program.md section 4.5 reserves `null` for own-stream-implicit cases, and B1 used `null`). B1's
provisional-single-seed geomean **0.234572**. Certified floors (`state/noise_floor.json`), expressed
relatively because every arm sits at skill 0.01-0.5: `min_claimable_effect / mean_skill` = pfc
**10.000%**, allen_cahn **10.000%**, fisher_kpp **10.000%**, cahn_hilliard **10.000%**, helmholtz
**70.165%**, ifc_poisson **15.323%**; pure certified seed spread relative = pfc **0.718%**,
allen_cahn **0.087%**, fisher_kpp **2.197%**, cahn_hilliard **3.467%**, helmholtz **70.165%**.
Geomean floor 0.8836555 / 6.703016 = **13.183%**. Convention (B1 part-5 layer-2 precedent, accepted
by the initial analyzer): cross-*arm* skill claims use the 10% `min_claimable_effect` reading; a
*paired within-corrector* selection contrast (identical checkpoint, identical split, only a post-hoc
selection stage differs) uses the pure seed spread. Every clause below names which it uses.

**ADRs.** 0004 strict single seed (all numbers `provisional-single-seed`). 0005 H100 + `--time`.
0007 propose-many: reconciled as a **sweep** exactly as `s1_poisson-B2` did — the arms ARE the
contrasts, all are reported, primaries fixed before submit, plus one contract-tier plumbing screen
whose numbers are never reportable. 0009: the trust head must be physics-agnostic; ANCHOR's
residual-based estimator is disqualified, so every head feature is a statistic of `X`, of the LF
field, or of the corrector's own output.

## 2. Proposal reasoning

### 2.1 Card shape: repair-and-control on the B1 substrate

B1 part 7 `next_direction` opens with "s6-B2 should be a CONTROL-AND-REPAIR card on the same family,
not a new architecture, and it must carry the closed-form filter as a scored arm", and closes with
"Do NOT spend a batch on capacity, depth, receptive field or modes". The websearcher agrees on all
five items. I therefore did **not** consider new architectures. Rejected alternatives:

- *A new hybrid composition (e.g. spectral+local two-branch)*: rejected — it is capacity spend, the
  stencil measurement (F15: 94-99% of the optimal operator's energy inside 12 cells, radius_50pct
  1.4-3.0) says receptive field is already sufficient, and B1's open question (is there any neural
  content at all beyond `T(k)`?) must be answered before more network is bought.
- *Chasing cahn_hilliard's low band*: rejected — B1 M5 hands it to `s3_warp` with a quantified
  displacement signature; duplicating it here wastes the batch.
- *helmholtz-first card built on the per-sample oracle*: rejected as the card's headline because
  helmholtz's certified floor is 70.165% relative — no numeric claim is possible there under any
  design. It stays as a report-only mechanism leg.
- *Screen-and-promote (ADR 0007's default)*: rejected in favour of the sweep, because four of the five
  arms are **controls whose value is being reported, not selected** (a discarded control is a lost
  measurement). Same reconciliation `s1_poisson-B2` recorded.

### 2.2 The padding repair, and why its size is predictable

The mechanism is now fully identified and it is *not* only "convolutions need periodic padding":
`eval/panel_data.py::copylf_prediction` upsamples with `scipy.ndimage.zoom(..., order=1,
grid_mode=True, mode="nearest")`, which is **not periodic**, so copy-LF itself carries a wrap seam.
Measured (my probe, HF vs LF_up wrap-jump / interior-jump RMS ratio, 32 train samples):

| dataset | HF ratio y / x | LF_up ratio y / x |
|---|---|---|
| pfc | 1.0152 / 0.9908 | 4.1191 / 3.9286 |
| allen_cahn | 0.9906 / 1.0210 | 3.9283 / 4.1764 |
| fisher_kpp | 0.9988 / 0.9871 | 3.9912 / 3.8904 |
| cahn_hilliard | 0.9998 / 1.0003 | 4.0014 / 4.0007 |
| helmholtz | 0.3478 / 0.8585 | (interior jump 0 -> undefined) |
| heat_local | 10.6358 / 16.5482 | 15.8690 / 19.6506 |
| fluid | 2.5563 / 1.2146 | 6.9243 / 5.0490 |

So on the four sharp datasets the truth is periodic and the *base prediction* has a 4x seam
discontinuity that the corrector must repair — while zero padding forbids it from seeing across that
seam. The eval layer is immutable (section 5.3): the model fixes it, we do not touch `panel_data.py`.

Size prediction, from F10's shares plus my new measurement that the target `R` is boundary-uniform
(12-cell band energy density ratio 1.043 pfc / 1.045 AC / 1.041 FK / 1.024 CH): if the repair brings
the boundary band's error density down to the interior density, remaining squared error falls to
0.2893 (pfc) / 0.3680 (AC) / 0.6666 (FK) / 0.9952 (CH) of B1's, i.e. **nRMSE -46.2% / -39.3% /
-18.4% / -0.2%**. Label: *ideal-repair upper bound from energy-share arithmetic* (assumes the repair
is complete and adds nothing elsewhere); the honest expectation is roughly half of it. Even at half,
pfc (-23%) and allen_cahn (-20%) clear the 10% floor by 2x; fisher_kpp (-9%) does not, so fisher_kpp
and cahn_hilliard are **reported, not claimed**.

Data-driven periodicity switch (no physics, ADR 0009): `S6_PAD_MODE=circular_if_periodic` computes
the HF-train wrap-continuity ratio and uses `padding_mode="circular"` iff `max(ratio_y, ratio_x) <=
S6_PERIODIC_TOL=1.25`, else `zeros`; the measured ratios and the decision go into the diag sidecar.
Predicted decisions: circular on pfc / allen_cahn / fisher_kpp / cahn_hilliard / helmholtz (0.859,
where the field nearly vanishes at the boundary so circular ~ zeros), zeros on heat_local / fluid,
and `sharp__sod_1d` collapses to a 1-cell kernel in H already (`odd_kernel`).

### 2.3 The LSI control arm: a floor, not a method

Written as a **scored control with zero method novelty**, exactly as the verdict demands. One
transfer function `T(k) = sum_n R_hat LF_hat* / sum_n |LF_hat|^2` fitted on the family's own
`fit_idx` (the same 320 samples the trained arms use, same `torch.randperm` seed -> paired), the
scalar switch selected by the family's own `fit_alpha` on `val_idx` (candidate set contains 0), and
`pred = LF_te + alpha * T*LF_te` scored through `score_panel.py`. Vendored into the family as
`lsi_filter.py` (adapted with citation from `tools/defect_correction_learnability.py`, itself
promoted from B1 turn 2/3) rather than imported from `tools/` — importing spec-surface code would
put logic outside the family `code_hash` and silently poison the eval cache.

Reproduction validity gate (`S6_LSI_F6_TOL=0.02`): the arm must reproduce B1 F6's test nRMSE within
2% relative — pfc **0.0006124685**, allen_cahn **0.0008319634**, fisher_kpp **0.0076950811**,
cahn_hilliard **0.0385687516** (`worktrees/s6_local/B1/scratchpad/turn2_lsi_*.json`,
`A_lsi_ceiling.nrmse_LSI_transfer_only`), with `S6_LSI_RIDGE=0` to match turn 2 (the promoted tool
defaults to ridge 1e-6 and a different permutation, which is why its numbers differ by 1-9%). On
helmholtz the held-out switch is expected to select **alpha = 0** (F14; tool
`heldout_trust_switch_alpha` 0.0), making the prediction bit-equal to copy-LF -> skill 1.000.

Predicted LSI panel geomean **0.19722** (skills 1.000000 / 0.013677 / 0.051509 / 0.122861 / 0.439981
/ 1.545326) = **15.92% below B1's 0.234572**, above the 13.183% geomean floor. That is the batch's
sharpest possible statement and it is *pre-registered before the run*: the round's best panel number
may have zero trained parameters. Leaderboard eligibility of a zero-parameter arm is **flagged to the
operator, not decided here** — s2-B1's `do_not_promote` rule was written for training-free *lookup*
(retrieval), and this is a train-fitted predictor; the card reports it either way.

Cross-stream boundary, stated explicitly per the task brief: `s2_beyond_copy-B2` owns the *trained*
LF-residual FNO control and the *retrieval* floors; this arm is neither — closed-form, zero trained
parameters, no gradient steps, no neighbour lookup.

### 2.4 The per-sample trust head (the one open surface)

Construction, fully specified so the builder has no freedom:

- Stages 0-2 are **B1's, unchanged**, with `S6_PAD_MODE=circular_if_periodic`: corrector fitted on
  `fit_idx`, pixel gate (in-sample, as-was, worth <=0.63% so it preserves pairing).
- Stage 3' replaces B1's single held-out scalar. On `val_idx` (n=80; never seen by stages 0-2 ->
  Wolpert 1992 satisfied, cited via https://arxiv.org/pdf/1106.1684):
  1. per-sample closed-form optimum `a*_i = <R_i, C_i> / ||C_i||^2`, clipped to [0, 1.5];
  2. features `phi_i` — **physics-free by construction**: `X_i` (cond vector, dim<=10); `log||LF_i||_2`;
     `log(||grad LF_i||_2 / ||LF_i||_2)` (finite differences, roughness); the 4 log band-energy
     fractions of `LF_i` on the round's band grid; `log(||C_i||_2 / ||LF_i||_2)`; the 4 log
     band-energy fractions of `C_i`. All computable at test time from the LF field and the model's
     own output; **no PDE residual, no operator, no free energy** (ADR 0009; ANCHOR is disqualified
     precisely because its estimator is the residual). Standardized with `val`-slice moments.
  3. ridge regression `a_hat(phi)`, `lambda` from `S6_HEAD_RIDGE_GRID=1e-3,1e-2,1e-1,1,10`;
  4. **selection by 4-fold CV inside `val_idx`** (`S6_HEAD_CV_FOLDS=4`): candidates = {per-sample head,
     B1's global held-out scalar, 0}; winner = lowest mean fold rel-L2, and the head wins only by
     `S6_HEAD_MIN_GAIN=1e-3` over the better of the other two; then refit the winner on all 80.
  5. prediction `y_hat_i = LF_i + clip(a_hat_i, 0, 1.5) * C_i`; `a_hat == 0` reproduces copy-LF exactly.
- **Pre-registered risk**: per-sample gating trades the *exact* copy-LF no-harm floor for headroom.
  On helmholtz (`rho_val` -0.22457, F5) a head that fires on the wrong samples can score worse than
  copy-LF. Admissible outcome and itself a finding; the candidate set containing 0 and the CV margin
  are the only guards, deliberately.
- Pairing tripwire: stages 0-2 are seed-identical to the `circ_repair` arm, so the corrector weights
  must be bit-identical; the arm emits `corrector_state_sha256` and the builder asserts equality
  across the two arms (`S6_ASSERT_PAIRED_CORRECTOR=1`). This is what makes the trust contrast paired
  and lets it use the pure-seed-spread floor.

Expected size: pfc oracle per-sample is -22.8% (F3), so the achievable head is expected in
**0-10%**; helmholtz oracle 0.16233 vs copy-LF 0.32945 (-50.7%), achievable expected in
[0.25, 0.33] **if** the CV switches the head on, else exactly 0.3294501. Numbers on helmholtz are
report-only (70.165% floor); the mechanism statement there is binary (head selected vs alpha=0).

### 2.5 The Wolpert-fixed per-pixel gate arm: dropped, and why that is the honest call

The task asks for a justification either way. **Drop it as a training arm.** Three reasons, each a
measured number:
1. Ceiling below the floor: the ORACLE per-pixel map (fitted on the test set itself) is worth 4.1%
   (pfc), 1.2% (allen_cahn), 0.6% (fisher_kpp) and **-17% (cahn_hilliard)** — F2. Every one of those
   is below the 10.000% relative `min_claimable_effect` for its dataset, so no possible outcome of the
   arm is claimable; program.md section 4.5 says a claimed effect smaller than the floor is
   unfalsifiable and my own self-check must reject it.
2. The achievable version has already been run: F2 states the val-fitted (i.e. out-of-fold) per-pixel
   gate is *worse* than `g==1` on 3 of 4 datasets. The experiment's informative content exists.
3. The mechanism claim is closable for free. The trust-head arm already holds `C_val` and `R_val` in
   memory, so the out-of-fold per-pixel map `a_pix(x) = sum_i R_i(x)C_i(x) / sum_i C_i(x)^2` over
   `val_idx` costs one numpy expression. It ships as a **measurement-only sidecar**
   (`S6_PIXEL_OOF_SIDECAR=1`, keys `nrmse_pixel_oof`, `nrmse_persample`, `nrmse_global_scalar`), in no
   falsification clause, quoted with the <=4.1% / -17% ceiling beside it. Wolpert 1992 is cited as the
   one-sentence protocol note the verdict allows, and B1's *provable no-op* observation (uniform-gate
   argmin exactly 1.0 on fit/val/test, `J(0)` the maximum — F4) is recorded as the free contrast with
   classic leakage-induced over-confidence.

### 2.6 The owed pointwise control

`pointwise_ctrl` at 200 epochs with `S6_KERNEL=1`, **circular padding** so the contrast against
`circ_repair` isolates locality extent at fixed padding (B1's promoted arm is reproduced by the
`b1_replica` arm for the padding contrast, so nothing is lost). Pre-registered expectation from F7 +
F15: a 1-cell kernel can realise only a pointwise (band-independent) gain plus a pointwise
nonlinearity, while the fitted operator's band gain rises monotonically from 0.117-0.202 (band 0) to
0.960-1.000 (top band) and its radius_50pct is 1.4-3.0 cells. So the K=1 arm should be **>=2x worse
in nRMSE than `circ_repair` on >=3 of the 4** defect datasets. If instead it matches within 10%
relative on >=3, H2's locality content is *pointwise recalibration*, not spatial kernels — a large
finding either way, which is why the control is worth its 18 minutes.

### 2.7 Arms, cost, and what is reported

| tag | padding | variant | selection | role |
|---|---|---|---|---|
| `b1_replica` | `zeros` | `local_pixel_gate` | held-out scalar (B1) | reproduction gate + padding-contrast control |
| `circ_repair` | `circular_if_periodic` | `local_pixel_gate` | held-out scalar (B1) | **PRIMARY** for C1 (padding) and C2 (LSI gap) |
| `lsi_ctrl` | n/a (FFT is implicitly periodic) | `lsi_ctrl` (0 trained params) | held-out scalar | scored zero-parameter floor |
| `trust_head_circ` | `circular_if_periodic` | `local_pixel_gate` | out-of-fold per-sample head, CV-selected | **PRIMARY** for C3 (trust) |
| `pointwise_ctrl_circ` | `circular_if_periodic` | `pointwise_ctrl` (K=1) | held-out scalar | owed locality-extent control |

All five run `--datasets panel` (6 datasets, so the geomean stays comparable with B1 and the anchor;
ifc_poisson takes B1's pre-registered champion no-op fallback, no claim). `circ_repair` and
`lsi_ctrl` additionally run `--datasets guard` at 200 epochs (section 2.3 requires a guard run for a
panel-win claim; B1's analyzer flagged the 2-epoch guard as too weak). Every arm emits `skill_LSI`
in its own diag sidecar (`S6_LSI_SIDECAR=1`) per B1 part-7 cross-stream note 1.

Cost from `state/timing_ledger.json`: B1's 200-epoch 6-dataset panel run was **17.95 min** on H100;
4 trained arms ~72 min, `lsi_ctrl` ~5 min (numpy FFT 2-33 s/dataset + 0.6 min champion fallback),
paired LSI sidecars ~3 min/arm, guard legs ~12 min => **~100 min**; reserve `--time=04:00:00`.
Screen: contract tier, 2 epochs, all five arms, panel+guard — B1's equivalent screen was 8.6 min;
reserve 01:00:00. Checkpoint-resume keyed on `(arm, variant, stage, epochs_target, grid)`.

## 3. Proposal

- **Category**: `mf_composition` / control-and-repair on the B1 defect-correction substrate
  (padding repair + zero-parameter floor + out-of-fold per-sample trust).
- **Card type**: `model`.
- **Motivation** (quotes the verdict): the batch's only open surface is verdict row (iii) — "A
  **data-driven, physics-free, per-SAMPLE scalar, fitted out-of-fold, deciding whether a FIELD-VALUED
  defect corrector is applied at all, with the scored copy-LF field as the exact fallback** appears in
  no fetched source" — while row (i) is "preempted as a *method*, open as a *reported baseline*"
  ("Claim **zero method novelty**; the contribution is the *measured floor*"), row (ii) is
  "`preempted (cite)` — hygiene, not a contribution" whose "only reportable" content is "B1's
  *measurement* that zero padding held **45-81%** of a defect corrector's remaining squared error in a
  12-cell band ... plus the post-repair delta", and row (iv) is "the founding rule of stacking; file as
  a protocol bug fix". B1 part 7 demands exactly this batch and forbids capacity spend.
- **Concrete config**: as section 2.7; family `models_r1/s6_local_repair` vendored from
  `models_r1/s6_local_lf_corrector` @ `3abc0e30d56446148f5322787fbfd1d5f384cc82` with sha256-16 pins
  `bands.py 42b869598fcc864e`, `local_corrector.py dcf531f8207b93a3`, `model.py 80d8940d8b90a4ac`,
  `smoke_eval.py 91ee5a6459609a26`, `manifest.json f336edbecb2de3c7`,
  `INSPIRATION.md ece1c608b492dbe1` (verified by `git show 3abc0e3:<path> | sha256sum`). Code changes:
  (1) `padding_mode` plumbed through `ConvNeXtLiteBlock`/`LocalCorrector`/`PixelGate` (default `zeros`
  = bit-preserving; parameter shapes and init order unchanged, so `b1_replica` is bit-identical to
  B1); (2) new `periodicity.py` (wrap-continuity criterion); (3) new `lsi_filter.py` (closed-form
  `T(k)` + the paired sidecar); (4) new `trust_head.py` (stage 3' + the out-of-fold pixel sidecar);
  (5) `VARIANTS` gains `lsi_ctrl`; (6) score-neutral diag additions
  (`padding_decision`, `wrap_ratio_hf`, `corrector_state_sha256`, `skill_LSI`, `nrmse_pixel_oof`,
  `nrmse_persample`, `nrmse_global_scalar`, `head_selected`, `head_cv_table`). No new scored metric;
  section 2.1 untouched.
- **Recipe**: see report.md (identical JSON).
- **Expected outcome**: `circ_repair` per-dataset nRMSE (ideal-repair upper bound, honest label)
  0.0007229 pfc / 0.0007891 allen_cahn / 0.0048646 fisher_kpp / 0.0409769 cahn_hilliard, i.e. skill
  0.016144 / 0.048854 / 0.077669 / 0.467453, helmholtz 1.000000 (alpha=0 expected), ifc_poisson
  1.545326 -> panel geomean **0.18807** (-19.8% vs B1's 0.234572, above the 13.183% geomean floor);
  realistic mid-case ~half the gain -> geomean ~0.21 (-10%, below the geomean floor, which is why the
  primary clauses are per-dataset). `lsi_ctrl` geomean **0.19722** (-15.9%). `trust_head_circ`: pfc
  0-10% below `circ_repair` (oracle -22.8%), helmholtz report-only in [0.25, 0.33] if the head fires.
  `pointwise_ctrl_circ`: >=2x worse than `circ_repair` on >=3 of 4. Paired post-repair NN-vs-LSI
  ratios: fisher_kpp 0.632 (NN better 36.8%), allen_cahn 0.948 (5.2%), cahn_hilliard 1.062 (LSI
  better 6.2%), pfc 1.180 (LSI better 18.0%) => predicted 1 of 4 clears the 10% margin.
- **Expected falsification** (three contrast clauses + two validity gates, all
  `provisional-single-seed`, ADR 0004):
  - **C1 (padding repair; cross-arm, 10% floor convention).** Falsified if `circ_repair`'s test nRMSE
    is not at least **10% below** `b1_replica`'s on **both** `sharp__phase_field_crystal_2d` and
    `sharp__allen_cahn_2d` (10.000% = each dataset's certified `min_claimable_effect` expressed
    relatively, 13.9x and 115x their pure seed spreads 0.718% / 0.087%); the ideal-repair prediction is
    -46.2% / -39.3%, so the clause is cleared by 4.6x / 3.9x if the mechanism is real.
    `sharp__fisher_kpp_2d` (predicted -18.4%) and `sharp__cahn_hilliard` (-0.2%) are reported, not
    claimed; `ext__helmholtz_2d` (70.165% floor) and `ifc_poisson` (fallback) carry no claim.
  - **C2 (does anything neural survive; cross-arm, 10% floor convention).** H2's *neural* content is
    SUPPORTED only if `circ_repair` beats the paired `lsi_ctrl` arm by **>10% relative nRMSE on >=2 of
    the 4** defect datasets {pfc, allen_cahn, fisher_kpp, cahn_hilliard}; it is REFUTED at <=1, and
    the card's headline becomes the target ("nested-ladder defect correction on top of the real coarse
    solve"), not the operator class. Pre-registered expectation: **REFUTED, 1 of 4 (fisher_kpp only)**.
  - **C3 (per-sample trust; paired within-corrector, pure-seed-spread convention).** The per-sample
    trust hypothesis (B1 F3) is falsified if BOTH (a) `trust_head_circ`'s test nRMSE on
    `sharp__phase_field_crystal_2d` is less than **5% below** `circ_repair`'s (5% is 7.0x pfc's
    certified relative seed spread 0.718%; legitimate because the two arms share a bit-identical
    corrector checkpoint, asserted via `corrector_state_sha256`, and differ only in the post-hoc
    selection stage) AND (b) the 4-fold CV inside `val_idx` does not select the per-sample head over
    {global scalar, 0} on **>=2 of the 5** beyond-copy datasets. `ext__helmholtz_2d` numbers are
    report-only (70.165% floor); its mechanism leg is binary — head selected vs alpha=0 — and a
    helmholtz score *worse* than copy-LF 0.3294501 is an admissible, pre-registered outcome (per-sample
    gating trades the exact no-harm floor for headroom) and is itself a finding.
  - **V1 (validity gate, not a clause).** `b1_replica` must reproduce B1 seed-0 test nRMSE within 10%
    relative on all six panel datasets (0.3294501 / 0.00134416 / 0.00130074 / 0.00595834 / 0.04107603
    / 0.05563172) and the identity path must stay bit-equal to `eval/copylf_baselines.json`. A miss
    means the vendoring changed inherited behaviour: ALGO, fix before reading any contrast.
  - **V2 (validity gate).** `lsi_ctrl` must reproduce B1 F6 within 2% relative (0.0006124685 /
    0.0008319634 / 0.0076950811 / 0.0385687516) and select alpha=0 on `ext__helmholtz_2d`.
- **Anchor reference**: `"s6_local-B1"`.

## 4. Status

- Slot covered: **yes**, one card, `model`, five arms + two guard legs + one contract screen.
- Skipped: no.
- Reopen candidates resolved: none exist (B1 `reopen_candidate: false`) — nothing to retry or drop.
- Dropped-with-reason (recorded so it is an auditable dead end, not a silent omission): the
  Wolpert-fixed per-pixel *training* arm, replaced by a free out-of-fold sidecar (section 2.5).
- Immutables self-check: **pass 10/10** (section 5).

## 5. Immutables self-check (positive evidence, all 10)

1. **Data read-only.** No arm reads or writes any dataset path except through
   `round1/eval/panel_data.py::load_split/copylf_prediction` (the same calls B1 made at
   `smoke_eval.py:341-343`); `S6_LF_SOURCE=dataset_lf_fidelity` and `S6_LF_FID=max` are asserted in
   `read_knobs()` and B1's tripwire (i) raises `S6ContractError` unless the LF fidelity's native grid
   is strictly coarser than HF (verified in the vendored code at `smoke_eval.py:331-340`); N_hf is
   untouched (n_train 400 on the five, 5 on ifc_poisson), no regeneration anywhere in the recipe.
2. **Panel + guard fixed.** `datasets: "panel"` expands from `project.yaml panel:` (6 datasets) and
   the guard legs use `--datasets guard` (`heat_local, fluid, sharp__sod_1d`); no dataset is added,
   dropped, or re-weighted, and the two report-only/no-claim legs (helmholtz, ifc_poisson) stay in the
   geomean exactly as in B1.
3. **Eval layer / spec untouched.** Every code change listed in section 3 lives under
   `models_r1/s6_local_repair/`; the LSI logic is *vendored into the family* precisely so that
   `tools/` and `round1/eval/` need no edit, and the copy-LF wrap seam I found in
   `panel_data.py::copylf_prediction` is handled by the *model* (circular padding), with the card
   explicitly refusing to touch the eval layer.
4. **One nRMSE definition.** Every scored number comes from `score_panel.py` -> `eval/nrmse.py`
   (`nrmse_def_hash` d3d0ade9191c13bacc40702f3eb26ad290e01641cacee22a1d2233b74c035850, the hash on
   B1's result JSONs); all new quantities (`skill_LSI`, `nrmse_pixel_oof`, `nrmse_persample`,
   `head_cv_table`, wrap ratios) are diag-sidecar keys computed with the same `round_nrmse` helper and
   enter no scored split.
5. **Contract CLI fixed.** `smoke_eval.py` keeps the six-argument signature
   (`--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`) inherited byte-for-byte from the
   pinned `91ee5a6459609a26`; every new knob is an `S6_*` env var and all of them are listed in the
   recipe `env` block, so they enter the eval cache key.
6. **Seeds and epochs fixed.** `seeds: [0]` and `epochs: 200` (smoke tier) for all five arms and both
   guard legs; the only 2-epoch usage is the contract-tier plumbing screen, whose numbers are
   explicitly non-reportable (ADR 0007); no 2500-epoch run is requested.
7. **Guarded factory surfaces untouched.** The vendoring command is
   `git checkout 3abc0e3 -- models_r1/s6_local_lf_corrector` inside the B2 worktree followed by
   `git mv` to `models_r1/s6_local_repair`; no path under `factory_root/{eval,baselines,references,
   scripts,data}/`, `factory.md`, or `mf_field/akash/**` appears anywhere in the recipe, and the base
   family's `model.py` stays the byte-identical copy of `mf_fno_transfer_film/model.py` @ 967562e.
8. **Checkpoint-resume.** Inherited from the pinned `smoke_eval.py` (`_save_ckpt`/`_load_ckpt`, mirror
   write to `<ckpt_dir>/last.pt` at `smoke_eval.py:471-476`), with the meta guard extended to
   `(arm, variant, padding_mode, stage, epochs_target, grid, seed)`; stage 3' (the head) is fitted
   after the `stage="done"` write and is deterministic given the checkpoint, so a preempted arm
   resumes without retraining.
9. **Falsification thresholds exceed the noise floor, numbers quoted.** C1 uses **10.000%** relative
   on pfc and allen_cahn = each dataset's certified `min_claimable_effect` (1.1511001 / 11.511001 and
   1.6334071 / 16.334071), which is 13.9x and 115x their pure certified seed spreads (0.718% /
   0.087%); prediction -46.2% / -39.3%. C2 uses the same 10.000% relative margin on the four defect
   datasets (floors 10.000% each; pure spreads 0.718 / 0.087 / 2.197 / 3.467%). C3 uses **5%** on pfc
   = 7.0x its pure certified seed spread 0.718%, legitimate only because the contrast is paired on a
   bit-identical corrector (asserted). Every dataset whose floor cannot be cleared carries **no
   numeric claim**: `ext__helmholtz_2d` (70.165%) and `ifc_poisson` (15.323%, fallback leg). The
   geomean bar, where quoted, is 0.8836555 / 6.703016 = **13.183%** relative and the prediction is
   -19.8% (`circ_repair`) / -15.9% (`lsi_ctrl`).
10. **Not a pre-falsified lever.** Nearest is **LF low-mode freezing (`mf_fno_spectral`: "worst on
    sharp, catastrophic on lid-cavity")**, which also touches per-band treatment of the LF field. The
    differences: `mf_fno_spectral` *froze* LF low modes inside a generative FNO whose output replaced
    the LF field, whereas here the base prediction **is** the real coarse solve, nothing is frozen or
    discarded, the correction is additive with a held-out switch whose candidate set contains 0 (exact
    copy-LF recoverable), and the only band-wise object is a *diagnostic* profile plus the closed-form
    `T(k)` control that B1 measured to *rise* monotonically to 1.0 (F7) instead of suppressing modes.
    The other two pre-falsified levers (WNO backbone swap; diffusion prior) share no component with
    this card: no backbone swap, no generative prior. Guard-set relevance also differs — the lid-cavity
    catastrophe is addressed head-on by the 200-epoch guard legs plus B1 F16's pre-claim (`fluid`
    held-out rho 0.4732, non-compact operator) and the periodicity criterion keeping `fluid` on zero
    padding.
