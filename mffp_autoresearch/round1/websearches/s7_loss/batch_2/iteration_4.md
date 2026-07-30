# Iteration 4 — `s7_loss` batch 2 (§3.3 refutation pass, part 1)

## Search rationale

ENOUGH was declared in iteration 3. This turn's only goal is to **refute
novelty** for three of the candidate directions batch 2 may propose:

- **D3 — copy-LF-referenced per-sample loss weight** `w_i = 1/‖y_i − LF_i‖²`
  (train the panel's skill denominator directly; LF used at training time only,
  so ADR 0009 is untouched; a fixed per-sample constant ⇒ convex in `p`, so
  B1's origin stationary point is impossible by construction).
- **D4 — tempered per-sample norm weight** `w_i = ‖y_i‖^{−2β}`, β ∈ [0,1],
  a continuous MSE↔rel-MSE dial with an effective-sample-fraction readout.
- **D5 — jointly trained scalar gain head** on a normalized-shape objective
  (the loss-level analogue of s1-B3's post-hoc closed-form ridge gain head).

## Search terms used

1. `"skill score" as training loss deep learning normalize each sample by reference forecast error downscaling super-resolution baseline-relative loss`
2. `loss weight target magnitude power exponent tuning between absolute and relative error regression scale sensitivity alpha`
3. `network predicts normalized field and separate scalar amplitude head rescale output per-sample gain regression PDE field super-resolution`

## Findings

### Term 1 → D3 (copy-LF-referenced weighting)

Top results: `https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12205029`
(US patent, deep generative weather forecasting), `https://arxiv.org/pdf/2209.05128`,
`https://arxiv.org/html/2307.02694v3`, `https://arxiv.org/pdf/2106.06033`,
`https://arxiv.org/pdf/2606.09954`.

Three distinct near-neighbours appear, and **none is the construction**:
(i) *ratio-to-a-baseline-loss* — the returned patent text describes minimizing
"the ratio of the loss over a baseline … [where] the baseline may be a copy of
the current loss without the backward gradient path", so that "all mini-batches
may have the same importance regardless of the loss value". That normalizes by
the **model's own detached loss**, per mini-batch, for optimization speed — not
by an independent reference model's per-sample error, and it carries no
fidelity semantics. (ii) *skill score as verification* — "a quantitative
measure of the performance of the model in comparison to a reference", stated
for validation/testing, with the explicit division of labour that "in the
training phase loss functions should be chosen according to the learning task,
and in the validation/testing phase skill scores should [be used]". (iii)
*Fractions Skill Score as a training loss* for precipitation nowcasting — a
**spatial-tolerance** verification metric turned into a loss; FSS has no
reference-forecast denominator, so it does not preempt per-sample
baseline-error weighting.

I could not fetch a citable page for (i)/(iii) this turn (the patent endpoint
is a PDF of the class batch 1 found unfetchable). Carried to iteration 5.

### Term 2 → D4 (tempered exponent β)

**No usable results** for a target-magnitude power weight in regression. The
returned exponent-tuning precedents are in *ordinal classification*
(class-distance weighted cross-entropy with a tunable α,
`https://www.emergentmind.com/topics/class-weighted-loss`) and *imbalanced
classification* (inverse-frequency / effective-number weighting with swept
exponents, same page). The only amplitude-adjacent statement returned — that
loss weights should track "the effective amplitude with which each independent
source component is expressed through the corrupted input" rather than total
target energy — is from a source-separation context and was not fetched.
The class-imbalance lineage (effective number of samples) is the honest nearest
neighbour for the **effective-sample-fraction** readout, but it re-weights
*classes*, not per-sample target norms in field regression.

### Term 3 → D5 (jointly trained gain head)

Top results: `https://arxiv.org/html/2406.17244v2` (Near-Field Super-Resolution
Network), `https://www.sciencedirect.com/science/article/pii/S2095034925000364`
(physics field SR via diffusion + FNO), `https://arxiv.org/html/2411.07576v2`
(Multiscale Corrections by Continuous Super-Resolution),
`https://arxiv.org/pdf/2101.09839` (Variational Multi-scale Super-resolution).

The pattern in every hit is **normalize inputs and outputs to [0,1] (or into
normalized basis coefficients) and predict in the normalized space** — the
normalization is a *preprocessing convention*, and the de-normalizing scale is
a known dataset constant, not a **predicted per-sample quantity**. No hit
splits the prediction into a normalized shape plus a learned scalar gain that
is trained jointly with a shape loss. Combined with iteration 2's finding that
"amplitude calibration" in this literature means *uncertainty* calibration,
D5's mechanism remains unrefuted at the level of PDE-field surrogates.

## Interpretation

D4 is the weakest: its mechanism (exponent-swept magnitude weighting) is a
standard tuning idiom in the imbalance literature and would be a knob, not a
finding. D3 and D5 both survived a dedicated refutation turn — D3's nearest
neighbours (batch-loss ratio normalization, skill-as-verification, FSS-as-loss)
each miss the per-sample reference-error denominator; D5's nearest neighbours
normalize by dataset constants rather than predicting the gain. One more
refutation turn is needed to (a) ground the LpLoss/metric-aligned-training
question with a fetched source and (b) give D3 a second, differently-framed
attempt at refutation before it can be called open.
