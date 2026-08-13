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


def render_wins_pairs(lb: dict, out: Path) -> None:
    """Companion figure: absolute rel-L2 of both models on the 5 win datasets."""
    pd = lb["per_dataset"]
    wins = []
    for ds in lb["common_eligible_set"]:
        skill = pd[ds][FILM]["mean"] / pd[ds][MODEL]["mean"]
        if skill > 1:
            wins.append((ds, skill))
    wins.sort(key=lambda t: -t[1])

    fig = plt.figure(figsize=(9.5, 4.6), constrained_layout=True)
    fig.get_layout_engine().set(rect=(0, 0.06, 1, 0.94))
    ax = fig.add_subplot(1, 1, 1)
    colors = {MODEL: "#4C72B0", FILM: "#C44E52"}
    label = {MODEL: "round-3 certified model (r3s2_route)", FILM: "film-transfer FNO baseline"}
    for i, (ds, skill) in enumerate(wins):
        for k, fam in enumerate((MODEL, FILM)):
            rec = pd[ds][fam]
            yy = i + (0.19 if k == 0 else -0.19)
            ax.barh(yy, rec["mean"],
                    xerr=[[max(0.0, rec["mean"] - rec["min"])], [max(0.0, rec["max"] - rec["mean"])]],
                    height=0.34, color=colors[fam],
                    label=label[fam] if i == 0 else None,
                    error_kw={"lw": 0.9, "capsize": 2, "ecolor": "0.35"})
        ax.text(max(pd[ds][FILM]["max"], pd[ds][MODEL]["max"]) * 1.25, i,
                f"{skill:.2f}× lower error", va="center", fontsize=9, color="0.2")
    ax.set_yticks(range(len(wins)), [ds for ds, _ in wins], fontsize=9)
    ax.invert_yaxis()
    ax.set_xscale("log")
    ax.set_xlim(right=ax.get_xlim()[1] * 4)
    ax.set_xlabel("relative-L2 error, 3-seed mean (log scale; shorter bar = more accurate; "
                  "whiskers span the per-seed values)", fontsize=9)
    fig.legend(loc="outside right center", fontsize=9)
    ax.set_title("The five datasets where the certified model beats film: absolute error, side by side\n"
                 "(same runs as the skill figure; the annotation is film's error ÷ the certified model's)",
                 fontsize=10)
    fig.text(0.01, 0.005, "source: benchmark30 state/leaderboard.json (manifest eac7b48e; "
             "fact-check-converged 2026-08-13).", fontsize=7, color="0.35")
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=180)
    print(f"wrote {out}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--leaderboard", default=DEFAULT_LB)
    ap.add_argument("--out", default=str(Path(__file__).resolve().parents[1]
                                         / "figures/b30_skill_per_dataset.png"))
    args = ap.parse_args()

    lb = json.load(open(args.leaderboard))
    render_wins_pairs(lb, Path(args.out).parent / "b30_wins_pairs.png")
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
    import matplotlib.lines as mlines
    import matplotlib.patches as mpatches
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in GROUP_COLOR.values()]
    labels = [f"{g} datasets" for g in GROUP_COLOR]
    handles += [
        mlines.Line2D([], [], color="0.15", lw=1.2),
        mlines.Line2D([], [], color="0.3", lw=1.2, ls="--"),
        mpatches.Patch(color="0.6", alpha=0.25),
    ]
    labels += [
        "parity: both models equal error",
        f"29-dataset panel geomean ({gm:.3f})",
        "geomean range across the 3 seeds",
    ]
    ax.legend(handles, labels, loc="lower right", fontsize=8,
              title="benchmark_30 group / reference lines", title_fontsize=8)
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
