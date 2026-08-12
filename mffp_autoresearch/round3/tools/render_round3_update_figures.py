#!/usr/bin/env python
"""Render the round-3 mentor-update figures from the batch-1 cards + anchors.

Derived-data rule: these figures are regenerable from the cards; edit nothing by
hand. Outputs land in `round3/docs/figures/`:

  - r3_performance_vs_baselines.png  (ALL certified cards in one combined
    leaderboard chart on a shared copy-LF skill axis, vs the training-free
    floor and the learned baselines)
  - r3_architectures_overview.png    (one schematic per stream, with its
    3-seed panel number and verdict)

Data sources (read-only): experiment_cards/*/batch_1/B1.json part 5,
state/anchors/launch_anchors.json, state/anchors_repaired/noise_floor.json;
round close 2026-08-12 adds the two batch-3 cards' part 5
(experiment_cards/{r3s2_field_reach,r3s3_lf_value}/batch_3/B3.json).
Per operator directive 2026-08-12 the leaderboard is ONE combined chart —
no era panels, no divider, no separate batch-3 axes; the panel-composition
difference is carried by a single dagger footnote line only.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.patches import FancyBboxPatch

ROOT = Path("/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/round3")
FIGDIR = ROOT / "docs" / "figures"
FIGDIR.mkdir(parents=True, exist_ok=True)

INK = "#20232E"; MUTED = "#8A8D9C"; ACCENT = "#5B21B6"; BLUE = "#2563EB"
FLOOR = "#B45309"; GROUND = "#FBFAFC"
plt.rcParams.update({
    "figure.facecolor": GROUND, "axes.facecolor": "#FFFFFF",
    "axes.edgecolor": "#E5E2EE", "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "font.size": 10,
    "axes.titlesize": 10.5, "font.family": "serif",
})

DS_SHORT = {
    "sharp__allen_cahn_2d": "allen_cahn", "sharp__fisher_kpp_2d": "fisher_kpp",
    "sharp__cahn_hilliard": "cahn_hilliard", "ifc_poisson": "ifc_poisson",
    "ifc_heat": "ifc_heat", "sharp__phase_field_crystal_2d": "pfc",
}
# The panel the batch-1/2 cards were REGISTERED on (ADR r3-0004 era).  Card
# skills and their film-unit conversion constant (`_panel_geomean_c`) live on
# this panel and must not be silently re-based.
REGISTERED_PANEL = [
    "sharp__allen_cahn_2d", "sharp__fisher_kpp_2d", "sharp__cahn_hilliard",
    "ifc_poisson", "ifc_heat",
]
# The CURRENT scored panel + report-only list are read from
# state/anchors/launch_anchors.json (`_panel` / `_report_only`, ADR r3-0007),
# never hardcoded here — see load_anchors().

# Every batch-1/2 card with a CERTIFIED 3-seed panel value (r3s2-B2's
# certified value lives in state/anchors/r3s2_field_reach.json and is added
# separately).  Excluded by design: r3s3-B2 (2-dataset diagnostic geomean only,
# no 5-ds panel claim) and r3s4-B2 (diagnostic instrument, 0 panel cells
# scored).  The two batch-3 cards are read by load_batch3() and appear as
# ordinary bars in the same combined chart (dagger footnote carries the
# panel-composition scoping).
CARDS = {
    "r3s1_factorised-B1": dict(label="r3s1 factorised head (B1)"),
    "r3s1_factorised-B2": dict(label="r3s1 factorised head (B2)"),
    "r3s2_field_reach-B1": dict(label="r3s2 IC-reach stack (B1)"),
    "r3s3_lf_value-B1": dict(label="r3s3 LF-value contrast (B1)"),
    "r3s4_audit-B1": dict(label="r3s4 certifier (B1; instrument)"),
}


def _find_key(obj, key):
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for v in obj.values():
            got = _find_key(v, key)
            if got is not None:
                return got
    elif isinstance(obj, list):
        for v in obj:
            got = _find_key(v, key)
            if got is not None:
                return got
    return None


def load_cards():
    out = {}
    for cid in CARDS:
        stream, batch = cid.split("-")
        bn = batch[1:]  # "B1" -> "1"
        p = ROOT / "experiment_cards" / stream / f"batch_{bn}" / f"{batch}.json"
        c = json.loads(p.read_text())
        r5 = c["5_actual_result"]
        three = r5.get("three_seed_reading") or r5
        # panel geomean, 3-seed
        pg = (_find_key(three, "panel_geomean_skill_mean")
              or _find_key(three, "panel_geomean_skill")
              or _find_key(r5, "panel_geomean_skill"))
        if isinstance(pg, dict):
            ci = pg.get("ci95")
            pg = pg.get("mean") or pg.get("value")
        else:
            ci = None
        if ci is None:
            # collect every ci95 in the card and keep the first that brackets our own mean
            cis = []
            def _collect(o):
                if isinstance(o, dict):
                    for k, v in o.items():
                        if k == "ci95" and isinstance(v, list) and len(v) == 2:
                            cis.append(v)
                        else:
                            _collect(v)
                elif isinstance(o, list):
                    for v in o:
                        _collect(v)
            _collect(r5)
            ci = next((c2 for c2 in cis if c2[0] <= float(pg) <= c2[1]), None)
        # per-dataset mean skill: prefer the direct part-5 table over recursive descent
        per_ds = {}
        pd_block = r5.get("per_dataset")
        if not (isinstance(pd_block, dict) and any(ds in pd_block for ds in REGISTERED_PANEL)):
            pd_block = _find_key(three, "per_dataset") or _find_key(r5, "per_dataset") or {}
        for ds in REGISTERED_PANEL:
            v = None
            if isinstance(pd_block, dict) and ds in pd_block:
                cell = pd_block[ds]
                if isinstance(cell, dict):
                    v = (cell.get("mean_skill") or cell.get("skill_mean")
                         or cell.get("mean") or cell.get("skill"))
                    if isinstance(v, dict):
                        v = v.get("mean")
                elif isinstance(cell, (int, float)):
                    v = cell
            per_ds[ds] = float(v) if isinstance(v, (int, float)) else None
        if not (isinstance(ci, list) and len(ci) == 2 and ci[0] <= float(pg) <= ci[1]):
            ci = None  # _find_key can land on an unrelated nested ci95 (e.g. an anchor's); accept only a bracket of our own mean
        out[cid] = dict(panel=float(pg), ci=ci, per_ds=per_ds)
    return out


def load_anchors():
    a = json.loads((ROOT / "state" / "anchors" / "launch_anchors.json").read_text())
    best_floor = a["best_floor"]["value"]
    per = a["best_floor"]["per_dataset"]
    floors_ds = {ds: (v["skill"] if isinstance(v, dict) else float(v)) for ds, v in per.items()}
    # report-only floor cells (e.g. ifc_poisson under ADR r3-0007) are carried
    # outside best_floor; pick them up from ifc_floors_repaired when present.
    for ds, v in (a.get("ifc_floors_repaired") or {}).items():
        if ds not in floors_ds:
            got = v.get("skill") if isinstance(v, dict) else (float(v) if isinstance(v, (int, float)) else None)
            if got is None and isinstance(v, dict):
                got = _find_key(v, "skill")
            if got is not None:
                floors_ds[ds] = float(got)
    r2 = {card: dict(mean=e["mean"], ci=e.get("ci95"))
          for card, e in a["cards"].items() if "mean" in e}
    scored = list(a["_panel"])
    report_only = list(a.get("_report_only", []))
    return best_floor, floors_ds, r2, scored, report_only


def load_r3s2_b2():
    """The round's best model (r3s2-B2 certified stream anchor), if certified."""
    p = ROOT / "state" / "anchors" / "r3s2_field_reach.json"
    if not p.exists():
        return None
    s = json.loads(p.read_text())
    if s.get("provisional"):
        return None
    return dict(panel=float(s["value"]), ci=list(s["ci95"]),
                per_ds={ds: float(v) for ds, v in s.get("per_dataset_mean_skill", {}).items()})


