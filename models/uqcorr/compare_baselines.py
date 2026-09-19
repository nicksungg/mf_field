"""Compare uqcorr corrector arms with the surrogate-track release baselines on the shared datasets."""
import json, csv, math, sys, random
from collections import defaultdict
from pathlib import Path
import numpy as np
B = Path.home() / "Downloads/mf_field_surrogate_bench/results"
U = Path.home() / "Downloads/mf_field_session_20260905/uqcorr/results"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
page = json.load(open(B / "tables/results_page_data.json")); cells = page["cells"]; arms_meta = page["arms"]
rel_elo = json.load(open(B / "tables/elo.json"))
# regenerated table: value + source per cell
reg = {}
with open(B / "tables/st_table_regenerated.csv") as f:
    for row in csv.DictReader(f):
        ds = row["dataset"]
        for k, v in row.items():
            if k == "dataset" or k.endswith("__source") or v in ("", None): continue
            reg[(k, ds)] = (float(v), row.get(k + "__source", ""))
ST_ARMS = sorted(arms_meta)
# my arms: mean over seeds
mine_seed = defaultdict(list)
with open(U / "corr.csv") as f:
    for row in csv.DictReader(f):
        mine_seed[(row["arm"], row["name"])].append(float(row["test"]))
mine = {k: float(np.mean(v)) for k, v in mine_seed.items()}
MY_DS = sorted({ds for _, ds in mine})
MY_ARMS = sorted({a for a, _ in mine})
THETA_ARMS = [a for a in MY_ARMS if not a.endswith("-real")]
REAL_ARMS = [a for a in MY_ARMS if a.endswith("-real")]
print("my datasets", len(MY_DS), "my arms", MY_ARMS)
# release values on my datasets: regenerated (primary) vs page mean-over-seeds
rel = {}; diffs = []
for a in ST_ARMS:
    for ds in MY_DS:
        r = reg.get((a, ds)); p = cells.get(f"{a}|{ds}")
        if r is not None: rel[(a, ds)] = r[0]
        elif p is not None: rel[(a, ds)] = p["v"]
        if r is not None and p is not None: diffs.append((abs(r[0] / p["v"] - 1), a, ds, r[0], p["v"], r[1]))
diffs.sort(reverse=True)
print("regenerated vs page cells on my datasets: n", len(diffs), "median rel diff %.3f" % np.median([d[0] for d in diffs]), "top:", [(round(d[0],3), d[1], d[2], d[5]) for d in diffs[:6]])
missing = [(a, ds) for a in ST_ARMS for ds in MY_DS if (a, ds) not in rel]
print("release cells missing on my datasets:", len(missing), sorted({a for a,_ in missing}), sorted({d for _,d in missing}))

def elo(players, datasets, val, n_orders=500, K=32, base=1500.0, seed=0):
    """compute_elo_full procedure: one match per (pair, dataset), K=32, sequential updates over a random order; mean over orders."""
    matches = [(a, b, d) for i, a in enumerate(players) for b in players[i+1:] for d in datasets if (a, d) in val and (b, d) in val]
    rng = random.Random(seed); acc = {p: [] for p in players}; wl = {p: [0, 0, 0] for p in players}
    for o in range(n_orders):
        rng.shuffle(matches); R = {p: base for p in players}
        for a, b, d in matches:
            va, vb = val[(a, d)], val[(b, d)]; sa = 0.5 if va == vb else (1.0 if va < vb else 0.0)
            ea = 1 / (1 + 10 ** ((R[b] - R[a]) / 400)); R[a] += K * (sa - ea); R[b] += K * ((1 - sa) - (1 - ea))
            if o == 0:
                if sa == 1: wl[a][0] += 1; wl[b][1] += 1
                elif sa == 0: wl[b][0] += 1; wl[a][1] += 1
                else: wl[a][2] += 1; wl[b][2] += 1
        for p in players: acc[p].append(R[p])
    elo.std = {p: float(np.std(acc[p])) for p in players}
    return {p: float(np.mean(acc[p])) for p in players}, wl

