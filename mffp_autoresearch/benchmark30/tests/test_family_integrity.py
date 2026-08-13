"""A4: vendored certified family byte-identity guard (spec D2).

The campaign runs the round-3 certified family `models_r3/r3s2_route` at
commit `e606a4f` (the commit the certified jobs ran at).  The vendored copy
must be byte-identical to that commit for EVERY file except `upsample.py`,
which may differ only by append-only growth of the three convention set
literals (seam (b), applied in A5).

If this guard fails, the "certified" label no longer applies — see spec D2.
"""
from __future__ import annotations

import ast
import hashlib
import json
import subprocess
from pathlib import Path

import pytest

CAMPAIGN = Path(__file__).resolve().parents[1]
VENDORED = CAMPAIGN / "family/r3s2_route_b30"
B2_WORKTREE = Path("/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/round3/worktrees/r3s2_field_reach/B2")
CERT_COMMIT = "e606a4f"
FAMILY_REL = "models_r3/r3s2_route"
IDENTITY_FILE = CAMPAIGN / "state/family_byte_identity.json"

APPEND_ONLY_SETS = {"PERIODIC_NODE_DATASETS", "DIRICHLET_NODE_DATASETS",
                    "LEGACY_CELL_DATASETS"}


def _cert_files() -> dict:
    """relpath -> content bytes at the certified commit (from the git object)."""
    ls = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", CERT_COMMIT, FAMILY_REL],
        capture_output=True, text=True, check=True, cwd=B2_WORKTREE).stdout.split()
    out = {}
    for path in ls:
        blob = subprocess.run(["git", "show", f"{CERT_COMMIT}:{path}"],
                              capture_output=True, check=True, cwd=B2_WORKTREE).stdout
        out[str(Path(path).relative_to(FAMILY_REL))] = blob
    return out


@pytest.fixture(scope="module")
def cert():
    return _cert_files()


def test_vendored_family_exists():
    assert (VENDORED / "smoke_eval.py").exists(), f"vendored family missing at {VENDORED}"


def test_every_file_byte_identical_except_upsample(cert):
    diffs, missing = [], []
    for rel, blob in cert.items():
        p = VENDORED / rel
        if not p.exists():
            missing.append(rel)
        elif rel != "upsample.py" and p.read_bytes() != blob:
            diffs.append(rel)
    assert not missing, f"files missing from vendored family: {missing}"
    assert not diffs, f"files differ from certified commit {CERT_COMMIT}: {diffs}"
    extras = {str(p.relative_to(VENDORED)) for p in VENDORED.rglob("*")
              if p.is_file() and not p.name.endswith(".pyc")} - set(cert)
    assert not extras, f"files added to vendored family (not permitted by D2): {extras}"


def _top_level_index(src: str) -> dict:
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


def _node_name(node):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return node.name
    if isinstance(node, ast.Assign) and len(node.targets) == 1 \
            and isinstance(node.targets[0], ast.Name):
        return node.targets[0].id
    return None


def _module_sequence(src: str, masked: set) -> list:
    seq = []
    for node in ast.parse(src).body:
        n = _node_name(node)
        seq.append(f"<seam:{n}>" if n in masked else ast.dump(node))
    return seq


def test_upsample_differs_only_in_registry_sets(cert):
    """r1 fix F9: full module-sequence comparison — a subscript assignment
    like CONVENTION_BY_FN[...] = ... appended after the checked defs would be
    a NEW top-level node and now fails; only the three set literals may vary,
    append-only, with the exact ADR additions pinned by test_registry."""
    orig = cert["upsample.py"].decode()
    vend = (VENDORED / "upsample.py").read_text()
    assert _module_sequence(vend, APPEND_ONLY_SETS) == \
        _module_sequence(orig, APPEND_ONLY_SETS), (
        "upsample.py module structure differs outside the three registry sets "
        "(spec D2 — no other statement may be added, removed or reordered)")
    for name in APPEND_ONLY_SETS:
        o, v = _set_literal(orig, name), _set_literal(vend, name)
        assert o <= v, f"{name}: vendored family dropped/changed entries {o - v}"


def test_identity_record_matches_reality(cert):
    assert IDENTITY_FILE.exists(), f"missing {IDENTITY_FILE}"
    rec = json.load(open(IDENTITY_FILE))
    assert rec["cert_commit"].startswith(CERT_COMMIT)
    for rel, blob in cert.items():
        assert rec["files"][rel] == hashlib.sha256(blob).hexdigest(), \
            f"identity record stale for {rel}"


def test_family_eval_dir_materialized_byte_identical():
    """G3-fix follow-up: the frozen family hashes EVAL_DIR/nrmse.py for
    provenance at result-write time (smoke_eval.py:1912); at the vendored
    depth EVAL_DIR is <campaign>/mffp_autoresearch/round2/eval, so that file
    must EXIST there and be byte-identical to the vendored eval/nrmse.py
    (itself byte-identical to round-2's, by test_nrmse_byte_identical)."""
    materialized = CAMPAIGN / "mffp_autoresearch/round2/eval/nrmse.py"
    assert materialized.exists(), "materialized EVAL_DIR/nrmse.py missing"
    assert materialized.read_bytes() == (CAMPAIGN / "eval/nrmse.py").read_bytes()