def load_film():
    """ADR r3-0006 conversion constants; None if the denominator is not yet certified."""
    p = ROOT / "state" / "anchors" / "film_denominator.json"
    if not p.exists():
        return None
    return json.loads(p.read_text())


def load_batch3():
    """Batch-3 rows, read verbatim from the two B3 cards' adjudicated part 5.

    Both enter the combined leaderboard as ordinary bars (operator directive
    2026-08-12): r3s2-B3 as its 5-cell anchor-comparand (same dataset
    composition as the batch-1/2 panel), r3s3-B3 as its registered ADR
    r3-0007 scored-panel value (pfc in place of ifc_poisson) with a dagger
    footnote carrying that scoping.
    """
    out = {}
    p = ROOT / "experiment_cards" / "r3s2_field_reach" / "batch_3" / "B3.json"
    if p.exists():
        r5 = json.loads(p.read_text())["5_actual_result"]
        va = r5["vs_anchor"]
        pg = r5["panel_geomean_skill"]
        out["r3s2_B3"] = dict(
            comparand=float(va["this_card_mean_same_subset"]),
            comparand_ci=list(va["this_card_ci95"]),
            anchor=float(va["anchor_value"]), anchor_ci=list(va["anchor_ci95"]),
            delta=float(va["delta"]), delta_over_mce=float(va["delta_over_seed_mce"]),
            panel6=float(pg["mean"]), panel6_ci=list(pg["ci95"]))
    p = ROOT / "experiment_cards" / "r3s3_lf_value" / "batch_3" / "B3.json"
    if p.exists():
        pg = json.loads(p.read_text())["5_actual_result"]["panel_geomean_skill"]
        f = pg["film_units"]
        out["r3s3_B3"] = dict(
            film=float(f["geomean_skill_film_mean"]),
            film_ci=list(f["geomean_skill_film_ci95"]),
            copylf=float(pg["mean"]), copylf_ci=list(pg["ci95"]))
    return out


