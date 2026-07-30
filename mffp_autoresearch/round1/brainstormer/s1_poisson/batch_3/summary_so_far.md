# Summary so far — Stream `s1_poisson`, Batch 3

Every claim below is quoted or transcribed from a file read in this run; paths
are relative to `${ROUND_ROOT}` = `mffp_autoresearch/round1/`.

## 1. Websearch findings + prior-art verdict (batch 3)

Source: `websearches/s1_poisson/batch_3/report.md` (5 iterations, 15 searches,
12/12 fetches usable; ar5iv route recovered the benchmark paper's body).

Verdict rows that bear on this slot, **verbatim**:

- **(i)** "Ladder-pooled per-sample **gain head** g(X) on the frozen
  `allpairs__per_level` base -- head fitted on the **175 pooled ladder rows**
  (supervision = the frozen operator's residual at levels 8/16/32), applied at
  fidelity 64 where N_hf = 5 | **`preempted-but-MF-composition-open`** | ROMES:
  GP from cheap indicators to the error distribution; "correcting the
  reduced-order-model output with this surrogate can improve prediction accuracy
  by an order of magnitude" -- https://arxiv.org/abs/1405.5170 . LR-MFS: scale
  factor by least squares **on HF samples** -- https://arxiv.org/abs/1705.02956 .
  IFC: "latent output as a continuous function of the input and fidelity ...
  multiplied with a basis matrix" (g(X) = the K=1 case) --
  https://ar5iv.labs.arxiv.org/html/2207.00678 (+ 1609.07196v5 rho(x),
  MF-POD coefficient regression, APEX amplitude anchor) | **What remains open**:
  Fitting the calibration law **on auxiliary fidelity levels of the same ladder,
  supervised by the frozen operator's own residual there, and transferring it to
  the top level at N_hf = 5**. Every fetched MF scale estimator fits against
  **HF** observations ... Frame as a **measured MF composition of published
  parts**."
- **(ii)** exact construction = "**`novel` (narrow, weak)** -- say "not previously
  reported", never "novel method"". "**But the transfer assumption is the
  experiment**, and the literature's prior is against it: recursive co-kriging
  fits **a separate rho per level** and "Different fidelity levels have distinct
  parameter estimates" (search-return, iteration_2)".
- **(iii)** "**0.018 is ODE2 at 128^2 extrapolation**, i.e. a different task from
  our 64^2 test split, and it is not GPODE's -- contra
  `docs/adr/0002-ifc-poisson-skill-reference.md`. ADRs are immutable in-round:
  keep 0.036 as denominator, cite this, and route the correction to the operator
  as a written note. **Structural gap**: IFC = per-sample fidelity-continuous
  latent coefficients x shared fidelity-varying bases under one joint likelihood;
  the base has the joint training but **no per-sample coefficient factor**. g(X)
  is its rank-1 amplitude-only case; a K>1 coefficient head with fixed bases is
  the indicated batch-4 successor, not a batch-3 scope creep."
- **(iv)** LOO headroom 0.02431 = "**`preempted` methodological warning -- report
  as an upper bound only**"; small calibration sets "can still lead to poorly
  calibrated models **because of overfitting**".

Directives in that report's "For the brainstormer": name ROMES in `prior_art`;
use the IFC "no per-sample coefficient factor" sentence as motivation and cap
scope (K>1 head = batch 4); **report the fitted gain law's coefficients per level
(8/16/32 separately) as score-neutral instrumentation -- "That single table
decides the mechanism regardless of whether the nRMSE clause fires, and it is
cheap"**; regularize the head and choose the regularization strength **without**
test targets; "The whole available effect is 0.0099-0.0113 nRMSE against a
**0.0086367** floor (~1.15-1.31x) -- quote both numbers in the same sentence and
say plainly that a null result is the likely outcome and is still informative";
state explicitly that the card is **not** REEF-GP and **not** PDE-residual
correction at inference; a *learned* scale head is architecture, not a knob, so
it belongs in s1's model card and not s5's.

## 2. `program.md` §12.1 conventions -- verbatim

> ### 12.1 `s1_poisson` (gap)
>
> - **Bar**: paper 0.036 (IFC-ODE2); stretch IFC-GPODE 0.018. Current best zoo:
>   0.042 (`mf_fno_pinn_transfer`, factory bench). Anchor: `state/anchors/s1_poisson.json`.
> - **N_hf = 5.** Every claim is anecdote-grade by sample count; the CI + noise
>   floor conventions are the only defensible reporting. Prefer designs that
>   reduce variance (ensembling across seeds, all-pairs training) or add
>   information (physics residuals) over designs that add capacity.
> - Batch-1 seed direction: **all-pairs fidelity training** applied to the gap --
>   `mf_field/akash/models/mf_fno_allpairs` was the mentor's best on the hard
>   subset (gm 0.0094 vs FiLM 0.0121, FINDINGS.md); its known failure is
>   O(L^2) pair cost on many-level datasets (era5 timeout) -- irrelevant here
>   (ifc ladder L=4).
> - Physics fact: Poisson is elliptic with global coupling; the IFC papers'
>   ODE/GPODE methods exploit the fidelity-ladder structure directly.

Anchor (`state/anchors/s1_poisson.json`): `value` 1.5656334312786022 skill
(= 0.056363 nRMSE), 3-seed certified, `provisional: false`.
Noise floor (`state/noise_floor.json`, `ifc_poisson`): `min_claimable_effect`
**0.23990756041925798** skill units = **0.0086367 nRMSE**.

## 3. Within-stream prior cards

`experiment_cards/s1_poisson/batch_1/B1.json` -- status `complete`,
`reopen_candidate: false`. The 2x2 precursor; measured that 74.73 % of its
primary arm's squared test error was removable by a per-sample scalar gain, and
that its level-set contrast was measured *through* a normalization defect.

`experiment_cards/s1_poisson/batch_2/B2.json` -- status `complete`,
`reopen_candidate: false`, `anchor_reference: null`, family
`models_r1/mf_fno_ladder_norm`, `build_commit`
`21fdcdade463a4ceebb52a80d329790d8a401af7`, 5 arms in ONE H100 job (66008912),
**5.6 min total**, seed 0, `nrmse_def_hash d3d0ade9...`.

Part 5 (parsed from `score_panel` JSONs): `allpairs__per_level` (PRIMARY)
**0.034250020008724666 nRMSE / skill 0.9513894446867965** -- the round's first
sub-paper-bar ifc_poisson number; `two_level__per_level` 0.07854787;
`two_level__shared` 0.10266942; `allpairs__shared` 0.20934890;
`allpairs__shared_reweight` 0.21859201. Both pre-registered clauses
**confirmed** (F1 20.27x floor, F2 5.13x floor); B1-continuity gate passed by
250x margin; not cratered. Guard set **owed at confirmation**, mitigated because
the family default `shared` is bit-preserving; a contract-tier guard run exists
(`result_guard_allpairs_per_level_s0.json`, e2: heat_local 0.005755, fluid
0.312326, sharp__sod_1d 0.026013 -- plumbing, not a claim).

Part 6 facts this slot depends on:
- "of the winning arm's remaining 0.034250, **57.10 %** of the squared error is
  STILL per-sample amplitude: the per-sample oracle gain gives **0.022917**
  (skill 0.6366) while ONE global oracle gain gives **0.03511** (no help).
  Residual gain: mean 0.99307, std 0.03046, range [0.90123, 1.03765]. That gain
  is nearly linear in the 5-D condition vector -- leave-one-out ridge on [1, X]
  R^2 = **0.9190** -> nRMSE **0.02431** (skill 0.6752) ... HEADROOM LABEL: the
  LOO fit uses the test targets, so 0.0243 is an upper bound on a calibration
  head, not a score."
- Error is **bulk-dominated** (error falls monotonically from smoothest to
  steepest |grad HF| decile; 99.78 % of target energy in radial band 0) and
  `f_src` is **measurably inert** at inference (rel-L2 0.0089 sweeping it 0->1).
- Ruled out **by measurement** for this dataset: interface-aware losses,
  local/CNN branches, LF-consuming defect correctors (not expressible: no LF in
  the test split; train levels not index-aligned, max |X^(s)-X^(t)| 0.58-0.74),
  spectral-mode capacity, per-row loss reweighting, "restoring unit continuity".
- Per-level scalers re-verified bit-for-bit: 0.07714622467756271 /
  0.023720204830169678 / 0.006939543876796961 / **0.0018356895307078958** at fid
  8/16/32/64, and `scaler_hf` == `level_scaler[64]` exactly.
- `ftgt_output_rms_sweep` (winning arm): delivered dynamic range **1.8827** vs
  **1.8011** required under `per_level` (104.5 % of required).
- Train counts **100 / 50 / 20 / 5** at fid 8/16/32/64; HF-only 128-sample test.

Part 7 `next_direction` (the slot's mandate): "a MODEL card that attacks the
CALIBRATION residual and nothing else, with `per_level` + `allpairs` frozen as
the new base ... one head that predicts a per-sample scalar gain g(X) applied to
the field output, with the head **FITTED ON THE POOLED LADDER ROWS** (all 175
distinct points ...) rather than on the 5 HF rows -- the 6-parameter-on-5-points
saturation is the whole design constraint ... the honest falsifiable clause is
'the head fails to beat the frozen base by more than 0.23991 skill units
(0.0086367 nRMSE)' ... so the card must ALSO pre-register the negative reading
(the gain is a property of the HF solve that the lower levels do not share,
which would itself close the stream)." Cheap extra arms suggested: `self_only`
at production capacity; a level-density variant.

## 4. Cross-stream cards (light scan)

- `experiment_cards/s5_tuning/batch_1/B1.json` part 7: "modes_cap 12 was a real
  truncation only where the model already predicts a pattern (**ifc_poisson,
  64x64, worth 14.6 % nRMSE**)"; operational note 5 -- the round's metric is
  `rel_l2_mean` (per-sample mean), which B2 part 5 confirms for this family;
  note 6 -- `tools/regen_preds_from_ckpt.py` recovers preds from a shipped ckpt.
- `experiment_cards/s6_local/batch_1/B1.json` part 7: the router synthesis
  explicitly falls back to the champion path on **ifc_poisson**, matching B2 part
  7 cross-note 1 (defect correction is not expressible here).
- `tools/index.md` on `residual_gain_learnability.py` (promoted by B2): "with 5
  HF training samples a 6-parameter linear gain model is already saturated, **so
  the honest design estimates the law on the lower-fidelity levels and transfers
  it**"; verified on B2's preds: frac 0.5710, oracle 0.02292, LOO R^2 0.9190 ->
  0.02431, `n_hf_train` 5.

## 5. Reopen candidates

**None.** Verified by reading both cards: B1 `status: complete,
reopen_candidate: false`; B2 `status: complete, reopen_candidate: false`. No
skipped slot exists in this stream.

## 6. What is UNKNOWN

1. **Does the per-sample gain law transfer across fidelity levels?** The whole
   batch. B2 measured that the law exists at level 64 (LOO R^2 0.919 against
   *test* gains) but that fit used test targets and cannot be reproduced from the
   5 HF train rows (6 params / 5 points). Nobody has measured the gain law at
   levels 8/16/32 at all -- not its slope, not its intercept, not its dispersion.
   The literature's prior is *against* transfer (co-kriging fits a separate rho
   per level; search-return grade).
2. **How much of the level-to-level difference is a pure multiplicative constant
   vs a different shape?** B2's `ftgt_output_rms_sweep` (1.8827 delivered vs
   1.8011 required) says the *constant* is off by ~4.5 % between the ends of the
   f_tgt axis -- enough to matter against a 3.05 % residual-gain std -- so a
   full-law transfer (shared intercept) and a shape-only transfer (per-level
   intercept + HF-fitted intercept) are quantitatively different experiments.
   Which one the ladder supports is unmeasured.
