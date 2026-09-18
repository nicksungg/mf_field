# Direct reported loss control

Specification frozen on 15 September 2026 before calculating any new evaluation result. This is a post hoc analysis of previously inspected historical predictions, not an independent confirmation experiment.

## Scope and inputs

Use every one of the 60 existing historical partitions across 20 datasets and the fixed budget of five calibration fields. Preserve the nine expert order, archived input group identities, calibration rows and evaluation rows. Exclude the separate ERA5 experiment from this control. No expert fitting, new simulations, feature selection, model selection, or new data partition is allowed.

Use authentic per case normalized error Gram matrices from the preserved ORCD cache copied into `data/review_grams`. Hash every source file. Validate each calibration mean Gram against its archived fit artifact and each historical evaluation vector against archived weights and errors. A material mismatch stops the computation and is not repaired by substituting another dataset or split.

## Fixed method

The new candidate minimizes the average relative L2 error directly: mean_i ||A_i w||_2, subject to w >= 0 and sum(w) = 1, with A_i^T A_i = G_i. Solve the epigraph second order cone problem using CVXPY and Clarabel with absolute gap, relative gap and feasibility tolerances 1e-10, maximum 500 iterations. Normalize the Gram matrices by their calibration mean diagonal only to improve numerical conditioning. No hyperparameter is tuned using evaluation results.

Symmetrize each calibration Gram and factor it by eigendecomposition. Negative eigenvalues no larger than 1e-12 times its spectral scale are treated as roundoff, clipped to zero and recorded. More negative eigenvalues trigger a failure, never an unnoticed square root of an indefinite matrix. Require an optimal solver status, finite weights, simplex residual at most 1e-8, and an objective no worse than the archived fitted mixture and all single models to relative tolerance 1e-7. Record primal residual and solver status. Use the original squared fitted and inverse mixture weights as replay references, without changing them.

Finish and save every partition's fitted weights and calibration diagnostics before starting the evaluation stage. Record a SHA256 of the complete locked weight file. Evaluation uses only these saved weights.

## Reporting

Compute each method's mean relative L2 over its fixed evaluation cases, then average the three partition errors per dataset. Compute geometric error ratios across datasets and across the seven existing classes, following the manuscript's original aggregation. Compare direct metric fitting with the archived selected model, inverse mixture and squared fitted mixture. A win requires a ratio below 0.99 and a loss above 1.01. Retain neutral cases and report all 20 datasets; do not select favorable subsets.

The control addresses loss choice for a frozen expert library. It does not demonstrate independent training reproducibility, compute efficiency, the value of multifidelity relative to fine only ensembles, or generalization to a new problem family.

## Numerical amendment before evaluation

The first calibration only solve (Darcy, partition s172) terminated `optimal_inaccurate` with a primal residual around 1.5e-10 at the requested 1e-10 feasibility tolerance. No new evaluation was run and no weights were locked. The solver feasibility tolerance is therefore fixed at 1e-9 for every partition, keeping both gap tolerances at 1e-10 and the independent simplex check at 1e-8. This changes numerical termination only, not the objective, data, model list, or reporting specification.
