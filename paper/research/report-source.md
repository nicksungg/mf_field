# AutoMF: research synthesis for an application-focused ICLR draft

Audience: Nicholas Sung and scientific-machine-learning reviewers. Date: 2026-09-14.
Scope: a complete LaTeX draft grounded in the existing experiments, with literature
publicly available by this date. Anonymous working manuscript; no submission or claim
that the pending repaired experiments have finished. This is the canonical internal
research synthesis; manuscript text and tables are generated separately.

## Executive answer

The strongest supported story is automated construction of a parameter-to-field
surrogate from a fixed heterogeneous portfolio trained using LF/HF data. The pipeline
uses a small additional set of fine calibration fields to select a single expert,
inverse-error mixture, or convex stack, then fixes its weights for new inputs.
It is a practical systems/empirical contribution. Classical stacking, weighted
surrogates, automatic MF strategy choice, and field ensembling already exist.
The paper should make the studied deployment contract and comparative evidence
concrete rather than claim to invent those components.

## Consequential literature findings

Wolpert (1992), Breiman (1996), Super Learner (2007), Caruana et al. (2004),
auto-sklearn and AutoGluon establish learned library combinations and automated model
selection. Breiman explicitly formulates the residual Gram objective. Our field-valued
version and elementary perturbation bound are explanatory analysis, not novel theory.
Goel et al. (2007) already weight surrogate libraries using cross-validation errors.
Primary sources: https://statistics.berkeley.edu/sites/default/files/tech-reports/367.pdf ;
https://doi.org/10.1016/S0893-6080(05)80023-1 ;
https://doi.org/10.2202/1544-6115.1309 ;
https://doi.org/10.1145/1015330.1015432 ; https://arxiv.org/abs/2003.06505 ;
https://doi.org/10.1007/s00158-006-0051-9 .

EL-MFS uses adaptive surrogate ensembling within a hierarchical MF framework.
AQBMF screens LF basis functions and selects hierarchical/ensemble/SF possibilities.
MAESTRO trains five LF/discrepancy model families and applies prescreening and LOOCV.
These directly disconfirm broad claims of first automated MF learning. MAESTRO's
journal issue is dated November 2026, but its SSRN preprint was posted February10,2026;
cite the preprint. Its full text was inaccessible and claims here are abstract-level.
Sources: https://doi.org/10.1016/j.aei.2024.102535 ;
https://web.mae.ufl.edu/nkim/Papers/paper151.pdf ;
https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6207840 .

LANE-SI already combines neural sea-ice fields and climatology using learned linear
and convolutional combiners. Its conclusion reserves general AutoML ensemble design
for future work. HyperNOs automates neural-operator hyperparameter search. Therefore
neither full-field combination nor automated operator training is new. AutoMF's
question is the joint practical setting: multiple LF-use mechanisms, compatible
parameter-only deployment, tiny explicitly counted whole-field calibration, and
cross-problem evaluation of a common rule. The search cannot prove unique priority.
Sources: https://arxiv.org/html/2312.04330v1 ; https://arxiv.org/abs/2503.18087 .

MFRNP, multifidelity DeepONet, and MF-FNO/WNO already learn scientific fields from
multiple fidelities. Faza et al.'s August2026 preprint compares MF mechanisms under
nontrivial fidelity differences, motivating but preceding our task-dependence story.
The local FIRE implementation is an FNO adaptation; the original FIRE paper uses
tabular foundation models. Local DeepONet is a nearest-LF-library residual wrapper,
not an exact reproduction of Howard et al.'s composite MF-DeepONet.
Sources: https://proceedings.mlr.press/v235/niu24d.html ;
https://arxiv.org/abs/2204.09157 ; https://arxiv.org/abs/2608.04708 ;
https://arxiv.org/abs/2601.22371 .

The ERA5 construction follows MFRNP's climate-driver-to-temperature task, distinct
from weather forecasting and from ClimateBench itself. Reanalysis is not direct
ground truth. Lütjens et al. demonstrate that simple pattern scaling is a serious
climate comparator and internal variability can distort model comparisons.
Sources: https://arxiv.org/html/2402.18846v2 ; https://doi.org/10.1002/qj.3803 ;
https://doi.org/10.1029/2021MS002954 ; https://arxiv.org/abs/2408.05288 .

## Evidence available for the draft

Audited historical study:20datasets,7classes,9frozen experts,3calibration partitions;
5/10/20 additional fields, legacy cavity capped at8. Full convex stacking improves
14/20 at K=5; class-balanced ratio0.8743288831 and equal-dataset ratio0.9217276517
against a calibration-selected singleton. Inverse weighting nearly ties full fitting.
These are reused historical evaluation cases, not fresh tests or3trainingseeds.
The full automatic selector is implemented in the repair campaign but its final
evaluation is pending. Historical full-stack results must never be relabeled as
automatic-selector results.

A15dataset sensitivity excludes5documented generation/conditioning/synthetic-LF
issues by membership, without ranking errors. At K=5 full stacking has ratio0.868878
class-balanced and0.897893 equal-dataset,12wins/3losses. This retrospective analysis
does not certify the remaining generators or replace the20dataset result.

Fresh heat:168new simulations,40calibrationpool and128final cases. Inverse weighting
beats full fitting and LOO shrinkage at each tested budget. This is a single PDE and
one base-training seed. On changed predicted-coarse resolution, refreshing weights
using the same calibration answers recovers most performance; this is a practical
deployment observation, not a novel adaptation algorithm.

ERA5 repair:55base-HF/10calibration/7evaluation; all17reserved inputs removed from
every LF/HF training source, new checkpoints, corrected exact-input all-pairs join.
Seven compatible ensemble experts plus a fine-only control; work grid128x256.
Paired correctors are unavailable. Four missing PDE datasets are also being completed.
No repaired accuracy is reported. Historical ERA5 values are excluded.

## Remaining experiments that materially affect the contribution

1. Evaluate the frozen automatic rule on all eligible datasets and fresh cases.
2. Compare Caruana greedy ensemble selection on identical cached fields and counted
   calibration budgets; add regularized stacking and compatible reduced-basis MF
   predecessors rather than asserting superiority from a citation-only comparison.
3. Compare matched-HF-label fine-only portfolios and well-tuned single learners.
   Sweep base HF count separately from calibration count. Most historical solver
   tables have equal LF/HF row counts, so LF-abundance/sample-efficiency is unproven.
4. Report complete model-building, OOF member, calibration and inference costs;
   cheap combination does not imply cheap end-to-end AutoML.
5. Strengthen climate with linear/pattern-scaling controls, area-weighted absolute
   errors, provenance-verified time/scenario splits, and more evaluation cases.
6. Confirm on independent surrogate seeds and untouched problems; keep related
   dataset versions together. Report every failure and quality caveat.

## Research stopping and verification

Two substantial lanes reviewed original AutoML/stacking and MF/operator/climate
sources. The coordinator independently inspected the closest collision papers,
official conference requirements, implementation objectives, audit source data,
and numerical denominators. Searches were narrowed after finding direct precedents.
The final follow-up resolved MAESTRO's pre-cutoff availability and LANE-SI's scope.
Further broad searching is unlikely to change the no-first-claim positioning.
Source access limitations remain in the ledger. Pending experimental evidence is
explicit, not inferred from component results.

The official ICLR2027 template and9page main-text limit were verified at
https://iclr.cc/Conferences/2027/AuthorGuidelines . An AI-use statement is required;
the draft accurately describes assistance but does not assert human approval that
has not occurred: https://iclr.cc/Conferences/2027/AIPolicyForAuthors .
