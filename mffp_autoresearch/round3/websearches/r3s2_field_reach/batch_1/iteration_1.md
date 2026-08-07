# Iteration 1 — r3s2_field_reach, batch 1

## Search rationale

The round-3-specific object is the "internal option C" the program puts in scope: the condition vector now *completely* determines the HF field via band-limited IC coefficients (ADR r3-0001 D1), so a model may reconstruct the IC field from those coefficients internally and then map it to the readout-time field.
Open question 1 in `summary_so_far.md` asks whether that composition is published.
Terms 1–2 attack it directly (coefficients→field→operator); term 3 attacks the general framing question — is "condition on a finite-dimensional parameterization of the input function" already the standard alternative to "consume the input function"?

## Search terms used

1. `neural operator mapping truncated Fourier coefficients of initial condition to solution field parametric PDE surrogate`
2. `reconstruct initial condition field inside surrogate from finite parameter vector then apply neural operator rollout`
3. `operator learning finite-dimensional parameterization of input function versus function-space input generalization PDE`

## Findings

### Term 1 — coefficients → solution field
Top results were generic neural-operator material, not the specific composition:
- Walsh-Hadamard Neural Operators, https://arxiv.org/html/2511.07347v2 — spectral-basis substitution (Walsh–Hadamard for Fourier), operates on truncated spectral coefficients of the *input field*, not on an exogenous parameter vector.
- BENO: Boundary-embedded Neural Operators, https://arxiv.org/pdf/2401.09323 — embeds boundary data, still consumes fields.
- Model-Parallel FNOs for large-scale parametric PDEs, https://arxiv.org/pdf/2204.01205 — scale, not parameterization.
No result mapped an exogenous truncated-coefficient IC parameterization to a field and then through an operator. **No usable direct hit.**

### Term 2 — reconstruct-IC-then-rollout
- Hybrid Adaptive FNO with U-Net backbone for phase-field simulations, https://arxiv.org/pdf/2406.17119 — phase-field (relevant domain: our pfc/ac/ch panel) but takes the *current field state* and rolls forward; no IC reconstruction from parameters.
- Model-Agnostic Knowledge Guided Correction for Improved Neural Surrogate Rollout, https://arxiv.org/pdf/2503.10048 — rollout correction, field-in.
- Plasma-edge neural operator surrogates, https://iopscience.iop.org/article/10.1088/1741-4326/adfdfb — data-efficiency study, field-in.
**No usable results** for the exact "parameters → reconstructed IC field → operator" topology.

### Term 3 — finite-dimensional parameterization as an operator-learning input mode (the framing question)
- **[FETCHED]** Kovachki/Serrano et al. (eds.), "Principled approaches for extending neural architectures to function spaces for operator learning", *Nature Machine Intelligence* (2026), https://www.nature.com/articles/s42256-026-01267-z. Verbatim from the fetched page: *"Neural operators can be viewed as conditional neural fields, where the conditioning variable is the input function."* and, immediately after, *"Alternatively, one can condition the implicit neural representations on the parameters of a finite-dimensional parametrization of the space of input functions"* (with two citations attached).
  → Conditioning a decoder on the *parameters* of the input function rather than on the input function itself is stated in a 2026 review as an established alternative, not a new idea. This directly bears on any r3s2 proposal framed as "FiLM/INR decoder conditioned on the IC coefficients".
- **[FETCHED]** Zhang, Liu, Liao & Lin, "Coefficient-to-Basis Network (C2BNet): A Fine-Tunable Operator Learning Framework for Inverse Problems with Adaptive Discretizations and Theoretical Guarantees", https://arxiv.org/abs/2503.08642. Fetched abstract: C2BNet is *"a novel framework for solving inverse problems within the operator learning paradigm"* that *"efficiently adapts to different discretizations through fine-tuning, using a pre-trained model"*. The name matches the coefficient→basis-expansion shape, but the fetched abstract frames it as an inverse-problem / discretization-adaptation method, and the fetch did not confirm an internal reconstruct-then-evolve topology. Nearest neighbour, not a hit.
- Basis-to-Basis Operator Learning Using Function Encoders, https://arxiv.org/pdf/2410.00171 (snippet-level only) — coefficient-space maps between learned bases; another nearest neighbour worth a targeted refutation search later.

## Interpretation

The general mechanism — "condition a field decoder on a finite-dimensional parameterization of the input function instead of on the input function" — is explicitly named as standard practice in a 2026 Nature MI review, so any r3s2 proposal whose novelty rests on *conditioning on IC coefficients* is preempted at the mechanism level.
What three terms did NOT surface is the specific two-stage internal topology (parameters → exactly reconstructed IC field → operator to readout time) and, more importantly, any measurement of whether that internal lift buys anything over direct parameter conditioning.
Next iteration should hunt (a) the reconstruct-then-evolve topology under its likely alternative names, and (b) whether anyone has measured the "structured intermediate vs direct conditioning" contrast — that contrast, not the architecture, is where r3s2's claim would have to live.
