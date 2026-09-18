# Response to the scientific review

> Historical review record from 15 September. Its roster dependent counts are superseded by [the 16 September scope update](SCOPE_UPDATE_20260916.md). The current manuscript and generated results use 19 settings, with 18 in the common aggregate.

This document explains how the separate revised draft addresses the [scientific review](SOURCE_REVIEW.md). The original manuscript at `mf_field_automf_paper_20260914` remains untouched. All revisions and additional artifacts are in `mf_field_automf_paper_review_revision_20260915`. The original file manifest is retained in [original_manifest.json](original_manifest.json).

**Overall assessment:** the revision corrects the scholarly positioning, evaluates the previously missing automatic selector on the historical archive, investigates the loss mismatch, and improves protocol precision and calibration reproducibility. It does **not** resolve all major scientific objections. No base models were retrained, no matched cost experiment was conducted, and no new independent confirmation set was collected. The new automatic and loss analyses are retrospective uses of predictions already inspected during development. The resulting draft is a more defensible empirical study, not evidence that the complete system now satisfies every standard in the review.

“Addressed” below means that the specified omission or inconsistency is corrected. It does not imply that a broader scientific claim has been proved. “Partially addressed” identifies useful new evidence with material remaining limits. “Unresolved experiment” means the necessary experiment or scientific verification has not been performed.

## 1. Closest engineering prior work and the actual contribution

**Status: addressed for citation and claim scope. The strength of the empirical distinction remains an open research question.**

The revised title is **AutoMF: Calibrated Ensembles for Multifidelity Field Prediction**. The abstract and introduction identify the contribution as the implemented field library and its empirical calibration study. They do not claim a new averaging algorithm, nine new backbone methods, a new principle of parameter based deployment, or a general five example guarantee.

[Related work](../sections/related_work.tex) now directly discusses the three central omissions:

- Acar and Rais Rohani (2009), [optimized metamodel weights](https://doi.org/10.1007/s00158-008-0230-y).
- Viana, Haftka, and Steffen Jr. (2009), [selection, weighting, and surrogate subsets](https://doi.org/10.1007/s00158-008-0338-0).
- Brunel et al. (2025), [a unified multifidelity functional output framework and benchmark](https://doi.org/10.1016/j.cma.2024.117577).

The manuscript explains that these studies already establish the central selection versus combination question and field surrogate benchmarking. Its proposed addition is the specific heterogeneous field library, prediction interface, and empirical calibration evidence. Existing comparisons with Goel, EL MFS, AQBMF, MAESTRO, AutoGluon, and operator learning work remain. The appendix comparison table distinguishes established components from the present investigation and explicitly avoids implying measured superiority to frameworks that were not run.

HyperNOs now uses its final journal citation, volume 19, pages 709–743 (2026), first published online in October 2025. Other preprints remain identified as preprints. Details and verification sources are in [LITERATURE_CHANGES.md](LITERATURE_CHANGES.md).

**Remaining limit:** accurate citations and narrower claims do not establish that the incremental contribution is sufficiently valuable for acceptance. A strong complete workflow comparison and reproducible training artifact are still needed to support a systems advantage.

## 2. The specified automatic selector was missing from the main experiment

**Status: addressed for historical evaluation coverage, partially addressed for workflow validation.**

The exact three rule leave one out selector is now evaluated on all 60 historical dataset partitions at nominal calibration budgets of 5, 10, and 20, giving 180 fits. The candidate set, tie order, numerical optimizer, original expert predictions, and case memberships are preserved. Choices and weights were saved before the new scoring stage. Cavity I uses its eight available calibration fields at nominal budgets of 10 and 20.

The main [Results](../sections/results.tex), subsection “Evaluating the automatic rule selector,” and the appendix [additional analyses](../sections/review_analysis.tex) now report the complete chooser beside the fixed rules. At five calibration fields:

| Procedure | Class ratio to selected model | Dataset ratio to selected model | Wins / within 1% / losses |
| --- | ---: | ---: | ---: |
| Inverse mixture | 0.878 | 0.924 | 13 / 2 / 5 |
| Original fitted mixture | 0.874 | 0.922 | 14 / 0 / 6 |
| Automatic selector | 0.873 | 0.915 | 14 / 4 / 2 |

The automatic chooser selects the single model, inverse mixture, and fitted mixture in 18, 15, and 27 of the 60 partitions. Its unrounded class and dataset ratios to the selected model are 0.872862 and 0.914514. Its advantage over the original fitted mixture is small: ratios 0.998322 and 0.992174. At ten and twenty fields it is approximately 1.6% and 1.5% worse than fixed fitted stacking under the class metric.

The appendix also reports remaining selection error. Against the best of the same three rules chosen **separately within each partition using evaluation answers**, automatic selection has ratios 1.02711 and 1.04203 at five fields. This is an unavailable hindsight reference, not a deployable method or a statistical error bound.

**Remaining limit:** the new protocol was specified before computing these additional scores, but the underlying evaluations had influenced research development. This is retrospective completion of a missing comparison, not prospective confirmation. The new direct loss control described below is not inserted into the selector after observing its result.

## 3. Common test cases do not establish fair comparisons with published baselines

**Status: partially addressed through explicit interpretation. Matched reference experiments remain unresolved.**

The [protocol](../sections/experiments.tex), [model adaptations](../sections/model_adaptations.tex), and [additional reference appendix](../sections/visual_appendix.tex) distinguish common evaluation cases from common training, tuning, or computation. They explicitly state that lower error than an adapted implementation is not evidence of superiority to the complete cited method under equal resources.

The appendix preserves the consequential adaptation disclosures. B1 is a plug in autoregressive POD GP approximation, B5 omits DMFAL's variational and acquisition components, and B8 omits IFC's neural ODE and GP. These references are not presented as faithful reproductions of the complete published procedures. B9 and B10 are described as two archived score entries for the same inspected transfer recipe, not two distinct baseline families. Their differing scores remain unexplained by the inspected source.

The concrete Darcy label allocation example is now explicit: B3 to B5 fit 360 fine rows and validate on 40, whereas B1, B2, and the library transfer recipe fit 400 before mixture calibration. Both allocations consume fine labels, but those labels serve different roles. Some archived timestamps measure export rather than original training and cannot reconstruct matched training cost.

**Remaining experiment:** validate the strongest compatible references and compare defensible recipes under a declared information and computation allowance. No new baseline training, tuning sweep, or trustworthy common runtime ledger has been added in this revision.

## 4. The multifidelity specific source of the gain is not isolated

**Status: unresolved experiment, with corrected claims.**

The [Discussion](../sections/discussion.tex) and protocol now state that the gains may reflect ordinary heterogeneous ensembling. The library includes a fine only POD GP, and many settings have equally sized coarse and fine training tables. Five calibration fields are five **additional** fine labels, not five total fine simulations.

No matched fine only library, same architecture ensemble, LF removal control, LF abundance curve, or alternative allocation of calibration labels to training has been run in this revision. All candidate and shared coarse ensemble costs still need to be counted. The paper therefore limits its conclusion to calibration of the existing library and does not attribute the improvement causally to multifidelity information or claim measured simulation savings.

## 5. Available library quality is different from successful model selection

**Status: addressed in result interpretation and comparator definitions.**

The main results distinguish the following quantities:

- The best library member beats the best available additional baseline on 13 of 20 settings, with class and dataset ratios 0.752 and 0.822. Both minima use evaluation answers and measure available quality.
- The deployable fitted mixture beats that baseline reference on 11 settings and loses on nine, with ratios 0.685 and 0.820.
- The fitted mixture beats calibration based single model selection on 14 settings, with ratios 0.874 and 0.922.
- Against the best member identified after averaging evaluation partitions, the fitted ratios are 0.911 and 0.997. The equal dataset advantage is only approximately 0.3%.

The stronger reference that chooses a best expert separately within each evaluation partition remains explicitly distinguished in the appendix, where the fitted equal dataset ratio is 1.016. The paper no longer uses a generic statement that the ensemble outperforms the individuals without naming the available selection information and aggregation convention.

## 6. Dataset defects and incomplete sensitivity analyses

**Status: partially addressed with new sensitivity results. Scientific validation remains unresolved.**

The paper retains the requested 21 settings but identifies them as settings, not independent physical families. The main protocol now exposes the Poisson boundary scaling defects, incomplete realization information in Cahn Hilliard I, synthetic LF Pressure Poisson fields, and related cavity simulations. Detailed qualifications remain in the dataset appendix.

All central comparisons are now recomputed under the same five audit exclusions, the common 18 setting B1 to B11 coverage subset, and their 13 setting intersection. Membership follows the documented exclusions and coverage, not the new scores. At five fields:

| Scope | Settings | Best library / best baseline | Fitted / selected | Automatic / selected |
| --- | ---: | ---: | ---: | ---: |
| Historical | 20 | 0.752 / 0.822 | 0.874 / 0.922 | 0.873 / 0.915 |
| Audit retained | 15 | 0.751 / 0.823 | 0.869 / 0.898 | 0.862 / 0.889 |
| Common baseline coverage | 18 | 0.777 / 0.861 | 0.870 / 0.936 | 0.868 / 0.928 |
| Intersection | 13 | 0.780 / 0.877 | 0.864 / 0.914 | 0.856 / 0.903 |

Each pair is the class ratio followed by the equal dataset ratio. The full set of headline comparisons appears in the appendix tables, not only these selected columns. Importantly, on the common 18 setting subset, fitted stacking and automatic selection are **2.0% and 1.1% worse** than the hindsight best library member under equal dataset weighting. This adverse sensitivity is now reported in the main results and appendix.

**Remaining limit:** these analyses support calibration versus choosing a model on the same calibration fields. They do not certify retained solvers, remove shared simulations, reconstruct missing realization parameters, or make synthetic coarse data evidence about an actual cheaper physical solver. A validated scientific core remains an empirical and provenance task.

## 7. Statistical replication and generalization

**Status: partially addressed in accounting and scope. Uncertainty and prospective validation remain unresolved.**

The [evaluation protocol](../sections/experiments.tex) now distinguishes 2,890 query pool rows from 1,740 evaluation appearances across the three partitions and 1,423 distinct dataset and row pairs. The latter are not necessarily distinct physical simulations across related archives. Cavity I has two evaluation cases per partition and only four distinct evaluation rows.

The paper consistently states that partitions share predictors trained with a single seed. It explains that a singleton problem class assigns its setting eight times the weight of one member of the eight setting elliptic class. Both class and equal dataset summaries are retained, and the 1% threshold is explicitly descriptive rather than a significance test.

The existing 128 case heat evaluation is kept as an independently generated input draw for one already modeled PDE. Its 40 case calibration pool, shared experts, and repeated calibration selections are explained. That experiment predates the new review analyses. It does not evaluate the new direct loss rule or complete automatic selector and is not an unseen family test.

**Remaining experiment:** additional training seeds, uncertainty estimates respecting case and simulation dependence, and a prospective workflow evaluation on untouched scientific cases or settings. No new confidence interval, independent training replication, or new scientific test draw has been fabricated or substituted for these missing controls.

## 8. Training role separation and cross dataset overlap

**Status: addressed for the inconsistent scope statement. Historical provenance limits remain explicit.**

The [Method](../sections/method.tex), protocol, and implementation appendix now define input exclusion **within each dataset's training tables**. They explicitly disclose that all Cavity I simulations occur in Cavity II training while their libraries are fitted separately. This does not by itself demonstrate leakage into the Cavity I predictor, but prevents treating the settings as independent or as a test of generalization to an unseen physical family.

Within partition calibration and evaluation row identities are replayed and disjoint. This code and identity verification does not reconstruct every earlier researcher decision or independently revalidate every historical base trainer. The wording now preserves those distinctions.

## 9. Mathematical novelty, assumptions, and the small sample bound

**Status: addressed for mathematical interpretation. No new theoretical novelty is claimed.**

The main [Analysis](../sections/analysis.tex) now calls the quadratic field error identity standard explanatory ensemble mathematics. The proof is retained in the appendix. The deterministic bound concerns excess **squared** relative error and does not require independent fields once its entrywise estimation assumption holds. Independence and boundedness are needed for the separate probabilistic sufficient condition.

The appendix explicitly computes the excess risk bounds as 3.596B, 2.543B, and 1.798B for nine models at budgets of 5, 10, and 20 with failure probability 0.05 and exact optimization. The trivial bound B is tighter at all three budgets. The paper therefore states that the bound neither justifies five calibration fields nor provides a useful numerical guarantee for these experiments. Pixels are not counted as independent examples, and full rank of a single field Gram matrix is correctly distinguished from population estimation accuracy.

## 10. Fitting squared error while reporting relative L2

**Status: partially addressed with a direct optimization control and corrected theory. Independent validation remains unresolved.**

The [error geometry appendix](../sections/analysis_detail.tex) now separates expected squared relative error from expected relative L2. It includes the review's scalar counterexample, where the squared loss optimizer is about 8.9% worse under the reported loss, and explains why Jensen's inequality does not transfer an excess risk guarantee to the other optimum.

A new convex control directly fits mean relative L2 through a second order cone formulation. It was evaluated on all 60 historical five field partitions with the same nine experts and case identities. The specification was saved before computing the new scores, and weights were saved before their evaluation.

The direct loss fit has class and dataset ratios **0.856997 and 0.901446** to the selected model. Relative to the original squared loss fit, its ratios are **0.980176 and 0.977996**, corresponding to approximately 2.0% and 2.2% reductions. Eleven settings improve by more than 1%, none worsens by that margin, and nine are within it. The original fitted results are retained rather than silently replaced.

**Remaining limit:** this is a consequential loss choice within established convex ensembling, not a new weighting principle. It is a retrospective control on previously inspected predictions. It remains outside the three rule selector, and its utility requires independent confirmation before it becomes a newly claimed deployment default.

## 11. Numerical optimization and artifact replay

**Status: addressed for the additional computations, within numerical replay scope.**

The automatic analysis reproduces original per case error vectors within 3.55 × 10⁻¹⁵ and fitted mixture means within 1.55 × 10⁻¹⁵ relative error. Source hashes, calibration and evaluation memberships, and saved weights pass replay checks. All original fixed rule results remain unchanged.

All 60 direct loss solves report optimal status using CVXPY 1.9.2 and Clarabel 0.11.1 under the recorded tolerances. The largest preprojection simplex residual is 4.15 × 10⁻¹¹. PSD handling clips negative eigenvalues only at the stated numerical tolerance, records every adjustment, and rejects materially indefinite input. The scalar counterexample and field error identity are checked numerically.

Evidence is preserved in [review_analysis_checks.json](../qa/review_analysis_checks.json), [loss_control_checks.json](../qa/loss_control_checks.json), and the corresponding saved arrays and fit protocols. An additional [independent recheck](INDEPENDENT_RECHECK.md) verifies the 180 automatic choices and 720 per partition scores. These are checks of computation and provenance, not independent model training or physical solver validation.

## 12. Duplicate experts and what weight concentration means

**Status: partially addressed through a stronger provenance diagnosis. The deduplication experiment remains unresolved.**

The recovered source hashes show that M8 and M9 reference the same complete prediction archives on Darcy and Helmholtz I. This strengthens the original observation of matching calibration Gram rows. The main results and [reanalysis appendix](../sections/review_analysis.tex) now say these entries do not provide independent prediction diversity on those settings.

The appendix explains that inverse weighting changes when an entry is duplicated and that effective model count measures weight concentration over entries, not a count of distinct predictive mechanisms. The historical library is preserved in all new automatic and loss comparisons. No unreported deduplication result is claimed. A deduplicated library requires its own specified evaluation.

## 13. ERA5 application evidence

**Status: partially addressed through accurate application scope. No new ERA5 result has been added.**

ERA5 remains the twenty first setting, with **seven evaluated experts**, 55 fine training inputs, ten calibration inputs, and seven evaluation inputs. It is kept separate from the 20 setting nine model aggregate. The [ERA5 section](../sections/climate.tex) now explicitly states that this is the supplied climate emulation archive, not weather forecasting or verified prediction of future years.

The existing results are unchanged: inverse weighting gives 6.5785% against 6.7369% for the training mean, a 2.35% relative improvement. The original fitted and automatically selected rule gives 6.7723%, about 0.53% worse than the mean. The selected POD GP is constant on the reserved inputs. These results do not establish strong learned climate driver response beyond climatology.

The main protocol and visual inventory distinguish the native 721 × 1440 illustration from the 128 × 256 evaluation grid. The paper states that physical units and calendar coordinates are unverified, relative error depends on additive temperature offsets, and the working loss is unweighted rather than geographic area weighted.

**Remaining work:** establish units, transformations, time and scenario provenance, latitude and longitude conventions, and performance under suitable area weighted absolute, anomaly, and pattern metrics with strong application references. Additional queued or external runs are not represented as completed evidence in this revision.

## 14. Reproducible reporting versus a reusable training system

**Status: partially addressed with a portable calibration implementation. Full pipeline release remains unresolved.**

A new [calibration CLI](../scripts/calibrate_fields.py) accepts separate calibration predictions and fine targets, fits selected, inverse, fitted, or automatic rules using the existing implementation, and writes a weights record with model identities, geometry, settings, and hashes. Its prediction command applies fixed saved weights and never accesses query targets. Documentation is in [CALIBRATION_CLI.md](CALIBRATION_CLI.md).

All eight integration checks pass in isolated copies containing only the CLI and bundled rule implementation. They test numerical replay, opposite signed field error cancellation, query target nonaccess, fixed weights, model order validation, malformed arrays, and overwrite protection. Dependencies for this CLI are NumPy and SciPy. The separate direct loss experiment additionally records its CVXPY and Clarabel dependencies.

The [reproducibility statement](../sections/statements.tex) and pseudocode explicitly limit this artifact to calibration from saved expert predictions. It does not train the nine base models or supply complete datasets, checkpoints, solver metadata, redistribution permissions, or measured resource accounting. End to end reproducibility from supplied scientific inputs remains incomplete.

## 15. Clarity, notation, and presentation inconsistencies

**Status: addressed for the identified wording and labeling defects, subject to final compiled document checks.**

The revisions make the following specific corrections:

| Review issue | Revision |
| --- | --- |
| “Automated” could imply headline evaluation of the full chooser. | Title uses “Calibrated.” The abstract and results separate fixed rules, the complete retrospective selector, and independent input evidence. |
| Query count could be read as independent final tests. | Query pools, evaluation appearances, unique row pairs, shared training, and Cavity I counts are stated separately. |
| ERA5 native picture could imply native prediction resolution. | Main figure caption, protocol, and appendix state the working evaluation grid. |
| Rounded ties receive different bolding. | Main table caption states that bolding uses unrounded errors. |
| B8 aggregates use a different subset. | Coverage remains visible, and the common 18 setting comparison is now reported. |
| “Selected single” conflicts with “selected model.” | Manuscript terminology and generated table labeling are standardized to “selected model.” |
| Coarse refresh results omit their dataset. | The paragraph names Heat I and specifies averaging over evaluation cases and then calibration selections. |
| “Transolver” shorthand obscures the adaptation. | The heatmap uses the slice attention corrector name, while source citations retain the original model name. |
| Algorithm 1 was presented as a numbered figure. | The pseudocode now has an algorithm counter and is placed directly under its explanation without a competing figure caption. |

The review found no central algebra changing typo. The main changes are scientific precision rather than cosmetic correction. The optional signed error mechanism figure was not added, and no new visualization is offered as a substitute for missing controls.

## 16. Venue year and template

**Status: drafting choice clarified. Actual submission metadata remains to be updated.**

The ICLR 2026 style is retained at the user's request as the drafting template. This is not a claim that the manuscript was submitted to the original ICLR 2026 review cycle. Several cited works appeared after that cycle began. The venue year and official template must be changed to the intended actual submission before submission. The paper remains a separate draft with anonymous author formatting.

## Prioritized next empirical work

1. **Freeze one final procedure and confirm it prospectively.** Decide the candidate library, duplication policy, calibration budget, loss, and whether to use a fixed rule or automatic selection before accessing the new evaluation answers. Evaluate that exact procedure beside the original fixed rules on genuinely untouched scientific cases or settings. The retrospective direct loss improvement should inform this specification, not be called its confirmation.
2. **Run the decisive resource and information controls.** Compare a matched fine only library, appropriately tuned individual references, and a closest compatible engineering workflow. Match total fine label access and document its training, validation, and calibration allocation. Include the alternative of spending the extra labels on expert fitting and account for every trained candidate and shared coarse model.
3. **Establish a validated scientific core and meaningful uncertainty.** Confirm solver equations and data provenance, group shared simulations, resolve incomplete inputs, and distinguish diagnostic synthetic fidelity settings. Use independent training seeds where needed and uncertainty estimates that preserve scientific dependence rather than resampling pixels or repeated exposures as independent observations.
4. **Complete the ERA5 application evidence before elevating its claim.** Verify transformations, units, coordinates, and scenario or temporal separation, then assess anomaly and physical skill against climatology and pattern references. Expand expert coverage only under a common audited split, and report it as new evidence only after completion.
5. **Release the actual training workflow and audit diversity and cost.** Package adapters, trainer configurations, split manifests, and one complete scientific example. Evaluate duplicate removal and smaller libraries under a frozen design, including training and inference cost. This would establish whether the practical library earns its complexity.

The revision makes the paper's tested contribution clearer and adds substantive analyses where the stored predictions permit them. Fair training comparisons, independent confirmation, validated application metadata, and a complete training artifact remain necessary evidence rather than editorial tasks.
