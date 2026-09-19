# Numerical analysis archive

This directory contains data and scripts for reproducing the reported results. It contains no manuscript, submission template or manuscript revision notes.

Start from the repository root:

```bash
python scripts/reproduce_results.py
```

For a full replay from per-case records, see [reproduction instructions](../docs/REPRODUCIBILITY.md). The command works in a new `outputs/` workspace, preserving these reference inputs.

- `data/table2_ranking.json`: complete 22-dataset comparison and Elo.
- `data/`: per-case archives, summaries, weights, fitting partitions and figure source fields.
- `scripts/`: frozen analysis, validation and plotting routines.
- `protocols/`: experiment specifications required to verify the archived fit hashes.

Historical filenames, model identifiers and source paths remain in provenance records. Files named `paper_*` contain numerical reporting scope or summaries, not manuscript text. Exploratory controls are archived here; the public ensemble interface exposes the three principal rules only.
