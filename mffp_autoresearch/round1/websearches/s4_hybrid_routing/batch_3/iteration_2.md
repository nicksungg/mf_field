# iteration_2 — the OOF gate's canonical citations (cross-fitting / super learner)

## Search rationale

B2's headline defect is a keep test that trains AND scores against an
in-sample base and therefore sign-inverts 5/5. The B3 card must **cite, not
claim**, that this is a known estimator defect. The s6-B2 loop got Wolpert only
*through* arXiv:1106.1684 (the Wolpert PDF 425'd and the Super Learner PDF
403'd), so this turn hunts a fetchable canonical source for each of the three
classical framings: (1) super learner / CV-selector oracle inequality,
(2) double-ML **cross-fitting** (the name for K-fold sample splitting used to
kill overfitting bias in a two-stage estimator — structurally identical to our
stage-3 gate), (3) an explicit statement of the in-sample-base failure mode.

## Search terms used

1. `Super Learner van der Laan Polley Hubbard cross-validated ensemble oracle inequality arxiv`
2. `Chernozhukov double machine learning cross-fitting sample splitting arXiv 1608.00060`
3. `out-of-fold predictions required stacked generalization leakage overfitting combiner in-sample base predictions bias`

## Findings

### Term 1 — Super Learner
Returns: https://biostats.bepress.com/ucbbiostat/paper222/ and
https://biostats.bepress.com/cgi/viewcontent.cgi?article=1269&context=ucbbiostat
(van der Laan, Polley & Hubbard 2007, *Super Learner*, SAGMB),
https://escholarship.org/uc/item/4qn0067v ,
https://tlverse.org/csp2020-workshop/sl3.html ,
https://www.stat.berkeley.edu/users/laan/Class/Class_subpages/BASS_sec1_3.1.pdf ,
https://arxiv.org/html/2405.17259 (joint survival super learner).
Engine summary (NOT a citation): *"The Super Learner is a weighted average of
the library of algorithms, where the weights are chosen to minimize the
cross-validated empirical risk"*; oracle inequality from van der Laan & Dudoit
(2003), van der Vaart–Dudoit–van der Laan (2006).
**Both fetch attempts failed**: bepress `viewcontent.cgi` → **HTTP 403**;
https://escholarship.org/content/qt4qn0067v/qt4qn0067v_noSplash_3d914a3ffc0c837588da377e4239d245.pdf
→ 1.5 MB PDF binary, no extractable quotes.
**Super Learner is therefore NOT citable from this loop's fetches.** (Third
attempt deferred to iteration 5 under a different term, per the ≤2-fetch rule.)

### Term 2 — double ML cross-fitting — **DIRECT HIT, fetched**
https://arxiv.org/abs/1608.00060 (Chernozhukov, Chetverikov, Demirer, Duflo,
Hansen, Newey, Robins — *Double/Debiased Machine Learning for Treatment and
Causal Parameters*), **fetched**, abstract verbatim:
*"In order to avoid overfitting, our construction also makes use of the K-fold
sample splitting, which we call cross-fitting."*
The fetch confirms the two names are used interchangeably (**K-fold sample
splitting = cross-fitting**) and that its purpose is to let a broad array of ML
methods solve the auxiliary prediction problem *"without risk of overfitting
bias"*. This is the canonical name for what B3's OOF gate does at every stage:
the first-stage nuisance (our base) must be fitted on folds excluding the
points on which the second stage (our keep test / alpha) is evaluated.
Also returned, not fetched: https://academic.oup.com/ectj/article/21/1/C1/5056401
(the Econometrics Journal version), https://arxiv.org/pdf/2007.02852
(cross-fitting AND averaging for heterogeneous effects — the "average over
folds" variant), https://arxiv.org/pdf/2602.11333 (cross-fitting-FREE debiased
ML, i.e. an active line arguing the split can be avoided under conditions).

### Term 3 — the in-sample-base failure mode stated explicitly — **fetched**
https://mcpanalytics.ai/articles/stacking-ensemble-practical-guide-for-data-driven-decisions
(**fetched**; practitioner guide, not peer-reviewed — usable only for the
*statement of the failure mode*, never as a mechanism source):
*"Training a base model on the full dataset and using those predictions for the
meta-learner creates severe overfitting that inflates validation scores by
10-20% while producing poor production performance."* and
*"Always use out-of-fold predictions: for each data point, only include
predictions from base models that never saw that point during training."*
Note the **direction**: the literature's canonical artifact is an *inflated
validation score*, which is exactly B2's measurement (stage 3 claims +14…+85 %
on val, delivers −5…−28 % on test); the published magnitude quoted here is
10-20 %, while B2 measured a `val_base_oof / val_base_insample` optimism ratio
of **16.4×** on cahn_hilliard. Other returns were applied stacking papers
(https://arxiv.org/pdf/2206.08473 , https://arxiv.org/pdf/2001.09055 ,
https://arxiv.org/pdf/2605.13730) — none about the artifact itself.

## Interpretation

The OOF gate is **fully preempted and now citably so**: cross-fitting has a
canonical name and a fetched primary source (arXiv:1608.00060), and the
in-sample-base optimism is a textbook artifact. What the fetched sources do
*not* contain is a **two-sided** statement — nothing says the optimism can flip
a *keep/discard decision*'s sign in a shrinkage line search whose grid contains
0, which is the specific mechanism B2 measured.
