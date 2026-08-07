# iteration_5 — `r3s1_factorised`, batch 1 (FINAL — cap reached; verdict recorded)

**Iteration cap note:** k = 5 of 5. This is the last iteration permitted by
`subagents/websearcher.md` §3.2; no further searching happens for this
stream-batch.

## Search rationale

Closing triplet, each aimed at refuting one surviving residue:
(i) D2 — does a published **pre-fit predictor of whether joint / cross-target
modelling helps** exist (the MTL negative-transfer and task-grouping literature
is the most dangerous preemption, and no earlier turn had touched it);
(ii) D1 regime framing — is "predict the HF field from IC spectral coefficients +
parameters, with no coarse solve at inference" itself a distinguishing feature
(it is not — round 2 already declared it preempted, re-confirmed here);
(iii) D1 composition — one last direct attempt at "stacked POD coefficients vs
independent per-mode regression under high-dimensional parameters".

## Search terms used

1. `when is multi-task learning beneficial predict negative transfer before training task affinity diagnostic`
2. `predict PDE solution field from initial condition spectral coefficients parameter vector no coarse solve at inference operator surrogate`
3. `stacking POD coefficients cross-mode dependence surrogate parametric PDE outperforms independent per-mode regression high dimensional parameters`

## Findings

### Term 1 — nearest preemption of D2 (FETCHED)

**FETCHED**: Ayman, Mukhopadhyay & Laszka, *"Task Grouping for Automated
Multi-Task Machine Learning via Task Affinity Prediction"*,
<https://arxiv.org/abs/2310.16241> (retrieved 2026-08-07). Verbatim:
> *"the advantage of MTL depends on various factors, such as the **similarity of
> the tasks, the sizes of the datasets**, and so on; in fact, some tasks might not
> benefit from MTL and may even incur a loss of accuracy compared to STL. Hence,
> the question arises: which tasks should be learned together? … We identify
> **inherent task features and STL characteristics that can help us to predict
> whether a group of tasks should be learned together using MTL or if they should
> be learned independently using STL**."*

So "predict, before training, whether sharing across targets pays, from cheap
per-target characteristics" **is published** — as MTL task grouping. Related
returns (not fetched): negative-transfer identification via surrogate models
<https://openreview.net/forum?id=KgfFAI9f3E> (fetch returned no usable text —
JS-rendered; **NOT citable**); higher-order task affinities on graphs
<https://arxiv.org/pdf/2306.14009>. Aggregated search return also records the
honest limit: *"Transfer affinity does not necessarily predict whether tasks
should be learned jointly in a multi-task setting, as multi-task compatibility
depends strongly on factors such as model capacity, dataset size, and
optimization interactions."*

### Term 2 — the regime is not a distinguishing feature

Returns: parameter-conditioned interpretable U-Net surrogate
<https://arxiv.org/html/2601.22654v1> (**already cited as preempting FiLM/
condition-conditioned decoders in `round2/websearches/r2s1_direct/batch_1`**);
operator boosting for PDE surrogates <https://arxiv.org/html/2606.17460>;
PDEformer-2 <https://arxiv.org/pdf/2507.15409>; ML-based spectral methods
<https://pmc.ncbi.nlm.nih.gov/articles/PMC9889394/>; VAE-DNN parametric surrogate
<https://arxiv.org/pdf/2508.03839>. Aggregated search return confirms the
standard shape verbatim: *"a reduced-order model approximates the PDE solution by
first calculating the initial modal coefficients corresponding to the initial
condition"*, and *"FiLM implements sample- and channel-wise affine modulation
driven by the coefficient vector"*. **Conclusion unchanged from round 2**:
condition/IC-coefficient → field with no solve at inference is thoroughly
preempted and is a *baseline*, never a contribution.

### Term 3 — D1 composition survives a third refutation attempt

