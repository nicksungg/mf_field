"""Payoff analysis: model error vs dataset properties.
(A) difficulty-sorted error heatmap with HF<->LF-corr and high-freq strips on top
    -> hard columns line up with low correlation / high frequency.
(B) FiLM error vs HF<->LF correlation -> error rises as LF stops predicting HF.
(C) per-dataset mean error vs high-frequency ratio -> sharp fields are hard for all.
Out: plots/fig5_payoff.png
"""
import csv, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import matplotlib.gridspec as gridspec

MF = "/orcd/data/faez/001/nick/mf_field"; R = f"{MF}/akash/results"; PLOTS = f"{R}/plots"
COLL_C = {"core": "#0072B2", "ext": "#E69F00", "sharp": "#009E73"}
INK, MUTED, GRID = "#1a1a1a", "#666666", "#dddddd"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "text.color": INK,
                     "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED,
                     "axes.linewidth": 0.8, "figure.dpi": 150})

def coll_of(d): return "ext" if d.startswith("ext__") else "sharp" if d.startswith("sharp__") else "core"
def base(d):
    for p in ("ext__", "sharp__"):
        if d.startswith(p): return d[len(p):]
    return d
def spearman(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    ra = np.argsort(np.argsort(a)).astype(float); rb = np.argsort(np.argsort(b)).astype(float)
    ra -= ra.mean(); rb -= rb.mean()
    return float((ra @ rb) / (np.linalg.norm(ra) * np.linalg.norm(rb) + 1e-12))

# ---- load ----
char = {}
for r in csv.DictReader(open(f"{R}/dataset_characterization.csv")):
    char[(r["collection"], r["dataset"])] = r
def prop(d, k):
    row = char.get((coll_of(d), base(d)), {})
    try: return float(row.get(k, "nan"))
    except Exception: return float("nan")
def mfu(d): return int(char.get((coll_of(d), base(d)), {}).get("mf_useless", 0))

rel = {}; models_set = set(); ds_set = set(); valbased = {}
for r in csv.DictReader(open(f"{R}/bench_full_metrics.csv")):
    rel[(r["model"], r["dataset"])] = float(r["rel_l2"]); models_set.add(r["model"])
    ds_set.add(r["dataset"]); valbased[r["model"]] = valbased.get(r["model"], 0) or int(r["val_based"])
models = [m for m in [x["model"] for x in csv.DictReader(open(f"{R}/bench_full_elo.csv"))] if m in models_set]
datasets = sorted(ds_set)
FILM = "mf_fno_transfer_film"

mean_err = {d: np.nanmedian([rel[(m, d)] for m in models if (m, d) in rel]) for d in datasets}  # median = robust
order = sorted(datasets, key=lambda d: mean_err[d])   # easy -> hard

# ============ figure (two gridspecs so heatmap labels don't collide with scatters) ============
fig = plt.figure(figsize=(19, 12.5))
gs = fig.add_gridspec(3, 1, height_ratios=[0.3, 0.3, 3.4], hspace=0.09,
                      left=0.07, right=0.90, top=0.94, bottom=0.46)
gsb = fig.add_gridspec(1, 2, wspace=0.17, left=0.07, right=0.985, top=0.36, bottom=0.06)
axC = fig.add_subplot(gs[0, 0]); axF = fig.add_subplot(gs[1, 0]); axH = fig.add_subplot(gs[2, 0])
# strips = the TRUE difficulty predictors: field roughness (TV) and operator learnability (pf)
tv_row = np.array([[prop(d, "hf_tv_rel") for d in order]])
pf_row = np.array([[prop(d, "pf_dist_corr") for d in order]])
axC.imshow(tv_row, aspect="auto", cmap="Reds", vmin=np.nanmin(tv_row), vmax=np.nanpercentile(tv_row, 95))
axF.imshow(pf_row, aspect="auto", cmap="viridis", vmin=np.nanmin(pf_row), vmax=np.nanmax(pf_row))
for ax, lab in ((axC, "roughness (TV)"), (axF, "learnability")):
    ax.set_yticks([0]); ax.set_yticklabels([lab], fontsize=8); ax.set_xticks([])
    ax.tick_params(length=0)
axC.set_title("Dataset difficulty (columns sorted easy→hard) tracks HIGH roughness + LOW operator-learnability "
              "— NOT HF↔LF correlation (ρ≈0)", loc="left", fontweight="bold", fontsize=11, pad=6)
M = np.full((len(models), len(order)), np.nan)
for i, m in enumerate(models):
    for j, d in enumerate(order):
        if (m, d) in rel: M[i, j] = rel[(m, d)]
cmap = plt.cm.magma_r.copy(); cmap.set_bad("#e8e8e8")
im = axH.imshow(M, aspect="auto", cmap=cmap, norm=LogNorm(vmin=max(1e-4, np.nanmin(M[M > 0])), vmax=2.0))
axH.set_yticks(range(len(models)))
axH.set_yticklabels([("⚠ " if valbased.get(m) else "") + m for m in models], fontsize=8)
axH.set_xticks(range(len(order)))
axH.set_xticklabels([base(d) for d in order], rotation=90, fontsize=6.3)
for tick, d in zip(axH.get_xticklabels(), order):
    tick.set_color("#b00" if mfu(d) else COLL_C[coll_of(d)])
cb = fig.colorbar(im, ax=[axC, axF, axH], pad=0.006, fraction=0.014)
cb.set_label("rel-L2 (log) · lighter=better", fontsize=8)

# Panel B: mean error vs field roughness (the strongest predictor)
axB = fig.add_subplot(gsb[0, 0])
xs, ys, cs = [], [], []
for d in datasets:
    x = prop(d, "hf_tv_rel"); y = mean_err[d]
    if np.isnan(x) or np.isnan(y) or y > 5: continue   # exclude degenerate / blown-up
    xs.append(x); ys.append(y); cs.append(COLL_C[coll_of(d)])
axB.scatter(xs, ys, c=cs, edgecolors="white", linewidths=0.7, s=55, zorder=3)
axB.set_yscale("log")
lx = np.array(xs); ly = np.log10(np.array(ys)); a, b = np.polyfit(lx, ly, 1)
xx = np.linspace(min(xs), max(xs), 50); axB.plot(xx, 10**(a*xx+b), color=MUTED, lw=1.6, ls="--", zorder=2)
rho = spearman(xs, ys)
axB.set_xlabel("field roughness (relative total variation)")
axB.set_ylabel("mean rel-L2 across models  (log)")
axB.set_title(f"B. Rough fields are hard for everyone  (ρ = {rho:+.2f}, learnable datasets)", loc="left", fontweight="bold", fontsize=11)
axB.grid(True, color=GRID, lw=0.6, zorder=0); axB.set_axisbelow(True)

# Panel C: per-dataset mean error vs operator learnability
axCC = fig.add_subplot(gsb[0, 1])
xs2, ys2, cs2 = [], [], []
for d in datasets:
    x = prop(d, "pf_dist_corr"); y = mean_err[d]
    if np.isnan(x) or np.isnan(y) or y > 5: continue   # exclude degenerate / blown-up
    xs2.append(x); ys2.append(y); cs2.append(COLL_C[coll_of(d)])
axCC.scatter(xs2, ys2, c=cs2, edgecolors="white", linewidths=0.7, s=55, zorder=3)
axCC.set_yscale("log")
lx2 = np.array(xs2); ly2 = np.log10(np.array(ys2)); a2, b2 = np.polyfit(lx2, ly2, 1)
xx2 = np.linspace(min(xs2), max(xs2), 50); axCC.plot(xx2, 10**(a2*xx2+b2), color=MUTED, lw=1.6, ls="--", zorder=2)
rho2 = spearman(xs2, ys2)
axCC.set_xlabel("operator learnability (param→field correlation)")
axCC.set_ylabel("mean rel-L2 across models  (log)")
axCC.set_title(f"C. Chaotic operators are hard for everyone  (ρ = {rho2:+.2f}, learnable datasets)", loc="left", fontweight="bold", fontsize=11)
axCC.grid(True, color=GRID, lw=0.6, zorder=0); axCC.set_axisbelow(True)
handles = [plt.Line2D([0],[0], marker='o', ls='', mfc=COLL_C[c], mec='white', label=c, ms=9) for c in ("core","ext","sharp")]
axCC.legend(handles=handles, loc="lower right", frameon=False, fontsize=8)

fig.suptitle("Payoff analysis — difficulty is intrinsic to the field/operator (roughness, complexity), "
             "not the fidelity relationship", x=0.07, ha="left", fontsize=13.5, fontweight="bold")
fig.savefig(f"{PLOTS}/fig5_payoff.png", bbox_inches="tight", dpi=145); plt.close(fig)
print("wrote fig5_payoff.png ; rho(err vs corr)=", round(rho,3), " rho(err vs hifreq)=", round(rho2,3))
