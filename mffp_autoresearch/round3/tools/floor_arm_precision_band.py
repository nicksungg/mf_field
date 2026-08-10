#!/usr/bin/env python
"""Per-ARM floating-point precision band for training-free floor arms,
including `affine_on_hf_train`, and per-arm adjudication of reproduction misses.

**Why this exists beside `tools/floor_precision_seam.py`.** That tool is the
round's floor-precision instrument and this one uses its estimator definitions
verbatim (`ulp_dither`, `rel`, E1 = float64-vs-native-dtype path difference,
E2 = max over B random +-1-ULP dithers of the float32 view, band = max(E1, E2)).
But it hard-codes `FROZEN_ARMS = ("nn_condition", "train_mean", "zero")` and
raises `SystemExit(f"unknown arm {a!r}")` for anything else (`arms_from`, :138),
so it cannot measure `affine_on_hf_train` — the arm `program.md` section 2 makes
MANDATORY next to every ifc number. Measured (`r3s4_audit-B2` turn 2), the
affine band is 1-2 orders of magnitude WIDER than the other arms and exceeds the
round's per-dataset recommended tolerances on 8 of 10 datasets, so a per-DATASET
tolerance (a max over three arms that exclude affine) cannot adjudicate an
affine reproduction claim at all.

**What it adds.**

  * the band for ANY of `affine_on_hf_train` / `nn_condition` / `train_mean` /
    `zero`, per dataset;
  * `--check ds:arm=rel_diff` (repeatable): reads a recorded reproduction
    `rel_diff` against **that arm's own band** rather than the dataset's,
    verdicting `INSIDE_ARM_BAND` (metrology) vs `OUTSIDE_ARM_BAND` (a real
    reproduction failure). Six of `r3s4_audit-B2`'s seven `@full` misses are the
    first; the seventh is only visible as the second under a per-arm reading;
  * the affine design matrix's rank and condition number, which is what predicts
    a wide affine band: a degenerate (zero-variance) condition dimension makes
    the design singular, and the `sd == 0 -> 1.0` remedy that fixes the
    standardized NN distance does NOT reach the affine arm, which fits on the RAW
    condition.

**Run it** before pinning ANY exact-reproduction tolerance that an affine or
rank-deficient arm has to pass, after any regeneration/trim/dtype change, and
whenever a reproduction miss needs adjudicating as metrology vs defect.

REPORT-ONLY: never writes `state/`, never re-freezes a floor, never edits
`floor_precision_seam.py`.

Provenance: `r3s4_audit-B2` turn 2 (card
`experiment_cards/r3s4_audit/batch_2/B2.json` part 6).
"""
from __future__ import annotations

import argparse
import datetime
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np


def _project_root() -> Path:
    here = Path(__file__).resolve()
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                             cwd=str(here.parent), capture_output=True,
                             text=True, check=True)
        return Path(out.stdout.strip())
    except Exception:                                              # noqa: BLE001
        return here.parents[3]


ROOT = _project_root()
sys.path.insert(0, str(ROOT / "mffp_autoresearch" / "round2" / "eval"))
sys.path.insert(0, str(ROOT / "mf_field" / "factory_mffp"))

from nrmse import NRMSE_DEF_HASH, nrmse                            # noqa: E402

ARMS_DEFAULT = "affine_on_hf_train,nn_condition,train_mean,zero"


# ── estimator primitives: VERBATIM from tools/floor_precision_seam.py ──

def ulp_dither(a32, rng):
    a = np.asarray(a32, dtype=np.float32)
    up = np.nextafter(a, np.float32(np.inf))
    dn = np.nextafter(a, np.float32(-np.inf))
    return np.where(rng.integers(0, 2, size=a.shape).astype(bool),
                    up, dn).astype(np.float64)


def rel(a, b):
    d = max(abs(a), abs(b))
    return abs(a - b) / d if d > 0 else 0.0


def standardize_cond(c_tr, c_te):
    mu, sd = c_tr.mean(axis=0), c_tr.std(axis=0)
    sd = np.where(sd > 0, sd, 1.0)
    return (c_tr - mu) / sd, (c_te - mu) / sd


def affine_fit(X, Y):
    A = np.hstack([X, np.ones((len(X), 1))])
    W, *_ = np.linalg.lstsq(A, Y, rcond=None)
    return lambda Xq: np.hstack([Xq, np.ones((len(Xq), 1))]) @ W


