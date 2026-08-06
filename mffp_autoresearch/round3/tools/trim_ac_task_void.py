#!/usr/bin/env python
"""ADR r3-0003 D1: remove task-void rows from allen_cahn_2d's test split.

A test row is task-void when its per-row copy-LF gap (canonical variant-C
construction, `round2/eval/panel_data.copylf_prediction`) is below
max(1e-6, 1% of the dataset's median per-row gap): LF ~= HF there, so the row
prices no prediction task and deflates the copy-LF reference.

Idempotent-guarded: refuses to run twice (backup dir is the sentinel).
Applies ONE row mask to every test_l*.npz in the dataset dir (all keys),
archives the originals byte-identical, and records kept/dropped indices in
meta.json. Train files untouched.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import numpy as np

ROOT = Path("/resnick/groups/Hippo/ezeng/mf_field")
DS = ROOT / "benchmark_42" / "sharp" / "allen_cahn_2d"
BACKUP = DS / "_pretrim_backup_2026-08-06"
EVAL = ROOT / "mffp_autoresearch" / "round2" / "eval"
sys.path.insert(0, str(EVAL))

from panel_data import copylf_prediction, load_split  # noqa: E402

NAME = "sharp__allen_cahn_2d"


def per_row_gap():
    data = load_split(NAME, "test")
    pred = copylf_prediction(data, NAME)
    hf = data["field_by_fid"][data["hf_fid"]].reshape(pred.shape[0], -1)
    return np.linalg.norm(pred - hf, axis=1) / np.linalg.norm(hf, axis=1)


def main():
    if BACKUP.exists():
        raise SystemExit("trim already applied (backup dir exists) — refusing to re-run")
    test_files = sorted(DS.glob("test_l*.npz"))
    assert test_files, f"no test files under {DS}"

    gap = per_row_gap()
    thresh = max(1e-6, 0.01 * float(np.median(gap)))
    void = np.where(gap < thresh)[0]
    keep = np.where(gap >= thresh)[0]
    print(f"rows={len(gap)} median_gap={np.median(gap):.3e} thresh={thresh:.3e} "
          f"void={len(void)} keep={len(keep)}")
    assert 0 < len(void) < len(gap) // 2, "unexpected void count — investigate before trimming"

    BACKUP.mkdir()
    for f in test_files:
        shutil.copy2(f, BACKUP / f.name)
        arrs = dict(np.load(f, allow_pickle=False))
        n = {k: (v[keep] if v.ndim >= 1 and v.shape[0] == len(gap) else v) for k, v in arrs.items()}
        np.savez(f, **n)
        print(f"trimmed {f.name}: " + ", ".join(f"{k}{arrs[k].shape}->{n[k].shape}" for k in arrs))

    meta_p = DS / "meta.json"
    meta = json.loads(meta_p.read_text())
    meta["test_trim_2026_08_06"] = {
        "adr": "round3/docs/adr/0003-estimator-integrity-repairs.md D1",
        "criterion": f"per-row canonical copy-LF gap < max(1e-6, 1% of median) = {thresh:.3e}",
        "n_before": int(len(gap)), "n_after": int(len(keep)),
        "dropped_indices": [int(i) for i in void],
        "backup": BACKUP.name,
    }
    meta_p.write_text(json.dumps(meta, indent=2) + "\n")

    # verification against the artifact: re-run the gap on the trimmed split
    gap2 = per_row_gap()
    assert len(gap2) == len(keep) and gap2.min() >= thresh, "post-trim verification failed"
    print(f"VERIFIED: trimmed split n={len(gap2)}, min per-row gap {gap2.min():.3e} >= {thresh:.3e}")


if __name__ == "__main__":
    main()
