# Iteration 2 — H3: gradient clipping as the implicit robustifier, and clipping x loss-scale coupling

## Search rationale

Scope item 2. B2's handoff leaves H3 explicitly untested: *"`grad_clip = 1.0` interacts
directly with the loss scale (helmholtz's `maxabs` loss is ~1/1558 of the `zscore`
loss). If the clipper is what robustified the outlier, a per-batch gradient-norm/clip-rate
log is one cheap line of instrumentation that would settle it."* For the B3 card to claim
anything here I need (a) whether clipping-as-implicit-per-sample-reweighting is published,
and (b) whether the clip threshold's dependence on the loss scale, and its redundancy with
normalization, are published. Carried over from iteration 1: the APEX fetch.

## Search terms used

1. `gradient clipping implicit reweighting heavy-tailed loss distribution outlier samples robustness`
2. `gradient clipping threshold depends on loss scale normalization redundant per-sample normalization training`
3. `Adam scale invariance loss rescaling gradient clipping epsilon breaks invariance`

(+ carry-over fetch of APEX from iteration 1's term 3.)

## Findings

### Carry-over — APEX (https://arxiv.org/abs/2605.26732), FETCHED

Verbatim abstract: *"A central difficulty is that cross-frequency transfer is inherently
asymmetric: coarse amplitude structure remains relatively stable across frequencies,
whereas phase-sensitive oscillatory structure deteriorates much more rapidly as frequency
increases. Motivated by this asymmetry, we propose APEX, Amplitude-anchored and
Phase-prior-guided Enhancement from eXtrapolated coarse predictions ... **A lower-frequency
neural operator first provides a coarse prediction in the target-frequency regime, from
which we retain only the amplitude as a transferable structural anchor.** A conditional
flow-matching enhancer then reconstructs the target higher-frequency field under the
guidance of a Green's-function-inspired phase prior."*
Decisive detail for the verdict: APEX's anchor is the **amplitude field of a learned
lower-frequency operator's prediction**, consumed by a **conditional flow-matching
enhancer** — i.e. an architecture with two trained networks, not a scalar statistic used
to (de)normalize a target. The fetched abstract does **not** state a per-sample scalar,
nor an output rescaling. This confirms s5-B2's territory ruling that APEX is **A**
(architecture), and it is therefore *not* an occupant of the `revin_lf` scaler slot.

### Term 1 — clipping as implicit reweighting

Results: "Can gradient clipping mitigate label noise?" (https://openreview.net/pdf?id=rklB76EKPr,
Menon et al.); "Optimized Gradient Clipping for Noisy Label Learning"
(https://arxiv.org/html/2412.08941v4); "Revisiting Gradient Normalization and Clipping for
Nonconvex SGD under Heavy-Tailed Noise" (https://arxiv.org/html/2410.16561); "Robust
Stochastic Optimization via Gradient Quantile Clipping" (https://arxiv.org/pdf/2309.17316);
Google's re-weighted gradient descent
(https://research.google/blog/re-weighted-gradient-descent-via-distributionally-robust-optimization/).

**FETCHED — Optimized Gradient Clipping for Noisy Label Learning
(https://arxiv.org/html/2412.08941v4)**: reports Menon et al.'s result verbatim —
*"a loss function l equipped with gradient clipping is equivalent to a Huberised-like loss
function"* — and gives the induced loss for cross-entropy once gradients exceed the
threshold tau: `l_CE = 1 − tau·p(y|x) + log tau`. On the sample-level effect:
clipping *"bounds the gradient caused by noisy samples, enhancing the robustness of the
loss function against noisy labels"* and *"helps the loss function assign small gradients
to outlier samples (which are likely to be corrupted)"*. **Explicitly absent** (fetch's
own note): *"no explicit formula deriving per-sample weights from clipping thresholds, nor
does it quantify how individual samples' loss contributions are reweighted."*

**DEAD FETCH**: https://openreview.net/pdf?id=rklB76EKPr returned an OpenReview browser
verification page, no content. The Menon result is therefore cited **through**
2412.08941v4, which quotes it — not from memory.

### Term 2 — clip threshold vs loss scale; redundancy with normalization

Results: NFNets / adaptive gradient clipping (https://arxiv.org/pdf/2102.06171); "Robust
and Fast Training via Per-Sample Clipping" (https://arxiv.org/pdf/2605.02701); ZClip
(https://arxiv.org/pdf/2504.02507); "Gradient Shaping Beyond Clipping"
(https://arxiv.org/pdf/2510.01578); Automatic Clipping (https://arxiv.org/pdf/2206.07136);
practitioner pages (emergentmind, apxml, linkedin).

**FETCHED (via ar5iv after the `/pdf/` fetch returned binary) — "Automatic Clipping:
Differentially Private Deep Learning Made Easier and Stronger"
(https://ar5iv.labs.arxiv.org/html/2206.07136)**: the small-threshold limit makes clipping
*exactly* normalization —
`ClipAbadi(g_i;R) = min(R/||g_i||, 1) ≈ R/||g_i|| =: ClipAUTO-V(g_i;R)`; the threshold is
absorbed into the step size — *"We can view eta_effective ≡ eta·R as a whole: increasing R
has the same effect as increasing eta"*; and for adaptive optimizers, R *"cancels out"*,
*"making the clipping threshold redundant across methods like Adam and LAMB."*
Caveat I must carry: this is **per-sample** clipping in the DP-SGD setting, whereas our
`grad_clip = 1.0` is a **whole-batch** norm clip — the redundancy statement transfers as an
argument, not as a theorem about our recipe.

### Term 3 — Adam scale invariance and what breaks it

Results: FAdam (https://arxiv.org/pdf/2405.12807); "Why Adam Works Better with beta1=beta2"
(researchgate); "Scaling Exponents Across Parameterizations and Optimizers"
(https://arxiv.org/pdf/2407.05872); Unit Scaling (https://arxiv.org/pdf/2303.11257);
AdamW/scale-freeness (https://arxiv.org/pdf/2202.00089); Keras Adam docs
(https://keras.io/api/optimizers/adam/); Automatic Clipping again.
The search text asserts Adam's invariance to diagonal gradient rescaling and epsilon as the
breaker, but **FETCH FAILED** on the one primary source I tried
(https://arxiv.org/abs/2303.11257 — abstract page carries none of it), so **I record no
citable claim about Adam scale-invariance**. The B3 card must not cite this line; the
clip-side argument above stands on its own.

## Interpretation

H3's *mechanism* is published and formalizable: clipping is a Huberised loss, i.e. an
implicit down-weighting of the highest-gradient samples (2412.08941v4 quoting Menon), and
the clip threshold is scale-coupled and partly redundant with normalization
(ar5iv 2206.07136). What is unretrieved is any work that **measures clip-rate as the
explanatory variable for a target-normalization result** — which is exactly what B3's
per-batch grad-norm/clip-rate log would do. APEX is confirmed out of the scaler slot.
