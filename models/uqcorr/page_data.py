"""Page-ready JSON + markdown report from cmp.json."""
import json, math, sys
from pathlib import Path
import numpy as np
S = Path(sys.argv[1]); d = json.load(open(S / "cmp.json")); meta = d["arms_meta"]
LABEL = {"irno-pred": "IRNO, predicted", "convnext-pred": "ConvNeXt, predicted", "transolver-pred": "Transolver, predicted",
         "irno-pred_spread": "IRNO, predicted + spread", "convnext-pred_spread": "ConvNeXt, predicted + spread", "transolver-pred_spread": "Transolver, predicted + spread",
         "irno-real": "IRNO, real coarse", "convnext-real": "ConvNeXt, real coarse", "transolver-real": "Transolver, real coarse",
         "film_r1": "FiLM transfer, ours 30k", "film_r0": "FiLM fine-only, ours 30k"}
def group(a):
    if a in LABEL: return "uq-real" if a.endswith("-real") else ("uq-theta" if a.startswith("film") else "uq-pred")
    k = meta[a]["kind"]
    return "rel-paper" if k.startswith("paper") else ("rel-control" if "control" in k else ("rel-floor" if "floor" in k else "rel-mf"))
DSL = {"ext__cahn_hilliard_2d": "ext: cahn_hilliard", "lid_driven_cavity_generated": "cavity", "lid_driven_cavity_v2": "cavity_v2", "ext__pressure_poisson_poiseuille": "ext: pressure_poisson",
       "ext__rayleigh_benard_2d": "ext: rayleigh_benard", "ext__eikonal_2d": "ext: eikonal", "ext__wave_2d": "ext: wave", "ext__helmholtz_2d": "ext: helmholtz",
       "sharp__burgers_2d": "sharp: burgers", "sharp__euler": "sharp: euler", "sharp__helmholtz_2d": "sharp: helmholtz", "sharp__porous_medium_2d": "sharp: porous_medium",
       "sharp__shallow_water_2d": "sharp: shallow_water", "heat_generated": "heat", "poisson_generated": "poisson", "darcy_generated": "darcy"}
lab = lambda n: DSL.get(n, n)
players = [dict(arm=r["arm"], label=(LABEL.get(r["arm"]) or meta[r["arm"]]["label"]), group=group(r["arm"]), elo=r["elo_all"], std=r["std_all"], eloT=r["elo_theta"], stdT=r["std_theta"],
                W=r["w"], L=r["l"], T=r["t"], gm=r["geo20"], wins=r["wins"], how=(meta[r["arm"]]["how"] if r["arm"] in meta else "")) for r in d["ranking"]]
per = []
for r in d["per_dataset"]:
    per.append(dict(name=r["dataset"], label=lab(r["dataset"]), best_arm=r["rel_best_arm"], best_label=meta[r["rel_best_arm"]]["label"], best=r["rel_best"], film=r["film"], hf_only=r["hf_only"], fire=r["fire"], cnx=r["cnx"], allpairs=r["allpairs"], pod_gp=r["pod_gp"], koh=r["koh"],
                    pred=r["best_pred"], pred_arm=LABEL[r["best_pred_arm"]], real=r["best_real"], real_arm=LABEL[r["best_real_arm"]], r1=r["r1"], r0=r["r0"],
                    r_film=r["pred_over_film"], r_fire=r["pred_over_fire"], r_best=r["pred_over_best"], r_real_best=r["real_over_best"], rank=r["rel_rank_of_best_pred"]))
