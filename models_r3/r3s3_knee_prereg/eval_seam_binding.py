"""`R3S3B3_DATA_BINDING_ASSERT` — tie `copylf_baselines.json` to `floors.json`.

Card `r3s3_lf_value-B1` part 3, verbatim, listing this among the blocking
pre-flights:

    a data-binding assertion tying `copylf_baselines.json` to `floors.json`
    references.

WHY THE CARD ASKS FOR IT (`recipe.env._base_commit_rationale`, verbatim):

    round3-substrate (8aae33a) is STALE for this card: its
    round2/eval/copylf_baselines.json predates the ac trim, the pfc
    crystalline-box swap and the ifc_heat promotion, and it has no ifc_heat
    entry at all (score_panel.py would raise ScoreContractError). [...]
    R3S3B3_DATA_BINDING_ASSERT is the check that decides it either way.

So this is not decoration: it is the mechanism by which a leg launched from a
stale substrate FAILS LOUDLY instead of scoring against a superseded
denominator. Three independent things must agree, and each is checked:

1. **The eval layer that computes the skill denominator is the one the
   baselines were built under.** `copylf_baselines.json._copylf_def_hash` ==
   `eval/panel_data.py::COPYLF_DEF_HASH` (read-only import). `score_panel.py`
   checks this too; it is re-checked here so a direct `smoke_eval.py`
   invocation cannot bypass it.
2. **The floors were computed under the same eval layer.**
   `floors.json._copylf_def_hash` == the baselines' hash, and
   `floors.json._nrmse_def_hash` == `eval/nrmse.py::NRMSE_DEF_HASH`.
3. **The per-dataset reference is the SAME NUMBER in both files.**
   `copylf_baselines[ds]["test_nrmse"]` == `floors[ds]["reference"]["test_nrmse"]`,
   exact float equality. This is the binding that actually matters: the skill
   this card reports has the baselines' denominator, while every floor/anchor
   the card compares against has the floors file's. If they ever diverge, every
   `E_total` in the card is measured against a mixed denominator.

Verified 2026-08-07 by this builder: all three hold, with exact float equality
on the references, for all 5 scored datasets + `sharp__phase_field_crystal_2d`
+ the 3 guard datasets.

READ-ONLY. Nothing here writes to the eval layer (program.md §5 immutable 3).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def assert_data_binding(dataset: str, eval_dir, floors_json) -> dict:
    eval_dir = Path(eval_dir)
    if str(eval_dir) not in sys.path:
        sys.path.insert(0, str(eval_dir))
    import panel_data                                       # noqa: E402 (read-only)
    import nrmse as nrmse_mod                               # noqa: E402 (read-only)

    baselines_path = eval_dir / "copylf_baselines.json"
    if not baselines_path.exists():
        raise SystemExit(
            f"copylf_baselines.json missing at {baselines_path}; the eval layer cannot "
            "produce a skill denominator (R3S3B3_DATA_BINDING_ASSERT)")
    baselines = json.loads(baselines_path.read_text())

    floors_path = Path(floors_json)
    if not floors_path.exists():
        raise SystemExit(f"floors.json not found at {floors_path} (R3S3B3_FLOORS_JSON)")
    floors = json.loads(floors_path.read_text())

    b_hash = baselines.get("_copylf_def_hash")
    if b_hash != panel_data.COPYLF_DEF_HASH:
        raise SystemExit(
            f"DATA BINDING FAILED: {baselines_path} was built under copylf_def_hash "
            f"{b_hash!r}, but the live eval layer at {eval_dir} is "
            f"{panel_data.COPYLF_DEF_HASH!r} — the reference construction moved; "
            "re-run make_copylf_baselines.py or point at the right substrate")
    f_hash = floors.get("_copylf_def_hash")
    if f_hash != b_hash:
        raise SystemExit(
            f"DATA BINDING FAILED: {floors_path} carries copylf_def_hash {f_hash!r} but "
            f"{baselines_path} carries {b_hash!r} — the floors and the skill denominators "
            "come from different eval layers; refusing to score")
    f_nrmse = floors.get("_nrmse_def_hash")
    if f_nrmse != nrmse_mod.NRMSE_DEF_HASH:
        raise SystemExit(
            f"DATA BINDING FAILED: {floors_path} carries nrmse_def_hash {f_nrmse!r} but "
            f"the live eval layer is {nrmse_mod.NRMSE_DEF_HASH!r}; refusing to score")

    if dataset not in baselines:
        raise SystemExit(
            f"DATA BINDING FAILED: {dataset!r} has no entry in {baselines_path} — a stale "
            "substrate (the round-3 launch substrate predates the ifc_heat promotion); "
            "score_panel.py would raise ScoreContractError on this dataset")
    if dataset not in floors:
        raise SystemExit(f"DATA BINDING FAILED: {dataset!r} has no entry in {floors_path}")

    ref_b = float(baselines[dataset]["test_nrmse"])
    ref_f = float(floors[dataset]["reference"]["test_nrmse"])
    if ref_b != ref_f:
        raise SystemExit(
            f"DATA BINDING FAILED on {dataset}: copylf_baselines test_nrmse {ref_b!r} != "
            f"floors reference test_nrmse {ref_f!r}. The skill this leg reports and the "
            "floors/anchors it is compared against would use different denominators; "
            "refusing to score")

    return {
        "performed": True,
        "eval_dir": str(eval_dir),
        "copylf_baselines_json": str(baselines_path),
        "floors_json": str(floors_path),
        "copylf_def_hash": b_hash,
        "nrmse_def_hash": f_nrmse,
        "reference_test_nrmse": ref_b,
        "reference_type_baselines": baselines[dataset].get("reference_type"),
        "reference_type_floors": floors[dataset]["reference"].get("reference_type"),
        "floors_certified_utc": floors.get("_certified_utc"),
        "checks": ["baselines._copylf_def_hash == panel_data.COPYLF_DEF_HASH",
                   "floors._copylf_def_hash == baselines._copylf_def_hash",
                   "floors._nrmse_def_hash == nrmse.NRMSE_DEF_HASH",
                   "dataset present in both files",
                   "baselines[ds].test_nrmse == floors[ds].reference.test_nrmse (exact)"],
    }
