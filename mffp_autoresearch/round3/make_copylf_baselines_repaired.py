#!/usr/bin/env python
"""Repaired-panel copy-LF baselines (2026-08-03) — the panel-mutation path.

`round2/eval/make_copylf_baselines.py` seam-pins every reference to the round-2
audit values, by design: it freezes the round-2 denominators and cannot admit a
deliberate panel change (its sanity band correctly rejects the repaired
fisher_kpp, whose copy-LF collapsed ~130x because the complete band-limited IC
leaves LF ~= HF).

This script executes the sanctioned mutation instead (PROGRAM_NOTE §5: panel
changes happen under an explicit ADR with the objective recomputed from the
change forward).  It does NOT edit the guarded eval layer: references for the
three regenerated datasets are computed through the same unedited
`panel_data.copylf_prediction` + `nrmse` code path, every other dataset must
reproduce the archived round-2 value to 1e-9 (bit-stability seam), and the
result replaces `eval/copylf_baselines.json` — whose round-2 version is
archived at `eval/copylf_baselines_round2_frozen_2026-08-03.json`.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVAL = HERE.parent / "round2" / "eval"
sys.path.insert(0, str(EVAL))

from nrmse import nrmse, NRMSE_DEF_HASH                      # noqa: E402
from panel_data import (COPYLF_DEF_HASH, copylf_prediction,  # noqa: E402
                        load_config, load_split)

REGENERATED = ["sharp__phase_field_crystal_2d", "sharp__allen_cahn_2d",
               "sharp__fisher_kpp_2d"]
FROZEN = EVAL / "copylf_baselines_round2_frozen_2026-08-03.json"
OUT = EVAL / "copylf_baselines.json"


def main() -> None:
    cfg = load_config()
    datasets = list(cfg["panel"]) + list(cfg["guard_set"])
    frozen = json.loads(FROZEN.read_text())
    if frozen.get("_copylf_def_hash") != COPYLF_DEF_HASH:
        raise SystemExit("archived round-2 baselines hash mismatch — wrong archive?")

    out = {k: v for k, v in frozen.items() if k.startswith("_")}
    out["_notes"] = dict(out.get("_notes", {}))
    out["_notes"]["panel_mutation_2026_08_03"] = (
        "pfc / allen_cahn_2d / fisher_kpp_2d references recomputed on the "
        "IC-complete regenerated data (condition_completeness_proposal/, operator-"
        "approved); all other entries reproduce the archived round-2 file to 1e-9. "
        "Round-2 skills are NOT comparable across this mutation on the three "
        "regenerated datasets. Round-2 denominators archived at "
        "copylf_baselines_round2_frozen_2026-08-03.json."
    )

    print(f"{'dataset':34s} {'ref_type':>9s} {'reference':>12s} {'round2_frozen':>13s} {'ratio':>8s}")
    for ds in datasets:
        prev = frozen[ds]
        if prev["reference_type"] != "copylf":
            out[ds] = dict(prev)                     # ifc paper bar: unchanged by design
            print(f"{ds:34s} {prev['reference_type']:>9s} {prev['test_nrmse']:>12.6g}"
                  f" {prev['test_nrmse']:>13.6g} {'kept':>8s}")
            continue
        data = load_split(ds, "test")
        value = float(nrmse(copylf_prediction(data, ds),
                            data["field_by_fid"][data["hf_fid"]]))
        if ds in REGENERATED:
            out[ds] = {**prev, "test_nrmse": value,
                       "round2_frozen_nrmse": prev["test_nrmse"],
                       "recomputed": "2026-08-03 repaired panel"}
        else:
            if abs(value - prev["test_nrmse"]) > 1e-9:
                raise SystemExit(f"{ds}: untouched dataset moved: {value!r} vs "
                                 f"frozen {prev['test_nrmse']!r} — investigate before writing")
            out[ds] = dict(prev)
        print(f"{ds:34s} {'copylf':>9s} {value:>12.6g} {prev['test_nrmse']:>13.6g}"
              f" {value / prev['test_nrmse']:>8.3g}")

    OUT.write_text(json.dumps(out, indent=2))
    print(f"-> {OUT}")


if __name__ == "__main__":
    main()
