"""Verify training convergence per (family x dataset) from SLURM job logs.

Each akash/logs/bench_<jid>.out has a header line
  'family=<F> dataset=<D> epochs=<E> seed=<S>'
followed by periodic loss prints ('... mse=<v>' or '... loss=<v>'). We take the
final training stage's loss tail and flag a cell as NOT converged if the loss is
still dropping meaningfully at the end (relative improvement over the tail > THRESH).

Usage: convergence_report.py [EPOCHS] [SEED]   (filter to a phase; default all)
Out: akash/results/convergence_report.csv + prints the non-converged list to bump.
"""
from __future__ import annotations

import csv
import glob
import re
import sys
from pathlib import Path

MF = Path("/orcd/data/faez/001/nick/mf_field")
LOGS = MF / "akash/logs"
OUT = MF / "akash/results/convergence_report.csv"
THRESH = 0.05            # tail still improving > 5% => still moving
TAIL_FRAC = 0.30         # use the last 30% of loss points as the "tail"
FLOOR = 1e-3             # BUT if final loss < FLOOR it's already fit (tail drop is cosmetic LR-anneal);
                         # only cells still improving AND with non-negligible final loss are "not converged"

hdr_re = re.compile(r"family=(\S+)\s+dataset=(\S+)\s+epochs=(\d+)\s+seed=(\d+)")
# broad: a metric keyword (any prefix) then = or : then a float. Covers
#   mse=..  loss=..  val_nRMSE=..  "nRMSE (norm units) = .."  "test loss: .."
loss_re = re.compile(r"(?i)(?:nrmse|rmse|mse|loss|err)[a-z _()]*[=:]\s*([0-9.]+(?:[eE][+\-]?\d+)?)")


def analyze(path: Path):
    txt = path.read_text(errors="ignore")
    h = hdr_re.search(txt)
    if not h:
        return None
    fam, ds, ep, seed = h.group(1), h.group(2), int(h.group(3)), int(h.group(4))
    vals = []
    for line in txt.splitlines():
        if "train" in line.lower():      # focus on eval/finetune stage, not warmup/train loss
            continue
        m = loss_re.search(line)
        if not m:
            continue
        try:
            v = float(m.group(1))
            if v == v and v < 1e12:      # drop nan/inf
                vals.append(v)
        except ValueError:
            pass
    if len(vals) < 4:
        return dict(family=fam, dataset=ds, epochs=ep, seed=seed, n_pts=len(vals),
                    final_loss=(vals[-1] if vals else None), improvement=None, converged=None)
    k = max(2, int(len(vals) * TAIL_FRAC))
    tail = vals[-k:]
    v0, v1 = tail[0], tail[-1]
    impr = (v0 - v1) / abs(v0) if v0 != 0 else 0.0
    conv = int(impr < THRESH or v1 < FLOOR)   # converged if plateaued OR already tiny loss
    return dict(family=fam, dataset=ds, epochs=ep, seed=seed, n_pts=len(vals),
                final_loss=v1, improvement=round(impr, 4), converged=conv)


def main():
    ep_filt = int(sys.argv[1]) if len(sys.argv) > 1 else None
    seed_filt = int(sys.argv[2]) if len(sys.argv) > 2 else None
    rows = {}
    for f in glob.glob(str(LOGS / "bench_*.out")):
        r = analyze(Path(f))
        if r is None:
            continue
        if ep_filt and r["epochs"] != ep_filt:
            continue
        if seed_filt is not None and r["seed"] != seed_filt:
            continue
        rows[(r["family"], r["dataset"], r["epochs"], r["seed"])] = r  # last log wins
    rows = list(rows.values())
    if not rows:
        print("no matching logs"); return
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader()
        for r in sorted(rows, key=lambda x: (x["family"], x["dataset"])):
            w.writerow(r)
    judged = [r for r in rows if r["converged"] is not None]
    notconv = [r for r in judged if r["converged"] == 0]
    frac = 1 - len(notconv) / max(len(judged), 1)
    print(f"converged {len(judged)-len(notconv)}/{len(judged)} ({frac:.0%}); "
          f"{len(rows)-len(judged)} unparseable")
    if notconv:
        print("NOT converged (bump epochs):")
        for r in sorted(notconv, key=lambda x: -x["improvement"]):
            print(f"  {r['family']:24s} {r['dataset']:28s} tail_impr={r['improvement']:.2%} final={r['final_loss']:.3e}")
    print(f"[wrote] {OUT}")


if __name__ == "__main__":
    main()
