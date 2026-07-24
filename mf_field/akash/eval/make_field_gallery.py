"""Gallery: one representative HF field from each of the 42 datasets (2-D heatmap or 1-D line).
Border color = collection (core=blue, ext=orange, sharp=green). Out: plots/fig4_field_gallery.png
"""
import csv, json, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

MF = "/orcd/data/faez/001/nick/mf_field"
FACT = f"{MF}/factory_mffp"; sys.path.insert(0, FACT)
from data_adapters import load_mf_dataset
from data_adapters.geometry import resolve_grid
DATA = f"{FACT}/data"; PLOTS = f"{MF}/akash/results/plots"
COLL_C = {"core": "#0072B2", "ext": "#E69F00", "sharp": "#009E73"}

names = open(f"{MF}/akash/eval/bench_datasets.txt").read().split()
def coll_of(d): return "ext" if d.startswith("ext__") else "sharp" if d.startswith("sharp__") else "core"
def base(d):
    for p in ("ext__", "sharp__"):
        if d.startswith(p): return d[len(p):]
    return d
names.sort(key=lambda d: ({"core":0,"ext":1,"sharp":2}[coll_of(d)], base(d)))

def load_hf_field(name):
    d = f"{DATA}/{name}"
    if os.path.exists(f"{d}/meta.json"):
        meta = json.load(open(f"{d}/meta.json")); ndim = int(meta.get("ndim", 2)); ladder = meta["ladder"]
        y = np.load(f"{d}/train_l{len(ladder)}.npz")["y"][0].astype(float); g = ladder[-1]
        return (y.reshape(g[0]) if ndim == 1 else y.reshape(g[0], g[1])), ndim
    tr = load_mf_dataset(d, "train"); hf = tr["hf_fid"]
    g = tr["grid_shape_by_fid"].get(hf) or resolve_grid(name, int(tr["n_cells_by_fid"][hf]))
    y = np.asarray(tr["field_by_fid"][hf][0], float); ndim = 1 if int(g[0]) == 1 else 2
    return (y.reshape(int(g[1])) if ndim == 1 else y.reshape(int(g[0]), int(g[1]))), ndim

def cap2d(f, m=220):
    H, W = f.shape; return f[:: max(1, H // m), :: max(1, W // m)]

ncol = 7; nrow = int(np.ceil(len(names) / ncol))
fig, axes = plt.subplots(nrow, ncol, figsize=(19, 2.7 * nrow))
axes = axes.ravel()
for ax in axes[len(names):]:
    ax.axis("off")
for i, name in enumerate(names):
    ax = axes[i]; c = coll_of(name)
    try:
        field, ndim = load_hf_field(name)
    except Exception as e:
        ax.text(0.5, 0.5, "load err", ha="center"); ax.set_title(base(name), fontsize=7); continue
    if ndim == 1:
        ax.plot(field, color=COLL_C[c], lw=1.3)
        ax.set_xticks([]); ax.tick_params(labelsize=5)
        ax.margins(x=0.02)
    else:
        f = cap2d(field); mx = np.nanmax(np.abs(f))
        if f.min() < -0.05 * mx and f.max() > 0.05 * mx:   # signed -> diverging, centered
            ax.imshow(f, cmap="RdBu_r", vmin=-mx, vmax=mx, aspect="auto")
        else:
            ax.imshow(f, cmap="viridis", aspect="auto")
        ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(base(name), fontsize=7.5, color="#1a1a1a", pad=2)
    for s in ax.spines.values():
        s.set_edgecolor(COLL_C[c]); s.set_linewidth(2.2)

# collection legend
handles = [plt.Line2D([0],[0], marker='s', ls='', mfc=COLL_C[c], mec=COLL_C[c],
           label={"core":"core (15)","ext":"extension (8)","sharp":"sharp (19)"}[c], ms=11)
           for c in ("core","ext","sharp")]
fig.legend(handles=handles, loc="upper right", frameon=False, fontsize=10, bbox_to_anchor=(0.995, 0.998))
fig.suptitle("Example high-fidelity field from each of the 42 benchmark datasets",
             fontsize=14, fontweight="bold", x=0.01, ha="left")
fig.tight_layout(rect=[0, 0, 1, 0.975])
fig.savefig(f"{PLOTS}/fig4_field_gallery.png", bbox_inches="tight", dpi=145); plt.close(fig)
print("wrote fig4_field_gallery.png")