per.sort(key=lambda x: x["r_best"])
gm = lambda xs: math.exp(np.mean(np.log(xs)))
summary = dict(n_ds=len(per), n_elo=len(d["elo_datasets"]), n_players=len(players),
               pred_vs_best=gm([x["r_best"] for x in per]), pred_beats_best=sum(x["r_best"] < 1 for x in per),
               pred_vs_film=gm([x["r_film"] for x in per]), pred_beats_film=sum(x["r_film"] < 1 for x in per),
               pred_vs_fire=gm([x["r_fire"] for x in per]), pred_beats_fire=sum(x["r_fire"] < 1 for x in per),
               real_vs_best=gm([x["r_real_best"] for x in per]), real_beats_best=sum(x["r_real_best"] < 1 for x in per),
               median_rank=float(np.median([x["rank"] for x in per])))
json.dump(dict(players=players, per=per, summary=summary, elo_datasets=d["elo_datasets"]), open(S / "cmp_page.json", "w"))
# markdown report
L = ["# uqcorr correctors vs the surrogate-track release (mf_field_surrogate_bench, 2026-09-12)", "",
     "Shared protocol: the same 20 st_bench datasets, the same 100-sample test split, relative L2 per sample on the working grid (cap 256), arithmetic mean over the seeds available (42 and 123 for the uqcorr arms and most release arms; 42 only for convnext_unet_film, wno_transfer_film, fno_fire_distcond, mf_fno_allpairs). Release values follow the release's own precedence (rerun > re-evaluated checkpoint > legacy JSON; `results/tables/st_table_regenerated.csv`). Elo: every pair of arms plays one match per dataset, lower error wins, K = 32, base 1500, mean over 500 shuffled match orders, ext__helmholtz_2d excluded as unlearnable (the release's own rule; my implementation reproduces the release's elo.json within 14 points and its win counts exactly).", "",
     f"Summary over the {summary['n_ds']} datasets: best solver-free corrector vs the best release arm per dataset, geomean ratio {summary['pred_vs_best']:.2f} (wins {summary['pred_beats_best']}/{summary['n_ds']}); vs FiLM transfer {summary['pred_vs_film']:.2f} (wins {summary['pred_beats_film']}); vs FIRE residual {summary['pred_vs_fire']:.2f} (wins {summary['pred_beats_fire']}); best real-coarse corrector vs best release arm {summary['real_vs_best']:.2f} (wins {summary['real_beats_best']}). Median rank of the best solver-free corrector among the 24 release arms: {summary['median_rank']:.0f}.", "",
     "## Joint ranking (35 players: 24 release arms + 11 uqcorr arms)", "", "| arm | group | Elo (35) | Elo (theta-only 32) | W–L | geomean 20 | per-dataset wins |", "|---|---|---|---|---|---|---|"]
for p in players: L.append(f"| {p['label']} (`{p['arm']}`) | {p['group']} | {p['elo']} ± {p['std']} | {p['eloT'] if p['eloT'] is not None else '—'} | {p['W']}–{p['L']} | {p['gm']:.4f} | {p['wins']} |")
L += ["", "## Per dataset (sorted by best solver-free corrector / best release arm)", "", "| dataset | best release arm | value | FiLM transfer | fine-only | FIRE | all-pairs | POD-GP | KOH | ours r1 | ours r0 | best solver-free | arm | best real-coarse | arm | pred/best | pred/FiLM | pred/FIRE | real/best | rank of pred /24 |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
f = lambda v: f"{v:.3g}"
for x in per: L.append(f"| {x['name']} | {x['best_label']} | {f(x['best'])} | {f(x['film'])} | {f(x['hf_only'])} | {f(x['fire'])} | {f(x['allpairs'])} | {f(x['pod_gp'])} | {f(x['koh'])} | {f(x['r1'])} | {f(x['r0'])} | {f(x['pred'])} | {x['pred_arm']} | {f(x['real'])} | {x['real_arm']} | {x['r_best']:.2f} | {x['r_film']:.2f} | {x['r_fire']:.2f} | {x['r_real_best']:.2f} | {x['rank']} |")
open(S / "BASELINE_CMP.md", "w").write("\n".join(L) + "\n"); print("wrote", S / "BASELINE_CMP.md", S / "cmp_page.json"); print(json.dumps(summary, indent=0))
