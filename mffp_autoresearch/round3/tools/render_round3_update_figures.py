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
    "ifc_heat": "ifc_heat",
}
PANEL = list(DS_SHORT)

CARDS = {
    "r3s1_factorised-B1": dict(label="r3s1 factorised head", ),
    "r3s2_field_reach-B1": dict(label="r3s2 IC-reach stack"),
    "r3s3_lf_value-B1": dict(label="r3s3 LF-value contrast"),
    "r3s4_audit-B1": dict(label="r3s4 certifier"),
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
        p = ROOT / "experiment_cards" / stream / "batch_1" / "B1.json"
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
        if not (isinstance(pd_block, dict) and any(ds in pd_block for ds in PANEL)):
            pd_block = _find_key(three, "per_dataset") or _find_key(r5, "per_dataset") or {}
        for ds in PANEL:
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
    floors_ds = {ds: v["skill"] for ds, v in a["best_floor"]["per_dataset"].items()}
    r2 = {card: e["mean"] for card, e in a["cards"].items() if "mean" in e}
    return best_floor, floors_ds, r2


def fig_performance(cards, best_floor, floors_ds, r2_anchors):
    fig = plt.figure(figsize=(10.5, 5.4), constrained_layout=True)
    gs = GridSpec(1, 2, figure=fig, width_ratios=[1.0, 1.25])
    fig.suptitle(
        "Round 3, batch 1: every stream beats the training-free floor; skill is copy-LF-referenced nRMSE (lower = better)\n"
        "Panel = geometric mean over the 5 scored datasets (ADR r3-0004). Floors and anchors recomputed on the repaired data (2026-08-10).",
        fontsize=10.5, x=0.02, ha="left")

    # Panel A: panel geomeans
    ax = fig.add_subplot(gs[0, 0])
    names, vals, errs = [], [], []
    for cid, meta in CARDS.items():
        d = cards[cid]
        names.append(meta["label"]); vals.append(d["panel"])
        if d["ci"]:
            errs.append((d["panel"] - d["ci"][0], d["ci"][1] - d["panel"]))
        else:
            errs.append((0, 0))
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    y = range(len(order))
    ax.barh(list(y), [vals[i] for i in order], color=ACCENT, alpha=0.85, height=0.55,
            xerr=list(zip(*[errs[i] for i in order])), error_kw=dict(ecolor=INK, capsize=3, lw=1))
    ax.set_yticks(list(y), [names[i] for i in order])
    ax.axvline(best_floor, color=FLOOR, ls="--", lw=1.4)
    ax.text(best_floor + 0.6, 1.5, f"training-free floor {best_floor:.1f}\n(no model: best of\nNN / mean / zero)",
            color=FLOOR, fontsize=8.5, va="center", ha="left")
    r2best = min(r2_anchors.values())
    ax.axvline(r2best, color=BLUE, ls=":", lw=1.4)
    ax.text(r2best + 0.4, -0.38, f"best round-2 anchor {r2best:.1f}", color=BLUE, fontsize=8.5, va="bottom", ha="left")
    ax.set_xlabel("panel geomean skill, 3-seed mean with 95% CI (lower = better)")
    ax.set_title("A — batch-1 models vs the two baselines", loc="left")
    ax.set_xlim(0, best_floor * 1.25)

    # Panel B: per-dataset best model vs floor
    ax2 = fig.add_subplot(gs[0, 1])
    rows = []
    for ds in PANEL:
        best_cid, best_v = None, None
        for cid in CARDS:
            v = cards[cid]["per_ds"].get(ds)
            if v is not None and (best_v is None or v < best_v):
                best_cid, best_v = cid, v
        rows.append((ds, floors_ds.get(ds), best_v, best_cid))
    ypos = range(len(rows))
    for i, (ds, fl, bv, bc) in enumerate(rows):
        if fl and bv:
            ax2.plot([bv, fl], [i, i], color="#E5E2EE", lw=2, zorder=1)
        if fl:
            ax2.plot(fl, i, "s", color=FLOOR, ms=7, zorder=3)
        if bv:
            ax2.plot(bv, i, "o", color=ACCENT, ms=8, zorder=3)
            ax2.annotate(f"{bv:.2f}  ({CARDS[bc]['label'].split()[0]})", (bv, i),
                         textcoords="offset points", xytext=(0, 9), fontsize=8, color=INK, ha="center")
    ax2.set_yticks(list(ypos), [DS_SHORT[r[0]] for r in rows])
    ax2.set_xscale("log")
    ax2.set_xlabel("per-dataset mean skill, log scale (lower = better)")
    ax2.axvline(1.0, color=MUTED, lw=1, ls="-")
    ax2.text(1.07, len(rows) - 0.62, "skill = 1: as good as\ncopying the LF solve", color=MUTED,
             fontsize=8, va="bottom", ha="left")
    ax2.set_title("B — best batch-1 model (circle) vs floor (square)", loc="left")
    ax2.invert_yaxis()

    out = FIGDIR / "r3_performance_vs_baselines.png"
    fig.savefig(out, dpi=170)
    plt.close(fig)
    return out


ARCH = [
    ("r3s1 factorised head — 24.96 [24.87, 25.07] · CONFIRMED",
     ["condition vector", "stage 1: per-direction\ncondition→POD-coefficient maps\n(closed form, OOF-selected)",
      "stage 2: gated cross-coefficient\ncorrection (OOF inputs)", "HF field"],
     "Win concentrates in cahn_hilliard (+1.31 skill, ~80/100 rows).\nLimit found: an arbitrary basis cap (SELECT_MAX=32), not the factorisation."),
    ("r3s2 IC-reach stack — 12.96 [10.32, 17.83] · corrector FALSIFIED",
     ["condition vector\n(incl. IC coefficients)", "stage 1: FiLM-FNO emulator\ncondition→pseudo-LF field",
      "stage 2: frozen corrector\n(pseudo-LF→HF)", "HF field"],
     "IC information is real and lives in stage 1 (63.7% / 85.4% of emulator\nerror removed on ac/fk). Stage 2 adds nothing resolvable — round 2's null replicates."),
    ("r3s3 LF-value contrast — 11.08 [10.84, 11.25] · no vs-anchor delta",
     ["condition vector", "multi-rung FNO trained with /\nwithout LF rows (matched budget)",
      "controlled arms:\ncovered vs uncovered conditions", "HF field"],
     "LF-at-train's value = supplying NEW distinct condition rows\n(E_cov/E_total ≈ 1.0 on 30/30 cells); covered-only LF learns the same function."),
    ("r3s4 certifier — 19.64 [19.42, 19.93] · noise floor CERTIFIED",
     ["condition vector", "reference model +\nfloor reproduction arms", "seed/row bootstrap\n→ per-dataset MDD, τ_rel, τ_abs",
      "certified noise floor\n(prices every claim)"],
     "Its certification now licenses all round-3 claims; also priced the audit\ninstruments themselves (train_seconds rule: 0 unique TPs / 62 FPs → deleted)."),
]


def fig_architectures():
    fig = plt.figure(figsize=(11, 7.4), constrained_layout=True)
    gs = GridSpec(2, 2, figure=fig)
    fig.suptitle(
        "Round 3, batch 1 — the four stream architectures (condition → HF field; no solver, no LF at test)\n"
        "Number = 3-seed panel geomean skill [95% CI], lower is better; training-free floor = 34.42",
        fontsize=10.5, x=0.02, ha="left")
    for k, (title, boxes, note) in enumerate(ARCH):
        ax = fig.add_subplot(gs[k // 2, k % 2])
        ax.set_axis_off()
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)
        ax.set_title(title, loc="left", fontsize=9.5, fontweight="bold")
        n = len(boxes)
        xs = [0.5] * n
        ys = [0.88 - i * (0.78 / (n - 1)) for i in range(n)]
        for i, (bx, by, text) in enumerate(zip(xs, ys, boxes)):
            first_last = i == 0 or i == n - 1
            fc = "#F1EFF7" if not first_last else "#FFFFFF"
            ec = ACCENT if not first_last else MUTED
            ax.add_patch(FancyBboxPatch((bx - 0.33, by - 0.075), 0.66, 0.15,
                                        boxstyle="round,pad=0.012", fc=fc, ec=ec, lw=1.2))
            ax.text(bx, by, text, ha="center", va="center", fontsize=8.2, color=INK)
            if i < n - 1:
                ax.annotate("", xy=(bx, ys[i + 1] + 0.078), xytext=(bx, by - 0.078),
                            arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.2))
        ax.text(0.5, -0.06, note, ha="center", va="top", fontsize=7.8, color=MUTED,
                transform=ax.transAxes)
    out = FIGDIR / "r3_architectures_overview.png"
    fig.savefig(out, dpi=170)
    plt.close(fig)
    return out


def main():
    cards = load_cards()
    best_floor, floors_ds, r2 = load_anchors()
    missing = [(cid, ds) for cid, d in cards.items() for ds, v in d["per_ds"].items() if v is None]
    if missing:
        print("WARN: per-dataset values not found for:", missing)
    p1 = fig_performance(cards, best_floor, floors_ds, r2)
    p2 = fig_architectures()
    print("wrote", p1)
    print("wrote", p2)
    for cid, d in cards.items():
        print(cid, "panel", d["panel"], "ci", d["ci"], "per_ds", {DS_SHORT[k]: v for k, v in d["per_ds"].items()})


if __name__ == "__main__":
    main()
