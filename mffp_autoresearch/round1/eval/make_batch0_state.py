"""Aggregate batch-0 results into state/noise_floor.json + state/anchors/*.json (gate G3).

Reads mffp_autoresearch_outputs/round1/batch0/eval/<family>__<dataset>_s<seed>.json
(written by run_batch0.sbatch) and certifies:

- state/noise_floor.json — per panel dataset: the best family's per-seed nRMSE/skill,
  spread, and the minimum claimable effect (max(spread, 10% of mean skill) guidance).
- state/anchors/{stream}.json — per program.md §4.5:
    s1_poisson: best certified skill on ifc_poisson
    s2_beyond_copy: skill 1.0 (copy-LF bar), with certified best-skill context
    s3_testtime / s4_hybrid_routing / s5_tuning: champion's panel geomean skill

Run:  python make_batch0_state.py [--eval_dir <dir>]
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
from collections import defaultdict
from pathlib import Path

from nrmse import bootstrap_ci
from panel_data import load_config, repo_root


def utcnow() -> str:
    return subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"],
                          capture_output=True, text=True, check=True).stdout.strip()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--eval_dir", default=None)
    args = p.parse_args()

    root = repo_root()
    cfg = load_config()
    panel = list(cfg["panel"])
    seeds = list(cfg["seed_protocol"]["seeds"])
    eval_dir = Path(args.eval_dir) if args.eval_dir else (
        root / cfg["paths"]["outputs_root"] / "batch0" / "eval"
    )
    state = root / cfg["paths"]["round_root"] / "state"

    # gather: {family: {dataset: {seed: (nrmse, skill)}}}
    data = defaultdict(lambda: defaultdict(dict))
    for f in sorted(eval_dir.glob("*.json")):
        with open(f) as fh:
            r = json.load(fh)
        fam, seed = r["family"], int(r["seed"])
        for ds, entry in r["per_dataset"].items():
            data[fam][ds][seed] = (entry["nRMSE"], entry["skill"])

    missing = [(fam, ds, s) for fam in data for ds in panel for s in seeds
               if s not in data[fam].get(ds, {})]
    if missing:
        raise SystemExit(f"INCOMPLETE batch 0 — missing cells: {missing[:10]}"
                         f"{' ...' if len(missing) > 10 else ''}")

    # noise floor: per dataset, the best family's (by mean skill) per-seed values
    floor = {"_certified_utc": utcnow(), "_families": sorted(data)}
    per_family_geomeans = {}
    for fam in data:
        gms = []
        for s in seeds:
            sk = [data[fam][ds][s][1] for ds in panel]
            gms.append(math.exp(sum(math.log(x) for x in sk) / len(sk)))
        per_family_geomeans[fam] = gms

    for ds in panel:
        best_fam = min(data, key=lambda f: sum(data[f][ds][s][1] for s in seeds))
        skills = [data[best_fam][ds][s][1] for s in seeds]
        nrmses = [data[best_fam][ds][s][0] for s in seeds]
        mean, lo, hi = bootstrap_ci(skills)
        spread = max(skills) - min(skills)
        floor[ds] = {
            "family": best_fam,
            "per_seed_nrmse": nrmses,
            "per_seed_skill": skills,
            "mean_skill": mean,
            "ci95": [lo, hi],
            "spread": spread,
            "min_claimable_effect": max(spread, 0.10 * mean),
        }

    (state / "noise_floor.json").write_text(json.dumps(floor, indent=2, sort_keys=True))

    champion = min(per_family_geomeans, key=lambda f: sum(per_family_geomeans[f]) / len(seeds))
    ch_gms = per_family_geomeans[champion]
    ch_mean, ch_lo, ch_hi = bootstrap_ci(ch_gms)

    def write_anchor(stream, payload):
        base = {"stream": stream, "source": "batch0", "certified_utc": utcnow(),
                "provisional": False}
        base.update(payload)
        (state / "anchors" / f"{stream}.json").write_text(
            json.dumps(base, indent=2, sort_keys=True))

    s1_fam = floor["ifc_poisson"]["family"]
    write_anchor("s1_poisson", {
        "anchor_type": "best_skill_on_dataset", "datasets": ["ifc_poisson"],
        "family": s1_fam, "value": floor["ifc_poisson"]["mean_skill"],
        "per_seed": floor["ifc_poisson"]["per_seed_skill"],
        "ci95": floor["ifc_poisson"]["ci95"],
        "note": "skill vs paper bar 0.036 (ADR 0002); N_hf=5 caveat applies",
    })
    write_anchor("s2_beyond_copy", {
        "anchor_type": "copylf_bar",
        "datasets": [d for d in panel if d != "ifc_poisson"],
        "value": 1.0,
        "certified_best_skills": {d: floor[d]["mean_skill"] for d in panel if d != "ifc_poisson"},
        "note": "the bar is copy-LF itself (skill 1.0); certified best skills show the gap",
    })
    for stream in ("s3_testtime", "s4_hybrid_routing", "s5_tuning"):
        write_anchor(stream, {
            "anchor_type": "champion_panel_geomean", "datasets": panel,
            "family": champion, "value": ch_mean, "per_seed": ch_gms,
            "ci95": [ch_lo, ch_hi],
        })

    print(f"champion: {champion} panel geomean skill {ch_mean:.3f} [{ch_lo:.3f}, {ch_hi:.3f}]")
    print(f"{'dataset':32s} {'best fam':22s} {'mean skill':>10s} {'spread':>8s} {'min effect':>10s}")
    for ds in panel:
        e = floor[ds]
        print(f"{ds:32s} {e['family']:22s} {e['mean_skill']:10.3f} {e['spread']:8.3f} "
              f"{e['min_claimable_effect']:10.3f}")
    print(f"\nwrote {state/'noise_floor.json'} + 5 anchors")


if __name__ == "__main__":
    main()
