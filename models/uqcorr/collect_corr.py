"""Collect stage-2b results (raw_corr/*.json, both corr_ens and film_ctrl schemas) into results/corr.csv and results/CORR.md."""
import csv, json, math, sys
from collections import defaultdict
from pathlib import Path

U = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent; RAW = U / "raw_corr"; OUT = U / "results"; OUT.mkdir(exist_ok=True)
rows = []
for f in sorted(RAW.glob("*.json")):
    j = json.load(open(f)); tag = f.stem; arm = tag.split("__")[0]
    if "splits" in j:                                   # film_ctrl (family JSON)
        s = j["splits"]["test_hf"]
        rows.append(dict(name=j["dataset"], arm=arm, seed=j.get("seed"), test=s["rel_l2_mean"], start=None, real_floor=None, k1=None, k2K=None, train_s=j.get("train_seconds"), params=j.get("n_params")))
    else:
        rows.append(dict(name=j["name"], arm=arm, seed=j["seed"], test=j["test_rel_l2"], start=j["start_rel_l2_test"], real_floor=j["real_copy_rel_l2_test"],
                         k1=j.get("test_rel_l2_K1"), k2K=j.get(f"test_rel_l2_K{2*j['K']}"), train_s=j["train_seconds"], params=j["n_params"]))
if not rows:
    sys.exit("no corrector results")
with open(OUT / "corr.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

def gm(v):
    v = [x for x in v if x is not None and x > 0 and math.isfinite(x)]
    return math.exp(sum(map(math.log, v)) / len(v)) if v else None
fmt = lambda x: "—" if x is None else f"{x:.4g}"
agg = defaultdict(list)
for r in rows: agg[(r["name"], r["arm"])].append(r)
arms = sorted({r["arm"] for r in rows}, key=lambda s: (not s.startswith("film"), s))
names = sorted({r["name"] for r in rows})
lines = ["# Stage 2b: correction from predicted (FNO-ensemble) coarse fields to the fine grid", "",
         "Test rel-L2 at the finest coarse level, geomean over seeds. `start` = rho*prolong(input) copy floor for the predicted input; `real floor` = the same from the real coarse solve. "
         "Arms: <backbone>-<input>; film_r0 = fine-only FiLM-FNO, film_r1 = coarse-pretrained FiLM-FNO (theta-only surrogates).", "",
         "| dataset | real floor | pred start | " + " | ".join(arms) + " |", "|---|---|---|" + "---|" * len(arms)]
for n in names:
    rf = gm([r["real_floor"] for a in arms for r in agg.get((n, a), [])]); st = gm([r["start"] for a in arms if "pred" in a for r in agg.get((n, a), [])])
    lines.append(f"| {n} | {fmt(rf)} | {fmt(st)} | " + " | ".join(fmt(gm([r['test'] for r in agg.get((n, a), [])])) for a in arms) + " |")
lines += ["", "Geomean over datasets present for every arm:"]
common = [n for n in names if all(agg.get((n, a)) for a in arms)]
if common:
    lines.append("| arms | " + " | ".join(arms) + " |"); lines.append("|---|" + "---|" * len(arms))
    lines.append(f"| geomean ({len(common)} sets) | " + " | ".join(fmt(gm([gm([r['test'] for r in agg[(n, a)]]) for n in common])) for a in arms) + " |")
(OUT / "CORR.md").write_text("\n".join(lines) + "\n"); print("\n".join(lines))