# 1) validate the Elo implementation against the release's elo.json (24 arms, 25 datasets minus ext__helmholtz_2d, page cells)
page_val = {(k.split("|")[0], k.split("|")[1]): c["v"] for k, c in cells.items()}
rel_ds = [d for d in page["labds"] if d not in page["elo_degen"]]
e_chk, wl_chk = elo(ST_ARMS, rel_ds, page_val, n_orders=200)
dev = [(a, round(e_chk[a]), rel_elo[a]["elo"], wl_chk[a][0], rel_elo[a]["w"]) for a in ST_ARMS]
print("Elo check (mine vs release; w mine vs release):", max(abs(x[1]-x[2]) for x in dev), "max abs dev;", dev[:5])

# 2) joint table on my datasets
val = dict(rel); val.update({(a, ds): v for (a, ds), v in mine.items()})
ELO_DS = [d for d in MY_DS if d not in page["elo_degen"]]
players_theta = ST_ARMS + THETA_ARMS
e_joint, wl_joint = elo(players_theta, ELO_DS, val); std_joint = dict(elo.std)
players_all = ST_ARMS + MY_ARMS
e_all, wl_all = elo(players_all, ELO_DS, val); std_all = dict(elo.std)
def geo(a, dss):
    xs = [val[(a, d)] for d in dss if (a, d) in val]
    return (math.exp(np.mean(np.log(xs))) if xs else float("nan")), len(xs)
common_ds = [d for d in MY_DS if all((a, d) in val for a in players_all)]
print("datasets with every arm present:", len(common_ds), "of", len(MY_DS), "; absent:", sorted(set(MY_DS) - set(common_ds)))
rows = []
for a in players_all:
    g20, n20 = geo(a, MY_DS); gc, _ = geo(a, common_ds)
    rows.append(dict(arm=a, group=("uqcorr" if a in MY_ARMS else "release"), elo_theta=(round(e_joint[a]) if a in e_joint else None), elo_all=round(e_all[a]), std_all=round(std_all[a]), std_theta=(round(std_joint[a]) if a in std_joint else None), t=wl_all[a][2],
                     w=wl_all[a][0], l=wl_all[a][1], geo20=g20, n20=n20, geo_common=gc,
                     wins=sum(1 for d in MY_DS if (a, d) in val and val[(a, d)] <= min(val[(b, d)] for b in players_all if (b, d) in val))))
rows.sort(key=lambda r: r["elo_all"], reverse=True)
print("\n== joint ranking on my %d datasets (Elo over %d datasets, %d theta-only players / %d incl. real) ==" % (len(MY_DS), len(ELO_DS), len(players_theta), len(players_all)))
print(f"{'arm':26s} {'grp':8s} {'eloT':>5s} {'eloA':>5s} {'w':>4s} {'l':>4s} {'geo20':>8s} {'n':>3s} {'geo_c':>8s} wins")
for r in rows: print(f"{r['arm']:26s} {r['group']:8s} {str(r['elo_theta']):>5s} {r['elo_all']:>5d} {r['w']:>4d} {r['l']:>4d} {r['geo20']:8.4f} {r['n20']:>3d} {r['geo_common']:8.4f} {r['wins']}")

