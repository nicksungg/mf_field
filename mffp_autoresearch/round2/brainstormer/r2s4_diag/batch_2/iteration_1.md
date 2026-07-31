# Iteration 1 — Stream `r2s4_diag`, Batch 2

## Design context considered

- `summary_so_far.md` §6 (the seven unknowns) and the batch-2 prior-art verdict.
- program.md §12.4 verbatim (quoted in the summary), §1 criterion 1, §2.2 floor arms,
  §2.3 panel + best-floor table, §2.4 tiers, §5 immutables 1-13, §4.2 seed protocol,
  §13.1 ADR r2-0003.
- Stream anchor `state/anchors/r2s4_diag.json`: `certified_3seed_panel_geomean`
  **19.817844731907492**, CI95 [19.3853, 20.5271], source card r2s4_diag-B1.
- `state/noise_floor.json` (`_provisional: false`) per-dataset `min_claimable_effect`:
  helmholtz 2.95299157437233, ifc_poisson 0.9377041289531141, allen_cahn
  0.8797047190126648, cahn_hilliard 0.09124535322300886, fisher_kpp 0.0007136812826775696,
  pfc 0.21302734961699343, panel geomean 1.1418668211296108.
- `state/anchors/floors.json` (mandatory floor arms, test skill): helmholtz nn 4.3853 /
  mean 14.6107 / zero 3.3441; ifc_poisson 10.0549 / 11.2063 / 27.7778; allen_cahn 269.1959
  / 562.0295 / 561.5560; cahn_hilliard 23.1803 / 23.9691 / 23.9217; fisher_kpp 16.3379 /
  11.9931 / 46.6211; pfc 68.5555 / 59.8118 / 135.4871.
- `eval/copylf_baselines.json` + `eval/panel_data.py::copylf_prediction`: the copy-LF
  reference uses `lf_fid = max(data["lf_fids"])` (the FINEST LF rung) and the per-dataset
  registration convention `node_aligned_periodic` / `dirichlet_node` /
  `legacy_cell_centred` (ADR r2-0001).
- `stripped_data/`: train LF IS present (`train_l1.npz`, `train_l2.npz`, `train_l3.npz`);
  only `test_l*` below HF is absent. Verified per dataset. So a train-time LF signal is
  available without ever touching `data_root`.
- `state/timing_ledger.json`: r2s4_cert_min ran 6 datasets x 200 epochs in **4.13-4.42 min**
  per seed on h200. Compute is not a binding constraint for this stream.
- The immutables block (§4.5 of my prompt) verbatim, plus round-2 additions 9-13.
- Pre-falsified levers (r1 §5): WNO backbone swap, LF low-mode freezing, diffusion prior
  for point accuracy.

## Proposal reasoning

### Step 1 — what the slot must be

program.md §12.4 names three later-batch directions (value-of-LF accounting; overfitting
anatomy at N_hf in {5,20,50}/400; floor certification). Floor certification is DONE (B1,
F3 reproduced at relative difference exactly 0.0 on 9 datasets x 3 arms). Round 2 is at
batch 2 of ~3 and **criterion 1 of the round is r2s4's** and is still entirely unmeasured
(summary §6.1). So the slot is the value-of-LF accounting card. The only real design
question is *how* to pose it so that the overwhelmingly likely null is interpretable.

### Step 2 — why a bare +/- LF contrast would waste the slot

Three independent priors say the naive contrast returns ~0 at N=400:

- r2s4-B1 T2-F1/T2-F2: the certifier is at 1.010x / 1.139x / ~1.11x a training-free
  aleatoric barrier on fisher_kpp / pfc / allen_cahn. B1's own H8: "a null result there
  would be uninformative about LF."
- r2s1-B1 I1: "THE ARCHITECTURE IS NOT THE BINDING CONSTRAINT... the condition determines
  1-3 out-of-fold degrees of freedom per dataset." An LF training signal cannot add
  degrees of freedom to a condition-only test-time map; at N=400 it cannot even improve
  the *estimation* of 1-3 DOF, which is already saturated.
