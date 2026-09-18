# Narrative and style revision, 16 September 2026

The abstract is preserved exactly, including the requested 19 dataset scope and
final comparison sentence. The original manuscript directory is untouched. The
preceding revision is saved outside this package as
`../automf_revision_backups_20260916/before_full_story_revision.zip`.

The style reference is the supplied `overleaf_interpretability_reframed (1).zip`.
The revision follows its explanatory sequence: a concrete scientific problem,
the choice that motivates an experiment, the evidence from that experiment, and
the conclusion that the evidence supports. It does not import the reference
paper's results or claims of architectural novelty.

The introduction now connects parameter to field prediction to the practical
problem of choosing a surrogate. It explains calibration and the three rules
before presenting the contribution. The background situates the workflow within
engineering surrogate ensembles, automated libraries and field prediction.
The method first defines the prediction task, explains why the library contains
different uses of coarse information, and then introduces the weighting and
selection equations.

The results follow the questions needed to interpret the workflow: which models
provide useful predictions, whether calibration benefits from combining them,
how much simple weighting achieves, and what automatic rule selection adds.
Coverage checks, the fitting loss control and new heat inputs then test the
limits of those findings. ERA5 illustrates the distinction between an available
ensemble gain and a calibration procedure that finds it reliably. The discussion
connects these findings to the remaining information and resource comparisons.

The appendix introduces technical details through the question they address.
Model descriptions lead with rationale before implementation, supplementary
analyses explain their purpose before the numerical record, and captions define
the comparison shown. Related sentences are joined into developed paragraphs.
Technical equations, numerical artifacts and original study limitations are
preserved. Calibration selection remains distinct from choosing the best model
after evaluation, and retrospective analyses remain identified as such.

Verification checks the exact abstract, the unchanged bibliography and display
equations, hashes of the 801 data, table and figure artifacts, and the original
manuscript manifest. The ICLR template remains unchanged and the main text fits
within nine pages. The companion source package is verified through a clean
extraction and rebuild.
