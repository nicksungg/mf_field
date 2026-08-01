#!/usr/bin/env python
"""Aggregate the end-of-round top-3 seed-confirm results (seeds 0-2).

Report §8 step 2: after the operator-gated `submit_seeds_2_3.sh` runs complete,
re-issue the leaderboard with 3-seed means and the certified seed spreads.

Every number is parsed from the per-seed eval artifacts in the outputs repo;
seed 0 is re-derived the same way and must reproduce the card values exactly
(rel 1e-9) before seeds 1-2 are trusted.  Nothing is typed in by hand.

    .venv/bin/python tools/aggregate_seed_confirm.py            # validate + print
    .venv/bin/python tools/aggregate_seed_confirm.py --update-cards
"""
import argparse
import datetime
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARDS = ROOT / "experiment_cards"
OUTPUTS = ROOT.parent.parent / "mffp_autoresearch_outputs" / "round1"
STATE_OUT = ROOT / "state" / "seed_confirm_2026-08-01.json"

SEEDS = [0, 1, 2]
T975_DF2 = 4.302652729911275  # two-sided 95% t quantile, df = 2 (n = 3 seeds)

CONFIRM = {
    "s4_hybrid_routing": {
        "card": "s4_hybrid_routing/batch_3/B3.json",
        "eval_dir": "s4_hybrid_routing/B3/eval",
        "kind": "diag",
        "diag_field": "nrmse_trained",
        "gates_glob": "gates_s{seed}.json",
        "jobs": {1: 66165252, 2: 66165253},
        "slurm_state": {1: "FAILED", 2: "FAILED"},
    },
    "s6_local": {
        "card": "s6_local/batch_2/B2.json",
        "eval_dir": "s6_local/B2/eval",
        "kind": "diag",
        "diag_field": "nrmse_trained",
        "gates_glob": "validity_gates_s{seed}.json",
        "jobs": {1: 66165254, 2: 66165255},
        "slurm_state": {1: "COMPLETED", 2: "COMPLETED"},
    },
    "s1_poisson": {
        "card": "s1_poisson/batch_3/B3.json",
        "eval_dir": "s1_poisson/B3/eval",
        "kind": "result",
        "jobs": {1: 66165256, 2: 66165257},
        "slurm_state": {1: "COMPLETED", 2: "COMPLETED"},
    },
}


def geomean(vals):
    return math.exp(sum(math.log(v) for v in vals) / len(vals))


def seed_stats(per_seed):
    n = len(per_seed)
    mean = sum(per_seed) / n
    sd = math.sqrt(sum((v - mean) ** 2 for v in per_seed) / (n - 1))
    hw = T975_DF2 * sd / math.sqrt(n)
    return {
        "per_seed": per_seed,
        "mean": mean,
        "sd": sd,
        "min": min(per_seed),
        "max": max(per_seed),
        "ci95": [mean - hw, mean + hw],
        "ci95_basis": "t-interval, df=2, over n=3 independent training seeds",
    }


def check(ok, msg):
    if not ok:
        raise SystemExit(f"SEED-0 VALIDATION FAILED: {msg}")


def close(a, b, tol=1e-9):
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def panel_datasets(res):
    return [ds for ds, v in res["per_dataset"].items()
            if v.get("scope", "panel").startswith("panel")]


