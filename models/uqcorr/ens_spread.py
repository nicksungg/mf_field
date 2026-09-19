"""Zero-training follow-up: is ENSEMBLE SPREAD across the already-trained coarse models spatially informative?
For each (dataset, level) the sweep trained 4 models (plain/hetero x seeds 42/123); their TEST-split predictions are in preds/.
Ensemble mean = average of the 4 mu_test; spread = std over the 4; err = |mean - real coarse|.  Reports per-pixel and per-sample
Spearman for: 4-model spread, 2-model plain-seed spread, hetero sigma (mean of the 2 hetero models), and total = sqrt(spread^2 + sigma^2)."""
import json, math, sys, glob, os
from pathlib import Path
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from diag_coarse import ROSTER, level_files, grids_for, rankdata, spearman_rows
U = Path(os.path.dirname(os.path.abspath(__file__)))
out = []
for f in sorted(glob.glob(str(U / "raw" / "plain__*__s42.json"))):
    j = json.load(open(f))
    if j.get("excluded"): continue
    name, L = j["name"], j["coarse_level"]
    if name not in ROSTER: continue
    P = {}
    for pf in sorted((U / "preds").glob(f"*__{name}__L{L}__s*.npz")):
        var, s = pf.stem.split("__")[0], int(pf.stem.rsplit("__s", 1)[1])
        P[(var, s)] = np.load(pf)
    if len(P) < 4: continue
    hs = [k for k in P if k[0] == "hetero"]
    d = ROSTER[name]; trains, tests = level_files(d)
    cells = [int(np.load(t)["y"].shape[1]) for t in trains]; g = grids_for(name, cells)[L - 1]
    with np.load(tests[L - 1]) as z: y = z["y"].astype(np.float32).reshape(-1, *g)
    mus = np.stack([P[k]["mu_test"] for k in sorted(P)])                       # (4, N, H, W)
    mean = mus.mean(0); spreadM = mus.std(0)
    spread2 = np.stack([P[("plain", 42)]["mu_test"], P[("plain", 123)]["mu_test"]]).std(0)
    sig = np.stack([np.exp(0.5 * P[k]["logvar_test"]) * float(P[k]["scaler"]) for k in hs]).mean(0)
    total = np.sqrt(spreadM ** 2 + sig ** 2)
    err = np.abs(mean - y); E = err.reshape(len(y), -1)
    rel = np.linalg.norm((mean - y).reshape(len(y), -1), axis=1) / np.maximum(np.linalg.norm(y.reshape(len(y), -1), axis=1), 1e-8)
    single = np.mean([np.mean(np.linalg.norm((P[k]["mu_test"] - y).reshape(len(y), -1), axis=1) / np.maximum(np.linalg.norm(y.reshape(len(y), -1), axis=1), 1e-8)) for k in P])
    row = dict(name=name, level=L, grid="x".join(map(str, g)), n_test=int(len(y)), n_members=int(len(P)), rel_single=float(single), rel_ens=float(rel.mean()),
               gap=float(j["test"]["gap_rel_l2"]))
    # saturation curve: metrics vs ensemble size M, averaged over random member subsets
    rng = np.random.default_rng(0); Y = y.reshape(len(y), -1); ynorm = np.maximum(np.linalg.norm(Y, axis=1), 1e-8); curve = {}
    for M in [m for m in (2, 3, 4, 5, 6, 8, 10) if m <= len(P)]:
        acc = []
        for _ in range(20 if M < len(P) else 1):
            idx = rng.choice(len(P), M, replace=False); mm = mus[idx].mean(0); ss = mus[idx].std(0)
            Ef = np.abs(mm - y).reshape(len(y), -1); Sf = ss.reshape(len(y), -1); rl = np.linalg.norm((mm - y).reshape(len(y), -1), axis=1) / ynorm
            acc.append((spearman_rows(Sf, Ef).mean(), spearman_rows(Sf.mean(1)[None], rl[None])[0], (Ef <= 2 * Sf).mean(), rl.mean()))
        a = np.array(acc).mean(0); curve[M] = dict(pix=float(a[0]), samp=float(a[1]), cov2=float(a[2]), rel_ens=float(a[3]))
    row["curve"] = curve
    for nm, S in (("spreadM", spreadM), ("spread2", spread2), ("sigma", sig), ("total", total)):
        Sf = S.reshape(len(y), -1)
        row[f"pix_{nm}"] = float(spearman_rows(Sf, E).mean())
        row[f"samp_{nm}"] = float(spearman_rows(Sf.mean(1)[None], rel[None])[0])
        row[f"cov2_{nm}"] = float((E <= 2 * Sf).mean())
    out.append(row)
    print("   M-curve: " + "  ".join(f"M={M}: pix {c['pix']:.2f} samp {c['samp']:.2f} cov2 {c['cov2']:.2f} err {c['rel_ens']:.4f}" for M, c in curve.items()))
    print(f"{name:30s} L{L} {row['grid']:>9s} rel single {single:.4f} ens {rel.mean():.4f} gap {row['gap']:.4f} | pix: spreadM {row['pix_spreadM']:5.2f} spread2 {row['pix_spread2']:5.2f} sigma {row['pix_sigma']:5.2f} total {row['pix_total']:5.2f} | samp: spreadM {row['samp_spreadM']:5.2f} sigma {row['samp_sigma']:5.2f} | cov2 spreadM {row['cov2_spreadM']:.2f} total {row['cov2_total']:.2f}", flush=True)
(U / "results").mkdir(exist_ok=True)
json.dump(out, open(U / "results" / "ens_spread.json", "w"), indent=1)
print(f"wrote {len(out)} rows to results/ens_spread.json")
