#!/usr/bin/env python
"""Round-3 launch anchors on the ADR r3-0001 panel (5 datasets, helmholtz excluded).

Rerunnable. Two phases, both executed on every run:

1. Training-free floors for the repaired ifc_poisson ladder (NN-in-condition /
   train-mean / zero, paper-bar denominator unchanged by design) + the round-3
   best-floor geomean over the D4 panel.  Sharp floors are reused verbatim from
   `state/anchors_repaired/floors.json` (already computed on repaired data).
2. The four anchor cards' per-seed panel geomeans, rebuilt from the per-(dataset,
   seed) artifacts in `mffp_autoresearch_outputs/round3_anchors/`.  Shipped-row
   ifc entries were quarantined 2026-08-05 (`*_void_ifc_shipped_2026-08-05/`);
   until the repaired-ifc re-score lands, cards are emitted with status
   PENDING_IFC_RESCORE and a sharp-only interim geomean.  Once fresh ifc
   entries exist, re-running this script certifies the full 5-dataset anchors.

Validation seam (reconcile-aggregates-against-raw-rows): before any subset
number is emitted, the aggregation must reproduce the certified 6-dataset
`anchor_summary_3seed_2026-08-03.json` seed geomeans to 5e-3 using the
quarantined shipped-row ifc values — a failed reproduction aborts the run.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path("/resnick/groups/Hippo/ezeng/mf_field")
ROUND3 = ROOT / "mffp_autoresearch" / "round3"
OUT_ANCHORS = ROOT / "mffp_autoresearch_outputs" / "round3_anchors"
EVAL = ROOT / "mffp_autoresearch" / "round2" / "eval"
sys.path.insert(0, str(EVAL))

from nrmse import nrmse, skill, NRMSE_DEF_HASH  # noqa: E402

PANEL = [
    "sharp__phase_field_crystal_2d",
    "sharp__allen_cahn_2d",
    "sharp__fisher_kpp_2d",
    "sharp__cahn_hilliard",
    "ifc_poisson",
    "ifc_heat",  # ADR r3-0001 Amendment A1 (2026-08-05)
]
SHARP4 = PANEL[:4]
IFC = ["ifc_poisson", "ifc_heat"]
PANEL6_R2 = ["ext__helmholtz_2d"] + SHARP4 + ["ifc_poisson"]  # certified-summary panel (round-2 composition)
SEEDS = [0, 1, 2]
CARDS = {
    "r2s1_direct-B2": ("results", "r2s1_selected_form"),
    "r2s1_direct-B3": ("results", "r2s1_stagefree_permode"),
    # r2s2-B1's results/ dir holds a non-certified variant; the cache is the
    # source that reproduces anchor_summary_3seed exactly (checked 2026-08-05).
    "r2s2_stacked-B1": ("cache", "r2s2_stack"),
    "r2s3_lf_train_signal-B3": ("eval_a1", None),
}
VOID_CACHE = "cache_void_ifc_shipped_2026-08-05"
VOID_RESULTS = "results_void_ifc_shipped_2026-08-05"
# datasets whose CERTIFIED-summary values were measured on superseded data; the
# certified-reproduction pass substitutes their quarantined entries for the live
# ones (never mixes). Extend this map with each sanctioned data mutation.
VOID_DATASETS = {
    "ifc_poisson": [VOID_CACHE, VOID_RESULTS],
    "sharp__allen_cahn_2d": ["quarantine_ac_pretrim_2026-08-06"],
    "sharp__phase_field_crystal_2d": ["quarantine_pfc_prebox_2026-08-06"],
}


def void_files(base, suffix_globs):
    out = []
    for dirs in VOID_DATASETS.values():
        for d in dirs:
            for g in suffix_globs:
                out += list((base / d).glob(g))
    return out


def geomean(vals):
    v = np.asarray(vals, dtype=np.float64)
    assert v.size and (v > 0).all()
    return float(np.exp(np.log(v).mean()))


def ifc_floors(name):
    """Training-free floors on a repaired ifc ladder (ADR D3/D6; A1 for ifc_heat)."""
    baselines = json.loads((EVAL / "copylf_baselines.json").read_text())
    ref = baselines[name]["reference"] if "reference" in baselines[name] else baselines[name]["test_nrmse"]
    if isinstance(ref, dict):
        ref = ref["test_nrmse"]
    d = ROOT / "benchmark_42" / "core" / name
    Xtr = np.load(d / "train" / "fidelity_64" / "Xs.npy")
    ytr = np.load(d / "train" / "fidelity_64" / "ys.npy").reshape(len(Xtr), -1)
    Xte = np.load(d / "test" / "fidelity_64" / "Xs.npy")
    yte = np.load(d / "test" / "fidelity_64" / "ys.npy").reshape(len(Xte), -1)
    mu, sd = Xtr.mean(0), Xtr.std(0)
    sd[sd == 0] = 1.0
    dist = np.linalg.norm((Xte - mu) / sd - ((Xtr - mu) / sd)[:, None], axis=2)  # (n_train, n_test)
    nn_idx = dist.argmin(axis=0)  # tie -> lowest train index (argmin convention)
    floors = {
        "nn_condition": {
            "definition": "L2 nearest in per-dim train-standardized condition space; tie -> lowest train index",
            "nrmse": nrmse(ytr[nn_idx], yte),
            "nn_index_hist": {str(i): int((nn_idx == i).sum()) for i in range(len(Xtr))},
        },
        "train_mean": {"nrmse": nrmse(np.tile(ytr.mean(0), (len(yte), 1)), yte)},
        "zero": {"nrmse": 1.0},
    }
    for arm in floors.values():
        arm["skill"] = skill(arm["nrmse"], ref)

    # Degeneracy audit (2026-08-05): affine closed-form floor. FITTED, not
    # training-free — reported next to models (round-2 granted-law discipline),
    # never part of the best_floor anchor. oracle_affine_residual ~0 means the
    # condition->HF map is exactly affine (intrinsic degeneracy evidence).
    def affine_fit(X, Y):
        A = np.hstack([X, np.ones((len(X), 1))])
        W, *_ = np.linalg.lstsq(A, Y, rcond=None)  # min-norm when underdetermined
        return lambda Xq: np.hstack([Xq, np.ones((len(Xq), 1))]) @ W

    aff = nrmse(affine_fit(Xtr, ytr)(Xte), yte)
    floors["affine_on_hf_train"] = {
        "definition": "min-norm least-squares affine map condition->field, fit on the HF train rows; "
                      "mandatory reported arm for ifc claims (program.md section 2), NOT in best_floor",
        "class": "closed_form_fitted",
        "nrmse": aff,
        "skill": skill(aff, ref),
        "oracle_affine_residual_nrmse": nrmse(affine_fit(Xte, yte)(Xte), yte),
    }
    return {
        "reference": {"convention": "paper_bar", "reference_type": "paper_bar", "test_nrmse": ref},
        "cond_dim": int(Xtr.shape[1]),
        "n_train_hf": int(len(Xtr)),
        "n_test": int(len(Xte)),
        "data": f"benchmark_42/core/{name} (repaired nested ladder, adopted 2026-08-05)",
        **floors,
    }


def extract_nrmse(d, path):
    if "nRMSE" in d:
        return float(d["nRMSE"])
    splits = d.get("splits", {})
    if "test_hf" in splits:
        return float(splits["test_hf"]["nRMSE"])
    if "test" in splits:
        return float(splits["test"]["nRMSE"])
    raise SystemExit(f"{path}: no nRMSE (keys {sorted(d)[:8]}, splits {sorted(splits)})")


def load_card_skills(card, mode, family, floors_by_ds, include_void_ifc):
    """{(dataset, seed): skill}; ifc from live dirs only unless include_void_ifc."""
    base = OUT_ANCHORS / card
    refs = json.loads((EVAL / "copylf_baselines.json").read_text())

    def ref_of(ds):
        e = refs[ds]
        return e["test_nrmse"] if "test_nrmse" in e else e["reference"]["test_nrmse"]

    out = {}
    if include_void_ifc:
        # certified-reproduction pass prices with the references in effect when
        # anchor_summary_3seed was certified (pre-A1, pre-ac-trim archive).
        refs = json.loads((EVAL / "copylf_baselines_pre_ifc_heat_2026-08-05.json").read_text())
    if mode == "cache":
        cands = {}
        files = list((base / "cache").glob("*.json"))
        if include_void_ifc:
            # restrict to the certified-summary panel: post-certification datasets
            # (ifc_heat, A1) have no entry in the era refs and no certified row.
            files = [f for f in files
                     if json.loads(f.read_text()).get("dataset") in set(PANEL6_R2) - set(VOID_DATASETS)]
            files += [f for f in void_files(base, ["*.json"])
                      if not f.name.startswith("diag_")
                      and {"dataset", "seed", "nrmse_def_hash"} <= set(json.loads(f.read_text()))]  # cache-schema only
        for f in files:
            d = json.loads(f.read_text())
            if d.get("nrmse_def_hash") != NRMSE_DEF_HASH:
                raise SystemExit(f"{f}: nrmse def hash mismatch")
            key = (d["dataset"], int(d["seed"]))
            cands.setdefault(key, []).append(skill(extract_nrmse(d, f), ref_of(key[0])))
        cert = json.loads((ROUND3 / "state" / "anchor_summary_3seed_2026-08-03.json").read_text())[card]["per_dataset_mean_skill"]
        # resolve duplicates: per dataset, choose the per-seed combination whose
        # 3-seed mean reproduces the certified per-dataset mean.
        from itertools import product
        for ds in {k[0] for k in cands}:
            per_seed = {s: cands[(ds, s)] for s in SEEDS if (ds, s) in cands}
            seeds_here = sorted(per_seed)
            if all(len(v) == 1 for v in per_seed.values()):
                for s in seeds_here:
                    out[(ds, s)] = per_seed[s][0]
                continue
            if ds not in cert:
                raise SystemExit(f"{card}/{ds}: ambiguous cache entries and no certified mean to resolve them")
            for combo in product(*(per_seed[s] for s in seeds_here)):
                if abs(float(np.mean(combo)) - cert[ds]) < 1e-3:
                    for s, v in zip(seeds_here, combo):
                        out[(ds, s)] = v
                    break
            else:
                raise SystemExit(f"{card}/{ds}: no cache combination reproduces certified mean {cert[ds]}")
    elif mode == "results":
        files = list((base / "results" / family).glob("*_e200_s*.json"))
        if include_void_ifc:
            files = [f for f in files
                     if any(f.name.startswith(ds) for ds in set(PANEL6_R2) - set(VOID_DATASETS))]
            files += [f for f in void_files(base, ["*_e200_s*.json"])
                      if any(f.name.startswith(ds) for ds in VOID_DATASETS)]
        for f in files:
            d = json.loads(f.read_text())
            m = re.search(r"_s(\d+)\.json$", f.name)
            if not m:
                raise SystemExit(f"{f}: cannot parse seed from filename")
            ds, seed = d["dataset"], int(m.group(1))
            if d.get("nrmse_def_hash") != NRMSE_DEF_HASH:
                raise SystemExit(f"{f}: nrmse def hash mismatch")
            out[(ds, seed)] = skill(extract_nrmse(d, f), ref_of(ds))
    else:  # r2s3-B3: per-leg eval files, claimable arm A1_lf_cov, mean nRMSE over draws
        files = list((base / "eval").glob("result_*_A1_*.json"))
        if include_void_ifc:
            # certified-reproduction pass: quarantined (superseded-data) entries stand IN
            # PLACE OF the fresh ones — never mixed (they would average together below).
            files = [f for f in files
                     if any(ds in f.name for ds in set(PANEL6_R2) - set(VOID_DATASETS))]
            files += [f for f in void_files(base, ["result_*_A1_*.json"])]
        acc = {}
        for f in files:
            d = json.loads(f.read_text())
            m = re.match(r"^result_(?P<ds>.+?)_[a-z]{2,5}_A1(?:_d(?P<draw>\d+))?_s(?P<s>\d+)\.json$", f.name)
            if not m:
                if re.match(r"^result_guard_", f.name):
                    continue  # guard leg: contract tier, not a panel cell
                raise SystemExit(f"{f}: cannot parse leg filename")
            seed = int(m.group("s"))
            for ds, entry in d["per_dataset"].items():
                acc.setdefault((ds, seed), []).append(float(entry["nRMSE"]))
        for (ds, seed), vals in acc.items():
            out[(ds, seed)] = skill(float(np.mean(vals)), ref_of(ds))
    return out


def main():
    certified = json.loads((ROUND3 / "state" / "anchor_summary_3seed_2026-08-03.json").read_text())
    floors_repaired = json.loads((ROUND3 / "state" / "anchors_repaired" / "floors.json").read_text())

    # ---- phase 1: floors ----
    ifc = {name: ifc_floors(name) for name in IFC}
    best_floor = {}
    for ds in PANEL:
        src = ifc[ds] if ds in IFC else floors_repaired[ds]
        arms = {a: src[a]["skill"] for a in ("nn_condition", "train_mean", "zero")}  # training-free only; affine floor reported separately
        arm = min(arms, key=arms.get)
        best_floor[ds] = {"arm": arm, "skill": arms[arm]}
    best_floor_geomean = geomean([v["skill"] for v in best_floor.values()])

    # ---- phase 2: cards, validated against the certified 6-ds summary ----
    cards_out, pending = {}, []
    for card, (mode, family) in CARDS.items():
        with_void = load_card_skills(card, mode, family, floors_repaired, include_void_ifc=True)
        # validation seam: reproduce the certified summary (6-ds, shipped-ifc)
        if "seed_geomeans" in certified[card]:
            val = [geomean([with_void[(ds, s)] for ds in PANEL6_R2]) for s in SEEDS]
            cert = certified[card]["seed_geomeans"]
            if not np.allclose(sorted(val), sorted(cert), atol=5e-3):
                raise SystemExit(f"{card}: aggregation fails certified reproduction: {val} vs {cert}")
        else:  # r2s3-B3 arm-contrast schema: per-dataset per-seed A1 skills
            val = []
            for ds in PANEL6_R2:
                cert_seed = certified[card]["per_dataset_arm_skills"][ds]["A1"]["per_seed_mean_skill"]
                mine = [with_void[(ds, s)] for s in SEEDS]
                val.append(round(float(np.mean(mine)), 4))
                if not np.allclose(sorted(mine), sorted(cert_seed), atol=5e-3):
                    raise SystemExit(f"{card}/{ds}: A1 per-seed skills fail certified reproduction: {mine} vs {cert_seed}")
        live = load_card_skills(card, mode, family, floors_repaired, include_void_ifc=False)
        have_ifc = all((ds, s) in live for ds in IFC for s in SEEDS)
        entry = {"validated_against_certified_6ds": [round(v, 4) for v in val]}
        if have_ifc:
            sg = [geomean([live[(ds, s)] for ds in PANEL]) for s in SEEDS]
            entry.update(status="CERTIFIED", seed_geomeans=[round(v, 4) for v in sg],
                         mean=round(float(np.mean(sg)), 4),
                         ci95=[round(float(np.mean(sg) - 1.96 * np.std(sg, ddof=1) / np.sqrt(3)), 4),
                               round(float(np.mean(sg) + 1.96 * np.std(sg, ddof=1) / np.sqrt(3)), 4)])
        else:
            sg = [geomean([live[(ds, s)] for ds in SHARP4]) for s in SEEDS]
            entry.update(status="PENDING_IFC_RESCORE", sharp4_seed_geomeans=[round(v, 4) for v in sg],
                         sharp4_mean=round(float(np.mean(sg)), 4))
            pending.append(card)
        entry["per_dataset_mean_skill"] = {
            ds: round(float(np.mean([live[(ds, s)] for s in SEEDS])), 4)
            for ds in (PANEL if have_ifc else SHARP4)}
        cards_out[card] = entry

    out = {
        "_adr": "round3/docs/adr/0001-launch-panel-composition.md (D6; panel per D4 as amended by A1)",
        "_panel": PANEL,
        "_note": ("Round-3 launch anchors over the ADR D4+A1 panel (helmholtz excluded, report-only; "
                  "ifc_poisson and ifc_heat on repaired nested ladders). Shipped-row ifc entries quarantined; "
                  "PENDING_IFC_RESCORE cards certify automatically when the repaired-ifc re-score lands "
                  "and this script is re-run."),
        "best_floor": {"value": round(best_floor_geomean, 4), "per_dataset": best_floor,
                       "source": "training_free_floors"},
        "ifc_floors_repaired": ifc,
        "cards": cards_out,
        "pending_ifc_rescore": pending,
    }
    dest = ROUND3 / "state" / "anchors"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "launch_anchors.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in ("best_floor", "pending_ifc_rescore")}, indent=1))
    for c, e in cards_out.items():
        print(c, e["status"], e.get("seed_geomeans") or e.get("sharp4_seed_geomeans"))
    print("->", dest / "launch_anchors.json")


if __name__ == "__main__":
    main()