- r2s2-B1 sidecar S2: a real-LF corrector reaches nRMSE 1.7e-7-5.9e-3. So LF is not
  short of information — the bottleneck is the condition-only test interface.

The websearcher's instruction 1 says exactly this: "D1 is the batch's strongest card and it
is now an adjudication, not a hunt for a gain... Write the null as the pre-registered
expectation." A null with no positive control and no mechanism is worth nothing; the design
work is entirely in making the null load-bearing.

### Step 3 — the adopted design (DOPD advantage-gap, ported to fields)

Websearcher instruction 2: "Adopt DOPD's advantage-gap design instead of inventing a
contrast. Compare an LF-consuming teacher and a condition-only student *on the same
samples* and split the error into a capability gap and an information gap."

The port has one hard constraint the source does not: immutable §5.9 forbids scoring any
LF-consuming model on the test split (the test LF files are physically absent from
`stripped_data`). So the advantage-gap legs must live entirely on a held-out **inner fold
of the TRAIN split**, where LF exists. That is not a compromise — it is what makes the
decomposition legal and auditable:

- **Information gap** (inner fold, LF available): `I1_lf_teacher` (coords + upsampled real
  LF as an input channel) vs `I2_lf_ablated` (identical architecture, identical budget, the
  LF channel replaced by the constant train-mean LF field, retrained from scratch). Same
  architecture, only the *information* in the privileged channel differs — the clean
  ablation, not an architecture comparison.
- **Capability gap** (inner fold, free — both models already trained): `T0_cond_only` vs
  `I2_lf_ablated`. Isolates the extra input channel's capacity from its information.
  Pre-registered ~0 from r2s1-B1 I1.
