"""Debug attempt 1 -- r3s2_field_reach-B3, job 261188 FAILED on the fluid guard cell.

Symptom (slurm .err, job 261188; the six-cell panel invocation COMPLETED, the
separate `--datasets guard` invocation died):
  floor_matched_n.FloorMatchedNError: fluid: R3S2B3_FLOOR_MATCHED_N declares
  sharp:320 but the HOT plan's |T| is 205 -- refusing to report a mismatched floor

Hypothesis: `matched_n_band` classifies the CELL SHAPE by "does the plan carry a
T array" (floor_matched_n.py:175-176), but `hot_split.plan`'s PROPORTIONAL
FALLBACK -- the branch the guard cells take -- also returns a T. So a guard cell
is read as the `sharp` shape and is asked for the sharp:320 obligation the card
never gave it (recipe env names exactly two shapes: R3S2B3_HOT_SPLIT_SHARP and
R3S2B3_HOT_SPLIT_IFC; floor_matched_n.py:204 already says in prose that "the
guard/fallback cells carry no matched-n obligation" -- the classifier just never
lets a guard cell reach that branch).

This script tabulates, for every panel + guard cell, n_train_hf, the hot_split
protocol it lands in, the shape the SHIPPED classifier assigns, and the shape the
proposed knob-keyed classifier assigns. Reads arrays only; no training, no GPU.
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORKTREE = os.path.normpath(os.path.join(HERE, ".."))
FAMILY = os.path.join(WORKTREE, "models_r3", "r3s2_ceiling")
EVAL_DIR = "/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/round2/eval"
STRIPPED = "/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/round2/stripped_data"
FACTORY = "/resnick/groups/Hippo/ezeng/mf_field/mf_field/factory_mffp"
for p in (FAMILY, EVAL_DIR, FACTORY):
    if p not in sys.path:
        sys.path.insert(0, p)

import hot_split  # noqa: E402
import floor_matched_n as fmn  # noqa: E402
from data_adapters.loaders import load_mf_dataset  # noqa: E402

PANEL = ["sharp__phase_field_crystal_2d", "sharp__allen_cahn_2d",
         "sharp__fisher_kpp_2d", "sharp__cahn_hilliard", "ifc_poisson", "ifc_heat"]
GUARD = ["heat_local", "fluid", "sharp__sod_1d"]     # round2/project.yaml order
KNOB = "sharp:320,ifc:C5_4_loo"                      # recipe R3S2B3_FLOOR_MATCHED_N


def shape_shipped(plan):
    """floor_matched_n.py:175-176 exactly as shipped in c763246e."""
    return ("ifc" if str(plan.get("protocol", "")).startswith("enumerate_C")
            else ("sharp" if plan.get("T") is not None else None))


def shape_proposed(plan):
    """Proposed: the shape IS the card knob the plan was built from."""
    k = str(plan.get("knob", ""))
    return ("ifc" if k == "R3S2B3_HOT_SPLIT_IFC"
            else ("sharp" if k == "R3S2B3_HOT_SPLIT_SHARP" else None))


def main():
    want = fmn._requested(KNOB)
    print(f"R3S2B3_FLOOR_MATCHED_N={KNOB!r} parses to {want}\n")
    hdr = (f"{'dataset':32s} {'n_tr_hf':>7s} {'protocol':28s} {'|T|':>4s} "
           f"{'elig':>5s} {'shipped':>8s} {'fixed':>6s}  outcome")
    print(hdr)
    print("-" * len(hdr))
    for name in PANEL + GUARD:
        d = os.path.join(STRIPPED, name)
        tr = load_mf_dataset(d, "train")
        hf = max(tr["fids"])
        n_tr = int(tr["field_by_fid"][hf].shape[0])
        plan = hot_split.plan(name, n_tr, 0)
        nT = "-" if plan.get("T") is None else str(len(plan["T"]))
        s_old, s_new = shape_shipped(plan), shape_proposed(plan)
        spec_old = want.get(s_old) if s_old else None
        spec_new = want.get(s_new) if s_new else None
        if (spec_old and spec_old.isdigit() and plan.get("T") is not None
                and int(spec_old) != len(plan["T"])):
            outcome = f"RAISES today (declares {spec_old}, |T|={len(plan['T'])})"
        else:
            outcome = f"ok today (spec={spec_old})"
        outcome += (f" -> fixed: spec={spec_new}" if spec_new
                    else " -> fixed: applicable=False, no matched-n obligation")
        print(f"{name:32s} {n_tr:7d} {plan['protocol']:28s} {nT:>4s} "
              f"{str(plan['registered_unit_eligible']):>5s} "
              f"{str(s_old):>8s} {str(s_new):>6s}  {outcome}")

    # The refusal must STAY ARMED for the sharp shape: a plan that really was built
    # from R3S2B3_HOT_SPLIT_SHARP but whose |T| is not the declared 320 is a
    # mismatched floor and must still raise (this is the guard the fix must not
    # weaken -- only the guard-cell MISROUTING is removed).
    import numpy as np
    bad = {"protocol": "seeded_perm_fit320_heldout80",
           "knob": "R3S2B3_HOT_SPLIT_SHARP",
           "T": np.arange(205), "disclosure_legs": []}
    z = np.zeros((3, 2))
    try:
        fmn.matched_n_band(bad, "synthetic_sharp_wrong_T", KNOB,
                           z, z, z, z, {}, {}, {"applicable": False})
        print("\nREGRESSION: sharp-shape |T| mismatch did NOT raise")
    except fmn.FloorMatchedNError as e:
        print(f"\nrefusal still armed for the sharp shape: {e}")


if __name__ == "__main__":
    main()
