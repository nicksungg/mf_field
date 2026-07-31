# Iteration 1 — Stream `r2s2_stacked`, Batch 2

## Design context considered

- `summary_so_far.md` §6 (unknowns 1-6) and the batch-2 prior-art verdict table
  (`websearches/r2s2_stacked/batch_2/report.md`), especially D1 / D3 / D4.
- program.md §12.2 verbatim (quoted in the summary), §2.2 floor arms, §2.3 panel + anchor
  table, §4.2 skip/crater rules, §5 immutables 1-13 (in particular §5.9 stripped test view and
  §5.10a declared reuse), §13.3 prior-art discipline.
- Anchor: `state/anchors/r2s2_stacked.json` value **23.063616857615774**
  (`best_floor_panel_geomean`, `provisional: false`). Crater bound = 1.5x = **34.595**.
- Certified noise floor `state/noise_floor.json` (`_provisional: false`, source r2s4-B1,
  3 seeds, family `r2s4_cert_min`): `min_claimable_effect` panel geomean **1.1418668**,
  helmholtz **2.9529916**, pfc **0.2130273**, allen_cahn **0.8797047**, fisher_kpp
  **0.0007137**, cahn_hilliard **0.0912454**, ifc_poisson **0.9377041**. Same file's
  per-dataset `mean_skill` is the certified condition->HF comparator.
- Frozen floors `state/anchors/floors.json` (all three arms, skill): helmholtz nn 4.3853 /
  mean 14.6107 / **zero 3.3441**; pfc nn 68.5555 / **mean 59.8118** / zero 135.4871;
  allen_cahn **nn 269.1959** / mean 562.0295 / zero 561.5560; fisher_kpp nn 16.3379 /
  **mean 11.9931** / zero 46.6211; cahn_hilliard **nn 23.1803** / mean 23.9691 / zero 23.9217;
  ifc_poisson **nn 10.0549** / mean 11.2063 / zero 27.7778.
- B1 card parts 5-7 (numbers reproduced in `summary_so_far.md` §3), the promoted probe
  `tools/surrogate_coherence_eligibility.py` (read: per-band coherence, in-sample oracle Wiener
  ceiling `sqrt(1-gamma^2)` weighting, verdict rule FUTILE <= 0.52 / ELIGIBLE >= 0.95,
  `--pred/--target` npy/npz CLI, train-split-only assertion).
- Pre-falsified levers (program.md §5 -> r1 §5): WNO backbone swap, LF low-mode freezing,
  diffusion prior for point accuracy. Plus B1's own explicit prohibition: do NOT re-run the
  frozen-vs-finetuned contrast as B1 specified it (confounded by a 50% larger optimizer budget;
  worth <= 0.08% on the five paired columns).
- Sibling cards in flight: `r2s1_direct-B2` (closed-form condition->HF head + capacity ladder
  on the full panel, incl. helmholtz and the ifc POD+ridge head) and `r2s4_diag-B2`
  (value-of-LF accounting with LF-teacher / LF-ablated arms).
- Orchestrator note for this slot: three paths open (A realisation-aware emulator; B pivot to
  helmholtz/ifc — do NOT duplicate r2s1-B2; C a coherence-calibration / D4-measurement
  diagnostic), plus an honest skip.

## Proposal reasoning

### Rejected: part-7 option (A) as written (realisation-aware generative emulator on cahn_hilliard)