- **Transfer gap** (test split, condition-only at test): `T0_cond_only` vs `T1_lf_aux`
  (same trunk, one extra 1x1 head predicting the upsampled LF field as an auxiliary
  training target; at test only the HF head runs, so the scored forward signature is
  byte-identical to T0's). This is criterion 1's matched +/- LF-training contrast.

The headline statistic, declared a **project convention** (websearcher instruction 6 —
n_eff has no literature standard, and neither does this):

    transfer_efficiency := [nRMSE(T0, test) - nRMSE(T1, test)]
                           / [nRMSE(I2, inner) - nRMSE(I1, inner)]

"of the LF information that demonstrably exists, what fraction crosses a condition-only
bottleneck." Reported as undefined when the denominator is below its own in-job null.
Caveat to be carried on the card: numerator and denominator live on different splits of the
same generator.

### Step 4 — the addition that makes the null a positive result

r2s1-B1 I1 (1-3 identifiable DOF) plus r2s4-B1's barriers imply a sharper, *risky*
prediction than "LF adds nothing":

> **LF-as-training-signal can only pay where the condition-only estimator is SAMPLE-limited,
> not where it is INFORMATION-limited.**

At N_fit=320 the sharp panel is estimation-saturated (1-3 DOF from 320 samples) -> predict
zero. At N_hf=5 (ifc_poisson) it is severely sample-limited -> predict the only claimable
full-N effect, and r2s3-B1 already observed a large one there (-7.3497, harmful direction).
That prediction is directly testable *inside this card* by sweeping the fit-fold size:
train T0 and T1 at **N_fit in {20, 80, 320}** on the five N=400 datasets, holding the val
fold, the inner fold and the test split fixed and nesting the subsamples. The effect must
GROW as N falls. This is the D4 "overfitting anatomy" direction folded into the D1 card at
near-zero marginal cost (smaller fits train faster), and it is the composition the
websearcher's D1 row calls open, grounded in the MF-scaling-law citation
(https://arxiv.org/abs/2511.01830) and Yang et al.'s non-monotone LUPI law
(https://arxiv.org/abs/2209.08754).

### Step 5 — the shrinkage column (B1 part 7 item 3, websearcher instruction 4)

B1 asks for train-fold-calibrated shrinkage as a REQUIRED arm; the websearcher says sell
lambda*, not the shrinkage, and warns that FALCON needs ~1000 calibration points while our
inner fold has <=40. Resolution: shrinkage is a **reported column, not an arm**. Every arm's
test predictions are scored twice — raw, and after `P_bar + lambda*(P - P_bar)` with
lambda* fitted on the **inner fold** (never on test, unlike B1's T3-F1 oracle) — and
lambda* plus a bootstrap CI (B=2000 over the <=40 inner points) is a mandatory column. Zero
extra training. It also buys power exactly where the card needs it: helmholtz's certified
constant 2.95299 is large *because* the seeds learn mutually near-orthogonal harmful
condition-dependence (B1 T1-F5), which is what lambda* removes (6.1725 -> 3.5214 in B1's
oracle), so the re-certified spread of the shrunk column should be far smaller than 2.95299
on the one dataset with certified headroom.

### Step 6 — re-certification (B1 part 7 item 4, websearcher instruction 7)

B1's constants were measured on an arm that is conditional-mean-collapsed on 3 of 6
datasets and are a LOWER bound (H5). fisher_kpp's 0.00071 is plainly unusable for an arm
carrying an auxiliary head. So the card defines the **operative threshold** as

    operative_threshold(ds) = max( certified min_claimable_effect (state/noise_floor.json),
                                   in-job 3-seed paired spread of the two compared arms )

which is >= the certified floor for every dataset **by construction**, and discharges item
(4) by re-certifying on the arm actually compared. This requires seeds {0,1,2} — the same
justification §12.4 gave B1 ("the exception is the point"), and immutable 6 fixes the seed
set to exactly {0,1,2}. Cost: 3 jobs, each ~30-45 min by the timing ledger
(r2s4_cert_min: 4.13-4.42 min for 6 datasets x 200 epochs; this card is ~44 trainings/seed
vs B1's 6, most of them on smaller fit folds).

### Alternatives weighed and rejected

1. **Distillation student (`T2_lf_distill`) as a second with-LF mechanism.** Rejected for
   scope: the KD teacher would be queried only at train conditions where HF is already
   known, adding a teacher-quality confound to a measurement card, and program.md §12.3
   assigns distillation to r2s3 ("r2s4 measures, r2s3 optimizes"). The I1 teacher is
   trained anyway, so a B3 can add the student for one extra training if
   transfer_efficiency turns out non-zero. Recorded as the cheapest follow-on.
2. **Building a ceiling estimator that works at 19 dims / N_hf=5** (B1 part 7 item 2).
   REJECTED on the websearcher's explicit instruction 3: D2 is `preempted` at the method
   level and "the 19-dim failure is a **known theorem-level property**, not a bug"; at
   N_hf=5 arXiv:2410.23440 says no ceiling claim is defensible. The card instead uses a
   *relative* LF-present-vs-ablated measurement, which needs no absolute ceiling and
   therefore works on cahn_hilliard and ifc_poisson — the exact datasets B1 called the
   round's blind spot.
3. **Using ifc_poisson's extra ladder rungs (20/50 lower-fidelity samples) as the LF
   signal.** Rejected: it changes the sample count and breaks "same budget", it is r2s3's
   lever, and r2s3-B1 already ran it (-7.3497 on ifc). This card uses only the **aligned**
   train LF at the same conditions as the HF samples — a pure privileged-information
   (LUPI) setting, identical in construction on all 6 datasets.
4. **Posing the contrast on helmholtz only** (B1 part 7 item 1 read literally). Rejected as
   too narrow: criterion 1 asks for >=3 panel datasets, and the barrier-bound datasets are
   needed as the instrument's positive control (they are where the information gap is known
   to be huge because the realized IC lives in the LF field — ADR r2-0003). helmholtz is
   still first in reporting priority.
5. **Overfitting anatomy as a standalone card.** Rejected: it would duplicate the training
   matrix. Folded in as the N_fit sweep, where it does double duty as the risky prediction.

## Proposal

- **Category**: `diagnostic / value-of-LF accounting (DOPD advantage-gap ported to fields)
  + HF-sample-count scaling of the transfer effect`
- **Card type**: `diagnostic` (WITH training — the §12.4 exception B1 established:
  `epochs = 200`, `seeds = [0,1,2]`)
- **Motivation**: the batch-2 prior-art verdict row D1 reads
  `preempted-but-MF-composition-open (cite)` — "Nothing found pre-registers the null
  datasets **from a measured training-free ceiling**, nor uses LF *fields* as privileged
  info for a *field-valued* output scored in copy-LF skill. Concrete adoptable design:
  DOPD's advantage-gap split (capability gap vs information gap) ported to fields."
  This card is that composition: B1's measured barriers pre-register the nulls, and the
  advantage-gap split is adopted by citation rather than invented. It also discharges
  program.md §1 criterion 1 (the round's only unmeasured success criterion) and B1 part 7
  items (1), (3) and (4).

- **Concrete config** — new from-scratch family `models_r2/r2s4_b2_lfvalue/`
  (`manifest.json`, `model.py`, `smoke_eval.py`, `INSPIRATION.md`) plus one probe
  `probes/lf_value_accounting.py`. Backbone identical to r2s4_cert_min (width 32, 2
  FiLM-FNO blocks, 16 modes, FiLM MLP width 64, ~1M params), re-implemented in the new
  family dir with a provenance comment; optimizer/schedule/normalization identical to B1
  (AdamW 1e-3 / wd 1e-5, batch 16, cosine, clip 1.0, MSE in `train_zscore_global` target
  space, 200 epochs).

  **Folds** (fixed by `R2S4B2_SPLIT_SEED=0` — identical for every arm, every N level and
  every training seed, so the training seed varies only init/shuffle):
  fit 0.8 / val 0.1 (model selection ONLY) / **inner 0.1 (LF-available evaluation +
  lambda* calibration ONLY, never used for selection)**. Round-1's D3 val_idx
  double-consumption caveat (§12.1) is the reason the two are disjoint and separately
  named. On ifc_poisson (N_hf=5) val and inner are disabled (`VAL_MIN_N=20`,
  `INNER_MIN_N=20`); final-epoch weights, B1's recorded caveat.

  **LF definition** (identical on every dataset): the **finest** train LF rung,
  `lf_fid = max(lf_fids)` — the same rung `eval/panel_data.py::copylf_prediction` uses for
  the skill denominator — upsampled to the HF grid with the **same** per-dataset
  registration convention (`node_aligned_periodic` / `dirichlet_node` /
  `legacy_cell_centred`, ADR r2-0001), vendored into the family dir with a provenance
  comment and asserted to agree with `eval/panel_data.py`'s upsampler on the TRAIN split
  during the contract-tier run (a read-only call; the eval layer is not edited). Only
  `stripped_data` is read, at train and test.

  **Arms** (all same backbone, same optimizer, same budget, same folds):
  1. `T0_cond_only` — condition-only; **PRIMARY scored arm** (`splits.test_hf`). The
     without-LF arm and the in-job paired control (drift-class rule).
  2. `T1_lf_aux` — same trunk + a second 1x1 head predicting the upsampled LF field;
     loss = MSE_HF + `AUX_WEIGHT` * MSE_LF with a **separate LF scaler** (r1 s5 revin_lf
     two-scaler finding, §12.3: "normalization transfer across fidelities is a solved
     sub-problem; reuse it, don't rediscover it"; also the mechanism r2s3-B1's crater is
     currently attributed to). At test only the HF head runs -> scored forward identical
     to T0. The with-LF-training arm.
  3. `I1_lf_teacher` — coords(2ch) + upsampled real LF(1ch) input; trained on fit,
     selected on val, evaluated on **inner ONLY**. Structurally has no test code path.
  4. `I2_lf_ablated` — identical to I1 with the LF channel replaced by the constant
     train-mean LF field (computed on the fit fold), retrained from scratch; inner ONLY.
  On ifc_poisson, I1/I2 run as a 5-fold leave-one-out (5 samples) and every number from
  them is labelled **anecdote-grade** and excluded from every falsification clause
  (arXiv:2410.23440: at N_hf=5 no ceiling claim is defensible).

  **N_fit sweep**: T0 and T1 additionally at `N_FIT_LEVELS = 20,80` (nested subsamples of
  the same fit fold; 320 is the full leg) on the five N=400 datasets. val/inner/test are
  held fixed across levels.

  **Reported columns (mandatory, every arm x dataset)**: raw and shrunk skill
  (`P_bar + lambda*(P - P_bar)`, lambda* on a 0.0:1.5:0.05 grid fitted on the **inner
  fold**), lambda* with a B=2000 bootstrap CI over the <=40 inner points, the three floor
  arms `ref_nn_condition` / `ref_train_mean` / `ref_zero` recomputed through the same
  nRMSE path (§2.2, B1's merge pattern, leaving `test_hf` byte-identical), the paired
  per-seed deltas, the in-job 3-seed spread of every compared pair, the operative
  threshold, `information_gap`, `capability_gap` and `transfer_efficiency`.
  Guard leg at contract tier (2 epochs, heat_local / fluid / sharp__sod_1d), as B1 did.

  Adapted-on-use from `tools/`: `conditional_mean_collapse.py` (shrinkage / lambda* /
  own-mean-broadcast) and `condition_predictability_ceiling.py` (barrier numbers for the
  pre-registration table); adapted versions to be promoted via the register turn.

- **Recipe**:

```json
{
  "base_family": "none (new from-scratch family; backbone re-implemented from models_r2/r2s4_cert_min = r2s4_diag-B1, same round, with provenance comments; NO round-1 reuse; reuses only the factory data_adapters plumbing loaders.load_mf_dataset / geometry.resolve_grid / metrics.finalize_and_write)",
  "base_commit": "9e10d414e35a96398f7b091bc84ddf936d88acc7",
  "family_dir": "models_r2/r2s4_b2_lfvalue",
  "datasets": "panel",
  "epochs": 200,
  "seeds": [0, 1, 2],
  "env": {
    "R2S4B2_WIDTH": "32",
    "R2S4B2_BLOCKS": "2",
    "R2S4B2_MODES": "16",
    "R2S4B2_FILM_MLP_WIDTH": "64",
    "R2S4B2_BATCH": "16",
    "R2S4B2_LR": "1e-3",
    "R2S4B2_WD": "1e-5",
    "R2S4B2_CLIP": "1.0",
    "R2S4B2_SCHED": "cosine",
    "R2S4B2_TARGET_NORM": "train_zscore_global",
    "R2S4B2_LF_TARGET_NORM": "train_zscore_global_lf_separate",
    "R2S4B2_ARMS": "T0_cond_only,T1_lf_aux,I1_lf_teacher,I2_lf_ablated",
    "R2S4B2_PRIMARY_ARM": "T0_cond_only",
    "R2S4B2_SPLIT_SEED": "0",
    "R2S4B2_FIT_FRAC": "0.8",
    "R2S4B2_VAL_FRAC": "0.1",
    "R2S4B2_INNER_FRAC": "0.1",
    "R2S4B2_VAL_MIN_N": "20",
    "R2S4B2_INNER_MIN_N": "20",
    "R2S4B2_IFC_INNER_MODE": "loo_anecdote",
    "R2S4B2_N_FIT_LEVELS": "20,80",
    "R2S4B2_N_FIT_SWEEP_ARMS": "T0_cond_only,T1_lf_aux",
    "R2S4B2_LF_RUNG": "max_lf_fid",
    "R2S4B2_LF_UPSAMPLE": "match_copylf_convention",
    "R2S4B2_LF_ABLATION": "fit_fold_mean_lf",
    "R2S4B2_AUX_WEIGHT": "1.0",
    "R2S4B2_SHRINK_GRID": "0.0:1.5:0.05",
    "R2S4B2_SHRINK_CALIB": "inner_fold",
    "R2S4B2_SHRINK_BOOT": "2000",
    "R2S4B2_FLOOR_ARMS": "nn_condition,train_mean,zero",
    "R2S4B2_FLOORS_JSON": "mffp_autoresearch/round2/state/anchors/floors.json",
    "R2S4B2_NOISE_FLOOR_JSON": "mffp_autoresearch/round2/state/noise_floor.json",
    "R2S4B2_BOOTSTRAP_B": "10000",
    "R2S4B2_GUARD_EPOCHS": "2",
    "R2S4B2_DIAG_OUT": "mffp_autoresearch_outputs/round2/r2s4_diag/B2/eval"
  }
}
```

  (`base_commit` = `round2-substrate` HEAD, verified `git rev-parse round2-substrate` ->
  `9e10d414e35a96398f7b091bc84ddf936d88acc7`. Cost: ~44 trainings/seed of a ~1M-param FNO
  vs B1's 6 at 4.13-4.42 min total (`state/timing_ledger.json`), most on smaller fit folds
  -> ~30-45 min/seed; request `--time 02:00:00`. Orchestrator may submit seed 0 via
  `submit.sh` and seeds 1-2 via `submit_seeds_2_3.sh`; seed 0 answers the direction, seeds
  1-2 deliver the re-certification.)

- **Expected outcome** (skill units under the corrected denominators; own-stream anchor
  = certified 3-seed panel geomean **19.8178**, panel min_claimable_effect **1.14187**):

  - **Primary arm vs anchor**: `T0_cond_only` panel geomean **19.8-22.5** (predicted
    +0.5 to +2.5 vs 19.8178 because the fit fold is 320 not 400 — a deliberate, stated
    consequence of carving the inner fold; the delta may exceed the 1.14187 panel floor and
    is itself the card's first N-scaling datum).
  - **Transfer gap at full N** `|T1 - T0|` vs the operative threshold
    `max(certified MCE, in-job 3-seed spread)`: fisher_kpp < 0.05 (floor 0.00071 -> the
    re-certified spread will dominate), pfc < 0.5 (floor 0.21303), allen_cahn < 1.5 (floor
    0.87970), cahn_hilliard < 0.3 (floor 0.09125) — all **pre-registered nulls**;
    helmholtz 0 to 3 raw (floor 2.95299 — likely not claimable raw, plausibly claimable on
    the shrunk column once lambda* removes the harmful condition-dependence that made the
    B1 spread 2.95299 in the first place); **ifc_poisson the one predicted claimable
    full-N effect, sign NEGATIVE (LF hurts), magnitude 0.5-5 vs floor 0.93770**
    (r2s3-B1's comparable, unmatched number was -7.3497).
  - **Information gap** `I2/I1` (inner-fold nRMSE ratio): **>= 10** on fisher_kpp / pfc /
    allen_cahn — the LF field at the same condition carries the realized IC that ADR
    r2-0003 says the condition lacks, and its test copy-LF nRMSE there is 0.02145 /
    0.00738 / 0.00178 against a condition-only barrier of 0.2479 / 0.3531 / 0.2623;
    **smallest on cahn_hilliard (1.2-3)**, whose 16 `ic_c*` dims put the IC *in* the
    condition. That ranking is a falsifiable structural prediction of ADR r2-0003.
  - **Capability gap** `T0 - I2` on the inner fold: ~0 (within the operative threshold) on
    >= 5 of 6 datasets, pre-registered from r2s1-B1 I1.
  - **transfer_efficiency**: < 0.05 on the four sharp datasets; unknown on helmholtz;
    plausibly negative on ifc_poisson.
  - **N_fit sweep**: `|T1 - T0|` at N_fit=20 exceeds its value at N_fit=320 by more than
    the operative threshold on >= 3 of the 5 sweepable datasets (the risky prediction).
  - **lambda\***: ~0-0.3 on helmholtz (B1 oracle 0.0), ~1.0 on pfc/allen_cahn/fisher_kpp,
    ~1.0-1.2 cahn_hilliard; bootstrap CI width the open question.
  - **Honest read on criterion 1**: I expect claimable full-N transfer effects on **1-2**
    panel datasets (ifc_poisson, possibly helmholtz), not 3. If that is what lands, the
    card's deliverable is a *certified* value-of-LF measurement with a demonstrated-sensitive
    instrument (the information-gap positive control) plus the N-scaling law, and the
    maintainer should adjudicate whether criterion 1 is met by a certified null on a
    sensitivity-proven instrument. I am not going to predict 3 claimable effects to make the
    criterion come out right.

- **Expected falsification** (one sentence, four disjuncts): the card's hypothesis — "LF as
  a training-only signal pays only where the condition-only estimator is SAMPLE-limited,
  not where it is INFORMATION-limited, and a matched LF-ablation instrument can prove it
  sees the information that exists" — is falsified if ANY of: **(F1, instrument)** the
  inner-fold information-gap ratio `nRMSE(I2)/nRMSE(I1)` is < 2.0 on >= 2 of {fisher_kpp,
  pfc, allen_cahn}, where copy-LF nRMSE 0.02145 / 0.00738 / 0.00178 against a condition-only
  barrier 0.2479 / 0.3531 / 0.2623 predicts >= 10 — the instrument cannot see an information
  gap known to exist and no transfer null is interpretable; **(F2, barrier)** at full N_fit
  `|T1 - T0|` exceeds `max(certified min_claimable_effect, in-job 3-seed paired spread)` on
  >= 2 of {fisher_kpp (0.0007136812826775696), pfc (0.21302734961699343), allen_cahn
  (0.8797047190126648)} — LF-as-training-signal moved the score where B1 certified <= 1.14x
  of room, which would overturn the barrier reading; **(F3, scaling)** `|T1 - T0|` at
  N_fit=20 fails to exceed its N_fit=320 value by more than the operative threshold on >= 3
  of the 5 sweepable datasets — the sample-limited/information-limited law is wrong; or
  **(F4, calibration)** the inner-fold lambda* bootstrap CI (B=2000, n <= 40) admits a skill
  range exceeding the operative threshold on >= 4 of the 5 shrinkable panel datasets, or the
  raw and shrunk columns give different claimable/not-claimable verdicts on >= 2 panel
  datasets — the mandatory shrinkage column B1's part 7 item (3) asks for is not certifiable
  at this calibration-fold size (FALCON's ~1000-point requirement,
  https://arxiv.org/html/2607.01354v1).
  *Attached reasoning*: the mandatory floor arms (`nn_condition` / `train_mean` / `zero`
  from `state/anchors/floors.json`) are reported as `ref_*` splits beside every arm on
  every dataset and are the standing "has this learned anything" comparison (§2.2) —
  helmholtz's zero column 3.3441 stays visible per the standing report-only discipline,
  and B1's certifier already failed to beat it (6.9438); a transfer effect on a dataset
  where neither arm beats its best floor is reported but not claimed.

- **Anchor reference**: `null` (program.md §4.5: null for all four round-2 streams; the
  own-stream anchor `certified_3seed_panel_geomean` 19.8178 is implicit).

## Status

- Slot covered: **yes**, 1/1 (no skip).
- Reopen candidates resolved: **0 exist** — verified `reopen_candidate: false` on all four
  round-2 batch-1 cards; nothing to retry or drop.
- Immutables self-check: **pass (11/11)** — see below.

### Immutables self-check (positive evidence for each)

1. **Data read-only** — the family only *reads* `stripped_data/{ds}/train_l*.npz` and
   `test_l{HF}.npz` through `data_adapters.loaders.load_mf_dataset`; N_hf is untouched
   (the N_fit sweep subsamples the *fit fold* of the existing train split and never adds a
   sample); the LF used is the shipped coarse solve at `max(lf_fids)`, never a downsampled
   HF (upsampling goes coarse->fine only, by the ADR r2-0001 registration map).
2. **Panel + guard fixed** — `datasets: "panel"` (the 6 §2.3 datasets) plus the standard
   2-epoch guard leg over `heat_local, fluid, sharp__sod_1d`; no dataset is added, dropped
   or substituted, and the N_fit sweep changes fit-fold size, not the dataset list.
3. **Eval layer / spec untouched** — the card requires no edit to `round2/eval/`,
   `project.yaml`, `program.md` or any agent prompt; the one interaction with `eval/` is a
   read-only *call* to `panel_data.py`'s upsampler in the contract-tier assertion, and all
   scoring goes through the unmodified `score_panel.py` -> `nrmse.py` path.
4. **One nRMSE definition** — every reported number (test, inner fold, shrunk column, floor
   arms, sweep levels) is computed by `eval/nrmse.py` via
   `data_adapters.metrics.finalize_and_write`, exactly as B1 did (`nrmse_def_hash`
   d3d0ade9…3850 must appear in every emitted JSON); the auxiliary LF loss is a *training*
   loss, which §5.4 leaves free.
5. **Contract CLI fixed** — `smoke_eval.py` keeps the six-arg signature
   (`--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`); every one of the 30
   knobs above is an `R2S4B2_*` environment variable listed in `recipe.env`, so all of them
   enter the cache key and none is a new flag.
6. **Seeds {0,1,2}, tier epochs fixed** — `seeds: [0,1,2]` is exactly the immutable's seed
   set, `epochs: 200` is the smoke tier from §2.4, the guard leg uses the contract tier 2,
   and no full-tier (2500) run is requested anywhere.
7. **Guarded factory surfaces untouched** — all new code lives in the worktree at
   `models_r2/r2s4_b2_lfvalue/` and `probes/`; `mf_field/factory_mffp/{eval,baselines,
   references,scripts,data}`, `factory.md` and `akash/` are imported-from at most
   (`data_adapters` only) and never written, exactly as B1's family did.
8. **Checkpoint-resume from `<ckpt_dir>/last.pt`** — each of the ~44 trainings writes
   `<ckpt_dir>/last.pt` under a key of (arm, dataset, N_fit level, fold index,
   epochs_target, grid, seed) and resumes at the stored epoch with optimizer, scheduler,
   best-val and shuffle-RNG state restored; this is B1's implemented pattern extended with
   the arm/level/fold key, and the arm loop is itself resumable (completed arms are skipped
   when their result JSON exists).
9. **Falsification threshold > noise floor, per dataset** — F2's threshold is
   `max(certified min_claimable_effect, in-job 3-seed paired spread)`, which is
   >= the certified floor **by construction**, quoting fisher_kpp 0.0007136812826775696,
   pfc 0.21302734961699343, allen_cahn 0.8797047190126648 (and for the reported columns
   helmholtz 2.95299157437233, ifc_poisson 0.9377041289531141, cahn_hilliard
   0.09124535322300886, panel geomean 1.1418668211296108); F3 and F4 use the same operative
   threshold; F1 is an inner-fold ratio with its own in-job 3-seed null, and B1's H5
   ("the constants... are a LOWER bound for any less-collapsed successor") is precisely why
   the `max(...)` form is used rather than the bare constant.
10. **Not a pre-falsified lever** — the nearest r1 §5 lever is **LF low-mode freezing**,
    which imposed LF's low modes as a hard constraint on an LF-consuming model *at test*;
    this card's `T1_lf_aux` uses LF only as a soft auxiliary training target on a separate
    head that is absent from the scored forward pass, and — decisively — the card does not
    claim it as a win: it is the instrument of a measurement whose pre-registered
    expectation is a null. WNO backbone swap and the diffusion prior are not involved.
11. **Floor arms** — although this is a `diagnostic` card, `ref_nn_condition`,
    `ref_train_mean` and `ref_zero` are recomputed from `state/anchors/floors.json` through
    the same nRMSE path and merged beside every arm on every dataset (B1's pattern, leaving
    `test_hf` byte-identical), and they appear in the expected_falsification attached
    reasoning above as the standing "has this learned anything" comparison, with
    helmholtz's zero column 3.3441 kept visible.
