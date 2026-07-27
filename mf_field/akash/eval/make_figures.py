"""Three benchmark figures: (1) dataset landscape, (2) details table, (3) model x dataset error heatmap.
Palette: Okabe-Ito (CVD-safe) categorical for collections; single-hue log-sequential for errors.
Out: akash/results/plots/{fig1_dataset_landscape,fig2_dataset_table,fig3_error_heatmap}.png
"""
import csv, math, os
from collections import defaultdict
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

MF = "/orcd/data/faez/001/nick/mf_field"
R = f"{MF}/akash/results"; PLOTS = f"{R}/plots"; os.makedirs(PLOTS, exist_ok=True)
MAN = "/orcd/data/faez/001/nick/mffp_bench_combined.csv"

# Okabe-Ito, CVD-safe: core=blue, ext=orange, sharp=green
COLL_C = {"core": "#0072B2", "ext": "#E69F00", "sharp": "#009E73"}
INK, MUTED, GRID = "#1a1a1a", "#666666", "#dddddd"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "text.color": INK, "xtick.color": MUTED, "ytick.color": MUTED,
                     "axes.linewidth": 0.8, "figure.dpi": 150})

def base(ds):
    for p in ("ext__", "sharp__"):
        if ds.startswith(p): return ds[len(p):]
    return ds

# ---- load characterization + manifest keyed by (collection, base) ----
char = {}
for r in csv.DictReader(open(f"{R}/dataset_characterization.csv")):
    char[(r["collection"], r["dataset"])] = r
man = {}
for r in csv.DictReader(open(MAN)):
    man[(r["collection"], r["dataset"])] = r

# ---- load metrics ----
rel = {}; models_set = set(); ds_set = set(); valbased = {}
for r in csv.DictReader(open(f"{R}/bench_full_metrics.csv")):
    m, d = r["model"], r["dataset"]; rel[(m, d)] = float(r["rel_l2"])
    models_set.add(m); ds_set.add(d); valbased[m] = valbased.get(m, 0) or int(r["val_based"])
# model order by ELO
model_order = [r["model"] for r in csv.DictReader(open(f"{R}/bench_full_elo.csv"))]
models = [m for m in model_order if m in models_set] or sorted(models_set)

# dataset order: collection then base name
def coll_of(d):
    return "ext" if d.startswith("ext__") else "sharp" if d.startswith("sharp__") else "core"
datasets = sorted(ds_set, key=lambda d: ({"core":0,"ext":1,"sharp":2}[coll_of(d)], base(d)))

def cval(d, k, default=np.nan, cast=float):
    row = char.get((coll_of(d), base(d)))
    if not row or row.get(k) in (None, "", "nan"): return default
    try: return cast(row[k])
    except Exception: return default

# ============ FIGURE 1: dataset landscape ============
fig, (axA, axB) = plt.subplots(1, 2, figsize=(14, 6.2), gridspec_kw={"width_ratios": [1.35, 1]})
# Panel A: MF-applicability (x) vs operator-learnability (y)
for d in datasets:
    c = coll_of(d); x = cval(d, "lf_hf_pearson"); y = cval(d, "pf_dist_corr")
    cd = cval(d, "cond_dim", 2, int); deg = cval(d, "mf_useless", 0, int)
    if np.isnan(x) or np.isnan(y): continue
    axA.scatter(x, y, s=30 + 10*cd, c=COLL_C[c], alpha=0.85,
                edgecolors="#b00" if deg else "white", linewidths=1.6 if deg else 0.7, zorder=3)
axA.axvspan(-0.2, 0.3, color="#b00", alpha=0.06, zorder=0)
axA.text(0.05, -0.19, "MF-useless\n(LF⊥HF)", color="#b00", fontsize=8, ha="left", va="bottom")
# annotate low-corr / notable
for d in datasets:
    x = cval(d, "lf_hf_pearson"); y = cval(d, "pf_dist_corr")
    if np.isnan(x) or np.isnan(y): continue
    if x < 0.45 or y < 0.12:
        axA.annotate(base(d), (x, y), fontsize=6.5, color=MUTED,
                     xytext=(3, 3), textcoords="offset points")
axA.set_xlabel("HF↔LF correlation  →  multi-fidelity applicability")
axA.set_ylabel("param→field correlation  →  operator learnability")
axA.set_title("A. Dataset landscape (42 datasets)", loc="left", fontweight="bold", color=INK)
axA.grid(True, color=GRID, lw=0.6, zorder=0); axA.set_axisbelow(True)
axA.set_xlim(-0.2, 1.05); axA.set_ylim(-0.25, 1.05)
handles = [plt.Line2D([0],[0], marker='o', ls='', mfc=COLL_C[c], mec='white',
           label=f"{c} ({sum(1 for d in datasets if coll_of(d)==c)})", ms=9) for c in ("core","ext","sharp")]
handles.append(plt.Line2D([0],[0], marker='o', ls='', mfc="#ccc", mec="#b00", mew=1.6, label="degenerate", ms=9))
axA.legend(handles=handles, loc="lower right", frameon=False, fontsize=8)

