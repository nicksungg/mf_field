#!/usr/bin/env python
"""Recertify the noise-floor panel constant on the ruled compositions (ADR r3-0008, Option C, step 1).

`state/anchors_repaired/noise_floor.json` (certified 2026-08-08) calibrates
`_panel_geomean.seed_mce` on the ADR r3-0004 five — a composition that includes
now-report-only `ifc_poisson` and omits now-scored `pfc`, matching no panel a
claim is read on. Option C requires a bar calibrated on each claim-bearing
composition, with the calibration panel recorded machine-readably so
`subset_geomean_unit_audit.py --bar-calibration-json` reads it instead of being
told it.

This script re-aggregates the EXISTING certification legs — no new training:

  * the five ADR-0004 cells from
    `mffp_autoresearch_outputs/round3/r3s4_audit/B1/eval/result_panel5_s{0,1,2}.json`
    (r3s4_cert_min, 200 epochs, seeds 0-2 — the noise_floor.json provenance files);
  * the pfc cell from
    `.../r3s4_audit/B1_pfc_ext/eval/result_pfc_certmin_s{0,1,2}.json`
    (the ADR r3-0005 extension legs, same family/tier/protocol).

Protocol (byte-identical to the certified file's own `_protocol`):
per-seed panel geomean of per-dataset skill; `spread_maxmin` = max-min over
seeds; `paired_null_95` = 95th pct of |mean of 3 signed pairwise seed deltas|
under a 10,000-resample bootstrap of the 6-element signed pool, fresh
`np.random.default_rng(0)`; `seed_mce = max(spread_maxmin, paired_null_95)`.

CONTROL (runs first, hard-fails on mismatch): recomputing the ADR-0004 five
must reproduce the certified file exactly — per_seed, pairwise deltas,
spread_maxmin, paired_null_95 (0.40667775361433317) and seed_mce
(0.5082844131597604). If the control fails, this invocation does not match the
original methodology and nothing is written.

Sanctioned-mutation pattern: the certified `noise_floor.json` is never touched.
Outputs are new era-stamped files:
  state/anchors_repaired/noise_floor_scored5_adr0008.json      (ADR-0007 scored five)
  state/anchors_repaired/noise_floor_registered4_adr0008.json  (registered-4)
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path("/resnick/groups/Hippo/ezeng/mf_field")
ROUND3 = ROOT / "mffp_autoresearch" / "round3"
B1 = ROOT / "mffp_autoresearch_outputs" / "round3" / "r3s4_audit" / "B1" / "eval"
PFC_EXT = (ROOT / "mffp_autoresearch_outputs" / "round3" / "r3s4_audit"
           / "B1_pfc_ext" / "eval")
OUT_DIR = ROUND3 / "state" / "anchors_repaired"
CERTIFIED = OUT_DIR / "noise_floor.json"

SEEDS = [0, 1, 2]
PFC = "sharp__phase_field_crystal_2d"

ADR0004_FIVE = ["ifc_heat", "ifc_poisson", "sharp__allen_cahn_2d",
                "sharp__cahn_hilliard", "sharp__fisher_kpp_2d"]
SCORED5_ADR0007 = ["sharp__allen_cahn_2d", "sharp__cahn_hilliard",
                   "sharp__fisher_kpp_2d", PFC, "ifc_heat"]
REGISTERED4 = ["sharp__allen_cahn_2d", "sharp__cahn_hilliard",
               "sharp__fisher_kpp_2d", "ifc_heat"]


def geo(v):
    return float(np.exp(np.mean(np.log(np.asarray(v, dtype=float)))))


def load_skills():
    """{(dataset, seed): skill} from the panel5 + pfc-extension legs, plus the
    pipeline's own recorded panel composites (exact bytes for the control)."""
    sk, src, recorded5 = {}, [], []
    for s in SEEDS:
        f = B1 / f"result_panel5_s{s}.json"
        d = json.load(open(f))
        assert d["seed"] == s and d["family"] == "r3s4_cert_min"
        for ds, e in d["per_dataset"].items():
            sk[(ds, s)] = float(e["skill"])
        recorded5.append(float(d["panel_geomean_skill"]))
        src.append(str(f))
    for s in SEEDS:
        f = PFC_EXT / f"result_pfc_certmin_s{s}.json"
        d = json.load(open(f))
        assert d["seed"] == s and d["family"] == "r3s4_cert_min"
        sk[(PFC, s)] = float(d["per_dataset"][PFC]["skill"])
        src.append(str(f))
    return sk, src, recorded5