def arms_from(c_tr, y_tr, c_te, y_te, arms):
    out = {}
    if "nn_condition" in arms:
        z_tr, z_te = standardize_cond(c_tr, c_te)
        d2 = ((z_te[:, None, :] - z_tr[None, :, :]) ** 2).sum(axis=2)
        out["nn_condition"] = float(nrmse(y_tr[np.argmin(d2, axis=1)], y_te))
    if "train_mean" in arms:
        out["train_mean"] = float(nrmse(np.broadcast_to(
            y_tr.mean(axis=0), y_te.shape), y_te))
    if "affine_on_hf_train" in arms:
        out["affine_on_hf_train"] = float(nrmse(affine_fit(c_tr, y_tr)(c_te), y_te))
    if "zero" in arms:
        out["zero"] = float(nrmse(np.zeros_like(y_te), y_te))
    missing = [a for a in arms if a not in out]
    if missing:
        raise SystemExit(f"unknown arm(s) {missing!r}")
    return out


def load_view(root: Path, dataset: str):
    from data_adapters.loaders import load_mf_dataset
    tr = load_mf_dataset(Path(root) / dataset, "train")
    te = load_mf_dataset(Path(root) / dataset, "test")
    hf = tr["hf_fid"] if tr["hf_fid"] in te["fids"] else te["hf_fid"]
    return (np.asarray(tr["cond_by_fid"][hf]), np.asarray(tr["field_by_fid"][hf]),
            np.asarray(te["cond_by_fid"][hf]), np.asarray(te["field_by_fid"][hf]))


