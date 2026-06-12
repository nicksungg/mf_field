"""Print the final fair-benchmark summary from results/raw_bench/ JSONs."""
import glob, os, json, math
from collections import Counter

os.chdir("/orcd/data/faez/001/nick/mf_field/factory_mffp")
fams = ["fno_mf_stack","fno_coregionalization","fno_coreg_residual","fno_coreg_conditioned","fno_coreg_lf_hf_transfer",
        "transolver_residual","transolver_attention_fusion","v9_baseline",
        "mfrnp","mf_deeponet","d_mfd","mf_fno_transfer","mf_fno_transfer_2m","mf_fno_transfer_film","fno_additive","fno_autoregressive","fno_multilevel","fno_fire_distcond","fno_dino_residual","fno_fire_mcdropout"]
dss = ["ifc_heat","ifc_poisson","poisson_local","heat_local","fluid","era5",
       "pm_test","advection_diffusion_generated","allen_cahn_generated",
       "burgers_generated","burgers_param_generated","darcy_generated",
       "heat_generated","lid_driven_cavity_generated","poisson_generated"]

cell = {}
for p in glob.glob("results/raw_bench/*__e2500__s42.json"):
    d = json.load(open(p)); s = d.get("splits", {}).get("test_hf", {})
    fam, ds = os.path.basename(p).replace("__e2500__s42.json", "").split("__", 1)
    cell[(fam, ds)] = {"m": s.get("rel_l2_mean"), "p": d.get("n_params"),
                       "lat": d.get("latency_ms_per_sample")}

def gm(xs):
    xs = [x for x in xs if x and x > 0]
    return math.exp(sum(math.log(x) for x in xs) / len(xs)) if xs else float("nan")
def med(xs):
    xs = sorted(x for x in xs if x is not None)
    return xs[len(xs)//2] if xs else float("nan")

win = Counter(); winner_of = {}
for d in dss:
    cands = [(cell[(f, d)]["m"], f) for f in fams if cell.get((f, d), {}).get("m") is not None]
    if cands:
        b = min(cands); win[b[1]] += 1; winner_of[d] = (b[1], b[0])

print("=== PER-MODEL LEADERBOARD (sorted by geomean rel-L2 over 15 datasets) ===")
print("%-30s %14s %12s %11s %4s" % ("model", "geomean_relL2", "med_params", "med_lat_ms", "wins"))
rows = []
for f in fams:
    ms = [cell.get((f, d), {}).get("m") for d in dss]
    ps = [cell.get((f, d), {}).get("p") for d in dss]
    ls = [cell.get((f, d), {}).get("lat") for d in dss]
    rows.append((gm(ms), f, med(ps), med(ls), win[f]))
for g, f, p, l, w in sorted(rows):
    print("%-30s %14.4e %12d %11.3f %4d" % (f, g, int(p) if p == p else 0, l, w))

print("\n=== PER-DATASET WINNER (lowest rel-L2 mean) ===")
for d in dss:
    if d in winner_of:
        print("  %-30s %-28s %.4e" % (d, winner_of[d][0], winner_of[d][1]))

print("\ncells=%d/135  fully_done_models=%d/9" %
      (len(cell), sum(1 for f in fams if sum(1 for d in dss if (f, d) in cell) == 15)))