The websearcher's instruction is the decisive test: *"Say what your stage 1 conditions on that
the conditional mean does not have. If the answer is 'nothing', the arm is refuted before it
runs."* Under §5.9 the test row exposes **only the condition vector**. Therefore every
admissible stage 1 is a function of c (deterministic) or a draw from a distribution indexed by
c (stochastic). In the second case the drawn realisation is independent of the test row's own
realisation, so its band>=1 coherence with the target is 0 in expectation and its per-sample
relative L2 is worse than the conditional mean's — the mean-vs-sample trade under an L2-relative
metric, which is what B1's part 7 already states. There is no third object: nothing on the test
path carries realisation information. The one column where part 7 kept the option alive
(cahn_hilliard) is, by B1's own taxonomy, **sampling**-limited (nn condition distance 3.91 sd at
N=320, in-sample 0.0317 -> held-out 0.4649), i.e. its binding defect is generalisation in a
19-dim condition space, which a stochastic head does not touch and which §5.11 forbids fixing
with more data. Add the budget argument the websearcher supplies (ceiling ~1.6 skill units
against a 14.08 panel geomean) and this arm is a costly re-derivation of a known negative.

**But**: the *empirical* version of option (A) costs nothing and has never been scored. The
nearest-condition train LF field is exactly a draw from the empirical p(LF | c); k-NN averaging
over the k nearest train conditions sweeps continuously from that draw (k=1, full band>=1
amplitude, wrong realisation) to the conditional mean (k=N). That ladder is training-free,
test-legal (train LF is training data; §5.9 constrains only the test view), and settles the
sample-vs-mean question directly. So option (A)'s *question* survives; only its expensive
implementation is dropped.

### Rejected: part-7 option (B) (pivot to helmholtz / ifc_poisson learning gaps)

`experiment_cards/r2s1_direct/batch_2/B2.json` is already running the closed-form-head +
capacity-ladder programme on the full panel, including the ifc POD+ridge head that D2b names as
a declared baseline and the Wiener band-gain calibration. B1's own part 7 says option (B)
*"should be run as a condition->HF card and coordinated with r2s1/r2s4 rather than as another
stacking arm"* — it has been, by r2s1. Re-proposing it here is duplication and a rebadge risk.

### Rejected: honest skip

Available under §4.6 and defensible if the only remaining ideas were (A) and (B). It is not the
best call: unknowns 2 and 3 in `summary_so_far.md` §6 are *live risks to a rule this stream has
already exported to the whole round* (B1 cross-stream note 3 tells every stream to run
`surrogate_coherence_eligibility.py` as a precondition), and they are cheap to settle. Shipping
an uncalibrated, never-stress-tested rule and then skipping the batch that could falsify it
would be the worst of the available options.

### Chosen: a diagnostic that calibrates the correctability rule and measures the closure

The three open things that are (i) this stream's own, (ii) not owned by another stream, and
(iii) cheap:

1. **Calibration (D3).** value-add(gamma) has three measured points and a *frozen* corrector,
   so correctability and distribution shift are confounded. Refit the corrector at every rung at
   an identical budget -> the curve measures correctability alone, and it is exactly the
   budget-matched protocol B1's part 7 demands if the frozen/finetuned axis is touched at all.
2. **Rule safety.** The exported rule's ceiling is an LSI oracle; round 1's corrector is a
   spatially adaptive gated CNN that can, in principle, exceed it (registration/edge errors are
   the classic case an LSI filter cannot fix). This is a genuine falsification risk to a
   round-level rule, and it has never been tested.
3. **Closure (D4) as a measurement.** DPI is a theorem, so the *principle* is preempted; the
   measurement is not. Its field-valued form is partial coherence given the condition: for any
   deterministic intermediate g(c) it is 0, so the stacked class cannot beat a direct
   condition->HF model of equal capacity. Measuring it — with a permutation null and against the
   *real* LF's partial coherence (how much a genuine coarse solve carries beyond c) — converts
   B1's argument into a number on six datasets.

Two ladders make all three decidable in one job:

- **Ladder A (train-side only, oracle):** spectral convex mix between the row's own real
  paired train LF and a realisation-mismatched real LF (the LF of its nearest-condition *other*
  train row), t in {0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0}. Spans gamma from ~1 down to the
  mismatched end while holding the marginal field distribution fixed — the only way to move
  coherence without also moving amplitude statistics. Never on a test path.