# Panel B: sharpness (high-freq energy ratio), top datasets
hf = [(d, cval(d, "hf_highfreq_ratio", 0)) for d in datasets]
hf = [t for t in hf if t[1] > 0.005]; hf.sort(key=lambda t: t[1])
axB.barh([base(d) for d, _ in hf], [v for _, v in hf],
         color=[COLL_C[coll_of(d)] for d, _ in hf], height=0.7, zorder=3)
axB.set_xlabel("high-frequency energy ratio  →  sharpness")
axB.set_title("B. Sharpest fields (spectral high-freq content)", loc="left", fontweight="bold", color=INK)
axB.grid(True, axis="x", color=GRID, lw=0.6, zorder=0); axB.set_axisbelow(True)
axB.tick_params(labelsize=7)
fig.suptitle("Multi-fidelity benchmark — 42 datasets (core · extension · sharp)",
             fontsize=13, fontweight="bold", x=0.02, ha="left")
fig.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig(f"{PLOTS}/fig1_dataset_landscape.png", bbox_inches="tight"); plt.close(fig)

# ============ FIGURE 2: details table ============
cols = ["dataset", "dim", "#fid", "HF grid", "N_tr", "N_te", "d", "HF↔LF", "hi-freq", "flag"]
rows = []
for d in datasets:
    c = coll_of(d); m = man.get((c, base(d)), {})
    flags = []
    if cval(d, "mf_useless", 0, int): flags.append("MF-useless")
    if cval(d, "operator_hard", 0, int): flags.append("op-hard")
    rows.append([base(d), f"{int(cval(d,'ndim',2,int))}D", m.get("n_fidelity",""),
                 (char.get((c,base(d)),{}) or {}).get("hf_grid",""), m.get("n_train",""), m.get("n_test",""),
                 str(int(cval(d,"cond_dim",0,int))), f"{cval(d,'lf_hf_pearson'):.2f}",
                 f"{cval(d,'hf_highfreq_ratio',0):.2f}", ",".join(flags)])
figh = 0.30 * len(rows) + 1.2
figT, axT = plt.subplots(figsize=(13, figh)); axT.axis("off")
cw = [0.19, 0.05, 0.05, 0.11, 0.15, 0.13, 0.045, 0.08, 0.075, 0.12]
tbl = axT.table(cellText=rows, colLabels=cols, loc="center", cellLoc="left", colWidths=cw)
tbl.auto_set_font_size(False); tbl.set_fontsize(7.5); tbl.scale(1, 1.25)
for j, cname in enumerate(cols):
    cell = tbl[0, j]; cell.set_facecolor("#333333"); cell.set_text_props(color="white", fontweight="bold")
for i, d in enumerate(datasets, start=1):
    for j in range(len(cols)):
        cell = tbl[i, j]; cell.set_facecolor("#f2f2f2" if i % 2 else "white"); cell.set_edgecolor("#eeeeee")
        if j == len(cols)-1 and rows[i-1][-1]: cell.set_text_props(color="#b00")
axT.set_title("Dataset details — 42 multi-fidelity benchmark datasets",
              fontweight="bold", fontsize=13, loc="left", pad=14)
figT.savefig(f"{PLOTS}/fig2_dataset_table.png", bbox_inches="tight"); plt.close(figT)

# ============ FIGURE 3: model x dataset error heatmap ============
M = np.full((len(models), len(datasets)), np.nan)
for i, m in enumerate(models):
    for j, d in enumerate(datasets):
        if (m, d) in rel: M[i, j] = rel[(m, d)]
vmin = max(1e-4, np.nanmin(M[M > 0])); vmax = np.nanmax(M)
cmap = plt.cm.magma_r.copy(); cmap.set_bad("#e8e8e8")   # missing = light gray
figH, axH = plt.subplots(figsize=(19, 5.4))
im = axH.imshow(M, aspect="auto", cmap=cmap, norm=LogNorm(vmin=vmin, vmax=min(vmax, 2.0)))
axH.set_xticks(range(len(datasets)))
xlabels = [base(d) for d in datasets]
axH.set_xticklabels(xlabels, rotation=90, fontsize=6.5)
# color dataset labels by collection; red for degenerate
for tick, d in zip(axH.get_xticklabels(), datasets):
    tick.set_color("#b00" if cval(d, "mf_useless", 0, int) else COLL_C[coll_of(d)])
axH.set_yticks(range(len(models)))
axH.set_yticklabels([("⚠ " if valbased.get(m) else "") + m for m in models], fontsize=8)
# collection separators
prev = None
for j, d in enumerate(datasets):
    c = coll_of(d)
    if prev is not None and c != prev: axH.axvline(j - 0.5, color="white", lw=2.5)
    prev = c
cb = figH.colorbar(im, ax=axH, pad=0.008, fraction=0.02)
cb.set_label("relative-L2 error (log scale)  ·  lighter = better", fontsize=8)
axH.set_title("Model × dataset error  (rows = models, ELO order top→bottom; gray = missing; red label = degenerate; ⚠ = val-based)",
              loc="left", fontweight="bold", fontsize=11)
figH.tight_layout()
figH.savefig(f"{PLOTS}/fig3_error_heatmap.png", bbox_inches="tight"); plt.close(figH)

print("wrote:", os.listdir(PLOTS))
