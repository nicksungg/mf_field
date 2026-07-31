# Iteration 5 — refutation pass 2 (ITERATION CAP: 5/5 used, no further turns permitted)

## Search rationale

Two candidate directions still needed a dedicated refutation search: **D3** (the
shrink-toward-own-mean arm; is it James-Stein rebadged?) and **D1**'s mechanism
half (is "privileged signal gives no gain / hurts" already an established
finding with a named experimental design?). A third term retried the D2 gap from
the Bayes-error / irreducible-error angle to see whether a *field-valued, few-
sample* estimator exists under different vocabulary.

## Search terms used

1. `shrinkage estimator combining prediction with mean prediction James-Stein neural network regression improves test error` (D3)
2. `privileged information distillation ablation shows no gain or hurts student negative transfer teacher variance` (D1)
3. `estimate Bayes error irreducible error field-valued output surrogate few samples paired samples identical parameters` (D2, reworded)

## Findings

### Term 1 (D3) — James-Stein / shrinkage

The operation is 70 years old and named. Search summaries: "The James-Stein
estimate is a weighted average of two different estimators, where the weight is
chosen in a data-driven fashion such that the estimate is improved in terms of
mean squared error"; "shrinking coefficients towards the center of the parameter
space, resulting in improved predictions"; "a uniform reduction in the summed
squared errors when compared with the maximum likelihood estimator" (SNIPPETS).
Sources returned: Efron & Hastie CASI ch.7 —
https://efron.ckirby.su.domains/other/CASI_Chap7_Nov2014.pdf ; Hansen,
"Generalized Shrinkage Estimators" —
https://web-docs.stern.nyu.edu/old_web/emplibrary/shrink3.pdf ; "James-Stein
estimator improves accuracy and sample efficiency in human kinematic and
metabolic data" — https://pmc.ncbi.nlm.nih.gov/articles/PMC12185630/
(**FETCH FAILED**: 301 redirect to a different host, not followed) and its
biorxiv preprint https://www.biorxiv.org/content/10.1101/2024.10.07.616339.full.pdf ;
"Data enriched linear regression" — https://arxiv.org/pdf/1304.1837.
B1's lambda in `P_bar + lambda*(P - P_bar)` is exactly a shrinkage weight toward a
grand mean; the only difference is that P_bar is the *model's own* mean
prediction rather than a global/parametric mean, and that lambda is read as a
diagnostic rather than tuned for accuracy.

### Term 2 (D1) — privileged information that does not transfer

Two fetched sources establish that "PI can fail to help" is a *published,
named* phenomenon with dedicated experimental designs:

- **DOPD** — https://arxiv.org/html/2606.30626v1 — **FETCHED**: "the apparent
  superiority of a privileged teacher does not always correspond to transferable
  capability, but may instead arise from information asymmetry", which the paper
  names the **"privilege illusion"**. Its separation design is a token-ablation
  study using a "privilege advantage gap" = absolute log-probability difference
  between privileged-teacher and student policies given identical privileged
  inputs; ablating high-gap tokens costs ~50% efficiency while low-gap/random
  ablations do not — i.e. it *operationalises* the split between a capability gap
  and an information gap.
- "A Functional Perspective on Knowledge Distillation in Neural Networks" —
  https://arxiv.org/abs/2510.12615 — **FETCHED**: reports "a consistent and
  severe asymmetric transfer of negative knowledge to the student, raising safety
  concerns"; negative asymmetric transfer dominates even in self-distillation.
- Also returned, unfetched: the NeurIPS proceedings copy of Yang et al. 2022
  (batch 1's LUPI non-monotone-law citation) —
  https://proceedings.neurips.cc/paper_files/paper/2022/file/aa31dc84098add7dd2ffdd20646f2043-Paper-Conference.pdf ;
  https://arxiv.org/pdf/2602.04942 (privileged-information distillation for LMs,
  teacher/student share parameters and only the teacher sees PI — an architecture
  directly relevant to an r2s3/r2s4 matched-arm design);
  https://openreview.net/pdf?id=dg1tqNIWg3 ; https://arxiv.org/pdf/2110.14993
  (provably efficient learning with time-series PI);
  https://arxiv.org/html/2408.09035v1 (multi-teacher PKD explicitly "mitigating
  negative transfer").

### Term 3 (D2 reworded) — Bayes error for field-valued outputs

