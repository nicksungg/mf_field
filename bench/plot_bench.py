"""Build the fair-benchmark error-bar plots + compute/size/latency tables.

Reads results/raw_bench/<family>__<dataset>__e*__s*.json (written by each
family's smoke_eval via data_adapters.metrics.finalize_and_write), and produces:

  results/plots/bench_errorbars_per_model.png  — 9 subplots, 15 datasets each,
        mean per-sample relative-L2 with 95% bootstrap CI error bars (log y).
  results/plots/bench_errorbars_grouped.png    — all models overlaid per dataset.
  results/bench_metrics.csv                     — model,dataset,rel_l2_mean,ci_lo,ci_hi,n_samples,nRMSE_agg
  results/bench_compute.csv                     — per model: params, mean latency ms/sample, mean peak MB, mean train s

Usage: .venv/bin/python bench/plot_bench.py [--epochs 2500] [--seed 42]
Re-runnable at any time; missing (model,dataset) cells are shown as n/a.
"""
from __future__ import annotations

import argparse
import csv
import glob
import io
import json
import os
from pathlib import Path


def _atomic_write_text(path, text):
    tmp = f"{path}.tmp.{os.getpid()}"
    with open(tmp, "w", newline="") as fh:
        fh.write(text)
    os.replace(tmp, path)


def _atomic_savefig(fig, path, **kw):
    tmp = f"{path}.tmp.{os.getpid()}.png"
    fig.savefig(tmp, **kw)
    os.replace(tmp, path)

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "results" / "raw_bench"
PLOTS = ROOT / "results" / "plots"

MODELS = ["fno_mf_stack", "fno_coregionalization", "fno_coreg_residual", "fno_coreg_conditioned", "fno_coreg_lf_hf_transfer",
          "transolver_residual", "transolver_attention_fusion", "v9_baseline",
          "mfrnp", "mf_deeponet", "d_mfd", "mf_fno_transfer", "mf_fno_transfer_2m", "mf_fno_transfer_film", "fno_additive", "fno_autoregressive", "fno_multilevel","fno_fire_distcond","fno_dino_residual","fno_fire_mcdropout"]
DATASETS = ["ifc_heat", "ifc_poisson", "poisson_local", "heat_local", "fluid",
            "era5", "pm_test", "advection_diffusion_generated",
            "allen_cahn_generated", "burgers_generated", "burgers_param_generated",
            "darcy_generated", "heat_generated", "lid_driven_cavity_generated",
            "poisson_generated"]
DSHORT = [d.replace("_generated", "").replace("_local", "·loc") for d in DATASETS]


