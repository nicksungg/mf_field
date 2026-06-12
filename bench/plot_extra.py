"""Extra benchmark visualizations:
  1. grouped bar plot: rel-L2 per model per dataset (95% bootstrap CI error bars)
  2. ELO ranking of the 9 models from pairwise per-dataset wins (mean +- std over
     many random match orderings) -> bar plot + CSV
  3. dataset gallery: one HF sample field per dataset (imshow / 1-D curve)

All outputs land in results/plots/ and results/.
"""
import glob, os, json, math, random
from collections import defaultdict
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = "/orcd/data/faez/001/nick/mf_field/factory_mffp"
os.chdir(ROOT)
import sys
sys.path.insert(0, ROOT)
from data_adapters import load_mf_dataset
from data_adapters.geometry import resolve_grid

PLOTS = "results/plots"
os.makedirs(PLOTS, exist_ok=True)

FAMS = ["fno_mf_stack","fno_coregionalization","fno_coreg_residual","fno_coreg_conditioned","fno_coreg_lf_hf_transfer",
        "transolver_residual","transolver_attention_fusion","v9_baseline",
        "mfrnp","mf_deeponet","d_mfd","mf_fno_transfer","mf_fno_transfer_2m","mf_fno_transfer_film","fno_additive","fno_autoregressive","fno_multilevel","fno_fire_distcond","fno_dino_residual","fno_fire_mcdropout"]
DSS = ["ifc_heat","ifc_poisson","poisson_local","heat_local","fluid","era5",
       "pm_test","advection_diffusion_generated","allen_cahn_generated",
       "burgers_generated","burgers_param_generated","darcy_generated",
       "heat_generated","lid_driven_cavity_generated","poisson_generated"]
DSHORT = [d.replace("_generated","").replace("_local","·loc") for d in DSS]

# ---- load cells ----
cell = {}
for p in glob.glob("results/raw_bench/*__e2500__s42.json"):
    d = json.load(open(p)); s = d.get("splits", {}).get("test_hf", {})
    fam, ds = os.path.basename(p).replace("__e2500__s42.json", "").split("__", 1)
    cell[(fam, ds)] = {"m": s.get("rel_l2_mean"), "lo": s.get("rel_l2_ci95_lo"),
                       "hi": s.get("rel_l2_ci95_hi")}

cmap = plt.get_cmap("tab10")
COL = {f: cmap(i % 10) for i, f in enumerate(FAMS)}

# ============================================================
# 1. GROUPED BAR PLOT (model x dataset)
# ============================================================
fig, ax = plt.subplots(figsize=(26, 9))
nM = len(FAMS); w = 0.9 / nM
x = np.arange(len(DSS))
for j, f in enumerate(FAMS):
    ys, lo, hi = [], [], []
    for d in DSS:
        c = cell.get((f, d))
        m = c["m"] if c else None
        if m is not None and np.isfinite(m) and m > 0:
            ys.append(m)
            lo.append(max(m - (c["lo"] or m), 0)); hi.append(max((c["hi"] or m) - m, 0))
        else:
            ys.append(np.nan); lo.append(0); hi.append(0)
    ax.bar(x + j*w, np.nan_to_num(ys, nan=1e-5), w, yerr=[lo, hi], capsize=1.5,
           label=f, color=COL[f], error_kw={"elinewidth": 0.6, "alpha": 0.6})
ax.set_yscale("log"); ax.set_ylim(1e-4, 3e0)
ax.set_xticks(x + 0.45); ax.set_xticklabels(DSHORT, rotation=90, fontsize=9)
ax.axhline(1.0, color="k", lw=0.6, ls=":")
ax.set_ylabel("relative L2 error (log scale, lower = better)")
ax.set_title("MFFP fair benchmark — rel-L2 per model per dataset (mean ± 95% bootstrap CI), 2500 ep, seed 42")
ax.legend(ncol=3, fontsize=9, loc="upper left")
fig.tight_layout()
fig.savefig(f"{PLOTS}/bench_grouped_bars.png", dpi=130, bbox_inches="tight")
plt.close(fig)
print("wrote", f"{PLOTS}/bench_grouped_bars.png")

# ============================================================
# 2. ELO RANKING (pairwise per-dataset wins, averaged over orderings)
# ============================================================
# build match list: per dataset, every model pair where both have a finite score
matches = []   # (winner, loser) ; ties -> two half results handled below
ties = []
for d in DSS:
    present = [f for f in FAMS if cell.get((f, d), {}).get("m") is not None
               and np.isfinite(cell[(f, d)]["m"])]
    for i in range(len(present)):
        for k in range(i+1, len(present)):
            a, b = present[i], present[k]
            ma, mb = cell[(a, d)]["m"], cell[(b, d)]["m"]
            if ma < mb:   matches.append((a, b))
            elif mb < ma: matches.append((b, a))
            else:         ties.append((a, b))

def run_elo(seed, K=24, base=1500.0):
    rng = random.Random(seed)
    R = {f: base for f in FAMS}
    order = list(matches); rng.shuffle(order)
    def upd(w, l, sw):
        ew = 1.0 / (1.0 + 10 ** ((R[l] - R[w]) / 400.0))
        R[w] += K * (sw - ew); R[l] += K * ((1-sw) - (1-ew))
    for w, l in order:
        upd(w, l, 1.0)
    for a, b in ties:
        upd(a, b, 0.5)
    return R

