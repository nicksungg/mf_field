import csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

ROOT = "/orcd/data/faez/001/nick/mf_field/factory_mffp/results"

MODELS = [
    ("mf_fno_transfer_film", "Transfer+FiLM"),
    ("fno_fire_distcond",    "FIRE (distcond)"),
    ("mf_fno_transfer",      "Transfer"),
    ("fno_dino_residual",    "DINO-residual"),
    ("transolver_residual",  "Transolver"),
    ("mfrnp",                "MFRNP"),
    ("mf_deeponet",          "MF-DeepONet"),
]   # row order = ELO ranking
order = [m for m, _ in MODELS]
mlabel = dict(MODELS)

# pretty dataset names
DS_LABEL = {
    "advection_diffusion_generated": "advection-diffusion",
    "allen_cahn_generated": "allen-cahn",
    "burgers_generated": "burgers",
    "burgers_param_generated": "burgers-param",
    "darcy_generated": "darcy",
    "era5": "era5",
    "fluid": "fluid",
    "heat_generated": "heat",
    "heat_local": "heat-local",
    "ifc_heat": "ifc-heat",
    "ifc_poisson": "ifc-poisson",
    "lid_driven_cavity_generated": "lid-cavity",
    "pm_test": "pm-test",
    "poisson_generated": "poisson",
    "poisson_local": "poisson-local",
}

# read
data = {}
datasets = set()
with open(f"{ROOT}/bench_metrics.csv") as f:
    for r in csv.DictReader(f):
        if r["model"] in order and r["rel_l2_mean"].strip():
            data[(r["model"], r["dataset"])] = float(r["rel_l2_mean"])
            datasets.add(r["dataset"])

# order datasets by mean difficulty (across the 7) ascending -> easy left, hard right
datasets = sorted(datasets, key=lambda d: np.nanmean(
    [data.get((m, d), np.nan) for m in order]))
dlabels = [DS_LABEL.get(d, d) for d in datasets]

M = np.full((len(order), len(datasets)), np.nan)
for i, m in enumerate(order):
    for j, d in enumerate(datasets):
        if (m, d) in data:
            M[i, j] = data[(m, d)]

fig, ax = plt.subplots(figsize=(15, 6))
vmin = max(np.nanmin(M), 1e-4)
im = ax.imshow(M, aspect="auto", cmap="RdYlGn_r",
               norm=LogNorm(vmin=vmin, vmax=np.nanmax(M)))

ax.set_xticks(range(len(datasets)))
ax.set_xticklabels(dlabels, rotation=45, ha="right", fontsize=10)
ax.set_yticks(range(len(order)))
ax.set_yticklabels([mlabel[m] for m in order], fontsize=11)

# annotate each cell
for i in range(len(order)):
    for j in range(len(datasets)):
        v = M[i, j]
        if not np.isnan(v):
            txt = f"{v:.3f}" if v >= 0.001 else f"{v:.0e}"
            ax.text(j, i, txt, ha="center", va="center", fontsize=7.5,
                    color="black")

# bold-ish separator after the top-4 (the architectures explained)
ax.axhline(3.5, color="black", lw=2)

cbar = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.01)
cbar.set_label("relative L2 error (log scale)")
ax.set_title("Relative L2 error per model × dataset  (rows = ELO order; datasets easy→hard)",
             fontweight="bold", pad=12)
fig.tight_layout()
out = f"{ROOT}/plots/story_error_heatmap.png"
fig.savefig(out, dpi=160, bbox_inches="tight")
print("saved", out)

# also print a compact table
print("\n" + "model".ljust(16) + "  geomean   best-ds            worst-ds")
for m in order:
    vals = {d: data[(m, d)] for d in datasets if (m, d) in data}
    gm = np.exp(np.mean(np.log(list(vals.values()))))
    bd = min(vals, key=vals.get); wd = max(vals, key=vals.get)
    print(f"{mlabel[m]:16s}  {gm:.4f}   {DS_LABEL[bd]:12s}{vals[bd]:.4f}   {DS_LABEL[wd]:12s}{vals[wd]:.4f}")
