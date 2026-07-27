"""Compute the subset ELO leaderboard + per-dataset metrics + smooth/sharp split.

Reads akash/results/raw_bench/<model>__<dataset>__e<EPOCHS>__s<SEED>.json (written
by each model's smoke_eval via finalize_and_write) and produces:
  akash/results/bench_metrics_subset.csv  (per model x dataset rel-L2 + CI + compute)
  akash/results/bench_elo_subset.csv      (ELO leaderboard, geomean overall/smooth/sharp)
  akash/results/SUBSET_COMPARISON.md      (human-readable ranked summary)

ELO: per dataset, the model with the lower per-sample rel-L2 mean wins each pairwise
match (tie if within 1e-9). Matches are replayed in N_ORDERS random orders (seeded),
K=32, base 1500; we report mean/std of the final rating across orders — matching the
methodology behind the existing results/bench_elo.csv.
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
import math
import os
import random
from collections import defaultdict

MF = "/orcd/data/faez/001/nick/mf_field"
RAW = os.path.join(MF, "akash/results/raw_bench")
OUTDIR = os.path.join(MF, "akash/results")

SMOOTH = {"era5", "pm_test", "ifc_poisson", "darcy_generated",
          "lid_driven_cavity_generated", "poisson_local", "heat_local"}
SHARP = {"euler_generated", "burgers_2d_generated", "kuramoto_sivashinsky_generated",
         "shallow_water_2d_generated", "cahn_hilliard_generated"}
ANCHORS = {"mf_fno_transfer_film", "mf_fno_transfer_bar"}

N_ORDERS = 500
K = 32.0
BASE = 1500.0


def gm(vals):
    vals = [v for v in vals if v is not None and v > 0 and math.isfinite(v)]
    if not vals:
        return float("nan")
    return math.exp(sum(math.log(v) for v in vals) / len(vals))


def load(epochs, seed):
    """metric[model][dataset] = dict(rel_l2_mean, nRMSE, ci_lo, ci_hi, n, params, train_s, lat, mem)"""
    metric = defaultdict(dict)
    suffix = f"__e{epochs}__s{seed}.json"
    for f in sorted(glob.glob(os.path.join(RAW, f"*{suffix}"))):
        base = os.path.basename(f)[: -len(suffix)]
        model, _, dataset = base.partition("__")
        try:
            d = json.load(open(f))
            sp = d["splits"]
            k = "test_hf" if "test_hf" in sp else next(iter(sp))
            s = sp[k]
            metric[model][dataset] = dict(
                rel=s.get("rel_l2_mean", s.get("nRMSE")),
                nrmse=s.get("nRMSE"),
                ci_lo=s.get("rel_l2_ci95_lo"), ci_hi=s.get("rel_l2_ci95_hi"),
                n=s.get("n_samples"), params=d.get("n_params"),
                train_s=d.get("train_seconds"), lat=d.get("latency_ms_per_sample"),
                mem=d.get("peak_mem_mb"),
            )
        except Exception as e:
            print(f"[warn] bad result {f}: {e}")
    return metric


def elo(metric):
    models = sorted(metric.keys())
    datasets = sorted({d for m in models for d in metric[m]})
    # build match list: (dataset, mi, mj, outcome_for_mi)  outcome in {1,0,0.5}
    matches = []
    wins = defaultdict(int); losses = defaultdict(int); ties = defaultdict(int)
    for ds in datasets:
        present = [m for m in models if ds in metric[m] and metric[m][ds]["rel"] is not None]
        for a in range(len(present)):
            for b in range(a + 1, len(present)):
                mi, mj = present[a], present[b]
                ri, rj = metric[mi][ds]["rel"], metric[mj][ds]["rel"]
                if abs(ri - rj) < 1e-9:
                    out = 0.5; ties[mi] += 1; ties[mj] += 1
                elif ri < rj:
                    out = 1.0; wins[mi] += 1; losses[mj] += 1
                else:
                    out = 0.0; losses[mi] += 1; wins[mj] += 1
                matches.append((mi, mj, out))
    ratings_acc = defaultdict(list)
    for o in range(N_ORDERS):
        rng = random.Random(1234 + o)
        order = matches[:]
        rng.shuffle(order)
        r = {m: BASE for m in models}
        for mi, mj, out in order:
            ei = 1.0 / (1.0 + 10 ** ((r[mj] - r[mi]) / 400.0))
            r[mi] += K * (out - ei)
            r[mj] += K * ((1.0 - out) - (1.0 - ei))
        for m in models:
            ratings_acc[m].append(r[m])
    elo_mean = {m: sum(v) / len(v) for m, v in ratings_acc.items()}
    elo_std = {m: (sum((x - elo_mean[m]) ** 2 for x in v) / len(v)) ** 0.5
               for m, v in ratings_acc.items()}
    return models, datasets, elo_mean, elo_std, wins, losses, ties


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=2500)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    metric = load(args.epochs, args.seed)
    if not metric:
        print("[compute_elo] no results found — nothing to do"); return
    models, datasets, em, es, wins, losses, ties = elo(metric)

    # per-(model,dataset) metrics CSV
    with open(os.path.join(OUTDIR, "bench_metrics_subset.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["model", "dataset", "rel_l2_mean", "nRMSE", "ci95_lo", "ci95_hi",
                    "n_samples", "n_params", "train_seconds", "latency_ms", "peak_mem_mb"])
        for m in models:
            for ds in sorted(metric[m]):
                r = metric[m][ds]
                w.writerow([m, ds, r["rel"], r["nrmse"], r["ci_lo"], r["ci_hi"],
                            r["n"], r["params"], r["train_s"], r["lat"], r["mem"]])

    # ELO leaderboard CSV
    rows = []
    for m in models:
        ga = gm([metric[m][d]["rel"] for d in metric[m]])
        gs = gm([metric[m][d]["rel"] for d in metric[m] if d in SMOOTH])
        gh = gm([metric[m][d]["rel"] for d in metric[m] if d in SHARP])
        rows.append(dict(model=m, elo_mean=em[m], elo_std=es[m], wins=wins[m],
                         losses=losses[m], ties=ties[m], n_datasets=len(metric[m]),
                         geomean_all=ga, geomean_smooth=gs, geomean_sharp=gh))
    rows.sort(key=lambda r: -r["elo_mean"])
    with open(os.path.join(OUTDIR, "bench_elo_subset.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)

    # markdown summary
    md = ["# Subset comparison — ELO leaderboard\n",
          f"Models: {len(models)} | Datasets: {len(datasets)} "
          f"({len([d for d in datasets if d in SMOOTH])} smooth, "
          f"{len([d for d in datasets if d in SHARP])} sharp) | "
          f"epochs={args.epochs} seed={args.seed}\n",
          "Per-dataset metric = per-sample rel-L2 mean (lower better). "
          "geomean = geometric mean across that regime's datasets.\n",
          "| Rank | Model | ELO | ±std | W-L-T | n_ds | geomean_all | smooth | sharp |",
          "|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(rows, 1):
        tag = " *(anchor)*" if r["model"] in ANCHORS else ""
        md.append(f"| {i} | {r['model']}{tag} | {r['elo_mean']:.0f} | {r['elo_std']:.0f} | "
                  f"{r['wins']}-{r['losses']}-{r['ties']} | {r['n_datasets']} | "
                  f"{r['geomean_all']:.4f} | {r['geomean_smooth']:.4f} | {r['geomean_sharp']:.4f} |")
    # missing cells
    missing = [(m, d) for m in models for d in datasets if d not in metric[m]]
    if missing:
        md.append("\n**Missing cells** (job failed/timed out — excluded from that model's geomean):")
        for m, d in missing:
            md.append(f"- {m} × {d}")
    open(os.path.join(OUTDIR, "SUBSET_COMPARISON.md"), "w").write("\n".join(md) + "\n")

    print("\n".join(md))
    print(f"\n[compute_elo] wrote bench_elo_subset.csv, bench_metrics_subset.csv, SUBSET_COMPARISON.md")


if __name__ == "__main__":
    main()
