# Scientific recheck during revision integration

> Historical review record from 15 September. Its roster dependent counts are superseded by [the 16 September scope update](SCOPE_UPDATE_20260916.md). The current manuscript and generated results use 19 settings, with 18 in the common aggregate.

This check inspected the revised method, experiments, introduction, abstract, reproducibility statement, appendix, and the numerical reanalysis outputs. The results section was still being integrated at the time of the first pass. The manuscript was not edited by this check.

## Checks passed

- Independently reconstructed the historical case accounting from all split files: 1,740 evaluation appearances and 1,423 distinct dataset and row pairs. The elliptic class has eight settings, consistent with the stated weighting example.
- Independently checked all 180 automatic choices against their leave one out score minima in the fixed tie order. Every saved automatic weight vector equals its chosen rule's full calibration refit exactly.
- Independently reconstructed all 720 per partition mean errors from the saved per case arrays. They agree with the JSON scores.
- The protocol correctly distinguishes within dataset exclusion from cross archive overlap, the three partitions from independent training replications, and five additional calibration fields from five total fine simulations.
- The method correctly states that weights are shared across pixels and new cases, and that selected models and automatic rule selection use mean relative L2 while inverse and squared stacking fit squared errors.
- The abstract and introduction now acknowledge the established combination methods, prescribed training recipes, historical development access, and the limited scope of the implemented calibration stage. The reproducibility statement correctly declines to claim a complete public trainer/simulator release.
- The original fitted and inverse scores are reproduced, not silently replaced by improved optimizers. The new metric aligned rule is a separate post hoc control.

## Exact meaning of selection regret

The denominator in `tables/review_selection.tex` is an evaluation oracle chosen **separately in each partition**. For dataset d and partition s, compute the mean evaluation relative L2 error of each of the three fixed rules, then take the smallest of those three means. Average these three partition minima within dataset d. Divide the automatic rule's partition averaged error by that denominator, then form the stated equal class or equal dataset geometric aggregate.

This is a **relative error ratio**, not an additive regret and not a mean of per case oracle choices. At five fields the ratios are 1.027108 and 1.042028, or 2.71 percent and 4.20 percent worse than the partition oracle. The same independently reconstructed equal dataset ratios at ten and twenty fields are 1.044423 and 1.041811.

Do not describe this denominator as merely the best fixed rule per dataset. Taking the minimum only after averaging partitions is a different, weaker diagnostic, whose five field ratios are 1.01731 and 1.02195. The JSON retains both with distinct names.

## Necessary integration checks

1. The final results must actually report the exact automatic selector and identify it as a new post hoc replay, with fixed candidate set and no new test draw. At five fields the class/dataset ratios to calibrated individual selection are 0.872862/0.914514, with 14 wins, four neutral, and two losses at the one percent threshold. Counts of selected/inverse/fitted choices are 18/15/27 out of 60. Its advantage over either fixed mixture is small, and it loses to fixed fitted stacking at ten and twenty fields.
2. The common 18 dataset coverage check weakens any claim of general superiority to the best individual. Fitted versus retrospective best library has equal dataset ratio 1.02041, and automatic versus that reference has 1.01123. Reporting only the favorable class ratios would conceal this substantive sensitivity. The 15 audit retained subset supports mixing versus calibrated individual selection, but it does not validate the retained simulators or establish equal resource comparisons.
3. M8 and M9 reference identical full prediction archives on Darcy and Helmholtz I, as verified by source hashes. The final diversity interpretation should disclose this and identify effective model count as weight dispersion. No deduplication performance control has been run.
4. The metric aligned fitting control must remain outside the automatic candidate set. The automatic rule evaluated in the replay chooses among the original three rules only. Its post hoc 2.0/2.2 percent gain over squared fitting cannot be described as a prospectively validated new method or silently substituted into the automatic headline.
5. Keep the nominal budget cap visible: Cavity I uses eight fields at nominal K=10 and K=20. Twenty historical settings and seven ERA5 experts remain the correct comparison coverage. The reanalysis adds no ERA5 experts and no matched training budget evidence.

## Remaining substantive limitations after presentation repair

No observed inconsistency invalidates the checked reanalysis arithmetic or the stated simplex procedure. However, a revised manuscript still cannot claim a new ensemble principle, matched resource superiority to published baselines, multifidelity specific causal gains, prospective complete workflow validation, independent 21 family generalization, or strong operational climate skill. These require additional evidence rather than wording changes. The revised scope and limitations currently acknowledge these distinctions.
