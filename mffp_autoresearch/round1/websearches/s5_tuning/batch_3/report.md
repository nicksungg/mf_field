# Websearch Report — Stream `s5_tuning`, Batch 3

**Stream**: s5_tuning
**Batch**: 3
**Total iterations**: 5 (cap)
**WebSearch calls**: 15 (3 per iteration; the engine self-reformulated iteration 5's term 3
into four result sets, all recorded in `iteration_5.md`)
**WebFetch calls**: 19 (13 usable, 6 dead — listed under Dead ends)
**Cap hit**: YES (5/5 iterations). Not searched: nothing in the assigned scope was left
unsearched; all four scope items got a dedicated iteration plus a refutation pass.

**Scope discipline**: this loop is the **raw-target / LF-blind twin** of
`websearches/s2_beyond_copy/batch_3/report.md`. That report's **D1** ground (per-sample
normalization of the **fidelity-residual** target; DiSOL magnitude decoupling; the
heavy-tail/ESS-outside-SciML literature; tail-reweighting's fetched negative) was **not
re-searched** and is cited by reference. Everything below is new retrieval.

## Search trace

### Turn 1 — RevIN outside time series; target de-normalization by INPUT statistics → `iteration_1.md`
Terms: RevIN in PDE/operator learning; "normalize target by input statistics, denormalize
output" in image-to-image regression; APEX.
- RevIN-style normalize/denormalize **is already inside PDE surrogates**, twice: MORPH —
  *"We normalize the data and cache the corresponding means and standard deviations, then
  use these statistics to exactly denormalize model outputs"*
  [cite: https://arxiv.org/html/2509.21670v3] — following MPP.
- **The strongest general preemption of this batch**: WNE proves the wrapper *is* the
  function class — *"a parameter-free wrapper that normalizes the input, applies any
  backbone, and denormalizes the output. We prove every NE function admits this
  factorization, so the wrapper exactly parameterizes the class of NE functions"*; NE
  defined as `f(a y + b1) = a f(y) + b1` [cite: https://arxiv.org/abs/2605.08193]. Domain:
  blind image denoising, where input and target share a space.

### Turn 2 — H3: clipping as implicit reweighting; clip x loss-scale coupling → `iteration_2.md`
Terms: clipping/implicit reweighting under heavy tails; clip threshold vs loss scale and
redundancy with normalization; Adam scale invariance.
- Clipping **is** a modified loss: *"a loss function l equipped with gradient clipping is
  equivalent to a Huberised-like loss function"*, and it *"helps the loss function assign
  small gradients to outlier samples"* [cite: https://arxiv.org/html/2412.08941v4, quoting
  Menon et al.]. The same fetch notes **no per-sample weight formula** is derived.
- Threshold-scale coupling and redundancy: `ClipAbadi(g_i;R) = min(R/||g_i||,1) ≈
  R/||g_i||`; *"We can view eta_effective ≡ eta·R as a whole"*; under adaptive optimizers R
  *"cancels out"*, *"making the clipping threshold redundant across methods like Adam and
  LAMB"* [cite: https://ar5iv.labs.arxiv.org/html/2206.07136].
- APEX resolved: *"A lower-frequency neural operator first provides a coarse prediction ...
  from which we retain only the amplitude as a transferable structural anchor. A
  conditional flow-matching enhancer then reconstructs the target ..."*
  [cite: https://arxiv.org/abs/2605.26732] — architecture, **not** a scaler.
- Adam-scale-invariance line **abandoned**: fetch failed, no citable claim.

### Turn 3 — effective N of a realized batch loss as a diagnostic → `iteration_3.md`
Terms: effective minibatch size; ESS/participation ratio as a training metric; Kish N_eff on
weighted losses.
- ESS is textbook with an explicit **diagnostic** framing: *"n_eff = 1/||alpha||_2^2 =
  1/Sum_i alpha_i^2"*, used in RL replay buffers as *"a diagnostic control signal: how much
  real information the buffer still holds"*; the page *"does not discuss loss or gradient
  concentration during training"* [cite: https://alex.smola.org/posts/40-effective-sample-size/].
- An *"effective minibatch size"* exists, but for importance-sampling variance accounting
  [cite: https://arxiv.org/abs/2501.13296].
- **Honesty correction**: the participation-ratio/ESS-proxy attribution to SALT was a search
  summariser artefact — the verbatim abstract contains none of it
  [cite: https://arxiv.org/abs/2606.05800]. Not citable. Likewise the Kish-formula-on-
  weighted-loss attribution to FOSSIL could not be confirmed (fetch unusable) and is **not**
  cited.

### Turn 4 — target-scaling / dynamic-range studies in operator learning → `iteration_4.md`
Terms: operator-learning normalization ablations; dynamic range vs regression accuracy; MF
normalization practice.
- QuadNorm compares *"LayerNorm, InstanceNorm, GroupNorm, and RMSNorm, along with no
  normalization"* — i.e. **layers**; the fetch's explicit findings are that the paper
  *"does not explicitly distinguish whether normalization applies to inputs, targets, or
  feature activations"* and *"lacks direct ablations comparing global vs. instance/per-sample
  or min-max vs. standardization"*. Usable methodological line: *"Most benchmarks evaluate
  at the training resolution, which masks the effect of normalization-induced
  cross-resolution degradation"* [cite: https://arxiv.org/html/2605.07375].
- Dynamic-range-of-target-vs-accuracy: **no usable primary results** on two framings.

### Turn 5 — MANDATORY refutation pass → `iteration_5.md`
Terms: HF target scaled by LF magnitude in MF surrogates; clipping-vs-normalization
attribution ablations; per-sample normalization when the scale is unobservable at test time.
- MF survey (unified framework, **functional outputs**) is silent exactly where E1 lives:
  corrections are *purely additive*; *"the survey does not address ... per-sample scaling or
  normalization of functional outputs ... no discussion of normalizing high-fidelity targets
  by low-fidelity magnitude"* [cite: https://ar5iv.labs.arxiv.org/html/2408.17075].
- Clipping vs normalization as competing alternatives, with a fetched **negative for
  clipping**: *"gradient clipping does not improve the performance"* vs normalization
  *"improves significantly ... between 0.45 and 0.82 percentage points"*
  [cite: https://ar5iv.labs.arxiv.org/html/1707.06799].
- The E2 killer quote: *"In DAIN ..., per instance normalization is applied using learned
  scale and offset factors ... but no denormalization module is proposed"*; RevIN's own
  statistics are the observed window's, *"available at inference"*; plus
  *"training via backpropagation in the normalized space yields better models ... even when
  evaluating with the non-normalized MSE"* and *"normalizing by instance on certain
  stationary datasets might be detrimental"* [cite: https://arxiv.org/html/2603.11869].

## Prior-art verdict

| Candidate direction | Verdict | Citations (fetched in THIS loop) | What remains open |
|---|---|---|---|
| **E1** — arm A3 `revin_lf` at 200 epochs: per-sample de-normalization of the **raw HF target** by a scalar statistic of the **LF input field** (`s_i = max\|LF_i\|`), scaler-only, zero new parameters, across an LF-pretrain -> HF-finetune boundary | **preempted-but-MF-composition-open** | WNE: *"a parameter-free wrapper that normalizes the input, applies any backbone, and denormalizes the output. We prove every NE function admits this factorization"*, NE = `f(ay+b1)=af(y)+b1` — https://arxiv.org/abs/2605.08193 (`iteration_1.md`). MORPH: *"normalize the data and cache the corresponding means and standard deviations, then use these statistics to exactly denormalize model outputs"* — https://arxiv.org/html/2509.21670v3 (`iteration_1.md`). RevIN construction + inference-available statistics — https://arxiv.org/html/2603.11869 (`iteration_5.md`). APEX = learned coarse operator + flow-matching enhancer, **not** a scaler — https://arxiv.org/abs/2605.26732 (`iteration_2.md`). MF survey silent on per-sample functional-output scaling — https://ar5iv.labs.arxiv.org/html/2408.17075 (`iteration_5.md`) | (i) the statistic comes from a **different fidelity's field**, not the sample's own target — unretrieved anywhere; (ii) applied to a **raw** (non-residual) target, which is the complement of s2-B3's D1; (iii) as a **scaler-only knob**, zero new parameters, inside a few-HF-sample MF recipe whose own survey leaves field magnitude *"to each surrogate's implicit assumptions"*; (iv) **WNE's guarantee does not transfer**: in denoising input and target share a space, across a fidelity boundary they do not, so `max\|LF_i\|`-as-HF-scale-proxy is an empirical question (B2 measured helmholtz 3929x -> 1.74x; sharp CV <= 0.0099 = no-op) |
| **E2** — LF-free per-sample-scale arm on the raw target (`s_i = max\|Y_i\|`) | **preempted (cite)** — and retrieval says the only honest s5-legal form is an **oracle** arm | DAIN: *"per instance normalization is applied using learned scale and offset factors ... but no denormalization module is proposed"*; RevIN's statistics are the observed window's, *"available at inference"* — https://arxiv.org/html/2603.11869 (`iteration_5.md`). Cross-ref (s2-B3's fetch, not mine): DiSOL's *"optional amplitude regressor"* — https://arxiv.org/html/2601.09143v1 | Only the framing. `max\|Y_i\|` is unobservable at test time, so the arm is either an **oracle upper bound** (a measurement — legal, cheap, must be labelled) or needs a scale predictor, which s5-B2's territory ruling and program.md §12.5 both place **outside s5**. Nothing about the *mechanism* is open |
| **E3** — H3: per-batch gradient-norm / clip-rate logging to test whether `grad_clip=1.0`, not the scaler, robustified the dominant helmholtz sample | **preempted (cite)** for the mechanism; **open** for the attribution measurement | *"a loss function l equipped with gradient clipping is equivalent to a Huberised-like loss function"*; clipping *"helps the loss function assign small gradients to outlier samples"* — https://arxiv.org/html/2412.08941v4 (`iteration_2.md`). `min(R/\|\|g\|\|,1) ≈ R/\|\|g\|\|`; *"eta_effective ≡ eta·R"*; R *"cancels out"*, *"making the clipping threshold redundant across methods like Adam and LAMB"* — https://ar5iv.labs.arxiv.org/html/2206.07136 (`iteration_2.md`). Clipping *"does not improve the performance"* vs normalization *"improves significantly ... 0.45 to 0.82 percentage points"* — https://ar5iv.labs.arxiv.org/html/1707.06799 (`iteration_5.md`) | Nobody uses **clip rate as the explanatory variable for a target-normalization result** — i.e. nobody asks "was the normalization gain actually the clipper?". Also note the transfer caveat: 2206.07136's redundancy result is for **per-sample** (DP-SGD) clipping, ours is a **whole-batch** norm clip, so it is an argument, not a theorem about our recipe |
| **E4a** — headline metric: **effective N of the realized per-batch loss** | **preempted** as a formula; **open** as this diagnostic | *"n_eff = 1/\|\|alpha\|\|_2^2 = 1/Sum_i alpha_i^2"*, *"a diagnostic control signal"*, and explicitly *"does not discuss loss or gradient concentration during training"* — https://alex.smola.org/posts/40-effective-sample-size/ (`iteration_3.md`). *"effective minibatch size to enable automatic learning rate adjustment"* under importance sampling — https://arxiv.org/abs/2501.13296 (`iteration_3.md`). Cross-ref (s2-B3): class-balanced effective number — https://arxiv.org/pdf/1901.05555 | Every retrieved use computes ESS from **chosen sampling/importance weights**. Computing it from the **realized per-sample loss energies of an unweighted MSE batch**, as a dataset-pathology diagnostic that a *global* scaler provably cannot move (B2: 1.0145/400 vs 1.0179/400), is unretrieved. **Cite the formula, claim only the application** |
| **E4b** — eligibility rule `G = max\|Y_train\|/sd(Y_train) >= 8` gated on a live pattern channel | **novel** (narrow), nearest neighbour is the qualitative version of the same claim | *"normalizing by instance on certain stationary datasets might be detrimental"* (instance norm **increases** distribution distance on Traffic) — https://arxiv.org/html/2603.11869 (`iteration_5.md`). *"Most benchmarks evaluate at the training resolution, which masks the effect of normalization-induced cross-resolution degradation"* — https://arxiv.org/html/2605.07375 (`iteration_4.md`) | Everything quantitative: no retrieved source offers a **target dynamic-range statistic as a pre-registered eligibility predictor** for whether a normalization change will act. Given §13.3 (0-for-4) and s5's no-novelty charter, present G as **a predictor under test**, not a contribution |

## Citations summary

Fetched and usable in this loop:
- [2026] "Normalization Equivariance for Arbitrary Backbones, with Application to Image Denoising" (WNE) — https://arxiv.org/abs/2605.08193 (also https://arxiv.org/pdf/2605.08193) — used in: iteration_1, verdict E1
- [2025/26] MORPH, "PDE Foundation Models with Arbitrary Data Modality" — https://arxiv.org/html/2509.21670v3 — used in: iteration_1, verdict E1
- [2026] APEX, "Amplitude Anchors and Phase Priors for Target-Scarce Higher-Frequency Wave Prediction" — https://arxiv.org/abs/2605.26732 — used in: iteration_2, verdict E1
- [2024/26] "Optimized Gradient Clipping for Noisy Label Learning" (quoting Menon et al. on the Huberised-loss equivalence) — https://arxiv.org/html/2412.08941v4 — used in: iteration_2, verdict E3
- [Bu et al. 2022] "Automatic Clipping: Differentially Private Deep Learning Made Easier and Stronger" — https://ar5iv.labs.arxiv.org/html/2206.07136 — used in: iteration_2, verdict E3
- [Smola] "The effective sample size" — https://alex.smola.org/posts/40-effective-sample-size/ — used in: iteration_3, verdict E4a
- [2025] "Exploring Variance Reduction in Importance Sampling for Efficient DNN Training" — https://arxiv.org/abs/2501.13296 — used in: iteration_3, verdict E4a
- [2026] SALT — https://arxiv.org/abs/2606.05800 — used in: iteration_3 as a **negative/correction** (the ESS-proxy attribution is NOT in the paper)
- [2026] QuadNorm, "Resolution-Robust Normalization for Neural Operators" — https://arxiv.org/html/2605.07375 — used in: iteration_4, verdict E4b
- [2024] "A survey on multi-fidelity surrogates for simulators with functional outputs" — https://ar5iv.labs.arxiv.org/html/2408.17075 — used in: iteration_5, verdict E1
- [Reimers & Gurevych 2017] "Optimal Hyperparameters for Deep LSTM-Networks for Sequence Labeling Tasks" — https://ar5iv.labs.arxiv.org/html/1707.06799 — used in: iteration_5, verdict E3
- [2026] "On the Role of Reversible Instance Normalization" — https://arxiv.org/html/2603.11869 — used in: iteration_5, verdicts E1/E2/E4b

Search-listed only (located, NOT fetched — do not quote):
- RevIN original — https://openreview.net/forum?id=cGDAkQo1C0p , https://seharanul17.github.io/RevIN/
- DAIN — https://arxiv.org/pdf/1902.07892 (its content reaches us only through 2603.11869's quote)
- MF-FNO for geological carbon storage (min-max on **inputs**) — https://arxiv.org/pdf/2308.09113
- Convolutional Neural Operators — https://arxiv.org/pdf/2302.01178 ; Multi-Grid Tensorized FNO — https://arxiv.org/pdf/2310.00120 ; PDE-Transformer — https://arxiv.org/html/2505.24717
- "Revisiting Gradient Normalization and Clipping ... Heavy-Tailed Noise" — https://arxiv.org/html/2410.16561 ; "Gradient Quantile Clipping" — https://arxiv.org/pdf/2309.17316 ; NFNets/AGC — https://arxiv.org/pdf/2102.06171 ; ZClip — https://arxiv.org/pdf/2504.02507
- FOSSIL — https://arxiv.org/pdf/2509.13218 (Kish-formula attribution UNCONFIRMED — must not be cited)

Cross-references to other agents' fetches (cited as theirs, not mine):
- DiSOL magnitude decoupling — https://arxiv.org/html/2601.09143v1 — `websearches/s2_beyond_copy/batch_3/iteration_4.md`
- Class-Balanced Loss / effective number — https://arxiv.org/pdf/1901.05555 — `websearches/s2_beyond_copy/batch_3/iteration_2.md`
- MPP (RevIN in a PDE surrogate) — https://arxiv.org/html/2310.02994v2 — `websearches/s5_tuning/batch_2/iteration_3.md`

## Dead ends

- `https://openreview.net/pdf?id=rklB76EKPr` (Menon et al., "Can gradient clipping mitigate
  label noise?") → OpenReview browser-verification page, no content. The result is cited
  **through** https://arxiv.org/html/2412.08941v4, which quotes it.
- `https://arxiv.org/pdf/2206.07136`, `https://arxiv.org/pdf/2606.05800`,
  `https://arxiv.org/pdf/2509.13218` → undecodable PDF binary. **Use `/abs/`, `/html/<id>v1`,
  or `ar5iv.labs.arxiv.org/html/<id>`** (worked for 2206.07136, 1707.06799, 2408.17075).
- `https://arxiv.org/abs/2303.11257` (Unit Scaling) → abstract page carries none of the
  loss-scaling/Adam-invariance content; the Adam scale-invariance line was **dropped**, not
  cited from memory.
- `https://ar5iv.labs.arxiv.org/html/2308.09113` → "Fatal error during HTML conversion".
- Term framings with **no usable results**: "dynamic range of target field affects neural
  network regression accuracy ... physics surrogate" (the summariser itself concluded no
  such paper surfaced) and three re-formulations of "per-sample target normalization without
  access to target at test time" (returned bioinformatics normalization and USPTO patents).
  Those absences ARE the E4b / Q4 finding.

## For the brainstormer

The brainstormer MUST quote the verdict for whatever it proposes.

1. **Lead with E1 (arm A3 `revin_lf` at 200 epochs)** and quote:
   *"preempted-but-MF-composition-open — the normalize/denormalize wrapper is not merely
   published but PROVEN to exhaust the function class ('a parameter-free wrapper that
   normalizes the input, applies any backbone, and denormalizes the output. We prove every
   NE function admits this factorization', https://arxiv.org/abs/2605.08193), and it is
   already inside PDE surrogates ('use these statistics to exactly denormalize model
   outputs', https://arxiv.org/html/2509.21670v3). What is unoccupied is taking the
   statistic from a DIFFERENT FIDELITY's field and applying it to a RAW HF target: the 2024
   MF survey of functional-output surrogates uses purely additive corrections and 'does not
   address ... per-sample scaling or normalization of functional outputs'
   (https://ar5iv.labs.arxiv.org/html/2408.17075), and the nearest MF occupant, APEX, is a
   learned operator + flow-matching enhancer, not a scaler (https://arxiv.org/abs/2605.26732)."*
   Add the **statable delta**: WNE's equivariance holds because denoising's input and target
   share a space; across a fidelity boundary they do not, so `max|LF_i|`-as-HF-scale-proxy is
   an empirical claim B2 already quantified (helmholtz 3929x -> 1.74x; sharp CV <= 0.0099).
2. **Label the LF-free arm (E2) an ORACLE, not a method.** Retrieval is decisive: RevIN
   works because its statistics are the observed window's, *"available at inference"*, and
   DAIN, which learns the scale instead, has *"no denormalization module"*
   (https://arxiv.org/html/2603.11869). A train-time `max|Y_i|` used at test time is an
   oracle upper bound; a scale predictor is architecture and leaves s5. Say which one is
   being run, in the card, before submit.
3. **H3 (E3) is the batch's cleanest genuine contribution — but as an ATTRIBUTION
   measurement.** The mechanism is fully published (clipping = Huberised loss,
   https://arxiv.org/html/2412.08941v4; threshold absorbed into the effective LR and
   redundant under adaptive optimizers, https://ar5iv.labs.arxiv.org/html/2206.07136;
   clipping-vs-normalization head-to-head with clipping losing,
   https://ar5iv.labs.arxiv.org/html/1707.06799). Unretrieved: anyone using **clip rate as
   the explanatory variable for a target-normalization result**. Carry the caveat that
   2206.07136's redundancy is for per-sample DP clipping, ours is whole-batch.
4. **A `grad_clip`-off control arm is now well-motivated by retrieval, not just by H3.** If
   the clipper is the robustifier, `maxabs + no clip` and `zscore + no clip` should converge;
   1707.06799 supplies a fetched precedent where clipping was **inert** while normalization
   was not — i.e. the *opposite* of H3 — so both signs have published support and the card
   should pre-register both outcomes as informative.
5. **Effective N (E4a): cite the formula, claim the application.**
   `n_eff = 1/Sum_i alpha_i^2` is textbook (https://alex.smola.org/posts/40-effective-sample-size/)
   and an "effective minibatch size" exists for importance sampling
   (https://arxiv.org/abs/2501.13296); nobody computes it from the realized per-sample loss
   energies of an **unweighted** MSE batch. Pair it with B2's proof that a global scaler
   cannot move it (1.0145/400 -> 1.0179/400) — that pairing is the card's evidence design.
6. **Do not overclaim G (E4b).** `novel` (narrow), but the nearest neighbour already says
   the qualitative thing — instance normalization *"on certain stationary datasets might be
   detrimental"* (https://arxiv.org/html/2603.11869). Pre-register G >= 8 + live pattern
   channel as a **predictor under test**, with the four sharp sets as pre-declared NULLs
   (floors: pfc 1.151, allen_cahn 1.633, fisher_kpp 0.418, cahn_hilliard 0.553; helmholtz
   report-only 9.695; ifc_poisson 0.240; geomean 0.884). A uniform gain across all six would
   falsify the mechanism story even if the geomean improves.
7. **One retrieved design warning worth pre-registering**: *"training via backpropagation in
   the normalized space yields better models ... even when evaluating with the non-normalized
   MSE"* (https://arxiv.org/html/2603.11869). Our scored metric is the raw-field per-sample
   rel-L2, so a per-sample scaler changes *which* samples the optimizer serves relative to
   the metric. State the train-space/score-space mismatch explicitly rather than letting it
   be an unexamined confound.
