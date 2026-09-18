---
title: "Scientific Review of AutoMF"
subtitle: "AutoMF: Automated Ensembles for Multifidelity Field Prediction"
author: "AI assisted presubmission review"
date: "15 September 2026"
fontsize: 11pt
geometry: "margin=0.85in"
colorlinks: true
linkcolor: NavyBlue
urlcolor: NavyBlue
toc: true
toc-depth: 1
numbersections: true
---

# Overall assessment

**Recommendation: reject in its current form for an ICLR research submission, with a credible route to a substantially stronger empirical and systems paper.** The main obstacles are an insufficiently established contribution beyond close engineering precedents, incomplete evaluation of the proposed automatic workflow, and comparisons that do not isolate the value of multifidelity learning from training resources and ensemble diversity. The central mathematical identities and headline aggregate arithmetic passed the checks described below.

The paper studies a useful practical problem: given parameters and coarse and fine solution fields, which surrogate should a practitioner use, and should several predictors be combined? It implements nine heterogeneous predictors and compares selection, inverse error weighting, and joint fitting of nonnegative mixture weights. The mixture has **one fixed weight per model per dataset**, shared over all pixels and future inputs. It is not an input dependent router, a spatial weighting network, or a model trained to generalize across unseen PDE families. The main quantitative comparison uses 20 datasets. ERA5 is a twenty first setting with seven evaluated experts and a separate evaluation.

The strongest supported finding is a conditional empirical one: **on the archived predictors and evaluation partitions, small calibration sets often improve on choosing one library member, and a simple inverse error rule captures almost all of the aggregate benefit of joint fitting.** That is useful evidence. It is weaker than demonstrating a generally superior automated multifidelity modeling system, a new ensemble principle, or a reliable five sample solution to model selection.

