# Field-conditioned ensembles across eight PDE classes

## Matched-prior follow-up

This isolated revision fixes a training/evaluation mismatch in the original
class-holdout experiment. The original gate fitted and tuned against excellent
dataset-specific priors on known datasets, then received a generic global prior
on a held-out class. This revision uses the **same global starting weights at
fit, tune and evaluation time** in every class-holdout run. The case-holdout
procedure is unchanged and its three results are linked read-only from the
original campaign. No new base predictions, features, data splits, parameter
budgets, losses or hyperparameter grids are introduced.

The seven strict class runs and one climate diagnostic are repeated. This is
an exploratory protocol correction after the original test results were viewed;
it is not an independent confirmation. Original runs remain available under
`../fieldgate_20260912`. Runtime assertions verify that fit/tune receive the
same global starting prior as inference on the unseen class.

User authorized this CLUSTER pilot after discussing adaptive averaging of existing
field predictors. This is a new isolated campaign. Existing base-model sources,
checkpoints, release tables and the earlier blending follow-up remain unchanged.
Every new Slurm job excludes node2900 and node4200.

The seven experts are FiLM-FNO transfer, all-pairs FNO, ConvNeXt transfer, FIRE,
WNO transfer, DeepONet, and HF-only POD-GP. Common coverage is 22 datasets in all
eight previously defined classes: elliptic, diffusion, shocks, convection,
porous flow, reaction-diffusion, waves and climate. The class map comes from
`mf_field_report/build_2d_figs.py`, with corrected Poisson/cavity versions added
to their original classes. No rankings or historical test errors determine
class labels, model weights or decision rules.

**Audit revision:** all seven ERA5 inputs occur in LF training, although none
occur in HF training. The first cache job stopped before any production gate
fit, and dependent jobs were cancelled. That attempt is preserved under
`attempts/pre_climate_audit`. Primary experiments use 21 datasets in seven
classes. ERA5 supplies no gate/prior fitting or tuning labels. One additional
climate-class evaluation is retained as a separately reported **LF-seen**
diagnostic, excluded from all primary aggregates.

Three datasets lack common current-checkpoint coverage: sharp Allen–Cahn,
Fisher–KPP and phase-field crystal. Known legacy defects in the remaining
datasets are retained and reported. ERA5 has only seven available historical
test cases; its results cannot support a strong claim by themselves.

## Precision, identities and what is reused

The old prediction archive is float16 and classical fields are in scaled units.
Paper checkpoints are replayed on GPUs into new float32 arrays. Export code
forbids backward passes, optimizer steps and checkpoint writes, and checks that
model state was loaded. Original checkpoint hashes are recorded. POD-GP has no
saved estimator state, so its original training-only fit is reproduced on CPU.
Its training-derived scale restores physical units. Across experts, grid and
theta identities must match exactly and target differences must be below 5e-7
in relative L2. The raw FiLM target is canonical for all mixture errors.

**Numerical replay revision:** a same-GPU FIRE/Rayleigh–Benard check gave
0.0002951 error with default TF32-enabled convolution versus 0.00003684 with
TF32 disabled. The archived benchmark metric is 0.00002926, so exact replay
is still hardware-sensitive at very small error. Before any production gate
fit, all neural exports were repeated with TF32 disabled for both matmul and
convolution and float32 matmul precision set to `highest`. CPU POD-GP fits are
reused. The default-precision exports and their metadata are preserved under
`attempts/default_tf32`; the two-mode diagnostic is in `diagnostics/`.
All ensemble comparisons use the same new strict-FP32 fields, not historical
leaderboard numbers. No new neural base-model training was performed.

Feature/error calculations accumulate in float64. Training overlap is checked
against every original LF/HF parameter row and any overlapping historical test
rows are excluded from the primary evaluation. ERA5 alone is retained in the
separate LF-seen diagnostic. Input hashes group matching old/fixed generator instances.

## Explicit meta-learning split

The existing **historical benchmark test predictions** form a new exploratory
meta-learning corpus. This does not create a fresh benchmark test set or erase
the fact that historical test results guided the research direction.

1. **Case holdout:** three deterministic 60% fit / 20% tune / 20% evaluation
   partitions (seeds 71, 172, 273), grouped by input identity across related
   dataset versions. Every expert sees the same rows.
