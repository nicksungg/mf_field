#!/usr/bin/env python
"""ADR r3-0003 D1: recompute allen_cahn_2d's copy-LF reference and training-free
floors on the trimmed (78-row) test split.

Sanctioned-mutation path (PROGRAM_NOTE MUST #5): the unedited round-2 eval code
computes the values; only the ac entries of `eval/copylf_baselines.json` and
`round3/state/anchors_repaired/floors.json` change; both files are archived
first; every other dataset's entry must be byte-identical after (seam).
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import numpy as np

ROOT = Path("/resnick/groups/Hippo/ezeng/mf_field")
EVAL = ROOT / "mffp_autoresearch" / "round2" / "eval"
STATE = ROOT / "mffp_autoresearch" / "round3" / "state"
sys.path.insert(0, str(EVAL))

from nrmse import nrmse, skill  # noqa: E402
from panel_data import copylf_prediction, load_split  # noqa: E402

NAME = "sharp__allen_cahn_2d"
STAMP = "2026-08-06"


def main():
    test = load_split(NAME, "test")
    train = load_split(NAME, "train")
    hf_te = test["field_by_fid"][test["hf_fid"]]
    hf_te = hf_te.reshape(hf_te.shape[0], -1)
    assert hf_te.shape[0] == 78, f"expected trimmed split (78), got {hf_te.shape[0]}"

    ref = float(nrmse(copylf_prediction(test, NAME), hf_te))

    # floors on the trimmed split (same definitions as the frozen floors file)
    Xtr = train["cond_by_fid"][train["hf_fid"]]
    ytr = train["field_by_fid"][train["hf_fid"]]
    ytr = ytr.reshape(ytr.shape[0], -1)
    Xte = test["cond_by_fid"][test["hf_fid"]]
    mu, sd = Xtr.mean(0), Xtr.std(0)
    sd[sd == 0] = 1.0
    dist = np.linalg.norm((Xte - mu) / sd - ((Xtr - mu) / sd)[:, None], axis=2)
    nn_idx = dist.argmin(axis=0)
    arms = {
        "nn_condition": float(nrmse(ytr[nn_idx], hf_te)),
        "train_mean": float(nrmse(np.tile(ytr.mean(0), (len(hf_te), 1)), hf_te)),
        "zero": 1.0,
    }

    # --- copylf_baselines.json (archive, mutate ac only, seam-check the rest) ---
    bp = EVAL / "copylf_baselines.json"
    arch = EVAL / f"copylf_baselines_pre_ac_trim_{STAMP}.json"
    shutil.copy2(bp, arch)
    b = json.loads(bp.read_text())
    before = {k: v for k, v in b.items() if k != NAME and not k.startswith("_")}
    prev = b[NAME]["test_nrmse"]
    b[NAME] = {**b[NAME], "test_nrmse": ref, "pre_trim_nrmse": prev,
               "recomputed": f"{STAMP} ADR r3-0003 D1 (78-row trimmed test split)"}
    b.setdefault("_notes", {})["ac_trim_2026_08_06"] = (
        f"allen_cahn_2d reference recomputed on the trimmed test split "
        f"({prev:.6g} -> {ref:.6g}); pre-trim file archived at {arch.name}. "
        "Skills across the trim are not comparable.")
    after = {k: v for k, v in b.items() if k != NAME and not k.startswith("_")}
    assert before == after, "seam violation: a non-ac entry changed"
    bp.write_text(json.dumps(b, indent=2, sort_keys=True) + "\n")

    # --- floors.json (archive, mutate ac arms only) ---
    fp = STATE / "anchors_repaired" / "floors.json"
    farch = STATE / "anchors_repaired" / f"floors_pre_ac_trim_{STAMP}.json"
    shutil.copy2(fp, farch)
    f = json.loads(fp.read_text())
    old = f[NAME]
    for arm, v in arms.items():
        f[NAME][arm] = {**old[arm], "nrmse": v, "skill": skill(v, ref)}
    f[NAME]["n_test"] = 78
    f[NAME]["reference"] = {**old.get("reference", {}), "test_nrmse": ref}
    f[NAME]["_data_note"] = f"trimmed test split ({STAMP}, ADR r3-0003 D1); pre-trim archived at {farch.name}"
    fp.write_text(json.dumps(f, indent=1, sort_keys=True) + "\n")

    print(json.dumps({"reference": {"pre_trim": prev, "trimmed": ref},
                      "floors_nrmse": arms,
                      "floors_skill": {a: skill(v, ref) for a, v in arms.items()}}, indent=1))


if __name__ == "__main__":
    main()
