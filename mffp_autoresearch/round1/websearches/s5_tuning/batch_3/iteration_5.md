# Iteration 5 — MANDATORY refutation pass + prior-art verdicts (ITERATION CAP REACHED)

**Cap note**: this is iteration 5 of 5. No further searching is permitted; the verdicts
below are final for this loop.

## Search rationale

Iterations 1-4 established the field context for all four scope items. Per the websearcher
contract §3.3, this final turn spends its three terms exclusively on **refutation** — each
term is framed as "has this exact composition already been done?" against one of the four
candidate directions B3 is likely to propose.

## The candidate directions being refuted

Taken from B2 part 7's `next_direction` and the orchestrator's B3 scoping:

- **E1** — arm A3 `revin_lf` at 200 epochs: per-sample de-normalization of the **raw HF
  target** by a scalar statistic of the **LF input field** (`s_i = max|LF_i|`, both stages,
  `maxabs` fallback where the split ships no LF), scaler-only, zero new parameters, across
  an LF-pretrain -> HF-finetune fidelity boundary.
- **E2** — an **LF-free** per-sample-scale arm on the raw target (train-time `s_i =
  max|Y_i|`; the scale is *not observable at test time*).
- **E3** — **H3**: per-batch gradient-norm / clip-rate logging to attribute B2's zscore
  gain to `grad_clip = 1.0` rather than to the scaler.
- **E4** — headline metric **effective N of the realized per-batch loss**, plus the
  eligibility predictor **`G = max|Y_train|/sd(Y_train) >= 8` gated on a live pattern
  channel**.

## Search terms used (refutation-framed: "has this been done?")

1. `normalize high-fidelity target by low-fidelity solution magnitude per-sample rescale prediction multi-fidelity surrogate`
2. `ablation gradient clipping versus data normalization which caused improvement clip rate logging attribution`
3. `per-sample target normalization without access to target at test time predicted scale factor regression scale head`

## Findings

### Term 1 (refutes E1) — does anyone scale the HF target by the LF field's magnitude?