An ICLR contribution does not need a novel theorem or a new architecture. A rigorous benchmark, application, or systems result can contribute substantial knowledge. The official [reviewer guidance](https://iclr.cc/Conferences/2026/ReviewerGuide) explicitly asks reviewers to assess the value of the knowledge produced, rather than require state of the art scores alone. My recommendation therefore does **not** rest on the absence of sophisticated mathematics. It rests on whether the evidence establishes the paper's proposed practical contribution.

## Review scope and confidence

I reviewed the current 36 page PDF, including its nine page main text, bibliography, and appendices, and checked relevant LaTeX sources, frozen numerical artifacts, and comparison scripts. The reviewed file is `mf_field_automf_paper_20260914/main.pdf`. Page and line references below refer to its printed pages and review line numbers. I also checked the most relevant prior literature through publisher, proceedings, institutional, and author sources.

This is an AI assisted, nonblind presubmission critique, not an official or independent conference decision. The assessment uses supplementary local evidence that an ordinary reviewer might not receive. No models were retrained and no full solver or training pipeline was independently replicated. Confidence is high in the algebraic checks and reproduced aggregate arithmetic, and moderate in causal conclusions about training failures and generalization. The manuscript was not edited.

## What the paper does well

1. **It asks an important practitioner question.** A heterogeneous field library is useful when the best representation and use of coarse information vary by problem.
2. **The revised attribution is unusually explicit.** The appendix distinguishes actual adaptations from reproductions of Transolver, WNO, FIRE, DMFAL, IFC, and other cited methods. This deserves credit.
3. **Several evaluation safeguards are substantive.** Calibration and evaluation rows are separated within partitions, calibration labels are counted separately from base training, and stored predictions and weights permit numerical replay.
4. **The paper reports inconvenient findings.** Joint fitting offers little advantage over inverse weighting, the latter wins on fresh heat cases, ERA5's constant predictor is strong, and automatic selection can choose the worse rule.
5. **The ensemble mathematics is correct and educational.** The discussion distinguishes uncentered error products from centered covariance, and whole fields from independent pixels.
6. **The manuscript is clearer than its research premise alone might suggest.** It defines its three principal choices, exposes individual model errors, and explicitly qualifies the 20 versus 21 dataset coverage.

## The most important weaknesses

The paper currently supports an interesting calibration study more convincingly than an automated modeling system. The closest engineering literature already covers optimized surrogate mixtures, selection versus averaging, and unified multifidelity functional output benchmarking. The proposed complete automatic selector is not evaluated in the main 20 dataset experiment. The individual baseline comparisons use different training budgets and sometimes substantial method adaptations. Missing fine only ensemble and label allocation controls prevent attributing gains specifically to multifidelity learning. Finally, dataset defects, related variants, weak statistical replication, and the limited ERA5 application restrict the significance of the resulting benchmark evidence.

# Novelty and the closest engineering literature

## The central question has substantial precedent

The relevant comparison is not just with FNO, DeepONet, and generic AutoML. The paper's central question sits directly in the engineering literature on **ensembles of metamodels** and **multifidelity functional output surrogates**. The current bibliography covers important examples but omits three particularly close studies.

**Acar and Rais-Rohani (2009), missing.** Their [study of optimized metamodel weights](https://link.springer.com/article/10.1007/s00158-008-0230-y) treats weighted combination as optimization of a prediction error metric and examines error estimates from training information or a few validation points. This directly precedes the fitted mixture motivation. AutoMF's field outputs and specific normalized simplex objective are useful specifications, but do not establish a new principle of ensemble learning.

**Viana, Haftka, and Steffen (2009), missing.** Their [study of cross validation for multiple surrogates](https://link.springer.com/article/10.1007/s00158-008-0338-0) examines selecting one predictor versus weighting several, integrated squared error for weight determination, and using a subset versus the full library. These questions overlap closely with both AutoMF's main narrative and its supplementary pair and library controls. This is a central omission, not a request to add a tangential citation.

**Brunel et al. (2025), missing.** Their [unified framework and benchmark for multifidelity functional outputs](https://arxiv.org/abs/2408.17075), available as a preprint in 2024, implements more than a dozen existing surrogates in one framework. It studies when different approaches work and discusses fidelity correlation, training size, and residual complexity. The [author institutional record](https://sudret.ibk.ethz.ch/publications/preprints-archive/2024-006.html) confirms this implemented benchmark contribution. This is closer to AutoMF's library and benchmark premise than generic PDE benchmark citations. AutoMF adds a different collection, modern neural candidates, and posttraining mixtures, but must establish what new understanding these additions produce.

These omissions mean the answer to “was all key closest prior work cited?” is **no**. Adding the references would repair the scholarly positioning, but citations alone would not supply the missing experimental distinction.

## Important close work is already acknowledged

It would be unfair to say the authors ignore engineering precedent entirely. The following work is already cited and is broadly characterized correctly:

| Prior work | Relevant overlap | Meaningful distinction in AutoMF |
|:--|:--|:--|
| [Goel et al. (2007)](https://doi.org/10.1007/s00158-006-0051-9) | Selecting or combining diverse surrogates with error based weights. | A modern field predictor portfolio with several fidelity use mechanisms. |
| [EL MFS, Wang et al. (2024)](https://doi.org/10.1016/j.aei.2024.102535) | Ensemble learning within hierarchical multifidelity fusion. | Combining completed target field predictors rather than only improving the LF stage. |
| [AQBMF, Lee et al. (2026)](https://web.mae.ufl.edu/nkim/Papers/paper151.pdf) | Screening LF information and automatically choosing among surrogate candidates. | Fixed mixtures across heterogeneous field architectures rather than its hierarchical Kriging candidate construction. |
| [MAESTRO, Kim et al. (2026)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6207840) | Surrogate family screening and leave one out selection in multifidelity modeling. | Direct, corrective, and fine only field experts followed by convex averaging. This is a contemporaneous preprint, not a mature benchmark standard. |
| [AutoGluon, Erickson et al. (2020)](https://arxiv.org/abs/2003.06505) | Automated model libraries and combination. | A fixed, domain specific field library and a small menu of calibration rules. |

A newer [engineering application of multifidelity stacking by Cao et al. (2026)](https://www.tandfonline.com/doi/abs/10.1080/19942060.2026.2646081) is relevant context. It combines operational and simulation experts for pipeline quantities. Its use of “field data” means operational observations, not dense spatial outputs, so it should not be treated as an identical field prediction system. It is a lower citation priority than the three omissions above.

The current paper is also correct to distinguish FIRE's foundation model inference from its own trained distribution FNO, and the original Transolver operation from its modified slice attention corrector. Neither those distinctions nor the engineering precedents imply that every cited system must be reproduced. A focused, technically faithful comparison with the closest compatible approaches is preferable to an indiscriminate expansion of the baseline list.

## What is actually new?

**Not new in itself:** weighted averaging, selecting weights from held out predictions, inverse squared error weights, leave one out selection, the quadratic error Gram identity, the standard uniform estimation error argument, or parameter to output deployment without a new expensive simulation.

**Potentially new and useful:** the specific implementation of a heterogeneous field library, consistent prediction interfaces across several fidelity strategies, the curated evaluation artifacts, and an empirical characterization of small additional calibration budgets for this library. Integrating these components can require substantial technical work. The scientific question is what the resulting artifact reliably establishes that earlier systems did not.

**Not yet demonstrated:** a superior complete automatic workflow, a multifidelity specific source of the gains, general savings in fine simulations or computation, reliable generalization to new problem families, or a substantial new mathematical result. The paper largely acknowledges these limits, but its title, opening workflow, and principal experimental emphasis are not yet aligned tightly enough.

The delta is therefore **nontrivial implementation work but a currently modest and insufficiently isolated scientific contribution**. The nine implementations are not nine separate methodological contributions. The authors could strengthen a systems paper without inventing another weighting rule, provided that the final workflow is actually evaluated, fairly compared, and reproducibly released.

# What the numerical results establish

The main arithmetic is reproducible from the frozen artifacts. The following table makes the reference choices explicit. Ratios below one favor the numerator. Wins and losses use the paper's greater than 1 percent threshold and are descriptive counts, not significance tests.

| Comparison on 20 datasets | Class ratio | Dataset ratio | Wins / losses |
|:--|--:|--:|:--:|
| Best library member / best additional baseline | 0.7518 | 0.8223 | 13 / 7 |
| Fitted mixture / calibration selected model | 0.8743 | 0.9217 | 14 / 6 |
| Inverse mixture / calibration selected model | 0.8775 | 0.9237 | 13 / 5 |
| Fitted mixture / best library member | 0.9106 | 0.9967 | 12 / 7 |
| Fitted mixture / best additional baseline | 0.6846 | 0.8196 | 11 / 9 |

Rows whose counts sum to less than 20 contain changes within the threshold. “Best” in this table is determined retrospectively from partition averaged evaluation errors. Source: manuscript Tables 1, 2, and 10 and independently recomputed frozen summaries.

Four conclusions follow.

**First, the 13 wins establish available library quality, not successful automatic discovery of that member.** Both sides are retrospective minima. The deployable fitted rule has 11 wins against the retrospective best additional baseline, with substantial aggregate gains but nine losses. These comparisons are useful diagnostics. They must not be conflated with what a user can select without evaluation answers.

**Second, the strongest ensemble claim is relative to calibration based selection.** Its 12.6 percent class balanced and 7.8 percent dataset balanced improvements are correctly calculated. Against the best individual library member, however, the equal dataset reduction is only approximately **0.335 percent**. A different, stronger hindsight reference that chooses an expert within each partition gives an equal dataset ratio of **1.016**, slightly favoring that reference; the appendix discloses this. There is no contradiction, but the phrase “outperforms the individual models” needs a precisely named reference.

**Third, class weighting changes the practical impression.** With seven classes, a class containing one dataset has eight times the per dataset weight of a member of the eight dataset elliptic class. This is a defensible convention when chosen for scientific reasons, but neither convention is uniquely correct. The paper appropriately reports both. The difference between approximately 8.94 percent and 0.335 percent improvement over the best member is consequential and should not be hidden behind one headline.

**Fourth, the evidence favors simple calibration more than elaborate fitting.** At five fields, fitting all interactions improves the class aggregate by only about 0.36 percent relative to inverse weighting, and the ordering reverses on fresh heat cases. This is a valuable negative result about complexity. It weakens an argument for the fitted optimizer as the new methodological contribution, while supporting a simpler practical default.

# Experimental rigor and validity

## Major: the automatic workflow is not the main evaluated object

Section 3.4, equation (5), and Algorithm 1 specify choosing among three rules by leave one out calibration error. The 20 dataset results instead evaluate the rules individually. Inspection of all 60 historical runs found no corresponding three rule automatic selector result. The algorithm caption acknowledges this, but only in the appendix, on page 32, lines 1704–1706.

The actual automatic selector is evaluated on ERA5, where it chooses the fitted mixture in every recorded fit even though inverse weighting performs better at evaluation. This does not prove the selector is generally bad. It does mean that the positive benchmark results cannot be read as validation of the complete system described in the workflow.

The decisive experiment is straightforward: freeze the library and selection procedure, then report the complete selector alongside rules fixed in advance, using exactly the same calibration and evaluation cases. Report selection frequencies and the cost of choosing the wrong rule. A system with a fixed inverse weighting policy can also be “automatic,” but the tested system and the specified system must be the same.

## Major: common test rows do not make the baselines fully comparable

The row matching is a real strength. Nevertheless, Section 4.1 and Appendix B disclose unequal training, tuning, and computation. Several baselines also depart materially from the cited methods. B5 removes the variational and acquisition components of DMFAL. B8 omits IFC's neural ODE and Gaussian process. B1 is not joint probabilistic co Kriging. B7 imports upstream MFRNP but changes normalization, training, batching, resizing, and context handling. B9 and B10 have byte identical inspected model files but unexplained differences in saved scores.

These are legitimate *implemented references* when clearly named. Beating them does not establish superiority to the associated papers as published. The revised manuscript generally respects that distinction, and the review should not accuse it of claiming exact reproductions. The remaining problem is whether this restricted comparison is persuasive evidence of the proposed library's quality.

There are also concrete differences in information allocation. In the inspected Darcy examples, B3 to B5 use 360 fine training examples and 40 internal validation examples, whereas B1 and B2 fit 400, and the library transfer recipe fits 400 before additional mixture calibration. Validation examples are still fine labels, but they serve different purposes. No single ranking can isolate architecture from these choices. Some reexported timing fields describe effectively instantaneous export operations rather than original training, so they cannot reconstruct trustworthy training costs.

A strong revision should validate the most important comparator implementations, use defensible tuning budgets, and report total fine labels and measured computation. It need not make every algorithm use identical optimizer iterations; equal iterations are not equal cost or equal optimization quality. It should compare reasonable recipes under transparent, matched resource envelopes.

## Major: the multifidelity contribution is not isolated

Much of the observed benefit could arise from ordinary heterogeneous ensembling. The library already includes a fine only POD GP, which wins all three Poisson variants. A field library containing only appropriately trained fine predictors is missing as a matched ensemble control. A same architecture ensemble across initializations would help separate architecture diversity from ordinary variance reduction.

Many tasks have 400 coarse and 400 fine training rows. Thus the experiments do not systematically establish the common multifidelity regime in which coarse data are abundant and fine labels are scarce. Varying only the number of additional calibration fields is not a learning curve for the whole multifidelity pipeline.

The key controls are: a fine only library under the same total fine label budget, LF removal or quality variation, and comparison of spending the extra fine fields on calibration versus additional expert training. Training the full portfolio, including out of fold coarse ensembles, must be counted. The paper correctly avoids claiming proven cost savings. Without these controls, it should also avoid attributing the gains specifically to multifidelity information rather than to model diversity.

## Major: the dataset collection is not yet a validated scientific benchmark

Appendix C.1 acknowledges boundary scaling defects in Poisson I and III, shared simulations between Cavity I and II, missing realization information in Cahn Hilliard I, synthetic coarse fields for Pressure Poisson, and amplitude normalization in Helmholtz II. These are different issues and should not be collapsed into a generic label such as “imperfect data.”

A boundary defect can change the physical target or fidelity relation. Missing realization information means the supplied parameters need not identify a deterministic field, which conflicts with the simple simulator mapping interpretation unless the task is explicitly stochastic. Shared cavity simulations make the settings dependent. Synthetic coarse data can be a useful controlled experiment but do not establish performance with an actual cheaper solver. Amplitude normalization changes the scientific prediction objective.

The sensitivity analysis excluding five flagged settings is valuable: the fitted to selected class ratio remains approximately 0.869 on 15 entries. However, that analysis does not reproduce **all** central claims, including the library versus baseline comparison and automatic workflow performance. It therefore cannot certify the entire benchmark story. A validated core analysis, accompanied by explicitly identified stress or diagnostic settings, would be stronger than treating every file collection as equivalent physical evidence.

Using 21 dataset settings is not itself an error. The paper explicitly distinguishes related settings from independent physical families, and does not silently add ERA5 to the 20 dataset aggregates. The review should assess the quality and effective diversity of those settings, not demand a larger arbitrary count.

## Major: uncertainty and generalization are insufficiently measured

The three partitions reuse predictors trained with a single seed. Independent replay found 1,740 evaluation exposures across partitions, corresponding to 1,423 distinct dataset and row pairs. These counts are not independent training replicates, and the row pair count does not guarantee independent physical realizations across related datasets. Cavity I contributes two evaluation cases per partition and only four distinct evaluation rows across the three partitions.

The descriptive greater than 1 percent win threshold is explicitly not a significance test. That is honest. Nevertheless, results close to unity, including the fitted versus inverse gap and the best member comparison, cannot support strong reliability conclusions without uncertainty estimates. Confidence intervals should preserve pairing, dependence, and scientific grouping. Climate cases require a time or scenario aware design once their metadata are established. A naive bootstrap of all pixels or repeated partition entries would be inappropriate.

The new heat experiment is a meaningful fresh input check: 128 evaluation cases with a separate calibration pool. It still reuses the trained library and covers one PDE. It checks new inputs for an existing problem, not transfer to a previously untouched problem family. Because the historical cases informed development, a frozen workflow on new scientific settings would provide much stronger confirmatory evidence than additional resampling of the same archive.

## Major for the application claim: ERA5 demonstrates little application skill yet

The ERA5 results use 55 fine training examples, a ten example calibration pool, and seven evaluation inputs. Inverse weighting gives 6.5785 percent error against 6.7369 percent for the training mean, a 2.35 percent relative improvement. The fitted and automatically selected rule gives 6.7723 percent, approximately 0.53 percent worse than the mean. POD GP is constant over all 17 calibration and evaluation inputs, and the mean control beats every neural expert. These are correctly reported and scientifically useful observations, but weak evidence for an impactful climate application.

The task is climate driver emulation from the supplied assembly, not weather forecasting. The manuscript already says so. No criticism should invent a forecasting claim that the authors do not make. The actual concerns are the lack of verified time coordinates and absolute units, the tiny evaluation set, and the absence of anomaly or pattern skill measurements beyond a strong climatological predictor.

The inspected arrays do not include unit or time metadata. Their target values include negative numbers, so assuming they are untransformed Kelvin would be unjustified. Relative temperature error is sensitive to an additive temperature origin: converting a consistently represented field and prediction between Celsius and Kelvin leaves their difference unchanged but changes the denominator. The reported percentages therefore require an explicit unit and normalization definition before their physical meaning can be assessed.

Evaluation is on an unweighted $128\times256$ working grid, whereas Figure 2 shows the native $721\times1440$ grid. A regular latitude and longitude grid generally requires area weights for a global physical loss. Verified units, area weighted absolute and anomaly errors, a training mean and pattern scaling reference, and appropriately separated time periods or scenarios would make the case substantially more convincing. The seven expert coverage is disclosed; it is a coverage limitation, not an arithmetic error.

## Important: role separation is stated too broadly in places

Section 3.1, page 3, lines 116–118, says reserved inputs are removed from all LF and HF training tables and that related input versions retain the same role. Appendix B.3 repeats a similar related version statement. Appendix C.1 then says all 50 Cavity I simulations, including its query cases, occur in Cavity II training.

For predictors and mixtures fitted separately within each dataset, this cross dataset overlap does **not** establish leakage into the Cavity I predictor. It does limit independence across datasets and makes the universal wording too broad. Any pooled gate or claim about unseen families needs a separate audit. Section 4.3's reference to family holdouts is also not enough to establish that the main experiment is an unseen family test.

The paper should explicitly separate within dataset input exclusion, grouping across historical query partitions, and any exclusion across base training collections. This is a protocol precision issue with scientific consequences, not grounds for an unsupported accusation of test leakage.

## Important: numerical reproducibility is not yet pipeline reproducibility

The companion material allows unusually useful checks of frozen results. Appendix I also states that full training code, checkpoints, and datasets are not in the manuscript package. That is a material limitation for a paper whose main contribution is a reusable library and automated workflow. A table rebuild cannot demonstrate that another group can supply new data and reproduce the claimed system.

A versioned implementation, complete training and tuning configurations, exact split manifests, documented dataset equations and units, and a small end to end example would be central evidence for this contribution. Missing checkpoints alone need not prevent acceptance, but the system and its scientific inputs must be reconstructible. Provenance and redistribution constraints should be resolved for a benchmark release.

# Mathematical and technical correctness

## Correct identities and conditional statements

Let normalized model errors be $e_m=(f_m(x)-y)/s(y)$, let $G_{mn}=\langle e_m,e_n\rangle_Q$, and let $w$ lie on the nonnegative unit simplex. Equations (1), (2), and (7) correctly imply

$$
\left\|\sum_m w_me_m\right\|_Q^2=w^\top Gw,
\qquad R(w)=w^\top Cw,\qquad C=\mathbb E[G].
$$

The errors are uncentered, so shared bias is retained. No independence between model errors is needed. The inverse squared error rule correctly minimizes the diagonal quadratic approximation, with an explicit numerical floor. The directional and ambiguity identities in the appendix are also correct. These are established ensemble facts, appropriately connected to [stacked regression](https://statistics.berkeley.edu/sites/default/files/tech-reports/367.pdf) and the ensemble literature already cited in the paper.

Proposition 1 is correct. If every entry of $\widehat C-C$ is bounded by $\epsilon$, then every simplex quadratic form differs by at most $\epsilon$. Two such comparisons and empirical suboptimality $\delta$ yield

$$R(\widehat w)-R(w^*)\leq 2\epsilon+\delta.$$

This is a deterministic conditional statement. It does not itself require independent fields. Independence and boundedness enter when turning matrix estimation error into a sample based probability statement. The current main text makes this distinction correctly, though later appendix phrasing could be sharper.

## Correct but standard and quantitatively weak theory

The Hoeffding and union bound argument has the correct constant under the stated conditional independent sampling and entrywise boundedness assumptions. The paper appropriately warns that these assumptions have not been established for the data.

The bound is also numerically uninformative at the reported budgets. With $M=9$, failure probability $0.05$, and exact empirical optimization, its excess risk upper bound is approximately $3.596B$, $2.543B$, and $1.798B$ for $K=5,10,20$. Under the same assumptions, each simplex risk lies between zero and $B$, so the trivial excess risk bound is already $B$. Thus the stated sample bound is vacuous at all three budgets even if its assumptions hold.

This does not make the empirical results wrong. It shows that the theorem is an explanatory observation rather than a quantitative justification for the operating regime. The field Gram matrix can have full rank even with one field, so the objection should not be that five fields necessarily make a nine model fit algebraically impossible. The issue is population estimation, not simply matrix rank.

## Important limitation: fitting and reporting optimize different objectives

The fitted mixture minimizes average **squared** relative error. The headlines and rule selection use average relative $L^2$ error **without squaring**. The manuscript discloses this, so it is not a hidden implementation error. However, it is a substantive limit on the explanatory force of the theory. The objectives can select different population optima, even with unlimited calibration data.

For a concrete counterexample, take two equally probable scalar cases with normalized errors

$$e_A=(0,2),\qquad e_B=(1.1,1.1).$$

Put weight $t$ on A and $1-t$ on B. The mean absolute relative error is

$$L(t)=1.1-0.1t,$$

which is minimized at $t=1$, with value 1. The squared relative risk is

$$R(t)=1.21-0.22t+1.01t^2,$$

whose minimizer is $t=11/101$. Its reported mean error is $110/101\approx1.0891$, about 8.9 percent worse than the mean error optimum. Scalar examples can be embedded in constant field predictions, so the distinction applies to the field setting as well.

Accordingly, Proposition 1 cannot establish near optimality for the reported metric merely by increasing the number of calibration fields. A useful technical control is direct minimization of mean relative $L^2$, which is also convex over the mixture weights, alongside the squared objective. Alternatively, the authors can retain the present practical objective and make the limited theoretical interpretation explicit.

## Numerical optimization appears sound in the checked artifacts

Independent checks covered all 180 saved fitted mixtures across 60 dataset partitions and three calibration budgets. Simplex feasibility held to approximately $2.22\times10^{-16}$. The Gram matrices were positive semidefinite up to roundoff, with the smallest checked eigenvalue about $-1.11\times10^{-16}$. The inverse weighting formula agreed with stored weights within $3.33\times10^{-16}$.

An exhaustive numerical active support recheck improved the archived empirical objective by at most approximately 0.04091 percent. This is not an exact arithmetic certificate or an independent training replication, but it provides no indication that a major optimizer failure explains the reported trends. The Frank–Wolfe gap discussed in the paper is a valid way to report a more direct optimization residual. Small calibration objective differences alone do not bound changes in evaluation error.

## Secondary technical concerns

The calibration Gram rows of M8 and M9 coincide on Darcy and Helmholtz I across the checked partitions, within archived precision. This indicates indistinguishable calibration error vectors there, not two independent sources of diversity. Inverse weighting is not invariant to duplicating a predictor: duplicating one equally accurate expert increases the group's total influence. A duplicate or near duplicate sensitivity check would clarify the library design. Effective model count $1/\sum_mw_m^2$ measures weight concentration, not the number of distinct predictive mechanisms.

The all pairs FNO changes target repetition and optimization cost while receiving no source field. Its name should not imply the same mechanism as Poseidon's temporal pair learning. The paper discloses this and appropriately calls for matched update controls. Similarly, iterative correction with an equilibrium penalty does not establish contraction or physical stability. The paper does not claim such a theorem, and none should be inferred from six refinement steps.

# Clarity, pedagogy, and the most consequential inconsistencies

The main narrative and three rule definitions are reasonably clear. The strongest pedagogical idea is that different predictions can have complementary errors, so the best weighted field need not come from the individually best model. The distinction between whole fields and independent pixels is especially helpful. The main weaknesses are displaced protocol details, inconsistent scope language, and overly precise numbers whose physical or statistical interpretation is not always established.

| Location in reviewed PDF | Issue and consequence | Suggested clarification |
|:--|:--|:--|
| Page 3, lines 116–118; pages 19–20, Appendix C.1 | Related input role separation is broader than the disclosed cross cavity overlap. | State precisely which collections are excluded from each model's training. Do not equate within dataset separation with unseen family evaluation. |
| Page 4, Section 4.1; page 5, Section 4.2 | The 2,890 query cases can be mistaken for independent final test cases. | Distinguish query pool size, per partition evaluation counts, repeated exposures, and unique cases. |
| Page 5, Figure 2; page 24, lines 1287 onward | Native ERA5 resolution is visually prominent, but predictions are scored on a smaller working grid. | Identify training illustration resolution versus evaluation resolution near the main figure or protocol. |
| Page 6, Table 1 | Rounded values can appear tied although only one is bold, such as the two 0.125 cavity mixture entries. | State that bolding uses unrounded errors or increase precision where required. |
| Page 7, Table 2 | B8 has $N=18$ while most rows have $N=20$. The ratios do not all summarize the same set. | Retain the coverage label and avoid treating the entire table as a single strictly comparable ranking. A common subset check would help. |
| Page 23, Table 10 | “Selected single” reappears after the main text standardizes “selected model.” | Use one name for the same deployment rule. |
| Page 24, lines 1268–1275 | The coarse refresh paragraph gives precise errors without identifying the dataset. | Name Heat and specify how evaluation cases and calibration selections are averaged. Otherwise the numbers can be read as cross dataset results. |
| Page 31, Figure 5 | The heatmap uses “Transolver” shorthand for the custom slice attention corrector. | Use M8 or the adapted model name, preserving the attribution distinction made in Table 2. |
| Page 32 | “Algorithm 1” is embedded inside a float captioned “Figure 6.” The associated heading is separated from it by intervening material. | Use one numbering system and keep the procedure with its explanation. |
| Page 1 and conclusion | “Automated” can suggest that the full rule chooser produced the headline results. | Say which automated decisions are evaluated and which results are fixed rule components. |

I did not find a serious spelling error or an algebra changing typesetting typo in the central equations. Most important corrections are scientific scope and terminology issues rather than grammar. The prose's removal of conventional compound hyphens sometimes makes noun sequences harder to read, but this is a minor editorial preference and not a reason to reject the paper.

The current figures illustrate fields, not error mechanisms or deployment reliability. A scientifically stronger visual would show, on a predetermined case, a target, a good individual prediction, a complementary prediction, and the mixture's signed error under a shared scale. This is optional presentation work, not a substitute for missing controls. The current compact baseline plus nine model table is useful and worth retaining.

There is also a venue metadata inconsistency if the document is intended as an actual original ICLR 2026 submission: it cites work first available in August 2026, while [ICLR 2026 reviewing began in 2025](https://iclr.cc/Conferences/2026/ReviewerGuide). If the 2026 style is only a drafting template, this is administrative rather than scientific. Use the correct eventual venue year. Existing preprint citations can be valid, but bibliographic metadata should be updated where final publication is known, for example HyperNOs.

# What would make the contribution convincing?

## Changes that could alter the recommendation

**1. Evaluate one frozen final system.** Decide whether the contribution is fixed inverse weighting, fitted stacking, or automatic selection among rules. Run that exact procedure on the shared benchmark and independent confirmation cases. Do not select the best rule after inspecting final results. This is the highest priority because it aligns the evaluated object with the claimed contribution.

**2. Establish fair reference experiments.** Validate the strongest relevant implementations and report training labels, tuning labels, calibration labels, runtime, and inference cost. Include a fine only ensemble, a strong reduced basis multifidelity reference, and a closest compatible engineering automation comparison. If a scalar framework is adapted to functional outputs, use a defensible shared representation and document the adaptation rather than constructing an intentionally weak per pixel baseline.

**3. Strengthen the scientific data and uncertainty.** Use a validated core for the primary claim and report all headline comparisons under the quality sensitivity analysis. Preserve related simulation groups in any external validation. Add independent training replicates where needed to distinguish variability from small gains, and confidence intervals appropriate to the dependence structure. Freeze the method before evaluating genuinely new problems or scientific scenarios.

**4. Demonstrate the claimed practical artifact.** Release enough code, definitions, and configurations to run the full workflow from supplied data. Include one complete example and an auditable resource ledger. If ERA5 is the principal application, establish its units, time and scenario provenance, geographical metric, and skill relative to strong application references.

**5. State the contribution against the engineering literature precisely.** Cite the three central missing precedents, acknowledge that the weighting and Gram theory are established, and identify the tested implementation or empirical insight that makes this artifact worth adopting. “Nine models plus a weighted average” is a description of components, not by itself a sufficiently justified contribution statement.

These recommendations do not require a new theorem, all possible baselines, universal wins, or a larger arbitrary dataset count. A technically reliable and practically valuable empirical contribution could be enough. The purpose is to demonstrate what the current system adds, rather than to accumulate more loosely connected experiments.

## Useful but secondary improvements

Direct mean relative error fitting would clarify the objective mismatch. Duplicate expert sensitivity would clarify the meaning of diversity. A cost versus accuracy curve would establish whether the full library earns its expense. Controlled changes in LF abundance and quality would explain when multifidelity information matters. Physics residual or application quantity metrics would be valuable on selected tasks, but should be tailored to the declared application rather than added as generic decoration.

# Questions for an author response

1. What single procedure is proposed for deployment: a predetermined mixture rule or the leave one out chooser? Where are the latter's 20 dataset results?
2. What empirical result distinguishes the workflow from the closest engineering ensemble and functional output benchmark approaches, beyond replacing their candidate models with newer architectures?
3. Which baseline implementations have been validated against their intended source behavior, and how will their training, tuning, and fine label allocations be made comparable?
4. Do gains remain against a fine only ensemble under the same information and computation budget, and when the additional fine labels are used for expert training instead of mixture calibration?
5. Do the library versus baseline and complete workflow conclusions survive the same data quality exclusions used for the fitted versus selected sensitivity result?
6. What were the exact selection and development roles of each dataset, including related cavity versions? Which results come from a final method frozen before any access to their evaluation outcomes?
7. What are the physical units, time coordinates, input meanings, and latitude and longitude conventions of the ERA5 assembly, and what skill remains beyond climatology under an appropriate physical metric?
8. Can an independent group run the full workflow on a new dataset from the provided artifact, and what measured resources does that require?

# Review evidence and verification record

The recommendation is driven by missing empirical distinction and controls. The arithmetic and mathematical identity checks passed. Independent checks reproduced the historical mixture summaries to a maximum absolute difference of approximately $4.44\times10^{-16}$, verified saved weight hashes, and confirmed disjoint calibration and evaluation identities within the 60 historical runs. These are artifact consistency checks. They do not reconstruct every historical researcher decision or independently prove that each base trainer excluded every possible source of test information.

Supporting audit files are saved beside this report:

- `experiment_audit.md`: experimental assessment.
- `math_audit.md`: mathematical and optimizer checks.
- `prior_work_audit.md`: verified source comparisons.
- `recompute_experiment_claims.py`: aggregate recalculation, with JSON results.

The literature audit distinguishes verified primary source descriptions from untested claims in those sources. The PDF, LaTeX manuscript, section sources, and bibliography were fingerprinted before review and checked again afterward.

**Reviewed PDF SHA256:**

```
ad368a95c34ae20d2be23375eef1763081bb5c590ad52bef84e8f60f8ca6c5ef
```

The links throughout the report identify the primary sources behind the literature comparisons. Priority references to add or discuss are Acar and Rais-Rohani, *Structural and Multidisciplinary Optimization* 37, 279–294 (2009), DOI 10.1007/s00158-008-0230-y; Viana, Haftka, and Steffen, the same journal 39, 439–457 (2009), DOI 10.1007/s00158-008-0338-0; and Brunel et al., *Computer Methods in Applied Mechanics and Engineering* 435, 117577 (2025), DOI 10.1016/j.cma.2024.117577. The first is online from 2008, and the third has a 2024 preprint, so their priority does not depend on recent publication dates.

**Final judgment:** the manuscript contains useful implementation work, transparent limitations, correct elementary mathematics, and encouraging conditional results. Its strongest defensible contribution is an empirical field library and calibration study. The current evidence does not yet establish the substantial, reproducible advantage of the automatic multifidelity workflow needed to make that contribution convincing at ICLR.
