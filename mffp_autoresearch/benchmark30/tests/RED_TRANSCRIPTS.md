# Red-phase transcripts (TDD evidence, one entry per task)

## A1 — tests/test_config.py

Command: `.venv/bin/python -m pytest tests/test_config.py -x -q` (before config.yaml existed)

```
tests/test_config.py:28: AssertionError
ERROR tests/test_config.py::test_thirty_unique_datasets - AssertionError: cam...
1 error in 0.33s
```

Failure reason: `campaign config missing at .../config.yaml` — the fixture asserts the file exists.
Green after writing config.yaml: `8 passed in 0.34s`.

## A2 — tests/test_manifest.py

Command: `.venv/bin/python -m pytest tests/test_manifest.py -x -q` (before staging/manifest.py existed)

```
ERROR tests/test_manifest.py
Interrupted: 1 error during collection   # ModuleNotFoundError: staging.manifest
1 error in 0.70s
```

Green after implementing staging/manifest.py: `12 passed` (one intermediate failure was a fixture-arithmetic error in the TEST — expectation 32 vs the fixture's actual 16 cells — fixed in the test, implementation unchanged).

## A3 — tests/test_vendor_integrity.py

Command: `.venv/bin/python -m pytest tests/test_vendor_integrity.py -q` (before eval/ vendoring)

```
FAILED tests/test_vendor_integrity.py::test_registry_sets_append_only - FileN...
FAILED tests/test_vendor_integrity.py::test_seam_manifest_names_every_seam - ...
8 failed in 0.41s
```

Green after vendoring + seams: `20 passed` (one intermediate failure was a test bug — ast.Name attribute is `.id` not `.name` — fixed in the test).

## A4 — tests/test_family_integrity.py

The intended pre-implementation red run mis-executed (wrong cwd, "no tests ran") — recorded honestly here.
In its place, the guard was MUTATION-VERIFIED after implementation:

```
# appended "# tampered" to family/r3s2_route_b30/front_end.py and hid state/family_byte_identity.json
FAILED tests/test_family_integrity.py::test_every_file_byte_identical_except_upsample
FAILED tests/test_family_integrity.py::test_identity_record_matches_reality
2 failed, 2 passed in 0.90s
```

Restored → `24 passed`.

## A5 — tests/test_registry.py

Command: `.venv/bin/python -m pytest tests/test_registry.py -q` (before the registry appends)

```
FAILED tests/test_registry.py::test_every_2d_campaign_dataset_classified_in_both
FAILED tests/test_registry.py::test_dirichlet_node_endpoint_mapping
FAILED tests/test_registry.py::test_campaign_classification_counts
3 failed, 6 passed in 1.74s
```

Green after appends + ADR: full suite passes (the dirichlet synthetic test was corrected mid-red to assert variant E's ACTUAL certified contract — exact at shared nodes + linear inside the LF span, clamped edge band — instead of an over-strong everywhere-linear property the frozen code never had).

## A6 — tests/test_preflight.py

Command: `.venv/bin/python -m pytest tests/test_preflight.py -q` (before staging/preflight.py existed)

```
Interrupted: 1 error during collection   # ModuleNotFoundError: staging.preflight
1 error in 0.49s
```

Green after implementation: full suite passes (one intermediate red was a test-expectation bug — `_verify` raises SystemExit, which `pytest.raises(Exception)` does not catch — fixed in the test; the leak WAS detected by the audit both times).

## A7 — tests/test_copylf_baselines.py

Command: `.venv/bin/python -m pytest tests/test_copylf_baselines.py -q` (before eval/make_copylf_baselines_b30.py existed)

```
no tests ran in 0.02s   # collection error: module absent
```

Green after implementation: full suite passes.
Key anchor: freshly computed sharp__cahn_hilliard copy-LF equals the round-2 committed value to 1e-9 — the vendored construction IS the round-2 construction.
(One intermediate red: fixture dict lacked grid_shape_by_fid, a loader-provided key — fixed in the fixture.)

## A8 — tests/test_launch.py

Command: `.venv/bin/python -m pytest tests/test_launch.py -q` (before slurm/launch.py existed)

```
no tests ran in 0.07s   # collection error: module absent
```

Green after implementation: `49 passed` (one intermediate red was a test-helper bug — nested tmp state dirs need mkdir(parents=True)).

## A9 — tests/test_aggregate.py

Command: `.venv/bin/python -m pytest tests/test_aggregate.py -q` (before aggregate/collect.py existed)

```
1 error in 0.43s   # collection error: module absent
```

Green after implementation: `55 passed`.
Key pin: the non-symmetric fixture proves the headline uses per-seed panel geomeans then mean/[min,max] — numerically distinct on this fixture from the seed-averaged-then-geomean order, which the test computes and asserts differs.
(One intermediate red: a leftover expect={"family": None} placeholder in the validator call — fixed to validate against the filename prefix.)

## post-campaign: ops table smoke contamination (test_ops_table_extracted_from_family_results, e2 fixture)

Production red transcript (before the fix, first full collect at rev-eac7b48e):
`leaderboard.json ops.mf_fno_transfer_film.allen_cahn_generated.s0.train_seconds == 2.66`
while s1/s2 showed 77.4/76.6 — every seed-0 ops entry carried the 2-epoch smoke
run's numbers because `_load_ops` had no epochs filter and `*_e2_s0.json` sorts
after `*_e200_s0.json` ('0' < '_'), overwriting it. Scientific tables were
unaffected (`load_scores` already filtered by epochs). Fix: `_load_ops` takes
`expected_epochs` and skips non-matching files; the extended test plants the
e2 file and asserts the e200 value survives.
