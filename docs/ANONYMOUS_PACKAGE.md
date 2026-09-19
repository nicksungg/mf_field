# Anonymous review package

## Two files

- `AutoMF_Anonymous_Review.zip` includes model and generator source, the three ensemble rules, raw text results, the main analysis summaries, figures, the animated overview and a small CPU example. It can run the demo and recompute aggregate ratios and Elo without the companion.
- `AutoMF_Anonymous_Data.zip` contains the remaining numerical arrays: the dataset archives, campaign inputs and saved predictions, and two larger baseline replay arrays. This is a separate, deduplicated companion. It is needed for retraining or full numerical replay.

The code does not contact a named source repository or require Git LFS. Obtain both files through the review submission's anonymized attachments or links. This package does not embed a public download endpoint.

## Import data

Place the companion beside the extracted `AutoMF_Anonymous` directory, then run from that directory:

```bash
python scripts/import_data.py --archive ../AutoMF_Anonymous_Data.zip --group analysis
python scripts/reproduce_results.py --full
```

The first command imports only the two analysis arrays. Full replay also needs `requirements-analysis.txt`. To restore all datasets and prediction archives instead:

```bash
python scripts/import_data.py --archive ../AutoMF_Anonymous_Data.zip
python scripts/verify_release.py --full
```

The importer checks each object's SHA256 before installing it. Duplicate byte-identical files share one object in the companion, but are restored to every required relative path. Allow approximately 12 GB for the complete extracted package in addition to the companion ZIP. New experiment outputs require additional space.

## Scope and metadata

This copy excludes manuscript source and PDF files, Git history and remotes, credentials, private development plans and operational scheduling records. Author-specific filesystem prefixes and computer identifiers in provenance records have been normalized. Source-file checksums that refer to edited metadata are refreshed so integrity checks remain usable. Numerical NPZ archives are preserved byte for byte. Normalizing provenance paths does not change which experimental run or data version was used.

Scholarly references, software authorship notices and third-party licenses are retained, including ordinary third-person citations to relevant prior work. They attribute existing work; they do not identify the submission's author list. Not all original checkpoints are included. See [reproduction scope](REPRODUCIBILITY.md) and [attribution](THIRD_PARTY_NOTICES.md).