- **Ladder B (test-legal, condition-only):** k-NN-in-condition LF composite, k in
  {1, 2, 4, 8, 16, 64, 256, all}; k=1 is the empirical posterior sample (option A at zero
  cost), k=all is the conditional-mean LF (B1's A5 arm). Leave-one-out on train rows.

Per rung: training-free stats via the promoted probe (gamma_band0..3, in-sample oracle LSI
ceiling, the rule's verdict label) recorded BEFORE any corrector is fitted (the websearcher's
"go/no-go before the submit" is thereby a recorded pre-registration inside the job); then the
refit closed-form LSI Wiener (all rungs, 3 fold resamples) and the refit nonlinear
LocalCorrector (a fixed subset of rungs, identical step budget) evaluated on a disjoint
train-eval fold.

**Alternatives weighed inside the chosen direction.** (a) *Reuse other streams' checkpoints
instead of building ladders* — rejected: different families, different ckpt schemas, different
branches, and the timing of r2s1-B2 / r2s4-B2 is not under this card's control; the ladders are
analytic, reproducible and self-contained. (b) *Train a generative (VAE/diffusion) stage 1 to
populate the high-gamma end* — rejected: expensive, and the pre-falsified-lever list already
contains "diffusion prior for point accuracy"; ladder A reaches gamma ~ 1 for free. (c) *Score
the raw uncorrected k=1 intermediate as `test_hf`* — rejected: it would sit far above the floor
band on allen_cahn/pfc and risks a mechanical crater verdict on a diagnostic whose content is
not its score; the out-of-fold blend (below) removes that risk honestly. (d) *epochs = 0, no
test scoring at all* — rejected: the sample-vs-mean question (unknown 4) deserves a test-split
answer in skill units, and the certified per-dataset mce only applies there.

**Scored arm, and why it cannot crater.** `test_hf` = ladder-B rung k* (chosen on the
calibration fold) -> LSI Wiener with an alpha line search **including 0** -> LocalCorrector with
a zero-init gate -> out-of-fold blend lambda in [0,1] (21-point grid) against a base chosen from
{zero, train_mean, nn_condition} on the same calibration fold. Because alpha=0 and lambda=0 are
in the grids, the arm degrades gracefully to the best out-of-fold floor; its expected landing is
the floor band (panel geomean 15-25 against the 23.064 anchor and the 34.595 crater bound), and
lambda* itself is the deliverable — an out-of-fold estimate of what the realisation-carrying
intermediate is worth beyond the training-free floors. This is declared in part 4 as a
diagnostic instrument, not a champion attempt.

**ifc_poisson.** B1 recorded `pairing.paired_real_lf=false`,
`max_abs_cond_deviation_lf_vs_hf=0.682`, `attribution.valid=false` (n_hf_train=5, n_lf=20).
Ladder A is therefore not constructible there and every coherence statistic is low-n: the column
is pre-declared **report-only for the law**, still scored for the panel geomean, and carries
B1's `semantics_degraded` flag forward. helmholtz stays report-only per the standing discipline
(its certified mce 2.95299 exceeds any effect available against a zero floor of 3.3441), with
the zero-floor column always shown. pfc claims carry the band-limited denominator caveat
(`eval/copylf_baselines.json _notes.pfc`) and the wrap-seam caveat (deep-bulk ratio 0.908).

**Declared reuse.** Corrector code is vendored with provenance from B1's family
(`worktrees/r2s2_stacked/B1/models_r2/r2s2_stack` @ 6b4e1d48, itself vendored from round-1
`s4_router` @ b90d4662): `lsi_filter.py`, `local_corrector.py`, `bands.py`, `periodicity.py`,
`upsample.py`. Under §5.10a the corrector is the declared frozen-lineage sub-component and the
reuse is the experiment; the novel object here is the *ladder + calibration instrument*, not an
architecture, so the rebadge check (§5.10) is answered by the card carrying no architectural
claim at all.

## Proposal

- **Category**: `correctability_calibration / coherence-calibrated eligibility threshold for
  defect correctors + partial-coherence (DPI) closure measurement of the condition-only stacked
  class`
- **Card type**: `diagnostic` (with training — the correctors are refit per rung; precedent:
  r2s4-B1, a diagnostic card with training)

- **Motivation** (quotes the batch-2 prior-art verdict verbatim):
  D3 is *"`preempted-but-MF-composition-open (cite)`"* — *"FreqNO-DPS's diagnostic validates an
  ASSUMPTION OF ITS OWN FILTER (Fourier-diagonal residual covariance). r2s2's rule is a
  CALIBRATED THRESHOLD ON CORRECTOR VALUE (0.52 < gamma_b1 < 0.95 bracketed by the real->pseudo
  interpolation) plus an oracle-Wiener upper bound. No fetched source calibrates coherence
  against realised corrector value-add"* (FreqNO-DPS https://arxiv.org/html/2606.03936, VERIFIED:
  *"prerequisite check for applying the method to any new surrogate"*). D4 is *"`preempted
  (cite)` as a principle; open as a measurement"* — *"No fetched source states the DPI for
  stacked PDE surrogates or measures the resulting ceiling on field-valued MF benchmarks. Claim
  the measurement, cite the theorem for the principle"*
  (https://en.wikipedia.org/wiki/Data_processing_inequality). And the card answers D1's negative
  prior in the design rather than around it — *"an independent sample has coherence 0 with the
  test realisation in expectation"* — by scoring the empirical posterior sample (k=1 NN-in-
  condition LF) against the conditional mean (k=all) at zero emulator cost, which is the only
  form of *"realisation-aware stage 1"* the stripped view (§5.9) admits.

- **Concrete config**: new family `models_r2/r2s2_correctability` (worktree
  `worktrees/r2s2_stacked/B2`, branch `round2/exp-r2s2_stacked-B2`), condition-only at test,
  stripped view only, `R2S2B2_REQUIRE_NO_TEST_LF=1` tripwire (raise if any test-side LF array is
  constructed) and `R2S2B2_ORACLE_LADDER_TRAIN_ONLY=1` (raise if a ladder-A rung is reachable
  from a test path). Vendored with provenance comments from
  `worktrees/r2s2_stacked/B1/models_r2/r2s2_stack` @ 6b4e1d48 (lineage `s4_router` @ b90d4662):
  `lsi_filter.py` (closed-form Wiener T(k), alpha line search including 0),
  `local_corrector.py::LocalCorrector` (`local_pixel_gate`, kernel 7, depth 4, width 32,
  zero-init head), `bands.py`, `periodicity.py`, `upsample.py` (per-dataset ADR r2-0001
  convention `node_aligned_periodic` / `dirichlet_node` / `legacy_cell_centred`, asserted to
  agree with `round2/eval/panel_data.py` on the TRAIN split at 1e-9 via a read-only import).
  Probe `probes/correctability_law.py` = `tools/surrogate_coherence_eligibility.py` adapted
  (same band grid and coherence/oracle formulas) plus the two new modes M2 needs
  (partial coherence given the condition; permutation null) — promoted back via the register
  turn.

  Folds per dataset, fixed by `R2S2B2_FOLD_SEEDS=0,1,2` and identical across every rung and arm:
  train split -> fit 0.70 / calib 0.15 / ladder-eval 0.15, disjoint and asserted disjoint (round
  1's D3 val_idx double-consumption caveat). `ifc_poisson` (N_hf=5): LOO, calib/ladder-eval
  disabled below `R2S2B2_LOO_MIN_N=20`, final-epoch weights, everything low-n flagged.

  **Ladder A (train-side only, calibration):** `X_t = irfft2((1-t) F_real + t F_mismatch)`,
  `F_real` = the row's own paired real train LF (upsampled by the dataset convention),
  `F_mismatch` = the real train LF of its nearest-condition *other* train row; t in
  {0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0}. Marginal amplitude statistics are held ~fixed while
  coherence sweeps.
  **Ladder B (test-legal, condition-only):** `X_k` = mean of the real train LF fields of the k
  nearest train conditions (per-dim train-standardized L2, the floors.json definition), k in
  {1, 2, 4, 8, 16, 64, 256, all}; leave-one-out when the query is a train row.

  Per rung, in this order: (M1a) training-free stats written BEFORE any fit — gamma_band0..3,
  target energy share, `input_over_target_amp`, in-sample oracle LSI ceiling, identity nRMSE,
  and the promoted rule's verdict label; (M1b) refit closed-form LSI Wiener on the fit fold,
  alpha on calib, evaluated on ladder-eval, at all rungs x 3 fold seeds; (M1c) refit
  LocalCorrector on the fit fold at an identical step budget for every rung
  (`R2S2B2_CORR_STEPS_PER_EPOCH=10` -> 2000 steps at 200 epochs, 20 at contract tier), at rungs
  {A:0, A:0.5, A:1.0, B:1, B:k*, B:all}, fold seed 0. Value-add(rung) =
  `1 - nRMSE(corrected)/nRMSE(intermediate)` on ladder-eval.
  (M2) partial coherence given the condition: conditioners `knn_oof` (k by out-of-fold error)
  and `ridge_pod16`, fitted on the fit fold, applied out-of-fold to BOTH intermediate and HF;
  band coherence recomputed on the residuals; permutation null = 200 draws re-pairing the
  intermediate rows within the eval fold.
  (M3) scored test arm as described above, with reference splits (none beginning with `test`)
  `ref_k1_corrected`, `ref_kall_corrected`, `ref_k1_raw`, `ref_kall_raw`, `ref_rule_selected`
  (what the training-free verdict picks), and the three frozen floors `ref_zero`,
  `ref_train_mean`, `ref_nn_condition` seam-checked against `state/anchors/floors.json` at 1e-9,
  RAISING on mismatch. Guards `heat_local, fluid, sharp__sod_1d` at contract tier (2 epochs) in
  a separate invocation — they populate the high-gamma end of the law (B1 F13: value-add 0.63 /
  0.68 at t=1) and are labelled contract-tier.

- **Recipe**: see `report.md` (complete JSON; transcribed verbatim to the card).

- **Expected outcome**:
  * Scored `test_hf` panel geomean **15-25** — floor band, explicitly NOT a champion attempt
    (anchor 23.0636; crater bound 34.595). lambda* -> 0 expected on pfc / allen_cahn /
    fisher_kpp (structural ceiling), lambda* > 0 possible only on cahn_hilliard and the two
    learning-gap columns.
  * M1: value-add(gamma) monotone in gamma with the claimable crossing between gamma_band1 0.52
    and 0.95 (B1's bracket), located to +/- one ladder step; predicted gamma* in 0.80-0.95 for
    LSI. Refit vs B1's frozen numbers isolates distribution shift: expect the refit curve to sit
    ABOVE the frozen curve at low gamma by a few percent and to converge at gamma -> 1.
  * M1c (the risky prediction): the nonlinear LocalCorrector's realised value-add stays at or
    below the training-free in-sample oracle-LSI ceiling on every condition-only rung.
  * M2: partial gamma_band1 of every ladder-B rung inside its permutation-null band
    (|delta| < 0.10) on >= 5/6 datasets, against real LF (ladder A, t=0) partial gamma_band1
    >= 0.9 on the three ADR r2-0003 datasets — the closure number: what a real coarse solve
    carries beyond the condition, and that no condition-only intermediate carries any of it.
  * M3: after correction, k=1 (sample) WORSE than k=all (conditional mean) on >= 5/6 datasets,
    by more than the certified mce on >= 3 — the direct, test-split refutation of the
    realisation-aware branch, at zero emulator cost.
  * vs the noise floor: every test-split comparison is judged against the certified per-dataset
    `min_claimable_effect` (pfc 0.2130273, allen_cahn 0.8797047, fisher_kpp 0.0007137,
    cahn_hilliard 0.0912454, ifc_poisson 0.9377041; helmholtz 2.9529916 = report-only) and the
    panel value 1.1418668; train-side dimensionless quantities are judged against the in-job
    3-fold-seed paired spread with an absolute 0.05 relative-gain floor.

- **Expected falsification** (one sentence, four clauses):
  H-r2s2-B2 — *"correctability of an intermediate is governed by its coherence with the target
  after the condition-predictable component is removed, so on this panel no condition-only
  intermediate is worth correcting and the exported training-free coherence rule is safe for
  nonlinear correctors"* — is FALSIFIED if **(F1, rule safety)** a refit LocalCorrector's
  realised value-add on any rung the promoted rule labels `CORRECTOR_FUTILE`
  (gamma_band1 <= 0.52) exceeds that rung's training-free in-sample oracle-LSI ceiling by more
  than `max(3x in-job fold-seed paired spread, 0.05 relative error reduction)` on >= 3 ladder
  cells, **or (F2, realisation-aware branch)** the k=1 sample arm beats the k=all
  conditional-mean arm on the TEST split by more than that dataset's certified
  `min_claimable_effect` (pfc 0.2130273 / allen_cahn 0.8797047 / fisher_kpp 0.0007137 /
  cahn_hilliard 0.0912454 / ifc_poisson 0.9377041; helmholtz report-only at 2.9529916) on >= 2
  panel datasets, **or (F3, closure)** any ladder-B rung's partial coherence given the condition
  exceeds its own permutation-null 95th percentile by > 0.10 on >= 2 datasets under both
  conditioners, **or (F4, calibration validity)** the scored blended arm loses to its own
  out-of-fold-selected floor base by more than the certified `min_claimable_effect` on >= 2
  panel datasets.

- **Anchor reference**: `null` (program.md §4.5 / §12: null for all four round-2 streams; the
  own-stream anchor 23.0636 is implicit).

## Immutables self-check (program.md §5; §4.5 distillation, 8 + 3 extras)

1. **Data read-only.** The card only reads existing arrays: train LF/HF through the stripped
   view loader and the frozen `state/anchors/floors.json`; ladder A and B are in-memory
   functions of arrays already on disk (a Fourier convex combination and a k-NN average). No
   generator is invoked, no file under `data/` or `stripped_data/` is written, N_hf stays 5 on
   ifc_poisson and 400 on the sharp datasets, and no LF is produced by downsampling HF (both
   ladders are built from *real coarse solves* that already exist).
2. **Panel + guard fixed.** `datasets: "panel"` resolves to the six §2.3 datasets and the guard
   leg is the exact triple `heat_local, fluid, sharp__sod_1d` at contract tier — the same two
   invocations B1 used (`state/timing_ledger.json` records both legs for r2s2_stack).
3. **Eval layer / spec untouched.** The card requires no edit to `round2/eval/`, `project.yaml`,
   `program.md` or the subagent prompts: scoring goes through `score_panel.py` unchanged, and
   the only contact with the eval layer is a read-only import of the upsampling convention from
   `eval/panel_data.py` plus a 1e-9 agreement assert — the same pattern already reviewed on
   `r2s4_diag-B2` (its part 3: *"vendored with provenance and asserted at contract tier to agree
   with the eval implementation on the TRAIN split (a read-only call; the eval layer is not
   edited)"*).
4. **One nRMSE definition.** Every reported nRMSE (scored splits, ladder-eval value-add,
   identity nRMSE inside the probe) is computed by `round2/eval/nrmse.py`, which the promoted
   probe already imports (`from nrmse import NRMSE_DEF_HASH, nrmse`); the result JSON carries
   `nrmse_def_hash` d3d0ade9... and `copylf_def_hash` 9753ff24..., matching B1's verified pair.
   Corrector fitting losses are free and are not reported as scores.
5. **Contract CLI fixed.** The family exposes the unchanged six-argument
   `smoke_eval.py --dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`; every knob in
   the design (ladder grids, fold fractions, corrector shape, blend grid, tripwires) is an
   `R2S2B2_*` env key listed in the recipe `env` block and therefore enters the cache key.
6. **Seeds / tier epochs fixed.** `seeds: [0]`, `epochs: 200` (smoke tier) for the panel leg and
   2 (contract tier) for the guard leg; no seeds 1-2 are requested (diagnostic card, §4.2 strict
   1-seed in-round), and no full-tier run is implied.
7. **Guarded factory surfaces untouched.** All new code lives under
   `worktrees/r2s2_stacked/B2/models_r2/r2s2_correctability/` plus one probe under that
   worktree's `probes/`; nothing under `mf_field/factory_mffp/{eval,baselines,references,
   scripts,data}`, `factory.md` or `akash/` is read-modified — the vendor sources are copied out
   of an immutable round-1 branch and B1's round-2 branch, not edited in place.
8. **Checkpoint-resume from `<ckpt_dir>/last.pt`.** The job is a sequence of independent rung
   fits, so `last.pt` stores `{rung_cursor, fold_seed_cursor, per-rung corrector state_dicts,
   fitted LSI T(k)/alpha, completed training-free stats}`; on resume the family reloads it,
   skips completed rungs, and continues at the cursor — strictly easier than B1's five-arm
   resume, which is already implemented in the vendored `smoke_eval.py` skeleton.
9. **Falsification threshold vs the certified noise floor.** F2 and F4 are stated *as* the
   certified per-dataset `min_claimable_effect` values and require strict exceedance: pfc
   0.2130273, allen_cahn 0.8797047, fisher_kpp 0.0007137, cahn_hilliard 0.0912454, ifc_poisson
   0.9377041 (`state/noise_floor.json`, `_provisional: false`); helmholtz (2.9529916) is
   excluded from claims and carried report-only with its zero-floor column 3.3441. F1 and F3 are
   dimensionless train-side quantities to which the skill-unit floor does not apply, so they use
   the in-job 3-fold-seed paired spread with an absolute floor (0.05 relative gain; 0.10
   coherence over a 200-draw permutation null) — both larger than the fold-to-fold variation B1
   observed on the same slices.
10. **Not a pre-falsified lever.** Nearest listed levers: "LF low-mode freezing" (a *fixed*
    low-band pass-through inside a corrector) and "diffusion prior for point accuracy". This
    card freezes no band and trains no generative prior; the LSI stage is refit per rung with an
    alpha line search that includes 0. Nearest in-stream prohibition: B1 part 7's *"Do NOT
    re-run the frozen-vs-finetuned contrast as the card specified it"* — the difference is that
    the frozen/finetuned axis is deleted entirely and replaced by a coherence axis on which
    every corrector is refit at an identical step budget, which is precisely the remedy that
    sentence prescribes (*"run it budget-matched and only on a surrogate that has already passed
    the coherence precondition"*).
11. **Floor arms.** Although this is a diagnostic card, the mandatory §2.2 floor arms
    (`nn_condition` / `train_mean` / `zero` from `state/anchors/floors.json`) are carried as
    `ref_*` splits on every dataset, seam-checked at 1e-9 with a RAISE on mismatch, and they are
    load-bearing in the falsification reasoning: F4 is *defined* against the out-of-fold-selected
    floor base, and the expected-outcome section states the scored arm's floor band (15-25) and
    the standing helmholtz zero-floor column 3.3441.

## Status

- Slot covered: 1/1, `diagnostic` card, no skip.
- Reopen candidates resolved: 0 of 0 (none exist round-wide;
  `grep -rl '"reopen_candidate": true' experiment_cards/` empty, B1 `reopen_candidate: false`).
- Immutables self-check: **pass (11/11)** on the first pass; no revision required, so no
  `iteration_2.md`.
