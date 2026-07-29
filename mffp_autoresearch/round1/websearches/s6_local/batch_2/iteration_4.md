# Iteration 4 — held-out-fold gate training / in-sample gate blindness (topic (d))

## Search rationale

B1's F4/F5 + M2 diagnosed a *structural* defect, not a tuning failure: stage 2
minimised `MSE(g*Delta, R)` over the **same `fit_idx`** that stage 1 fitted
`Delta` on, so the uniform-gate landscape's argmin is `c = 1.0` on fit, val and
test alike and `g -> 1` is the *correct* answer; on the one dataset with a real
generalization gap (helmholtz: rho 0.99968 in-sample, **-0.22457** held-out,
val-argmin `c = 0.25`) the pixel gate still saturated at `g_mean = 0.9970`.
Part 7 item (3) is the repair: freeze the corrector, train the gate head on a
LATER fold, select the scalar on a third. The question for the card's framing:
**is "train the gate/meta-learner out-of-fold" a named, textbook requirement?**
If yes, B1's finding is a *self-inflicted protocol bug* that must be reported as
such, and the batch-2 arm claims no novelty for the fix. Terms attack (i) the
stacking/out-of-fold formulation, (ii) the MoE gate-degeneracy formulation,
(iii) the primary-source formulation (Wolpert 1992).

## Search terms used

1. `gating network trained on same data as base models overfitting stacked generalization cross-validated out-of-fold predictions leakage`
2. `mixture of experts gate saturates degenerate in-sample residual correction gate learns to always trust expert`
3. `Wolpert stacked generalization 1992 cross-validation partition avoid meta-learner bias base learner in-sample predictions overfit`

## Findings

### Term 1 — stacking / out-of-fold: the failure mode is TEXTBOOK
- Search-returns state B1's defect almost verbatim: *"Training a base model on the
  full dataset and using those predictions for the meta-learner creates severe
  overfitting that inflates validation scores by 10-20% while producing poor
  production performance"* and *"Always use out-of-fold predictions: for each
  data point, only include predictions from base models that never saw that point
  during training"*
  [https://mcpanalytics.ai/articles/stacking-ensemble-practical-guide-for-data-driven-decisions ,
  https://machinelearningmastery.com/out-of-fold-predictions-in-machine-learning/ —
  practitioner-grade sources, search-return].
- Academic framing: *"Stacked generalization performs k-fold cross-validation to
  generate out-of-bag predictions for the validation set of each fold, and
  collectively, the k out-of-bag predictions create a new training set for the
  second level learning task"* [https://arxiv.org/pdf/2001.09055 , search-return].
- **Fetch failed**: "Stacked Generalization: An Introduction to Super Learning",
  https://www.biorxiv.org/content/10.1101/172395.full.pdf — HTTP 403.

### Term 2 — MoE gate degeneracy: a DIFFERENT failure, do not conflate
- Search-returns describe MoE's characteristic pathology as **load imbalance**:
  *"the gate might learn a degenerate solution where a small number of experts
  handle most inputs"*, *"experts at each layer that perform best for the first
  few examples end up overpowering the remaining experts"*, remedied by an
  *"auxiliary loss term that encourages the gating network to distribute tokens
  evenly across experts"* [Shazeer et al. sparsely-gated MoE,
  https://www.researchgate.net/publication/312619873_Outrageously_Large_Neural_Networks_The_Sparsely-Gated_Mixture-of-Experts_Layer ;
  https://brunomaga.github.io/Mixture-of-Experts ; https://aman.ai/primers/ai/mixture-of-experts/
  — all search-return].
- Explicit negative: *"the search results don't contain extensive details
  specifically about the 'in-sample residual correction' mechanism or how the gate
  learns to 'always trust expert'"*. **So B1's specific failure — a trust gate
  saturating at 1 because it is scored on the corrector's in-sample residual — is
  NOT the documented MoE failure mode**; the MoE literature is about expert
  utilisation balance, not about a gate blind to its expert's generalization
  error. Nearest in name only: "Gate to the Vessel: Residual Experts Restore What
  SAM Overlooks" https://openreview.net/pdf/c6cf19bdd4fea96b63ecfd29a19199ef909a880b.pdf
  (search-return, medical segmentation).

### Term 3 — the primary source: it is Wolpert's founding requirement
- **"Max-Margin Stacking and Sparse Regularization for Linear Classifier
  Combination and Selection"**, https://arxiv.org/pdf/1106.1684 — **FETCHED.**
  The fetch confirms the paper repeatedly cites **Wolpert 1992** (`cite.wolpert92sg`)
  for the principle that *"the combiner must be trained on predictions from base
  classifiers applied to held-out data, not the training instances used to build
  those classifiers"*, and that base classifiers generate level-1 features
  *"on out-of-sample instances through cross-validation folds, ensuring
  independence between base classifier training and combiner training data"*.
- Search-return statements of the same rule with the failure named:
  *"Care is taken to ensure that the models are formed from a batch of training
  data that does not include the instance in question, in just the same way as
  ordinary cross-validation"*; *"Training the combiner (meta-learner) with the
  same data instances which are used for training the base classifiers will lead
  to overfitting the database and eventually result in poor generalization
  performance"* [https://arxiv.org/pdf/1105.5466 "Issues in Stacked
  Generalization"; https://www.ijcai.org/Proceedings/97-2/Papers/011.pdf
  "Stacked Generalization: when does it work?"].
- **Fetch failed**: Wolpert 1992 primary PDF,
  https://machine-learning.martinsewell.com/ensembles/stacking/Wolpert1992.pdf —
  HTTP 425 Too Early. Semantic Scholar record exists
  (https://www.semanticscholar.org/paper/Original-Contribution:-Stacked-generalization-Wolpert/bbc25a700e51984e560eae27df1587baa92e3afe,
  not fetched).

## Interpretation

Topic (d) resolves cleanly and unfavourably for any novelty claim: **out-of-fold
training of a combiner is the founding requirement of stacked generalization
(Wolpert 1992, confirmed via a fetched paper that cites it for exactly this
rule), and training the combiner in-sample is the named, classic overfitting
failure.** B1's gate was an instance of that classic bug applied to a field
corrector; the batch-2 repair is therefore **standard methodology**, and the
card must present it as "we ran the protocol wrong in B1 and here is the
corrected measurement". Note the *interesting* asymmetry to report: in the
classic setting in-sample stacking makes the combiner **over-confident in a
spuriously good direction**; in B1 it made the gate a **provable no-op**
(landscape argmin exactly 1), which is a cleaner, stronger statement than the
literature's "inflates validation scores by 10-20%". Final turn: adversarial
verdicts.
