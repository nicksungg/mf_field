"""Regression tests for `tools/zero_work_resume_scan.py`.

Provenance: handoff r3s4_audit-B2 (`worktrees/r3s4_audit/B2/notes/
handoff_experiment_mechanism_analyzer.md`), sections 3a and 3b.

3a: model-less marker legs (result JSONs carrying `train_seconds` but no
`model` key) made `sorted(by)` compare str against None and abort with a
TypeError at the grouped table. Fixture: two result files -- one WITH `model`,
one WITHOUT -- asserting exit 0 and that both appear in the grouped table,
with the raw `model` field preserved (None) beside the new `model_group` key.

3b item 1: UNDERIVABLE blind-spot coverage is a GATE, not a printed counter --
any UNDERIVABLE leg must fail the scan loudly (after the --out JSON lands).

Run:  pytest tests/test_zero_work_resume_scan.py   (from round3/tools/)
  or: python tests/test_zero_work_resume_scan.py
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE.parent / "zero_work_resume_scan.py"
FIXTURE_ROOT = HERE / "fixtures" / "zero_work_resume"


def run_tool(root, *extra):
    return subprocess.run(
        [sys.executable, str(TOOL), "--root", str(root), *extra],
        capture_output=True, text=True)


def test_model_less_marker_leg_no_typeerror(tmp_path):
    """Handoff 3a: both fixture legs grouped, exit 0, raw `model` untouched."""
    out = tmp_path / "scan.json"
    p = run_tool(FIXTURE_ROOT, "--out", str(out))
    assert p.returncode == 0, f"stderr:\n{p.stderr}"
    assert "TypeError" not in p.stderr
    # both legs appear in the grouped ZERO_WORK table
    assert "fno_demo" in p.stdout, p.stdout       # leg WITH model
    assert "marker_fam" in p.stdout, p.stdout     # model-less leg -> dir name
    legs = json.loads(out.read_text())["legs"]
    assert len(legs) == 2
    by_group = {r["model_group"]: r for r in legs}
    # grouping key added BESIDE the raw field, never replacing it:
    assert by_group["fno_demo"]["model"] == "fno_demo"
    assert by_group["marker_fam"]["model"] is None
    assert all(r["status"] == "ZERO_WORK" for r in legs)


def test_underivable_gate_fails_loudly(tmp_path):
    """Handoff 3b item 1: an UNDERIVABLE leg fails the scan, not a counter."""
    root = tmp_path / "root"
    leg_dir = root / "blind_fam" / "smoke"
    leg_dir.mkdir(parents=True)
    (leg_dir / "blind_e2_s0.json").write_text(json.dumps(
        {"dataset": "ifc_heat", "train_seconds": 3.0}))  # no step metadata
    out = tmp_path / "scan.json"
    p = run_tool(root, "--out", str(out))
    assert p.returncode != 0, "UNDERIVABLE leg must fail the scan"
    assert "UNDERIVABLE gate" in p.stderr, p.stderr
    # census and --out JSON still land before the gate fires (forensics)
    assert "blind_fam" in p.stdout
    assert json.loads(out.read_text())["n_underivable"] == 1


if __name__ == "__main__":
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        test_model_less_marker_leg_no_typeerror(Path(td))
    with tempfile.TemporaryDirectory() as td:
        test_underivable_gate_fails_loudly(Path(td))
    print("OK: both regression tests passed")
