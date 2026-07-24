import csv, math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = "/orcd/data/faez/001/nick/mf_field/factory_mffp/results"

# representative model per family for the comparison story
MODELS = [
    ("mf_fno_transfer_film", "Transfer+FiLM"),
    ("mf_fno_transfer",      "Transfer"),
    ("fno_fire_distcond",    "FIRE (distcond)"),
    ("fno_dino_residual",    "DINO-residual"),
    ("transolver_residual",  "Transolver"),
    ("mfrnp",                "MFRNP"),
    ("mf_deeponet",          "MF-DeepONet"),
]
order = [m for m, _ in MODELS]
label = dict(MODELS)

# --- ELO ---
elo, elo_sd = {}, {}
with open(f"{ROOT}/bench_elo.csv") as f:
    for r in csv.DictReader(f):
        elo[r["model"]] = float(r["elo_mean"])
        elo_sd[r["model"]] = float(r["elo_std"])

# --- error: geomean of rel_l2_mean across datasets ---
vals = {m: [] for m in order}
with open(f"{ROOT}/bench_metrics.csv") as f:
    for r in csv.DictReader(f):
        if r["model"] in vals and r["rel_l2_mean"].strip():
            v = float(r["rel_l2_mean"])
            if v > 0:
                vals[r["model"]].append(v)
err = {m: math.exp(np.mean(np.log(vals[m]))) for m in order}

# sort by ELO descending for display
disp = sorted(order, key=lambda m: elo[m], reverse=True)
labels = [label[m] for m in disp]
y = np.arange(len(disp))[::-1]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.2))
colors = plt.cm.viridis(np.linspace(0.15, 0.85, len(disp)))

# ELO panel
ax1.barh(y, [elo[m] for m in disp], xerr=[elo_sd[m] for m in disp],
         color=colors, edgecolor="black", linewidth=0.6, error_kw=dict(lw=1, capsize=3))
ax1.set_yticks(y); ax1.set_yticklabels(labels)
ax1.set_xlabel("ELO rating  (↑ better)")
ax1.set_title("Head-to-head ELO")
ax1.set_xlim(min(elo[m] for m in disp) - 120, max(elo[m] for m in disp) + 80)
for yi, m in zip(y, disp):
    ax1.text(elo[m] + elo_sd[m] + 8, yi, f"{elo[m]:.0f}", va="center", fontsize=9)

# Error panel (log scale)
ax2.barh(y, [err[m] for m in disp], color=colors, edgecolor="black", linewidth=0.6)
ax2.set_yticks(y); ax2.set_yticklabels(labels)
ax2.set_xscale("log")
ax2.set_xlabel("Geomean relative L2 error  (↓ better)")
ax2.set_title("Accuracy across 15 datasets")
for yi, m in zip(y, disp):
    ax2.text(err[m] * 1.1, yi, f"{err[m]:.3f}", va="center", fontsize=9)

fig.suptitle("MF-Field benchmark: representative model per family", fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.96])
out = f"{ROOT}/plots/story_elo_vs_error.png"
fig.savefig(out, dpi=160, bbox_inches="tight")
print("saved", out)
for m in disp:
    print(f"{label[m]:16s}  ELO={elo[m]:7.1f}±{elo_sd[m]:.0f}   err={err[m]:.4f}")
