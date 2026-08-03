#!/usr/bin/env python
"""Render docs/figures/error_comparison.png from the round-2 experiment cards.

Every number is parsed from the experiment-card JSONs under experiment_cards/
and the certified anchor files under state/anchors/ — nothing is typed in by
hand (round-1 design philosophy, tools/render_error_comparison.py there).

    .venv/bin/python tools/render_error_comparison.py

Series (skill units, lower is better; round 2 is condition-only at test —
models see LF at train only, never at inference):
  * launch anchor — the certified best training-free floor per dataset
    (NN-in-condition / train-mean / zero), panel geomean 23.0636
  * r2s1_direct-B3 scored head arm (test_hf) + its decoder_big reference arm
  * r2s2_stacked-B3 scored stacked arm (A1_lsi)
  * r2s4_diag-B1 certified 3-seed certifier (per-dataset means from the
    certified anchor; CI95 whisker on the PANEL GEOMEAN row)
r2s3_lf_train_signal publishes no scored panel arm (diagnostic stream; its
grade table lives in docs/figures/top_models_overview.svg).
"""
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
CARDS = ROOT / "experiment_cards"
OUT = ROOT / "docs" / "figures" / "error_comparison.png"

GRAY, PURPLE_DARK, PURPLE, BLUE, ORANGE = (
    "#6B7280", "#5B21B6", "#7C3AED", "#2563EB", "#EA580C")


def card(rel):
    return json.load(open(CARDS / rel))["5_actual_result"]


def anchor(name):
    return json.load(open(ROOT / "state" / "anchors" / f"{name}.json"))


def geomean(vals):
    return math.exp(sum(math.log(v) for v in vals) / len(vals))


