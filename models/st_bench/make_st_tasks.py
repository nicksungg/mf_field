"""Build task lists for the surrogate-track benchmark, skipping (arm, dataset, seed) cells whose JSON exists.
cpu_tasks.txt : "<rel> classical <seed>"                      (six classical arms in one CPU task)
gpu_tasks.txt : "<rel> <arm> <seed>"  for st_mfdnn st_mfdeeponet st_dmfal film:hf_only film:lf_only film:pooled film:transfer
"""
import argparse, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from st_common import EPOCH_TAG, fac_name
ap = argparse.ArgumentParser()
ap.add_argument("--roster", default="/archive/mf_field/experiments/st_bench/roster.txt")
ap.add_argument("--transfer-for", default="", help="datasets that also get the st_film_transfer arm (empty: the lb:mf_fno_transfer_film rerun is the anchor)")
ap.add_argument("--lb-families", default="mf_fno_transfer_film,mf_fno_transfer_bar,mf_fno_transfer,fno_coregionalization,nomad_mf,mf_deeponet,mfrnp",
                help="leaderboard families rerun through their own smoke_eval.py (e2500) on --lb-for datasets; results in raw_lb/")
ap.add_argument("--lb-for", default="core/poisson_generated_v2,core/lid_driven_cavity_v2,core/lid_driven_cavity_generated")
ap.add_argument("--lb-epochs", type=int, default=2500)
ap.add_argument("--ct-arms", default="analytic,ct_mfirno,ct_mfrnp,ct_mf_deeponet", help="bench_ct correction-track arms (real coarse solve at test) on --ct-for datasets; results in raw_ct/")
ap.add_argument("--ct-for", default="core/poisson_generated_v2,core/lid_driven_cavity_v2,core/lid_driven_cavity_generated")
ap.add_argument("--fill-families", default="wno_transfer_film,convnext_unet_film,fno_fire_distcond,mf_fno_allpairs",
                help="leaderboard families with incomplete coverage: run them on every roster dataset that has no result in raw_lb OR akash/results/raw_full")
ap.add_argument("--lb-legacy", default="/archive/mf_field/akash/results/raw_full")
ap.add_argument("--fill-seeds", default="42", help="seeds to fill for --fill-families; the legacy campaign ran seed 42 only")
ap.add_argument("--raw", default="raw"); ap.add_argument("--seeds", default="42,123"); ap.add_argument("--exclude", default="")
ap.add_argument("--gpu-arms", default="st_mfdnn,st_mfdeeponet,st_dmfal,film:hf_only,film:lf_only,film:pooled", help="film:transfer is not run by default: collect_st.py reuses the leaderboard FiLM-transfer results as the anchor")
ap.add_argument("--only", default="", help="comma list of datasets (rel) to restrict to")
ap.add_argument("--out-gpu", default="gpu_tasks.txt"); ap.add_argument("--out-cpu", default="cpu_tasks.txt")
ap.add_argument("--order", default="arm", choices=["arm", "dataset"], help="arm: cheap neural arms across all datasets first, then FiLM arms")
a = ap.parse_args()
roster = [s.strip() for s in Path(a.roster).read_text().splitlines() if s.strip() and s.strip() not in a.exclude.split(",")]
if a.only:
    roster = [r for r in roster if r in a.only.split(",")]
seeds = [int(s) for s in a.seeds.split(",")]; raw = Path(a.raw)
FILM = {"film:hf_only": ["st_film_hf_only"], "film:lf_only": ["st_film_lf_only", "st_film_affine"], "film:pooled": ["st_film_pooled"], "film:transfer": ["st_film_transfer"]}
CLASSICAL = ["st_mean", "st_knn", "st_hf_pod_gp", "st_lf_affine_pod", "st_koh_pod", "st_nargp_pod"]
done = lambda arm, rel, seed: any((raw / f"{arm}__{fac_name(rel)}__e{t}__s{seed}.json").exists() for t in (EPOCH_TAG, "e" + EPOCH_TAG))   # "eest": tag bug in early st_film runs
gpu, cpu = [], []
for rel in roster:
    for seed in seeds:
        if not all(done(x, rel, seed) for x in CLASSICAL):
            cpu.append(f"{rel} classical {seed}")
        arms = a.gpu_arms.split(",") + (["film:transfer"] if rel in a.transfer_for.split(",") else [])
        for arm in arms:
            outs = FILM.get(arm, [arm])
            if not all(done(x, rel, seed) for x in outs):
                gpu.append(f"{rel} {arm} {seed}")
        if rel in a.ct_for.split(","):
            CT_ANALYTIC = ["ct_copy_lf", "ct_copy_lf_rho", "ct_richardson", "ct_koh_pod"]
            for arm in a.ct_arms.split(","):
                outs = CT_ANALYTIC if arm == "analytic" else [arm]
                if not all((raw.parent / "raw_ct" / f"{x}__{fac_name(rel)}__ect__s{seed}.json").exists() for x in outs):
                    (cpu if arm == "analytic" else gpu).append(f"{rel} ct:{arm} {seed}")
        if rel in a.lb_for.split(","):
            for fam in a.lb_families.split(","):
                if not (raw.parent / "raw_lb" / f"{fam}__{fac_name(rel)}__e{a.lb_epochs}__s{seed}.json").exists():
                    gpu.append(f"{rel} lb:{fam} {seed}")
        if str(seed) in a.fill_seeds.split(","):
            for fam in [x for x in a.fill_families.split(",") if x]:
                name = f"{fam}__{fac_name(rel)}__e{a.lb_epochs}__s{seed}.json"
                if not (raw.parent / "raw_lb" / name).exists() and not (Path(a.lb_legacy) / name).exists():
                    gpu.append(f"{rel} lb:{fam} {seed}")
if a.order == "arm":
    order = ["st_mfdnn", "st_mfdeeponet", "st_dmfal"] + ["lb:" + x for x in (a.lb_families + "," + a.fill_families).split(",")] + ["ct:" + x for x in a.ct_arms.split(",")] + ["film:hf_only", "film:lf_only", "film:pooled", "film:transfer"]
    prio = {x: i for i, x in enumerate(order)}
    gpu.sort(key=lambda t: (prio.get(t.split()[1], 99), int(t.split()[2]), roster.index(t.split()[0])))
Path(a.out_gpu).write_text("\n".join(gpu) + ("\n" if gpu else "")); Path(a.out_cpu).write_text("\n".join(cpu) + ("\n" if cpu else ""))
print(f"gpu tasks: {len(gpu)}   cpu tasks: {len(cpu)}   roster: {len(roster)} datasets x seeds {seeds}")
