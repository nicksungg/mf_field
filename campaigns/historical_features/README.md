# Input parameters and local summaries for whole-field averaging

Authorized small CLUSTER pilot, September 13, 2026. All new jobs exclude node2900
and node4200. No base networks are trained. Existing strict-FP32 neural outputs and training-only POD-GP refits
are read from `../fieldgate_20260912` on CLUSTER. Saved float32 Transolver and
ConvNeXt predicted-coarse corrector outputs come from `../uqcorr`. Their original
TF32 flags were not recorded. No new corrector inference is performed; every
mixture comparison uses these same candidate fields. Original runs remain unchanged.

## Question and frozen scope

Does the model-specific averaging gate benefit from actual simulation inputs,
local summaries of field disagreement, or both? It still outputs one weight
per expert for the entire field. The experiment compares seven and nine experts on the same 20 strict datasets and
the same three known-dataset case splits (71, 172, 273), keeping related-version
input groups together. The nine-expert pool adds `uqcorr_transolver_pred` and `uqcorr_convnext_pred`,
seed 42, K=6, with four-member predicted coarse inputs. ConvNeXt transfer is
already in the original seven. Sharp Cahn-Hilliard lacks these two corrector
predictions and is excluded from BOTH pools. Seven strict classes remain.
Climate is excluded because all its evaluation inputs occur in LF training.
There is no new class-holdout experiment: raw parameter coordinates differ in
dimension and physical meaning between datasets.

The original model-specific field-gate architecture is refitted on the common
20-dataset corpus as the control. The four variants are:
current 20 global features; current plus input parameters; current plus 24 local
features; current plus both. All use the same model-specific linear scorer,
bounded logit adjustment, convex output weights, 400 Adam updates, penalties
0/.01/.1, tuning checks every 20 updates, and exact fixed-prior fallback.
The fixed prior is fitted separately per dataset on fitting labels. A stronger
fixed mixture and a selected-single-model control use all fitting+tuning labels.
Original fit-only static and single-model controls are also included.

## Additional features

Six spatial regions: four quadrants, an outer 10% edge band (rounded up to grid
cells), and the remaining interior. Each region yields four per-expert features:
local/global RMS ratio, signed difference from the median prediction, RMS
disagreement with that median, and normalized gradient RMS. All summaries use
predictions only. Edge bands do not assert physical boundary conditions; gradient
spacing is normalized to a unit domain. Existing global spectral features stay.

Original float32 simulation input vectors come from the prediction archives.
Each dataset has its own parameter-coordinate block so unrelated quantities are
not conflated. The mean and standard deviation use only fitting rows within that
dataset. Other dataset blocks are zero. Constant fitting coordinates are ignored;
standardized values are clipped to [-8,8]. These already standardized blocks
bypass the gate's pooled feature standardizer to avoid rescaling rare datasets'
inputs by their dataset frequency. The control and local feature preprocessing
are unchanged. Input coordinates are broadcast to all expert scorers, whose
separate coefficients allow them to respond differently to the same parameter.

Extra features increase coefficient counts. A constant-feature diagnostic applies
each fitted gate to fitting-set mean features per dataset, testing whether actual
case variation helps beyond a learned shift in fixed preferences. This does not
fully match capacity; improvement alone is not a definitive feature mechanism claim.

## Labels, selection and evaluation

The case splits have 1,733 fitting, 577 tuning and 580 evaluation rows each.
Fitting and tuning receive only assigned label rows. Weight arrays are saved and
hashed before requesting evaluation rows for scoring. The cache builder uses targets only to audit alignment and construct supervised
error matrices. Feature functions receive predictions and input parameters only.
The seven-expert static controls must match the previous saved weights within
1e-7 on the retained datasets; the gate is refitted because the corpus changed.

These are historical benchmark cases previously inspected during method
development. Their reuse is exploratory, not fresh confirmation. The three seeds
vary meta-data partitions, not base training seeds. Fine calibration labels count
beyond base training; all seven or nine experts must predict each case, depending on the pool. Known legacy
dataset issues are retained, and tiny legacy cavity has only two evaluation rows
per split. No statistical significance or matched-compute claim is made.

PLAN.json and SOURCE.json are frozen before submission. The feature job checks
source hashes, runs four meaningful tests, and builds extra features. A six-task
array fits/evaluates the two pools across three partitions, followed by a dependent collection job.
No background feeder resubmits jobs. All results, splits, fitted parameters,
feature names, histories and locked weights are retained locally and on CLUSTER.


## Launch history and Transolver variants

An initial launch failed its source-manifest preflight before any feature building
or model fitting; dependent jobs were cancelled. The missing-manifest setup error
was fixed while incorporating the user's request to expand the expert pool.
No scientific results existed before the scope changed.

The older `transolver_residual` and `fno_transolver_seq` families are distinct from
the added uqcorr corrector. The legacy residual evaluator can synthesize LF from
HF for HF-only directory datasets; its npz_l path instead uses real LF test fields.
The sequential hybrid also uses real LF when available and its correction is
active, while falling back to its FNO base when alpha is zero. These are different
input budgets from the solver-free pool here. Their historical successes are not
silently inserted as solver-free predictions. Audit details are retained separately.