def fig_performance(cards, best_floor, r2_anchors, film, scored, batch3):
    """The round-3 leaderboard: ALL certified cards as bars in ONE combined
    chart on a shared copy-LF skill axis (operator directive 2026-08-12 — no
    era panels, no divider, no separate batch-3 axes).  This is a ranking of
    MODELS, not best-per-stream: both r3s2 entries (B1 and B2) stay.
    """
    import numpy as np
    # Conversion constants live per panel composition:
    #   gc_reg — the ADR r3-0004 5-dataset panel (most bars' composition);
    #   gc_cur — the current ADR r3-0007 scored panel (floor lives there).
    gc_reg = film["_panel_geomean_c"]
    gc_cur = float(np.exp(np.mean([np.log(film["datasets"][ds]["c_ds"]) for ds in scored])))
    film_skill = 1.0 / gc_reg  # film-transfer's own copy-LF panel value (14.0770, round3_report.md §2)
    # film-transfer's per-seed panel value in copy-LF units on the same panel
    film_seed_panels = []
    for si in range(3):
        vals = [film["datasets"][ds]["nrmse_film_per_seed"][si] / film["datasets"][ds]["ref_copylf"]
                for ds in REGISTERED_PANEL]
        film_seed_panels.append(float(np.exp(np.mean(np.log(vals)))))
    best_anchor = min(r2_anchors.items(), key=lambda kv: kv[1]["mean"])
    best_anchor_ratio = best_anchor[1]["mean"] * gc_cur

    fig, ax = plt.subplots(figsize=(13.5, 7.4), constrained_layout=True)
    fig.suptitle(
        "Round 3 final leaderboard (round closed 2026-08-12, all 10 cards complete) — every certified card in one combined chart,\n"
        "ranked by 3-seed panel geomean skill (copy-LF units: error ÷ copy-LF; lower = better; whiskers = 95% CI).\n"
        "Reference lines: mf_fno_transfer_film learned baseline = 14.08 copy-LF (solid; shaded band = its 3-seed panel spread);\n"
        "convnext U-Net (dotted) — dead heat with film, within seed noise; training-free floor = 53.21 (dashed; no model: best of NN / mean / zero; ADR r3-0007 panel).\n"
        "Purple = beats the film baseline; each bar is annotated with its film-unit reading.\n"
        "ifc_poisson is demoted to report-only (ADR r3-0007): its condition→field map is exactly linear — a closed-form task;\n"
        "no learned model ever beat copy-LF there; its values remain in the state records.\n"
        "† r3s3-B3 is scored on the ADR r3-0007 panel (pfc in place of ifc_poisson); all other bars share the ADR r3-0004 5-dataset panel.\n"
        "   r3s2-B3 shown as its 5-cell anchor-comparand (same datasets as the batch-1/2 panel).\n"
        f"Round-2 reference models are not shown as bars: the best carried-forward family (r2s3) sits at {best_anchor_ratio:.2f}x film on the current panel (state/anchors/launch_anchors.json).",
        fontsize=9.5, x=0.02, ha="left")

    UNET_C = "#7FA8E8"
    MISS_C = "#C7BCE3"  # certified but does not beat the film baseline
    rows = []  # (label, val, lo, hi, film_ratio)
    b2 = load_r3s2_b2()
    if b2 is not None:
        rows.append(("r3s2 IC-stack (B2 repair)", b2["panel"],
                     b2["panel"] - b2["ci"][0], b2["ci"][1] - b2["panel"],
                     b2["panel"] * gc_reg))
    for cid, meta in CARDS.items():
        d = cards[cid]
        lo, hi = ((d["panel"] - d["ci"][0], d["ci"][1] - d["panel"]) if d["ci"] else (0, 0))
        rows.append((meta["label"], d["panel"], lo, hi, d["panel"] * gc_reg))
    b3s2 = batch3.get("r3s2_B3")
    if b3s2 is not None:
        v, ci = b3s2["comparand"], b3s2["comparand_ci"]
        rows.append(("r3s2-B3 (anchor-comparand)", v, v - ci[0], ci[1] - v, v * gc_reg))
    b3s3 = batch3.get("r3s3_B3")
    if b3s3 is not None:
        v, ci = b3s3["copylf"], b3s3["copylf_ci"]
        # its film-unit reading is the card's own adjudicated film record, not a
        # gc_reg conversion (its registered composition differs — see footnote)
        rows.append((r"r3s3-B3$^{\dagger}$", v, v - ci[0], ci[1] - v, b3s3["film"]))
    rows.sort(key=lambda r: r[1])
    labels = []
    for rank, (label, v, lo, hi, ratio) in enumerate(rows, start=1):
        y = -(rank - 1)
        beats = ratio < 1.0
        ax.barh(y, v, color=(ACCENT if beats else MISS_C), alpha=0.9, height=0.55,
                xerr=[[lo], [hi]], error_kw=dict(ecolor=INK, capsize=3, lw=1), zorder=2)
        ax.annotate(f"{v:.4f}  ·  {ratio:.2f}× film" + (" — beats film" if beats else ""),
                    (v + (hi or 0), y), textcoords="offset points", xytext=(8, 0),
                    fontsize=7.8, color=(ACCENT if beats else INK),
                    fontweight="bold" if beats else "normal", va="center", ha="left", zorder=4)
        labels.append(f"{rank}.  {label}")
    ax.set_yticks([-i for i in range(len(rows))], labels)
    ax.set_ylim(-(len(rows) - 1) - 0.8, 1.55)
    # learned baselines as reference lines (film solid; U-Net dotted);
    # shaded band = film's own 3-seed panel spread
    ax.axvspan(min(film_seed_panels), max(film_seed_panels), color=BLUE, alpha=0.08, zorder=0)
    ax.axvline(film_skill, color=BLUE, ls="-", lw=1.4, zorder=1)
    unet_val = None
    unet_p = ROOT / "state" / "anchors" / "unet_baseline.json"
    if unet_p.exists():
        u = json.loads(unet_p.read_text())
        unet_val = u["_panel_geomean_ratio_to_film"] * film_skill
        ax.axvline(unet_val, color=UNET_C, ls=":", lw=1.6, zorder=1)
    note = f"reference: mf_fno_transfer_film = {film_skill:.2f} copy-LF (solid; band = its 3-seed spread)"
    if unet_val is not None:
        note += f"\nconvnext U-Net = {unet_val:.2f} (dotted) — dead heat with film, within seed noise"
    ax.annotate(note, (film_skill + 0.5, 1.05), fontsize=7.4, color=BLUE, ha="left", va="center", zorder=4)
    ax.axvline(best_floor, color=FLOOR, ls="--", lw=1.4, zorder=1)
    ax.text(best_floor - 0.5, -1.5, f"training-free floor {best_floor:.2f}\n(no model: best of NN / mean / zero;\nADR r3-0007 panel)",
            color=FLOOR, fontsize=7.6, va="center", ha="right")
    all_vals = [r[1] + r[3] for r in rows]
    ax.set_xlim(0, max(best_floor * 1.06, max(all_vals) * 1.12))
    ax.set_xlabel("panel geomean skill, copy-LF units (error ÷ copy-LF), 3-seed mean, 95% CI (lower = better)")

    out = FIGDIR / "r3_performance_vs_baselines.png"
    fig.savefig(out, dpi=170)
    plt.close(fig)
    return out


