# Iteration 1 — Stream `r2s4_diag`, Batch 4 (the B4-or-close decision)

## Design context considered

- `summary_so_far.md` section 6 (unknowns a–f) and the batch-4 prior-art verdict rows
  A / B / B-prime from `websearches/r2s4_diag/batch_4/report.md`.
- `program.md` 12.4 verbatim (quoted in `summary_so_far.md` section 2), the section-12
  preamble registration + target-scaler rules, 5 immutables 1–13, 4.2 (strict 1-seed
  in-round), 2.1–2.3 (one nRMSE definition, corrected copy-LF, mandatory floor arms),
  and 1 (both success criteria).
- Own-stream anchor `state/anchors/r2s4_diag.json`:
  `certified_3seed_panel_geomean` **19.817844731907492**, per-dataset ifc mean skill
  **8.261220201059428**. Launch anchor 23.063616857615774 preserved under `supersedes`.
- `state/noise_floor.json` -> `ifc_poisson.min_claimable_effect` =
  **0.9377041289531141** (= max(spread_maxmin 0.9377041289531141, paired_null_95
  0.9227235526286076)); per-seed skills 7.941161869912803 / 8.878865998865917 /
  7.963632734399563.
- `state/anchors/floors.json` -> `ifc_poisson`: `n_train_hf` 5, `n_test` 128,
  `cond_dim` 5, reference `paper_bar` 0.036; floors `nn_condition` nRMSE
  0.36197607346594873 / skill 10.054890929609687, `train_mean` 0.40342796839330697 /
  11.206332455369639, `zero` 1.0 / 27.77777777777778.
- Cross-stream: `r2s3_lf_train_signal-B3` ifc `A0_nolf` 8.13438381993564 vs `A1_lf_cov`
  **2.150091575784423**, effect 5.984292244151218 > MCE; `r2s2_stacked-B3` drafted with
  a panel (hence ifc) leg.
- Ground truth read off disk (`stripped_data/ifc_poisson`): train rungs
  fidelity_64 (5, 64, 64) / fidelity_32 (20, 32, 32) / fidelity_16 (50, 16, 16) /
  fidelity_8 (100, 8, 8); test fidelity_64 (128, 64, 64) only; no test LF.
- Registration ground truth: `eval/panel_data.py:48`
  `LEGACY_CELL_DATASETS = {"heat_local", "fluid", "sharp__sod_1d", "ifc_poisson",
  "ifc_heat"}`, and `factory_mffp/models/_common/lf_registration.py::convention_for`
  returns `"legacy_cell_centred"` for ifc_poisson with `resample_fields(...)` the
  sanctioned entry point.
- Envelope: B3 ran 92 min; `state/timing_ledger.json` records the stream's siblings at
  17–55 min on h200.

## Proposal reasoning

### Step 1 — Is close-now defensible? No, on round economics.

B3's part-7 recommendation is conditional: "close the stream unless the maintainer judges
criterion 1 … still reachable by another stream". I read `r2s3_lf_train_signal-B3` part 5
directly and the condition is met and then some: on ifc_poisson the LF-trained arm scores
skill **2.150091575784423**, i.e. 2.15x the published paper bar, versus 8.13438381993564
for the matched no-LF arm — a 5.98-skill-unit effect, 6.4x the certified MCE. Criterion 1
is not merely "still reachable"; ifc carries the round's strongest single value-of-LF
number, and `r2s2_stacked-B3` is in build with its own ifc leg. B3's own escape clause
therefore fires *for* a B4.

The websearcher independently kills the lazy close: row B says "no fetched source retires
a criterion for INFEASIBILITY (only saturation)", and futility stopping's published price
is a type-II inflation that would have to be stated (Lachin 2005, PubMed 16134130). Row
B-prime's close-with-futility-statement is explicitly "*a report artifact, not an
experiment card*" — it is a maintainer/report action, not a slot. So closing would burn
the slot on something that is not a card, while a live criterion-1 route goes unmeasured.

### Step 2 — B3's counter-argument is real and must be designed against, not waved away.

At N_hf = 5 the drift-class rule admits only in-job paired controls; the MCE is
0.9377041289531141 against a per-dataset skill of ~8.13; and B2 proved the ladder is
0 % pairable. A naive "train at N in {5,20,50} and eyeball the gap" card would return
`unclaimable`. Three design moves defuse this, and all three are the websearcher's:

