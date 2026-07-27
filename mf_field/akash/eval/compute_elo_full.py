"""Aggregate the full 42-dataset benchmark: ELO + category breakdowns.

Reads akash/results/raw_full/<model>__<dataset>__e<E>__s<seed>.json for the given
epochs and seed list, averages rel-L2 across seeds per (model,dataset), joins
dataset categories (collection, ndim, degeneracy from characterization), and emits:
  bench_full_metrics.csv   per model x dataset (rel, n_seeds, val_based, category)
  bench_full_elo.csv       ELO + geomean overall / core / ext / sharp / 1D / 2D
  BENCH_FULL.md            ranked leaderboard + breakdowns + excluded buckets

Metric extraction (in priority): splits.test_hf.rel_l2_mean -> splits.*.nRMSE ->
top-level best_val_nRMSE (flagged val_based, e.g. transolver). Datasets that are
MF-useless (characterization) or empirically degenerate (no model beats rel-L2 ~1)
are excluded from the headline ranking and reported separately.

Usage: compute_elo_full.py [--epochs E] [--seeds 42,1,2]
"""
from __future__ import annotations

import argparse, csv, glob, json, math, os, random
from collections import defaultdict

MF = "/orcd/data/faez/001/nick/mf_field"
RAW = f"{MF}/akash/results/raw_full"
OUT = f"{MF}/akash/results"
CHAR = f"{MF}/akash/results/dataset_characterization.csv"
N_ORDERS, K, BASE = 500, 32.0, 1500.0
DEGEN_EMPIRICAL = 0.95     # if best model's rel > this, dataset is unlearnable


def gm(vals):
    vals = [v for v in vals if v and v > 0 and math.isfinite(v)]
    return math.exp(sum(map(math.log, vals)) / len(vals)) if vals else float("nan")


def base_name(ds):
    for p in ("ext__", "sharp__"):
        if ds.startswith(p):
            return p[:-2], ds[len(p):]
    return "core", ds


def load_char():
    """(collection, base_dataset) -> {ndim, mf_useless, hf_corr, hi_freq}."""
    d = {}
    if os.path.exists(CHAR):
        for r in csv.DictReader(open(CHAR)):
            d[(r["collection"], r["dataset"])] = dict(
                ndim=int(r["ndim"]), mf_useless=int(r.get("mf_useless", 0)),
                hf_corr=float(r["lf_hf_pearson"]), hi_freq=float(r["hf_highfreq_ratio"]))
    return d


