"""EXP2 — when does the simple transfer baseline win? (regime split, from existing JSONs)

Bounds the central claim. Splits the 15 datasets into regimes and shows the transfer
FNO dominates on the SMOOTH regime but its margin collapses (or it loses) on the HARD
/ less-smooth regime — so "transfer wins" is conditional, not universal.

Regime label per dataset by the best-achievable rel-L2 across ALL models (a
model-agnostic proxy for intrinsic difficulty / smoothness):
  - "solved/smooth": best model gets < 5e-2  (everyone does well; FNO bias fits)
  - "hard":          best model >= 5e-2       (even the best struggles; bias mismatch)

For each regime: geomean rel-L2 per model, and where transfer ranks. Output table +
a grouped bar of transfer vs best-fusion vs best-overall per regime.
"""
import glob, os, json, math, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = "/orcd/data/faez/001/nick/mf_field/factory_mffp"
os.chdir(ROOT)

FAMS = ["mf_fno_transfer","mf_fno_transfer_2m","fno_coreg_residual","fno_mf_stack",
        "fno_coregionalization","fno_coreg_conditioned","fno_additive","fno_autoregressive",
        "fno_multilevel","transolver_residual","transolver_attention_fusion","v9_baseline",
        "mfrnp","mf_deeponet","d_mfd"]
DSS = ["ifc_heat","ifc_poisson","poisson_local","heat_local","fluid","era5","pm_test",
       "advection_diffusion_generated","allen_cahn_generated","burgers_generated",
       "burgers_param_generated","darcy_generated","heat_generated",
       "lid_driven_cavity_generated","poisson_generated"]
THRESH = 5e-2


def rell2(fam, ds):
    fs = glob.glob(f"results/raw_bench/{fam}__{ds}__e2500__s42.json")
    if not fs:
        return None
    s = json.load(open(fs[0])).get("splits", {}).get("test_hf", {})
    m = s.get("rel_l2_mean")
    return m if isinstance(m, (int, float)) and np.isfinite(m) and m > 0 else None


cell = {(f, d): rell2(f, d) for f in FAMS for d in DSS}
best_per_ds = {d: min([v for f in FAMS if (v := cell[(f, d)]) is not None], default=None) for d in DSS}
smooth = [d for d in DSS if best_per_ds[d] is not None and best_per_ds[d] < THRESH]
hard = [d for d in DSS if best_per_ds[d] is not None and best_per_ds[d] >= THRESH]


def gm(fam, dss):
    vs = [cell[(fam, d)] for d in dss if cell[(fam, d)] is not None]
    return math.exp(sum(math.log(v) for v in vs) / len(vs)) if vs else float("nan")


def rank_of(fam, dss):
    scored = sorted([(gm(f, dss), f) for f in FAMS if not math.isnan(gm(f, dss))])
    for i, (_, f) in enumerate(scored, 1):
        if f == fam:
            return i, len(scored)
    return None, len(scored)


print(f"SMOOTH regime ({len(smooth)} datasets, best<{THRESH}): {smooth}")
print(f"HARD regime   ({len(hard)} datasets, best>={THRESH}): {hard}\n")

for label, dss in [("SMOOTH", smooth), ("HARD", hard)]:
    print(f"=== {label} regime ({len(dss)} datasets) — geomean rel-L2, sorted ===")
    scored = sorted([(gm(f, dss), f) for f in FAMS if not math.isnan(gm(f, dss))])
    for g, f in scored[:6]:
        tag = "  <-- transfer" if f == "mf_fno_transfer" else ""
        print(f"   {f:28s} {g:.4e}{tag}")
    r, tot = rank_of("mf_fno_transfer", dss)
    print(f"   ... mf_fno_transfer rank = {r}/{tot}\n")

# CSV
with open("results/exp2_regime_split.csv", "w") as fh:
    fh.write("regime,n_datasets,model,geomean_relL2,rank\n")
    for label, dss in [("smooth", smooth), ("hard", hard)]:
        scored = sorted([(gm(f, dss), f) for f in FAMS if not math.isnan(gm(f, dss))])
        for i, (g, f) in enumerate(scored, 1):
            fh.write(f"{label},{len(dss)},{f},{g:.4e},{i}\n")
print("wrote results/exp2_regime_split.csv")

# Plot: transfer rank in each regime + transfer vs best-fusion geomean
fig, ax = plt.subplots(1, 2, figsize=(15, 6))
for axi, (label, dss) in zip(ax, [("SMOOTH", smooth), ("HARD", hard)]):
    scored = sorted([(gm(f, dss), f) for f in FAMS if not math.isnan(gm(f, dss))])
    fams_s = [f for _, f in scored][:8]; vals = [g for g, _ in scored][:8]
    cols = ["#d62728" if f == "mf_fno_transfer" else "#1f77b4" for f in fams_s]
    axi.barh(range(len(fams_s))[::-1], vals, color=cols)
    axi.set_yticks(range(len(fams_s))[::-1]); axi.set_yticklabels(fams_s, fontsize=9)
    axi.set_xscale("log"); axi.set_xlabel("geomean rel-L2 (log)")
    axi.set_title(f"{label} regime  (n={len(dss)})\nred = transfer FNO")
    axi.grid(axis="x", alpha=0.3, which="both")
fig.suptitle("EXP2: transfer FNO dominates the smooth regime; margin collapses on the hard regime", fontsize=13)
fig.tight_layout()
fig.savefig("results/plots/exp2_regime_split.png", dpi=130, bbox_inches="tight")
print("wrote results/plots/exp2_regime_split.png")