Returns: parametric-surrogate review
<https://link.springer.com/article/10.1007/s11831-026-10552-4>; parameter-dependent
ROM review <https://pmc.ncbi.nlm.nih.gov/articles/PMC5415687/>; POD-GP adaptive
sampling <https://www.sciencedirect.com/science/article/abs/pii/S0142727X1931210X>;
Galerkin-NN-POD <https://arxiv.org/pdf/2406.13567>; MF-ROM (RSPA) again
<https://royalsocietypublishing.org/rspa/article/480/2283/20230655/101080/Multi-fidelity-reduced-order-surrogate>.
Aggregated search return, verbatim and decisive: *"the search results … **don't
contain specific research directly addressing 'stacking POD coefficients' with
cross-mode dependence compared to independent per-mode regression** in
high-dimensional parameter spaces"*, alongside the standard prior that
*"POD provides an orthogonal basis where each modal coefficient corresponds to a
distinct basis direction. **Modeling them independently avoids introducing
artificial correlations** and yields a more efficient and scalable surrogate."*

That stated prior is a **linear-decorrelation** argument and is exactly what the
recorded r2s1-B3 measurement contradicts (discarded coefficients predictable from
the retained ones at OOF R² 0.92–0.94 on `sharp__cahn_hilliard`, B3 finding
T3-F24), so the composition is not merely unsearched — it is contrary to the
field's stated default.

---

## PRIOR-ART VERDICT

### D1 — propagation-aware two-stage cross-coefficient closed-form head as the scored condition→HF arm

**Verdict: `preempted-but-MF-composition-open (cite)`**

*Preempted mechanism, with fetched citations, which the card MUST name:*
- Spyromitros-Xioufis, Tsoumakas, Groves & Vlahavas, *Multi-Target Regression via
  Input Space Expansion: Treating Targets as Inputs*, arXiv:1211.6581 (Mach.
  Learn. 2016) — <https://arxiv.org/abs/1211.6581> (iteration_3). This owns BOTH
  halves: *"building a separate model for each target on an expanded input space
  where other targets are treated as additional input variables"* = the
  cross-coefficient stage (**Stacked Single-Target / Ensemble of Regressor
  Chains**); and *"a discrepancy of the values of the additional input variables
  between training and prediction … extensions that use out-of-sample estimates
  of the target variables during training"* = **the propagation-aware gate**. The
  card must state that F25's true-input-vs-OOF-input result is a rediscovery of
  this named discrepancy, not a finding.
- mlxtend `StackingCVRegressor` — <https://rasbt.github.io/mlxtend/user_guide/regressor/StackingCVRegressor/>
  (iteration_1): out-of-fold level-1 predictions as level-2 inputs, with the
  overfitting rationale stated verbatim. The gate is textbook stacked
  generalization.
- Callaham, Brunton & Loiseau, *On the role of nonlinear correlations in
  reduced-order modelling*, JFM — <https://www.cambridge.org/core/journals/journal-of-fluid-mechanics/article/on-the-role-of-nonlinear-correlations-in-reducedorder-modelling/CC2980F9AA4AC20A7453C3056ED950C4>
  (iteration_1): *"a minimal set of driving modes and a manifold equation for the
  remaining modes"*, coefficients *"directly expressed as algebraic functions of
  … driving modes"* — coefficient-on-coefficient completion, published, for
  **temporal** POD coefficients on an attractor, fitted on TRUE driving
  coefficients.

*What remains open (the only claimable residue):* the **composition** —
corrected (out-of-fold) target-as-input stacking applied to the **reduced-basis
coefficients of a parametric PDE field**, where stage-1 targets are themselves
regressed from a design/condition vector, scored on a copy-LF-skill panel in the
**no-LF-at-test** regime with N_hf as low as 5. Three independent refutation
searches (iterations 4 term 1, 5 term 3, plus iteration 2 term 1) returned **no**
source doing this; the field's stated default is the opposite ("model POD modal
coefficients independently … avoids introducing artificial correlations"), and
that default rests on **linear** decorrelation, which licenses nothing about the
nonlinear dependence B3-F24 measured. Nearest neighbours: arXiv:1211.6581 (same
estimator, tabular targets); the JFM manifold paper (same completion, temporal
not parametric); arXiv:2607.06832 (joint-vs-separate multi-output GPs, but
heterotopic design geometry, not a cascade on predicted targets);
arXiv:2402.17061 (MF ROM for high-dimensional inputs, but input-side ASM/PCAS
reduction, no output-coefficient cascade).

