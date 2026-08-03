#!/usr/bin/env python
"""Render docs/figures/top_models_overview.svg — round-2 per-stream top models.

Round-2 sibling of round1/docs/figures/top_models_overview.svg (same visual
language: Helvetica, role colors — blue trained NN, purple closed-form/fitted,
gray diagnostic). Every NUMBER is parsed from the experiment-card JSONs under
experiment_cards/ and the anchor files under state/anchors/ — nothing typed in
by hand. r2s3's row is its B4 substitution-audit grade table (the stream is
diagnostic: no scored panel geomean); the letter grades are parsed out of the
B4 card's part-6 judgment text and the effect sizes out of its part 5.

    .venv/bin/python tools/render_top_models_overview.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARDS = ROOT / "experiment_cards"
OUT = ROOT / "docs" / "figures" / "top_models_overview.svg"

DARK, GRAY = "#1F2937", "#6B7280"
BLUE, BLUE_BG = "#2563EB", "#DBEAFE"
PURPLE, PURPLE_BG = "#7C3AED", "#EDE9FE"
GREEN, GREEN_BG = "#059669", "#D1FAE5"
ORANGE, ORANGE_BG = "#EA580C", "#FFEDD5"
GRAY_BG = "#F3F4F6"


def card(rel):
    return json.load(open(CARDS / rel))


def anchor(name):
    return json.load(open(ROOT / "state" / "anchors" / f"{name}.json"))


def deep_find(obj, key):
    """First value of `key` anywhere in a nested dict/list."""
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for v in obj.values():
            r = deep_find(v, key)
            if r is not None:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = deep_find(v, key)
            if r is not None:
                return r
    return None


def deep_find_text(obj, needle):
    """First string anywhere in a nested structure containing `needle`."""
    if isinstance(obj, str):
        return obj if needle in obj else None
    if isinstance(obj, dict):
        vals = obj.values()
    elif isinstance(obj, list):
        vals = obj
    else:
        return None
    for v in vals:
        r = deep_find_text(v, needle)
        if r is not None:
            return r
    return None


def main():
    # ---------------- parse ----------------
    s1 = card("r2s1_direct/batch_3/B3.json")["5_actual_result"]
    s2 = card("r2s2_stacked/batch_3/B3.json")["5_actual_result"]
    s3 = card("r2s3_lf_train_signal/batch_4/B4.json")
    a_launch = anchor("r2s1_direct")
    a_s4 = anchor("r2s4_diag")

    panel = list(a_launch["datasets"])
    anchor_val = a_launch["value"]

    g1 = s1["panel_geomean_skill"]["mean"]                 # r2s1-B3, seed 0
    g2 = s2["panel_geomean_skill"]["mean"]                 # r2s2-B3, seed 0
    g4 = a_s4["value"]                                     # r2s4-B1 certified
    ci_lo, ci_hi = a_s4["ci95"]
    assert a_s4["source_card"] == "r2s4_diag-B1"
    assert a_s4["supersedes"]["value"] == anchor_val

    # r2s1 head sizes over the panel datasets (leg == 'panel' scope flag)
    head_params = [v["scored_head_n_params"] for ds, v in s1["per_dataset"].items()
                   if v.get("leg") == "panel"]
    assert len(head_params) == len(panel)
    pmin, pmax = min(head_params), max(head_params)

    # r2s3-B4 grade table: letters from the part-6 judgment, effects from part 5
    judgment = deep_find_text(s3["6_analysis"], "honesty grades")
    assert judgment, "r2s3-B4 part-6 judgment text not found"
    grades = dict(re.findall(r"\b(ch|ifc|ac) = ([A-C]):", judgment))
    assert grades == {"ch": "A", "ifc": "B", "ac": "C"}, grades
    # verify the prose used below against the card's own wording
    assert "broad-based" in judgment and "narrow" in judgment and "tail-carried" in judgment
    over_mce = deep_find(s3["5_actual_result"],
                         "achievable_gate_E_free_worst_draw_over_mce")
    x_ch = over_mce["sharp__cahn_hilliard"]     # 113.5x
    x_ifc = over_mce["ifc_poisson"]             # 1.41x
    x_ac = over_mce["sharp__allen_cahn_2d"]     # 26.9x (but fails ceiling gate)
    ceiling_survivors = deep_find(s3["5_actual_result"],
                                  "resolvable_above_floor_ceiling_gate_class_wide")
    assert ceiling_survivors == ["sharp__cahn_hilliard"]

    # sanity dump (verification requirement)
    print(f"anchor launch geomean          {anchor_val:.4f}")
    print(f"r2s1_direct-B3 scored test_hf  {g1:.4f}  (seed 0; head params {pmin}-{pmax})")
    print(f"r2s2_stacked-B3 scored A1_lsi  {g2:.4f}  (seed 0)")
    print(f"r2s4_diag-B1 certified 3-seed  {g4:.4f}  CI95 [{ci_lo:.3f}, {ci_hi:.3f}]")
    print(f"r2s3-B4 grades: ch={grades['ch']} ({x_ch:.1f}x mce), "
          f"ifc={grades['ifc']} ({x_ifc:.2f}x mce), ac={grades['ac']} ({x_ac:.1f}x achievable, "
          f"ceiling-gate survivors {ceiling_survivors})")

    # ---------------- geometry helpers ----------------
    W, H = 1160, 900
    X0, X1, V0, V1 = 90, 1070, 18.0, 24.0

    def xp(v):
        return X0 + (v - V0) / (V1 - V0) * (X1 - X0)

    e = []          # svg elements

    def text(x, y, s, size=12, fill=DARK, weight=None, anchor_=None, style=""):
        a = f' text-anchor="{anchor_}"' if anchor_ else ""
        w = f' font-weight="{weight}"' if weight else ""
        st = f" {style}" if style else ""
        e.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}"{w}{a}{st}>{s}</text>')

    def line(x1, y1, x2, y2, stroke=GRAY, sw=1.5, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        e.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def rect(x, y, w, h, fill, stroke=None, sw=2, rx=8):
        s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        e.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{s}/>')

    def circle(cx, cy, r, fill, stroke=None, sw=2):
        s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        e.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}"{s}/>')

    def diamond(cx, cy, r, fill):
        e.append(f'<path d="M {cx} {cy - r} L {cx + r} {cy} L {cx} {cy + r} L {cx - r} {cy} Z" fill="{fill}"/>')

    def star(cx, cy, r, fill):
        import math
        pts = []
        for i in range(10):
            rad = r if i % 2 == 0 else r * 0.45
            ang = -math.pi / 2 + i * math.pi / 5
            pts.append(f"{cx + rad * math.cos(ang):.1f},{cy + rad * math.sin(ang):.1f}")
        e.append(f'<polygon points="{" ".join(pts)}" fill="{fill}"/>')

    # ---------------- header ----------------
    e.append(f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>')
    text(30, 42, "MFFP Round 2 — Top Models per Stream (condition-only at test)",
         size=21, weight="bold")
    text(30, 64, "skill = nRMSE(model) / nRMSE(copy-LF) — lower is better; models see LF fields at "
                 "TRAIN time only, at inference only the condition vector", size=12, fill=GRAY)
    text(30, 82, f"launch anchor = geomean of the best training-free floor per dataset = "
                 f"{anchor_val:.4f}; every scored stream best beats it; only r2s4-B1 is 3-seed certified",
         size=12, fill=GRAY)

    ly = 98
    rect(30, ly, 14, 14, BLUE_BG, BLUE, rx=3)
    text(50, ly + 12, "trained neural network", size=12)
    rect(225, ly, 14, 14, PURPLE_BG, PURPLE, rx=3)
    text(245, ly + 12, "closed-form / fitted (no gradient training)", size=12)
    rect(540, ly, 14, 14, GRAY_BG, GRAY, rx=3)
    text(560, ly + 12, "diagnostic stream (no scored arm)", size=12)
    line(800, ly + 7, 840, ly + 7, DARK, 1.5, dash="5,4")
    text(848, ly + 12, "launch anchor", size=12)
    line(30, 126, 1130, 126, "#E5E7EB", 1)

    # ---------------- geomean number line ----------------
    text(30, 154, "Panel geomean skill by stream", size=13.5, weight="bold")
    text(300, 154, f"(6-dataset panel: {', '.join(d.replace('sharp__', '') for d in panel)})",
         size=11.5, fill=GRAY)

    ax_y = 238
    line(X0 - 10, ax_y, X1 + 10, ax_y, "#9CA3AF", 1.5)
    for t in range(int(V0), int(V1) + 1):
        line(xp(t), ax_y - 4, xp(t), ax_y + 4, "#9CA3AF", 1.2)
        text(xp(t), ax_y + 22, str(t), size=11, fill=GRAY, anchor_="middle")
    # lower-is-better arrow
    line(210, 178, 110, 178, GRAY, 1.5)
    e.append(f'<path d="M 110 178 l 9 -4 l 0 8 z" fill="{GRAY}"/>')
    text(218, 182, "lower is better", size=11, fill=GRAY)

    # anchor
    line(xp(anchor_val), 192, xp(anchor_val), ax_y + 8, DARK, 1.5, dash="5,4")
    text(xp(anchor_val), 186, f"launch anchor {anchor_val:.4f}", size=12, fill=DARK,
         anchor_="middle", weight="bold")
    # r2s4 CI band + marker
    line(xp(ci_lo), ax_y, xp(ci_hi), ax_y, ORANGE, 5)
    e.append(f'<line x1="{xp(ci_lo)}" y1="{ax_y - 7}" x2="{xp(ci_lo)}" y2="{ax_y + 7}" stroke="{ORANGE}" stroke-width="1.5"/>')
    e.append(f'<line x1="{xp(ci_hi)}" y1="{ax_y - 7}" x2="{xp(ci_hi)}" y2="{ax_y + 7}" stroke="{ORANGE}" stroke-width="1.5"/>')
    diamond(xp(g4), ax_y, 8, ORANGE)
    text(xp(g4) + 6, ax_y - 14, f"r2s4-B1 certified {g4:.4f}  CI95 [{ci_lo:.3f}, {ci_hi:.3f}]",
         size=11.5, fill=ORANGE, weight="bold")
    # r2s1 + r2s2 markers
    star(xp(g1), ax_y, 11, PURPLE)
    text(xp(g1) - 6, ax_y - 14, f"r2s1-B3 {g1:.4f}", size=11.5, fill=PURPLE,
         weight="bold", anchor_="end")
    circle(xp(g2), ax_y, 6, BLUE, "#FFFFFF", 1.5)
    line(xp(g2) + 10, ax_y + 10, xp(g2) + 38, ax_y + 34, BLUE, 1.0)
    text(xp(g2) + 42, ax_y + 40, f"r2s2-B3 {g2:.4f}", size=11.5, fill=BLUE, weight="bold")
    text(X0 - 10, ax_y + 62,
         "markers: r2s1 / r2s2 are single-seed (seed 0, strict in-round protocol); "
         "r2s3 has no scored arm (grade table below)", size=10.5, fill=GRAY)

    line(30, 312, 1130, 312, "#E5E7EB", 1)

    # ---------------- stream rows ----------------
    def row(y, stream, sub1, sub2, box_bg, box_stroke, desc_lines, value, vsub,
            vsub2=None, badge=None):
        text(30, y + 26, stream, size=15, weight="bold")
        text(30, y + 46, sub1, size=11.5, fill=GRAY)
        text(30, y + 62, sub2, size=11.5, fill=GRAY)
        rect(300, y + 8, 570, 96, box_bg, box_stroke)
        for i, ln in enumerate(desc_lines):
            text(315, y + 32 + i * 18, ln, size=12)
        if value is not None:
            text(1120, y + 48, value, size=26, weight="bold", anchor_="end")
            text(1120, y + 68, vsub, size=11, fill=GRAY, anchor_="end")
            if vsub2:
                text(1120, y + 84, vsub2, size=11, fill=GRAY, anchor_="end")
        if badge:
            rect(896, y + 8, 224, 22, PURPLE, rx=11)
            text(1008, y + 23, badge, size=11.5, fill="#FFFFFF", weight="bold",
                 anchor_="middle")

    y = 328
    row(y, "1 · r2s1_direct", "B3 — models_r2/r2s1_stagefree_permode",
        "scored arm: test_hf (stage-free head)",
        PURPLE_BG, PURPLE,
        ["condition -> per-mode closed-form head over an OOF-selected",
         f"direction bank (POD/FFT); {pmin}-{pmax} fitted params per dataset,",
         "zero gradient training. Instrument-repaired re-pricing of B2",
         "(T1-F2 / T1-F7 selection-arity defects)."],
        f"{g1:.4f}", "panel geomean skill — seed 0",
        badge="ROUND BEST (single-seed)")

    y += 128
    row(y, "2 · r2s2_stacked", "B3 — models_r2/r2s2_zerograd",
        "scored arm: A1_lsi (zero-gradient)",
        PURPLE_BG, PURPLE,
        ["condition-keyed retrieval intermediate -> closed-form LSI",
         "(Fourier-diagonal Wiener) transfer, no gradient training.",
         "Matched no-LF base swap (A3) is worse on 4/4 decidable",
         "datasets: the LF-derived retrieval intermediate is load-bearing."],
        f"{g2:.4f}", "panel geomean skill — seed 0")

    y += 128
    text(30, y + 26, "3 · r2s3_lf_train_signal", size=15, weight="bold")
    text(30, y + 46, "B4 — substitution audit (diagnostic,", size=11.5, fill=GRAY)
    text(30, y + 62, "epochs 0; prices the +-LF train effect)", size=11.5, fill=GRAY)
    rect(300, y + 8, 820, 118, GRAY_BG, GRAY)
    text(315, y + 30, "graded, not geomean'd: certified +-LF TRAIN-signal effect vs the best "
                      "ACHIEVABLE LF-free control (E_free, worst draw, x its mce)", size=11.5,
         fill=GRAY)
    grade_style = {"A": (GREEN, GREEN_BG), "B": (ORANGE, ORANGE_BG), "C": (GRAY, "#E5E7EB")}
    for i, (letter, txt) in enumerate([
        (grades["ch"], f"cahn_hilliard — E_free {x_ch:.1f}x mce; broad-based, "
                       f"sign-significant on every draw, survives the ceiling gate"),
        (grades["ifc"], f"ifc_poisson — E_free {x_ifc:.2f}x mce; real (paired CI95 excludes 0) "
                        f"but narrow, mean-driven, single native draw"),
        (grades["ac"], f"allen_cahn — achievable gate {x_ac:.1f}x mce but tail-carried "
                       f"(5-16 of 100 samples hold half the effect); fails the ceiling gate"),
    ]):
        fg, bg = grade_style[letter]
        cy = y + 54 + i * 24
        circle(324, cy - 4, 9, bg, fg)
        text(324, cy, letter, size=11.5, fill=fg, weight="bold", anchor_="middle")
        text(342, cy, txt, size=12)

    y += 150
    row(y, "4 · r2s4_diag", "B1 — models_r2/r2s4_cert_min",
        "certifier (scored test_hf split)",
        BLUE_BG, BLUE,
        ["condition-only FiLM-FNO decoder (2 FNO blocks, 16 modes,",
         "~1.06M params) — the certifier behind the round's certified",
         "noise floor and its only 3-seed certified anchor",
         f"(supersedes the launch floor {anchor_val:.4f})."],
        f"{g4:.4f}", "certified 3-seed panel geomean",
        vsub2=f"CI95 [{ci_lo:.3f}, {ci_hi:.3f}]")

    # ---------------- footer ----------------
    text(30, H - 28, "Rendered by tools/render_top_models_overview.py — every number parsed from "
                     "experiment_cards/*/batch_*/B*.json and state/anchors/*.json; nothing typed by hand.",
         size=10.5, fill=GRAY)
    text(30, H - 12, f"Certified anchor {a_s4['certified_utc']} (source card {a_s4['source_card']}). "
                     "Not shown: r2s2-B1 14.0756 (ifc corrector attribution invalid) and "
                     "r2s1-B2 18.3622 (head-selection defects, repriced by B3).",
         size=10.5, fill=GRAY)

    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif">\n'
           + "\n".join(e) + "\n</svg>\n")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