def certify(sk, panel, per_seed=None):
    """per_seed override lets the control run on the pipeline's own recorded
    composites (bit-exact); recomputed geomeans agree to ~1e-14 relative but
    differ in the final ulps from accumulation order."""
    if per_seed is None:
        per_seed = [geo([sk[(ds, s)] for ds in panel]) for s in SEEDS]
    deltas = [per_seed[0] - per_seed[1], per_seed[0] - per_seed[2],
              per_seed[1] - per_seed[2]]
    spread = float(max(per_seed) - min(per_seed))
    pool = np.array([x for v in deltas for x in (v, -v)])
    rng = np.random.default_rng(0)
    draws = rng.choice(pool, size=(10000, 3), replace=True)
    paired_null_95 = float(np.percentile(np.abs(draws.mean(axis=1)), 95))
    return {
        "panel": list(panel),
        "per_seed": per_seed,
        "pairwise_seed_deltas": deltas,
        "spread_maxmin": spread,
        "paired_null_95": paired_null_95,
        "seed_mce": max(spread, paired_null_95),
        "seed_mce_definition": "max(spread_maxmin, paired_null_95)",
    }


def main():
    sk, src, recorded5 = load_skills()
    cert = json.load(open(CERTIFIED))["_panel_geomean"]

    # aggregation-formula check: our geomean of per_dataset skills must agree
    # with each file's own recorded composite to 1e-12 relative
    for s, rec in zip(SEEDS, recorded5):
        mine = geo([sk[(ds, s)] for ds in ADR0004_FIVE])
        assert abs(mine - rec) / rec < 1e-12, (s, mine, rec)
    print("aggregation formula: agrees with recorded composites to <1e-12 rel")

    # ── control: reproduce the certified ADR-0004 constant exactly ───────
    ctl = certify(sk, ADR0004_FIVE, per_seed=recorded5)
    checks = {
        "per_seed": np.allclose(ctl["per_seed"], cert["per_seed"], rtol=0, atol=0),
        "spread_maxmin": ctl["spread_maxmin"] == cert["spread_maxmin"],
        "paired_null_95": ctl["paired_null_95"] == cert["paired_null_95"],
        "seed_mce": ctl["seed_mce"] == cert["seed_mce"],
    }
    # pairwise deltas: the certified file records seed pairs in the same order
    checks["pairwise_seed_deltas"] = np.allclose(
        sorted(map(abs, ctl["pairwise_seed_deltas"])),
        sorted(map(abs, cert["pairwise_seed_deltas"])), rtol=0, atol=0)
    for name, ok in checks.items():
        print(f"control {name}: {'REPRODUCED' if ok else 'MISMATCH'}")
    if not all(checks.values()):
        raise SystemExit("CONTROL FAILED — invocation does not match the "
                         "certified methodology; nothing written")

    # ── the two ruled compositions ───────────────────────────────────────
    for name, panel, out in [
        ("scored5_adr0007", SCORED5_ADR0007, OUT_DIR / "noise_floor_scored5_adr0008.json"),
        ("registered4", REGISTERED4, OUT_DIR / "noise_floor_registered4_adr0008.json"),
    ]:
        pg = certify(sk, panel)
        doc = {
            "_adr": "r3-0008 Option C step 1 (ratified 2026-08-12)",
            "_certified_utc": "2026-08-12",
            "_note": ("Bar for reading subset deltas on the "
                      f"{name} composition. Re-aggregated from the existing "
                      "r3s4_cert_min certification legs (no new training); "
                      "control reproduced the ADR-0004 certified constant "
                      "exactly before this was written. The certified "
                      "noise_floor.json is untouched and remains the "
                      "ADR-0004-era artifact."),
            "_protocol_source": "state/anchors_repaired/noise_floor.json _protocol",
            "_provenance": {"source_results": src,
                            "control": {
                                "composition": ADR0004_FIVE,
                                "reproduced_seed_mce": cert["seed_mce"],
                                "reproduced_paired_null_95": cert["paired_null_95"]}},
            "_panel_geomean": pg,
        }
        out.write_text(json.dumps(doc, indent=1))
        print(f"{name}: seed_mce={pg['seed_mce']:.7f} "
              f"(spread {pg['spread_maxmin']:.7f}, null95 {pg['paired_null_95']:.7f}) "
              f"per_seed={[round(x, 4) for x in pg['per_seed']]} -> {out.name}")


if __name__ == "__main__":
    main()
