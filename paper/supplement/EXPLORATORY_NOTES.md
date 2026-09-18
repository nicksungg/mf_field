# Exploratory material retained outside the paper

These records document earlier investigations. They do not add methods to the
paper's three primary rules or expand its main evaluation beyond 22 datasets.

## Regularized mixture controls

The original stability experiment used the 17 PDE diagnostic tasks and the
additional Heat I inputs. Shrinkage replaces the fitting error matrix by

\[
C_\alpha=\alpha\widehat C+(1-\alpha)\operatorname{diag}(\widehat C).
\]

The value of \(\alpha\) is chosen from \(0,0.25,0.5,0.75,1\) using leave one
out fitting error. A ridge variant penalizes departures from inverse error
weights, with its penalty selected from \(10,1,0.1,0.01,0\) under the same
fitting budget. Both controls reuse the trained model predictions. The full
formulations and definitions are retained under “Regularized mixture controls”
in [the archived appendix](archived_appendix/appendix.tex).

These controls are moved out because the current paper centers on selection,
inverse error weighting, and joint fitting. Their historical status and data
budgets are unchanged. This move is editorial and does not establish that the
controls were either unnecessary or successful.

## Refreshing weights after coarse inputs change

The additional Heat I experiment has 128 evaluation inputs. Its perturbation
pools the predicted coarse field to half resolution and reconstructs it before
supplying it to M8 and M9. The other seven models remain fixed. Reusing inverse
weights fitted before the perturbation gives 0.182726% error at five fitting
examples. Predicting those same fitting inputs again and refitting weights
gives 0.005563%. For the fitted mixture, the corresponding errors are
0.148234% and 0.005688%. Fine fitting answers are reused, so no new fine solves
are needed for this refit.

This is a controlled perturbation of one dataset, not evidence for arbitrary
changes in physics or climate. Its procedural description is preserved in
[the coarse refresh record](archived_appendix/coarse_refresh.tex). It remains
outside the current paper's main claim about fixed prediction pipelines.

## Longer concentration calculation

The paper retains the deterministic bound separating error matrix estimation
from numerical optimization. The earlier derivation additionally assumes
independent fitting fields and bounded error products to apply Hoeffding's
inequality. For nine models and 95% confidence, its excess risk bounds are
\(3.596B\), \(2.543B\), and \(1.798B\) for 5, 10, and 20 fields. Each is weaker
than the trivial bound \(B\). It therefore supplies no useful small sample
certificate. The assumptions, proof, optimization gap, and further identities
remain in [the original mathematical appendix](archived_appendix/appendix.tex).

## Extra tables and plots

The broader subset grid, repeated individual error tables, adaptation source
summary tables, class plot, and individual error heatmap remain in the source
package. The paper keeps one compact subset table and refers to its main
individual model table, avoiding repeated displays of the same evidence.
See [the companion index](README.md) for paths. Numerical results are unchanged.

