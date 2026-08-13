"""Build the campaign copy-LF baseline registry (spec D3 seam (a), gate G2).

Computes the copy-LF reference nRMSE per dataset with the VENDORED
construction (`panel_data.copylf_prediction` + `nrmse.nrmse`), writing
`state/copylf_baselines.json` in the exact schema `score_panel.py` consumes
(`test_nrmse`, `reference_type`, top-level `_copylf_def_hash`).

The ifc datasets ship HF-only test splits, so no copy-LF is computable for
them — their certified `paper_bar` entries carry over VERBATIM from the
round-2 committed registry (same rule round 2 used, ADR r1-0002 lineage).

A dataset where the construction itself fails (e.g. era5's mismatched
per-rung sample counts) is recorded in the ERRORS block and CANNOT be scored
by the campaign scorer — it enters the exclusion ledger for both families.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

CAMPAIGN = Path(__file__).resolve().parents[1]
ROUND2_BASELINES = Path("/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/round2/eval/copylf_baselines.json")
PAPER_BAR = {"ifc_heat", "ifc_poisson"}


def _vendored(name: str, fname: str):
    spec = importlib.util.spec_from_file_location(name, CAMPAIGN / "eval" / fname)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_pd = _vendored("b30_copylf_panel_data", "panel_data.py")
_nr = _vendored("b30_copylf_nrmse", "nrmse.py")


def build_entry(ds_id: str, test: dict | None = None) -> dict:
    """copy-LF entry for one dataset; `test` injectable for fixtures."""
    if ds_id in PAPER_BAR:
        r2 = json.load(open(ROUND2_BASELINES))
        return dict(r2[ds_id])
    if test is None:
        test = _pd.load_split(ds_id, "test")
    pred = _pd.copylf_prediction(test, ds_id)
    y = test["field_by_fid"][test["hf_fid"]]
    conv = ("spectral_rung" if ds_id in _pd.SPECTRAL_RUNG_DATASETS
            else "periodic_node" if ds_id in _pd.PERIODIC_NODE_DATASETS
            else "dirichlet_node" if ds_id in _pd.DIRICHLET_NODE_DATASETS
            else "legacy_cell" if ds_id in _pd.LEGACY_CELL_DATASETS
            else None)
    if conv is None and test.get("field_by_fid") is not None:
        # 1-D datasets never consult the registry; record the path they take
        conv = "1d_path"
    return {
        "convention": conv,
        "reference_type": "copylf",
        "source": "computed by benchmark30 vendored construction (ADR b30-0001)",
        "test_nrmse": float(_nr.nrmse(pred, y)),
    }


def build_all(only: list | None = None) -> dict:
    cfg = _pd.load_config()
    datasets = only if only is not None else list(cfg["panel"])
    out = {
        "_copylf_def_hash": _pd.COPYLF_DEF_HASH,
        "_nrmse_def_hash": _nr.NRMSE_DEF_HASH,
        "_split": "test",
        "_notes": ("benchmark30 campaign registry; ifc entries are paper_bar "
                   "carried verbatim from round-2 (HF-only test splits)"),
    }
    errors = {}
    for ds in datasets:
        try:
            out[ds] = build_entry(ds)
        except Exception as e:  # noqa: BLE001 — surfaced, never swallowed
            errors[ds] = f"{type(e).__name__}: {e}"
    if errors:
        out["_errors"] = errors
    return out


def main() -> None:
    out = build_all()
    dest = CAMPAIGN / "state/copylf_baselines.json"
    dest.parent.mkdir(exist_ok=True)
    with open(dest, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    n_ok = sum(1 for k in out if not k.startswith("_"))
    errs = out.get("_errors", {})
    print(f"[G2] copy-LF baselines: {n_ok} datasets -> {dest}")
    for ds, msg in errs.items():
        print(f"[G2] UNSCORABLE (exclusion-ledger candidate): {ds}: {msg[:140]}")


if __name__ == "__main__":
    main()
