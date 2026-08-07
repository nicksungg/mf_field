# Websearch Report — Stream `r3s1_factorised`, Batch 1

**Stream**: `r3s1_factorised` (gap) ·
**Batch**: 1 ·
**Total iterations**: 5 ·
**WebSearch calls**: 15 (3 per turn, cap respected) ·
**WebFetch calls**: 11 attempted / 8 yielding usable text ·
**Cap hit**: YES — 5/5 iterations used, noted in `iteration_5.md`.

**Tooling caveat (honest record).** The `WebFetch` tool in this environment is
intercepted by a context-mode plugin that redirects to MCP tools absent from this
subagent's tool list. Per the never-give-up-on-tool-errors rule the loop routed
around it with `curl` + local HTML text extraction
(`/tmp/claude-28156/wf/fetch.py`). Every source below marked FETCHED was actually
retrieved and read in this loop. The box has **no PDF text extractor**
(`pdftotext` absent, `pypdf` absent), so `arxiv.org/pdf/*` and publisher PDFs
extract to 0 chars; all fetched citations therefore use HTML landing pages.
Pages that blocked scripted retrieval (MDPI `computation13020058`, Royal Society
RSPA 20230655, Polimi MOX 83/2024, oa.upm.es survey, OpenReview `KgfFAI9f3E`) are
recorded in the iteration files as **not citable** and are not used in any
verdict.

## Search trace