ARCH = [
    ("Two-stage factorised head (r3s1) — 24.96 [24.87, 25.07] · CONFIRMED",
     ["condition vector\n(the 2–50 numbers that define the physics setup)",
      "stage 1 — closed-form regression:\npredict the weight of each of ~50 principal field shapes\n(POD basis) from the condition; one small cross-validated\nmap per shape, keep only the predictable ones",
      "stage 2 — gated correction:\nre-predict the poorly-fit weights from the well-fit ones,\nonly where cross-validation says it helps",
      "weights × shapes → fine-grid field"],
     "No neural network anywhere; the whole model is ~150 parameters.\nIts improvement is real only on cahn_hilliard; the found limit is an\narbitrary cap on how many shapes stage 1 may keep — not the idea itself.\nBatch 2: the calibrated selection rule lost to the plain cap fix;\nstream consolidated (its fisher_kpp basis is the binding constraint)."),
    ("Initial-condition stack (r3s2) — 12.96 [10.32, 17.83] · corrector FALSIFIED",
     ["condition vector\n(now includes the initial-condition coefficients)",
      "stage 1 — neural field generator:\na FiLM-conditioned Fourier neural operator synthesizes\na stand-in coarse field directly from the condition",
      "stage 2 — frozen corrector:\na network trained earlier on real coarse fields\nupgrades the synthetic coarse field to fine",
      "fine-grid field"],
     "Question: does routing through a synthetic coarse field help?\nAnswer: all measurable value is stage 1 using the IC information;\nstage 2 adds nothing resolvable (same null as round 2).\nBatch 2: repaired corrector instrument → round-best 10.09 (0.72× film).\nBatch 3 (closed, CONFIRMED): the ceiling is a scalar identity with stage-1's\nown LF error — unity gain, low-wavenumber failure; the detour is retired."),
    ("Value-of-coarse-data contrast (r3s3) — 11.08 [10.84, 11.25] · no resolvable delta",
     ["condition vector",
      "ONE multi-resolution Fourier neural operator,\ntrained repeatedly under controlled data diets:\nall coarse solves / coarse solves only at parameters the\nfine data already covers / no coarse solves at all",
      "the comparison of those training diets IS the result:\nwhat do coarse solves buy, and through which channel?",
      "fine-grid field (identical network interface at test)"],
     "Answer: coarse solves help ONLY by covering new parameter points\n(the covered-only diet learns the same function as no-coarse-data);\nheadline vs-baseline win retracted after the baseline repair.\nBatch 2: cost-curve knee confirmed at c* = 80 coarse conditions.\nBatch 3 (closed, FALSIFIED): the sealed knee predictions missed 6–19× τ —\nthe surrogate is a different learner's learning curve; its arm still beat film."),
    ("Noise-floor certifier (r3s4) — 19.64 [19.42, 19.93] · thresholds CERTIFIED",
     ["condition vector",
      "not a competitor — an instrument:\na fixed reference model plus the training-free predictors,\nre-run across seeds and data resamples",
      "bootstrap the spread → per-dataset minimum detectable\ndifference and claim thresholds (τ)",
      "certified noise floor:\nthe bar every other claim in the round must clear"],
     "Also audits the benchmark itself: this batch it priced the audit\ninstruments (one staleness rule: 0 true positives, 62 false alarms → deleted).\nBatch 2: six-role checkpoint↔data binding instrument CONFIRMED 108/108;\nnow a hard gate in every anchor build. Stream consolidated."),
]

