"""Family-side helper: write the role-resolved data binding into `last.pt`.

Card `r3s4_audit-B2` part 3, deliverable (ii). This is the ONLY thing a family
has to do to become auditable:

    from ckpt_binding import binding_block, ROLES_READ_BY_ARM
    state["data_binding"] = {dataset_name: binding_block(dataset_dir,
                                                         dataset_name,
                                                         roles_read)}
    torch.save(state, ckpt_dir / "last.pt")

`data_binding` is already one of `round3/tools/zero_work_resume_scan.py`'s
`BINDING_KEYS`, so that tool's coverage counter reads the block with NO edit to
it; the action predicate lives in `round3/tools/ckpt_data_binding.py` (also
unedited by the family — imported).

`roles_read` is the honest declaration of what the ARM consumes, and it is the
whole point: on the identical dataset a `train_lf`-only change must be RETRAIN
for an LF-consuming arm and NONE for a condition-only arm.

  cond_only     train_cond, train_hf, test_cond, test_hf
  lf_at_train   + train_lf

`test_lf` is read by NEITHER arm (round-3 stripped test view, program.md §5
immutable #9): it carries the copy-LF denominator only, which is why a
`test_lf` change is REREFERENCE and never RETRAIN.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORKTREE_ROOT = HERE.parents[1]                    # <worktree>/models_r3/_common -> <worktree>
TOOLS_DIR = WORKTREE_ROOT / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import ckpt_data_binding as cdb                    # noqa: E402  (read-only import)

ROLES = cdb.ROLES
TOOL_VERSION = cdb.TOOL_VERSION

# Card recipe.env R3S4B2_ARMS / R3S4B2_ROLES. Declared, not inferred.
ROLES_READ_BY_ARM = {
    "cond_only": ("train_cond", "train_hf", "test_cond", "test_hf"),
    "lf_at_train": ("train_cond", "train_hf", "train_lf", "test_cond", "test_hf"),
}


def roles_read_for(arm: str) -> tuple:
    if arm not in ROLES_READ_BY_ARM:
        raise SystemExit(
            f"unknown arm {arm!r}; recipe R3S4B2_ARMS = {sorted(ROLES_READ_BY_ARM)}")
    return ROLES_READ_BY_ARM[arm]


def binding_block(dataset_dir, dataset_name: str, roles_read) -> dict:
    """`{roles, role_n_units, union_sha256, roles_read, tool_version, recorded_utc}`."""
    return cdb.record(Path(dataset_dir), dataset_name, roles_read=list(roles_read))


def attach(state: dict, dataset_dir, dataset_name: str, arm: str) -> dict:
    """Attach `state['data_binding'] = {dataset_name: <block>}` in place."""
    state["data_binding"] = {
        dataset_name: binding_block(dataset_dir, dataset_name, roles_read_for(arm))
    }
    return state
