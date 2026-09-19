"""Collect the UQ-corrector diagnostic into results/diag.csv and results/DIAG.md (mean over seeds)."""
import csv, json, math, sys
from collections import defaultdict
from pathlib import Path

U = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent; RAW = U / "raw"; OUT = U / "results"; OUT.mkdir(exist_ok=True)
rows = []; excluded_rows = []
for f in sorted(RAW.glob("*.json")):
    j = json.load(open(f))
    if j.get("excluded"):
        excluded_rows.append((j["name"], j.get("coarse_level"), j["excluded"])); continue
    if j.get("nfolds"):          # K-fold OOF members are assembled by assemble_oof.py, not averaged into the 80/20 tables
        continue
    for split in ("hold", "test"):
        b = j[split]
        rows.append(dict(name=j["name"], level=j["coarse_level"], n_levels=j["n_levels"], variant=j["variant"], seed=j["seed"], split=split,
                         coarse_grid="x".join(map(str, j["coarse_grid"])), fine_grid="x".join(map(str, j["fine_grid"])), pool_abundant=j["pool_abundant"],
                         n_train=j["n_train"], fno=b["fno_coarse_rel_l2"], gap=b["gap_rel_l2"], start=b["pred_start_rel_l2"],
                         ratio_fno_gap=b["ratio_fno_to_gap"], ratio_start_gap=b["ratio_start_to_gap"],
                         sp_pix=b.get("spearman_pixel_mean"), sp_samp=b.get("spearman_sample"), cov2=b.get("coverage_2sigma"),
                         sig_rmse=b.get("sigma_over_rmse"), nll=b.get("nll_per_pixel"), train_s=j["train_seconds"], gpu=j.get("gpu")))
if not rows:
    sys.exit("no results")
with open(OUT / "diag.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

def gm(v):
    v = [x for x in v if x and x > 0 and math.isfinite(x)]
    return math.exp(sum(map(math.log, v)) / len(v)) if v else float("nan")
def mean(v):
    v = [x for x in v if x is not None and math.isfinite(x)]
    return sum(v) / len(v) if v else float("nan")

agg = defaultdict(list)
for r in rows:
    agg[(r["name"], r["level"], r["variant"], r["split"])].append(r)
keys = sorted({(r["name"], r["level"]) for r in rows})
lines = ["# UQ-corrector diagnostic: FiLM-FNO coarse prediction vs the real coarse solve", "",
         "Per dataset and coarse level, mean over seeds; train = 80 % of the paired train rows (plus any coarse-only pool rows), hold = the other 20 %, test = the test split. `fno` = FNO mean vs real coarse (coarse grid); `gap` = rho*prolong(real coarse) vs fine "
         "(what MF-IRNO starts from); `start` = rho*prolong(FNO mean) vs fine (what the proposed U-Net would start from). "
         "`ratio` = fno/gap: below 1 means the FNO's coarse error is smaller than the fidelity gap. Hetero columns: Spearman(sigma,|err|) within a sample, "
         "Spearman across samples, 2-sigma coverage (0.954 if calibrated), sigma/RMSE.", "",
         "| problem | L | grids | split | n_train | gap | fno plain | fno hetero | start plain | ratio plain | ratio hetero | sp_pix | sp_samp | cov2 | sig/rmse |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
for name, level in keys:
    for split in ("hold", "test"):
        pl, he = agg.get((name, level, "plain", split), []), agg.get((name, level, "hetero", split), [])
        any_ = (pl or he)
        if not any_: continue
        r0 = any_[0]
        fmt = lambda x: "—" if x is None or (isinstance(x, float) and math.isnan(x)) else (f"{x:.4g}" if abs(x) < 100 else f"{x:.3g}")
        lines.append("| " + " | ".join([name, f"{level}/{r0['n_levels']-1}", f"{r0['coarse_grid']}->{r0['fine_grid']}", split, str(r0["n_train"]),
                     fmt(gm([r["gap"] for r in any_])), fmt(gm([r["fno"] for r in pl])), fmt(gm([r["fno"] for r in he])), fmt(gm([r["start"] for r in pl])),
                     fmt(gm([r["ratio_fno_gap"] for r in pl])), fmt(gm([r["ratio_fno_gap"] for r in he])),
                     fmt(mean([r["sp_pix"] for r in he])), fmt(mean([r["sp_samp"] for r in he])), fmt(mean([r["cov2"] for r in he])), fmt(mean([r["sig_rmse"] for r in he]))]) + " |")
ex = json.load(open(U / "excluded.json")) if (U / "excluded.json").exists() else {}
if ex or excluded_rows:
    lines += ["", "Excluded:"] + [f"- {k}: {v}" for k, v in ex.items()] + [f"- {n} L{l}: {r}" for n, l, r in sorted(set(excluded_rows))]
done = defaultdict(set)
for r in rows: done[(r["variant"])].add((r["name"], r["level"], r["seed"]))
lines += ["", f"cells: plain {len(done['plain'])}, hetero {len(done['hetero'])} (name x level x seed); {len(rows)//2} result files"]
(OUT / "DIAG.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