S = 500
allR = defaultdict(list)
for seed in range(S):
    R = run_elo(seed)
    for f, v in R.items(): allR[f].append(v)
elo_mean = {f: float(np.mean(allR[f])) for f in FAMS}
elo_std  = {f: float(np.std(allR[f]))  for f in FAMS}

# win/loss/tie tallies for the CSV
wins = defaultdict(int); losses = defaultdict(int); tie_ct = defaultdict(int)
for w, l in matches: wins[w]+=1; losses[l]+=1
for a, b in ties: tie_ct[a]+=1; tie_ct[b]+=1

order = sorted(FAMS, key=lambda f: -elo_mean[f])
with open("results/bench_elo.csv", "w") as fh:
    fh.write("rank,model,elo_mean,elo_std,wins,losses,ties\n")
    for i, f in enumerate(order, 1):
        fh.write(f"{i},{f},{elo_mean[f]:.1f},{elo_std[f]:.1f},{wins[f]},{losses[f]},{tie_ct[f]}\n")
print("wrote", "results/bench_elo.csv")

fig, ax = plt.subplots(figsize=(11, 6))
yy = np.arange(len(order))[::-1]
vals = [elo_mean[f] for f in order]
errs = [elo_std[f] for f in order]
ax.barh(yy, vals, xerr=errs, color=[COL[f] for f in order], capsize=4,
        error_kw={"elinewidth": 1.2})
for y, f in zip(yy, order):
    ax.text(elo_mean[f] + elo_std[f] + 6, y,
            f"{elo_mean[f]:.0f}  ({wins[f]}W-{losses[f]}L)", va="center", fontsize=10)
ax.set_yticks(yy); ax.set_yticklabels(order, fontsize=11)
ax.set_xlabel("ELO rating (pairwise per-dataset wins; mean ± std over 500 random match orderings)")
ax.set_title("MFFP fair benchmark — model ELO ranking (15 datasets, 36 pairs each)")
ax.axvline(1500, color="k", lw=0.6, ls=":")
ax.margins(x=0.18)
fig.tight_layout()
fig.savefig(f"{PLOTS}/bench_elo_ranking.png", dpi=130, bbox_inches="tight")
plt.close(fig)
print("wrote", f"{PLOTS}/bench_elo_ranking.png")

# ============================================================
# 3. DATASET GALLERY (one HF sample per dataset)
# ============================================================
WORK_CAP = 256
def cap(g):
    H, W = g; mx = max(H, W)
    if mx <= WORK_CAP: return (H, W)
    f = WORK_CAP/mx; return (max(1, round(H*f)), max(1, round(W*f)))

fig, axes = plt.subplots(3, 5, figsize=(22, 12))
for ax, d in zip(axes.flat, DSS):
    try:
        data = load_mf_dataset(f"data/{d}", split="test")
        hf = data["hf_fid"]
        field = np.asarray(data["field_by_fid"][hf][0], dtype=np.float64)  # sample 0
        n = field.size
        H, W = resolve_grid(d, n)
        img = field.reshape(H, W)
        Hc, Wc = cap((H, W))
        if (Hc, Wc) != (H, W):
            # simple stride downsample for display
            img = img[:: max(1, H//Hc), :: max(1, W//Wc)]
        if H == 1:  # 1-D field -> plot as curve
            ax.plot(field, color="#1f77b4"); ax.set_title(f"{d}\n1-D, L={W}", fontsize=10)
        elif "cavity" in d:
            # vorticity field: lid-corner singularities saturate the colormap, so clip to
            # the robust 2–98 percentile range. Same viridis scheme as every other panel.
            vmin, vmax = np.percentile(img, 2), np.percentile(img, 98)
            im = ax.imshow(img, aspect="auto", cmap="viridis", vmin=vmin, vmax=vmax)
            fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
            ax.set_title(f"{d}\nHF grid {H}×{W} (vorticity, 2–98pct clip)", fontsize=10)
            ax.set_xticks([]); ax.set_yticks([])
        else:
            im = ax.imshow(img, aspect="auto", cmap="viridis")
            fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
            ax.set_title(f"{d}\nHF grid {H}×{W}", fontsize=10)
            ax.set_xticks([]); ax.set_yticks([])
        del data, field
    except Exception as e:
        ax.text(0.5, 0.5, f"{d}\n{type(e).__name__}", ha="center", va="center", fontsize=8)
        ax.set_xticks([]); ax.set_yticks([])
for ax in axes.flat[len(DSS):]:
    ax.axis("off")
fig.suptitle("MFFP datasets — high-fidelity sample field per dataset (15 non-chin_chun benchmarks)", fontsize=15, y=1.01)
fig.tight_layout(rect=[0, 0, 1, 0.99])
fig.savefig(f"{PLOTS}/datasets_gallery.png", dpi=120, bbox_inches="tight")
plt.close(fig)
print("wrote", f"{PLOTS}/datasets_gallery.png")

# print ELO order to stdout
print("\nELO ranking:")
for i, f in enumerate(order, 1):
    print(f"  {i}. {f:30s} {elo_mean[f]:6.0f} ± {elo_std[f]:.0f}   {wins[f]}W-{losses[f]}L")
