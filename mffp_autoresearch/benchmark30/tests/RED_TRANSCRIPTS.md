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
