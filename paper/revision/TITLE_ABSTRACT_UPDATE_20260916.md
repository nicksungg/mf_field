# Title and abstract revision, 16 September 2026

The current title is **AutoML: Automated Ensembles for Multifidelity Field Prediction**.
The method name, method section heading, PDF metadata and README use AutoML.

The abstract now follows the explanatory structure of the supplied manuscript in
`overleaf_interpretability_reframed (1).zip`: physical motivation, a concrete workflow,
an explicit comparison and quantitative findings. It motivates multifidelity learning
with temperature and velocity fields. Calibration is defined through additional
parameter inputs and their known fine solution fields, reserved from surrogate
training. The text explains selecting a single model and fitting averaging weights
before reporting either comparison. It uses datasets in place of settings and states
coverage across seven PDE classes and climate emulation. The fitted mixture is compared
against the individual model with the lowest error on the same five input and fine
solution pairs. The reductions are 12.7% under PDE class aggregation and 8.5% under
dataset aggregation. The aggregation definitions remain in the evaluation section.
The closing sentences about the hindsight best model and inverse weighting were
removed from the abstract. The reference manuscript supplied a writing style, not
experimental claims or numerical results.

The specific heat result, auxiliary loss analysis and closing limitations sentence
were removed from the abstract. Their substantive discussion remains in the paper.
The 19 setting roster, 18 setting common comparison and all numerical results are
unchanged. The original manuscript is untouched. The prior source package is saved
outside this directory as `../automf_revision_backups_20260916/before_title_abstract_edit.zip`.
The package immediately before the field context clarification is saved as
`../automf_revision_backups_20260916/before_field_context_abstract_edit.zip`.
The package before the reference style revision is saved as
`../automf_revision_backups_20260916/before_reference_style_abstract_edit.zip`.

The final abstract sentence now directly identifies the comparator as the individual
model with the lowest error on the same five calibration examples. The percentages
are not relative to the individual model chosen retrospectively using evaluation
answers. The preceding sentence was shortened to avoid repeating this comparison.
The package before this clarification is saved as
`../automf_revision_backups_20260916/before_abstract_comparator_edit.zip`.

The comparator was subsequently shortened to "the individual model with the lowest
calibration error". This avoids repeating the five examples while retaining the
distinction from choosing the individual model using evaluation answers. The prior
package is saved as `../automf_revision_backups_20260916/before_short_calibration_comparator.zip`.

The abstract now gives 19 as the study dataset count without repeating the numeric
PDE subset count. It scopes the model diversity and mixture comparisons to the PDE
evaluation in prose. The preceding sentence defines the individual reference using
the same five calibration examples, allowing the last sentence to use the requested
"lowest error individual model" wording and "when averaged across" aggregation
phrasing. The 12.7% and 8.5% results still describe the PDE comparison and have not
been recomputed to include climate emulation. All tables and evaluation scope
definitions are unchanged. The prior package is saved as
`../automf_revision_backups_20260916/before_19_dataset_abstract_edit.zip`.