def native_arrays(root: Path, dataset: str, split: str):
    d = Path(root) / dataset
    lv = sorted(int(p.stem.split("_l")[1]) for p in d.glob(f"{split}_l*.npz"))
    if lv:
        z = np.load(d / f"{split}_l{lv[-1]}.npz")
        return np.asarray(z["x"]), np.asarray(z["y"]).reshape(len(z["x"]), -1)
    fids = sorted(int(p.name.split("_")[1]) for p in (d / split).glob("fidelity_*")
                  if (d / split / p.name / "Xs.npy").exists())
    if fids:
        f = fids[-1]
        x = np.load(d / split / f"fidelity_{f}" / "Xs.npy")
        y = np.load(d / split / f"fidelity_{f}" / "ys.npy").reshape(len(x), -1)
        return np.asarray(x), np.asarray(y)
    return None, None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--datasets", default=None,
                    help="comma list; default = keys of --floors-json")
    ap.add_argument("--arms", default=ARMS_DEFAULT)
    ap.add_argument("--b-dither", type=int, default=64)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--stripped-root", default=str(
        ROOT / "mffp_autoresearch/round2/stripped_data"))
    ap.add_argument("--data-root", default=str(ROOT / "mf_field/factory_mffp/data"))
    ap.add_argument("--floors-json", default=str(
        ROOT / "mffp_autoresearch/round3/state/anchors_repaired/floors.json"))
    ap.add_argument("--tolerances-json", default=None,
                    help="a per-DATASET tolerance table (e.g. floor_tolerances.json); "
                         "each arm band is reported against it")
    ap.add_argument("--check", action="append", default=[],
                    help="ds:arm=rel_diff — adjudicate a recorded reproduction "
                         "miss against that ARM's own band (repeatable)")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)

    arms = [x for x in a.arms.split(",") if x]
    floors = json.loads(Path(a.floors_json).read_text()) if Path(a.floors_json).exists() else {}
    datasets = ([x for x in a.datasets.split(",") if x] if a.datasets
                else sorted(k for k in floors if not k.startswith("_")))
    tols = {}
    if a.tolerances_json and Path(a.tolerances_json).exists():
        t = json.loads(Path(a.tolerances_json).read_text())
        tols = t.get("tolerances", t)

    out = {"_tool": "floor_arm_precision_band", "_nrmse_def_hash": NRMSE_DEF_HASH,
           "_utc": datetime.datetime.now(datetime.timezone.utc)
                   .strftime("%Y-%m-%dT%H:%M:%SZ"),
           "_estimators": "E1/E2 verbatim from tools/floor_precision_seam.py; "
                          "affine_on_hf_train added (that tool's FROZEN_ARMS "
                          "excludes it)",
           "_report_only": "never writes state/; re-freezes nothing",
           "config": {"b_dither": a.b_dither, "seed": a.seed, "arms": arms},
           "datasets": {}}

    for ds in datasets:
        t0 = time.time()
        try:
            c_tr32, y_tr32, c_te32, y_te32 = load_view(Path(a.stripped_root), ds)
        except Exception as e:                                     # noqa: BLE001
            out["datasets"][ds] = {"status": f"LOAD_FAIL {type(e).__name__}"}
            continue
        f64 = lambda x: np.asarray(x, dtype=np.float64)            # noqa: E731
        base = arms_from(f64(c_tr32), f64(y_tr32), f64(c_te32), f64(y_te32), arms)

        e1, ndt = {}, None
        nx_tr, ny_tr = native_arrays(Path(a.data_root), ds, "train")
        nx_te, ny_te = native_arrays(Path(a.data_root), ds, "test")
        if nx_tr is not None and nx_te is not None:
            ndt = str(ny_tr.dtype)
            nv = arms_from(f64(nx_tr), f64(ny_tr), f64(nx_te), f64(ny_te), arms)
            e1 = {x: rel(base[x], nv[x]) for x in arms}

        rng = np.random.default_rng(a.seed)
        dev = {x: [] for x in arms}
        for _ in range(a.b_dither):
            v = arms_from(ulp_dither(c_tr32, rng), ulp_dither(y_tr32, rng),
                          ulp_dither(c_te32, rng), ulp_dither(y_te32, rng), arms)
            for x in arms:
                dev[x].append(rel(base[x], v[x]))
        e2 = {x: float(max(dev[x])) for x in arms}
        band = {x: max(e1.get(x, 0.0), e2[x]) for x in arms}

        A = np.hstack([f64(c_tr32), np.ones((len(c_tr32), 1))])
        sv = np.linalg.svd(A, compute_uv=False)
        rank = int((sv > sv.max() * max(A.shape) * np.finfo(float).eps).sum())
        tol = tols.get(ds)
        out["datasets"][ds] = {
            "status": "OK", "native_dtype": ndt, "stripped_dtype": str(y_tr32.dtype),
            "n_train": int(len(y_tr32)), "n_test": int(len(y_te32)),
            "cond_dim": int(c_tr32.shape[1]),
            "arm_values_float32_view": base,
            "E1_path_difference": e1, "E2_ulp_band_max": e2,
            "E2_ulp_band_median": {x: float(np.median(dev[x])) for x in arms},
            "per_arm_band": band,
            "widest_arm": max(band, key=band.get),
            "dataset_tolerance": tol,
            "arms_exceeding_dataset_tolerance": (
                sorted(x for x in arms if tol is not None and band[x] > float(tol))),
            "design_matrix": {
                "shape": [int(A.shape[0]), int(A.shape[1])], "rank": rank,
                "rank_deficient": bool(rank < A.shape[1]),
                "cond_number": (float(sv.max() / sv.min()) if sv.min() > 0 else None),
                "degenerate_cond_dims_std_exactly_zero": [
                    int(j) for j in np.where(f64(c_tr32).std(axis=0) == 0)[0]],
            },
            "seconds": time.time() - t0,
        }
        print(f"{ds:30s} " + "  ".join(
            f"{x}={band[x]:.4e}" for x in arms) +
            f"  rank={rank}/{A.shape[1]}"
            + (f"  exceeds_ds_tol={out['datasets'][ds]['arms_exceeding_dataset_tolerance']}"
               if tol is not None else ""))

    checks = {}
    for spec in a.check:
        key, rd = spec.split("=", 1)
        ds, arm = key.split(":", 1)
        b = (out["datasets"].get(ds, {}).get("per_arm_band", {}) or {}).get(arm)
        rd = float(rd)
        checks[f"{ds}:{arm}"] = {
            "recorded_rel_diff": rd, "arm_band": b,
            "dataset_tolerance": (out["datasets"].get(ds, {}) or {}).get("dataset_tolerance"),
            "verdict": (None if b is None else
                        ("INSIDE_ARM_BAND" if rd <= b else "OUTSIDE_ARM_BAND")),
            "factor_inside_arm_band": (b / rd if (b and rd) else None),
        }
        print(f"  check {ds}:{arm} rel_diff={rd:.4e} band={b} -> "
              f"{checks[f'{ds}:{arm}']['verdict']}")
    if checks:
        out["reproduction_checks"] = checks

    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(out, indent=2, sort_keys=True))
        print(f"\nwrote {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