def load_cell(model, dataset, epochs, seed):
    f = RAW / f"{model}__{dataset}__e{epochs}__s{seed}.json"
    if not f.exists():
        # tolerate any epochs/seed if exact not found
        cand = sorted(glob.glob(str(RAW / f"{model}__{dataset}__*.json")))
        if not cand:
            return None
        f = Path(cand[-1])
    try:
        d = json.load(open(f))
    except Exception:
        return None
    sp = (d.get("splits") or {}).get("test_hf") or {}
    if "rel_l2_mean" not in sp or sp.get("rel_l2_mean") is None:
        return None
    m = sp["rel_l2_mean"]
    if not np.isfinite(m):
        return None
    return {
        "mean": m, "lo": sp.get("rel_l2_ci95_lo", m), "hi": sp.get("rel_l2_ci95_hi", m),
        "n": sp.get("n_samples"), "nrmse_agg": sp.get("nRMSE"),
        "n_params": d.get("n_params"), "latency": d.get("latency_ms_per_sample"),
        "peak_mb": d.get("peak_mem_mb"), "train_s": d.get("train_seconds"),
        "work_grid": d.get("work_grid"),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", default="2500")
    ap.add_argument("--seed", default="42")
    args = ap.parse_args()
    PLOTS.mkdir(parents=True, exist_ok=True)

    grid = {(m, d): load_cell(m, d, args.epochs, args.seed) for m in MODELS for d in DATASETS}

    # ---- metrics CSV ----
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["model", "dataset", "rel_l2_mean", "ci95_lo", "ci95_hi",
                "n_samples", "nRMSE_aggregate", "work_grid"])
    for m in MODELS:
        for d in DATASETS:
            c = grid[(m, d)]
            if c:
                w.writerow([m, d, c["mean"], c["lo"], c["hi"], c["n"],
                            c["nrmse_agg"], c["work_grid"]])
            else:
                w.writerow([m, d, "", "", "", "", "", ""])
    _atomic_write_text(ROOT / "results" / "bench_metrics.csv", buf.getvalue())

    # ---- compute CSV (per model, averaged over datasets it ran on) ----
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["model", "n_params", "mean_latency_ms_per_sample",
                "mean_peak_mem_mb", "mean_train_seconds", "n_datasets_done"])
    for m in MODELS:
        cells = [grid[(m, d)] for d in DATASETS if grid[(m, d)]]
        if not cells:
            w.writerow([m, "", "", "", "", 0]); continue
        params = next((c["n_params"] for c in cells if c["n_params"]), "")
        def avg(key):
            vals = [c[key] for c in cells if isinstance(c.get(key), (int, float))]
            return round(float(np.mean(vals)), 4) if vals else ""
        w.writerow([m, params, avg("latency"), avg("peak_mb"), avg("train_s"), len(cells)])
    _atomic_write_text(ROOT / "results" / "bench_compute.csv", buf.getvalue())

    # ---- per-model error-bar figure ----
    fig, axes = plt.subplots(3, 3, figsize=(22, 13), sharey=True)
    x = np.arange(len(DATASETS))
    for ax, m in zip(axes.flat, MODELS):
        means, los, his = [], [], []
        for d in DATASETS:
            c = grid[(m, d)]
            if c:
                means.append(c["mean"]); los.append(c["mean"] - c["lo"]); his.append(c["hi"] - c["mean"])
            else:
                means.append(np.nan); los.append(0); his.append(0)
        means = np.array(means)
        yerr = np.clip(np.array([los, his]), 0, None)
        ax.bar(x, np.nan_to_num(means, nan=0.0), color="#3a7ca5")
        ax.errorbar(x, means, yerr=yerr, fmt="none", ecolor="k", elinewidth=1, capsize=2)
        for i, mm in enumerate(means):
            if not np.isfinite(mm):
                ax.text(i, 1.3e-4, "n/a", ha="center", va="bottom", fontsize=7, color="0.4", rotation=90)
        ax.axhline(1.0, color="k", lw=0.6, ls=":")
        ax.set_yscale("log"); ax.set_ylim(1e-4, 1e1)
        ax.set_title(m, fontsize=12, fontweight="bold")
        ax.set_xticks(x); ax.set_xticklabels(DSHORT, rotation=90, fontsize=7)
        ax.grid(axis="y", alpha=0.3, which="both")
    fig.suptitle(f"Fair benchmark: per-sample relative-L2 (mean ± 95% bootstrap CI), "
                 f"full-field eval on common working grid, {args.epochs} epochs, seed {args.seed}",
                 fontsize=15, y=1.01)
    fig.supylabel("relative L2 error (log scale, lower is better)")
    fig.tight_layout(rect=[0.01, 0, 1, 0.99])
    out1 = PLOTS / "bench_errorbars_per_model.png"
    _atomic_savefig(fig, out1, dpi=130, bbox_inches="tight"); plt.close(fig)

    # ---- grouped: all models per dataset ----
    fig, ax = plt.subplots(figsize=(24, 9))
    nm = len(MODELS); w = 0.9 / nm
    cmap = plt.cm.tab10(np.linspace(0, 1, nm))
    for j, m in enumerate(MODELS):
        means, los, his = [], [], []
        for d in DATASETS:
            c = grid[(m, d)]
            means.append(c["mean"] if c else np.nan)
            los.append((c["mean"] - c["lo"]) if c else 0)
            his.append((c["hi"] - c["mean"]) if c else 0)
        xj = x + (j - nm / 2) * w + w / 2
        means = np.array(means)
        ax.bar(xj, np.nan_to_num(means, nan=0.0), width=w, color=cmap[j], label=m)
        ax.errorbar(xj, means, yerr=np.clip(np.array([los, his]), 0, None),
                    fmt="none", ecolor="k", elinewidth=0.6, capsize=1.5)
    ax.set_yscale("log"); ax.set_ylim(1e-4, 1e1)
    ax.axhline(1.0, color="k", lw=0.6, ls=":")
    ax.set_xticks(x); ax.set_xticklabels(DSHORT, rotation=45, ha="right", fontsize=9)
    ax.set_ylabel("relative L2 error (log, lower=better)")
    ax.set_title(f"Fair benchmark — all 9 models per dataset (mean ± 95% CI), {args.epochs} ep, seed {args.seed}")
    ax.legend(ncol=3, fontsize=9)
    ax.grid(axis="y", alpha=0.3, which="both")
    fig.tight_layout()
    out2 = PLOTS / "bench_errorbars_grouped.png"
    _atomic_savefig(fig, out2, dpi=130, bbox_inches="tight"); plt.close(fig)

    done = sum(1 for v in grid.values() if v)
    print(f"cells with results: {done}/{len(grid)}")
    print(f"wrote {out1}")
    print(f"wrote {out2}")
    print(f"wrote {ROOT/'results'/'bench_metrics.csv'}")
    print(f"wrote {ROOT/'results'/'bench_compute.csv'}")


if __name__ == "__main__":
    main()
