# Verification records

`release_manifest.json` at the repository root is the current file-integrity authority. `readme_workflow.json` records checks of the code-first README, CPU example, comparison exporter and graphical overview.

The other records document validation of the original release packaging. They preserve historical paths, including paths to manuscript artifacts that are no longer distributed here. They are provenance reports rather than commands to execute or claims that those removed files remain in the current tree.

To verify current files after a full LFS checkout, run `python scripts/verify_release.py`. To check numerical results, follow [reproduction instructions](../docs/REPRODUCIBILITY.md).