3. **Are ladder-level gains in-sample-attenuated?** The base is trained on the
   very rows a ladder-fitted head would use, so those gains are in-sample
   residual gains and may be systematically flatter than the out-of-sample test
   gains (std 0.03046). Unmeasured. A leave-one-**level**-out fit is the cheap,
   test-free estimator of transfer quality and has never been run.
4. **Is the remaining 43 % structure error attackable at all?** Part 6 says it is
   bulk-dominated, band-0 dominated, with no interface/locality/bandwidth handle
   for this family. But s5-B1 measured 14.6 % nRMSE from `modes_cap 12->32` on a
   *different* family (transfer_film) on this same dataset; the two findings are
   not formally reconciled on `mf_fno_ladder_norm`.
5. **Is 0.034250 a seed accident?** ADR 0004 forbids seeds 1-2 in-round, so
   success criterion 1 is "provisionally met". Anything B3 measures inherits that
   caveat; B3's control arm retrains the base and therefore supplies a second
   independent seed-0 draw (a continuity gate, not a CI).
6. **What is claimable at this effect size?** Available effect 0.0099-0.0113
   nRMSE against the 0.0086367 floor = 1.15-1.31x. Whether a *fitted* head can
   reach ~87 % of an upper bound that itself used test targets is unknown, and
   the honest prior is that it cannot.
7. **Out of scope but open**: whether a K > 1 coefficient head (IFC's actual
   construction) beats the rank-1 amplitude case -- the websearcher explicitly
   dates this to batch 4.