def extract(d):
    sp = d.get("splits") or {}
    for key in ("test_hf",):
        if key in sp and sp[key].get("rel_l2_mean") is not None:
            return sp[key]["rel_l2_mean"], False
    for k, v in sp.items():
        if isinstance(v, dict) and v.get("rel_l2_mean") is not None:
            return v["rel_l2_mean"], False
    for k, v in sp.items():
        if isinstance(v, dict) and v.get("nRMSE") is not None:
            return v["nRMSE"], False
    if d.get("best_val_nRMSE") is not None:
        return float(d["best_val_nRMSE"]), True      # val-based fallback (transolver)
    return None, False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", default="2500", help="comma list; per cell the MOST-trained result wins")
    ap.add_argument("--seeds", default="42")
    args = ap.parse_args()
    seeds = [int(s) for s in args.seeds.split(",")]
    epochs = sorted((int(e) for e in str(args.epochs).split(",")), reverse=True)  # prefer highest
    char = load_char()

    # gather: per (model,dataset,seed) keep the MOST-trained (max-epoch) result;
    # then per (model,dataset) collect over seeds.
    best_by = {}   # (model,dataset,seed) -> (epoch, rel, val_based)
    for e in epochs:
        for s in seeds:
            for f in glob.glob(f"{RAW}/*__e{e}__s{s}.json"):
                b = os.path.basename(f)[: -len(f"__e{e}__s{s}.json")]
                model, _, ds = b.partition("__")
                try:
                    rel, vb = extract(json.load(open(f)))
                except Exception:
                    rel, vb = None, False
                if rel is None:
                    continue
                key = (model, ds, s)
                if key not in best_by or e > best_by[key][0]:   # epochs sorted desc, so first wins
                    best_by[key] = (e, rel, vb)
    acc = defaultdict(list)
    for (model, ds, s), (e, rel, vb) in best_by.items():
        acc[(model, ds)].append((rel, vb))
    if not acc:
        print("no results"); return

    models = sorted({m for m, _ in acc})
    datasets = sorted({d for _, d in acc})
    # per-cell mean rel
    rel = {}; valbased = defaultdict(bool); nseed = {}
    for (m, d), lst in acc.items():
        rel[(m, d)] = sum(x for x, _ in lst) / len(lst)
        nseed[(m, d)] = len(lst); valbased[m] = valbased[m] or any(vb for _, vb in lst)

    # degeneracy: MF-useless (measured) or empirically unlearnable (best model rel>0.95)
    excl = {}
    for d in datasets:
        coll, bn = base_name(d)
        mfu = char.get((coll, bn), {}).get("mf_useless", 0)
        best = min((rel[(m, d)] for m in models if (m, d) in rel), default=float("nan"))
        emp = math.isfinite(best) and best > DEGEN_EMPIRICAL
        excl[d] = ("MF-useless" if mfu else "") + (("+" if mfu and emp else "") + "unlearnable" if emp else "")
    learn = [d for d in datasets if not excl[d]]

    def cat(d):
        coll, bn = base_name(d)
        ndim = char.get((coll, bn), {}).get("ndim", 2)
        return coll, ndim

    def elo(ds_list):
        matches = []; wins = defaultdict(int); loss = defaultdict(int); tie = defaultdict(int)
        for d in ds_list:
            present = [m for m in models if (m, d) in rel]
            for i in range(len(present)):
                for j in range(i + 1, len(present)):
                    a, b = present[i], present[j]; ra, rb = rel[(a, d)], rel[(b, d)]
                    if abs(ra - rb) < 1e-12: o = 0.5; tie[a] += 1; tie[b] += 1
                    elif ra < rb: o = 1.0; wins[a] += 1; loss[b] += 1
                    else: o = 0.0; loss[a] += 1; wins[b] += 1
                    matches.append((a, b, o))
        racc = defaultdict(list)
        for n in range(N_ORDERS):
            rng = random.Random(7 + n); order = matches[:]; rng.shuffle(order)
            r = {m: BASE for m in models}
            for a, b, o in order:
                ea = 1 / (1 + 10 ** ((r[b] - r[a]) / 400))
                r[a] += K * (o - ea); r[b] += K * ((1 - o) - (1 - ea))
            for m in models: racc[m].append(r[m])
        em = {m: sum(v) / len(v) for m, v in racc.items()}
        es = {m: (sum((x - em[m]) ** 2 for x in v) / len(v)) ** .5 for m, v in racc.items()}
        return em, es, wins, loss, tie

    em, es, wins, loss, tie = elo(learn)
    rows = []
    for m in models:
        sub = lambda pred: gm([rel[(m, d)] for d in learn if (m, d) in rel and pred(cat(d))])
        rows.append(dict(model=m, val_based=int(valbased[m]), elo=round(em[m]), std=round(es[m]),
                         W=wins[m], L=loss[m], T=tie[m],
                         gm_all=round(gm([rel[(m, d)] for d in learn if (m, d) in rel]), 4),
                         gm_core=round(sub(lambda c: c[0] == "core"), 4),
                         gm_ext=round(sub(lambda c: c[0] == "ext"), 4),
                         gm_sharp=round(sub(lambda c: c[0] == "sharp"), 4),
                         gm_1d=round(sub(lambda c: c[1] == 1), 4),
                         gm_2d=round(sub(lambda c: c[1] == 2), 4),
                         n_ds=sum(1 for d in learn if (m, d) in rel)))
    rows.sort(key=lambda r: -r["elo"])

    # write CSVs
    with open(f"{OUT}/bench_full_metrics.csv", "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["model", "dataset", "collection", "ndim", "rel_l2", "n_seeds", "val_based", "excluded"])
        for m in models:
            for d in datasets:
                if (m, d) in rel:
                    coll, nd = cat(d)
                    w.writerow([m, d, coll, nd, round(rel[(m, d)], 6), nseed[(m, d)], int(valbased[m]), excl[d]])
    with open(f"{OUT}/bench_full_elo.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader()
        for r in rows: w.writerow(r)

    md = [f"# Full benchmark — {len(models)} models x {len(learn)} learnable datasets "
          f"(epochs={args.epochs}, seeds={seeds})\n",
          f"Excluded (degenerate): {[d for d in datasets if excl[d]] or 'none'}\n",
          "| # | model | ELO | ±std | W-L-T | gm_all | core | ext | sharp | 1D | 2D | n |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(rows, 1):
        vb = " ⚠val" if r["val_based"] else ""
        md.append(f"| {i} | {r['model']}{vb} | {r['elo']} | {r['std']} | {r['W']}-{r['L']}-{r['T']} | "
                  f"{r['gm_all']} | {r['gm_core']} | {r['gm_ext']} | {r['gm_sharp']} | {r['gm_1d']} | {r['gm_2d']} | {r['n_ds']} |")
    md.append("\n⚠val = metric is held-out **validation** nRMSE (transolver), not the unified HF test split — optimistic, not directly comparable.")
    open(f"{OUT}/BENCH_FULL.md", "w").write("\n".join(md) + "\n")
    print("\n".join(md))
    print(f"\n[wrote] bench_full_elo.csv, bench_full_metrics.csv, BENCH_FULL.md")


if __name__ == "__main__":
    main()
