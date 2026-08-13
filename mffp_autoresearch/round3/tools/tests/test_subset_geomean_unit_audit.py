"""Regression tests for the bar-calibration verdict in
`tools/subset_geomean_unit_audit.py`.

Provenance: ADR r3-0008 ("The aggregation defect") and
`docs/HANDOFF_2026-08-12.md` open item 2, step 3. The verdict used to be
`"OK" if sorted(cells) == sorted(panel)` where `panel` is the *declared*
`--panel` CLI argument -- it compared the claim to itself, so the "panel"
subset could never fail. In the round-3 R1-vs-R0 run this inverted the two
verdicts: the declared six-cell panel was blessed `OK` while the bar's true
five-cell calibration set (`adr0004_anchor5`) was flagged
`SUBSET_BAR_MISMATCH`.

The fixed contract, tested here:
  * the calibration panel comes from `--bar-calibration-json` (the anchor
    file's `_panel_geomean.panel`, e.g. `state/anchors_repaired/
    noise_floor.json`) or from an explicit `--bar-panel` list -- never from
    `--panel`;
  * a subset is `OK` iff it equals the bar's calibration set, so the declared
    panel itself CAN fail (the round-3 inversion, replayed below, comes out
    the right way around);
  * with no calibration source the verdict is `UNVERIFIED_BAR_CALIBRATION`
    for every subset -- the check can no longer pass by default.

Surviving mutation for each: revert the verdict line to compare against the
declared panel and test_declared_panel_can_fail + test_unverified_without_source
both go red.

Run:  pytest tests/test_subset_geomean_unit_audit.py   (from round3/tools/)
  or: python tests/test_subset_geomean_unit_audit.py
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE.parent / "subset_geomean_unit_audit.py"

# Six cells: the declared panel is all six, the bar was calibrated on five --
# the exact shape of the round-3 R1-vs-R0 inversion.
CELLS6 = ["a", "b", "c", "d", "e", "f"]
CALIB5 = ["a", "b", "c", "d", "e"]

SKILLS = {
    "arm": {ds: [1.0 + 0.1 * i, 1.1 + 0.1 * i] for i, ds in enumerate(CELLS6)},
    "ref": {ds: [1.2, 1.3] for ds in CELLS6},
}


def run_tool(workdir, *extra):
    skills = workdir / "skills.json"
    skills.write_text(json.dumps(SKILLS))
    out = workdir / "report.json"
    proc = subprocess.run(
        [sys.executable, str(TOOL), "--skills-json", str(skills),
         "--arms", "arm,ref", "--panel", ",".join(CELLS6),
         "--subset", "anchor5=" + ",".join(CALIB5),
         "--bar", "0.5", "--out", str(out), *extra],
        capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    return json.loads(out.read_text())


def verdicts(rep):
    return {nm: e["bar_calibration_verdict"] for nm, e in rep["subsets"].items()}


def test_declared_panel_can_fail():
    """The round-3 inversion, replayed: declared panel6 vs 5-cell calibration.
    panel must be SUBSET_BAR_MISMATCH and anchor5 must be OK -- the exact
    opposite of what the tautological check produced."""
    with tempfile.TemporaryDirectory() as td:
        wd = Path(td)
        calib = wd / "noise_floor.json"
        calib.write_text(json.dumps({"_panel_geomean": {"panel": CALIB5}}))
        rep = run_tool(wd, "--bar-calibration-json", str(calib))
        assert verdicts(rep) == {"panel": "SUBSET_BAR_MISMATCH", "anchor5": "OK"}
        assert sorted(rep["bar_calibration_panel"]) == sorted(CALIB5)


def test_explicit_bar_panel_equivalent():
    with tempfile.TemporaryDirectory() as td:
        rep = run_tool(Path(td), "--bar-panel", ",".join(CALIB5))
        assert verdicts(rep) == {"panel": "SUBSET_BAR_MISMATCH", "anchor5": "OK"}


def test_unverified_without_source():
    """No calibration source -> no subset may read OK; the check must not be
    able to pass by default."""
    with tempfile.TemporaryDirectory() as td:
        rep = run_tool(Path(td))
        assert set(verdicts(rep).values()) == {"UNVERIFIED_BAR_CALIBRATION"}


def test_ok_when_declared_equals_calibration():
    """Sanity: when the declared panel IS the calibration set, it reads OK and
    a differing subset mismatches."""
    with tempfile.TemporaryDirectory() as td:
        rep = run_tool(Path(td), "--bar-panel", ",".join(CELLS6))
        assert verdicts(rep) == {"panel": "OK", "anchor5": "SUBSET_BAR_MISMATCH"}


if __name__ == "__main__":
    raise SystemExit(subprocess.call(
        [sys.executable, "-m", "pytest", "-q", __file__]))