# 3) per-dataset table
KEY = ["mf_fno_transfer_film", "st_film_hf_only", "convnext_unet_film", "mf_fno_allpairs", "fno_fire_distcond", "st_hf_pod_gp", "st_koh_pod", "st_dmfal"]
per = []
print("\n== per dataset ==")
hdr = f"{'dataset':32s} {'rel_best':>9s} {'(arm)':22s} {'film':>8s} {'hf_only':>8s} {'fire':>8s} {'cnx_unet':>8s} | {'r1':>8s} {'r0':>8s} {'best_pred':>9s} {'(arm)':20s} {'best_real':>9s} | {'pred/best':>9s} {'pred/film':>9s} {'pred/fire':>9s} {'real/best':>9s}"
print(hdr)
for d in MY_DS:
    relv = {a: val[(a, d)] for a in ST_ARMS if (a, d) in val}; rb = min(relv, key=relv.get)
    pv = {a: val[(a, d)] for a in THETA_ARMS if not a.startswith("film") and (a, d) in val}; pb = min(pv, key=pv.get)
    rv = {a: val[(a, d)] for a in REAL_ARMS if (a, d) in val}; rbest = min(rv, key=rv.get)
    fire = relv.get("fno_fire_distcond", float("nan")); film = relv.get("mf_fno_transfer_film", float("nan"))
    rec = dict(dataset=d, rel_best=relv[rb], rel_best_arm=rb, film=film, hf_only=relv.get("st_film_hf_only"), fire=fire, cnx=relv.get("convnext_unet_film"),
               allpairs=relv.get("mf_fno_allpairs"), pod_gp=relv.get("st_hf_pod_gp"), koh=relv.get("st_koh_pod"),
               r1=val.get(("film_r1", d)), r0=val.get(("film_r0", d)), best_pred=pv[pb], best_pred_arm=pb, best_real=rv[rbest], best_real_arm=rbest,
               pred_over_best=pv[pb] / relv[rb], pred_over_film=pv[pb] / film, pred_over_fire=pv[pb] / fire, real_over_best=rv[rbest] / relv[rb],
               rel_rank_of_best_pred=1 + sum(1 for v in relv.values() if v < pv[pb]), n_rel=len(relv),
               r1_over_film=(val[("film_r1", d)] / film) if ("film_r1", d) in val else None, r0_over_hf=(val[("film_r0", d)] / relv["st_film_hf_only"]) if ("film_r0", d) in val and "st_film_hf_only" in relv else None)
    per.append(rec)
    print(f"{d:32s} {rec['rel_best']:9.4g} {rb:22s} {film:8.4g} {rec['hf_only']:8.4g} {fire:8.4g} {rec['cnx'] if rec['cnx'] is not None else float('nan'):8.4g} | {rec['r1']:8.4g} {rec['r0']:8.4g} {rec['best_pred']:9.4g} {pb:20s} {rec['best_real']:9.4g} | {rec['pred_over_best']:9.2f} {rec['pred_over_film']:9.2f} {rec['pred_over_fire']:9.2f} {rec['real_over_best']:9.2f}")
gm = lambda xs: math.exp(np.mean(np.log([x for x in xs if x is not None and not math.isnan(x)])))
print("\nsummary: best-pred/release-best geomean %.2f (wins %d/%d); best-pred/film %.2f; best-pred/fire %.2f (beats fire %d/%d); best-real/release-best %.2f (beats best surrogate %d/%d)" % (
    gm([r["pred_over_best"] for r in per]), sum(r["pred_over_best"] <= 1 for r in per), len(per), gm([r["pred_over_film"] for r in per]), gm([r["pred_over_fire"] for r in per]),
    sum(r["pred_over_fire"] < 1 for r in per), len(per), gm([r["real_over_best"] for r in per]), sum(r["real_over_best"] < 1 for r in per), len(per)))
print("rank of best predicted-corrector among the %d release arms per dataset:" % len(ST_ARMS), sorted(r["rel_rank_of_best_pred"] for r in per))
print("consistency film_r1/mf_fno_transfer_film: median %.2f, range %.2f-%.2f" % (np.median([r["r1_over_film"] for r in per]), min(r["r1_over_film"] for r in per), max(r["r1_over_film"] for r in per)))
print("consistency film_r0/st_film_hf_only: median %.2f, range %.2f-%.2f" % (np.median([r["r0_over_hf"] for r in per]), min(r["r0_over_hf"] for r in per), max(r["r0_over_hf"] for r in per)))
# fixed-arm comparisons (single arm, not best-of): convnext-pred_spread and irno-pred vs film / fire
for a in ["convnext-pred", "convnext-pred_spread", "irno-pred", "irno-pred_spread", "transolver-pred"]:
    rf = [val[(a, d)] / val[("mf_fno_transfer_film", d)] for d in MY_DS]; rr = [val[(a, d)] / val[("fno_fire_distcond", d)] for d in MY_DS if ("fno_fire_distcond", d) in val]
    print(f"{a:22s} vs film: geomean ratio {gm(rf):.2f}, wins {sum(x<1 for x in rf)}/{len(rf)} | vs fire: {gm(rr):.2f}, wins {sum(x<1 for x in rr)}/{len(rr)}")
json.dump(dict(ranking=rows, per_dataset=per, datasets=MY_DS, elo_datasets=ELO_DS, arms_meta=arms_meta, release_elo=rel_elo, common_ds=common_ds,
               release_values={f"{a}|{d}": v for (a, d), v in rel.items()}, my_values={f"{a}|{d}": v for (a, d), v in mine.items()},
               my_seed_values={f"{a}|{d}": v for (a, d), v in mine_seed.items()}), open(OUT / "cmp.json", "w"), indent=1)
print("wrote", OUT / "cmp.json")
