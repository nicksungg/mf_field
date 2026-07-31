# Iteration 5 — `r2s4_diag` batch 1 (refutation pass 2 of 2; ITERATION CAP HIT)

**Cap note**: this is iteration 5 of 5 (§3.2 hard cap). No further searching.

## Search rationale

Iteration 4 left two gaps: (i) the D2 refutation depended on a NeurIPS PDF that
failed to fetch, and (ii) D3 had received no dedicated refutation search. Term 1
re-attacks D2 through the arXiv version; term 2 attacks D3 (HF-sample-count
sweeps / learning curves in MF surrogates); term 3 makes a second, differently
worded attempt at D1's floor-panel half (does anyone report a neural operator
losing to a trivial predictor under relative-L2?).

## Search terms used

1. `privileged features distillation learning to rank why and when it works ablation arXiv` (→ D2)
2. `high-fidelity sample size sweep learning curve multi-fidelity neural operator overfitting train test gap diagnostic few high fidelity samples` (→ D3)
3. `relative L2 error benchmark neural operator worse than predicting zero mean field normalization critique` (→ D1 floor half)

## Findings per term

### Term 1 (→ D2)

Top results: arXiv version (https://arxiv.org/abs/2209.08754), NeurIPS
proceedings PDF
(https://proceedings.neurips.cc/paper_files/paper/2022/file/aa31dc84098add7dd2ffdd20646f2043-Paper-Conference.pdf),
Amazon Science copy
(https://assets.amazon.science/01/0e/607b7f7941a4a3d3379247a07db5/toward-understanding-privileged-features-distillation-in-learning-to-rank.pdf),
Calibration-compatible listwise distillation of privileged features for CTR
(https://arxiv.org/pdf/2312.08727), Counterfactual LTR via KD
(https://ceur-ws.org/Vol-3843/paper_10.pdf).

**Fetched — Yang, Sanghavi, Rahmanian, Bakus & Vishwanathan, "Toward
Understanding Privileged Features Distillation in Learning-to-Rank"
(https://arxiv.org/abs/2209.08754)**: teacher trained on all features including
those unavailable at test time instructs a student lacking them; evaluated on
three public datasets and an Amazon-scale ranking problem. Design is "empirical
ablation studies and theoretical analysis for linear models" to investigate when
PFD performs well, and **"explicitly includes a no-distillation baseline (the
student model without privileged information guidance), enabling direct
comparison of distillation's impact"**. Baselines: no-distillation,
pretraining–finetuning, self-distillation, generalized distillation. Headline
mechanism result, quoted from the fetch: "as the predictive power of a privileged
feature increases, the performance of the resulting student model initially
increases but then decreases" — because a highly predictive privileged teacher
produces high-variance predictions, hence high-variance student estimates and
worse test performance. **This is a matched with/without-privileged-information
arm design, published in 2022.**

### Term 2 (→ D3)

Top results: Multifidelity deep neural operators (Lu, Pestourie, Johnson,
Romano; https://arxiv.org/abs/2204.06684 ; journal:
https://link.aps.org/doi/10.1103/PhysRevResearch.4.023210), MF Bayesian neural
operator for spinodal metamaterials (https://arxiv.org/pdf/2602.13257),
gradient-enhanced multifidelity neural networks
(https://arxiv.org/pdf/2103.12247), MF prediction of flow/temperature via
transfer learning with FNO (https://arxiv.org/pdf/2304.06972), pretrain–finetune
neural operator for MF structural dynamics
(https://www.sciencedirect.com/science/article/abs/pii/S0141029625016098),
transfer learning for MF simulation-based inference in cosmology
(https://arxiv.org/pdf/2505.21215).

**Fetched — MF-DeepONet (https://arxiv.org/abs/2204.06684)**: architecture is
two DeepONets coupled by residual learning and input augmentation; claims it
"significantly reduces the required amount of high-fidelity data and achieves one
order of magnitude smaller error when using the same amount of high-fidelity
data." The fetch **could not confirm** an explicit N_hf sweep with learning
curves, nor a matched-architecture HF-only control arm — abstract only. Recorded
as unconfirmed; do not cite as a preemption of the N_hf-sweep design.
Search-snippet level (not fetched, so not citable): a sparse-HF case with 20
samples where the MF model beat the HF-only model, and gradient-enhanced MF NNs
needing 10–12 HF samples for a global accuracy target.

### Term 3 (→ D1 floor half)

Top results across three sub-queries: Performance of Neural and Polynomial
Operator Surrogates (https://arxiv.org/abs/2604.00689), QuadNorm: resolution-
robust normalization for neural operators (https://arxiv.org/html/2605.07375),
zero-shot weather downscaling effectiveness of neural operators
(https://arxiv.org/html/2409.13955v2), comprehensive PINN benchmark
(https://proceedings.neurips.cc/paper_files/paper/2024/file/8c63299fb2820ef41cb05e2ff11836f5-Paper-Datasets_and_Benchmarks_Track.pdf),
neural operator comparative review
(https://www.researchgate.net/publication/392477236). **No result reports a
neural operator losing to a zero/mean predictor under relative L2** — the
critique literature is about weak *numerical/classical* baselines and about
normalization not being resolution-invariant, not about trivial predictors.

**Fetched — Westermann, Huber, O'Leary-Roseberry & Zech, "Performance of Neural
and Polynomial Operator Surrogates" (https://arxiv.org/abs/2604.00689)**:
compares reduced-basis neural operators and FNOs against reduced-basis
sparse-grid and tensor-train polynomial surrogates. Finding: "polynomial
surrogates achieve substantially better data efficiency for smooth input fields",
with sparse-grid convergence matching theory; only for rough inputs does "the
Fourier neural operator display the fastest convergence rates"; derivative-informed
training is "a competitive alternative for rough inputs in the low-data regime".
Conclusion: match methodology to problem regularity rather than assuming neural
methods win. This is the strongest published instance of *simple beats neural in
the low-data regime* I found — but the simple method is a polynomial surrogate,
still a trained/fitted model, not a training-free floor.

---

# PRIOR-ART VERDICT (r2s4_diag, batch 1)

## D1a — Certify a minimum-claimable-effect from a 3-seed condition→HF spread

**Verdict: `preempted (cite)`.**
The general methodology is published and better developed than what §12.4
sketches: Agarwal et al., *Deep Reinforcement Learning at the Edge of the
Statistical Precipice* (https://ar5iv.labs.arxiv.org/html/2108.13264 —
iteration 4) targets exactly the "3–10 runs per task" regime and prescribes
stratified bootstrap CIs, interquartile mean, performance profiles, optimality
gap and probability of improvement instead of point estimates; Du, *When +1% Is
Not Enough* (https://arxiv.org/abs/2511.19794 — iteration 4) prescribes paired
multi-seed runs + BCa bootstrap CIs + a sign-flip permutation test on per-seed
deltas, and reports that **with three seeds the conservative paired protocol
"never declares significance"** for 0.6–2.0-point effects that single runs and
unpaired t-tests call significant.
*What remains open*: nothing methodological. What is open is the **empirical
constant** — nobody has measured the seed spread of a condition→HF surrogate on
THIS panel under copy-LF skill units. B1 should present itself as measuring a
number using an off-the-shelf protocol, and should adopt paired per-seed deltas
(matching round 2's own drift-class rule) rather than a bare max-min spread.

## D1b — Training-free floor panel (NN-in-condition / train-mean / zero) as mandatory reported arms

**Verdict: `preempted-but-MF-composition-open (cite)`.**
Preempted parts: the "you must beat a strong baseline" norm is quantified —
McGreivy & Hakim, *Weak baselines and reporting biases…*
(https://arxiv.org/abs/2407.07218 ; Nature MI
https://www.nature.com/articles/s42256-024-00897-5 — iteration 1): "79% (60/76)
compare to a weak baseline". The interpolation-vs-physics diagnostic is stated in
almost our terms by *Predictivity and Utility of Neural Surrogates of Multiscale
PDEs* (https://arxiv.org/html/2604.20061v1 — iteration 1): "The key diagnostic is
whether classical reduced-order methods with comparable offline cost achieve
similar accuracy; if so, the benchmark tests interpolation, not the capacity to
handle multiscale physics." Simple-beats-neural in the low-data regime is
documented by Westermann et al. (https://arxiv.org/abs/2604.00689 — this
iteration), and the empirical mean predictor is already used as an algorithmic
floor by Operator Boosting (https://arxiv.org/abs/2606.17460 — iteration 1).
*What remains open*: two dedicated refutation searches (iteration 4 term 2, this
iteration term 3) found **no source that reports a training-free trivial-predictor
panel — nearest-neighbour-in-parameter + train-mean + zero — as mandatory columns
beside every model**, and none that expresses such floors in **copy-LF skill
units** for a no-solver-at-test regime. The published floors are all *fitted*
(ROM, polynomial, GP, kriging). The composition that is open is precisely round
2's: training-free floors + a real-coarse-solve reference, reported together.

## D2 — Value-of-LF accounting via matched ± LF-training-signal arms

**Verdict: `preempted-but-MF-composition-open (cite)`.**
Preempted: the design is textbook LUPI. Yang et al., *Toward Understanding
Privileged Features Distillation in Learning-to-Rank*
(https://arxiv.org/abs/2209.08754 — this iteration) runs exactly the matched
with/without-privileged-information contrast (no-distillation, pretrain–finetune,
self-distillation, generalized distillation arms) plus theory, and reports the
**non-monotone law**: student performance rises then FALLS as the privileged
feature becomes more predictive, because a highly predictive teacher yields
high-variance predictions. The LUPI vocabulary itself is established
(https://pmc.ncbi.nlm.nih.gov/articles/PMC8596492/ — iteration 2). Negative
transfer when fidelity correlation is weak is a named MF phenomenon (iteration 2,
term 3).
*What remains open*: (a) three independently fetched MF/LUPI sources state there
is **no standard matched-arm protocol for isolating the marginal value** of the
privileged/LF signal (MAGPI "lacks explicit ablation studies quantifying
low-fidelity contributions in isolation", https://arxiv.org/html/2603.22050;
the LUPI multi-task paper's related work has none,
https://pmc.ncbi.nlm.nih.gov/articles/PMC8596492/); (b) nobody has instantiated
LUPI with **coarse-grid PDE solution fields as the privileged information for a
field-valued output**, scored in copy-LF skill units; (c) round 2 has a
domain-specific reason the value may be ZERO that the LUPI literature does not
consider — the **nested-ladder degeneracy** (program.md §12.3 / r1 report §6),
where an aligned/nested LF rung is a spectral truncation of the HF rung and
therefore adds no information the HF rung lacks. Yang et al.'s non-monotone law
is a concrete, citable *prediction* to test: on our panel the LF field is a very
predictive privileged feature, so the LUPI prior is that distillation may HURT.

## D3 — Overfitting anatomy at N_hf ∈ {5, 20, 50} / N = 400 (gap decomposition + n_eff)

**Verdict: `preempted-but-MF-composition-open (cite)` — low confidence, one
dedicated search.**
Preempted: HF-sample-count sweeps and HF-only control arms are routine in MF
surrogate work — MAGPI studies 10/16/45 HF samples
(https://arxiv.org/html/2603.22050 — iteration 2) with single-fidelity kriging as
the without-LF arm, and MF-DeepONet (https://arxiv.org/abs/2204.06684 — this
iteration) claims "one order of magnitude smaller error when using the same
amount of high-fidelity data" (its N_hf sweep could NOT be confirmed from the
abstract). Data-scaling power laws for operator learning exist as a comparison
frame (https://arxiv.org/abs/2203.13181 ; https://arxiv.org/pdf/2410.00357 —
iteration 3; the specific rates were NOT verifiable from the fetched abstracts
and must not be quoted).
*What remains open*: iteration 3 found **no published train/test gap
decomposition protocol for neural operators** and **no domain-specific effective-
sample-size estimator** (term 3 returned only applied-domain saturating learning
curves and MCMC-style ESS). The drift-class rule's n_eff/N < 1% criterion has no
found precedent in operator learning. Confidence is low — this direction received
one dedicated refutation search; if B2/B3 leans on it, re-search before claiming.
