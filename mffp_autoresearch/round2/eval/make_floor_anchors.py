"""Compute + freeze the round-2 training-free floors and stream anchors (spec §3).

All reference numbers are computed ONCE from the full untouched datasets and
frozen in `state/anchors/` BEFORE any experiment runs:

  - copy-LF denominator: from copylf_baselines.json (corrected; run
    make_copylf_baselines.py first).
  - NN-in-condition floor: predict the HF TRAIN field whose condition vector
    is nearest (L2 in per-dim train-standardized condition space) to the test
    condition. Deterministic; ties broken by lowest train index.
  - mean floor: predict the per-cell mean of the HF train fields.
  - zero floor: predict the zero field (nRMSE == 1.0 identically under the
    round's definition; computed anyway as a seam check — the round-1
    helmholtz lesson is that champions can lose to it).

Outputs:
  - state/anchors/floors.json           (per-dataset nRMSE + skill of each floor)
  - state/anchors/{stream}.json         (per-stream anchor files, r2s1-r2s4)
  - state/noise_floor.json              (INHERITED from round-1 batch 0, nRMSE
    seed spreads rescaled by the corrected denominators; provisional until
    r2s4-B1 certifies a round-2 spread — provisional anchors are not numeric
    thresholds, judge against falsification clauses; r1 program §4.5)

Run:  python make_floor_anchors.py
"""
from __future__ import annotations

import datetime
import json
from pathlib import Path

import numpy as np

from nrmse import nrmse, NRMSE_DEF_HASH
from panel_data import COPYLF_DEF_HASH, load_config, load_split, repo_root

EVAL_DIR = Path(__file__).resolve().parent
ROUND_ROOT = EVAL_DIR.parent


def _utc() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def floors_for(ds: str) -> dict:
    tr = load_split(ds, "train")
    te = load_split(ds, "test")
    hf_tr = np.asarray(tr["field_by_fid"][tr["hf_fid"]], dtype=np.float64)
    hf_te = np.asarray(te["field_by_fid"][te["hf_fid"]], dtype=np.float64)
    c_tr = np.asarray(tr["cond_by_fid"][tr["hf_fid"]], dtype=np.float64)
    c_te = np.asarray(te["cond_by_fid"][te["hf_fid"]], dtype=np.float64)
    if hf_tr.shape[1] != hf_te.shape[1]:
        raise ValueError(f"{ds}: train/test HF cell counts differ "
                         f"({hf_tr.shape[1]} vs {hf_te.shape[1]})")
    if c_tr.shape[1] != c_te.shape[1]:
        raise ValueError(f"{ds}: condition dims differ across splits")

    mu, sd = c_tr.mean(axis=0), c_tr.std(axis=0)
    sd = np.where(sd > 0, sd, 1.0)  # constant dims carry no distance
    d2 = (((c_te[:, None, :] - c_tr[None, :, :]) / sd) ** 2).sum(axis=2)
    nn_idx = d2.argmin(axis=1)

    zero_v = nrmse(np.zeros_like(hf_te), hf_te)
    if abs(zero_v - 1.0) > 1e-12:
        raise SystemExit(f"{ds}: zero-floor nRMSE {zero_v!r} != 1.0 — metric seam broken")

    uniq, counts = np.unique(nn_idx, return_counts=True)
    top = np.argsort(counts)[::-1][:5]
    return {
        "n_train_hf": int(hf_tr.shape[0]),
        "n_test": int(hf_te.shape[0]),
        "cond_dim": int(c_tr.shape[1]),
        "nn_condition": {
            "nrmse": nrmse(hf_tr[nn_idx], hf_te),
            "definition": "L2 nearest in per-dim train-standardized condition space; "
                          "tie -> lowest train index",
            "nn_index_hist_top5": {str(int(uniq[i])): int(counts[i]) for i in top},
        },
        "train_mean": {"nrmse": nrmse(np.broadcast_to(hf_tr.mean(axis=0), hf_te.shape), hf_te)},
        "zero": {"nrmse": zero_v},
    }


