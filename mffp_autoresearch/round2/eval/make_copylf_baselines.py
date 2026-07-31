"""Generate the round-2 copylf_baselines.json (corrected references; gate G2-r2).

For each panel + guard dataset: nRMSE of the CORRECTED copy-LF prediction
(ADR r2-0001 conventions in panel_data.py) on the TEST split of the ORIGINAL
dataset — the stored test LF that round-2 models never see. These are the
frozen skill denominators for the whole round (spec §3).

Seam checks (assert, don't default):
  - datasets whose convention changed must come out BELOW the round-1 frozen
    value and within a sanity band of the s3-B1 registration-audit variant
    values (AUDIT_EXPECTED below);
  - datasets whose convention is unchanged must reproduce the round-1 frozen
    value to 1e-9 (bit-stability regression);
  - ifc_poisson keeps the paper bar (test ships no LF; r1 ADR 0002).

Run:  python make_copylf_baselines.py
"""
from __future__ import annotations

import json
from pathlib import Path

from nrmse import nrmse, NRMSE_DEF_HASH
from panel_data import (
    COPYLF_DEF_HASH,
    DIRICHLET_NODE_DATASETS,
    PERIODIC_NODE_DATASETS,
    copylf_prediction,
    load_config,
    load_split,
    repo_root,
)

# s3-B1 registration audit, corrected-variant nRMSE (C for periodic-nested,
# E for helmholtz). Sanity band only — the frozen number is what THIS file
# computes on the full test split through the round's nrmse.py.
AUDIT_EXPECTED = {
    "sharp__allen_cahn_2d": 0.00178077,
    "sharp__phase_field_crystal_2d": 0.00738078,
    "sharp__fisher_kpp_2d": 0.0214495,
    "sharp__cahn_hilliard": 0.041803,
    "ext__helmholtz_2d": 0.299033,
}
AUDIT_BAND = (0.7, 1.4)


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


def r1_frozen() -> dict:
    path = repo_root() / "mffp_autoresearch/round1/eval/copylf_baselines.json"
    with open(path) as f:
        return json.load(f)


def main() -> None:
    cfg = load_config()
    datasets = list(cfg["panel"]) + list(cfg["guard_set"])
    r1 = r1_frozen()
    corrected = PERIODIC_NODE_DATASETS | DIRICHLET_NODE_DATASETS

    out = {
        "_nrmse_def_hash": NRMSE_DEF_HASH,
        "_copylf_def_hash": COPYLF_DEF_HASH,
        "_split": "test",
        "_notes": {
            "convention": "ADR r2-0001: registration ((r-1)/2 half-cell) + wrap-seam "
            "reference fixes. Periodic nested datasets use node-aligned bilinear with "
            "periodic wrap (variant C); helmholtz uses the Dirichlet interior-node map "
            "(variant E); guards/1-D keep the round-1 convention (audit: consistent).",
            "ifc_poisson": "ifc test ships only the HF fidelity, so copy-LF is undefined "
            "on the test split; the skill reference is the published paper bar (r1 ADR "
            "0002). skill < 1 there means 'beats the paper'.",
            "comparability": "round-2 skills are NOT comparable to round-1 skills on the "
            "corrected datasets: the round-1 denominators were inflated 2.0-8.6x by the "
            "registration defect (r1 report §5). r1_frozen_nrmse is recorded per dataset.",
            "pfc": "under a band-limited (variant D) reference pfc has no fidelity gap at "
            "all (nRMSE 3e-07); variant C is the round convention and pfc claims carry a "
            "standing caveat until the dataset is redesigned (r1 report §5 fix list).",
        },
    }
    print(f"{'dataset':34s} {'ref_type':>9s} {'reference':>11s} {'r1_frozen':>11s} {'ratio':>7s}")
    for ds in datasets:
        data = load_split(ds, "test")
        if data["lf_fids"]:
            value = nrmse(copylf_prediction(data, ds), data["field_by_fid"][data["hf_fid"]])
            ref_type = "copylf"
        else:
            value = paper_bar(ds)
            ref_type = "paper_bar"
        r1_val = r1.get(ds, {}).get("test_nrmse")

        if ref_type == "copylf" and r1_val is not None:
            if ds in corrected:
                if value >= r1_val:
                    raise SystemExit(
                        f"{ds}: corrected reference {value:.6g} is not below the round-1 "
                        f"frozen value {r1_val:.6g} — fix did not take"
                    )
                exp = AUDIT_EXPECTED[ds]
                if not (AUDIT_BAND[0] <= value / exp <= AUDIT_BAND[1]):
                    raise SystemExit(
                        f"{ds}: corrected reference {value:.6g} outside the sanity band "
                        f"{AUDIT_BAND} x audit value {exp:.6g}"
                    )
            else:
                if abs(value - r1_val) > 1e-9:
                    raise SystemExit(
                        f"{ds}: convention unchanged but value moved: "
                        f"{value!r} vs r1 {r1_val!r}"
                    )

        ratio = (value / r1_val) if r1_val else None
        out[ds] = {
            "reference_type": ref_type,
            "test_nrmse": value,
            "r1_frozen_nrmse": r1_val,
            "ratio_to_r1": ratio,
            "convention": (
                "node_aligned_periodic" if ds in PERIODIC_NODE_DATASETS
                else "dirichlet_node" if ds in DIRICHLET_NODE_DATASETS
                else "paper_bar" if ref_type == "paper_bar"
                else "legacy_cell_centred"
            ),
        }
        print(f"{ds:34s} {ref_type:>9s} {value:11.6f} "
              f"{r1_val if r1_val is not None else float('nan'):11.6f} "
              f"{ratio if ratio is not None else float('nan'):7.3f}")

    path = Path(__file__).resolve().parent / "copylf_baselines.json"
    with open(path, "w") as f:
        json.dump(out, f, indent=2, sort_keys=True)
    print(f"\nwrote {path}")


if __name__ == "__main__":
    main()
