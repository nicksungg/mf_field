#!/usr/bin/env python
"""Render the round-3 mentor-update figures from the batch-1 cards + anchors.

Derived-data rule: these figures are regenerable from the cards; edit nothing by
hand. Outputs land in `round3/docs/figures/`:

  - r3_performance_vs_baselines.png  (panel geomeans + per-dataset best-model
    skill vs the training-free floors and the repaired round-2 anchors)
  - r3_architectures_overview.png    (one schematic per stream, with its
    3-seed panel number and verdict)

Data sources (read-only): experiment_cards/*/batch_1/B1.json part 5,
state/anchors/launch_anchors.json, state/anchors_repaired/noise_floor.json.
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

# Every round-3 card with a CERTIFIED 3-seed panel value (r3s2-B2's certified
# value lives in state/anchors/r3s2_field_reach.json and is added separately).
# Excluded by design: r3s3-B2 (2-dataset diagnostic geomean only, no 5-ds panel
# claim) and r3s4-B2 (diagnostic instrument, 0 panel cells scored).
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


def fig_performance(cards, best_floor, floors_ds, r2_anchors, film, scored, report_only):
    import numpy as np
    all_ds = scored + [ds for ds in report_only if ds in film["datasets"]]
    c_ds = {ds: film["datasets"][ds]["c_ds"] for ds in all_ds + REGISTERED_PANEL}
    # Conversion constants live per panel era:
    #   gc_reg — the registered batch-1/2 panel (card skills were certified there);
    #   gc_cur — the current ADR r3-0007 scored panel (baselines + floor live there).
    gc_reg = film["_panel_geomean_c"]
    gc_cur = float(np.exp(np.mean([np.log(c_ds[ds]) for ds in scored])))
    # film-transfer's own per-seed panel value in film units on the CURRENT panel
    film_seed_panels = []
    for si in range(3):
        vals = [film["datasets"][ds]["nrmse_film_per_seed"][si] / film["datasets"][ds]["nrmse_film_mean"]
                for ds in scored]
        film_seed_panels.append(float(np.exp(np.mean(np.log(vals)))))

    fig = plt.figure(figsize=(13.5, 7.2), constrained_layout=True)
    gs = GridSpec(1, 2, figure=fig, width_ratios=[1.15, 1.0])
    fig.suptitle(
        "Round 3 — every certified model vs the learned baseline: error relative to mf_fno_transfer_film (ADR r3-0006; lower = better, 1.0 = the baseline)\n"
        "Scored panel per ADR r3-0007: allen_cahn, fisher_kpp, cahn_hilliard, pfc, ifc_heat (ifc_poisson report-only). Baselines certified at 3 fresh seeds, stale-gate clean.\n"
        "† = film-unit reading on the card's registered ADR r3-0004 panel (pre-pfc-restore); unmarked rows are on the current scored panel.\n"
        "Batch-3 cards (r3s2-B3 emulator ceiling, r3s3-B3 sealed knee predictions) are in flight — no bars yet; final leaderboard at round close.",
        fontsize=9.5, x=0.02, ha="left")

    # Panel A: grouped bars — baselines | round-2 anchors | round-3 cards — in film units
    ax = fig.add_subplot(gs[0, 0])
    UNET_C, ANCHOR_C = "#7FA8E8", "#9E86C8"
    groups = []  # (header, [(label, val, lo, hi, color)])
    base_rows = [("mf_fno_transfer_film (baseline)", 1.0,
                  1.0 - min(film_seed_panels), max(film_seed_panels) - 1.0, BLUE)]
    unet_val = None
    unet_p = ROOT / "state" / "anchors" / "unet_baseline.json"
    if unet_p.exists():
        u = json.loads(unet_p.read_text())
        useed = []
        for si in range(3):
            r = [u["datasets"][ds]["nrmse_per_seed"][si] / film["datasets"][ds]["nrmse_film_mean"] for ds in scored]
            useed.append(float(np.exp(np.mean(np.log(r)))))
        unet_val = u.get("_panel5_adr0007_ratio_to_film") or u["_panel_geomean_ratio_to_film"]
        base_rows.append(("convnext U-Net (certified baseline)", unet_val,
                          unet_val - min(useed), max(useed) - unet_val, UNET_C))
    groups.append(("learned baselines (current panel)", base_rows))
    anchor_rows = []
    for card, e in sorted(r2_anchors.items(), key=lambda kv: kv[1]["mean"]):
        v = e["mean"] * gc_cur
        lo, hi = ((e["mean"] - e["ci"][0]) * gc_cur, (e["ci"][1] - e["mean"]) * gc_cur) if e.get("ci") else (0, 0)
        anchor_rows.append((card, v, lo, hi, ANCHOR_C))
    groups.append(("round-2 anchor families (carried forward, current panel)", anchor_rows))
    card_rows = []
    b2 = load_r3s2_b2()
    if b2 is not None:
        card_rows.append(("r3s2 IC-stack (B2 repair; round best) †", b2["panel"] * gc_reg,
                          (b2["panel"] - b2["ci"][0]) * gc_reg, (b2["ci"][1] - b2["panel"]) * gc_reg, ACCENT))
    for cid, meta in CARDS.items():
        d = cards[cid]
        lo, hi = (((d["panel"] - d["ci"][0]) * gc_reg, (d["ci"][1] - d["panel"]) * gc_reg)
                  if d["ci"] else (0, 0))
        card_rows.append((meta["label"] + " †", d["panel"] * gc_reg, lo, hi, ACCENT))
    card_rows.sort(key=lambda r: r[1])
    groups.append(("round-3 cards (certified 3-seed panel values) †", card_rows))

    ys, labels, gap = [], [], 1.0
    ycur = 0.0
    header_positions = []
    for header, rows in groups:
        header_positions.append((ycur + 0.62, header))
        for (label, v, lo, hi, color) in rows:
            ys.append(ycur); labels.append(label)
            ax.barh(ycur, v, color=color, alpha=0.85, height=0.55,
                    xerr=[[lo], [hi]], error_kw=dict(ecolor=INK, capsize=3, lw=1))
            if not label.startswith("convnext"):  # U-Net gets the dead-heat annotation instead
                ax.annotate(f"{v:.2f}", (v + (hi or 0), ycur), textcoords="offset points",
                            xytext=(10, 0), fontsize=7.6, color=INK, va="center", ha="left")
            ycur -= 1.0
        ycur -= gap
    ax.set_yticks(ys, labels)
    ax.set_ylim(ycur + gap + 0.4, 0.95)
    for hy, header in header_positions:
        ax.annotate(header, (0.01, hy), xycoords=("axes fraction", "data"),
                    fontsize=7.6, color=MUTED, style="italic", ha="left", va="center")
    ax.axvline(1.0, color=BLUE, ls="-", lw=1.2)
    if unet_val is not None:
        uy = ys[1]
        uhi = groups[0][1][1][3]
        ax.annotate(f"{unet_val:.2f} — dead heat\n(within seed noise)",
                    (unet_val + uhi, uy), textcoords="offset points", xytext=(10, 0),
                    fontsize=7.6, color=BLUE, va="center", ha="left")
    floor_film = best_floor * gc_cur
    ax.axvline(floor_film, color=FLOOR, ls="--", lw=1.4)
    all_vals = [r[1] for _, rows in groups for r in rows]
    ax.set_xlim(0, max(floor_film * 1.42, max(all_vals) * 1.12))
    ax.text(floor_film + 0.06, ys[2] - 0.35, f"training-free floor {floor_film:.2f}\n(no model: best of NN / mean / zero;\nADR r3-0007 panel)",
            color=FLOOR, fontsize=8, va="top", ha="left")
    ax.set_xlabel("panel error ÷ film baseline, 3-seed mean, 95% CI (lower = better)")
    ax.set_title("A — all certified round-3 models and anchors vs the learned baseline", loc="left")

    # Panel B: per-dataset best model vs the baseline (1.0) and the floor, in film units
    ax2 = fig.add_subplot(gs[0, 1])
    per_ds_sources = {**{cid: cards[cid]["per_ds"] for cid in CARDS}}
    labels_by_src = {cid: CARDS[cid]["label"].split()[0] for cid in CARDS}
    if b2 is not None:
        per_ds_sources["r3s2-B2"] = b2["per_ds"]
        labels_by_src["r3s2-B2"] = "r3s2-B2"
    rows = []
    for ds in all_ds:
        best_src, best_v = None, None
        for src, pds in per_ds_sources.items():
            v = pds.get(ds)
            if v is not None and (best_v is None or v < best_v):
                best_src, best_v = src, v
        rows.append((ds, floors_ds.get(ds), best_v, best_src, ds in report_only))
    ypos = list(range(len(rows)))
    RO_GREY = "#9AA0AE"
    for i, (ds, fl, bv, bc, ro) in enumerate(rows):
        c = c_ds[ds]
        floor_c = RO_GREY if ro else FLOOR
        model_c = RO_GREY if ro else ACCENT
        if ro:
            ax2.axhspan(i - 0.42, i + 0.42, facecolor="#F0F0F3", zorder=0, hatch="///",
                        edgecolor="#DDDDE4", lw=0.0)
        if fl and bv:
            ax2.plot([bv * c, fl * c], [i, i], color="#E5E2EE", lw=2, zorder=1)
        if fl:
            ax2.plot(fl * c, i, "s", color=floor_c, ms=7, zorder=3)
        if bv:
            ax2.plot(bv * c, i, "o", color=model_c, ms=8, zorder=3)
            ax2.annotate(f"{bv * c:.2f}  ({labels_by_src[bc]})", (bv * c, i),
                         textcoords="offset points", xytext=(0, 9), fontsize=8,
                         color=RO_GREY if ro else INK, ha="center")
        elif fl:
            ax2.annotate("no round-3 model cell\n(pfc re-scored under ADR r3-0005,\nafter batch-1/2 registration)",
                         (fl * c, i), textcoords="offset points", xytext=(10, 0), fontsize=7.2,
                         color=MUTED, ha="left", va="center")
    ax2.set_yticks(ypos, [DS_SHORT[r[0]] + ("  (report-only)" if r[4] else "") for r in rows])
    ax2.set_xscale("log")
    from matplotlib.ticker import NullFormatter, FixedLocator, ScalarFormatter
    ax2.xaxis.set_minor_formatter(NullFormatter())
    ax2.xaxis.set_major_locator(FixedLocator([0.1, 0.2, 0.5, 1, 2, 5, 10]))
    fmt = ScalarFormatter(); fmt.set_scientific(False)
    ax2.xaxis.set_major_formatter(fmt)
    ax2.set_xlabel("per-dataset error ÷ baseline (log; 1.0 = baseline)")
    ax2.axvline(1.0, color=BLUE, lw=1.2, ls="-")
    ax2.set_title("B — best round-3 model vs baseline and floor", loc="left")
    ax2.invert_yaxis()

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
     "Question: does routing through a synthetic coarse field help?\nAnswer so far: all measurable value is stage 1 using the IC information;\nstage 2 adds nothing resolvable (same null as round 2).\nBatch 2: repaired corrector instrument → round-best 10.09 (0.72× film);\nbatch 3 asks what the coarse-field detour could EVER buy (ceiling card)."),
    ("Value-of-coarse-data contrast (r3s3) — 11.08 [10.84, 11.25] · no resolvable delta",
     ["condition vector",
      "ONE multi-resolution Fourier neural operator,\ntrained repeatedly under controlled data diets:\nall coarse solves / coarse solves only at parameters the\nfine data already covers / no coarse solves at all",
      "the comparison of those training diets IS the result:\nwhat do coarse solves buy, and through which channel?",
      "fine-grid field (identical network interface at test)"],
     "Answer: coarse solves help ONLY by covering new parameter points\n(the covered-only diet learns the same function as no-coarse-data);\nheadline vs-baseline win retracted after the baseline repair.\nBatch 2: cost-curve knee confirmed at c* = 80 coarse conditions (7×\nthe clause floor); batch 3 seals the surrogate's knee predictions."),
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
    weights = [1.0 if k == "io" else 1.9 for k in kinds]
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
    fig = plt.figure(figsize=(12.5, 8.6), constrained_layout=True)
    gs = GridSpec(2, 2, figure=fig, height_ratios=[1, 0.22])
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
    p3 = fig_model_detail(
        "r3_model_detail_ic_stack.png",
        "Model detail 1 — the initial-condition stack (r3s2; repaired batch-2 version = best model of the round, 0.72× the film-transfer baseline)\n"
        "Two learned stages: a neural generator invents the coarse field the solver would have produced, then a frozen corrector upgrades it.",
        "How it predicts (test time — condition only, no solver)",
        ["condition vector  (2–50 numbers: PDE coefficients, boundary/forcing\nparameters, and — new in round 3 — the initial-condition coefficients)",
         "STAGE 1 · pseudo-coarse generator\nFiLM-conditioned Fourier neural operator: 4 spectral blocks, width 64,\n12 Fourier modes; the condition enters every block as a learned\naffine modulation (FiLM), so one network serves all conditions.\nOutput: a synthetic coarse-grid field (32²/64² sharp, 8–32² ifc)",
         "registered lift  (the benchmark's certified per-dataset interpolation\nconvention raises the coarse field onto the fine grid)",
         "STAGE 2 · frozen corrector\nlocal CNN with a pixel-wise gate (7×7 kernels, depth 4, width 32),\ntrained in an earlier round on REAL coarse→fine pairs and frozen;\nbatch 2 adds the repaired spectral (LSI) filter: cross-validated ridge\n+ hard band-limit at the coarse grid's Nyquist frequency",
         "fine-grid field  (128² sharp / 64² ifc)"],
        ["io", "core", "io", "core", "io"],
        "How it is trained",
        ["training data: ~400 (condition → coarse field) pairs per sharp dataset\n+ only 5 fine-grid fields on the ifc datasets",
         "STAGE 1 trains condition → real coarse field (supervised on the\ncheap solves; relative-L2 loss; the fine fields never enter stage 1)",
         "STAGE 2 stays frozen (its weights come from coarse→fine supervision\nin an earlier round); only its input distribution changes —\nwhich is exactly the covariate shift the mechanism stage identified",
         "at test the real solver is gone: the stack must generate its own\ncoarse field — the benchmark's deployment premise"],
        ["io", "core", "core", "note"],
        "What the round established:  the initial-condition information is the entire measurable effect, and it acts in STAGE 1 (63.7% / 85.4% of generator error removed on\n"
        "allen_cahn / fisher_kpp; a fake IC does worse than none).  The corrector stage adds nothing resolvable — round 2's null replicates (0.0056 vs 0.0061).  Batch 2's repair\n"
        "removed the one failure mode (a 66× spectral amplification fitted from 3 samples) — proven by a replication arm that reproduced the defect digit-for-digit — improving the\n"
        "stream best from 12.96 to 10.09 (0.72× film-transfer).  Its remaining weakness: both ifc cells still lose to a 6-parameter affine fit (floors now quoted with their\n"
        "leave-one-out fold range per ADR r3-0007).")

    p4 = fig_model_detail(
        "r3_model_detail_lf_channels.png",
        "Model detail 2 — the LF-trained multi-resolution FNO (r3s3's A1 arm, 0.79× the film-transfer baseline)\n"
        "One network, one loss trick: it learns from cheap coarse solves at hundreds of conditions while seeing only 5–400 expensive fine fields.",
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
        "training-free surrogate for it — the basis of batch 3's sealed-prediction card.")
    return p3, p4


def main():
    cards = load_cards()
    best_floor, floors_ds, r2, scored, report_only = load_anchors()
    film = load_film()
    if film is None:
        raise SystemExit("film_denominator.json not built yet (ADR r3-0006) — run make_film_denominator.py first")
    missing = [(cid, ds) for cid, d in cards.items() for ds, v in d["per_ds"].items() if v is None]
    if missing:
        print("WARN: per-dataset values not found for:", missing)
    print("scored panel:", scored, "report-only:", report_only, "best_floor:", best_floor)
    p1 = fig_performance(cards, best_floor, floors_ds, r2, film, scored, report_only)
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
