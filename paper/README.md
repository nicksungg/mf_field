# AutoMF: Automated Ensembles for Multifidelity Field Prediction

This is the separate 22 dataset extension dated 17 September 2026. Read `main.pdf`.
The preceding review revision is preserved unchanged in its own directory.
The appendix is organized around datasets and evaluation, model adaptations,
ensemble implementation, complete results, robustness and ERA5, mathematical
explanation, and reproducibility statements. See [the companion material](supplement/README.md)
for the enlarged dataset gallery, exploratory branches, and detailed records
kept outside the condensed PDF. All numerical artifacts remain bundled.
The primary comparison covers 21 PDE datasets and ERA5, with all nine library
members, all eleven additional baseline entries, and the Selected model,
Inverse error mixture, and Fitted mixture rules on common evaluation cases.
The four additions are Allen Cahn, Cahn Hilliard II, Fisher KPP, and Phase field
crystal. Cahn Hilliard I denotes the previously included definition.
Cavity and Helmholtz remain unnumbered. Prior exclusions remain unchanged.

The primary tables, Elo rankings, class and budget plots, individual model
heatmap, gallery, inventory, abstract, and conclusion have been recomputed or
updated. Error geometry, comparison coverage diagnostics, and direct loss controls
remain explicitly restricted to the original 17 PDE dataset subset.
See `revision/FOUR_DATASET_EXTENSION_20260917.md` for provenance and scope.

The paper uses the supplied official ICLR 2026 anonymous review style, with nine
pages before the bibliography. The style is a drafting template, not a claim
of an ICLR 2026 submission. Some cited work postdates that conference's original
submission deadline. The eventual submission needs the correct venue year and
fresh template verification.

## What changed scientifically

The paper now presents a surrogate library and empirical ensemble fitting study. It
positions the contribution against engineering surrogate ensembles and the
closest functional output benchmark. It distinguishes components inspired by a
paper from faithful reproductions of the complete published model.

The direct fitting diagnostic uses previously inspected predictions and is not
independent confirmation or a new training campaign. Direct convex fitting of
the reported mean relative L2 metric improves on the original squared error
fit by 2.0% across classes and 2.1% across datasets. This control covers all
51 retained five field partitions and is reported separately from the three
main rules.

Earlier experiments that automatically chose among the three rules remain
archived for provenance. They are excluded from the manuscript, its reported
tables, figures, pseudocode, and conclusions.

The original 17 dataset diagnostic subset has data quality and baseline coverage
sensitivity analyses. On the fixed 15 dataset subset excluding the two recovered B8 entries, the
fitted mixture is 2.0% worse than the hindsight best library member under equal
dataset weighting. Ensemble fitting gains against selecting one model remain.
Source audits also identify duplicate M8 and M9 prediction archives on Darcy. Both observations are disclosed.

Per dataset results for the original 17 PDEs, ERA5, and the fresh heat draw remain unchanged. Main aggregates and figures include the four additions. Fitting code excludes a case's evaluation answer from its
weights. The reporting scope was narrowed after inspection of historical errors. This does not erase historical researcher access to evaluation scores.

## Coverage and remaining limitations

There are 22 datasets, each with all nine library entries. ERA5 now includes M8, M9 and nine model mixtures. The latter uses 55 fine training cases, ten fitting
cases, and seven evaluation cases. All twelve ERA5 baseline entries are complete and represent eleven independent fits, plus the separate training mean control. B8 achieves 5.1503% mean relative L2 error on the same seven evaluation inputs. B8 on Heat II and Burgers is included following fresh evaluation of fixed final campaign checkpoints on identified test inputs. All Table 2 methods now have results on all 22 datasets. Its class ratios use the 21 PDE datasets, while dataset ratios and Elo include ERA5. Table 2 removes the coverage column and sorts all methods by Elo, with ratings in the rightmost column. The fitted mixture reduces equal dataset geometric error by 7.5% across all 22 datasets, compared with 7.7% across the 21 PDE datasets alone. Native gallery resolution differs from the ERA5
128 by 256 evaluation grid.

Common evaluation cases do not equalize training, tuning, computation, or total
fine label exposure. The four dataset completion includes missing baseline fits and verified retained predictions. No matched budget training, fine only ensemble,
additional training seed, or prospective family evaluation was performed.
The collection retains related archives and documented data defects. The audit
subset does not certify all retained solvers. ERA5 absolute units and calendar
coordinates remain unverified from the supplied artifacts. Its relative scores
do not establish global physical climate skill.

