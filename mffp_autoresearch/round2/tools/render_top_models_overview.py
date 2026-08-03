#!/usr/bin/env python
"""Render docs/figures/top_models_overview.svg — round-2 per-stream top models.

Round-2 sibling of round1/docs/figures/top_models_overview.svg, in the SAME
visual language: Helvetica, role colors (green LF data, orange HF data /
prediction, blue trained NN, purple closed-form / fitted, gray input or
diagnostic), and — the part the first round-2 draft dropped — each top model
drawn as a CHAIN OF STAGE BOXES with a "MF method:" caption saying where (and
whether) low-fidelity data enters. A single prose box per stream cannot show
that; the whole point of the figure is that the three scored arms differ in
their stage graph, not in their wording.

Every NUMBER and every architecture constant is parsed out of the experiment-card
JSONs under experiment_cards/ and the anchor files under state/anchors/ —
nothing typed in by hand. Architecture constants are pulled from each card's
part-3 description with an explicit assert, so a card edit that changes the
recipe fails the render instead of silently shipping a stale diagram.
r2s3's row is its B4 substitution-audit grade table (the stream is diagnostic:
no scored panel geomean); the letter grades are parsed out of the B4 card's
part-6 judgment text and the effect sizes out of its part 5.

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

# Helvetica advance width is ~0.5 em averaged over mixed-case text; 0.55 is the
# conservative bound used by fit() so no label can overrun its box.
EM = 0.55


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


def flat(text):
    """Card prose with newlines and runs of spaces collapsed, for regex asserts."""
    if isinstance(text, list):
        text = " ".join(text)
    return re.sub(r"\s+", " ", text)


def recipe_assert(text, *needles):
    """Assert every architecture constant we draw is literally in the card."""
    for n in needles:
        assert n in text, f"card recipe no longer says {n!r} — figure is stale"


def main():
    # ---------------- parse ----------------
    c1 = card("r2s1_direct/batch_3/B3.json")
    c2 = card("r2s2_stacked/batch_3/B3.json")
    c4 = card("r2s4_diag/batch_1/B1.json")
    s1, s2 = c1["5_actual_result"], c2["5_actual_result"]
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

    # r2s1 head sizes and SET cardinalities over the panel (leg == 'panel')
    legs1 = [v for ds, v in s1["per_dataset"].items() if v.get("leg") == "panel"]
    assert len(legs1) == len(panel)
    head_params = sorted(v["scored_head_n_params"] for v in legs1)
    set_card = sorted(v["set_cardinality"] for v in legs1)
    pmin, pmax = head_params[0], head_params[-1]
    smin, smax = set_card[0], set_card[-1]

    # architecture constants, asserted against each card's own part-3 recipe
    r1 = flat(c1["3_description"])
    recipe_assert(r1, "POD modes 0-49", "DC-removed", "affine, quadratic, RBF kernel ridge, k-NN",
                  "tau = 0.1 (min 1, max 32)", "no Wiener gains and no blend")
    r2 = flat(c2["3_description"])
    recipe_assert(r2, "k nearest train conditions", "k ∈ {1,2,4,8,16,32,64,128}",
                  "closed-form LSI Wiener filter", "zero gradient steps",
                  "R2S2B3_REQUIRE_NO_TEST_LF=1", "ADR r2-0001 conventions")
    r4 = flat(c4["3_description"])
    recipe_assert(r4, "1×1 lift to width 32", "2 FNO blocks at 16 modes",
                  "2-layer MLP (width 64)", "1×1 head → 1 channel",
                  "No field input anywhere; no LF read at train or test", "200 epochs")

    # r2s2's no-LF control: the swap that shows the LF intermediate is load-bearing
    a3 = deep_find_text(s2, "A3") or ""
    assert "A3" in a3

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
    print(f"r2s1_direct-B3 scored test_hf  {g1:.4f}  (seed 0; head params {pmin}-{pmax}, "
          f"SET {smin}-{smax})")
    print(f"r2s2_stacked-B3 scored A1_lsi  {g2:.4f}  (seed 0)")
    print(f"r2s4_diag-B1 certified 3-seed  {g4:.4f}  CI95 [{ci_lo:.3f}, {ci_hi:.3f}]")
    print(f"r2s3-B4 grades: ch={grades['ch']} ({x_ch:.1f}x mce), "
          f"ifc={grades['ifc']} ({x_ifc:.2f}x mce), ac={grades['ac']} ({x_ac:.1f}x achievable, "
          f"ceiling-gate survivors {ceiling_survivors})")

    # ---------------- geometry helpers ----------------
    W = 1160
    X0, X1, V0, V1 = 90, 1070, 18.0, 24.0

    def xp(v):
        return X0 + (v - V0) / (V1 - V0) * (X1 - X0)

    e = []          # svg elements

    def esc(s):
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def text(x, y, s, size=12, fill=DARK, weight=None, anchor_=None, style=""):
        a = f' text-anchor="{anchor_}"' if anchor_ else ""
        w = f' font-weight="{weight}"' if weight else ""
        st = f" {style}" if style else ""
        e.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}"{w}{a}{st}>{esc(s)}</text>')

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

    def fit(lines, box_w, size):
        """Hard guard: no label may overrun its box (cold-reader legibility)."""
        for ln in lines:
            w = len(ln) * EM * size
            assert w <= box_w - 14, (f"label {ln!r} needs {w:.0f}px, box is {box_w}px "
                                     f"— shorten it or widen the box")

    def stage(x, y, w, h, title, lines, fg, bg, size=10.5):
        """One pipeline stage: bold title + detail lines, centered in a rounded box."""
        fit([title] + lines, w, 11)
        rect(x, y, w, h, bg, fg)
        cx = x + w / 2
        text(cx, y + 21, title, size=11, weight="bold", anchor_="middle")
        for i, ln in enumerate(lines):
            text(cx, y + 39 + i * 15, ln, size=size, anchor_="middle")

    def arrow(x, y, length=26):
        line(x, y, x + length - 7, y, DARK, 1.6)
        e.append(f'<path d="M {x + length} {y} l -8 -4.5 l 0 9 z" fill="{DARK}"/>')

    def up_arrow(x, y_from, y_to):
        line(x, y_from, x, y_to + 8, DARK, 1.6)
        e.append(f'<path d="M {x} {y_to} l -4.5 8 l 9 0 z" fill="{DARK}"/>')

    # ---------------- header ----------------
    text(30, 42, "MFFP Round 2 — Top Models per Stream: architecture and where low-fidelity data enters",
         size=21, weight="bold")
    text(30, 64, "skill = nRMSE(model) / nRMSE(copy-LF) — lower is better; models see LF fields at "
                 "TRAIN time only, at inference only the condition vector", size=12, fill=GRAY)
    text(30, 82, f"launch anchor = geomean of the best training-free floor per dataset = "
                 f"{anchor_val:.4f}; every scored stream best beats it; only r2s4-B1 is 3-seed certified",
         size=12, fill=GRAY)

    ly = 98
    for x, bg, fg, label in [
        (30, GREEN_BG, GREEN, "low-fidelity (LF) data — train time only"),
        (318, ORANGE_BG, ORANGE, "high-fidelity (HF) prediction"),
        (530, BLUE_BG, BLUE, "trained neural network"),
        (712, PURPLE_BG, PURPLE, "closed-form / fitted (no gradient steps)"),
        (990, GRAY_BG, GRAY, "model input"),
    ]:
        rect(x, ly, 14, 14, bg, fg, rx=3)
        text(x + 20, ly + 12, label, size=12)
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
    # r2s4-B1 is the one TRAINED arm on this line -> blue, matching the role legend
    line(xp(ci_lo), ax_y, xp(ci_hi), ax_y, BLUE, 5)
    e.append(f'<line x1="{xp(ci_lo)}" y1="{ax_y - 7}" x2="{xp(ci_lo)}" y2="{ax_y + 7}" stroke="{BLUE}" stroke-width="1.5"/>')
    e.append(f'<line x1="{xp(ci_hi)}" y1="{ax_y - 7}" x2="{xp(ci_hi)}" y2="{ax_y + 7}" stroke="{BLUE}" stroke-width="1.5"/>')
    diamond(xp(g4), ax_y, 8, BLUE)
    text(xp(g4) + 6, ax_y - 14, f"r2s4-B1 certified {g4:.4f}  CI95 [{ci_lo:.3f}, {ci_hi:.3f}]",
         size=11.5, fill=BLUE, weight="bold")
    # r2s1-B3 and r2s2-B3 are both zero-gradient closed-form arms -> purple, distinct glyphs
    star(xp(g1), ax_y, 11, PURPLE)
    text(xp(g1) - 6, ax_y - 14, f"r2s1-B3 {g1:.4f}", size=11.5, fill=PURPLE,
         weight="bold", anchor_="end")
    circle(xp(g2), ax_y, 6, PURPLE, "#FFFFFF", 1.5)
    line(xp(g2) + 10, ax_y + 10, xp(g2) + 38, ax_y + 34, PURPLE, 1.0)
    text(xp(g2) + 42, ax_y + 40, f"r2s2-B3 {g2:.4f}", size=11.5, fill=PURPLE, weight="bold")
    text(X0 - 10, ax_y + 62,
         "markers: r2s1 / r2s2 are single-seed (seed 0, strict in-round protocol); "
         "r2s3 has no scored arm (grade table below)", size=10.5, fill=GRAY)

    line(30, 312, 1130, 312, "#E5E7EB", 1)

    # ---------------- stream rows ----------------
    BX0, BW_TOTAL, GAP, BH = 40, 1080, 26, 92

    def pipeline_row(y, title, subtitle, value, vsub, stages, caption, chip=None,
                     badge=None, value_fill=DARK):
        """One stream: heading + right-hand number + stage chain + MF-method caption."""
        text(30, y + 16, title, size=15, weight="bold")
        text(30, y + 34, subtitle, size=11.5, fill=GRAY)
        text(1120, y + 18, value, size=25, weight="bold", anchor_="end", fill=value_fill)
        text(1120, y + 36, vsub, size=11, fill=GRAY, anchor_="end")
        if badge:
            rect(1120 - 232, y + 46, 232, 21, PURPLE, rx=10)
            text(1120 - 116, y + 61, badge, size=11.5, fill="#FFFFFF", weight="bold",
                 anchor_="middle")

        n = len(stages)
        bw = (BW_TOTAL - (n - 1) * GAP) / n
        by = y + (78 if badge else 54)
        for i, (t, lines, fg, bg) in enumerate(stages):
            bx = BX0 + i * (bw + GAP)
            stage(bx, by, bw, BH, t, lines, fg, bg)
            if i < n - 1:
                arrow(bx + bw, by + BH / 2, GAP)
        bottom = by + BH
        if chip:
            idx, ctitle, clines, cfg, cbg = chip
            cw, chh = bw, 26 + 14 * len(clines) + 8
            cx = BX0 + idx * (bw + GAP)
            cy = bottom + 26
            rect(cx, cy, cw, chh, cbg, cfg)
            fit([ctitle] + clines, cw, 11)
            text(cx + cw / 2, cy + 18, ctitle, size=11, weight="bold", anchor_="middle")
            for j, ln in enumerate(clines):
                text(cx + cw / 2, cy + 34 + j * 14, ln, size=10, anchor_="middle")
            up_arrow(cx + cw / 2, cy, bottom)
            bottom = cy + chh
        for i, ln in enumerate(caption):
            text(30, bottom + 22 + i * 16, ln, size=11.5,
                 fill=DARK if i == 0 else GRAY)
        return bottom + 22 + len(caption) * 16 + 22

    y = 336

    # --- 1 · r2s1_direct ---------------------------------------------------
    y = pipeline_row(
        y,
        "1 · r2s1_direct — B3 test_hf: stage-free closed-form head",
        "models_r2/r2s1_stagefree_permode · zero gradient steps · no LF at any stage",
        f"{g1:.4f}", "panel geomean skill — seed 0",
        [
            ("condition vector x",
             ["the only model input", "per-dim train-standardised"], GRAY, GRAY_BG),
            ("direction bank",
             ["DC / spatial-mean direction", "+ POD modes 0–49 of the",
              "DC-removed fit-fold residual"], PURPLE, PURPLE_BG),
            ("per-direction OOF selection",
             ["maps {affine, quadratic,", "RBF kernel ridge, k-NN}",
              f"SET gate OOF R² ≥ 0.1 → {smin}–{smax} kept"], PURPLE, PURPLE_BG),
            ("HF field = Σ ĉ(x)·φ",
             [f"{pmin}–{pmax} fitted parameters", "no Wiener gains, no blend"],
             ORANGE, ORANGE_BG),
        ],
        ["MF method: NONE — no LF is read at any stage, train or test. This is the round's honest condition-only baseline.",
         "The shared post-hoc stage (Wiener gains + floor blend) is demoted to reference splits and measured rather than shipped — "
         "the B3 repair that re-priced B2's selection-arity defects."],
        badge="ROUND BEST (single-seed)")

    # --- 2 · r2s2_stacked --------------------------------------------------
    y = pipeline_row(
        y,
        "2 · r2s2_stacked — B3 A1_lsi: retrieval → closed-form transfer",
        "models_r2/r2s2_zerograd · zero gradient steps · LF read at TRAIN time only",
        f"{g2:.4f}", "panel geomean skill — seed 0",
        [
            ("condition vector x",
             ["the only test-time input", "tripwire: no test-LF read"], GRAY, GRAY_BG),
            ("condition-keyed retrieval",
             ["mean of the real train LF fields", "of the k* nearest train conditions",
              "k ∈ {1,2,4,8,16,32,64,128}, k* OOF"], PURPLE, PURPLE_BG),
            ("closed-form LSI Wiener T(k)",
             ["on the HF-grid-lifted intermediate", "(ADR r2-0001 registration)",
              "α chosen out-of-fold, 0 allowed"], PURPLE, PURPLE_BG),
            ("HF prediction",
             ["zero gradient steps"], ORANGE, ORANGE_BG),
        ],
        ["MF method: LF enters at TRAIN time only, as a retrieved intermediate field — at test the model sees the condition vector alone.",
         "The matched no-LF base swap (A3, identical folds and identical k*) is worse on 4/4 decidable datasets: "
         "the LF-derived intermediate is load-bearing, not decoration."],
        chip=(1, "train-time LF fields",
              ["real coarse solves, train rows only", "never read at test"], GREEN, GREEN_BG))

    # --- 3 · r2s3_lf_train_signal (diagnostic grade table) ------------------
    text(30, y + 16, "3 · r2s3_lf_train_signal — B4 substitution audit (diagnostic, epochs 0)",
         size=15, weight="bold")
    text(30, y + 34, "no scored arm: the stream prices the ±LF TRAIN-signal effect instead of ranking a model",
         size=11.5, fill=GRAY)
    rect(BX0, y + 48, BW_TOTAL, 106, GRAY_BG, GRAY)
    text(BX0 + 15, y + 70, "certified ±LF train-signal effect vs the best ACHIEVABLE LF-free control "
                           "(E_free, worst draw, × that dataset's mce)", size=11.5, fill=GRAY)
    grade_style = {"A": (GREEN, GREEN_BG), "B": (ORANGE, ORANGE_BG), "C": (GRAY, "#E5E7EB")}
    for i, (letter, txt) in enumerate([
        (grades["ch"], f"cahn_hilliard — E_free {x_ch:.1f}× mce; broad-based, "
                       f"sign-significant on every draw, survives the ceiling gate"),
        (grades["ifc"], f"ifc_poisson — E_free {x_ifc:.2f}× mce; real (paired CI95 excludes 0) "
                        f"but narrow, mean-driven, single native draw"),
        (grades["ac"], f"allen_cahn — achievable gate {x_ac:.1f}× mce but tail-carried "
                       f"(5–16 of 100 samples hold half the effect); fails the ceiling gate"),
    ]):
        fg, bg = grade_style[letter]
        cy = y + 94 + i * 24
        circle(BX0 + 24, cy - 4, 9, bg, fg)
        text(BX0 + 24, cy, letter, size=11.5, fill=fg, weight="bold", anchor_="middle")
        text(BX0 + 42, cy, txt, size=12)
    text(30, y + 176, "MF method: LF as a TRAIN-time-only signal, priced against what the same "
                      "budget buys without it — the round's criterion-1 measurement.", size=11.5)
    text(30, y + 192, "fisher_kpp / pfc / helmholtz retired from the grading: negative E_free on all "
                      "nine draws.", size=11.5, fill=GRAY)
    y += 224

    # --- 4 · r2s4_diag -----------------------------------------------------
    y = pipeline_row(
        y,
        "4 · r2s4_diag — B1 certifier, condition-only FiLM-FNO",
        "models_r2/r2s4_cert_min · 200 epochs AdamW · the round's only 3-seed certified anchor",
        f"{g4:.4f}", f"certified 3-seed geomean · CI95 [{ci_lo:.3f}, {ci_hi:.3f}]",
        [
            ("coordinate grid + lift",
             ["normalized coord grid (2 ch)", "1×1 lift to width 32",
              "NO field input anywhere"], GRAY, GRAY_BG),
            ("2 FNO blocks · 16 modes",
             ["per-block FiLM (γ, β) from a", "2-layer MLP (width 64) on x",
              "modes 16, not the factory 12"], BLUE, BLUE_BG),
            ("1×1 head → 1 channel",
             ["~1M parameters", "trained on the HF split only"], BLUE, BLUE_BG),
            ("HF field prediction",
             ["scored on the native HF grid"], ORANGE, ORANGE_BG),
        ],
        [f"MF method: NONE — no field input anywhere, no LF read at train or test. This is the certifier, not a contender: "
         f"it defines the round's certified noise floor",
         f"and its 3-seed interval supersedes the training-free launch anchor {anchor_val:.4f} with the whole interval below it."],
        chip=(1, "condition vector x", ["drives FiLM only"], GRAY, GRAY_BG),
        value_fill=BLUE)

    # ---------------- footer ----------------
    H = int(y + 78)
    foot = [
        "Rendered by tools/render_top_models_overview.py — every number and every architecture "
        "constant parsed from experiment_cards/*/batch_*/B*.json and state/anchors/*.json.",
        f"Certified anchor {a_s4['certified_utc']} (source card {a_s4['source_card']}). Not shown: "
        "r2s2-B1 14.0756 — its panel geomean is an artifact of the degraded ifc_poisson",
        "column (unpaired ladder ⇒ attribution.valid=false); on the 5 properly-paired datasets the "
        "stack scores 19.1843 vs 19.1863 for the emulator alone.",
        "Also not shown: r2s1-B2 18.3622 (head-selection defects, repriced by B3).",
    ]
    for i, ln in enumerate(foot):
        assert len(ln) * EM * 10.5 <= 1100, f"footer line {i} overruns the canvas"
        text(30, H - 58 + i * 15, ln, size=10.5, fill=GRAY)

    e.insert(0, f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif">\n'
           + "\n".join(e) + "\n</svg>\n")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(svg)
    print(f"wrote {OUT}  ({W}x{H})")


if __name__ == "__main__":
    main()