### D2 — condition-dimension discriminator (per-direction OOF R² from condition vs from SET coefficients, across cond_dim 3/5/18/19/19/50) as a training-free pre-fit predictor of whether the two-stage arm pays

**Verdict: `preempted-but-MF-composition-open (cite)`**

*Preempted:* "predict before training whether sharing across targets pays, from
cheap per-target characteristics" is published as MTL **task grouping / negative
transfer prediction** — Ayman, Mukhopadhyay & Laszka, arXiv:2310.16241
(iteration_5, fetched): *"We identify inherent task features and STL
characteristics that can help us to predict whether a group of tasks should be
learned together using MTL or if they should be learned independently using
STL."* And Chen, Fan & Wang, arXiv:2607.06832 (iteration_2, fetched) already
supplies *"model-free diagnostics that can be computed before fitting"* plus *"a
first-order net benefit criterion for deciding when joint modelling is
worthwhile"* for multi-output kriging. The card may not claim "a pre-fit
diagnostic for whether to share across outputs" as an idea.

*What remains open:* the specific **independent variable and estimator**. Both
published criteria are keyed on task/design geometry (task affinity; directed
coverage / borrowing potential under heterotopic designs). Neither is keyed on
**condition (parameter) dimension against fit-row count**, neither predicts the
payoff of a **cascade fed by predicted stage-1 coefficients**, and neither is
instantiated on PDE reduced-basis coefficients. M15's testable prediction — at
cond_dim ≳ 10 the per-direction condition→coefficient map starves while a
coefficient→coefficient stage recovers the gap, and at cond_dim ≤ 3 neither moves
— is unrefuted, and round 3's panel takes it from n = 1 cell to n = 4 high-cond_dim
cells (pfc 18, allen_cahn 19, cahn_hilliard 19, fisher_kpp 50) against n = 2 low
(ifc_heat 3, ifc_poisson 5). **This is the strongest novelty position available
to this batch, and it is a diagnostic/discriminator claim, not an architecture
claim.**

### D3 — fitted closed-form floor battery (`affine_on_hf_train` + nn_condition + train_mean + zero) as the mandatory arm every learned condition→HF claim must clear

**Verdict: `preempted (cite)` at the level of the individual baselines; open only as a reporting protocol**

*Preempted:* train-mean (`PREDICTAVERAGE`) and nearest-neighbour baselines are
standard general-ML practice (ALMANACS, <https://arxiv.org/pdf/2312.12747>;
teaching material <https://bait509-ubc.github.io/BAIT509/lectures/lecture3.html>,
both iteration_4 search returns), and closed-form least-squares readouts over a
PCA latent are an existing architecture class (PCA-RaNN,
<https://arxiv.org/html/2606.29440v1>, cited already in round 2 batch 2).
McGreivy & Hakim's weak-baseline critique (<https://arxiv.org/abs/2407.07218>,
round-2 citation) owns the "your baseline is too weak" argument.

*What remains open:* two searches (iteration_4 term 3, iteration_3 term 3)
returned explicitly that the literature *"do[es] not contain … requirements for
reporting results on scarce high-fidelity samples, or detailed benchmarking
standards for operator learning specifically"* and *"[does not] explicitly detail
a requirement that methods must beat a linear regression or affine baseline in
few-sample settings"*. So the residue is a **reporting protocol**, not a
mechanism: a mandatory fitted-affine floor reported with its **oracle-affine
residual** (ifc_poisson 5.4e-16 — the map is exactly affine) so a reader can tell
"beat linearity" from "learned nothing". Ship as an instrument/bug-fix, never as
a contribution.
