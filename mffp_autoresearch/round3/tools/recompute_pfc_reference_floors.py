#!/usr/bin/env python
"""ADR r3-0005 phase 2: recompute pfc's copy-LF reference and training-free
floors under the spectral-rung convention (scored cell L1(32^2)->L3(128^2),
exact FFT zero-pad reference).

Sanctioned-mutation path (the ADR r3-0003 D1 / ac-trim pattern): the amended
round-2 eval code computes the values; only the pfc entries of
`eval/copylf_baselines.json` and `round3/state/anchors_repaired/floors.json`
change, plus the file-level `_copylf_def_hash` (the reference-construction
source changed under the ratified ADR; every other dataset's reference was
verified byte-identical pre/post edit — the seam this script re-asserts on one
sentinel dataset). Both files are archived first.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

import numpy as np

ROOT = Path("/resnick/groups/Hippo/ezeng/mf_field")
EVAL = ROOT / "mffp_autoresearch" / "round2" / "eval"
STATE = ROOT / "mffp_autoresearch" / "round3" / "state"
SC = Path("/tmp/claude-28156/-resnick-groups-Hippo-ezeng-mf-field/4079bc92-1a19-4e4f-bf78-aa24f8b36a1a/scratchpad")
sys.path.insert(0, str(EVAL))

from nrmse import nrmse  # noqa: E402
from panel_data import copylf_prediction, load_split, COPYLF_DEF_HASH  # noqa: E402

NAME = "sharp__phase_field_crystal_2d"
STAMP = "2026-08-10"
ADR_ACCEPT = dict(mean=0.012358, median=0.004520, mn=0.002692, mx=0.148364)


def main():
    # --- seam re-assert on a sentinel (ch): stored value must reproduce exactly ---
    b = json.loads((EVAL / "copylf_baselines.json").read_text())
    ch = load_split("sharp__cahn_hilliard", "test")
    ch_ref = float(nrmse(copylf_prediction(ch, "sharp__cahn_hilliard"),
                         ch["field_by_fid"][ch["hf_fid"]]))
    stored = b["sharp__cahn_hilliard"]["test_nrmse"]
    assert abs(ch_ref - stored) < 1e-12, f"sentinel seam broken: {ch_ref} vs {stored}"

    # --- pfc reference under the amended convention + ADR acceptance re-check ---
    test = load_split(NAME, "test")
    hf_te = np.asarray(test["field_by_fid"][test["hf_fid"]], dtype=np.float64)
    hf_te = hf_te.reshape(hf_te.shape[0], -1)
    pred = copylf_prediction(test, NAME).reshape(hf_te.shape[0], -1)
    ref = float(nrmse(pred, hf_te))
    gaps = np.linalg.norm(pred - hf_te, axis=1) / np.linalg.norm(hf_te, axis=1)
    for k, v in dict(mean=gaps.mean(), median=np.median(gaps), mn=gaps.min(), mx=gaps.max()).items():
        assert abs(v - ADR_ACCEPT[k]) < 5e-6, f"ADR acceptance mismatch on {k}: {v} vs {ADR_ACCEPT[k]}"
    assert (gaps > 1e-4).all(), "task-void rows present — repair did not take"

    # --- training-free floors on the new reference (same definitions as the frozen file) ---
    train = load_split(NAME, "train")
    Xtr = train["cond_by_fid"][train["hf_fid"]]
    ytr = np.asarray(train["field_by_fid"][train["hf_fid"]], dtype=np.float64)
    ytr = ytr.reshape(ytr.shape[0], -1)
    Xte = test["cond_by_fid"][test["hf_fid"]]
    mu, sd = Xtr.mean(0), Xtr.std(0)
    sd[sd == 0] = 1.0
    dist = np.linalg.norm((Xte - mu) / sd - ((Xtr - mu) / sd)[:, None], axis=2)
    nn_idx = dist.argmin(axis=0)
    arms_nrmse = {
        "nn_condition": float(nrmse(ytr[nn_idx], hf_te)),
        "train_mean": float(nrmse(np.tile(ytr.mean(0), (len(hf_te), 1)), hf_te)),
        "zero": float(nrmse(np.zeros_like(hf_te), hf_te)),
    }

    # --- copylf_baselines.json: archive done pre-edit; mutate pfc + re-stamp hash ---
    bp = EVAL / "copylf_baselines.json"
    arch = EVAL / f"copylf_baselines_pre_adr0005_{STAMP}.json"
    assert arch.exists(), "archive missing — create it before running"
    before = {k: v for k, v in b.items() if k != NAME and not k.startswith("_")}
    old_ref = b[NAME]["test_nrmse"]
    b[NAME]["test_nrmse"] = ref
    b[NAME]["convention"] = "spectral_zeropad_rung1"
    b[NAME]["ratio_to_r1"] = (ref / b[NAME]["r1_frozen_nrmse"]) if b[NAME].get("r1_frozen_nrmse") else None
    b["_copylf_def_hash"] = COPYLF_DEF_HASH
    b.setdefault("_changes", {})["pfc_spectral_rung_2026_08_10"] = (
        f"ADR r3-0005: pfc scored cell re-pointed to L1 with the exact spectral reference "
        f"({old_ref:.9g} -> {ref:.9g}); every other dataset's reference verified byte-identical "
        f"pre/post the panel_data amendment (seam hashes in {SC}/copylf_seam_pre.json); "
        "file-level _copylf_def_hash re-stamped (source amendment sanctioned by the ADR); "
        "pre-ADR score caches self-invalidate via the per-entry cache hash check. "
        "Skills across this change are not comparable on pfc.")
    after = {k: v for k, v in b.items() if k != NAME and not k.startswith("_")}
    assert json.dumps(before, sort_keys=True) == json.dumps(after, sort_keys=True), "non-pfc entry drifted"
    bp.write_text(json.dumps(b, indent=2) + "\n")

    # --- floors.json: archive, mutate pfc only ---
    fp = STATE / "anchors_repaired" / "floors.json"
    farch = STATE / "anchors_repaired" / f"floors_pre_adr0005_{STAMP}.json"
    shutil.copy2(fp, farch)
    f = json.loads(fp.read_text())
    fbefore = {k: v for k, v in f.items() if k != NAME and not k.startswith("_")}
    old_entry = f.get(NAME, {})
    new_entry = {}
    for arm, v in arms_nrmse.items():
        new_entry[arm] = {"nrmse": v, "skill": v / ref}
    for k, v in old_entry.items():
        # Carry over metadata INCLUDING dict-valued fields other than the floor
        # arms (the 2026-08-10 run dropped `reference` by skipping all dicts —
        # repaired in floors.json same day; this now preserves the class).
        if k not in new_entry and k not in arms_nrmse:
            new_entry[k] = v
    new_entry["reference"] = {"convention": "spectral_zeropad_rung1",
                              "reference_type": "copylf", "test_nrmse": ref}
    new_entry["_adr_r3_0005"] = (f"reference {old_ref:.9g} -> {ref:.9g} (spectral rung-1 cell); "
                                 f"floors recomputed {STAMP}; pre-ADR entry archived in {farch.name}")
    f[NAME] = new_entry
    f["_copylf_def_hash"] = COPYLF_DEF_HASH  # BOTH files carry the stamp (2026-08-10 miss: only baselines was stamped)
    fafter = {k: v for k, v in f.items() if k != NAME and not k.startswith("_")}
    assert json.dumps(fbefore, sort_keys=True) == json.dumps(fafter, sort_keys=True), "non-pfc floor drifted"
    fp.write_text(json.dumps(f, indent=1) + "\n")

    print(f"pfc reference: {old_ref:.9g} -> {ref:.9g}")
    print("pfc floors (nrmse / skill):")
    for arm, v in arms_nrmse.items():
        print(f"  {arm:14s} {v:.6f} / {v / ref:.4f}")
    print("copylf_baselines.json + floors.json mutated (pfc only, seam-asserted); def hash re-stamped")


if __name__ == "__main__":
    main()
