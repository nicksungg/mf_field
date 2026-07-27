#!/usr/bin/env python3
import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt


def read_loss_history(csv_path: Path):
    rows = []
    with csv_path.open("r", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)

    if not rows:
        return None

    def pick_col(*names):
        keys = rows[0].keys()
        for n in names:
            if n in keys:
                return n
        return None

    epoch_col = pick_col("epoch")
    train_col = pick_col("train_mse", "train_loss", "train")
    val_col = pick_col("val_mse", "val_loss", "valid_mse", "valid_loss", "val")

    if not train_col or not val_col:
        return None

    epochs = []
    train = []
    val = []

    for i, r in enumerate(rows, start=1):
        e = int(float(r[epoch_col])) if epoch_col and r.get(epoch_col, "") else i
        tv = float(r[train_col]) if r.get(train_col, "") else math.nan
        vv = float(r[val_col]) if r.get(val_col, "") else math.nan
        epochs.append(e)
        train.append(tv)
        val.append(vv)

    return {
        "epochs": epochs,
        "train": train,
        "val": val,
        "train_col": train_col,
        "val_col": val_col,
    }


def scenario_from_run(run_name: str) -> str:
    parts = run_name.split("_seed")
    return parts[0]


def plot_single(run_name: str, data: dict, out_path: Path, yscale: str):
    plt.figure(figsize=(11, 5.5))
    plt.plot(data["epochs"], data["train"], label="Train Loss", linewidth=1.8, alpha=0.75)
    plt.plot(data["epochs"], data["val"], label="Validation Loss", linewidth=2.2, linestyle="--", alpha=0.95)
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.title(f"{run_name}: Training vs Validation Loss")
    if yscale == "log":
        plt.yscale("log")
        plt.ylabel("Loss (log scale)")
    plt.grid(True, alpha=0.25)
    plt.legend()
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=160)
    plt.close()


def plot_group(scenario: str, series: list, out_path: Path):
    plt.figure(figsize=(12, 6))
    for run_name, data in series:
        plt.plot(data["epochs"], data["val"], linewidth=1.6, alpha=0.8, label=run_name)
    plt.yscale("log")
    plt.xlabel("Epoch")
    plt.ylabel("Validation Loss (log scale)")
    plt.title(f"{scenario}: Validation Loss Across Seeds")
    plt.grid(True, alpha=0.25)
    plt.legend(fontsize=8, ncol=2)
    plt.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=160)
    plt.close()


def main():
    parser = argparse.ArgumentParser(description="Plot all training/validation loss curves from checkpoints.")
    parser.add_argument("--checkpoints-dir", type=Path, default=Path("checkpoints"))
    parser.add_argument("--out-dir", type=Path, default=Path("checkpoints/loss_plots"))
    parser.add_argument("--yscale", type=str, default="log", choices=["log", "linear"])
    args = parser.parse_args()

    ckpt_dir = args.checkpoints_dir
    out_dir = args.out_dir

    if not ckpt_dir.exists():
        raise SystemExit(f"Missing checkpoints directory: {ckpt_dir}")

    run_dirs = sorted([d for d in ckpt_dir.iterdir() if d.is_dir()])
    all_runs = []
    grouped = defaultdict(list)

    for d in run_dirs:
        loss_csv = d / "loss_history.csv"
        if not loss_csv.exists():
            continue
        parsed = read_loss_history(loss_csv)
        if not parsed:
            print(f"[skip] {d.name}: unsupported or empty loss_history.csv")
            continue

        run_name = d.name
        all_runs.append((run_name, parsed))
        grouped[scenario_from_run(run_name)].append((run_name, parsed))

        run_plot_path = out_dir / "per_run" / f"{run_name}_{args.yscale}.png"
        plot_single(run_name, parsed, run_plot_path, args.yscale)

    for scenario, series in sorted(grouped.items()):
        group_plot_path = out_dir / "by_scenario" / f"{scenario}_val_{args.yscale}.png"
        plot_group(scenario, sorted(series, key=lambda x: x[0]), group_plot_path)

    print(f"Plotted {len(all_runs)} runs")
    print(f"Per-run plots: {out_dir / 'per_run'}")
    print(f"Scenario plots: {out_dir / 'by_scenario'}")


if __name__ == "__main__":
    main()