## Rebuild and verify

Requires `pdflatex`, `bibtex`, `pdfinfo`, `pdftotext`, NumPy, SciPy, Matplotlib,
and openpyxl. All data required for rebuilding are bundled. No cluster access
is needed.

```bash
make data
make all
make check
```

`make data` rebuilds the tables and figures and evaluates already saved
direct relative L2 weights. It also replays the archived automatic selector
for provenance checks, without adding that experiment to the manuscript.
`make check` verifies arithmetic, source identities, template integrity, page
limits, citations, and the fitting CLI integration tests. These are
artifact checks, not independent replication of model training or solvers.

The direct loss fit is preserved separately from evaluation. Optional refitting
requires CVXPY 1.9.2 and Clarabel 0.11.1:

```bash
python3 scripts/review_loss_control.py fit
python3 scripts/review_loss_control.py evaluate
```

Refitting replaces the new control's saved weights in this extracted copy.
The normal paper rebuild only evaluates the included locked weights. The
protocol and solver tolerances are recorded in
`revision/LOSS_CONTROL_PROTOCOL.md` and `data/loss_control/fit.json`.

The original numerical workbook is `data/paper_data.xlsx`. Subset diagnostics
and archived selector results are in `data/review_analysis.json`, with source and fit manifests
beside it. The loss control has separate JSON, NPZ, and per dataset CSV outputs
under `data/loss_control/`. Its original squared error references are replayed
against the historical case errors before reporting a new result.

## Use the ensemble fitting stage on new predictions

`scripts/calibrate_fields.py` implements the stated fitting rules and fixed
weighted prediction. It consumes model predictions, so it does not train the
nine base models from input parameters. Its interface and a runnable example
are in `revision/CALIBRATION_CLI.md`. The script and argument names retain their original spelling for compatibility. In the paper, this stage is called ensemble fitting.

```bash
python3 scripts/calibrate_fields.py fit \
  --calibration calibration.npz --rule fitted --output weights.json
python3 scripts/calibrate_fields.py predict \
  --predictions query_predictions.npz --weights weights.json --output mixed.npz
```

Predictions for the fitting examples have shape cases by models by field dimensions, with
matching fitting targets. Query prediction files need no targets. Model
names and field shapes are checked. The query step applies saved weights and
does not read query answers. The included tests exercise rule replay, shape and
model order checks, complementary predictions, and query target nonaccess.

## Figures and source package

Figure 1 uses ERA5 throughout, labels the emissions input x and fine target y, and shows the actual nine model inverse error mixture. The coarse preview is blurred for illustration, as documented in `data/overview_manifest.json`. Figure 2 shows all 22 datasets without colorbars. Larger appendix panels
have numerical scales. All gallery panels use the viridis color palette. The cavity
panel uses a signed logarithmic vorticity scale for its first training example.
Plot transformations do not alter targets
or accuracy metrics. Figure sources and hashes are bundled.

```bash
python3 scripts/build_package.py
```

This creates `automf_latex_source.zip`, verifies its source manifest, rebuilds
from a clean extraction, and compares generated tables and PDF text. The manuscript
package reproduces ensemble fitting and reporting. Surrogate implementations,
training drivers, and data preparation code are maintained separately in the
benchmark and experiment codebases. Their local locations are documented in
`revision/CONCLUSION_REPRODUCIBILITY_20260916.md`. Provenance
paths and collaboration notes are retained and require a separate anonymization
pass before any submission. The original manuscript preservation check is in
`qa/original_preservation.json`.

## Field comparison figure

Figure 3 shows an actual Heat I evaluation input with all nine surrogate models and the Selected model, Inverse error mixture, and Fitted mixture outputs. Rebuild it with `python3 scripts/build_field_comparison.py`. Bundled arrays and source hashes are in `data/field_example_heat.npz` and `data/field_example_heat_manifest.json`. The script verifies the saved error matrix, disjoint fitting examples, and locked weights before drawing shared color scales. The appendix records the illustrative case selection.

The three main rule names are Selected model, Inverse error mixture, and Fitted mixture. `scripts/rule_labels.py` centralizes table and figure naming, while archived method identifiers are unchanged.