### Turn 1 — attack the two genuinely-unchecked pieces of the seed direction
Terms chosen because round-2's three r2s1 loops already settled FiLM decoders,
POD-NN heads, per-mode OOF family selection, Bates–Granger blending and
supervised basis ordering; what no loop checked is (a) discarded-on-retained
coefficient completion and (b) the out-of-fold stage-1-prediction gate.
- `gappy POD … regression surrogate` → gappy POD completes a field from **partial
  spatial samples**, not from other modes' predictions — neighbouring, not the
  same mechanism [search-return only, https://kiwi.oden.utexas.edu/research/gappy-proper-orthogonal-decomposition].
- `two-stage regression POD coefficients … remaining modes` → **cross-coefficient
  completion is published** for temporal POD coefficients: *"a minimal set of
  driving modes and a manifold equation for the remaining modes"*
  [cite: https://www.cambridge.org/core/journals/journal-of-fluid-mechanics/article/on-the-role-of-nonlinear-correlations-in-reducedorder-modelling/CC2980F9AA4AC20A7453C3056ED950C4].
- `stacked generalization out-of-fold predictions` → the gate is textbook: *"uses
  out-of-fold predictions to prepare the input data for the level-2 regressor …
  which may lead to overfitting"* [cite: https://rasbt.github.io/mlxtend/user_guide/regressor/StackingCVRegressor/].
→ `iteration_1.md`

### Turn 2 — parametric side + the condition-dimension question (M15)
Chosen because round 3's panel makes M15 testable at n = 4 (cond_dim
18/19/19/50 vs 3/5), which is the stream's cheapest high-value experiment.
- `parametric ROM … Karhunen-Loeve input` → the field's stated default is
  *"Because POD reduced coefficients are decorrelated, independent regression
  models can be designed for each coefficient"* — a **linear**-decorrelation
  argument [search-return only].
- `curse of dimensionality … POD coefficient regression` → the classical worry
  starts at O(10²) input dims, above this panel's 18–50; the published remedy is
  input-side reduction, not output-coefficient cascades
  [cite: https://arxiv.org/html/2402.17061v1].
- `independent per-mode vs joint multi-output` → *"Whether a joint multivariate
  kriging metamodel then predicts better than separate univariate metamodels has
  remained unresolved"*, resolved by pre-fit **design-geometry** diagnostics
  [cite: https://arxiv.org/abs/2607.06832]. `ENOUGH` declared: field context
  sufficient; turns 3–5 to §3.3.
→ `iteration_2.md`

### Turn 3 — §3.3 refutation, ML side (decisive)
- `regressor chains … true versus predicted values` → **D1's mechanism is
  preempted**: Stacked Single-Target / Ensemble of Regressor Chains, plus
  *"extensions that use out-of-sample estimates of the target variables during
  training"* to fix *"a discrepancy of the values of the additional input
  variables between training and prediction"*
  [cite: https://arxiv.org/abs/1211.6581].
- `cascaded surrogate … error propagation` → propagates **uncertainty**, does not
  fit stage 2 on OOF stage-1 point predictions — weaker preemption, recorded not
  relied on.
- `linear baseline … must beat affine` → search returned that no source details a
  requirement to beat a linear/affine baseline in few-sample settings.
→ `iteration_3.md`

### Turn 4 — §3.3 refutation, close the three residues
- `stacked single-target … POD modal coefficients` → **No usable result**
  connecting SST/ERC to modal-coefficient targets; standard practice remains
  *"multiple independent regression models … each associated with one modal
  coefficient"*.
- `when does exploiting target dependence help … diagnostic` → **No usable
  result**: MTR reports average improvement, no dataset-level pre-fit diagnostic
  keyed on input dimension or row count.
- `trivial baselines operator learning benchmark` → search returned explicitly
  that the results *"do not contain specific information about operator learning
  benchmarks, requirements for reporting results on scarce high-fidelity
  samples"*; naive `PREDICTAVERAGE` / `NEARESTNEIGHBOR` are standard general-ML
  baselines [https://arxiv.org/pdf/2312.12747].
→ `iteration_4.md`

### Turn 5 — closing triplet + verdict (cap reached)
- `multi-task learning … predict negative transfer` → **the dangerous preemption
  for D2**: *"We identify inherent task features and STL characteristics that can
  help us to predict whether a group of tasks should be learned together using
  MTL or if they should be learned independently"*
  [cite: https://arxiv.org/abs/2310.16241].
- `predict PDE field from IC spectral coefficients … no coarse solve at inference`
  → regime is thoroughly preempted (FiLM/parameter-conditioned surrogates,
  modal-coefficient ROMs); baseline, never a contribution
  [https://arxiv.org/html/2601.22654v1, already a round-2 citation].
- `stacking POD coefficients cross-mode dependence … high dimensional parameters`
  → third refutation attempt returns **nothing**; the field's default is
  *"Modeling them independently avoids introducing artificial correlations"*.
→ `iteration_5.md` (verdict recorded there in full)

## Prior-art verdict

| Candidate direction | Verdict | Citations (fetched) | What remains open |
|---|---|---|---|
| **D1** — ship the propagation-aware **two-stage cross-coefficient closed-form head** (condition→SET coefficients; remaining coefficients regressed on **out-of-fold stage-1 predictions**) as the scored condition→HF arm on the honest panel | **`preempted-but-MF-composition-open (cite)`** | Spyromitros-Xioufis et al., *Multi-Target Regression via Input Space Expansion* — https://arxiv.org/abs/1211.6581 (**owns both the cascade (SST/ERC) and the OOF-corrected gate**); mlxtend `StackingCVRegressor` — https://rasbt.github.io/mlxtend/user_guide/regressor/StackingCVRegressor/ ; Callaham/Brunton/Loiseau JFM nonlinear correlations — https://www.cambridge.org/core/journals/journal-of-fluid-mechanics/article/on-the-role-of-nonlinear-correlations-in-reducedorder-modelling/CC2980F9AA4AC20A7453C3056ED950C4 | Only the **composition**: OOF-corrected target-as-input stacking on **reduced-basis coefficients of a parametric PDE field**, where stage-1 targets are themselves regressed from the condition vector, scored on a copy-LF-skill panel in the **no-LF-at-test** regime at N_hf down to 5. Three refutation searches returned nothing; the field's stated default ("model modal coefficients independently") is a *linear*-decorrelation argument that B3-F24's OOF R² 0.92–0.94 contradicts. **The card must name SST/ERC and state that F25 rediscovered the published train/predict discrepancy.** |
| **D2** — **condition-dimension discriminator**: per-direction OOF R² from the condition vs from the SET coefficients across all 6 cells (cond_dim 3/5/18/19/19/50) as a **training-free pre-fit predictor** of whether the two-stage arm pays (M15, now n = 4 high-cond_dim cells) | **`preempted-but-MF-composition-open (cite)`** | Ayman/Mukhopadhyay/Laszka, *Task Grouping … via Task Affinity Prediction* — https://arxiv.org/abs/2310.16241 ; Chen/Fan/Wang, *When is multivariate kriging worthwhile?* — https://arxiv.org/abs/2607.06832 | The **idea** of a pre-fit "should we share?" predictor is published. Open: the **independent variable and estimator** — both published criteria key on task affinity / heterotopic design geometry, neither on **condition dimension vs fit-row count**, neither predicts the payoff of a **cascade fed by predicted stage-1 coefficients**, neither is instantiated on PDE reduced-basis coefficients. **Strongest novelty position available to this batch — and it is a diagnostic claim, not an architecture claim.** |
| **D3** — **fitted closed-form floor battery** (`affine_on_hf_train` + nn_condition + train_mean + zero) as the mandatory arm every learned condition→HF claim must clear | **`preempted (cite)`** at the level of the individual baselines | ALMANACS naive `PREDICTAVERAGE` / `NEARESTNEIGHBOR` — https://arxiv.org/pdf/2312.12747 (search return); PCA-RaNN closed-form LS readout — https://arxiv.org/html/2606.29440v1 ; McGreivy & Hakim weak baselines — https://arxiv.org/abs/2407.07218 (round-2 citation) | Only a **reporting protocol**: no returned source requires beating a fitted linear/affine baseline in few-sample PDE-surrogate work, and two searches returned explicitly that operator-learning benchmarks lack scarce-HF reporting standards. Ship the affine floor **with its oracle-affine residual** (ifc_poisson 5.4e-16) as an instrument/bug-fix, never as a contribution. |

## Citations summary

- [Spyromitros-Xioufis et al. 2012/2016] "Multi-Target Regression via Input Space Expansion: Treating Targets as Inputs" — https://arxiv.org/abs/1211.6581 — FETCHED, used in: `iteration_3.md` (term 1), verdict D1
- [mlxtend docs] "StackingCVRegressor: stacking with cross-validation for regression" — https://rasbt.github.io/mlxtend/user_guide/regressor/StackingCVRegressor/ — FETCHED, used in: `iteration_1.md` (term 3), verdict D1
- [Callaham, Brunton & Loiseau] "On the role of nonlinear correlations in reduced-order modelling", J. Fluid Mech. — https://www.cambridge.org/core/journals/journal-of-fluid-mechanics/article/on-the-role-of-nonlinear-correlations-in-reducedorder-modelling/CC2980F9AA4AC20A7453C3056ED950C4 — FETCHED, used in: `iteration_1.md` (term 2), verdict D1
- [Chen, Fan & Wang 2026] "When is multivariate kriging worthwhile? A design-geometry analysis of heterotopic multi-output Gaussian processes" — https://arxiv.org/abs/2607.06832 — FETCHED, used in: `iteration_2.md` (term 3), verdict D2
- [Ayman, Mukhopadhyay & Laszka 2023] "Task Grouping for Automated Multi-Task Machine Learning via Task Affinity Prediction" — https://arxiv.org/abs/2310.16241 — FETCHED, used in: `iteration_5.md` (term 1), verdict D2
- [anon. 2024] "A Multi-Fidelity Methodology for Reduced Order Models with High-Dimensional Inputs" — https://arxiv.org/html/2402.17061v1 — FETCHED, used in: `iteration_2.md` (term 2)
- [Alves et al. 2023] "Nonlinear parametric models of viscoelastic fluid flows" — https://arxiv.org/abs/2308.04405 — FETCHED (abstract), used in: `iteration_1.md` (term 2) — SINDy temporal ROM, weaker match, recorded not relied on
- [ALMANACS] "A Simulatability Benchmark for Language Model Explainability" — https://arxiv.org/pdf/2312.12747 — SEARCH RETURN ONLY, used in: `iteration_4.md` (term 3), verdict D3 (naive-baseline naming only)
- Round-2 citations reused (already fetched in `round2/websearches/r2s1_direct/`): PCA-RaNN https://arxiv.org/html/2606.29440v1 ; McGreivy & Hakim https://arxiv.org/abs/2407.07218 ; parameter-conditioned U-Net https://arxiv.org/html/2601.22654v1 ; REALM https://arxiv.org/html/2512.18595

## Dead ends

- `gappy POD … retained coefficients` → gappy POD reconstructs from **partial
  spatial observations**, not from other modes' predicted coefficients; adjacent
  mechanism, not a preemption. Not fetched.
- `cascaded surrogate models error propagation` → the hits propagate *uncertainty*
  through a cascade; none fits stage 2 on OOF stage-1 point predictions.
- Royal Society RSPA 20230655 / Polimi MOX 83-2024 / MDPI computation13020058 /
  oa.upm.es multi-output survey / OpenReview `KgfFAI9f3E` → all blocked scripted
  retrieval or are PDFs this box cannot extract (no `pdftotext`, no `pypdf`).
  **Not citable**; no verdict rests on them.
- `stacked single-target … POD modal coefficients` and `stacking POD coefficients
  cross-mode dependence …` → both returned **nothing** on the composition; that
  null is itself the D1 residue, recorded twice independently.

## For the brainstormer

The brainstormer MUST quote the prior-art verdict for whatever it proposes.

1. **Do not propose the two-stage head as a novel architecture.** D1 is
   `preempted-but-MF-composition-open` — the card must name **Stacked
   Single-Target / Ensemble of Regressor Chains** (arXiv:1211.6581) and state
   explicitly that r2s1-B3's F25 result (true-input gate 18.7500→19.9704 vs
   OOF-input gate →18.6787) is a **rediscovery** of that paper's named
   train/predict discrepancy, not a finding. Claimable residue is the
   composition only: corrected target-stacking on **PDE reduced-basis
   coefficients** under the no-LF-at-test, tiny-N_hf, copy-LF-skill panel.
2. **The strongest novelty position in this batch is D2, the condition-dimension
   discriminator — a diagnostic, not an architecture.** Round 3 upgrades M15 from
   n = 1 to n = 4 high-cond_dim cells (pfc 18, allen_cahn 19, cahn_hilliard 19,
   fisher_kpp 50) against n = 2 low (ifc_heat 3, ifc_poisson 5), because the IC
   coefficients are now inside the condition vector. Report per-direction OOF R²
   **from the condition** vs **from the SET coefficients** on every panel cell and
   test M15's stated prediction. Cite arXiv:2310.16241 and arXiv:2607.06832 as the
   published pre-fit "should we share?" criteria the proposal is distinct from
   (different independent variable; not a cascade on predicted targets).
3. **Exploit the field's stated default as the framing, and say so.** The
   published justification for one-regressor-per-mode is that *"POD reduced
   coefficients are decorrelated"* / *"modeling them independently avoids
   introducing artificial correlations"* — a **second-order** argument that
   licenses nothing about nonlinear cross-coefficient dependence. B3-F24 measured
   OOF R² 0.92–0.94 for exactly that dependence. This is the honest one-sentence
   motivation and it is retrieval-grounded (iteration_2 term 1, iteration_5 term 3).
4. **Every number in the card is new.** Round-2's 18.6787 / 11.4148 / 12.6601 are
   **void** (`program.md` §2): the panel is 6 completeness-certified datasets, the
   launch best-floor geomean is **38.63**, and `state/anchors_repaired/noise_floor.json`
   is **PROVISIONAL** pending r3s4. Do not quote a round-2 skill as an expectation;
   quote it only as a direction with the void flag.
5. **Floor arms are mandatory and D3 is a bug-fix, not a contribution.** Report
   `nn_condition`, `train_mean`, `zero`, and — on any ifc cell — the fitted
   `affine_on_hf_train` floor next to the claim (ifc_poisson skill 1.5938,
   oracle-affine residual 5.4e-16; ifc_heat skill 0.9584). A model that does not
   beat the affine floor has learned nothing beyond linearity, and skill < 1 on
   ifc_heat is not by itself a strong claim (`program.md` §2 affine-floor rule).
6. **Regime is not a differentiator.** Condition/IC-coefficient → field with no
   solve at inference, FiLM-conditioned decoders, POD-NN/PCA-Net heads, per-mode
   OOF family selection, supervised basis ordering and Bates–Granger blending are
   ALL already preempted (this loop's iteration_5 term 2 plus
   `round2/websearches/r2s1_direct/batch_{1,2,3}/report.md`). Any of them appears
   in the card as a **declared baseline arm**, never as the contribution.
