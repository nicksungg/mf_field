# Baselines for the four additional PDE datasets

This archive records the completed baseline comparison for Allen Cahn, Cahn Hilliard II, Fisher KPP and Phase field crystal. The common evaluation, fitting roles, reused predictions and final comparisons are recorded in `results/`, `COVERAGE.json`, `REUSE.json`, `TASKS.json` and the frozen configurations.

See [the training guide](../../docs/TRAINING.md#four-added-pde-datasets) to prepare a new workspace and run the released baseline workers. The archive's own reference outputs must not be overwritten. Cluster-specific launch and scheduling records are not required for local execution.

Historical training-file hashes are not available for every reused paper baseline. Evaluation correspondence is checked using available source-file hashes or saved target rows. The two transfer labels share an executable recipe; reused outputs do not represent independent additional fits. Available fine data and compute settings differ across implementations, as recorded in the result metadata.
