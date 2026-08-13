"""Build the campaign training-free floors file (G3-fix; spec D5 note 2).

The certified family HARD-REQUIRES `nn_condition`/`train_mean`/`zero` floor
entries per dataset (floor_arms.collect raises without them); round-3 state
covers only its own 10 datasets.  This builder computes all 30 with the
round-2 construction (vendored `floors_for` semantics, verbatim) through the
VENDORED panel_data/nrmse, and writes the file at the ONE path the frozen
family can see first: `roots[0]/FLOORS_REL`, where `roots[0]` resolves to
this campaign directory at the vendored family depth.

`affine_on_hf_train` needs no entry here — the family's own collect() marks
it not-applicable outside the certified ifc cells (frozen behavior).

Equivalence anchor: for the 10 datasets present in the certified round-3
floors file, the freshly computed nRMSEs must match it (tests).
"""
from __future__ import annotations

import datetime
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

CAMPAIGN = Path(__file__).resolve().parents[1]
# family/r3s2_route_b30/floor_arms.py: FLOORS_REL under roots[0] == CAMPAIGN dir
FLOORS_OUT = CAMPAIGN / "mffp_autoresearch/round3/state/anchors_repaired/floors.json"
CERTIFIED = Path("/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/round3/state/anchors_repaired/floors.json")


def _vendored(name: str, fname: str):
    spec = importlib.util.spec_from_file_location(name, CAMPAIGN / "eval" / fname)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_pd = _vendored("b30_floors_panel_data", "panel_data.py")
_nr = _vendored("b30_floors_nrmse", "nrmse.py")


def floors_for(ds: str, tr: dict = None, te: dict = None) -> dict:
    """Round-2 `make_floor_anchors.floors_for` construction, verbatim semantics."""
    tr = tr or _pd.load_split(ds, "train")
    te = te or _pd.load_split(ds, "test")
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
    nn_idx = d2.argmin(axis=1)  # numpy argmin tie -> lowest index (the definition)

    zero_v = _nr.nrmse(np.zeros_like(hf_te), hf_te)
    if abs(zero_v - 1.0) > 1e-12:
        raise SystemExit(f"{ds}: zero-floor nRMSE {zero_v!r} != 1.0 — metric seam broken")

    uniq, counts = np.unique(nn_idx, return_counts=True)
    top = np.argsort(counts)[::-1][:5]
    return {
        "n_train_hf": int(hf_tr.shape[0]),
        "n_test": int(hf_te.shape[0]),
        "cond_dim": int(c_tr.shape[1]),
        "nn_condition": {
            "nrmse": _nr.nrmse(hf_tr[nn_idx], hf_te),
            "definition": "L2 nearest in per-dim train-standardized condition space; "
                          "tie -> lowest train index",
            "nn_index_hist_top5": {str(int(uniq[i])): int(counts[i]) for i in top},
        },
        "train_mean": {"nrmse": _nr.nrmse(np.broadcast_to(hf_tr.mean(axis=0), hf_te.shape), hf_te)},
        "zero": {"nrmse": zero_v},
    }


def build_all(only: list = None) -> dict:
    cfg = _pd.load_config()
    datasets = only if only is not None else list(cfg["panel"])
    out = {
        "_nrmse_def_hash": _nr.NRMSE_DEF_HASH,
        "_copylf_def_hash": _pd.COPYLF_DEF_HASH,
        "_split": "test",
        "_certified_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "_notes": ("benchmark30 campaign floors, all 30 datasets, round-2 "
                   "floors_for construction via the vendored panel_data/nrmse; "
                   "placed at roots[0]/FLOORS_REL for the frozen family "
                   "(G3-fix, convergence log)"),
    }
    errors = {}
    for ds in datasets:
        try:
            out[ds] = floors_for(ds)
        except Exception as e:  # noqa: BLE001
            errors[ds] = f"{type(e).__name__}: {e}"
    if errors:
        out["_errors"] = errors
    return out


def main() -> None:
    out = build_all()
    FLOORS_OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(FLOORS_OUT, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    n = sum(1 for k in out if not k.startswith("_"))
    print(f"[G3-fix] campaign floors: {n} datasets -> {FLOORS_OUT}")
    for ds, msg in out.get("_errors", {}).items():
        print(f"  FLOOR-UNBUILDABLE (ledger candidate): {ds}: {msg[:120]}")


if __name__ == "__main__":
    main()