VERDICT_KEY = (
    "How to read the verdicts\n"
    "CONFIRMED — the pre-registered prediction passed its threshold at 3 seeds.\n"
    "FALSIFIED — the pre-registered prediction failed its threshold; reported as a finding, not a process failure.\n"
    "CERTIFIED — measured at 3 seeds AND priced against the audited minimum-detectable-effect table (the strongest label).\n"
    "not resolvable — the measured difference is smaller than the certified minimum detectable effect; no claim either way.")


def fig_architectures():
    fig = plt.figure(figsize=(12.5, 10.6), constrained_layout=True)
    gs = GridSpec(3, 2, figure=fig, height_ratios=[1, 1, 0.30])
    fig.suptitle(
        "Round 3 — the four experiment lines (every model maps condition → fine-grid field; no solver, no coarse field at test)\n"
        "Number = 3-seed batch-1 panel error [95% CI], lower is better; the no-training reference at batch-1 registration = 34.42\n"
        "(on the current ADR r3-0007 scored panel — pfc in, ifc_poisson report-only — the training-free floor is 53.21).",
        fontsize=10.5, x=0.02, ha="left")
    for k, (title, boxes, note) in enumerate(ARCH):
        ax = fig.add_subplot(gs[k // 2, k % 2])
        ax.set_axis_off()
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)
        ax.set_title(title, loc="left", fontsize=9.3, fontweight="bold", pad=6)
        # geometry: boxes live in [0.30, 0.99]; the note lives in [0.0, 0.24]. All inside the axes.
        n = len(boxes)
        heights = [0.10 if i in (0, n - 1) else 0.185 for i in range(n)]
        top, bottom = 0.99, 0.30
        gap = (top - bottom - sum(heights)) / (n - 1)
        ys, y = [], top
        for i in range(n):
            ys.append(y - heights[i] / 2)
            y -= heights[i] + gap
        for i, (by, text) in enumerate(zip(ys, boxes)):
            first_last = i == 0 or i == n - 1
            fc = "#F1EFF7" if not first_last else "#FFFFFF"
            ec = ACCENT if not first_last else MUTED
            ax.add_patch(FancyBboxPatch((0.02, by - heights[i] / 2), 0.96, heights[i],
                                        boxstyle="round,pad=0.010", fc=fc, ec=ec, lw=1.2))
            ax.text(0.5, by, text, ha="center", va="center", fontsize=8.0, color=INK, linespacing=1.35)
            if i < n - 1:
                ax.annotate("", xy=(0.5, ys[i + 1] + heights[i + 1] / 2 + 0.003),
                            xytext=(0.5, by - heights[i] / 2 - 0.003),
                            arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.2))
        ax.text(0.5, 0.12, note, ha="center", va="center", fontsize=7.7, color=MUTED, linespacing=1.4)
    axk = fig.add_subplot(gs[2, :])
    axk.set_axis_off()
    axk.set_xlim(0, 1); axk.set_ylim(0, 1)
    axk.add_patch(FancyBboxPatch((0.01, 0.04), 0.98, 0.92, boxstyle="round,pad=0.006",
                                 fc="#FFFFFF", ec="#C9CDC9", lw=1.0))
    axk.text(0.03, 0.5, VERDICT_KEY, ha="left", va="center", fontsize=8.6, color=INK, linespacing=1.75)
    out = FIGDIR / "r3_architectures_overview.png"
    fig.savefig(out, dpi=170)
    plt.close(fig)
    return out