def main():
    # ---------------- parse ----------------
    s1 = card("r2s1_direct/batch_3/B3.json")
    s2 = card("r2s2_stacked/batch_3/B3.json")
    a_launch = anchor("r2s1_direct")           # launch anchor (floors)
    a_s4 = anchor("r2s4_diag")                 # certified 3-seed anchor

    # Panel = the certified launch-anchor dataset list; verify every source
    # agrees (cards' per_dataset keys + scope flags, anchors' dataset lists).
    panel = list(a_launch["datasets"])
    assert a_launch["anchor_type"] == "best_floor_panel_geomean"
    for stream in ("r2s2_stacked", "r2s3_lf_train_signal"):
        other = anchor(stream)
        assert other["datasets"] == panel and other["value"] == a_launch["value"], stream
    assert a_s4["anchor_type"] == "certified_3seed_panel_geomean"
    assert a_s4["datasets"] == panel
    assert a_s4["supersedes"]["value"] == a_launch["value"]

    s1_panel = {ds: v for ds, v in s1["per_dataset"].items() if v.get("leg") == "panel"}
    assert sorted(s1_panel) == sorted(panel), "r2s1-B3 panel-leg keys != anchor panel"
    assert sorted(s2["per_dataset"]) == sorted(panel), "r2s2-B3 per_dataset keys != anchor panel"
    assert sorted(a_s4["per_dataset_mean_skill"]) == sorted(panel)

    # per-dataset series (skill, lower = better)
    floors = {ds: a_launch["per_dataset"][ds]["skill"] for ds in panel}
    floors["GEOMEAN"] = a_launch["value"]

    head = {ds: s1_panel[ds]["mean_skill"] for ds in panel}
    head["GEOMEAN"] = s1["panel_geomean_skill"]["mean"]

    decoder = {ds: s1_panel[ds]["ref_arm_skill"]["ref_decoder_big"] for ds in panel}
    decoder["GEOMEAN"] = geomean([decoder[ds] for ds in panel])  # derived, not a card-level number

    stacked = {ds: s2["per_dataset"][ds]["mean_skill"] for ds in panel}
    stacked["GEOMEAN"] = s2["panel_geomean_skill"]["mean"]

    cert = {ds: a_s4["per_dataset_mean_skill"][ds] for ds in panel}
    cert["GEOMEAN"] = a_s4["value"]
    ci_lo, ci_hi = a_s4["ci95"]

    # ---------------- sanity checks (printed, and asserted) ----------------
    for name, vals, ref, tol in (
        ("launch anchor", floors, a_launch["value"], 1e-9),
        ("r2s1-B3 head (test_hf)", head, s1["panel_geomean_skill"]["mean"], 1e-9),
        ("r2s2-B3 stacked (A1_lsi)", stacked, s2["panel_geomean_skill"]["mean"], 1e-9),
    ):
        re_geo = geomean([vals[ds] for ds in panel])
        assert abs(re_geo - ref) / ref < tol, (name, re_geo, ref)
        print(f"[check] {name}: geomean over 6 datasets {re_geo:.6f} == card/anchor {ref:.6f}")
    re_geo4 = geomean([cert[ds] for ds in panel])
    # anchor value is the mean of the 3 per-seed panel geomeans; the geomean of
    # per-dataset 3-seed means is a slightly different aggregate — near, not equal.
    assert abs(re_geo4 - a_s4["value"]) / a_s4["value"] < 0.01
    assert abs(sum(a_s4["per_seed"]) / 3 - a_s4["value"]) < 1e-9
    print(f"[check] r2s4 certified: mean of per-seed geomeans {a_s4['value']:.6f} "
          f"(geomean of per-dataset 3-seed means {re_geo4:.6f}); CI95 [{ci_lo:.4f}, {ci_hi:.4f}]")

    # row labels, with scope flags parsed from the cards
    def short(ds):
        lab = ds.replace("sharp__", "").replace("ext__", "ext__")
        if "report-only" in str(s2["per_dataset"][ds].get("note", "")):
            lab += "\n(report-only)"
        elif s2["per_dataset"][ds].get("reference_type") == "paper_bar":
            lab += "\n(paper-bar ref)"
        return lab

    rows = [(ds, short(ds)) for ds in panel] + [("GEOMEAN", "PANEL GEOMEAN")]

    series = [
        (f"launch anchor — best training-free floor per dataset\n"
         f"(NN-in-cond / train-mean / zero; geomean {floors['GEOMEAN']:.4f})",
         floors, dict(marker="s", color=GRAY, mfc=GRAY), {}),
        (f"r2s1-B3 stage-free per-mode head, scored test_hf\n"
         f"— ROUND BEST {head['GEOMEAN']:.4f} (seed 0)",
         head, dict(marker="*", color=PURPLE_DARK, mfc=PURPLE_DARK, ms=17), {}),
        (f"r2s1-B3 decoder_big reference arm, same family\n"
         f"(~14M-param trained decoder; derived geomean {decoder['GEOMEAN']:.2f})",
         decoder, dict(marker="o", color=PURPLE, mfc="white"), {}),
        (f"r2s2-B3 zero-gradient stacked arm A1_lsi\n"
         f"(retrieval $\\rightarrow$ closed-form LSI; {stacked['GEOMEAN']:.4f}, seed 0)",
         stacked, dict(marker="o", color=BLUE, mfc=BLUE), {}),
        (f"r2s4-B1 certifier, condition-only FiLM-FNO —\n"
         f"certified 3-seed {cert['GEOMEAN']:.4f}, CI95 [{ci_lo:.3f}, {ci_hi:.3f}]",
         cert, dict(marker="D", color=ORANGE, mfc=ORANGE), {"GEOMEAN": (ci_lo, ci_hi)}),
    ]

    # ---------------- draw ----------------
    fig, ax = plt.subplots(figsize=(13.8, 7.4))
    n = len(rows)
    for i in range(n):
        if i % 2 == 0:
            ax.axhspan(n - 1 - i - 0.5, n - 1 - i + 0.5, color="#F3F4F6", zorder=0)
    ax.axhline(0.5, color="#9CA3AF", lw=1.0, zorder=1)

    offsets = [0.28, 0.12, -0.02, -0.16, -0.30]
    for (label, vals, style, ranges), dy in zip(series, offsets):
        xs, ys = [], []
        for r, (key, _) in enumerate(rows):
            y = n - 1 - r + dy
            if key in ranges:
                lo, hi = ranges[key]
                ax.plot([lo, hi], [y, y], color=style["color"], lw=2.4, alpha=0.4,
                        solid_capstyle="butt", zorder=2.5)
                for x in (lo, hi):
                    ax.plot([x, x], [y - 0.055, y + 0.055], color=style["color"],
                            lw=1.4, alpha=0.55, zorder=2.5)
            if key in vals:
                xs.append(vals[key])
                ys.append(y)
        ms = style.pop("ms", 9)
        ax.plot(xs, ys, ls="none", markersize=ms, mew=1.6, label=label,
                marker=style["marker"], color=style["color"], mfc=style["mfc"], zorder=3)

    ax.axvline(floors["GEOMEAN"], color="#1F2937", ls="--", lw=1.2, zorder=2)
    ax.text(floors["GEOMEAN"] * 1.06, n - 0.63,
            f"launch anchor geomean {floors['GEOMEAN']:.4f}",
            fontsize=10.5, color="#1F2937")
    ax.annotate("better", xy=(3.05, -0.42), xytext=(4.9, -0.42), fontsize=10.5,
                color=GRAY, arrowprops=dict(arrowstyle="->", color=GRAY), va="center")

    ax.set_xscale("log")
    ax.set_xlim(2.6, 420)
    ax.set_ylim(-0.5, n - 0.5)
    ax.set_yticks([n - 1 - r for r in range(n)])
    ax.set_yticklabels([lab for _, lab in rows], fontsize=11.5)
    ax.set_xlabel("skill  =  nRMSE(model) / nRMSE(copy-LF reference)     "
                  "(log scale — lower is better)", fontsize=12)
    ax.tick_params(axis="x", labelsize=11)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color("#9CA3AF")

    ax.set_title(
        "Round 2 — top scored arms vs launch anchor, per-dataset error in skill units\n"
        "condition-only at test: models receive LF fields at TRAIN time only; at inference only the condition\n"
        "vector — the copy-LF reference uses the test LF the models never see, so skill $\\gg$ 1 is structural\n"
        "and the round is judged against the training-free-floor anchor, not copy-LF parity.\n"
        "markers: r2s1 / r2s2 = seed 0 (strict 1-seed in-round protocol); r2s4 = certified 3-seed mean,\n"
        "whisker on PANEL GEOMEAN = its CI95; open marker = non-scored reference arm of the same family",
        fontsize=12.5, loc="left")
    ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5), fontsize=10.5, frameon=False)

    fig.text(0.01, 0.015,
             "Notes: helmholtz is report-only (ADR r2-0004 §3: HF test fields reproduce from the condition vector alone via two FFTs — no MF/learning claim can rest on it).\n"
             "ifc_poisson skills divide by the fixed paper bar (nRMSE 0.036), not copy-LF, and sit on 5 HF train rows (low-n LOO). decoder_big's geomean is derived in-script\n"
             "from the six per-dataset card values (open marker; the scored arm is the head). r2s3_lf_train_signal is absent by design: a diagnostic stream with no scored\n"
             "panel arm — its A/B/C substitution-audit grade table is in top_models_overview.svg. Not shown: r2s2-B1 14.0756 (gain entirely the ifc column where corrector\n"
             "attribution is invalid — pseudo-LF fit, attribution.valid=false) and r2s1-B2 18.3622 (T1-F2/T1-F7 head-selection defects; B3 is its instrument-repaired\n"
             "re-pricing). All stream anchors except r2s4's remained the launch floor: §2e requires 3 seeds and the round closed before any confirm pass.",
             fontsize=9.5, color=GRAY, va="bottom")

    fig.subplots_adjust(left=0.145, right=0.70, top=0.76, bottom=0.25)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=150, bbox_inches="tight")
    print(f"wrote {OUT}")

    # ---------------- verification dump ----------------
    print("\nplotted values (skill; rows in figure order):")
    hdr = f"{'dataset':32s} {'anchor-floor':>12s} {'s1-B3 head':>11s} {'s1-B3 dec':>10s} {'s2-B3 A1':>9s} {'s4 cert':>9s}"
    print(hdr)
    for key, _ in rows:
        print(f"{key:32s} {floors[key]:12.4f} {head[key]:11.4f} {decoder[key]:10.4f} "
              f"{stacked[key]:9.4f} {cert[key]:9.4f}")
    print(f"r2s4 GEOMEAN CI95: [{ci_lo:.4f}, {ci_hi:.4f}]")


if __name__ == "__main__":
    main()
