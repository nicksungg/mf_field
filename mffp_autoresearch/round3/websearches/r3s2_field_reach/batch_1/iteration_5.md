# Iteration 5 — r3s2_field_reach, batch 1 (ITERATION CAP REACHED: k = 5 of 5)

## Search rationale

Last iteration. Two remaining refutation angles plus the mandatory §3.3 verdict work.
Term 1 attacks D2's only surviving open content — has anyone re-run a stacked pipeline *after* repairing an input-completeness defect in the benchmark itself?
Term 2 makes a final attempt on D1 under the phrasing a paper would actually use if the IC were synthesized analytically inside the model.
Term 3 attacks the plainest form of what the brainstormer is most likely to write down first — a FiLM-conditioned FNO/spectral decoder driven by a parameter vector with no input field.

## Search terms used

1. `benchmark defect fixed re-evaluate prior negative results informative input features added dataset regenerated surrogate re-test scientific machine learning`
2. `analytic synthesis of input function from stored coefficients as inductive bias neural operator "known parameterization" exact reconstruction layer`
3. `FiLM conditioned FNO decoder from parameter vector no input field spectral decoder few samples parametric PDE 2026`

## Findings

### Term 1 — re-testing after a benchmark repair
**No usable results.** The retrieval collapsed onto software-defect prediction (ReDef, https://arxiv.org/html/2509.09192) and benchmark-construction tooling (BenchMake, https://arxiv.org/html/2506.23419; PDEBench, https://papers.neurips.cc/paper_files/paper/2022/file/0a9747136d411fb83f0cf81820d44afb-Paper-Datasets_and_Benchmarks.pdf).
Nothing found re-evaluates a previously-negative surrogate result after adding the missing input information to the dataset. This is a genuine gap, but it is a gap in *benchmark practice*, not a mechanism — it can support a methodological contribution, never an architecture claim.

### Term 2 — exact/analytic IC synthesis inside the model
**No usable direct results.** Nearest neighbours, snippet-level only: a mathematical guide to operator learning, https://www.sciencedirect.com/science/article/pii/S1570865924000036 (notes DeepONet *"parameterizes the operator through a learned basis expansion"*); PDEInvBench, https://arxiv.org/pdf/2605.25353; Learning Generalizable Neural Operators for Inverse Problems, https://arxiv.org/pdf/2512.18120; basis-to-basis function-encoder framing (returned again from iteration 1's https://arxiv.org/pdf/2410.00171).
The recurring shape is *learned* basis expansions with learned coefficients — never a **fixed, exact, zero-parameter synthesis of a known band-limited parameterization** used as an internal layer.

### Term 3 — the plain FiLM/parameter-conditioned decoder (HIT — refutes the plainest proposal)
- **[FETCHED]** "Conditioning on PDE Parameters to Generalise Deep Learning Emulation of Stochastic and Chaotic Dynamics", https://arxiv.org/html/2509.09599. Verbatim: *"We present a deep learning emulator for stochastic and chaotic spatio-temporal systems, explicitly conditioned on the parameter values of the underlying partial differential equations (PDEs)"*, using *"adaptive layer normalisation, which enables the network to learn transformations of latent variables that are conditioned on varying parameter values"*, demonstrated on Kuramoto–Sivashinsky and beta-plane turbulence, with a probabilistic variant for UQ.
  → Explicit PDE-parameter conditioning via FiLM/adaLN on chaotic and stochastic systems is published. **Note the limit**: it conditions on parameters *in addition to the current state* — it is an emulator, not a condition-only field predictor.
- **[FETCHED]** "Generalizing PDE Emulation with Equation-Aware Neural Operators", https://arxiv.org/html/2511.09729 (code: https://github.com/google-research/generalized-pde-emulator). Verbatim: *"conditioning a neural model on a vector encoding representing the terms in a PDE and their coefficients"*; *"We condition the network's forward pass not only on the current state of the system but also on a compact vector representation – an equation encoding."*
  → Same limit, stated explicitly: *"not only on the current state"*. Vector-encoding conditioning is standard; **removing the state entirely is what our regime does and what these papers do not**.
- Meta-Learned Basis Adaptation for Parametric Linear PDEs, https://arxiv.org/pdf/2604.09289 (snippet-level) — parameter→basis adaptation, closest to a condition-only decoder among the returns; not fetched.

## Prior-art verdict (§3.3 — mandatory)

**D1 — internal "option C": condition vector → exact analytic synthesis of the band-limited IC field (zero learned parameters) → learned operator/rollout to the readout time.**
Verdict: **`preempted-but-MF-composition-open`**.
Preempting citations, all fetched in this loop: the Nature MI review, https://www.nature.com/articles/s42256-026-01267-z — *"one can condition the implicit neural representations on the parameters of a finite-dimensional parametrization of the space of input functions"* (iteration 1); DLDMF, https://arxiv.org/html/2603.12676 — *"maps PDE parameters through a deterministic feed-forward encoder that directly initializes and conditions a continuous latent state governed by a parameter-conditioned Neural ODE"*, decoded to fields *without test-time optimization* (iteration 2); explicit-vs-implicit conditioning on crystal growth, https://arxiv.org/html/2604.21753 — *"explicit parameter conditioning guarantees the best results"* (iteration 2); 2509.09599 and 2511.09729 above.
What remains open (three refutation terms failed to close it): no fetched source uses a **fixed, exact, zero-parameter reconstruction of a known band-limited IC parameterization** as an internal layer, and — decisively for this stream — **every parameter-conditioned emulator found still consumes a field or state at inference** (2604.21753 a single initial frame; 2601.09491 the IC function through the branch; 2509.09599 and 2511.09729 the current state explicitly). The condition-only, no-field-at-test regime with N_hf ∈ {5, 400}, LF at train only, scored in copy-LF skill units, is not represented in any fetched source.

**D2 — re-test of the stacked condition → pseudo-LF → corrector pipeline now that the condition vector is complete.**
Verdict: **`preempted (cite)`** — as a mechanism; open only as a measurement.
Citations fetched this loop: Demo, Tezzele & Rozza, https://arxiv.org/abs/2302.12682 — cheap reduced-order stage plus *"machine learning residual learning, such that the … error can be learned by a neural network and inferred for new predictions"*; Xu et al., https://arxiv.org/abs/2310.00057 — *"a low-fidelity subnet … and a high-fidelity subnet that learns the nonlinear correlation"*, i.e. the downstream stage consumes a *predicted* LF at inference. Operator Boosting, https://arxiv.org/html/2606.17460v2 (snippet this loop), additionally publishes the expected failure mode: boosted/residual stacks *"do not match the lowest full-size baseline error"* when *"the full-size baseline already captures the dominant dynamics"* — which is precisely round 2's r2s2-B1 result (corrector added 0.0061 units).
What remains open: only whether the completeness repair changes the **attribution** (round 2: 99.98% of stack error was stage-1). That is a measurement of this benchmark, not a mechanism — and it must be proposed as such.

**D3 — certified negative: a field-reachability audit showing that beyond the condition→level law nothing is reachable, now under a certified-complete parameterization.**
Verdict: **`preempted-but-MF-composition-open`**.
Preempting citation, fetched this loop: Junfeng Chen, "Diagnosing the conditional-mean barrier in scientific machine-learning surrogates", https://arxiv.org/abs/2605.28076 — the diagnostic framework *"combines residual-feature orthogonality and effect-size diagnostics to distinguish deterministic underfitting from irreducible conditional variability"*, and *"stochastic outputs do not by themselves overcome the barrier, because the objective penalizes model variance and drives the predictor back to the conditional mean."* r3s2 must NOT claim to have invented underfitting-vs-irreducible attribution.
What remains open: 2605.28076 measures the floor **at a fixed parameterization** ("irreducible with respect to the chosen parameterization"). Round 3 *changed the parameterization* to a completeness-certified one (ADR r3-0001 D1, reconstruction rel-L2 = 0.0), so the aleatoric floor is ≈ 0 by construction and any surviving residual must be attributed to estimation/optimization rather than aleatoric variability. The **paired incomplete→complete contrast on the same dataset family** appears in no fetched source, and iteration 4/5 term-3 searches found no SciML publication framed as a certified negative for a surrogate class against trivial baselines.

## Interpretation

The safest r3s2-B1 claim is a measurement, not an architecture: the mechanisms are all published, and the composition that is genuinely unrepresented is *condition-only field prediction with no field input at test under a certified-complete parameterization*.
Cap note: this is iteration 5 of the 5 permitted; no further searching is available in this batch.