def _flow_panel(ax, title, boxes, kinds):
    """Vertical box flow inside one axes. kinds: 'io' | 'core' | 'note' per box."""
    ax.set_axis_off()
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_title(title, loc="left", fontsize=9.0, fontweight="bold", pad=5)
    n = len(boxes)
    weights = [{"io": 1.0, "note": 1.35, "core": 1.9}[k] for k in kinds]
    total_w = sum(weights)
    avail = 0.97
    gap = 0.035
    box_space = avail - gap * (n - 1)
    heights = [box_space * w / total_w for w in weights]
    ys, y = [], 0.985
    for i in range(n):
        ys.append(y - heights[i] / 2)
        y -= heights[i] + gap
    for i, (by, text, kind) in enumerate(zip(ys, boxes, kinds)):
        fc = {"io": "#FFFFFF", "core": "#F1EFF7", "note": "#FBFAFC"}[kind]
        ec = {"io": MUTED, "core": ACCENT, "note": "#C9CDC9"}[kind]
        ax.add_patch(FancyBboxPatch((0.015, by - heights[i] / 2), 0.97, heights[i],
                                    boxstyle="round,pad=0.008", fc=fc, ec=ec, lw=1.1))
        ax.text(0.5, by, text, ha="center", va="center", fontsize=7.4, color=INK, linespacing=1.3)
        if i < n - 1:
            ax.annotate("", xy=(0.5, ys[i + 1] + heights[i + 1] / 2 + 0.002),
                        xytext=(0.5, by - heights[i] / 2 - 0.002),
                        arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.1))


def fig_model_detail(fname, suptitle, left_title, left_boxes, left_kinds,
                     right_title, right_boxes, right_kinds, findings):
    fig = plt.figure(figsize=(12.5, 9.2), constrained_layout=True)
    gs = GridSpec(2, 2, figure=fig, height_ratios=[1, 0.20])
    fig.suptitle(suptitle, fontsize=10.2, x=0.02, ha="left")
    _flow_panel(fig.add_subplot(gs[0, 0]), left_title, left_boxes, left_kinds)
    _flow_panel(fig.add_subplot(gs[0, 1]), right_title, right_boxes, right_kinds)
    axk = fig.add_subplot(gs[1, :])
    axk.set_axis_off(); axk.set_xlim(0, 1); axk.set_ylim(0, 1)
    axk.add_patch(FancyBboxPatch((0.005, 0.03), 0.99, 0.94, boxstyle="round,pad=0.006",
                                 fc="#FFFFFF", ec="#C9CDC9", lw=1.0))
    axk.text(0.02, 0.5, findings, ha="left", va="center", fontsize=8.0, color=INK, linespacing=1.6)
    out = FIGDIR / fname
    fig.savefig(out, dpi=170)
    plt.close(fig)
    return out


