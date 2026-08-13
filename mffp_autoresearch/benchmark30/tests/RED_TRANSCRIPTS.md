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