Results: MF survey with unified framework and benchmark (https://arxiv.org/pdf/2408.17075);
MF Residual Neural Processes (https://arxiv.org/pdf/2402.18846); MF reduced-order
surrogate modelling (Royal Society A); generative MF downscaling
(https://arxiv.org/html/2509.22474v1); MF surrogate via single linear regression
(https://arxiv.org/pdf/1705.02956); LF-guided DoE (ScienceDirect).
Search summariser surfaced the classical comprehensive-correction form
`H_hat(x) = rho * L_hat(x) + delta_hat(x)` — i.e. a **scale factor multiplying the LF
prediction**, not a normalizer of the target.

**FETCHED — MF survey, https://ar5iv.labs.arxiv.org/html/2408.17075**: the survey's
corrective method is *purely additive* — high-fidelity prediction = low-fidelity simulator
output plus a learned correction — and the fetch's explicit findings are: *"the document
does not discuss multiplicative/comprehensive correction formulations"* and *"Regarding
per-sample scaling or normalization of functional outputs: the survey does not address this
either ... it contains no discussion of normalizing high-fidelity targets by low-fidelity
magnitude or applying per-sample scaling to the functional fields themselves during
training. The survey standardizes comparison metrics but leaves individual field magnitude
handling to each surrogate's implicit assumptions."*
**This is the strongest negative retrieved for E1**: a 2024 survey whose stated purpose is
a unified framework for MF surrogates with **functional outputs** is silent on per-sample
field-magnitude handling.

### Term 2 (refutes E3) — is clipping-vs-normalization attribution published?

Results: "Optimal Hyperparameters for Deep LSTM-Networks for Sequence Labeling Tasks"
(https://arxiv.org/pdf/1707.06799); "Gradient Shaping Beyond Clipping"
(https://arxiv.org/pdf/2510.01578); policy-gradient second-order momentum
(https://arxiv.org/pdf/2505.11561); "Altering Backward Pass Gradients"
(https://arxiv.org/pdf/2111.12495); three practitioner pages (linkedin, datacamp,
metricgate) that describe **clip-rate logging** as monitoring practice — secondary sources,
**not cited**.

**FETCHED — https://ar5iv.labs.arxiv.org/html/1707.06799**: an explicit head-to-head
ablation treating the two as alternatives for the same purpose — *"gradient clipping does
not improve the performance"* (thresholds 1, 3, 5, 10; no statistically significant
improvement vs no clipping), whereas *"Gradient normalization ... improves significantly
the performance with an observed average improvement between 0.45 and 0.82 percentage
points"*, with the authors recommending normalization as *"has a better theoretical
justification"*. Domain: LSTM sequence labeling, **not** PDE/operator learning, and the
"normalization" there is of the *gradient*, not of the *target*.

### Term 3 (refutes E2) — per-sample normalization when the scale is unobservable at test time

The engine ran four re-formulations; usable hits: DAIN
(https://arxiv.org/pdf/1902.07892), RevIN critique (https://arxiv.org/html/2603.11869),
SPADE (https://arxiv.org/pdf/1903.07291), instance-norm reference pages (MATLAB,
labml.ai, GeeksforGeeks — secondary, not cited). Everything else returned bioinformatics
normalization and USPTO patents: **no usable results** on those framings.

**FETCHED — RevIN critique, https://arxiv.org/html/2603.11869** (re-fetched in this loop
with an E2-targeted prompt so the s5 verdict rests on my own retrieval):
- scope: *"Inspired by the normalization techniques from other domains, Kim et al. (2022)
  proposed Reversible Instance Normalization for time series forecasting"*, and the work
  *"focuses exclusively on time series applications with no discussion of broader domains"*;
- availability: statistics are the instance's own look-back window,
  `mu_x = 1/L sum x_i`, `sigma_x^2 = 1/(L-1) sum (x_i - mu_x)^2`, *"available at inference
  since they derive from the look-back window itself"*;
- **the decisive E2 quote**: *"In DAIN (Passalis et al., 2019), per instance normalization
  is applied using learned scale and offset factors ... **but no denormalization module is
  proposed**"*;
- *"training via backpropagation in the normalized space yields better models ... even when
  evaluating with the non-normalized MSE"*;
- and the eligibility-shaped caveat: *"normalizing by instance on certain stationary
  datasets might be detrimental"* (instance normalization **increases** distribution
  distance on the Traffic dataset).

## Prior-art verdicts (final)

### E1 — `revin_lf`: raw HF target de-normalized by an LF-field statistic
**`preempted-but-MF-composition-open`.**
Preempted at mechanism level, three independent ways, all fetched in this loop:
(a) the wrapper is a **theorem** — WNE: *"a parameter-free wrapper that normalizes the
input, applies any backbone, and denormalizes the output. We prove every NE function admits
this factorization, so the wrapper exactly parameterizes the class of NE functions"*
(https://arxiv.org/abs/2605.08193, image denoising, iteration_1);
(b) normalize/denormalize with **inference-available input statistics** is RevIN's defining
construction (https://arxiv.org/html/2603.11869, this iteration);
(c) it is already **inside PDE surrogates** — MORPH: *"We normalize the data and cache the
corresponding means and standard deviations, then use these statistics to exactly
denormalize model outputs"* (https://arxiv.org/html/2509.21670v3, iteration_1), following
MPP (https://arxiv.org/html/2310.02994v2, s5-B2's fetch).
**Open**: the statistic taken from a **different fidelity's field** (the LF companion),
applied to a **raw HF target**, as a **scaler-only knob with zero new parameters** in a
few-HF-sample MF recipe. The MF survey that is supposed to unify functional-output MF
surrogates *"does not address ... per-sample scaling of functional outputs"*
(https://ar5iv.labs.arxiv.org/html/2408.17075); the nearest MF occupant, APEX, is a
**learned coarse operator + conditional flow-matching enhancer**, not a scaler
(https://arxiv.org/abs/2605.26732, iteration_2).
**Statable delta (important)**: WNE's guarantee holds because in denoising the input and
the target live in the **same space**, so `f(a·y+b) = a·f(y)+b` is meaningful. Across a
**fidelity boundary** LF and HF do **not** share a space, so the equivariance theorem does
**not** transfer for free — whether `max|LF_i|` is a good proxy for the HF sample's scale is
an empirical question, and B2 already measured it (helmholtz 3929x -> 1.74x residual scale
spread; sharp sets CV <= 0.0099, i.e. a no-op).

### E2 — LF-free per-sample scale on a raw target
**`preempted (cite)` — and retrieval says the honest form is an ORACLE arm, not a method.**
RevIN works because its statistics come from the observed input window
(https://arxiv.org/html/2603.11869); DAIN, which learns the scale instead, *"no
denormalization module is proposed"* (same source). A raw-target `s_i = max|Y_i|` is not
observable at test time, so the arm is either (i) an **oracle upper bound** — legitimate
and cheap, but must be labelled as a measurement, not a method — or (ii) it needs a scale
predictor, which s5-B2's standing territory ruling and program.md §12.5 both put **outside
s5** (a learned scale head = architecture). s2-B3's D1 supplies the residual-side precedent
for the predictor route (DiSOL's *"optional amplitude regressor"*,
https://arxiv.org/html/2601.09143v1 — **their** fetch, cited as a cross-reference).

### E3 — H3, clip-rate as the explanatory variable
**`preempted (cite)` for the mechanism; `open` for the attribution measurement.**
Mechanism published: *"a loss function l equipped with gradient clipping is equivalent to a
Huberised-like loss function"* and clipping *"helps the loss function assign small gradients
to outlier samples"* (https://arxiv.org/html/2412.08941v4 quoting Menon et al.,
iteration_2). Scale coupling and redundancy published: `ClipAbadi(g;R) = min(R/||g||,1) ≈
R/||g||`, *"eta_effective ≡ eta·R"*, and R *"cancels out"* under adaptive optimizers,
*"making the clipping threshold redundant across methods like Adam and LAMB"*
(https://ar5iv.labs.arxiv.org/html/2206.07136, iteration_2). Clipping-vs-normalization as
competing alternatives, with a fetched **negative for clipping**: *"gradient clipping does
not improve the performance"* vs normalization *"improves significantly ... 0.45 to 0.82
percentage points"* (https://ar5iv.labs.arxiv.org/html/1707.06799, this iteration).
**Open**: nothing retrieved uses **clip rate as the explanatory variable for a
target-normalization result** — i.e. nobody tests "was the normalization gain actually the
clipper?". That attribution is what B3 can claim, as a measurement.

### E4a — effective N of the realized per-batch loss as the headline metric
**`preempted` as a formula; `open` as this particular diagnostic.**
`n_eff = 1/||alpha||_2^2 = 1/sum_i alpha_i^2` with a **diagnostic** framing is textbook
(https://alex.smola.org/posts/40-effective-sample-size/, iteration_3); an "effective
minibatch size" exists for importance-sampled DNN training
(https://arxiv.org/abs/2501.13296, iteration_3); the class-balanced "effective number of
samples" is s2-B3's citation (https://arxiv.org/pdf/1901.05555). **Every retrieved use
computes it from chosen sampling/importance weights.** Nothing retrieved computes it from
the **realized per-sample loss energies of an unweighted MSE batch** as a diagnostic of a
dataset's pathology. Claim the *application*, cite the *formula*.
**Honesty correction carried from iteration_3**: the "participation ratio / effective sample
size proxy from signed per-sample update contributions" attributed to SALT by a search
summariser is **not in the paper** (verbatim abstract fetched,
https://arxiv.org/abs/2606.05800) — do not cite it.

### E4b — `G = max|Y|/sd(Y) >= 8` + live-pattern gate as a pre-registered eligibility rule
**`novel` (narrow), with the nearest neighbour being a qualitative version of the same
claim.** No retrieved source proposes a **target dynamic-range statistic** as a
**quantitative eligibility predictor** for whether a normalization change will act. Nearest
neighbours: the RevIN critique's *"normalizing by instance on certain stationary datasets
might be detrimental"* with a distribution-distance demonstration on Traffic
(https://arxiv.org/html/2603.11869) — same shape of claim, no predictor; and QuadNorm's
methodological warning that *"Most benchmarks evaluate at the training resolution, which
masks the effect of normalization-induced cross-resolution degradation"*
(https://arxiv.org/html/2605.07375, iteration_4) — the same "normalization effects are
masked by how you evaluate" hygiene point in a different variable. Given program.md
§13.3's 0-for-4 record and s5's no-novelty charter, the card should present G as a
**pre-registered predictor being tested**, not as a claimed contribution.

## Interpretation

Every mechanism B3 would touch is published; **none of the four is published in B3's
composition**, and two of the four (E2, E4a) are honest only if framed as measurements
rather than methods. That is the correct posture for a tuning stream.