def fig_top_models():
    # "The architectures that beat the learned baseline": one figure per
    # beat-film architecture.  The two r3s2 IC-stack variants (B1 0.92×, B2
    # 0.72×) share one structure, so figure 1 shows ONE diagram plus an
    # explicit B2-repair-delta callout; figure 2 is r3s3's A1 arm (0.79×).
    p3 = fig_model_detail(
        "r3_model_detail_ic_stack.png",
        "Beats the learned baseline (1 of 2) — r3s2 initial-condition stack · B1 = 0.92× film · B2 (LSI repair) = 0.72× film — the round's best model\n"
        "One architecture, two batches: batch 2 changes ONLY the corrector's spectral least-squares-inversion (LSI) filter; everything else is identical.\n"
        "Verdicts: IC channel CONFIRMED (the entire measurable effect) · corrector value FALSIFIED · B2's stack beats the matched-budget direct route at panel level.",
        "Shared architecture, B1 and B2 — how it predicts (test time: condition only, no solver)",
        ["condition vector  (2–50 numbers: PDE coefficients, boundary/forcing\nparameters, and — new in round 3 — the initial-condition coefficients ic_c*)",
         "FRONT END · exact analytic IC synthesis (zero learned parameters)\nthe ic_c* coefficients are expanded as their trigonometric sum on the\ncoarse grid — the model is handed the true initial condition as a field;\nthe remaining condition dims enter as FiLM modulation",
         "STAGE 1 · pseudo-coarse generator\nFiLM-conditioned Fourier neural operator: 4 spectral blocks, width 64,\n12 Fourier modes — synthesizes the coarse field the solver would have\nproduced (32²/64² sharp, 8–32² ifc)",
         "registered lift  (the benchmark's certified per-dataset interpolation\nconvention raises the coarse field onto the fine grid)",
         "STAGE 2 · frozen corrector — trained on REAL coarse→fine pairs in an\nearlier round, then frozen: closed-form spectral LSI filter T(k), then a\nlocal CNN with a pixel-wise gate (7×7 kernels, depth 4, width 32)\n← the LSI filter is the part batch 2 repairs",
         "fine-grid field  (128² sharp / 64² ifc)"],
        ["io", "core", "core", "io", "core", "io"],
        "The B2 repair delta — and how the stack is trained",
        ["B2 REPAIR DELTA (the only change vs B1) — regularise the least-squares\ninversion: B1 fits the corrector's spectral filter T(k) by plain LSI from\nas few as 3 samples; one seed fitted a 66× amplification and cratered\nifc_poisson.  B2 zeroes T(k) above the coarse grid's Nyquist\n(k_cut = k_Nyq_HF · N_LF/N_HF) and ridges the inversion with a\nLOOCV-selected coefficient, chosen on the fit fold only.",
         "repair effect: stream best 12.96 → 10.09 (0.92× → 0.72× film).  A\nreplication arm reproduced B1's blow-up digit-for-digit (66.219…),\nproving the band-limit removed it — not re-implementation drift.",
         "how it is trained: STAGE 1 learns condition → real coarse field (~400\ncheap coarse solves per sharp dataset, only 5 fine fields on ifc;\nrel-L2 loss; the fine fields never enter stage 1).  STAGE 2 stays frozen;\nB2 holds every arm at the same total optimizer budget (300 epochs)",
         "at test the real solver is gone: the stack must generate its own\ncoarse field — the benchmark's deployment premise"],
        ["core", "note", "core", "note"],
        "What the round established:  the initial-condition information is the entire measurable effect, and it acts in STAGE 1 (63.7% / 85.4% of generator error removed on\n"
        "allen_cahn / fisher_kpp; a fake IC does worse than none).  The corrector stage adds nothing resolvable — round 2's null replicates (0.0056 vs 0.0061).  B2's repair\n"
        "removed the one failure mode (the 66× spectral amplification fitted from 3 samples), lifting the stream best from 12.96 (0.92× film) to 10.09 (0.72× film) — the\n"
        "round's best model.  Remaining weakness: both ifc cells still lose to a 6-parameter affine fit (floors now quoted with their leave-one-out fold range per ADR r3-0007).\n"
        "Batch 3 (ceiling card, CONFIRMED) closed the stream: the synthetic-coarse-field detour's value is capped by a scalar identity — the corrector passes stage-1's own LF\n"
        "error through at unity gain (0.80–1.02 on 6/6 cells), so the route is retired; the B3 replication matched the anchor within noise (+0.39 = 0.77× seed-mce).")

    p4 = fig_model_detail(
        "r3_model_detail_lf_channels.png",
        "Beats the learned baseline (2 of 2) — r3s3 LF-value contrast: LF-trained multi-resolution FNO (arm A1, B1) · 0.79× film · panel 11.08 [10.84, 11.25]\n"
        "One network, one loss trick: it learns from cheap coarse solves at hundreds of conditions while seeing only 5–400 expensive fine fields.\n"
        "Verdict: CONFIRMED — coarse data helps by covering new parameter points (supply), not by regularizing; the pre-repair vs-baseline headline was retracted.",
        "How it predicts (test time — condition only, no solver)",
        ["condition vector",
         "multi-resolution Fourier neural operator\n4 spectral blocks, width 64; Fourier modes pinned to the coarsest\nrung's Nyquist (cap 12) so every resolution shares one spectral\nbasis; per-rung output heads share the backbone",
         "only the FINE head is read out at test\n(the coarse heads exist purely to absorb training signal)",
         "fine-grid field"],
        ["io", "core", "core", "io"],
        "How it is trained (the part that makes it the round's best value-of-data story)",
        ["joint loss over resolutions: predict the coarse solve at every rung\nAND the fine field, equally weighted (λ_LF = 1);\nHF batch 5, LF batch 16; ~400 coarse rows vs as few as 5 fine rows",
         "the coarse rows enter at conditions the fine data never covers —\nhundreds of extra (condition → field) examples at low cost",
         "controlled arms isolate WHY it works: same network trained with\nno coarse data (A0), coarse data only at already-covered conditions\n(A2), and the full pool (A1)",
         "batch 2 confirmed the cost curve's knee: c* = 80 distinct coarse\nconditions on cahn_hilliard (7× the clause floor); batch 3 seals the\nsurrogate's knee predictions (sha256) before any training run"],
        ["core", "note", "core", "note"],
        "What the round established:  the coarse data's value is SUPPLY, not regularization — the covered-only arm (A2) learns the same function as no-coarse-data (A0), while new\n"
        "condition rows explain E_cov/E_total ≈ 1.0 on 30/30 cells.  Recovery tracks a measurable intermediate (condition–response alignment, r = 0.985).  Its headline vs-baseline\n"
        "win from before the anchor repair (−10.1%) was retracted as a stale-baseline artifact; what survives is the mechanism and the strongest panel number of batch 1 (11.08,\n"
        "0.79× film-transfer).  It is the best model on ifc_heat (0.07 = 15× better than copying the solver) and fisher_kpp.  Batch 2 confirmed the cost-curve knee at c* = 80 and a\n"
        "training-free surrogate for it.  Batch 3 (closed, FALSIFIED): the surrogate's sealed knee predictions missed at 6–19× τ_rel_film on both adjudicable cells — it is the\n"
        "learning curve of a DIFFERENT learner — while the same card's trained arm scored the round's best film-unit result (0.5780 [0.5606, 0.5897]).")
    return p3, p4


def main():
    cards = load_cards()
    best_floor, floors_ds, r2, scored, report_only = load_anchors()
    film = load_film()
    if film is None:
        raise SystemExit("film_denominator.json not built yet (ADR r3-0006) — run make_film_denominator.py first")
    batch3 = load_batch3()
    missing = [(cid, ds) for cid, d in cards.items() for ds, v in d["per_ds"].items() if v is None]
    if missing:
        print("WARN: per-dataset values not found for:", missing)
    print("scored panel:", scored, "report-only:", report_only, "best_floor:", best_floor)
    print("batch3 era rows:", json.dumps(batch3, indent=1))
    p1 = fig_performance(cards, best_floor, r2, film, scored, batch3)
    p2 = fig_architectures()
    p3, p4 = fig_top_models()
    print("wrote", p3)
    print("wrote", p4)
    print("wrote", p1)
    print("wrote", p2)
    for cid, d in cards.items():
        print(cid, "panel", d["panel"], "ci", d["ci"], "per_ds", {DS_SHORT[k]: v for k, v in d["per_ds"].items()})


if __name__ == "__main__":
    main()
