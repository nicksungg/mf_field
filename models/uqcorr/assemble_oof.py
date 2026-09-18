"""Assemble K-fold ensemble coarse predictions into per-cell inputs for the corrector (step 2a -> 2b).
For each (dataset, level) with fold results: every train row is held out by exactly one fold, whose M members give an
out-of-fold ensemble mean and spread for that row; the test rows get the mean/spread over all K*M members.
Writes oof/<name>__L<lf>.npz with: mean_train, spread_train (n_paired, H, W), mean_test, spread_test (n_test, H, W),
n_members_train (per row), members_test (K*M), plus sigma_train/sigma_test (mean hetero sigma where hetero members exist)
and a metrics summary in results/oof_summary.json (OOF error vs real coarse, per-pixel/per-sample Spearman of spread)."""
import json, glob, os, sys, re
from pathlib import Path
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from diag_coarse import ROSTER, level_files, grids_for, spearman_rows
args = [x for x in sys.argv[1:] if not x.startswith("--")]; REQUIRE = "--require-complete" in sys.argv
U = Path(args[0]) if args else Path(os.path.dirname(os.path.abspath(__file__)))
(U / "oof").mkdir(exist_ok=True); (U / "results").mkdir(exist_ok=True)
cells = {}
for f in glob.glob(str(U / "raw" / "*__F*of*__s*.json")):
    j = json.load(open(f))
    if j.get("excluded") or not j.get("nfolds"): continue
    cells.setdefault((j["name"], j["coarse_level"], j["nfolds"]), []).append(j)