def main() -> None:
    cfg = load_config()
    with open(EVAL_DIR / "copylf_baselines.json") as f:
        baselines = json.load(f)
    if baselines["_copylf_def_hash"] != COPYLF_DEF_HASH:
        raise SystemExit("copylf_baselines.json was computed under a different "
                         "panel_data.py — re-run make_copylf_baselines.py")

    anchors_dir = ROUND_ROOT / "state" / "anchors"
    anchors_dir.mkdir(parents=True, exist_ok=True)
    utc = _utc()

    floors = {"_certified_utc": utc, "_nrmse_def_hash": NRMSE_DEF_HASH,
              "_copylf_def_hash": COPYLF_DEF_HASH, "_split": "test"}
    print(f"{'dataset':34s} {'copylf':>10s} {'NN':>10s} {'NNskill':>8s} {'mean':>10s} {'zero':>6s}")
    for ds in list(cfg["panel"]) + list(cfg["guard_set"]):
        f = floors_for(ds)
        ref = baselines[ds]["test_nrmse"]
        for arm in ("nn_condition", "train_mean", "zero"):
            f[arm]["skill"] = f[arm]["nrmse"] / ref
        f["reference"] = {"test_nrmse": ref,
                          "reference_type": baselines[ds]["reference_type"],
                          "convention": baselines[ds]["convention"]}
        floors[ds] = f
        print(f"{ds:34s} {ref:10.6f} {f['nn_condition']['nrmse']:10.6f} "
              f"{f['nn_condition']['skill']:8.3f} {f['train_mean']['nrmse']:10.6f} "
              f"{f['zero']['nrmse']:6.3f}")

    with open(anchors_dir / "floors.json", "w") as fh:
        json.dump(floors, fh, indent=2, sort_keys=True)

    # Per-stream anchors: at round start no condition->HF model exists, so the
    # bar every model stream must beat is the best TRAINING-FREE floor per
    # dataset (min of NN/mean/zero skill), aggregated as the panel geomean.
    panel = list(cfg["panel"])
    best_floor_skill = {}
    for ds in panel:
        arms = {a: floors[ds][a]["skill"] for a in ("nn_condition", "train_mean", "zero")}
        best_floor_skill[ds] = {"skill": min(arms.values()),
                                "arm": min(arms, key=arms.get)}
    gm = float(np.exp(np.mean(np.log([v["skill"] for v in best_floor_skill.values()]))))

    for stream in [s["name"] for s in cfg["streams"]]:
        anchor = {
            "stream": stream,
            "source": "training_free_floors",
            "certified_utc": utc,
            "provisional": False,
            "anchor_type": "best_floor_panel_geomean",
            "datasets": panel,
            "value": gm,
            "per_dataset": best_floor_skill,
            "note": "Round-2 launch anchor: geomean over the panel of the best "
                    "training-free floor (NN-in-condition / train-mean / zero) per "
                    "dataset, under the corrected copy-LF denominators (ADR r2-0001). "
                    "skill < 1 vs copy-LF remains the headline deployment claim; "
                    "beating THIS anchor is the minimum bar for any trained model.",
        }
        with open(anchors_dir / f"{stream}.json", "w") as fh:
            json.dump(anchor, fh, indent=2, sort_keys=True)

    # Inherited noise floor: r1 batch-0 per-seed nRMSE rescaled by the corrected
    # denominators. Provisional by construction (LF-consuming model class).
    r1_nf_path = repo_root() / "mffp_autoresearch/round1/state/noise_floor.json"
    with open(r1_nf_path) as fh:
        r1_nf = json.load(fh)
    nf = {"_certified_utc": utc,
          "_provisional": True,
          "_source": "round1-batch0-rescaled",
          "_note": "Per-seed nRMSE spreads from round-1 batch 0 (LF-consuming families), "
                   "skills recomputed under the corrected round-2 denominators. "
                   "PROVISIONAL: not a numeric threshold (r1 program §4.5) until "
                   "r2s4-B1 certifies a condition->HF 3-seed spread at smoke tier."}
    for ds, entry in r1_nf.items():
        if ds.startswith("_") or ds not in baselines:
            continue
        ref = baselines[ds]["test_nrmse"]
        per_seed_skill = [v / ref for v in entry["per_seed_nrmse"]]
        mean_skill = float(np.mean(per_seed_skill))
        spread = float(max(per_seed_skill) - min(per_seed_skill))
        nf[ds] = {"family": entry["family"],
                  "per_seed_nrmse": entry["per_seed_nrmse"],
                  "per_seed_skill": per_seed_skill,
                  "mean_skill": mean_skill,
                  "spread": spread,
                  "min_claimable_effect": max(spread, 0.10 * mean_skill)}
    with open(ROUND_ROOT / "state" / "noise_floor.json", "w") as fh:
        json.dump(nf, fh, indent=2, sort_keys=True)

    print(f"\nbest-floor panel geomean skill (all-stream anchor): {gm:.4f}")
    print(f"wrote {anchors_dir}/floors.json, 4 stream anchors, state/noise_floor.json")


if __name__ == "__main__":
    main()
