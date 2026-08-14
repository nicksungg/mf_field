#!/usr/bin/env python3
"""Aggregate the b30 pilot2500 epoch ladder into one table.

Reads seed-0 per-dataset score JSONs:
  e200        -> .../benchmark30/rev-eac7b48e/results/scores/   (closed campaign)
  e600, e2500 -> .../benchmark30/pilot2500/results/scores/      (this pilot)

Writes ladder_table.md + ladder_table.csv under the pilot results root.
Missing cells are reported as MISSING, never silently dropped.
"""
import csv
import json
import math
from pathlib import Path

CAMPAIGN_SCORES = Path("/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch_outputs/benchmark30/rev-eac7b48e/results/scores")
PILOT_ROOT = Path("/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch_outputs/benchmark30/pilot2500")
PILOT_SCORES = PILOT_ROOT / "results" / "scores"

FAMILIES = ["mf_fno_transfer_film", "r3s2_route_b30"]
EPOCHS = [200, 600, 2500]
SEED = 0

PICKS = [
    "sharp__fisher_kpp_2d",
    "ext__helmholtz_2d",
    "sharp__allen_cahn_2d",
    "poisson_local",
    "sharp__euler",
    "darcy_generated",
    "ifc_heat",
    "poisson_generated",
]


def read_cell(fam: str, epochs: int, ds: str):
    root = CAMPAIGN_SCORES if epochs == 200 else PILOT_SCORES
    p = root / f"{fam}_s{SEED}_e{epochs}_{ds}.json"
    if not p.exists():
        return None
    with open(p) as f:
        d = json.load(f)
    # score_panel --out JSON: {"per_dataset": {ds: {"nRMSE": ...}}, ...}
    return float(d["per_dataset"][ds]["nRMSE"])


def fmt(v):
    return "MISSING" if v is None else f"{v:.5g}"


def main():
    grid = {(f, e, d): read_cell(f, e, d) for f in FAMILIES for e in EPOCHS for d in PICKS}

    lines = ["# b30 pilot2500 epoch ladder (seed 0, nRMSE; ratio = film/r3s2, >1 means r3s2 better)", ""]
    header = ["dataset"] + [f"{f}@e{e}" for f in FAMILIES for e in EPOCHS] + [f"ratio@e{e}" for e in EPOCHS]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + "---|" * len(header))
    csv_rows = [header]
    ratios_by_e = {e: [] for e in EPOCHS}
    for ds in PICKS:
        row = [ds]
        for f in FAMILIES:
            for e in EPOCHS:
                row.append(fmt(grid[(f, e, ds)]))
        for e in EPOCHS:
            film, r3s2 = grid[("mf_fno_transfer_film", e, ds)], grid[("r3s2_route_b30", e, ds)]
            if film is None or r3s2 is None:
                row.append("MISSING")
            elif not (math.isfinite(film) and math.isfinite(r3s2)) or film <= 0 or r3s2 <= 0:
                # a zero/negative nRMSE cell has no finite log-ratio; keep it
                # out of the geomean instead of aborting after the GPU spend
                row.append("DEGENERATE")
            else:
                ratio = film / r3s2
                ratios_by_e[e].append(ratio)
                row.append(f"{ratio:.3f}")
        lines.append("| " + " | ".join(row) + " |")
        csv_rows.append(row)

    lines.append("")
    for e in EPOCHS:
        rs = ratios_by_e[e]
        if rs and len(rs) == len(PICKS):
            gm = math.exp(sum(math.log(r) for r in rs) / len(rs))
            lines.append(f"- geomean film/r3s2 ratio @e{e} over {len(rs)}/8 pilot datasets: **{gm:.4f}**")
        else:
            lines.append(f"- geomean @e{e}: INCOMPLETE ({len(rs)}/8 cells)")
    lines.append("")
    lines.append("Pilot set is enriched for r3s2 wins/near-wins by design — the geomean here "
                 "is a trend read across rungs, not a benchmark_30 headline substitute.")

    PILOT_ROOT.joinpath("results").mkdir(parents=True, exist_ok=True)
    (PILOT_ROOT / "results" / "ladder_table.md").write_text("\n".join(lines) + "\n")
    with open(PILOT_ROOT / "results" / "ladder_table.csv", "w", newline="") as f:
        csv.writer(f).writerows(csv_rows)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