def collect_diag_stream(name, cfg, res):
    """s4/s6 layout: diag_{ds}__{arm}_e200_s{seed}.json, skill = nrmse/card ref."""
    eval_dir = OUTPUTS / cfg["eval_dir"]
    arms = sorted(res["panel_geomean_skill"]["per_arm"])
    dss = panel_datasets(res)
    per_arm = {}
    for arm in arms:
        per_seed_geo = []
        for seed in SEEDS:
            skills = []
            for ds in dss:
                d = json.loads((eval_dir / f"diag_{ds}__{arm}_e200_s{seed}.json").read_text())
                check(d["arm"] == arm and d["dataset"] == ds and d["seed"] == seed,
                      f"{name} diag identity mismatch {ds}/{arm}/s{seed}")
                ref = res["per_dataset"][ds]["reference_nrmse"]
                skill = d[cfg["diag_field"]] / ref
                if seed == 0:
                    check(close(d[cfg["diag_field"]], res["per_dataset"][ds]["per_arm_nrmse"][arm]),
                          f"{name} {ds}/{arm} s0 nrmse != card")
                    check(close(skill, res["per_dataset"][ds]["per_arm_skill"][arm]),
                          f"{name} {ds}/{arm} s0 skill != card")
                skills.append(skill)
            per_seed_geo.append(geomean(skills))
        check(close(per_seed_geo[0], res["panel_geomean_skill"]["per_arm"][arm]),
              f"{name} {arm} s0 panel geomean != card ({per_seed_geo[0]} vs "
              f"{res['panel_geomean_skill']['per_arm'][arm]})")
        per_arm[arm] = seed_stats(per_seed_geo)
    return {"panel_datasets": dss, "per_arm_panel_geomean_skill": per_arm}


def collect_result_stream(name, cfg, res):
    """s1 layout: result_ifc_poisson_{arm}_s{seed}.json, single-dataset panel."""
    eval_dir = OUTPUTS / cfg["eval_dir"]
    arms = sorted(res["per_arm"])
    per_arm = {}
    for arm in arms:
        skills, nrmses = [], []
        for seed in SEEDS:
            r = json.loads((eval_dir / f"result_ifc_poisson_{arm}_s{seed}.json").read_text())
            check(r["seed"] == seed, f"{name} {arm} s{seed} seed field mismatch")
            e = r["per_dataset"]["ifc_poisson"]
            if seed == 0:
                check(close(e["nRMSE"], res["per_arm"][arm]["nRMSE"]),
                      f"{name} {arm} s0 nRMSE != card")
                check(close(e["skill"], res["per_arm"][arm]["skill"]),
                      f"{name} {arm} s0 skill != card")
            skills.append(e["skill"])
            nrmses.append(e["nRMSE"])
        per_arm[arm] = seed_stats(skills)
        per_arm[arm]["per_seed_nrmse"] = nrmses
    return {"panel_datasets": ["ifc_poisson"], "per_arm_panel_geomean_skill": per_arm}


def collect_gates(cfg):
    out = {}
    for seed in SEEDS:
        if "gates_glob" not in cfg:
            out[str(seed)] = {"defined": False,
                              "note": "no per-seed verification gate script on this card; "
                                      "SLURM completion is the only in-job check"}
            continue
        p = OUTPUTS / cfg["eval_dir"] / cfg["gates_glob"].format(seed=seed)
        g = json.loads(p.read_text())
        fails = [e for gl in g.get("gates", g).values() if isinstance(gl, list)
                 for e in gl if not e.get("pass", True)]
        out[str(seed)] = {
            "defined": True,
            "all_pass": not fails,
            "failures": [{k: e[k] for k in
                          ("gate", "dataset", "arm", "rel_dev", "tol", "nrmse")
                          if k in e} for e in fails],
        }
    return out


def build():
    doc = {
        "generated_utc": datetime.datetime.now(datetime.timezone.utc)
        .strftime("%Y-%m-%dT%H:%M:%SZ"),
        "protocol": "round1_report.md §8 step 2 — top-3 seed confirms, smoke tier "
                    "(200 epochs), submit_seeds_2_3.sh verbatim at commit ddf5ddb",
        "seeds": SEEDS,
        "streams": {},
    }
    for name, cfg in CONFIRM.items():
        res = json.loads((CARDS / cfg["card"]).read_text())["5_actual_result"]
        coll = (collect_diag_stream if cfg["kind"] == "diag"
                else collect_result_stream)(name, cfg, res)
        gates = collect_gates(cfg)
        confirmed = all(g.get("all_pass", True) for g in gates.values()) and \
            all(s == "COMPLETED" for s in cfg["slurm_state"].values())
        coll.update({
            "jobs": {str(k): v for k, v in cfg["jobs"].items()},
            "slurm_state": {str(k): v for k, v in cfg["slurm_state"].items()},
            "gates": gates,
            "confirmed": confirmed,
        })
        doc["streams"][name] = coll
    return doc


