# Iteration 4 — r3s2_field_reach, batch 1

## Search rationale

Refutation pass. Three candidate directions have crystallised (see `report.md` §Prior-art verdict): **D1** internal IC reconstruction from the now-complete condition vector; **D2** completeness-conditioned re-test of the stacked pseudo-LF stack; **D3** a certified negative (a reachability audit that the field-level residual is unreachable from the condition).
Each term below is written to REFUTE novelty — "has someone already done this?" — not to find inspiration.

## Search terms used

1. `ablation giving surrogate exact initial condition coefficients instead of initial condition field equivalent performance operator learning study` (attacks D1)
2. `incomplete parameterization aleatoric ceiling conditional mean regression unresolved random initial condition PDE benchmark completing the parameter vector` (attacks D3, and the round-3 premise that completeness removes the round-2 aleatoric excuse)
3. `negative result neural operator does not beat trivial baseline benchmark null result publication PDE surrogate 2025 2026` (attacks D3's publication framing)

## Findings

### Term 1 — coefficients-vs-field ablation (D1): NOT refuted, one strong nearest neighbour
The engine's own summary: *"I did not find a specific study directly addressing the exact comparison of 'ablation giving surrogate exact initial condition coefficients instead of initial condition field'."*
- **[FETCHED]** Ceccanti, Galanti, Roghair & van Sint Annaland, "Deep Operator Networks for Surrogate Modeling of Cyclic Adsorption Processes with Varying Initial Conditions", https://arxiv.org/abs/2601.09491. Verbatim: *"the solution of a partial differential equation can be interpreted as an operator mapping an initial condition to its corresponding solution field"*; they build *"a mixed training dataset composed of heterogeneous initial conditions"* and test *"on initial conditions outside the parameter ranges used during training, as well as on completely unseen functional forms."*
  → The nearest neighbour to D1: IC-parameterization generalization is studied, but the branch net still **ingests the IC function** (sensor values); nobody in these results synthesizes the IC from stored coefficients inside the model.
- Operator Learning: A Statistical Perspective (Subedi & Tewari), https://www.ambujtewari.com/research/subedi26operator.pdf (snippet-level) and Generalization Error Bounds for Picard-Type Operator Learning, https://arxiv.org/pdf/2605.10277 (snippet-level) — theory on operator-learning sample complexity; noted for D3's bound-flavoured framing.
- Operator Boosting Produces Pareto-Efficient PDE Surrogates, https://arxiv.org/html/2606.17460v2 (snippet-level here) — relevant to D2 negatively: it documents *"tradeoff cases in two-dimensional reaction-diffusion, active matter, and MHD, where boosted stacks … do not match the lowest full-size baseline error"*, i.e. residual/stacked correction is already known to fail when *"the full-size baseline already captures the dominant dynamics"*.

### Term 2 — the aleatoric-ceiling / completeness axis (D3): REFUTES the naive version
- **[FETCHED]** Junfeng Chen, "Diagnosing the conditional-mean barrier in scientific machine-learning surrogates", https://arxiv.org/abs/2605.28076 (HTML https://arxiv.org/html/2605.28076). Verbatim: *"we formulate this limitation as the conditional-mean barrier and develop a diagnostic framework for identifying it in fitted scientific machine-learning surrogates. The framework combines residual-feature orthogonality and effect-size diagnostics to distinguish deterministic underfitting from irreducible conditional variability."* And, critically for anyone tempted to escape the barrier by sampling: *"stochastic outputs do not by themselves overcome the barrier, because the objective penalizes model variance and drives the predictor back to the conditional mean."*
  → The *diagnostic* that separates "the model underfits" from "the parameterization makes it irreducible" is **published**. The search summary further quotes the framing that the explained-variance ceiling *"reveals an aleatoric floor representing conditional variability that remains irreducible with respect to the chosen parameterization"* — parameterization-relative, exactly the axis round 3 moved along by completing the condition vector.
- Neural Operator Processes for Probabilistic Operator Learning under Partial Observations, https://arxiv.org/pdf/2606.22946 (snippet); Randomized neural operator with conformal UQ, https://arxiv.org/html/2606.29440v1 (snippet) — the partial-observation side of the same axis.

### Term 3 — publishing a negative (D3 framing): thin, and thin in a specific way
The engine's own summary: *"the results don't show a specific prominent publication explicitly framed as a 'negative result' where neural operators fail to beat trivial baselines across the board."*
Nearest neighbours (snippet-level, none fetched): Diagnosing Failure Modes of Neural Operators Across Diverse PDE Families, https://arxiv.org/html/2601.11428v6 (per-PDE-family failure taxonomy — failure modes, not certified impossibility); Data-Efficient Time-Dependent PDE Surrogates: GNS vs Neural Operators, https://arxiv.org/html/2509.06154v1; PDEBench, https://papers.neurips.cc/paper_files/paper/2022/file/0a9747136d411fb83f0cf81820d44afb-Paper-Datasets_and_Benchmarks.pdf.

## Interpretation

D3's *diagnostic machinery* is preempted by 2605.28076 — r3s2 must not claim "we invented a way to tell underfitting from an irreducible floor". But 2605.28076 measures a floor *at a fixed parameterization*; round 3 changed the parameterization to a certified-complete one, which flips the expected reading (aleatoric floor ≈ 0 by construction, so any surviving residual gap is estimation/optimization, not aleatoric). That contrast — the SAME dataset family measured under an incomplete and then a certified-complete condition vector — is what no fetched source has.
D1 survives three refutation attempts at the level of the exact composition, but its mechanism (condition a decoder on parameters of the input function) is preempted by the Nature MI review (iteration 1) and its latent form by DLDMF (iteration 2).
One iteration remains; I will spend it on the one direction still unattacked head-on — whether anybody has re-tested a stacked emulator pipeline *after* fixing an input-completeness defect — plus a last attempt at D1's exact composition under a different name.
