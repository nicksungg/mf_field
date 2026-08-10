#!/usr/bin/env python
"""ADR r3-0006: build `state/anchors/film_denominator.json` from the certified
film-transfer runs (round3_anchors/film_baseline-R3, 3 seeds x 5 scored datasets).

For each dataset: per-seed nRMSE, mean (THE denominator), normal-approx 95% CI,
and the exact conversion factor c_ds = ref_copylf(ds) / nRMSE_film(ds) that maps
copy-LF-referenced skills to film-referenced skills. Refuses to build unless
tools/stale_checkpoint_audit.py is clean over the source tree.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path("/resnick/groups/Hippo/ezeng/mf_field")
ROUND3 = ROOT / "mffp_autoresearch" / "round3"
SRC = ROOT / "mffp_autoresearch_outputs" / "round3_anchors" / "film_baseline-R3"
EVAL = ROOT / "mffp_autoresearch" / "round2" / "eval"

PANEL = ["sharp__allen_cahn_2d", "sharp__fisher_kpp_2d", "sharp__cahn_hilliard",
         "ifc_poisson", "ifc_heat"]
SEEDS = [0, 1, 2]
JOBS = {"0": 171858, "1": 171859, "2": 171860}


def main():
    gate = subprocess.run(
        [sys.executable, str(ROUND3 / "tools" / "stale_checkpoint_audit.py"),
         "--root", str(SRC / "results"), "--pattern", "*_e200_s*.json", "--fail-on-stale"],
        capture_output=True, text=True)
    if gate.returncode != 0:
        raise SystemExit(f"stale gate FAILED on the film source tree:\n{gate.stdout}\n{gate.stderr}")

    baselines = json.loads((EVAL / "copylf_baselines.json").read_text())
    out = {"_adr": "round3/docs/adr/0006-film-transfer-denominator.md",
           "_source": str(SRC), "_jobs": JOBS, "_family": "mf_fno_transfer_film",
           "_epochs": 200, "_seeds": SEEDS,
           "_note": ("nRMSE_film mean is THE ADR r3-0006 denominator; c_ds converts "
                     "copy-LF-referenced skills exactly: skill_film = skill_copylf * c_ds. "
                     "Caveat on record: the factory family emits no step metadata, so "
                     "zero_work_resume_scan reads UNDERIVABLE; the clean ckpt-mtime stale "
                     "audit (fresh dirs, fresh training) is the witness."),
           "datasets": {}}
    for ds in PANEL:
        vals = []
        for s in SEEDS:
            f = SRC / "results" / "mf_fno_transfer_film" / f"{ds}_e200_s{s}.json"
            d = json.loads(f.read_text())
            nr = d.get("nRMSE")
            if nr is None:
                nr = d["splits"]["test_hf"]["nRMSE"]
            vals.append(float(nr))
        arr = np.array(vals)
        mean = float(arr.mean())
        ci = 1.96 * float(arr.std(ddof=1)) / np.sqrt(len(arr))
        ref = float(baselines[ds]["test_nrmse"])
        out["datasets"][ds] = {
            "nrmse_film_per_seed": vals,
            "nrmse_film_mean": mean,
            "nrmse_film_ci95": [mean - ci, mean + ci],
            "ref_copylf": ref,
            "c_ds": ref / mean,
            "skill_copylf_of_film": mean / ref,
        }
    gm = float(np.exp(np.mean([np.log(v["skill_copylf_of_film"]) for v in out["datasets"].values()])))
    out["_panel_geomean_skill_copylf_of_film"] = gm
    out["_panel_geomean_c"] = float(np.exp(np.mean([np.log(v["c_ds"]) for v in out["datasets"].values()])))
    dest = ROUND3 / "state" / "anchors" / "film_denominator.json"
    dest.write_text(json.dumps(out, indent=1) + "\n")
    print("wrote", dest)
    for ds, v in out["datasets"].items():
        print(f"  {ds:32s} nRMSE_film {v['nrmse_film_mean']:.6f}  (seeds {['%.4f' % x for x in v['nrmse_film_per_seed']]})  "
              f"skill_copylf(film) {v['skill_copylf_of_film']:.4f}  c_ds {v['c_ds']:.6f}")
    print(f"  panel geomean skill_copylf(film) = {gm:.4f}")


if __name__ == "__main__":
    main()
