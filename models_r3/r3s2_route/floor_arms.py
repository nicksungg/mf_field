# == RE-VENDORED (round-3 card r3s2_field_reach-B2) ==========================
# SOURCE : round3/worktrees/r3s2_field_reach/B1/models_r3/r3s2_stack_ic/floor_arms.py
# COMMIT : d5069a74bb63da837b89b16508ae25a2164780cc  (tip of branch
#          round3/exp-r3s2_field_reach-B1; recipe.env._vendor_source. The
#          recipe's `base_commit` 76d15c2d is a TRUNK commit that carries NO
#          models_r3/ tree at all -- see notes/handoff_experiment_builder.md.)
# SHA256 : cc2c2ed0a290bce11cc8f6dac65025e050b5eb790a62b82964e1e1e65e0abefc
# STATUS : byte-identical below this header.
#          Copied, never imported: score_panel.py::code_hash hashes only
#          family_dir/**/*.py, so logic outside the family dir is invisible to
#          the eval cache key.
# ROLE   : declared reuse role (a), round-2 program 5.10a -- the DC-lineage
#          corrector stays a FROZEN test-time sub-component behind a
#          condition->pseudo-LF front end. The B2 contribution is the ROUTE
#          SWITCH + budget accountant, not this code.
# ============================================================================
"""The MANDATORY training-free floor arms reported next to every cell.

Card part 3: *"Mandatory floor arms on every cell: `nn_condition`, `train_mean`,
`zero` from `state/anchors_repaired/floors.json`, plus `affine_on_hf_train` on
both ifc cells (round-3 affine-floor rule)."*

These are CERTIFIED, already-computed numbers — round 3's program.md §2 makes
them the comparand, not something a model card re-derives. This module reads
them (read-only) and hands them to the diag, recording the file it read, that
file's sha256, and the definition string, so the analyzer never has to guess
which vintage of the floors a cell was read against.

`affine_on_hf_train` lives in `state/anchors/launch_anchors.json`
(`ifc_floors_repaired`), not in `floors.json`; program.md §2's affine-floor rule
makes it mandatory on ifc cells only, and it is deliberately NOT part of
`best_floor`.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

FLOORS_REL = "mffp_autoresearch/round3/state/anchors_repaired/floors.json"
ANCHORS_REL = "mffp_autoresearch/round3/state/anchors/launch_anchors.json"
FLOOR_KEYS = ("nn_condition", "train_mean", "zero")


class FloorArmsError(RuntimeError):
    """A mandatory floor arm could not be reported for this cell."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _pick(roots, rel: str):
    for r in roots:
        p = Path(r) / rel
        if p.exists():
            return p
    return None


def collect(dataset: str, roots, required: str) -> dict:
    """Assemble the floor-arm block for `dataset`.

    `roots` is an ordered list of candidate repo roots (worktree first, then the
    main checkout). `required` is the recipe's `R3S2_FLOOR_ARMS` csv; every name
    in it must be either reported or explicitly marked not-applicable.
    """
    want = [s.strip() for s in str(required).split(",") if s.strip()]
    fp = _pick(roots, FLOORS_REL)
    if fp is None:
        raise FloorArmsError(
            f"floors file not found under any of {[str(r) for r in roots]}/{FLOORS_REL}")
    floors = json.loads(fp.read_text())
    if dataset not in floors:
        raise FloorArmsError(
            f"{dataset!r} has no entry in {fp}: the mandatory floor arms "
            f"{FLOOR_KEYS} cannot be reported for this cell")
    entry = floors[dataset]

    out = {
        "_source": {
            "floors_file": str(fp), "floors_sha256": _sha256(fp),
            "certified_utc": floors.get("_certified_utc"),
            "nrmse_def_hash": floors.get("_nrmse_def_hash"),
            "copylf_def_hash": floors.get("_copylf_def_hash"),
            "split": floors.get("_split"),
        },
        "reference": entry.get("reference"),
        "requested": want,
    }
    for k in FLOOR_KEYS:
        if k in want:
            if k not in entry:
                raise FloorArmsError(f"{dataset}: floors.json has no {k!r} arm")
            out[k] = entry[k]

    if "affine_on_hf_train" in want:
        ap = _pick(roots, ANCHORS_REL)
        aff = None
        if ap is not None:
            anchors = json.loads(ap.read_text())
            aff = (anchors.get("ifc_floors_repaired", {}) or {}).get(dataset)
            out["_source"]["anchors_file"] = str(ap)
            out["_source"]["anchors_sha256"] = _sha256(ap)
        if aff is not None and "affine_on_hf_train" in aff:
            out["affine_on_hf_train"] = aff["affine_on_hf_train"]
        else:
            # program.md 2's affine-floor rule is scoped to the two ifc cells;
            # elsewhere the arm is not defined and says so rather than vanishing.
            out["affine_on_hf_train"] = {
                "applicable": False,
                "reason": (f"the round-3 affine-floor rule (program.md 2) publishes "
                           f"affine_on_hf_train for the ifc cells only; "
                           f"{dataset} has no certified entry in "
                           f"launch_anchors.json::ifc_floors_repaired"),
            }
    unknown = [w for w in want if w not in set(FLOOR_KEYS) | {"affine_on_hf_train"}]
    if unknown:
        raise FloorArmsError(f"R3S2_FLOOR_ARMS names unknown arms {unknown}")
    return out


def beat_table(model_nrmse: float, floors: dict) -> dict:
    """`{arm: model_nrmse - floor_nrmse}` — negative means the model beats it."""
    out = {}
    for k in list(FLOOR_KEYS) + ["affine_on_hf_train"]:
        e = floors.get(k)
        if isinstance(e, dict) and isinstance(e.get("nrmse"), (int, float)):
            out[k] = {"floor_nrmse": float(e["nrmse"]),
                      "model_minus_floor_nrmse": float(model_nrmse) - float(e["nrmse"]),
                      "model_beats_floor": bool(float(model_nrmse) < float(e["nrmse"]))}
    return out
