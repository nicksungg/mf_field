# Summary so far — Stream `r2s1_direct`, Batch 3

## 1. Websearch findings + prior-art verdict (batch 3)

Source: `websearches/r2s1_direct/batch_3/report.md` (5 iterations, cap hit;
14 WebSearch / 13 WebFetch, 5 usable; no arXiv `/pdf/` fetched).

Four candidate directions were priced. Verdict rows (verbatim key phrases):

- **C1** — per-mode out-of-fold model-family selection over a bank
  ({affine, quadratic, kernel ridge, k-NN}) for condition->POD-coefficient
  regression, priced against a trained decoder **before** any shared post-hoc
  stage: **`preempted-but-MF-composition-open (cite)`**. "One-regressor-per-mode
  is **presumed prior art (do not claim)**"; ASAMS
  (https://pmc.ncbi.nlm.nih.gov/articles/PMC7571090/) already does automatic
  whole-model selection over trained candidates. What is open is *the
  measurement*: a ~10^1-10^2-parameter per-mode OOF-selected map as the
  standing control a 10^7-parameter decoder must beat "on a **copy-LF-skill
  panel under the stripped no-LF-at-test view**, with the per-mode ORACLE
  ceiling reported."
- **C2** — the instrument/protocol claim: a shared post-hoc baseline-blend /
  floor-hedge stage pays off as a closed form in rho, so comparisons decided
  there are **decorrelation** verdicts:
  **`preempted-but-MF-composition-open (cite)` - best-supported novel
  composition for B3**. Mechanism is preempted and **must be named as
  Bates-Granger minimum-variance combination** `w_BG=(1'S^-1 1)^-1 1 S^-1`
  (https://search.r-project.org/CRAN/refmans/MuMIn/html/BGweights.html;
  Bates & Granger 1969); the symmetric-candidate framing
  (https://arxiv.org/html/2510.26456) confirms "none receives special
  'baseline' status". Open: its use as an **evaluation-protocol defect
  detector**. One targeted search returned no usable results.
- **C3** — predictability-ordered / identified-SET output basis:
  **`preempted (cite)`** (supervised PCA, https://arxiv.org/abs/2011.05309;
  supervised-DR review, https://pmc.ncbi.nlm.nih.gov/articles/PMC9633505/).
  "**Ship as a bug fix / instrument, never as a contribution.**"
- **C4** — the H2 test (decoder advantage = spatial inductive bias reaching
  low-energy, low-OOF-R^2 modes): **NOT PRIOR-ART-CHECKED THIS LOOP**.
  "Must not be headlined as novel. Admissible only as a diagnostic inside a
  C1/C2-claimed card", and only if the card makes `preds_test.npz` a build gate.

Websearcher's brainstormer instructions (report section "For the brainstormer"):
quote the row actually proposed; C2 is the strongest shape; do not claim C3;
**design the falsification per dataset and on 3 datasets, not 6**; do not
widen the Wiener grid; quote the anchor 23.0636 and the per-dataset floors.

## 2. Section 12 conventions verbatim (program.md 12.1 `r2s1_direct`, gap)

> - **Bar**: the per-dataset floor table (2.3). Beating NN-in-condition with
>   400 train samples is necessary but nowhere near sufficient; the interesting
>   question is how close a from-scratch condition->HF surrogate gets to
>   skill 1.0 on each dataset.
> - Design priors (spec 6): FiLM-conditioned FNO **decoders** (condition ->
>   spectral latent -> field), DeepONet-style branch-trunk (branch on condition,
>   trunk on coordinates), spectral/implicit decoders (SIREN/modulated INR
>   class). Condition vectors are 2-19 dims; ifc_poisson's is 5-dim.
> - **ADR r2-0003 (corrects a spec 4 grounding fact)**: on pfc, fisher_kpp
>   and allen_cahn the condition vector is NOT complete - per-sample random
>   ICs live only in the fields, so condition->HF is a stochastic map and
>   deterministic models are bounded by the conditional-mean floor
>   (train_mean > NN on those floors is the symptom). Skill->1 is unreachable
>   there; design and falsify against the conditional-mean floor, and treat
>   bare FiLM-decoders as declared baselines (prior-art verdict: preempted).
> - **Helmholtz lesson** (r1 report 5): the zero field is the floor to beat
>   there - any helmholtz claim must show the zero-floor column.
> - **pfc caveat** (2.3): denominator 0.007381 under variant C; no
>   fidelity gap under band-limited. State it on every pfc claim.
> - N_hf on ifc_poisson is 5 - every claim there is anecdote-grade; prefer
>   variance-reducing designs (r1 s1 lesson: ensembling, physics residuals are
>   out per ADR 0009 - physics-agnostic at test).
> - Overfitting is THE central threat at these sample counts; r2s4's
>   overfitting-anatomy diagnostics feed this stream. Train/val discipline in
>   the recipe is mandatory (no test-split peeking; the round-1 D3 val_idx
>   double-consumption caveat is the cautionary tale).

Stream anchor (`state/anchors/r2s1_direct.json`): best-floor panel geomean
**23.063616857615774**; per-dataset best floors helmholtz 3.3441 (zero), pfc
59.8118 (train_mean), allen_cahn 269.1959 (NN), fisher_kpp 11.9931
(train_mean), cahn_hilliard 23.1803 (NN), ifc_poisson 10.0549 (NN).
Certified `min_claimable_effect` (`state/noise_floor.json`, non-provisional,
r2s4-B1 3-seed): helmholtz 2.95299, pfc 0.21303, allen_cahn 0.87970,
fisher_kpp 0.00071, cahn_hilliard 0.09125, ifc_poisson 0.93770, panel 1.14187.

## 3. Within-stream prior cards

**`r2s1_direct-B1`** (`experiment_cards/r2s1_direct/batch_1/B1.json`, complete,
`reopen_candidate: false`) — identifiability-certified FiLM decoder with
condition-predicted amplitude/direction factorization + out-of-fold blend.
FALSIFIED (panel-geomean leg fired at 19.6444 vs 19.60, decided inside the
1.1419 panel mce). Part 7: apparent decoder capacity dissolved under out-of-fold
calibration on 5 of 6 cells; only `sharp__cahn_hilliard` survived (0.5511 skill,
6.0x mce). Directive: "Stop buying decoder capacity in this stream; spend B2 on
IDENTIFICATION and CALIBRATION"; identifiable-mode counts (OOF R^2 > 0.1):
helmholtz 5, pfc 2, allen_cahn 1, fisher_kpp 1, cahn_hilliard 3, ifc 1.

**`r2s1_direct-B2`** (`.../batch_2/B2.json`, complete, `reopen_candidate:
false`) — training-free selection of output parameterization + Wiener band
gains + floor blend, vs a decoder ladder. FALSIFIED on L1 and L2 (allen_cahn
+6.15109 = 6.99x mce; cahn_hilliard +1.29632 = 14.21x mce, both against the
staged `ref_decoder_big`). Wall clock **16.83 min** for the whole panel+guard
job (job 66189580, H200). Scored heads realized at **3-80 parameters**;
decoders 1.4e7-1.6e7.

Decisive B2 re-analysis findings (parts 6/7), the ones B3 must build on:
- **Post-hoc-stage artifact**: on allen_cahn the *raw* comparison has the
  OPPOSITE SIGN and 4.3x the magnitude - `ref_raw_head` 175.46241 vs
  `ref_raw_decoder_big` 202.15898 (head wins by 26.70 = 30.3x mce), while the
  staged comparison says the head loses by 6.15. Cause: the head's error is
  numerically the `dc_only` base (rho = 1.0000, RMS residual 1.01e-6), so no
  lambda can pay it, while the decoder at rho 0.69-0.78 collects 8.13 skill.
- **The blend payoff is a 1-parameter closed form in rho** fitted to <=1.6% rel
  RMS on 5/6 datasets; substituting the decoder's rho reverses the decisive cell
  by 2.07-7.15x mce. Promoted: `tools/blend_decorrelation_payoff.py`.
- **Selection-rule arity bug**: stage S counts modes clearing tau then fits the
  leading *window*; set != window on 3/6 datasets, worth 5.62x mce on
  cahn_hilliard (SET-indexed 80-param head 12.74087 vs shipped 13.25360).
  Also `heads.rank_statistic` hardcodes an `add`-form basis regardless of the
  selected centering form (helmholtz set {8,9,20} add-basis vs {0,8,9} fact).
  Promoted: `tools/selection_set_vs_window_audit.py`.
- **Wiener stage must not be widened**: the band-3 gain pinned at the [0,2] edge
  is a 40-sample calibration overfit (prediction-truth cosine 0.1218; LS-optimal
  gain 0.6401, a SHRINK; ORACLE 0.70); the stage COST 0.09837 skill on
  cahn_hilliard.
- **Per-mode OOF map selection works**: on allen_cahn a 10-parameter per-mode
  quadratic lifts mode-0 OOF R^2 to 0.99971, scores 146.681 - 20.7954 skill
  (23.64x mce) better than the 15,853,057-parameter decoder, at 99.2% of its
  mode set's ORACLE ceiling, blend standing down to lambda = 1.00.
- **Dead cells**: pfc and fisher_kpp have 0 of 30 leading POD coefficients
  condition-identifiable OOF after DC removal; ORACLE test-optimal blend
  lambda = 0.00 on both. ifc_poisson runs the LOO branch (n_fit 5, calib fold =
  all of N) - anecdote-grade.
- **B2 part 7 poses B3-OR-CLOSE explicitly** and makes three instrument repairs
  PREREQUISITE to any further capacity claim, plus a `preds_test.npz` build gate.

B2 raw (pre-stage) arm skills, the working priors for B3 (part 5
`arm_skill_table`): helmholtz raw_head 4.91600 / raw_decoder 3.11507;
pfc 55.42589 / 48.89325 (`ref_dc_only` 47.43211); allen_cahn 175.46241 /
202.15898; fisher_kpp 11.59581 / 11.58186 (`ref_dc_only` 11.55729);
cahn_hilliard 13.15523 / 12.06357; ifc_poisson 10.60818 / 20.11772.

## 4. Cross-stream cards (light scan)

- **`r2s4_diag-B2`** part 7 (b): helmholtz's certified mce 2.953 is *mostly
  metric* - 3-seed T0 spread 1.6363 mean-of-ratios vs 0.0656 energy-pooled
  (24.9x), so **no helmholtz arm contrast is claimable at any effect size**;
  "helmholtz loses to the zero field" should be restated as "mean-of-ratios
  2.06x the zero floor, energy-pooled 1.0205 against 1.0". Confirms keeping
  helmholtz report-only. Also (a): a training-free identifiability/support rule
  (candidate) predicting which datasets are information- vs sample-limited.
- **`r2s3_lf_train_signal-B2`** part 7 (3): "FISHER_KPP'S FLOOR LOSS IS A TASK
  PROPERTY, NOT AN ARM DEFECT - for r2s1 and r2s2, which also score
  condition-only arms there": every arm emits a condition response carrying
  77-92% of the truth's fluctuation energy at pooled alignment 0.064-0.070, so
  a constant field beats all of them and optimal shrinkage is lambda* = 0.1.
- `r2s2_stacked-B2` is `analyzing` with an empty part 7 - nothing to read yet.
- No cross-stream card attacks the immutables this stream depends on.

## 5. Reopen candidates

**None.** Verified by reading `reopen_candidate` on all 10 round-2 cards
(`experiment_cards/*/batch_*/B*.json`): every card reports `false`, including
both `r2s1_direct` cards. Nothing to retry or drop.

## 6. What is UNKNOWN

1. **Is the stream's entire head-vs-decoder verdict an instrument artifact?**
   B2 measured the sign reversal on allen_cahn *post hoc, on its own shipped
   folds*, with a law *fitted* to those same surfaces. Nothing in this stream
   has ever scored an arm with **no shared post-hoc stage at all**. Unknown:
   what the panel looks like when the scored column is stage-free and the stage
   becomes a measured object rather than part of the estimator.
2. **Does the rho-law predict out of sample?** The 1-parameter closed form was
   fitted to B2's calibration surfaces. Whether calibration-fold moments
   (sigma_arm, sigma_base, rho) *predict* the realized test payoff of a fresh
   arm set - the difference between a curve fit and a law - is untested. This is
   exactly the open part of the C2 verdict ("its use as an evaluation-protocol
   defect detector").
3. **How much of the cahn_hilliard residual survives every repair?** B2 excluded
   basis, band-gain amplitude, mode-set arity, map nonlinearity and per-mode
   shrinkage. The measured post-repair residual is ~0.78 skill (8.55x mce) but
   was computed in the *staged* frame; the stage-free frame gives ~0.64-0.70
   (~7x mce) by arithmetic on B2's raw column - never measured directly.
4. **Is that residual on the unidentifiable modes?** H2 (decoder's spatial
   inductive bias reaching modes 2-3, 20.6% of basis energy at OOF R^2 <= 0.035)
   is currently **untestable from this stream's artifacts** - B2 shipped no
   checkpoints and no `preds_test.npz`. Unknown until a card ships them.
5. **Does the per-mode OOF map bank hold up prospectively?** allen_cahn's
   146.681 came from re-analysis on B2's fixed folds with the family already
   chosen; whether an out-of-fold *family selection* procedure, pre-registered
   and run fresh, reproduces it is unknown.
6. **Are pfc/fisher_kpp genuinely dead, or only dead post-stage?** Pre-stage the
   arms are NOT tied there (pfc 55.43 vs 48.89 vs dc_only 47.43); the tie was
   manufactured by every blend collapsing to lambda = 0 on `dc_only`. Whether
   the pre-stage differences are anything but amplitude effects under the
   relative metric (r2s3-B2's task-property finding) is unknown.
7. **Marginal value question (the B3-or-close decision).** Unknown whether one
   more ~17-minute run adds more to the round report than an honest close. The
   deciding consideration is recorded in `iteration_1.md`: B3 is the only card
   that can convert two post-hoc instrument findings into pre-registered,
   out-of-sample tests, and the only card that can lift the `preds_test.npz`
   build gate the round report would otherwise inherit as a permanently blocked
   open item.
