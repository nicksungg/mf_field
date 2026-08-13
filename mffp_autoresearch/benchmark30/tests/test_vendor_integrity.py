"""A3: vendored-scorer byte-identity guard (spec D3).

The campaign scorer is a pinned copy of the round-2 eval layer with exactly
three named seams (D3): (a) baseline path, (b) registry appends [A5],
(c) config/data-root resolution.  This guard proves the metric path is
UNCHANGED: every top-level definition is ast-identical to the `83a547e`
original except the explicitly whitelisted seam functions, and the registry
sets may only ever GROW (append-only).

Failure here means someone changed scoring semantics under the certified
label — see docs/spec.md D3 and eval/SEAM_MANIFEST.md for the recorded
decision before touching anything.
"""
from __future__ import annotations

import ast
import subprocess
from pathlib import Path

import pytest

CAMPAIGN = Path(__file__).resolve().parents[1]
REPO = Path("/resnick/groups/Hippo/ezeng/mf_field")
BASE = "83a547e"
ORIGIN = "mffp_autoresearch/round2/eval"

# seam whitelist: the ONLY definitions allowed to differ from the original
SEAMED = {
    "score_panel.py": {"_load_baselines"},            # seam (a)
    "panel_data.py": {"load_config", "load_split"},   # seam (c)
    "nrmse.py": set(),                                # zero-delta dependency copy
}
# module-level set constants that may GROW (seam (b), A5) but never shrink/change
APPEND_ONLY_SETS = {"PERIODIC_NODE_DATASETS", "DIRICHLET_NODE_DATASETS",
                    "LEGACY_CELL_DATASETS"}


def _original(fname: str) -> str:
    return subprocess.run(
        ["git", "show", f"{BASE}:{ORIGIN}/{fname}"],
        capture_output=True, text=True, check=True, cwd=REPO,
    ).stdout


def _top_level_index(src: str) -> dict:
    """name -> ast dump for every top-level def/class/assignment."""
    out = {}
    for node in ast.parse(src).body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out[node.name] = ast.dump(node)
        elif isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name):
            out[node.targets[0].id] = ast.dump(node)
    return out


def _set_literal(src: str, name: str) -> set:
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name) \
                and node.targets[0].id == name:
            return set(ast.literal_eval(node.value))
    raise AssertionError(f"{name} not found")


@pytest.mark.parametrize("fname", sorted(SEAMED))
def test_vendored_file_exists(fname):
    assert (CAMPAIGN / "eval" / fname).exists(), f"vendored eval/{fname} missing"


def test_nrmse_byte_identical():
    assert (CAMPAIGN / "eval/nrmse.py").read_text() == _original("nrmse.py")


@pytest.mark.parametrize("fname", ["score_panel.py", "panel_data.py"])
def test_only_seamed_defs_differ(fname):
    orig = _top_level_index(_original(fname))
    vend = _top_level_index((CAMPAIGN / "eval" / fname).read_text())
    allowed = SEAMED[fname] | (APPEND_ONLY_SETS if fname == "panel_data.py" else set())
    # nothing deleted
    missing = set(orig) - set(vend)
    assert not missing, f"{fname}: definitions deleted from vendored copy: {missing}"
    # nothing changed outside the seam whitelist
    changed = {n for n in orig if vend[n] != orig[n]}
    illegal = changed - allowed
    assert not illegal, (
        f"{fname}: definitions differ outside the declared seams: {illegal} "
        f"(spec D3 — the metric path must stay byte-identical)")
    # additions must be seam helpers, declared in the manifest
    added = set(vend) - set(orig)
    manifest = (CAMPAIGN / "eval/SEAM_MANIFEST.md").read_text()
    undeclared = {n for n in added if n not in manifest}
    assert not undeclared, f"{fname}: undeclared additions {undeclared}"


def test_registry_sets_append_only():
    orig_src = _original("panel_data.py")
    vend_src = (CAMPAIGN / "eval/panel_data.py").read_text()
    for name in APPEND_ONLY_SETS:
        o, v = _set_literal(orig_src, name), _set_literal(vend_src, name)
        assert o <= v, f"{name}: vendored copy dropped/changed original entries {o - v}"


def test_seam_manifest_names_every_seam():
    manifest = (CAMPAIGN / "eval/SEAM_MANIFEST.md").read_text()
    for token in ("_load_baselines", "load_config", "load_split",
                  "seam (a)", "seam (b)", "seam (c)"):
        assert token in manifest, f"SEAM_MANIFEST.md missing {token!r}"
