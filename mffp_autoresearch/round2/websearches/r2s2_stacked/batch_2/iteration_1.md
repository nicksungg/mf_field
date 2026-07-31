# Iteration 1 — realisation-aware stage 1, conditional-mean diagnosis, coherence eligibility

## Search rationale

B1's mechanism result (part 6, I8) is that a DETERMINISTIC pseudo-LF cannot be an information
channel, and that the corrector's value is a step function of its input's band-1 coherence
(0.99997 at real LF, <= 0.0008 at pseudo-LF; threshold bracketed 0.52 < gamma_b1 < 0.95). Part 7
names two B2 options plus an implicit methodological one. This iteration attacks all three at
the level of "does the field already have this":
(1) has a *sample* from a generative emulator (rather than E[LF|c]) ever been fed into a
downstream deterministic corrector; (2) is "the surrogate collapsed to the conditional mean
because the conditioning variable is incomplete" an established *diagnosis* with named
statistics; (3) is spectral coherence between an intermediate and the target an established
*eligibility precondition* for building a corrector at all — the card's proposed round-level
rule.

## Search terms used

1. `generative emulator sample instead of conditional mean fed into downstream correction network PDE surrogate`
2. `conditional mean collapse blurry prediction diagnosis incomplete conditioning variable neural operator parametric PDE aleatoric`
3. `spectral coherence between surrogate prediction and target as criterion for whether downstream correction is worthwhile`

## Findings

### Term 1 — generative sample → downstream corrector

Search returned the generative-surrogate literature broadly, none of it in the
condition-only (no coarse solve at test) regime:

- "Generative Diffusion for Regional Surrogate Models From Sea-Ice Simulations" (Finn et al.,
  JAMES 2024) — https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2024MS004395
  (snippet-level; not fetched). Diffusion surrogate samples the conditional distribution to
  avoid the "mean-forecast" problem of deterministic surrogates.
- "Resolving Turbulent Magnetohydrodynamics: A Hybrid Operator-Diffusion Framework" —
  https://arxiv.org/pdf/2507.02106 (snippet-level). Snippet describes a score-based diffusion
  model acting as a **corrector conditioned on the low-frequency output of a trained
  operator** — i.e. generative stage DOWNSTREAM of a deterministic operator, the reverse of
  the card's option (A) ordering (generative stage 1 feeding a deterministic stage 2).
- "ENMA: Tokenwise Autoregression for Generative Neural PDE Operators" —
  https://arxiv.org/html/2506.06158v1 (snippet-level).
- "PerFlow: Physics-Embedded Rectified Flow ..." — https://arxiv.org/pdf/2605.03548
  (snippet-level).

Interpretation of the pattern: the published composition is
**deterministic operator → generative corrector**, not **generative emulator → deterministic
corrector**. No result in this turn showed a *sample* from a stochastic coarse-field emulator
being fed to a corrector that was trained on real coarse solves.

### Term 2 — conditional-mean collapse as a diagnosis

- **[VERIFIED, fetched]** "Diagnosing the Conditional-Mean Barrier in Scientific
  Machine-Learning Surrogates" — https://arxiv.org/html/2605.28076. Defines the barrier as: a
  deterministic surrogate trained with squared loss learns E[Y|X] but misses task-relevant
  variability, and residual variability "may reflect either deterministic underfitting or
  conditional variability irreducible relative to the chosen input X" — verbatim the fork
  r2s2/r2s4 face (LEARNING gap vs STRUCTURAL ceiling). Proposes three diagnostics:
  residual-feature orthogonality tests t_n(psi) on probes psi; effect-size e_n(psi) = fraction
  of residual variance removable by correction along psi; and an explained-variance ceiling
  (R^2 cannot exceed the conditional mean's share). Decision rule: barrier reached when effect
  sizes stay below task tolerance and residual mean-square stabilises. Fetched summary states
  the paper does **not** discuss rank collapse, coherence measures, missing latent initial
  conditions, or feeding a conditional-mean prediction into a downstream corrector.
- "Neural Operator Processes for Probabilistic Operator Learning under Partial Observations" —
  https://arxiv.org/pdf/2606.22946 (snippet-level).
- "Diagnosing Failure Modes of Neural Operators Across Diverse PDE Families" —
  https://arxiv.org/pdf/2601.11428 (snippet-level).

### Term 3 — coherence as a corrector-eligibility precondition

- **[VERIFIED, fetched]** "Correcting Neural Operator Spectral Bias via Diffusion Posterior
  Sampling with Sparse Observations" (FreqNO-DPS) — https://arxiv.org/html/2606.03936. Direct
  quotes returned by the fetch: *"the same diagnostic serves as a prerequisite check for
  applying the method to any new surrogate (Appendix B.6)"*; *"This diagonality is a verifiable
  property of the surrogate: we confirm it for the MIFNO via an off-diagonal cross-spectral
  coherence diagnostic."*; residual covariance diagonal in the Fourier basis by
  Wiener-Khinchin under WSS. Crucially for r2s2's D1: the corrector **is trained on real
  high-fidelity SEM solves** and **applied to the frozen surrogate's predicted field** treated
  "as an auxiliary observation", with spectral calibration on "paired ground-truth/MIFNO data
  on a held-out calibration split". (This paper is also [HF-2] in
  `docs/reports/MF_Leaderboard_Beaters_2026_Report.md` line 102 — cited there, verified here.)
- "Beyond Model Ranking: Predictability-Aligned Evaluation for Time Series Forecasting" —
  https://arxiv.org/pdf/2509.23074 (snippet-level): defines "Spectral Coherence Predictability
  (SCP)" as a tractable predictability surrogate — same statistic, different (time-series)
  domain.
- "Surrogate Data Analysis for Assessing the Significance of the Coherence Function" —
  https://www.researchgate.net/publication/8459881 (snippet-level; "surrogate" here means
  surrogate-data hypothesis testing, not surrogate modelling — vocabulary collision).

## Interpretation

The literature owns the deterministic-operator → generative-corrector ordering and it owns
coherence-as-prerequisite for a *specific* corrector's assumptions (FreqNO-DPS checks
off-diagonal coherence to justify a diagonal-in-Fourier residual model), so the card's proposed
"is the input worth filtering" rule has a very close published neighbour that must be
disclosed. The conditional-mean-barrier paper supplies published vocabulary and a decision rule
for exactly the LEARNING-gap-vs-STRUCTURAL-ceiling fork, but by its own account does not cover
rank collapse, coherence, or stacked correctors — leaving that composition open. Nothing yet on
a *stochastic* stage-1 feeding a real-LF-trained corrector.
