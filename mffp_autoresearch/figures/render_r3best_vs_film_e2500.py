#!/usr/bin/env python3
"""Round-3 certified best (r3s2_route) vs FiLM transfer, both at 2500 epochs.

Data source (the ONLY head-to-head of these two families at E=2500):
    mffp_autoresearch_outputs/benchmark30/pilot2500/results/ladder_table.csv
    (b30 pilot2500 epoch ladder, seed 0, 8 datasets, jobs 753056-753061,
     landed 2026-08-15; film@e200 ifc_heat reproduces the frozen benchmark_30
     seed-0 anchor 0.026826 bit-for-bit, so the two halves are comparable.)

Generation and plotting are separate: this script only reads the CSV, so
layout tweaks re-render in seconds with no retraining.

Usage:
    python render_r3best_vs_film_e2500.py [--csv PATH] [--out PATH]
"""

import argparse
import csv
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

REPO = Path(__file__).resolve().parents[2]
DEFAULT_CSV = (
    REPO
    / "mffp_autoresearch_outputs/benchmark30/pilot2500/results/ladder_table.csv"
)
DEFAULT_OUT = Path(__file__).resolve().parent / "r3best_vs_film_e2500.png"

FILM_COLOR = "#3b6fb6"   # blue
R3S2_COLOR = "#d1622b"   # orange
GREY = "#5a5a5a"

# short, cold-readable dataset labels (suite prefix kept -> provenance)
PRETTY = {
    "sharp__fisher_kpp_2d": "sharp: Fisher-KPP 2D",
    "ext__helmholtz_2d": "ext: Helmholtz 2D",
    "sharp__allen_cahn_2d": "sharp: Allen-Cahn 2D",
    "poisson_local": "core: Poisson (local)",
    "sharp__euler": "sharp: Euler",
    "darcy_generated": "core: Darcy",
    "ifc_heat": "core: Heat (IFC)",
    "poisson_generated": "core: Poisson (generated)",
}


def load(csv_path: Path):
    rows = []
    with open(csv_path, newline="") as fh:
        for r in csv.DictReader(fh):
            # ratios are recomputed from the error columns, not read from the
            # rounded ratio@* columns; this reproduces the published geomeans
            # (1.0856 @200, 0.8506 @2500) exactly.
            film2500 = float(r["mf_fno_transfer_film@e2500"])
            r3s22500 = float(r["r3s2_route_b30@e2500"])
            rows.append(
                dict(
                    dataset=r["dataset"],
                    film=film2500,
                    r3s2=r3s22500,
                    ratio2500=film2500 / r3s22500,
                    ratio200=float(r["mf_fno_transfer_film@e200"])
                    / float(r["r3s2_route_b30@e200"]),
                )
            )
    rows.sort(key=lambda d: d["ratio2500"])  # worst for r3s2 at the bottom
    return rows