1. **Exhaustive subsets instead of sampled ones.** With 5 HF rows there are exactly 31
   non-empty subsets. Enumerating all of them removes sampling error in the subset
   dimension entirely, and the 120 nested chains S1 c S2 c ... c S5 give a *paired*
   in-job delta distribution at **zero extra training cost** (every chain reuses already
   trained subsets). That is a textbook satisfaction of "only in-job paired controls are
   controls" on a strict-1-seed card, and it is the same trick B3 used with its 5 outer
   folds.
2. **Equivalence, not significance** (the loop's single most actionable finding; Harms &
   Lakens, PubMed 30873486). With the certified per-dataset MCE as the equivalence bound,
   "no effect" becomes the claim *"over the entire accessible HF range 1->5, marginal HF
   samples buy less than the round's minimum claimable effect"*. Both branches are
   results; only a CI wider than the bound is inconclusive, and that width is pre-stated.
3. **Rungs as independent designs, scored natively.** Because the ladder is non-nested,
   any cross-rung *pairing* is illegitimate — but a *within-rung* generalisation-gap
   measurement needs no pairing at all and no interpolation at all. Each rung trains and
   scores on its own grid; the comparable statistic is the dimensionless gap ratio.

### Step 3 — What can the {5, 20, 50} mandate actually mean here?

This is the fact I had to establish from disk and which no prior card records: there is no
20-sample or 50-sample 64x64 training set. `fidelity_32` has 20 rows at 32x32 and
`fidelity_16` has 50 rows at 16x16, with independently drawn conditions. A literal N_hf
sweep on the scored grid is impossible and manufacturing one is barred by immutables 1 and
11. So the mandate splits into the two measurable halves it was really asking for:

- **the marginal value of an HF sample**, measurable exactly and exhaustively on the
  scored rung over n in {1,2,3,4,5};
- **whether the gap closes with a 20x larger design**, measurable within each rung at
  n_fit in {4, 16, 40, 80} without ever mixing rungs.

Together they answer "sample-limited or architecture-limited?" without extrapolation.

### Step 4 — Alternatives weighed and rejected