**No usable results** for the specific object. The returned material is generic
Bayes-error/irreducible-error exposition ("Bayes error rate is the lowest
possible error rate for any classifier … analogous to the irreducible error";
"the irreducible error is simply the variance of Y given that X = x") plus
classification-oriented estimation surveys (https://arxiv.org/pdf/1707.04025,
https://en.wikipedia.org/wiki/Bayes_error_rate). The search engine stated
explicitly that the results "don't contain specific information about
field-valued outputs, estimating Bayes error with few or paired samples". Two
independent search framings (iteration 1 term 3; here) have now failed to find
one — that strengthens iteration 1's read that the *composition* is open while
the *method class* is preempted.

## PRIOR-ART VERDICT (r2s4_diag, batch 2)

### D1 — value-of-LF accounting: matched +/-LF-training-signal arms, helmholtz-first, with pre-registered aleatoric-null datasets
**Verdict: `preempted-but-MF-composition-open`**
Preempted parts (all fetched this loop): the *matched-budget MF composition
study* (https://arxiv.org/abs/2511.01830 — "the first study of empirical scaling
laws for multi-fidelity neural surrogate datasets", dataset axis decomposed into
compute budget and composition); the *finding that privileged signal need not
transfer* (https://arxiv.org/html/2606.30626v1 "privilege illusion" +
https://arxiv.org/abs/2510.12615 negative asymmetric transfer), on top of batch
1's Yang et al. non-monotone LUPI law (https://arxiv.org/abs/2209.08754).
**Open**: no source found runs the ablation with the **null datasets
pre-registered because a training-free aleatoric ceiling was measured first**,
nor with LF *fields* as the privileged variable for a *field-valued* output
scored in copy-LF skill units. Also open and cheap: DOPD's advantage-gap idea
ported to fields (compare an LF-consuming teacher's and a condition-only
student's error *on the same samples* to split capability gap from information
gap) — that is a concrete, citable design B2 can adopt rather than invent.

### D2 — a ceiling estimator with support at 19 condition dims and N_hf = 5
**Verdict: `preempted (cite)` for the method class; `preempted-but-MF-composition-open` for this regime**
B1's two estimators are named published objects: matched-pair extrapolation to
zero distance is **the differogram**
(https://www.sciencedirect.com/science/article/abs/pii/S0925231205001682) and the
LOO k-NN bound is difference-based / neighbour-based variance estimation
(review: https://link.springer.com/chapter/10.1007/978-3-032-07178-1_19 — fetch
blocked by auth redirect; related https://arxiv.org/abs/1711.09208 **fetched**;
NNVE https://www.tandfonline.com/doi/abs/10.1198/016214502388618780). The failure
at 19 dims is a **known property** of the class, not an implementation defect.
The obvious remedy — reduce dimension first via active subspaces
(https://arxiv.org/pdf/2304.14142 **fetched**: finite-difference-based important
directions, "robust with respect to noise or lack of smoothness"; infinite-
dimensional version https://arxiv.org/pdf/2510.11871) — is itself published, and
the *combination* was suggested only by an unconfirmed search snippet.
**Open**: no fetched source estimates an irreducible error for a **field-valued**
output from ~400 samples in 19 dims, and none at N = 5 (two framings failed).
B2 must present this as "compose active-subspace projection with a named
variance estimator and report where support fails", never as a new estimator.
Hard constraint to state in the card: arXiv:2410.23440 (**fetched**, iteration 3)
proves "no method to approximate Lipschitz operators based on m linear samples
can achieve algebraic convergence rates in m" absent fast covariance decay — at
N_hf = 5 no ceiling claim is defensible at all.

### D3 — mandatory post-hoc shrinkage-toward-own-mean arm (and lambda* as a diagnostic)
**Verdict: `preempted-but-MF-composition-open`**
The shrinkage operation is James-Stein/ridge (Efron & Hastie CASI ch.7
https://efron.ckirby.su.domains/other/CASI_Chap7_Nov2014.pdf ; Hansen
https://web-docs.stern.nyu.edu/old_web/emplibrary/shrink3.pdf — snippet-level);
the *phenomenon* it corrects is the textbook MSE-conditional-mean result stated
verbatim in https://arxiv.org/html/2604.20061v1 (**fetched**: "A network trained
with mean-squared error converges to the conditional expectation … over-smoothed
by construction … This is not a training failure — it is the optimal MSE solution
given the information available"); and post-hoc rescaling on a held-out fold is
standard calibration practice. **Open**: every published post-hoc surrogate
calibrator found rescales *variance / interval width* and explicitly leaves the
point prediction unchanged (FALCON, https://arxiv.org/html/2607.01354v1
**fetched**: "the central amplitude A_NN remains unchanged"; and its ~1000-point
calibration-set requirement rules it out here anyway), and the two amplitude-
correcting methods need test-time observations (FreqNO-DPS,
https://arxiv.org/pdf/2606.03936). Using lambda* as a *reported diagnostic
statistic* — lambda* = 0 certifying that a model's condition-dependence is net
harmful — was not found anywhere. Do NOT claim shrinkage itself is novel.

### D4 — overfitting anatomy at N_hf in {5,20,50}
**Verdict: `preempted-but-MF-composition-open` — confidence upgraded from LOW to MEDIUM** (batch 1 asked for this re-search; it got a full turn in iteration 3)
Preempted: the decomposition is textbook (Test Error = Train Error + gap;
bias-variance-**noise** with noise = irreducible error), fine-grained variants
exist (https://arxiv.org/pdf/2011.03321, https://arxiv.org/pdf/2010.08127); HF
sample sweeps are routine. Hard citable constraint (**fetched**):
https://arxiv.org/abs/2410.23440 — no algebraic rate in m for Lipschitz
operators without fast covariance decay, "confirms the intrinsic difficulty of
learning Lipschitz operators, regardless of the data or learning technique".
**Still open after two batches**: any PDE-domain **n_eff / effective-sample-size
estimator**. The nearest published handle is redundancy pruning
(https://arxiv.org/abs/1905.12737v1 **fetched** — ensemble-uncertainty-based, "up
to 50% of the full dataset" removable, and its abstract defines **no** effective
sample size statistic). If B2/B3 wants n_eff it must define it locally and say
so; the drift-class rule in program.md 12.4 is a project convention, not a
citable method.
