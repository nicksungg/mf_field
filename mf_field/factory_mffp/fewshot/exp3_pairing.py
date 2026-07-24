"""EXP3 — pairing-difficulty correlation (free, from existing benchmark JSONs).

Hypothesis: transfer learning's advantage over OUTPUT-SPACE discrepancy methods
(additive / coreg_residual / mf_stack) grows with how MISMATCHED the LF and HF
sample sets are. Output-space methods must pair an LF field to each HF sample
(here via nearest-neighbour in cond space); when N_LF >> N_HF or the conditioning
distributions differ, that pairing is noisy. Transfer needs NO pairing (LF is just
a pretraining corpus), so it should win by more when pairing is hard.

Metric of pairing difficulty per dataset: mismatch ratio = N_LF / N_HF (train),
log10. Metric of transfer advantage: log10( geo-best(output-space) / transfer )
on that dataset (>0 means transfer better).

Outputs: results/exp3_pairing.csv + results/plots/exp3_pairing_scatter.png, and
prints the Spearman/Pearson correlation.
"""
import glob, os, json, math, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = "/orcd/data/faez/001/nick/mf_field/factory_mffp"
os.chdir(ROOT); sys.path.insert(0, ROOT)
from data_adapters import load_mf_dataset

DSS = ["ifc_heat","ifc_poisson","poisson_local","heat_local","fluid","era5","pm_test",
       "advection_diffusion_generated","allen_cahn_generated","burgers_generated",
       "burgers_param_generated","darcy_generated","heat_generated",
       "lid_driven_cavity_generated","poisson_generated"]
OUTPUT_SPACE = ["fno_additive", "fno_coreg_residual", "fno_mf_stack"]  # need LF<->HF pairing
TRANSFER = "mf_fno_transfer"


def rell2(fam, ds):
    fs = glob.glob(f"results/raw_bench/{fam}__{ds}__e2500__s42.json")
    if not fs:
        return None
    s = json.load(open(fs[0])).get("splits", {}).get("test_hf", {})
    m = s.get("rel_l2_mean")
    return m if isinstance(m, (int, float)) and np.isfinite(m) and m > 0 else None


rows = []
for ds in DSS:
    tr = rell2(TRANSFER, ds)
    outs = [rell2(f, ds) for f in OUTPUT_SPACE]
    outs = [v for v in outs if v is not None]
    if tr is None or not outs:
        continue
    best_out = min(outs)              # best output-space method on this dataset
    try:
        d = load_mf_dataset(f"data/{ds}", "train")
        hf = d["hf_fid"]; lf = min(d["lf_fids"]) if d["lf_fids"] else hf
        n_hf = int(d["cond_by_fid"][hf].shape[0])
        n_lf = int(d["cond_by_fid"][lf].shape[0])
    except Exception:
        continue
    mismatch = n_lf / max(n_hf, 1)
    adv = best_out / tr               # >1 means transfer better
    rows.append(dict(dataset=ds, n_hf=n_hf, n_lf=n_lf, mismatch=mismatch,
                     log_mismatch=math.log10(max(mismatch, 1e-9)),
                     transfer=tr, best_output_space=best_out,
                     transfer_advantage=adv, log_adv=math.log10(max(adv, 1e-9))))

with open("results/exp3_pairing.csv", "w") as fh:
    fh.write("dataset,n_hf,n_lf,mismatch_ratio,transfer_relL2,best_outputspace_relL2,transfer_advantage(x)\n")
    for r in rows:
        fh.write(f"{r['dataset']},{r['n_hf']},{r['n_lf']},{r['mismatch']:.3f},"
                 f"{r['transfer']:.4e},{r['best_output_space']:.4e},{r['transfer_advantage']:.3f}\n")

if len(rows) >= 3:
    x = np.array([r["log_mismatch"] for r in rows])
    y = np.array([r["log_adv"] for r in rows])
    # Pearson on logs
    pear = float(np.corrcoef(x, y)[0, 1])
    # Spearman (rank)
    rx = np.argsort(np.argsort(x)); ry = np.argsort(np.argsort(y))
    spear = float(np.corrcoef(rx, ry)[0, 1])
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter(10**x, 10**y, s=60, c="#1f77b4", zorder=3)
    for r in rows:
        ax.annotate(r["dataset"].replace("_generated", "").replace("_local", "·loc"),
                    (r["mismatch"], r["transfer_advantage"]), fontsize=7,
                    xytext=(3, 3), textcoords="offset points")
    ax.axhline(1.0, color="k", lw=0.6, ls=":")  # advantage = 1 (tie)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("LF/HF train sample mismatch ratio  (N_LF / N_HF)")
    ax.set_ylabel("transfer advantage  =  best output-space rel-L2 / transfer rel-L2\n(>1: transfer better)")
    ax.set_title(f"EXP3: transfer advantage vs pairing difficulty\nPearson(log,log)={pear:.2f}  Spearman={spear:.2f}  (n={len(rows)})")
    ax.grid(alpha=0.3, which="both")
    fig.tight_layout()
    fig.savefig("results/plots/exp3_pairing_scatter.png", dpi=130, bbox_inches="tight")
    print(f"wrote results/plots/exp3_pairing_scatter.png  Pearson={pear:.3f} Spearman={spear:.3f} n={len(rows)}")
else:
    print(f"only {len(rows)} datasets with both transfer + output-space results — need >=3")

print("\ndataset                         N_HF   N_LF  mismatch  transfer  best_outsp  adv(x)")
for r in sorted(rows, key=lambda z: z["mismatch"]):
    print(f"{r['dataset']:30s} {r['n_hf']:5d} {r['n_lf']:6d} {r['mismatch']:8.2f}  "
          f"{r['transfer']:.2e}  {r['best_output_space']:.2e}  {r['transfer_advantage']:6.2f}")
