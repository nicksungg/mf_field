"""Collect raw/*.json -> results/st_metrics.csv (long), results/st_table.csv (dataset x arm, mean over seeds), results/ST_TABLE.md."""
import argparse, collections, glob, json, math, os
from pathlib import Path
ap = argparse.ArgumentParser(); ap.add_argument("--raw", default="raw"); ap.add_argument("--out", default="results")
ap.add_argument("--anchor-glob", default="/archive/mf_field/operator_library/results/raw_full/mf_fno_transfer_film__*__e2500__s*.json",
                help="leaderboard FiLM-transfer results merged in as arm film_transfer_lb (same test files except the 3 sharp reruns)")
ap.add_argument("--anchor-override-glob", default="/archive/mf_field/experiments/bench_ct/raw/surrogate_film__*__ect__s*.json",
                help="surrogate_film reruns on mf_field_final test files; override the leaderboard anchor for those datasets")
ap.add_argument("--ct-dir", default="raw_ct", help="correction-track arms (theta + real coarse solve at test) on the fixed datasets; reported in a separate table")
ap.add_argument("--lb-dir", default="raw_lb", help="leaderboard-family reruns on the fixed datasets (own smoke_eval.py, e2500)")
a = ap.parse_args()
rows = []
def seed_of(j, path):
    """The FiLM family's finalize_and_write drops the seed; recover it from the filename."""
    if j.get("seed") is not None: return j["seed"]
    tail = os.path.basename(path)[:-5].split("__")[-1]
    return int(tail[1:]) if tail.startswith("s") and tail[1:].isdigit() else None
for f in sorted(glob.glob(f"{a.raw}/*.json")):
    try: j = json.load(open(f))
    except Exception: continue
    s = j.get("splits", {}).get("test_hf", {}); v = s.get("rel_l2_mean")
    rows.append(dict(arm=j["model"], dataset=j["dataset"], seed=seed_of(j, f), rel_l2=v, ci_lo=s.get("rel_l2_ci95_lo"), ci_hi=s.get("rel_l2_ci95_hi"),
                     n_params=j.get("n_params"), train_seconds=j.get("train_seconds"), excluded=j.get("excluded", False), reason=j.get("reason", "")))
for f in sorted(glob.glob(f"{a.lb_dir}/*.json")):
    try: j = json.load(open(f)); s = j["splits"]["test_hf"]
    except Exception: continue
    rows.append(dict(arm=j["model"], dataset=j["dataset"], seed=seed_of(j, f), rel_l2=s.get("rel_l2_mean"), ci_lo=s.get("rel_l2_ci95_lo"), ci_hi=s.get("rel_l2_ci95_hi"),
                     n_params=j.get("n_params"), train_seconds=j.get("train_seconds"), excluded=j.get("excluded", False), reason="rerun_on_fixed_data"))
ct_rows = []
for f in sorted(glob.glob(f"{a.ct_dir}/*.json")):
    try: j = json.load(open(f)); s = j["splits"]["test_hf"]
    except Exception: continue
    ct_rows.append(dict(arm=j["model"], dataset=j["dataset"], seed=seed_of(j, f), rel_l2=s.get("rel_l2_mean"), excluded=j.get("excluded", False), reason=j.get("reason", "")))
anchor = {}
for pat, prio in ((a.anchor_glob, 0), (a.anchor_override_glob, 1), (f"{a.lb_dir}/mf_fno_transfer_film__*__e2500__s*.json", 2)):
    for f in glob.glob(pat):
        try: j = json.load(open(f)); s = j["splits"]["test_hf"]; v = s.get("rel_l2_mean")
        except Exception: continue
        key = (j["dataset"], j.get("seed"))
        if v is not None and (key not in anchor or anchor[key][0] < prio):
            anchor[key] = (prio, dict(arm="film_transfer_lb", dataset=j["dataset"], seed=j.get("seed"), rel_l2=v, ci_lo=s.get("rel_l2_ci95_lo"), ci_hi=s.get("rel_l2_ci95_hi"),
                                      n_params=j.get("n_params"), train_seconds=j.get("train_seconds"), excluded=False, reason={0: "leaderboard", 1: "rerun_on_final_files", 2: "rerun_on_fixed_data"}[prio]))
