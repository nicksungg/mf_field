# Reproduction scope

## What is included

The release covers the current paper's **22 datasets**, **M1 through M9**, **B1 through B11**, the **B12 nearest-neighbour** and **B13 training-mean** controls, and the three principal ensemble rules. Dataset and model identifiers in `configs/` are authoritative. Archival source code may also mention exploratory datasets and controls; these do not expand the paper roster.

- Training and test arrays at every available fidelity, together with the separately prepared ERA5 training and reserved-query splits.
- Original generator and preparation source, parameter configurations and the available convergence/reference checks. Imported MFRNP and ERA5 datasets are supplied as archives; this release does not include the original climate simulators or claim to regenerate ECMWF reanalysis from first principles.
- Model, optimizer, checkpoint-writing, data-adapter and prediction-export code. Later ERA5 and four-dataset campaigns preserve their distinct adaptations.
- Published per-case errors, ensemble fitting/evaluation partitions, saved weights, sufficient error Gram matrices, and saved field predictions where archived.
- Scripts and frozen inputs to rebuild the reported tables, figures and manuscript.

The ZIP does **not** include every original optimizer or trained model checkpoint. It includes code for retraining and the saved outputs needed to replay the results. Network retraining is not a bitwise replication guarantee: GPU type, framework version, numerical precision and checkpoint selection can matter. The paper uses a single final training seed per recipe; its three fitting partitions are not independent training-seed repeats.

## Numerical replay

`python scripts/reproduce_paper.py` reruns the original frozen analysis. The supplied `paper/data/paper_primary_summary.json` and `paper/data/table2_ranking.json` contain the main aggregate values. Detailed baseline and individual errors are under `paper/data/` and in the spreadsheet `paper/data/paper_data.xlsx`. `paper/scripts/verify_paper.py` also checks numerical and structural consistency after a full PDF rebuild.

For the original 17 PDE tasks, `paper/data/review_grams/` stores each case's matrix of normalized error inner products. This is sufficient to recompute any fixed convex mixture's relative squared L2 error without loading full spatial predictions. Four additional PDE tasks and ERA5 have separate completed campaign inputs and outputs. The primary aggregate covers all 22 datasets; the PDE-class aggregate excludes climate and weights the seven PDE classes equally.

## Provenance and versions

The source data versions used by the paper are preserved. In particular, Poisson I and Cavity use the corrected generated archives, while Poisson II is the imported archive used in the reported experiments. Regenerated alternatives from a later campaign are not substituted for it. Known task properties, such as synthetic coarse pressure fields and incomplete initial-condition information in Cahn Hilliard I, remain described in the manuscript and source metadata.

The paper compares errors on corresponding evaluation cases. Historical implementations have different training, validation, optimization and compute settings. The generic training launcher defaults are convenient starting values; the per-run JSON records and frozen campaign configurations are the authority for replicating a specific reported run. Do not infer equal computational budgets from a shared dataset name.

Some identities are deliberately preserved: B9/B10 share inspected transfer code, and M8/M9 have identical archived Darcy predictions. Historical GP exports can reconstruct the fitted estimator rather than load an original serialized estimator. The release makes these limitations inspectable.

## Release verification

`release_manifest.json` lists every distributed file's size and SHA256. Run `python scripts/verify_release.py` immediately after extraction or a Git LFS checkout. Rebuilding figures or metadata can legitimately alter generated file hashes; use a fresh extraction when checking the original bundle. Packaging changes concern paths, imports, documentation and release tooling, not historical field values or scores. Full retraining of the benchmark was not repeated during packaging.
