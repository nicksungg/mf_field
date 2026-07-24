"""Generate paper figures from results/raw_bench/*.json. Writes paper/figures/*.png + summary CSVs."""
import json, glob, math, os
from collections import defaultdict
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "results", "raw_bench")
FIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
os.makedirs(FIG, exist_ok=True)

HARD = {"ifc_poisson", "era5", "pm_test", "burgers_generated", "burgers_param_generated"}
DISPLAY = {
    "mf_fno_transfer_film": "FiLM-conditioned transfer (ours)",
    "mf_fno_transfer": "concat transfer (prior MF-FNO)",
    "mf_fno_transfer_2m": "FNO concat transfer (2M)",
    "fno_coreg_residual": "FNO coreg-residual",
    "fno_mf_stack": "FNO mf-stack",
    "fno_coreg_conditioned": "FNO coreg-conditioned",
    "fno_autoregressive": "FNO autoregressive",
    "fno_additive": "FNO additive",
    "fno_coregionalization": "FNO coregionalization",
    "fno_coreg_lf_hf_transfer": "FNO coreg LF-HF transfer",
    "transolver_attention_fusion": "Transolver attn-fusion",
    "transolver_residual": "Transolver residual",
    "fno_multilevel": "FNO multilevel",
    "mfrnp": "MFRNP",
    "v9_baseline": "v9 multistream",
    "mf_deeponet": "MF-DeepONet",
    "d_mfd": "D-MFD",
}
OURS = "mf_fno_transfer_film"

# ---- load, dedup by (model,dataset) keeping newest file ----
best = {}  # (model,dataset) -> (mtime, record)
for f in glob.glob(os.path.join(RAW, "*__e2500__s42.json")):
    try:
        d = json.load(open(f))
    except Exception:
        continue
    m, ds = d.get("model"), d.get("dataset")
    if not m or not ds:
        continue
    sp = d.get("splits", {})
    k = "test_hf" if "test_hf" in sp else (next(iter(sp), None))
    if not k:
        continue
    s = sp[k]
    rec = dict(mean=s.get("rel_l2_mean", s.get("nRMSE")),
               lo=s.get("rel_l2_ci95_lo"), hi=s.get("rel_l2_ci95_hi"),
               per=s.get("rel_l2_per_sample", []))
    mt = os.path.getmtime(f)
    key = (m, ds)
    if key not in best or mt > best[key][0]:
        best[key] = (mt, rec)

rows = defaultdict(dict)
for (m, ds), (_, rec) in best.items():
    rows[m][ds] = rec

ALLDS = sorted({ds for m in rows for ds in rows[m]})

def gm(vals):
    vals = [v for v in vals if v and v > 0]
    return math.exp(sum(map(math.log, vals)) / len(vals)) if vals else float("nan")

# ---- leaderboard order ----
lb = sorted(((gm([r["mean"] for r in rows[m].values()]), m) for m in rows))
order = [m for _, m in lb]

# ===== Fig 1: geomean leaderboard (horizontal bar, log) =====
fig, ax = plt.subplots(figsize=(8, 6))
gms = [g for g, _ in lb][::-1]
names = [DISPLAY.get(m, m) for _, m in lb][::-1]
cols = ["#d62728" if m == OURS else "#4c78a8" for _, m in lb][::-1]
ax.barh(range(len(gms)), gms, color=cols)
ax.set_yticks(range(len(gms)))
ax.set_yticklabels(names, fontsize=9)
ax.set_xscale("log")
ax.set_xlabel("Geometric-mean relative $L_2$ error over 15 datasets (log scale)")
for i, g in enumerate(gms):
    ax.text(g * 1.05, i, f"{g:.4f}", va="center", fontsize=8)
ax.set_title("Multi-fidelity parametric field prediction: method leaderboard")
ax.margins(x=0.18)
plt.tight_layout(); plt.savefig(os.path.join(FIG, "fig_leaderboard.png"), dpi=160); plt.close()

# ===== Fig 2: per-dataset error bars for 4 key methods =====
key4 = ["mf_fno_transfer_film", "mf_fno_transfer", "fno_coreg_residual", "fno_mf_stack"]
colors4 = {"mf_fno_transfer_film": "#d62728", "mf_fno_transfer": "#4c78a8",
           "fno_coreg_residual": "#59a14f", "fno_mf_stack": "#9467bd"}
fig, ax = plt.subplots(figsize=(13, 6))
x = np.arange(len(ALLDS)); w = 0.2
for j, m in enumerate(key4):
    means, los, his = [], [], []
    for ds in ALLDS:
        r = rows.get(m, {}).get(ds)
        if r and r["mean"]:
            means.append(r["mean"]); los.append(r["mean"] - (r["lo"] or r["mean"])); his.append((r["hi"] or r["mean"]) - r["mean"])
        else:
            means.append(np.nan); los.append(0); his.append(0)
    ax.bar(x + (j - 1.5) * w, means, w, yerr=[los, his], capsize=2,
           label=DISPLAY[m], color=colors4[m], error_kw=dict(lw=0.7))