ours = {r["dataset"] for r in rows}
rows += [v[1] for k, v in anchor.items() if k[0] in ours]
Path(a.out).mkdir(exist_ok=True)
with open(f"{a.out}/st_metrics.csv", "w") as f:
    f.write("arm,dataset,seed,rel_l2,ci_lo,ci_hi,n_params,train_seconds,excluded,reason\n")
    for r in rows: f.write(",".join("" if r[k] is None else str(r[k]).replace(",", ";") for k in ("arm", "dataset", "seed", "rel_l2", "ci_lo", "ci_hi", "n_params", "train_seconds", "excluded", "reason")) + "\n")
cell = collections.defaultdict(list)
for r in rows:
    if r["rel_l2"] is not None and math.isfinite(r["rel_l2"]): cell[(r["dataset"], r["arm"])].append(r["rel_l2"])
arms = sorted({k[1] for k in cell}); dss = sorted({k[0] for k in cell})
gm = {}
for arm in arms:
    common = [d for d in dss if (d, arm) in cell]
    vals = [sum(cell[(d, arm)]) / len(cell[(d, arm)]) for d in common]
    gm[arm] = (math.exp(sum(math.log(max(v, 1e-12)) for v in vals) / len(vals)) if vals else float("nan"), len(common))
wins = collections.Counter()
for d in dss:
    have = [(sum(cell[(d, x)]) / len(cell[(d, x)]), x) for x in arms if (d, x) in cell]
    if have: wins[min(have)[1]] += 1
with open(f"{a.out}/st_table.csv", "w") as f:
    f.write("dataset," + ",".join(arms) + "\n")
    for d in dss: f.write(d + "," + ",".join(f"{sum(cell[(d, x)]) / len(cell[(d, x)]):.6g}" if (d, x) in cell else "" for x in arms) + "\n")
with open(f"{a.out}/ST_TABLE.md", "w") as f:
    f.write("# Surrogate track (theta -> fine field): rel-L2 on the fine test grid, mean over seeds\n\n| arm | geomean | n datasets | wins |\n|---|---|---|---|\n")
    for arm in sorted(arms, key=lambda x: gm[x][0]): f.write(f"| {arm} | {gm[arm][0]:.5f} | {gm[arm][1]} | {wins[arm]} |\n")
    f.write("\n| dataset | " + " | ".join(arms) + " |\n|---|" + "---|" * len(arms) + "\n")
    for d in dss:
        best = min((sum(cell[(d, x)]) / len(cell[(d, x)]), x) for x in arms if (d, x) in cell)[1]
        f.write(f"| {d} | " + " | ".join((("**" if x == best else "") + f"{sum(cell[(d, x)]) / len(cell[(d, x)]):.3e}" + ("**" if x == best else "")) if (d, x) in cell else "-" for x in arms) + " |\n")
    if ct_rows:
        cc = collections.defaultdict(list)
        for r in ct_rows:
            if r["rel_l2"] is not None and math.isfinite(r["rel_l2"]): cc[(r["dataset"], r["arm"])].append(r["rel_l2"])
        carms = sorted({k[1] for k in cc}); cds = sorted({k[0] for k in cc})
        f.write("\n## Correction track (theta + real coarse solve at test) on the fixed datasets\n\n| dataset | " + " | ".join(carms) + " |\n|---|" + "---|" * len(carms) + "\n")
        for d in cds: f.write(f"| {d} | " + " | ".join(f"{sum(cc[(d, x)]) / len(cc[(d, x)]):.3e}" if (d, x) in cc else "-" for x in carms) + " |\n")
    exc = [r for r in rows if r["excluded"]]
    if exc: f.write("\nExcluded cells: " + "; ".join(f"{r['arm']}/{r['dataset']}/s{r['seed']}: {r['reason'][:80]}" for r in exc) + "\n")
print(f"{len(rows)} results, {len(dss)} datasets, {len(arms)} arms -> {a.out}/ST_TABLE.md"); print(open(f"{a.out}/ST_TABLE.md").read()[:3000])
