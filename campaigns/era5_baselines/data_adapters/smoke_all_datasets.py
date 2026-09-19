"""Verify load_mf_dataset + MFDataset work on all 17 factory_mffp datasets.

Reports layout, fids, cond_dim, per-fid shapes, and any errors.
Run: .venv/bin/python data_adapters/smoke_all_datasets.py
"""
from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from data_adapters import load_mf_dataset, MFDataset, detect_layout  # noqa: E402

PROJECT_DATA = HERE.parent / "data"

DATASETS_17 = [
    "ifc_heat", "ifc_poisson",
    "chin_chun_isothermal", "chin_chun_potential",
    "poisson_local", "heat_local",
    "fluid", "era5", "pm_test",
    "advection_diffusion_generated",
    "allen_cahn_generated",
    "burgers_generated", "burgers_param_generated",
    "darcy_generated", "heat_generated",
    "lid_driven_cavity_generated", "poisson_generated",
]


def summarize(ds_name: str) -> dict:
    ds_dir = PROJECT_DATA / ds_name
    if not ds_dir.exists():
        return {"dataset": ds_name, "status": "missing", "error": f"{ds_dir} not found"}
    out: dict = {"dataset": ds_name}
    try:
        out["layout"] = detect_layout(ds_dir)
    except Exception as e:
        return {"dataset": ds_name, "status": "detect_failed", "error": str(e)}

    for split in ("train", "test", "ood"):
        try:
            data = load_mf_dataset(ds_dir, split)
        except FileNotFoundError as e:
            out[f"{split}_status"] = "no_split"
            continue
        except Exception as e:
            out[f"{split}_status"] = "error"
            out[f"{split}_error"] = f"{type(e).__name__}: {e}"
            continue
        per_fid = {
            f: {
                "n_samples": int(data["cond_by_fid"][f].shape[0]),
                "cond_dim": int(data["cond_by_fid"][f].shape[1]),
                "n_cells": int(data["field_by_fid"][f].shape[1]),
                "grid_shape": data["grid_shape_by_fid"][f],
            }
            for f in data["fids"]
        }
        out[f"{split}_fids"] = data["fids"]
        out[f"{split}_hf_fid"] = data["hf_fid"]
        out[f"{split}_n_hf"] = data["n_samples"]
        out[f"{split}_cond_dim"] = data["cond_dim"]
        out[f"{split}_per_fid"] = per_fid

        # also verify MFDataset works end-to-end
        try:
            mfds = MFDataset(ds_dir, split)
            sample = mfds[0]
            out[f"{split}_mfdataset_sample0_shapes"] = {
                "cond": sample["cond"].shape,
                "lf_fields": [a.shape for a in sample["lf_fields"]],
                "hf_field": sample["hf_field"].shape,
            }
            out[f"{split}_mfdataset_len"] = len(mfds)
        except Exception as e:
            out[f"{split}_mfdataset_error"] = f"{type(e).__name__}: {e}"

    out["status"] = "ok"
    return out


def main():
    results = []
    print(f"{'dataset':32s} {'layout':9s} {'fids':>4s} {'hf':>4s} {'cond':>5s} {'n_hf':>6s} status")
    print("-" * 90)
    for ds in DATASETS_17:
        r = summarize(ds)
        results.append(r)
        if r["status"] != "ok":
            print(f"{ds:32s} {'?':9s} {'-':>4s} {'-':>4s} {'-':>5s} {'-':>6s} {r['status']}: {r.get('error','')[:60]}")
            continue
        train_status = "ok" if "train_per_fid" in r else r.get("train_status","?")
        test_status = "ok" if "test_per_fid" in r else r.get("test_status","?")
        ood_status = "ok" if "ood_per_fid" in r else r.get("ood_status","?")
        print(
            f"{ds:32s} {r['layout']:9s} "
            f"{len(r.get('train_fids',[])):>4d} "
            f"{r.get('train_hf_fid',0):>4d} "
            f"{r.get('train_cond_dim',0):>5d} "
            f"{r.get('train_n_hf',0):>6d}  "
            f"train={train_status}  test={test_status}  ood={ood_status}"
        )

    # also dump full JSON for review
    out_path = HERE / "smoke_report.json"
    out_path.write_text(json.dumps(results, indent=2, default=str))
    print(f"\nfull report -> {out_path}")

    # summarize
    n_ok = sum(1 for r in results if r["status"] == "ok"
               and "train_per_fid" in r and "test_per_fid" in r)
    print(f"\nfully-loadable datasets (train+test): {n_ok}/{len(results)}")


if __name__ == "__main__":
    main()