def update_cards(doc):
    for name, cfg in CONFIRM.items():
        path = CARDS / cfg["card"]
        text = path.read_text()
        # preserve the card's existing indent style (line 2's leading whitespace)
        indent = len(text.splitlines()[1]) - len(text.splitlines()[1].lstrip())
        card = json.loads(text)
        res = card["5_actual_result"]
        st = doc["streams"][name]
        res["seeds_available"] = SEEDS

        pg = res["panel_geomean_skill"]
        # which arm the card's headline mean refers to
        mean_arm = next(a for a, v in pg["per_arm"].items()
                        if close(v, pg["mean"]))
        stats = st["per_arm_panel_geomean_skill"][mean_arm]
        pg["per_seed"] = stats["per_seed"]
        if st["confirmed"]:
            pg["mean"] = stats["mean"]
            pg["ci95"] = stats["ci95"]
            pg["mean_basis"] = "3-seed mean (seed confirm 2026-08-01, all checks passed)"
            pg["ci95_note"] = ("t-interval over n=3 independent training seeds "
                               "(df=2); supersedes the in-round single-seed note")
        else:
            pg["mean_basis"] = ("seed 0 (in-round claimable value). Seeds 1-2 trained to "
                                "completion but FAILED the card's own verification gates "
                                "— NOT claimable; recorded as a seed-sensitivity finding. "
                                "3-seed spread in seed_confirm.")
            pg["ci95_note"] = ("no 3-seed CI issued: seeds 1-2 failed V1/V5 gates, so a "
                               "CI over them would launder non-verified runs into the claim")
        res["seed_confirm"] = {
            "date_utc": doc["generated_utc"],
            "jobs": st["jobs"],
            "slurm_state": st["slurm_state"],
            "confirmed": st["confirmed"],
            "gates": st["gates"],
            "per_arm_panel_geomean_skill": st["per_arm_panel_geomean_skill"],
            "source": "tools/aggregate_seed_confirm.py (validates seed 0 against this "
                      "card before trusting seeds 1-2)",
        }

        if name == "s1_poisson":
            # per-seed arrays on this card were designed for exactly this pass
            pd = res["per_dataset"]["ifc_poisson"]
            prim = st["per_arm_panel_geomean_skill"]["gain__ladder_level_intercept"]
            pd["per_seed_nrmse"] = prim["per_seed_nrmse"]
            pd["per_seed_skill"] = prim["per_seed"]
            pd["mean_skill"] = prim["mean"]
            pd["ci95"] = prim["ci95"]
            pd.pop("_ci95_null_reason", None)
            for arm, astats in st["per_arm_panel_geomean_skill"].items():
                res["per_arm"][arm]["per_seed_skill"] = astats["per_seed"]
                res["per_arm"][arm]["skill_3seed_mean"] = astats["mean"]
                res["per_arm"][arm]["skill_3seed_ci95"] = astats["ci95"]

        path.write_text(json.dumps(card, indent=indent) + "\n")
        print(f"updated card {path.relative_to(ROOT)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--update-cards", action="store_true")
    args = ap.parse_args()

    doc = build()
    STATE_OUT.write_text(json.dumps(doc, indent=1) + "\n")
    print(f"wrote {STATE_OUT.relative_to(ROOT)}\n")

    print("| Stream / arm | s0 | s1 | s2 | 3-seed mean | 95% CI | confirmed |")
    print("|---|---|---|---|---|---|---|")
    for name, st in doc["streams"].items():
        for arm, s in st["per_arm_panel_geomean_skill"].items():
            ci = f"[{s['ci95'][0]:.4f}, {s['ci95'][1]:.4f}]"
            print(f"| {name} `{arm}` | " +
                  " | ".join(f"{v:.4f}" for v in s["per_seed"]) +
                  f" | {s['mean']:.4f} | {ci} | {'yes' if st['confirmed'] else 'NO'} |")

    if args.update_cards:
        update_cards(doc)


if __name__ == "__main__":
    main()