summary = []
for (name, L, K), js in sorted(cells.items()):
    if name not in ROSTER:
        print(f"{name:30s} L{L}: not in the current roster; skipped", flush=True); continue
    d = ROSTER[name]; trains, tests = level_files(d)
    cs = [int(np.load(t)["y"].shape[1]) for t in trains]; g = grids_for(name, cs)[L - 1]
    with np.load(trains[L - 1]) as z: y_tr = z["y"].astype(np.float32).reshape(-1, *g)
    with np.load(tests[L - 1]) as z: y_te = z["y"].astype(np.float32).reshape(-1, *g)
    n = len(y_tr); sum_tr = np.zeros((n, *g), np.float64); sq_tr = np.zeros_like(sum_tr); cnt_tr = np.zeros(n, np.int32)
    sig_tr = np.zeros_like(sum_tr); sigcnt_tr = np.zeros(n, np.int32); te_by_fold = {}; sig_by_fold = {}
    folds_seen = set()
    for j in js:
        tag = f"{j['variant']}__{name}__L{L}__F{j['fold']}of{K}__s{j['seed']}"
        pf = U / "preds" / f"{tag}.npz"
        if not pf.exists(): continue
        z = np.load(pf); rows = z["hold_rows"]; mu = z["mu_hold"].astype(np.float64)
        sum_tr[rows] += mu; sq_tr[rows] += mu ** 2; cnt_tr[rows] += 1; folds_seen.add(j["fold"])
        te_by_fold.setdefault(j["fold"], []).append(z["mu_test"].astype(np.float64))
        if "logvar_hold" in z:
            s = np.exp(0.5 * z["logvar_hold"]) * float(z["scaler"]); sig_tr[rows] += s; sigcnt_tr[rows] += 1
            sig_by_fold.setdefault(j["fold"], []).append(np.exp(0.5 * z["logvar_test"]) * float(z["scaler"]))
    if not te_by_fold: continue
    # ONE FIXED ENSEMBLE SIZE (user 2026-09-10): every training row is predicted by the 4 members of the fold that held
    # it out, so the TEST ensemble must also be 4 members from a single fold -- otherwise the corrector trains on
    # 4-member means/spreads and is evaluated on 20-member ones (test spread ran 1.03-2.58x larger than training spread).
    n_per_fold = int(np.median(cnt_tr[cnt_tr > 0])) if (cnt_tr > 0).any() else 0
    pick = min((f for f, v in te_by_fold.items() if len(v) == n_per_fold), default=min(te_by_fold))
    te_members = te_by_fold[pick]; te_sig = sig_by_fold.get(pick, [])
    c = np.maximum(cnt_tr, 1)[:, None, None]
    mean_tr = sum_tr / c; spread_tr = np.sqrt(np.maximum(sq_tr / c - mean_tr ** 2, 0.0))
    te = np.stack(te_members); mean_te = te.mean(0); spread_te = te.std(0)   # 4 members, fold `pick`
    sigma_tr = sig_tr / np.maximum(sigcnt_tr, 1)[:, None, None] if sigcnt_tr.any() else None
    sigma_te = np.mean(te_sig, 0) if te_sig else None
    covered = int((cnt_tr > 0).sum())
    if REQUIRE and (covered < n or len(folds_seen) < K or cnt_tr.min() != cnt_tr.max()):
        print(f"{name:30s} L{L}: incomplete ({len(folds_seen)}/{K} folds, {covered}/{n} rows, members/row {cnt_tr.min()}-{cnt_tr.max()}); skipped", flush=True); continue
    np.savez_compressed(U / "oof" / f"{name}__L{L}.npz", mean_train=mean_tr.astype(np.float32), spread_train=spread_tr.astype(np.float32),
                        n_members_train=cnt_tr, mean_test=mean_te.astype(np.float32), spread_test=spread_te.astype(np.float32),
                        members_test=len(te_members), test_fold=pick, grid=np.array(g),
                        **({"sigma_train": sigma_tr.astype(np.float32), "sigma_test": sigma_te.astype(np.float32)} if sigma_tr is not None else {}))
    ok = cnt_tr > 0
    E_tr = np.abs(mean_tr - y_tr)[ok].reshape(ok.sum(), -1); S_tr = spread_tr[ok].reshape(ok.sum(), -1)
    rel_tr = np.linalg.norm((mean_tr - y_tr)[ok].reshape(ok.sum(), -1), axis=1) / np.maximum(np.linalg.norm(y_tr[ok].reshape(ok.sum(), -1), axis=1), 1e-8)
    E_te = np.abs(mean_te - y_te).reshape(len(y_te), -1); S_te = spread_te.reshape(len(y_te), -1)
    rel_te = np.linalg.norm((mean_te - y_te).reshape(len(y_te), -1), axis=1) / np.maximum(np.linalg.norm(y_te.reshape(len(y_te), -1), axis=1), 1e-8)
    row = dict(name=name, level=L, nfolds=K, folds_seen=sorted(folds_seen), members_per_row=float(cnt_tr[ok].mean()), rows_covered=covered, n_train=n,
               members_test=len(te_members), test_fold=int(pick), grid=list(g), oof_rel_l2=float(rel_tr.mean()), test_rel_l2=float(rel_te.mean()),
               oof_pix_spearman=float(spearman_rows(S_tr, E_tr).mean()), oof_samp_spearman=float(spearman_rows(S_tr.mean(1)[None], rel_tr[None])[0]),
               oof_cov2=float((E_tr <= 2 * S_tr).mean()), test_pix_spearman=float(spearman_rows(S_te, E_te).mean()),
               test_samp_spearman=float(spearman_rows(S_te.mean(1)[None], rel_te[None])[0]), test_cov2=float((E_te <= 2 * S_te).mean()))
    summary.append(row)
    print(f"{name:30s} L{L} K={K} folds {len(folds_seen)}/{K} members/row {row['members_per_row']:.1f} rows {covered}/{n} test members {len(te_members)} | "
          f"OOF rel {row['oof_rel_l2']:.4f} pix {row['oof_pix_spearman']:.2f} samp {row['oof_samp_spearman']:.2f} cov2 {row['oof_cov2']:.2f} | "
          f"test rel {row['test_rel_l2']:.4f} pix {row['test_pix_spearman']:.2f} cov2 {row['test_cov2']:.2f}", flush=True)
json.dump(summary, open(U / "results" / "oof_summary.json", "w"), indent=1)
print(f"assembled {len(summary)} cells -> oof/, results/oof_summary.json")
