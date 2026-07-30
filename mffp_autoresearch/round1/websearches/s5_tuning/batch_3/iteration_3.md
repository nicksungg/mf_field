# Iteration 3 — Q3: is "effective N of the realized per-batch loss" a published diagnostic?

## Search rationale

B2 part 7 pre-registers the B3 headline metric as *"effective N of the realized per-batch
loss, not of the target energy."* The stream needs to know whether that is (a) a
re-invention of a standard quantity, (b) a standard quantity used in an unusual place, or
(c) genuinely unoccupied — because s5 claims **no novelty** by charter, so if it is
standard the card simply cites it, and if it is not the card must not overclaim either.
s2-B3's report already located the *heavy-tail/ESS* literature outside SciML
(https://arxiv.org/pdf/1901.05555 class-balanced "effective number of samples";
https://arxiv.org/html/2601.15360v1), so I searched only the **realized-batch-loss
diagnostic** framing, which that report did not cover.

## Search terms used

1. `effective sample size of minibatch loss training diagnostic gradient dominated by few samples`
2. `"effective sample size" participation ratio loss concentration deep learning training metric`
3. `Kish effective sample size formula weighted loss neural network per-sample weights diagnostic`

## Findings

### Term 1 — effective minibatch size

Results: "Exploring Variance Reduction in Importance Sampling for Efficient DNN Training"
(https://arxiv.org/abs/2501.13296 / https://arxiv.org/pdf/2501.13296); resizable
mini-batch gradient (https://openreview.net/pdf?id=H1lGHsA9KX); large-minibatch SGD
(https://arxiv.org/pdf/1706.02677); second-order large-batch study
(https://arxiv.org/pdf/2012.08795); tutorial pages.

**FETCHED — https://arxiv.org/abs/2501.13296**, verbatim abstract: *"Importance sampling
is widely used to improve the efficiency of deep neural network (DNN) training by reducing
the variance of gradient estimators. ... This paper proposes a method for estimating
variance reduction during DNN training using only minibatches sampled under importance
sampling. By leveraging the proposed method, the paper also proposes an **effective
minibatch size** to enable automatic learning rate adjustment."* The abstract page does
**not** give the N_ems formula, so I can cite only the existence and purpose of an
"effective minibatch size" (variance-reduction accounting under importance sampling),
**not** a formula.

### Term 2 — ESS / participation ratio as a training metric

Results: Alex Smola, "The effective sample size"
(https://alex.smola.org/posts/40-effective-sample-size/); Class-Balanced Loss
(https://openaccess.thecvf.com/content_CVPR_2019/papers/Cui_Class-Balanced_Loss_Based_on_Effective_Number_of_Samples_CVPR_2019_paper.pdf
— already cited by s2-B3 via https://arxiv.org/pdf/1901.05555); SALT
(https://arxiv.org/abs/2606.05800); long-tailed dynamic class average loss (ScienceDirect).

**FETCHED — Smola, https://alex.smola.org/posts/40-effective-sample-size/**: definition
*"n_eff = 1/||alpha||_2^2 = 1/Sum_i alpha_i^2"* with weights normalized to sum 1; the ML
use quoted is RL replay buffers, where it is *"a diagnostic control signal: how much real
information the buffer still holds"*; the page *"does not discuss loss or gradient
concentration during training"*, only variance/tail concentration.

**FETCHED — SALT, https://arxiv.org/abs/2606.05800** (the search summariser had attributed
a "participation ratio / effective sample size proxy from signed per-sample update
contributions" to it). Verbatim abstract: *"under GRPO-style group normalization,
per-rollout policy-gradient features can concentrate into a low-rank, signed geometry,
causing substantial cancellation during aggregation and weakening the effective update ...
SALT estimates a dominant shared subspace from the mini-batch Gram geometry ..."*. The
fetch's explicit finding: *"the abstract does not mention an 'effective sample size' proxy,
participation ratio, or claims about batches yielding fewer independent signals than sample
count."* **So the participation-ratio attribution was a search-summariser artefact and is
NOT citable.** Recorded here so it is not silently reused. (The `/pdf/` fetch of the same
paper returned undecodable binary.)

### Term 3 — Kish N_eff on weighted losses

Results: FOSSIL (https://arxiv.org/pdf/2509.13218); R `svyweight::eff_n`
(https://search.r-project.org/CRAN/refmans/svyweight/html/eff_n.html); `balance` Python
package (https://arxiv.org/pdf/2307.06024); several causal-inference/IPW papers; Smola
again. The search summariser produced the Kish formula
`N_eff = (sum w_i)^2 / sum w_i^2`, the identity `Var(L_hat) = sigma^2 / N_eff`, and the
claim that generalization bounds scale with N_eff rather than n, attributing them to
FOSSIL. **FETCH FAILED to confirm**: https://arxiv.org/pdf/2509.13218 returned unusable
extraction and the fetch reported *"I cannot locate explicit definitions of the Kish
formula for N_eff, a statement equating Var(weighted loss) to sigma^2/N_eff, or mention of
N_eff as a training-time diagnostic in the material shown"* — it did confirm the title,
authors, and domain (*"handling imbalanced datasets and learning scenarios with limited
data"*). **Therefore the Kish-formula-on-weighted-loss claim is NOT citable from this
loop.** The only citable ESS definition I hold is Smola's `1/sum alpha_i^2`.

## Interpretation

ESS is a standard statistical quantity with a citable ML-side definition (Smola) and a
citable minibatch-side cousin ("effective minibatch size", 2501.13296), but **every
retrieved use computes it from importance/sampling weights**, i.e. from a *chosen*
weighting scheme. Nothing retrieved computes it from the **realized per-sample loss
energies of an unweighted MSE batch** as a diagnostic of training-set pathology. That is
the narrow slot B3's headline metric occupies — and it is a *measurement*, which is exactly
what s5's charter permits.
