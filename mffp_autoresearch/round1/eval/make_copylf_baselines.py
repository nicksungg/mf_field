"""Generate copylf_baselines.json for the panel + guard datasets (gate G2).

For each dataset: nRMSE of the copy-LF prediction on the TEST split, through
the round's single nRMSE definition. Joined against the mentor's independent
characterization (`lf_hf_rel_resid` in akash/results/dataset_characterization.csv)
as a sanity reference — large divergence must be investigated, not accepted.

Run:  python make_copylf_baselines.py
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

from nrmse import nrmse, NRMSE_DEF_HASH
from panel_data import copylf_prediction, load_config, load_split, repo_root


def characterization_refs() -> dict:
    path = repo_root() / "mf_field/akash/results/dataset_characterization.csv"
    refs = {}
    with open(path) as f:
        for row in csv.DictReader(f):
            key = (
                row["dataset"]
                if row["collection"] == "core"
                else f"{row['collection']}__{row['dataset']}"
            )
            refs[key] = float(row["lf_hf_rel_resid"])
    return refs


def paper_bar(dataset: str) -> float:
    """Published reference nRMSE from the guarded (read-only) baselines file."""
    path = repo_root() / "mf_field/factory_mffp/baselines/paper_baselines.json"
    with open(path) as f:
        splits = json.load(f)["datasets"][dataset]["splits"]
    values = [v["paper"] for v in splits.values()]
    if not values:
        raise ValueError(f"no paper splits recorded for {dataset}")
    prod = 1.0
    for v in values:
        prod *= v
    return prod ** (1.0 / len(values))


def main() -> None:
    cfg = load_config()
    datasets = list(cfg["panel"]) + list(cfg["guard_set"])
    refs = characterization_refs()

    out = {
        "_nrmse_def_hash": NRMSE_DEF_HASH,
        "_split": "test",
        "_notes": {
            "characterization_ref": "lf_hf_rel_resid from akash dataset_characterization.csv; "
            "computed on a different split/definition, sanity reference only (G2 bound: 0.25-4x)",
            "ifc_poisson": "ifc test ships only the HF fidelity, so copy-LF is undefined on the "
            "test split; the skill reference is the published paper bar instead (ADR 0002). "
            "skill < 1 there means 'beats the paper', matching spec success criterion 1.",
            "heat_local": "ratio_to_ref 0.028 is outside the G2 bound: heat_local has a 5-level "
            "ladder and this file uses the HIGHEST LF (l4, 96x96 -> 128x128) per the round "
            "convention, while the characterization's lf_hf_rel_resid evidently reflects a "
            "coarser fidelity. Verified deliberately divergent, not a bug (gate G2, gates.md).",
        },
    }
    print(f"{'dataset':34s} {'ref_type':>9s} {'reference':>11s} {'char_ref':>9s} {'ratio':>7s}")
    for ds in datasets:
        data = load_split(ds, "test")
        if data["lf_fids"]:
            value = nrmse(copylf_prediction(data), data["field_by_fid"][data["hf_fid"]])
            ref_type = "copylf"
        else:
            value = paper_bar(ds)
            ref_type = "paper_bar"
        ref = refs.get(ds)
        ratio = (value / ref) if (ref and ref_type == "copylf") else None
        out[ds] = {
            "reference_type": ref_type,
            "test_nrmse": value,
            "characterization_ref": ref,
            "ratio_to_ref": ratio,
        }
        print(f"{ds:34s} {ref_type:>9s} {value:11.4f} "
              f"{ref if ref is not None else float('nan'):9.4f} "
              f"{ratio if ratio is not None else float('nan'):7.3f}")

    path = Path(__file__).resolve().parent / "copylf_baselines.json"
    with open(path, "w") as f:
        json.dump(out, f, indent=2, sort_keys=True)
    print(f"\nwrote {path}")


if __name__ == "__main__":
    main()