2. **Class holdout:** seven strict folds plus one LF-seen climate diagnostic.
   All cases of one PDE class are evaluation
   cases. The remaining classes supply 80% fit / 20% tune cases. The excluded
   class supplies no labels for priors, standardization, fitting or selection.
   Its missing class/dataset prior falls back to the learned global mixture.
   ERA5 never enters fitting/tuning even when a different class is held out.

The class holdout concerns the **weighting rule**, not the underlying experts:
each held-out dataset already has its trained surrogate models. This tests
transfer of the rule for mixing those models, not zero-shot PDE prediction.

All feature normalization uses fit inputs only. Models use fit labels for
learning and tune labels for hyperparameter/checkpoint selection. Evaluation
weights are saved and hashed before evaluation scoring.
The cached error files contain all rows for auditing; fitting functions receive
only the explicitly selected fit/tune rows, and evaluation rows are requested
for scoring only after the weights are locked.
No oracle weights or test errors are used as inference inputs. Oracles are
calculated afterward as explicitly unattainable diagnostic bounds.

Additional fine labels used to train/calibrate the ensemble count as additional
labels beyond the original base-model training sets. This pilot establishes
neither lower total HF-label cost nor matched total training/inference costs.
It tests whether fields predict useful changes in mixture weights.

## Methods

- Equal averaging; globally fixed, class-fixed and dataset-fixed convex mixtures.
- Best individual expert selected from fit labels, with class/global fallback.
- **calibration_fixed:** a stronger static mixture using ALL fit+tune labels.
- **Shared field gate:** twenty linear coefficients score each expert using its
  field/peer descriptors. This scoring rule is shared across the seven experts.
- **Model-specific field gate:** 140 coefficients, allowing different responses
  to the same descriptors. Same descriptor inputs and calibration protocol.
- **Field rules:** depth 1–3 decision trees partition class/metadata/field
  descriptors. Leaf weights minimize actual combined field error. A tune-chosen
  interpolation with the existing prior controls departures from that prior.
- **Metadata-only rules:** the same tree procedure receives class, grid sizes,
  base HF training count and condition dimension, without per-case field features.
- **Constant-feature ablation:** apply each learned field gate to the fit-set
  mean feature vector of that dataset (class/global fallback when absent),
  instead of the new example's features. This isolates the value of case variation.

Gate features include amplitude ratios, gradients, skew, broad/middle/fine
spectral content and disagreement with the median predicted field. Twenty
descriptors are computed independently for each new example, with no truth.
DCT-II bands are relative to the output grid and are descriptive features, not
physical boundary assertions or hard Nyquist cutoffs. Grid sizes, HF training
count and condition dimension are additional inputs to the readable rule tree.

The gate starts from a 95% prior / 5% uniform smoothing so initially zero-weight
experts can become useful. Its logit changes are bounded by ±4. Regularization
strengths 0, .01 and .1 and checkpoints every twenty steps are selected on tune
data (400 updates maximum). If no candidate beats the original prior on tune
data, the exact original prior is retained. This fallback is reported explicitly.

Convex mixtures and gates optimize squared relative L2 with fit-only dataset
scaling and equal total class/dataset weights. Tune selection uses a class-balanced
geometric mean of dataset mean relative L2. Reports first average repeated split
means within each dataset, then give equal weight to classes. Per-case errors,
locked weights, readable rules, priors and parameter counts are retained.

## Running and outputs

`prepare.py` records coverage and original checkpoint locations. `export_one.py`
replays one expert; two GPU workers plus one CPU worker finish the export queue.
`cache.py` audits units/identities and separates prediction-only features from
supervised error matrices. `run.py` fits, locks and scores one split.

`launch_exports.py` and `launch_gates.py` are idempotent submission entry points.
The gate launcher requires the real Darcy smoke to pass. A cache job depends on
all exports, an eleven-task CPU array follows the cache with at most two tasks
running simultaneously, and a final report job follows the array. There are no
automatic resubmission feeders. User cancellation does not spawn replacement jobs.

`results/RESULTS.md`, `results/results.csv`, `results/status.json`, the launch
JSONs and `runs/<split>/` provide results and provenance. `sync_results.sh` pulls
lightweight reports, locked weights and per-case errors locally without copying
large prediction arrays or original checkpoints.

Verification covers the exact field/Gram mixture identity; feature independence
from other examples and equivariance to expert ordering; disjoint case/version
and entire-class splits; and a held-out synthetic case where field-regime
information should enable useful adaptive weights. A real CLUSTER Darcy smoke
checks the complete seven-expert pipeline before the full experiment.