def geomean(vals):
    return math.exp(sum(math.log(v) for v in vals) / len(vals))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    rows = load(args.csv)
    labels = [PRETTY.get(r["dataset"], r["dataset"]) for r in rows]
    y = list(range(len(rows)))

    g2500 = geomean([r["ratio2500"] for r in rows])
    g200 = geomean([r["ratio200"] for r in rows])
    n_win = sum(1 for r in rows if r["ratio2500"] > 1.0)

    fig = plt.figure(figsize=(14.5, 7.6), constrained_layout=True)
    gs = GridSpec(1, 2, figure=fig, width_ratios=[1.0, 1.0])

    # ---------------- Panel A: absolute error, both models, at E = 2500 -------
    axA = fig.add_subplot(gs[0, 0])
    h = 0.38
    axA.barh(
        [v + h / 2 for v in y],
        [r["film"] for r in rows],
        height=h,
        color=FILM_COLOR,
        label="FiLM transfer (mf_fno_transfer_film)",
    )
    axA.barh(
        [v - h / 2 for v in y],
        [r["r3s2"] for r in rows],
        height=h,
        color=R3S2_COLOR,
        label="round-3 best: r3s2_route (arm A1_stack_ic_reg)",
    )
    axA.set_xscale("log")
    axA.set_yticks(y)
    axA.set_yticklabels(labels)
    axA.set_xlabel(
        "held-out test error, nRMSE  (log scale, lower is better)"
    )
    axA.set_title(
        "A. Absolute error of each model after 2500 epochs\n"
        "(same harness, seed 0, 8 pilot datasets)",
        fontsize=11,
    )
    # blank bands below (for the legend) and above (for the direction labels in
    # panel B); both panels share the limits so the rows stay aligned.
    YLIM = (-2.3, len(rows) + 0.6)
    axA.set_ylim(*YLIM)
    axA.legend(loc="lower right", fontsize=9, framealpha=1.0).set_zorder(10)
    axA.grid(axis="x", which="both", alpha=0.25, linestyle=":")
    axA.set_axisbelow(True)
    for i, r in enumerate(rows):
        axA.text(
            r["film"] * 1.15,
            i + h / 2,
            f"{r['film']:.4g}",
            va="center",
            fontsize=7.5,
            color=FILM_COLOR,
        )
        axA.text(
            r["r3s2"] * 1.15,
            i - h / 2,
            f"{r['r3s2']:.4g}",
            va="center",
            fontsize=7.5,
            color=R3S2_COLOR,
        )
    axA.set_xlim(2e-4, 12.0)

    # ---------------- Panel B: head-to-head ratio, e200 -> e2500 -------------
    axB = fig.add_subplot(gs[0, 1])
    lr2500 = [math.log2(r["ratio2500"]) for r in rows]
    lr200 = [math.log2(r["ratio200"]) for r in rows]

    colors = [R3S2_COLOR if v > 0 else FILM_COLOR for v in lr2500]
    axB.barh(y, lr2500, height=0.55, color=colors, zorder=3)
    axB.scatter(
        lr200,
        y,
        marker="D",
        s=34,
        facecolor="white",
        edgecolor=GREY,
        linewidth=1.2,
        zorder=5,
        label="the same dataset at 200 epochs (the earlier training budget)",
    )
    for i in y:
        axB.annotate(
            "",
            xy=(lr2500[i], i),
            xytext=(lr200[i], i),
            arrowprops=dict(arrowstyle="->", color=GREY, lw=0.9, alpha=0.8),
            zorder=4,
        )

    axB.axvline(0.0, color="black", lw=1.2, zorder=6)
    axB.axvline(
        math.log2(g2500),
        color=R3S2_COLOR,
        lw=1.6,
        ls="--",
        zorder=6,
        label=f"geometric mean over the 8 datasets @2500 ep = {g2500:.3f}$\\times$",
    )
    axB.axvline(
        math.log2(g200),
        color=GREY,
        lw=1.4,
        ls=":",
        zorder=6,
        label=f"geometric mean @200 ep = {g200:.3f}$\\times$",
    )

    ticks = [-5, -4, -3, -2, -1, 0, 1, 2, 3]
    axB.set_xticks(ticks)
    axB.set_xticklabels(
        [
            f"{2.0**t:g}$\\times$" if t >= 0 else f"1/{2.0**(-t):g}$\\times$"
            for t in ticks
        ]
    )
    axB.set_yticks(y)
    axB.set_yticklabels([])
    axB.set_xlabel(
        "head-to-head error ratio  "
        r"$\mathrm{nRMSE_{FiLM}}\,/\,\mathrm{nRMSE_{r3s2}}$"
        "   (log$_2$ spacing)"
    )
    axB.set_title(
        "B. Which model wins at 2500 epochs, and how the verdict moved with budget\n"
        f"r3s2 better on {n_win} of the 8;  arrow tail = the same dataset at 200 epochs",
        fontsize=11,
    )
    axB.grid(axis="x", alpha=0.25, linestyle=":")
    axB.set_axisbelow(True)
    axB.set_xlim(-5.9, 3.5)
    axB.set_ylim(*YLIM)
    axB.legend(loc="lower left", fontsize=8.5, framealpha=1.0).set_zorder(10)
    # value label clears BOTH the bar end and the e200 marker
    for i, r in enumerate(rows):
        xv = lr2500[i]
        if xv > 0:
            x_text, ha = max(xv, lr200[i]) + 0.18, "left"
        else:
            x_text, ha = min(xv, lr200[i]) - 0.18, "right"
        axB.text(
            x_text,
            i,
            f"{r['ratio2500']:.3g}$\\times$",
            va="center",
            ha=ha,
            fontsize=8,
            color=colors[i],
        )
    axB.text(
        0.985,
        0.985,
        "r3s2 better $\\rightarrow$",
        transform=axB.transAxes,
        ha="right",
        va="top",
        fontsize=9,
        color=R3S2_COLOR,
        fontweight="bold",
    )
    axB.text(
        0.015,
        0.985,
        "$\\leftarrow$ FiLM better",
        transform=axB.transAxes,
        ha="left",
        va="top",
        fontsize=9,
        color=FILM_COLOR,
        fontweight="bold",
    )

    fig.suptitle(
        "Round-3 certified best model vs FiLM transfer, both trained to 2500 epochs\n"
        "MFFP: predict the high-fidelity PDE field from a cheap low-fidelity solve + condition vector",
        fontsize=13.5,
        fontweight="bold",
    )

    fig.text(
        0.005,
        -0.045,
        "nRMSE = RMSE on the held-out high-fidelity test split, normalised by the field norm; single seed (0), identical harness for both models.\n"
        "Source: mffp_autoresearch_outputs/benchmark30/pilot2500/results/ladder_table.csv (SLURM 753056-753061, landed 2026-08-15). "
        "Anchor check: FiLM@200ep on core: Heat (IFC) reproduces the frozen benchmark_30 seed-0 value 0.026826 exactly.\n"
        "CAVEAT: these 8 datasets were picked to over-represent r3s2 wins (3 wins / 3 narrow FiLM wins / 2 FiLM blowouts), so the geometric mean is a TREND read across "
        "budgets, not a benchmark_30 headline. The all-30-dataset headline at 200 epochs was skill 0.6004 in FiLM's favour.",
        fontsize=7.6,
        color="#333333",
        va="top",
        ha="left",
        wrap=False,
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.out, dpi=170, bbox_inches="tight", facecolor="white")
    print(f"wrote {args.out}")
    print(f"geomean@2500 = {g2500:.4f}   geomean@200 = {g200:.4f}   r3s2 wins {n_win}/8")


if __name__ == "__main__":
    main()