ax.set_yscale("log")
ax.set_xticks(x); ax.set_xticklabels(ALLDS, rotation=55, ha="right", fontsize=8)
ax.set_ylabel("relative $L_2$ error (log) with 95% bootstrap CI")
ax.set_title("Per-dataset accuracy (top methods); error bars = 95% bootstrap CI over test samples")
ax.legend(fontsize=9, ncol=4, loc="upper left")
plt.tight_layout(); plt.savefig(os.path.join(FIG, "fig_per_dataset_errorbars.png"), dpi=160); plt.close()

# ===== Fig 3: regime split grouped bars =====
focus = ["mf_fno_transfer_film", "mf_fno_transfer", "fno_coreg_residual",
         "fno_mf_stack", "fno_coreg_conditioned", "fno_coregionalization"]
sm = {m: gm([r["mean"] for ds, r in rows[m].items() if ds not in HARD]) for m in focus}
hd = {m: gm([r["mean"] for ds, r in rows[m].items() if ds in HARD]) for m in focus}
fig, ax = plt.subplots(figsize=(10, 5.5))
x = np.arange(len(focus)); w = 0.38
b1 = ax.bar(x - w/2, [sm[m] for m in focus], w, label="smooth (10 datasets)", color="#4c78a8")
b2 = ax.bar(x + w/2, [hd[m] for m in focus], w, label="hard / non-smooth (5 datasets)", color="#e45756")
ax.set_yscale("log")
ax.set_xticks(x); ax.set_xticklabels([DISPLAY[m] for m in focus], rotation=20, ha="right", fontsize=9)
ax.set_ylabel("geometric-mean relative $L_2$ (log)")
ax.set_title("Regime split: our FiLM-conditioned transfer wins BOTH smooth and hard regimes")
ax.legend();
for bars in (b1, b2):
    for b in bars:
        ax.text(b.get_x()+b.get_width()/2, b.get_height()*1.05, f"{b.get_height():.3f}", ha="center", fontsize=7)
plt.tight_layout(); plt.savefig(os.path.join(FIG, "fig_regime_split.png"), dpi=160); plt.close()

# ===== Fig 4: per-dataset ratio film/concat =====
ratios = []
for ds in ALLDS:
    a = rows["mf_fno_transfer_film"].get(ds, {}).get("mean")
    b = rows["mf_fno_transfer"].get(ds, {}).get("mean")
    if a and b:
        ratios.append((ds, a / b))
ratios.sort(key=lambda t: t[1])
fig, ax = plt.subplots(figsize=(11, 5))
dss = [d for d, _ in ratios]; rs = [r for _, r in ratios]
cols = ["#59a14f" if r < 1 else "#e45756" for r in rs]
ax.bar(range(len(rs)), rs, color=cols)
ax.axhline(1.0, color="k", lw=1, ls="--")
ax.set_xticks(range(len(dss))); ax.set_xticklabels(dss, rotation=55, ha="right", fontsize=8)
ax.set_ylabel("error ratio  FiLM / concat-transfer")
ax.set_title("FiLM vs concat conditioning, per dataset (<1 = FiLM better; 14/15 datasets)")
for i, r in enumerate(rs):
    ax.text(i, r + 0.02, f"{r:.2f}", ha="center", fontsize=7)
plt.tight_layout(); plt.savefig(os.path.join(FIG, "fig_film_vs_concat_ratio.png"), dpi=160); plt.close()

# ===== Fig 5: ELO (from results/bench_elo.csv if present) =====
elo_csv = os.path.join(ROOT, "results", "bench_elo.csv")
if os.path.exists(elo_csv):
    import csv
    rk, el, es = [], [], []
    for row in csv.DictReader(open(elo_csv)):
        rk.append(DISPLAY.get(row["model"], row["model"]))
        el.append(float(row["elo_mean"])); es.append(float(row.get("elo_std", 0) or 0))
    fig, ax = plt.subplots(figsize=(8, 6))
    yy = range(len(rk))[::-1]
    cols = ["#d62728" if "ours" in n else "#4c78a8" for n in rk]
    ax.barh(list(yy), el, xerr=es, color=cols, capsize=2, error_kw=dict(lw=0.7))
    ax.set_yticks(list(yy)); ax.set_yticklabels(rk, fontsize=9)
    ax.set_xlabel("ELO (pairwise wins across datasets; error bar = std)")
    ax.set_title("ELO ranking"); ax.set_xlim(min(el)-60, max(el)+60)
    plt.tight_layout(); plt.savefig(os.path.join(FIG, "fig_elo.png"), dpi=160); plt.close()

# ---- emit a tidy summary CSV the paper tables draw from ----
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "leaderboard_table.csv"), "w") as fh:
    fh.write("model,geomean_all,geomean_smooth,geomean_hard,n_datasets\n")
    for g, m in lb:
        s = gm([r["mean"] for ds, r in rows[m].items() if ds not in HARD])
        h = gm([r["mean"] for ds, r in rows[m].items() if ds in HARD])
        fh.write(f"{m},{g:.5f},{s:.5f},{h:.5f},{len(rows[m])}\n")

print("FIGURES:", sorted(os.listdir(FIG)))
print("\nLEADERBOARD (geomean all | smooth | hard):")
for g, m in lb:
    s = gm([r["mean"] for ds, r in rows[m].items() if ds not in HARD])
    h = gm([r["mean"] for ds, r in rows[m].items() if ds in HARD])
    print(f"  {DISPLAY.get(m,m):32s} {g:.5f} | {s:.5f} | {h:.5f}  (n={len(rows[m])})")
