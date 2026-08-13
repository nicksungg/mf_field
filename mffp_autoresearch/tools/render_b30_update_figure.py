"""Render the benchmark_30 head-to-head figure for the mentor update.

Reads the fact-check-converged leaderboard (committed on branch
`bench30-campaign`; default path points at the campaign worktree) and renders
one panel: per-dataset film-relative skill of the round-3 certified model,
log-x, grouped core/ext/sharp, with the headline geomean band.

Re-runnable without any recomputation: everything comes from leaderboard.json.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DEFAULT_LB = ("/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/benchmark30/"
              "worktree/mffp_autoresearch/benchmark30/state/leaderboard.json")
GROUP_COLOR = {"core": "#4C72B0", "ext": "#DD8452", "sharp": "#55A868"}
FILM = "mf_fno_transfer_film"
MODEL = "r3s2_route_b30"


def dataset_group(ds: str) -> str:
    if ds.startswith("ext__"):
        return "ext"
    if ds.startswith("sharp__"):
        return "sharp"
    return "core"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--leaderboard", default=DEFAULT_LB)
    ap.add_argument("--out", default=str(Path(__file__).resolve().parents[1]
                                         / "figures/b30_skill_per_dataset.png"))
    args = ap.parse_args()

    lb = json.load(open(args.leaderboard))
    pd, common = lb["per_dataset"], lb["common_eligible_set"]
    head = lb["headline"]

    rows = []
    for ds in common:
        film = pd[ds][FILM]["per_seed"]
        model = pd[ds][MODEL]["per_seed"]
        per_seed = [f / m for f, m in zip(film, model)]
        skill = (pd[ds][FILM]["mean"] / pd[ds][MODEL]["mean"])
        rows.append((ds, skill, min(per_seed), max(per_seed)))
    rows.sort(key=lambda r: r[1])

    fig = plt.figure(figsize=(9.5, 10.8), constrained_layout=True)
    fig.get_layout_engine().set(rect=(0, 0.035, 1, 0.965))
    ax = fig.add_subplot(1, 1, 1)
    names = [r[0] for r in rows]
    skills = [r[1] for r in rows]
    lo = [max(0.0, r[1] - r[2]) for r in rows]
    hi = [max(0.0, r[3] - r[1]) for r in rows]
    colors = [GROUP_COLOR[dataset_group(ds)] for ds in names]
    y = range(len(rows))
    ax.barh(y, skills, xerr=[lo, hi], color=colors, height=0.72,
            error_kw={"lw": 0.9, "capsize": 2, "ecolor": "0.35"})
    ax.set_yticks(list(y), names, fontsize=8)
    ax.set_xscale("log")
    ax.axvline(1.0, color="0.15", lw=1.2)
    ax.text(1.0, len(rows) - 0.2, " parity: equal error", fontsize=8,
            va="top", ha="left", color="0.15")
    gm, (g_lo, g_hi) = head["mean"], head["interval"]
    ax.axvspan(g_lo, g_hi, color="0.6", alpha=0.25)
    ax.axvline(gm, color="0.3", lw=1.2, ls="--")
    ax.annotate(f"panel geomean {gm:.3f}\n[{g_lo:.3f}, {g_hi:.3f}] across seeds",
                xy=(gm, 11.5), xytext=(2.2, 11.5), fontsize=8, color="0.25",
                va="center", arrowprops={"arrowstyle": "->", "color": "0.4", "lw": 0.9})
    ax.set_xlabel(r"film-relative skill $= \mathrm{relL2}_{\mathrm{film}} \,/\, "
                  r"\mathrm{relL2}_{\mathrm{r3s2}}$  (ratio of 3-seed means, log scale; "
                  r"$>1$: certified model beats film)", fontsize=9)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in GROUP_COLOR.values()]
    ax.legend(handles, [f"{g} datasets" for g in GROUP_COLOR], loc="lower right",
              fontsize=8, title="benchmark_30 group", title_fontsize=8)
    ax.set_title(
        "benchmark_30 head-to-head: round-3 certified model (r3s2_route, arm A1_stack_ic_reg)\n"
        "vs the film-transfer FNO baseline — 29-dataset common set, 3 seeds × 200 epochs,\n"
        "stripped-view protocol; whiskers span the three per-seed ratios",
        fontsize=10)
    fig.suptitle("")
    footer = ("source: benchmark30 state/leaderboard.json (manifest eac7b48e, registry b30-0001; "
              "fact-check-converged 2026-08-13). era5 excluded (predeclared: frozen-family grid cap).")
    fig.text(0.01, 0.002, footer, fontsize=7, color="0.35")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=180)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