- **A1. Close the stream (row B).** Rejected: B3's own escape clause fires (step 1), the
  verdict calls a bare close not retrieval-supported, and the slot would produce no card.
  The futility statement remains worth shipping — I recommend it to the maintainer as a
  *report* item (row B-prime's own framing), not as this slot.
- **A2. Sharp-panel N=400 overfitting anatomy** (the other half of the 12.4 sentence).
  Rejected: B3's part 7 says the sharp panel closes, and its band result already bounds
  every stream's test-time predictor there; a re-measurement would change nobody's next
  action. B3's cross-stream note (b) is a *bound*, and I am not going to re-derive a bound.
- **A3. Reproduce r2s3-B3's `A1_lf_cov` arm and sweep n on it.** Rejected as a scope and
  role violation: 12.4 says "r2s4 measures, r2s3 optimizes", and re-implementing another
  stream's lever to sweep it is optimisation. The card instead *bounds* that arm from the
  outside using the condition-only envelope (step 5), which needs none of its code.
- **A4. HF-sample-equivalent currency for the LF effect** ("LF coverage is worth X HF
  samples"). Rejected: reading X off the curve requires extrapolating past n = 5, which
  the verdict forbids outright (https://arxiv.org/abs/2103.10948). Replaced by the
  one-sided *bounding* statement in step 5, which is extrapolation-free.
- **A5. n_eff / effective-sample-count estimator** (named in 12.4's own sentence).
  Rejected on the verdict's explicit instruction: two batches of dead ends,
  "n_eff is not a citable diagnostic". Demoted to descriptive design-coverage statistics
  (`tools/design_coverage_audit.py`), labelled descriptive on the card.
- **A6. Add cross-rung transfer arms to enrich the ladder.** Rejected: that is r2s3's
  `A1_lf_cov`, already run, and mixing rungs would reintroduce the non-nestedness problem
  the native-grid design avoids.
- **A7. Wider capacity sweep (widths 8/16/32/64).** Trimmed to two levels {32, 8} at
  n in {1,3,5}: F3 only needs the capacity contrast at the scored n, and the leg budget
  has to stay inside B3's 92-min envelope.

### Step 5 — The bounding claim that pays the round back

The card reports `[min, max]` of condition-only test skill over all 31 subsets x 3
replicates, and asks whether `r2s3_lf_train_signal-B3`'s ifc `A1_lf_cov` skill
**2.150091575784423** lies inside or outside that envelope, with the margin. If it lies
outside by more than the MCE, the round gets a sentence it currently cannot write: *LF as
a training signal delivers on ifc_poisson what no HF sample count in the accessible range
delivers* — which underwrites r2s3-B3's criterion-1 leg and r2s2-B3's ifc leg. If it lies
inside, the same measurement bounds those claims honestly: the LF effect is reproducible by
sample count alone in the accessible range and must be reported as such. Either way the
slot changes what the round can say, which is B3's own test for warranting a B4.

## Proposal

**Category**: diagnostic / ifc_poisson few-HF anatomy — exhaustive HF-subset learning
curve + within-rung generalisation-gap ladder on the non-nested ifc ladder, with a
pre-registered equivalence outcome.

**Card type**: `diagnostic` (WITH training, the 12.4 exception; strict 1 card seed).

**Motivation** (quotes the batch-4 prior-art verdict, row A, verbatim):
> **No fetched source performs a train-vs-test error decomposition for a field-valued
> condition→HF surrogate at single-digit HF sample counts.** Also uncited: doing it in
> copy-LF-skill units against a *pre-certified* per-dataset min-claimable-effect, and on
> an explicitly non-nested ladder whose rungs are therefore independent designs.

This card is exactly that composition and nothing more: the train-vs-test decomposition is
done at n in {1..5} on a field-valued condition→HF surrogate, in copy-LF skill units
against the pre-certified ifc `min_claimable_effect` 0.9377041289531141, on a ladder that
is called non-nested by citation (https://arxiv.org/abs/2407.17087,
https://arxiv.org/html/2408.17075v2) and never presented as a discovery. It executes the
one un-executed 12.4 mandate on the only panel dataset where a round success criterion is
still live, and it is the measurement that either underwrites or bounds
`r2s3_lf_train_signal-B3`'s ifc leg (8.13438381993564 -> 2.150091575784423) and
`r2s2_stacked-B3`'s in-build ifc leg.

**Concrete config**

New from-scratch family `models_r2/r2s4_b4_anatomy/` (`manifest.json`, `model.py`,
`subsets.py`, `rung_cv.py`, `smoke_eval.py`, `INSPIRATION.md`) plus one probe
`probes/few_hf_anatomy.py`. Backbone re-implemented from `models_r2/r2s4_cert_min`
(= r2s4-B1) with provenance comments — width 32, 2 FiLM-FNO blocks, 16 modes, FiLM-MLP
width 64, ~1.06M params; optimizer/schedule/normalisation byte-identical to B1/B2/B3
(AdamW 1e-3, wd 1e-5, batch 16, cosine, clip 1.0, MSE in `train_zscore_global`, 200
epochs). Reads `stripped_data/ifc_poisson` only, at train and at test. NO round-1 reuse.
**All legs run inside ONE `smoke_eval.py` invocation with a single dataset load** (B2/B3
pattern) — this is what keeps 201 legs inside the envelope.

*Leg group A — exhaustive HF-subset curve on the scored rung (`fidelity_64`, N = 5).*
For n in {1,2,3,4,5}, ALL C(5,n) subsets (31 total) x R = 3 **in-job replicate init
seeds** derived deterministically from `R2S4B4_SPLIT_SEED = 0` (declared in-job
replicates, NOT card seeds — the B3 5-fold precedent), at width 32 = 93 trainings; plus
width 8 at n in {1,3,5} (16 subsets) x 3 = 48 trainings. Each leg records: **in-sample
nRMSE on its own n rows**, the frozen 128-row `test_hf` nRMSE and skill (paper bar 0.036),
the 5-n unused HF rows as a micro-holdout (descriptive, n < 5 only), and the three floor
arms **recomputed on the same n rows** (`nn_condition` / `train_mean` / `zero`).
**Primary scored arm** written to `splits.test_hf`: n = 5, width 32, replicate 0.

*Leg group C — within-rung generalisation-gap ladder (rungs are independent designs).*
5-fold CV inside each rung, folds fixed by `R2S4B4_SPLIT_SEED`, width 32, R = 3
replicates: `fidelity_8` (n_fit 80, 8x8), `fidelity_16` (n_fit 40, 16x16),
`fidelity_32` (n_fit 16, 32x32), `fidelity_64` (n_fit 4, 64x64) = 60 trainings. Per rung:
in-sample rel-L2, held-out-fold rel-L2 (rung-native, dimensionless), `gap = held_out -
in_sample`, `gap_ratio = held_out / in_sample`, plus the rung's own `train_mean` and
`nn_condition` floors so "has it learned anything here" is answerable at every rung.
**No cross-rung training and no cross-grid interpolation in any adjudicating column.**

*Leg group D — bridging column, REPORT-ONLY, adjudicates nothing.* Each group-C fold
model's prediction lifted to 64x64 via
`factory_mffp/models/_common/lf_registration.py::resample_fields(..., dataset_name=
"ifc_poisson")` (= `legacy_cell_centred`, the ADR r2-0001 convention;
`eval/panel_data.py:48`), scored on the 128-row HF test set. Zero extra training. Carries
its one-sided resolution confound explicitly plus the group-E band-energy caveat.

*Leg group E — training-free pre-registration, written to the diagnostic JSON BEFORE any
arm is scored* (B3's pattern): (1) frozen ifc floor reproduction to 1e-9 relative —
`nn_condition` 10.054890929609687, `train_mean` 11.206332455369639, `zero`
27.77777777777778, with `ref_zero` == 1.0 exactly; (2) non-nestedness certificate via
`tools/ladder_pair_alignment_audit.py --fail-on mispaired` over all rung pairs, recording
min pairwise standardised condition distance (B2 T2-F6 reproduction), cited not claimed;
(3) `tools/band_retention_probe.py` on the 128 HF test fields — fraction of test-field
energy above each rung's Nyquist (8/16/32 vs 64), the one-sided bound on group D;
(4) `tools/design_coverage_audit.py` nearest-neighbour standardised condition distances
per rung, **labelled a descriptive statistic, explicitly NOT an n_eff diagnostic**.

*Leg group F — mis-specification guards (B3's promoted rule),
`tools/ledger_contamination_audit.py`.* (i) **Control column**: the N-axis contrast
compares the SAME estimator at different n — architecture, budget and procedure identical
— so the function-class term is identically zero by construction and no control column is
needed; the width-32-vs-8 contrast IS a function-class contrast, is labelled as such, and
is never summed with an N effect. (ii) **Matched n_fit**: inherently unmatched on the
N-axis because n IS the treatment (declared); asserted equal within every (n, width) cell
and within every rung fold. (iii) **Ceiling before threshold**: report
`D(pred_{n=1}, pred_{n=5})` on the test set before reading any delta against the MCE — if
the triangle-inequality headroom is below the threshold the comparison could not have
fired and a surviving null is not evidence.

*Statistics, pre-registered.* Primary estimand `Delta_5_1 = mean_skill(n=1, w32) -
mean_skill(n=5, w32)` over all subsets x replicates (positive = more HF samples help,
skill lower-is-better). 90 % CI by stratified bootstrap, B = 10000, rng seed 0 (Agarwal
et al., https://ar5iv.labs.arxiv.org/html/2108.13264 — B1's adopted protocol), stratified
by n over (subset, replicate) cells. Secondary paired column: all 120 nested chains
S1 c ... c S5, zero extra training, the in-job paired control the drift-class rule
requires. **Equivalence bound = the certified ifc `min_claimable_effect`
0.9377041289531141.** Three pre-registered outcomes, TWO of which are claims:
- **O1 EFFECT** — 90 % CI entirely above +0.93770 -> "HF sample count is a binding
  constraint on ifc_poisson within the accessible range."
- **O2 EQUIVALENCE** (informative null; Harms & Lakens, PubMed 30873486) — 90 % CI
  entirely inside [-0.93770, +0.93770] -> "over the entire accessible HF range 1->5,
  marginal HF samples buy less than the round's certified minimum claimable effect; the
  8.13x gap to the paper bar is not attributable to marginal HF sample count at this
  scale."
- **O3 INCONCLUSIVE** — CI half-width > 0.93770 -> reported as inconclusive with the
  measured half-width quoted; pre-stated so it cannot be spun after the fact.

*Bounding claim (round-economics deliverable, extrapolation-free).* Report [min, max] of
condition-only test skill over all 31 x 3 group-A cells and state whether
`r2s3_lf_train_signal-B3`'s ifc `A1_lf_cov` **2.150091575784423** lies inside or outside
it, with the margin against the MCE.

*Forbidden claims, pre-registered on the card.* No scaling law or sample-complexity
extrapolation from the curve or the ladder (https://arxiv.org/abs/2103.10948, "no
universal model can be identified"); no ceiling / information-gap claim at N_hf = 5
(https://arxiv.org/abs/2410.23440); no `n_eff` diagnostic claim. **A non-monotone curve or
ladder is a RESULT, not a harness bug** — the published ill-behaved-learning-curve
phenomenon (https://arxiv.org/abs/2211.14061, "more data does not necessarily lead to
better generalization performance"), pre-registered here so the outcome cannot be
mistaken for a failure.

*Checkpoint-resume*: B3's pattern — a single `<ckpt_dir>/last.pt` holding completed-leg
results plus the in-flight leg's model/opt/sched/RNG state; a resumed job replays finished
legs and continues the in-flight one at its stored epoch (immutable 8).

*Target-scaler pre-flight*: the section-12 rule names `ext__helmholtz_2d` and
`sharp__phase_field_crystal_2d` only; ifc_poisson is out of scope — recorded as N/A on the
card rather than silently skipped.

**Recipe**

```json
{
  "base_family": "none (new from-scratch family; FiLM-FNO backbone re-implemented from models_r2/r2s4_cert_min = r2s4_diag-B1 with provenance comments; NO round-1 reuse; reuses only the factory data_adapters plumbing loaders.load_mf_dataset / geometry.resolve_grid / metrics.finalize_and_write and models/_common/lf_registration.py for the report-only bridging column)",
  "base_commit": "9e10d414e35a96398f7b091bc84ddf936d88acc7",
  "family_dir": "models_r2/r2s4_b4_anatomy",
  "datasets": "ifc_poisson",
  "epochs": 200,
  "seeds": [0],
  "env": {
    "R2S4B4_WIDTH": "32",
    "R2S4B4_BLOCKS": "2",
    "R2S4B4_MODES": "16",
    "R2S4B4_FILM_MLP_WIDTH": "64",
    "R2S4B4_BATCH": "16",
    "R2S4B4_LR": "1e-3",
    "R2S4B4_WD": "1e-5",
    "R2S4B4_CLIP": "1.0",
    "R2S4B4_SCHED": "cosine",
    "R2S4B4_TARGET_NORM": "train_zscore_global",
    "R2S4B4_SPLIT_SEED": "0",
    "R2S4B4_REPLICATES": "3",
    "R2S4B4_REPLICATE_SEMANTICS": "in_job_init_replicates_from_split_seed_not_card_seeds",
    "R2S4B4_SUBSET_LEVELS": "1,2,3,4,5",
    "R2S4B4_SUBSET_ENUMERATION": "exhaustive_all_31",
    "R2S4B4_CAPACITY_WIDTHS": "32,8",
    "R2S4B4_CAPACITY_LEVELS": "1,3,5",
    "R2S4B4_PRIMARY_LEG": "n5_w32_rep0",
    "R2S4B4_PRIMARY_SPLIT": "test_hf",
    "R2S4B4_RUNGS": "fidelity_8,fidelity_16,fidelity_32,fidelity_64",
    "R2S4B4_RUNG_FOLDS": "5",
    "R2S4B4_RUNG_SCORING": "native_grid_rel_l2",
    "R2S4B4_NO_CROSS_RUNG_TRAINING": "1",
    "R2S4B4_BRIDGE_COLUMN": "report_only",
    "R2S4B4_BRIDGE_REGISTRATION": "models_common_lf_registration.resample_fields",
    "R2S4B4_BRIDGE_CONVENTION": "legacy_cell_centred",
    "R2S4B4_NESTED_CHAINS": "all_120",
    "R2S4B4_PRIMARY_ESTIMAND": "delta_skill_n1_minus_n5_w32",
    "R2S4B4_CI_METHOD": "stratified_bootstrap_by_n",
    "R2S4B4_CI_LEVEL": "0.90",
    "R2S4B4_BOOTSTRAP_B": "10000",
    "R2S4B4_BOOTSTRAP_RNG_SEED": "0",
    "R2S4B4_EQUIVALENCE_BOUND": "0.9377041289531141",
    "R2S4B4_EQUIVALENCE_BOUND_SOURCE": "state/noise_floor.json:ifc_poisson.min_claimable_effect",
    "R2S4B4_OUTCOME_RULE": "O1_effect_if_ci_above_bound;O2_equivalence_if_ci_within_bound;O3_inconclusive_if_halfwidth_gt_bound",
    "R2S4B4_LF_EFFECT_BOUND_REFERENCE": "2.150091575784423",
    "R2S4B4_LF_EFFECT_BOUND_SOURCE": "experiment_cards/r2s3_lf_train_signal/batch_3/B3.json:5_actual_result.per_dataset.ifc_poisson.arms.A1_lf_cov.draw_mean_skill",
    "R2S4B4_FLOOR_ARMS": "nn_condition,train_mean,zero",
    "R2S4B4_FLOOR_ARMS_PER_SUBSET": "1",
    "R2S4B4_FLOORS_JSON": "mffp_autoresearch/round2/state/anchors/floors.json",
    "R2S4B4_FLOOR_TOL": "1e-9",
    "R2S4B4_NOISE_FLOOR_JSON": "mffp_autoresearch/round2/state/noise_floor.json",
    "R2S4B4_PREREG_TRAINING_FREE": "floor_repro,ladder_nonnestedness,band_energy_above_rung_nyquist,design_coverage",
    "R2S4B4_LADDER_AUDIT_FAIL_ON": "mispaired",
    "R2S4B4_CONTAMINATION_AUDIT": "control_column_na_same_estimator;matched_nfit_within_cell;triangle_headroom_before_threshold",
    "R2S4B4_F1_INSAMPLE_NRMSE_MAX": "0.10",
    "R2S4B4_TARGET_SCALER_PREFLIGHT": "na_ifc_poisson_not_in_scope",
    "R2S4B4_DUMP_PREDS": "1",
    "R2S4B4_GUARD_DATASETS": "heat_local,fluid,sharp__sod_1d",
    "R2S4B4_GUARD_EPOCHS": "2",
    "R2S4B4_DIAG_OUT": "mffp_autoresearch_outputs/round2/r2s4_diag/B4/eval"
  }
}
```

Recipe notes: `base_commit` = `round2-substrate` HEAD, verified by
`git rev-parse round2-substrate` = 9e10d414e35a96398f7b091bc84ddf936d88acc7. Leg budget:
93 (group A w32) + 48 (group A w8) + 60 (group C) = **201 trainings**, plus 3 guard legs at
2 epochs; every group-A leg is 200 optimiser steps on <= 5 rows of 64x64 and the largest
group-C leg is 80 rows of 8x8, all inside one process with a single dataset load. B3 ran
184 much larger legs in 92 min, so expect **45–75 min**; request `--time 02:00:00`.
Strict 1 card seed -> only `submit.sh` is needed, no `submit_seeds_2_3.sh` leg. Groups D–F
are numpy/closed-form post-processing on already-trained legs: no extra GPU, no new
dependencies.

**Expected outcome**

Own-stream anchor `certified_3seed_panel_geomean` 19.817844731907492; the adjudicating
per-dataset anchor is ifc mean skill **8.261220201059428** with MCE **0.9377041289531141**.

- **Instrument reproduction (primary leg, n = 5, w32, rep 0)**: test skill **8.0–8.6**,
  i.e. within the MCE 0.9377 of both B1's certified 8.261220201059428 and r2s3-B3's
  `A0_nolf` 8.13438381993564. Not a claim — an instrument check.
- **n = 1**: skill **10.5–13.0**, at or just above the `nn_condition` floor
  10.054890929609687 and near the `train_mean` floor 11.206332455369639.
- **Primary estimand `Delta_5_1`**: predicted **+2.0 to +4.5 skill units**, i.e. **2.1x to
  4.8x the certified MCE 0.9377041289531141** -> outcome **O1 EFFECT** expected. The
  claimed movement vs the per-dataset anchor is the *curve*, not a new best number: the
  card is a diagnostic and its primary leg deliberately reproduces the anchor.
- **In-sample nRMSE at n = 5, w32**: predicted **< 0.02** (vs test 0.2928) — a gap ratio
  > 14x, the signature of a variance/sample-limited regime. F1 fires only if it exceeds
  0.10, which is 2.78 skill units = **2.96x the MCE**.
- **Rung ladder**: `gap_ratio` ~ 30–100 at n_fit = 4 (rung 64) falling to **1.5–5** at
  n_fit = 80 (rung 8); predicted monotone-ish but non-monotonicity is pre-registered as a
  result, not a bug.
- **Bounding claim**: min over all 31 x 3 group-A cells predicted **>= 7.5**, so r2s3-B3's
  `A1_lf_cov` 2.150091575784423 sits **outside** the accessible-HF envelope by **>= 5.3
  skill units = 5.7x the MCE** -> "LF as a training signal delivers on ifc_poisson what no
  HF sample count in the accessible range delivers", underwriting r2s3-B3's criterion-1
  leg and r2s2-B3's ifc leg.
- **Floors**: reproduce to 1e-9 relative; `ref_zero` == 1.0 exactly.
- **vs the noise floor**: every adjudicating threshold is the certified ifc
  `min_claimable_effect` **0.9377041289531141** or `max(that, the in-job subset x
  replicate spread)`, so it exceeds the floor by construction; ifc is the only dataset the
  card cites, and its floor is the only one that applies.

**Expected falsification** (one sentence): the card's hypothesis — *"at N_hf = 5 on
ifc_poisson the condition→HF surrogate is variance/sample-limited rather than
architecture-limited: it fits its 5 training rows to near-zero in-sample error while test
error sits at ~8x the paper bar, marginal HF samples move the test skill by more than the
certified MCE over 1->5, and the generalisation gap closes as the within-rung design grows
20x"* — is falsified if ANY of: **(F1)** in-sample nRMSE at n = 5, width 32 exceeds
**0.10** (= 2.7778 skill units, 2.96x the MCE 0.9377041289531141 = 0.03376 nRMSE), i.e.
the model cannot even fit 5 fields and the failure is optimisation/architecture, not
samples; **(F2)** outcome **O3** fires — the 90 % CI half-width on `Delta_5_1` exceeds
0.9377041289531141, so neither an effect nor equivalence is declarable; **(F3)** the
width-8 arm beats width-32 at n = 5 by more than
`max(0.9377041289531141, in-job subset x replicate spread)`, i.e. capacity control rather
than sample count is the binding lever; **(F4)** the rung `gap_ratio` at n_fit = 80 is not
smaller than at n_fit = 4 by more than the in-job fold spread, i.e. a 20x larger design
does not close the generalisation gap on this PDE; or **(F5)** any frozen ifc floor
deviates from `state/anchors/floors.json` by > 1e-9 relative or `ref_zero` != 1.0 exactly
(which would invalidate every ifc number in the round and is the card's highest-value
outcome). *Attached floor-arm reasoning (spec section 3 / program 2.2)*: the three
mandatory floor arms `nn_condition` / `train_mean` / `zero` are reported beside the model
at **every** n — not just at n = 5 — so the "has this learned anything" comparison exists
at every point of the curve; at n = 5 they must reproduce the frozen
10.054890929609687 / 11.206332455369639 / 27.77777777777778 to 1e-9, and any curve point
where the model does not beat its own-n best floor by more than the MCE is **reported but
not claimed**. A non-monotone curve or ladder is pre-registered as the published
ill-behaved-learning-curve phenomenon (https://arxiv.org/abs/2211.14061), NOT a
falsification and NOT a harness bug.

**Anchor reference**: `null` (program 4.5 / section 12 — all four round-2 streams are
gap/lever/diag; the own-stream anchor 19.817844731907492 and its ifc component
8.261220201059428 are implicit; round 2 has no champion-re-targeting tuning stream).

## Immutables self-check

Positive evidence for each of program.md section 5's 8 items plus the 3 round-2 extras.

1. **Data read-only.** The card creates no data. It uses the 5 existing HF train rows and
   the existing rung files; every "N level" is a *subset* of rows already on disk, never an
   addition. `train/fidelity_64` stays (5, 64, 64) and the 128-row test set is untouched.
   No LF is ever downsampled from HF: the rungs are read as shipped and group C trains each
   rung on its OWN grid, so no field is ever produced by decimating an HF field. The single
   resampling in the whole card is group D's *prediction* lift, and it is an upsample.
2. **Panel + guard set fixed.** The card scores one existing panel dataset (`ifc_poisson`)
   and runs the three existing guards (`heat_local`, `fluid`, `sharp__sod_1d`) at contract
   tier via `R2S4B4_GUARD_DATASETS` / `R2S4B4_GUARD_EPOCHS=2`. No dataset is added, removed
   or reweighted; a single-dataset diagnostic is the B3 precedent
   (`R2S4B3_LEDGER_DATASETS` scoped the ledger to 5 of 6).
3. **Eval layer / spec untouched.** Nothing in the design requires editing `round2/eval/`,
   `project.yaml`, `program.md` or any agent prompt. `eval/panel_data.py` is consulted
   read-only (line 48, the `LEGACY_CELL_DATASETS` membership) and `score_panel.py` is
   invoked with its existing CLI plus `--env` knobs; `eval/nrmse.py` is used through
   `finalize_and_write`, unmodified.
4. **One nRMSE definition.** Every scored number flows through
   `data_adapters.metrics.finalize_and_write` -> `eval/nrmse.py`; the primary leg writes
   `splits.test_hf` exactly as B1/B2/B3 did, and the result JSON carries `nrmse_def_hash`
   d3d0ade9191c13bacc40702f3eb26ad290e01641cacee22a1d2233b74c035850 and `copylf_def_hash`
   9753ff24e856f595748492dec6cb6c215d748f97e8ec4a679b651f8846da907a. The rung-native
   rel-L2 of group C is the *same per-sample relative-L2 formula* applied on the rung grid,
   reported as a diagnostic column and never mixed into a scored skill.
5. **Contract CLI fixed.** The family exposes the unchanged six-arg
   `--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed` signature; all 51 knobs
   above live in `recipe.env` and reach the family only via `score_panel.py --env`, which
   is how they enter the cache key. No new CLI flag is introduced.
6. **Seeds and tier epochs fixed.** `seeds: [0]` — strict 1-seed in-round (program 4.2);
   `epochs: 200` — the smoke tier; guards at 2 = contract tier. The R = 3 replicates are
   *in-job* init replicates derived from `R2S4B4_SPLIT_SEED`, declared as such in
   `R2S4B4_REPLICATE_SEMANTICS`, exactly as B3's 5 outer folds and B2's fold-fixed spread
   supplied in-job paired distributions on strict-1-seed cards. They are never reported as
   a seed CI.
7. **Guarded factory surfaces untouched.** The only factory paths touched are read-only
   imports: `factory_mffp/data_adapters/{loaders,geometry,metrics}` and
   `factory_mffp/models/_common/lf_registration.py` (import, no edit — and `models/_common`
   is under `models/**`, the one modifiable tree, so even an accidental write would not hit
   a guarded surface). Nothing under `factory_mffp/{eval,baselines,references,scripts,data}`
   or `akash/` is read or written, and `factory.md` is not touched.
8. **Checkpoint-resume from `<ckpt_dir>/last.pt`.** Implementable and specified: B3's
   pattern is adopted verbatim — one `last.pt` holding the completed-leg result list plus
   the in-flight leg's model/opt/sched/RNG state, so a preempted job replays finished legs
   from the stored results and resumes the in-flight leg at its stored epoch. With 201
   short legs this is strictly easier than B3's 184-leg version, which shipped and passed
   review.
9. **Falsification thresholds exceed the noise floor, numbers quoted.** The card cites
   exactly one dataset. `state/noise_floor.json -> ifc_poisson.min_claimable_effect =
   0.9377041289531141` (= max(spread_maxmin 0.9377041289531141, paired_null_95
   0.9227235526286076)). F2's decision bound IS that constant; F3's threshold is
   `max(0.9377041289531141, in-job spread) >= 0.9377041289531141`; F1's 0.10 in-sample
   nRMSE equals 0.10 / 0.036 = **2.7778 skill units = 2.96x** the MCE (the MCE in nRMSE
   units is 0.9377041289531141 x 0.036 = **0.03375735**); the bounding claim's predicted
   margin >= 5.3 skill units is **5.7x** the MCE; F5's 1e-9 floor tolerance is a
   reproduction identity, not an effect, and is B1's certified tolerance. F4 is thresholded
   on the in-job fold spread, which is measured in-job and reported. No threshold anywhere
   sits below 0.9377041289531141.
10. **Not a pre-falsified lever.** The three round-1 pre-falsified levers are the WNO
    backbone swap, LF low-mode freezing, and a diffusion prior for point accuracy. The
    nearest is **LF low-mode freezing**: this card touches no LF spectrum, freezes nothing,
    and in fact never mixes LF into any training arm — group C trains each rung
    independently on its own grid and cross-rung training is explicitly disabled
    (`R2S4B4_NO_CROSS_RUNG_TRAINING=1`). The card is a measurement of an existing arm's
    sample dependence, not a mechanism proposal, so no lever is re-proposed as-is.
11. **Floor arms.** This is a `diagnostic` card, but it carries a scored `test_hf` leg, so
    it reports the mandatory arms anyway and goes further than the requirement: the
    `nn_condition` / `train_mean` / `zero` arms are recomputed **per subset at every n**
    (`R2S4B4_FLOOR_ARMS_PER_SUBSET=1`) and appear in the `expected_falsification` attached
    reasoning above, with the n = 5 values pinned to the frozen
    `state/anchors/floors.json` numbers 10.054890929609687 / 11.206332455369639 /
    27.77777777777778 at 1e-9 tolerance (F5), and with the standing rule that a curve point
    not beating its own-n best floor by more than the MCE is reported but not claimed.

**Verdict: pass (11/11).** No revision required; no iteration 2 needed.

## Status

- **Slot covered** — one proposal, `card_type: diagnostic`, category as above. Not skipped.
- **B4-or-close decision**: **B4**, on the ground that B3 part 7's own escape clause
  ("close … unless the maintainer judges criterion 1 … still reachable") is satisfied by
  `r2s3_lf_train_signal-B3`'s ifc `A1_lf_cov` 2.150091575784423 (effect 5.984292244151218
  vs MCE 0.9377041289531141) and by `r2s2_stacked-B3`'s in-build ifc leg, and that row B's
  bare close is not retrieval-supported. **Recommendation carried to the maintainer**: ship
  row B-prime's futility/equivalence statement as a *round-report* artifact regardless of
  this card's outcome — the verdict calls it "a report artifact, not an experiment card",
  so it is not this slot's business but it should not be lost.
- **Reopen candidates**: none exist for this stream (all three prior cards
  `reopen_candidate: false`); nothing to resolve.
- **Immutables self-check**: **pass (11/11)**.
