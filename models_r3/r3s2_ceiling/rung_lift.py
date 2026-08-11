"""`R3S2B3_RUNG_LIFT_TRIPWIRE = 1` -- the family's LF rung AND its lift must be
the SCORED CELL's, per dataset.

WHY THIS EXISTS
---------------
ADR r3-0005 (ratified 2026-08-10) re-pointed `sharp__phase_field_crystal_2d`'s
scored cell from the max LF rung to rung **1** with an **exact spectral (FFT
zero-pad) lift**; the rung override and the lift are INSEPARABLE per the ADR.
Earlier batches in this stream ran the emulator at `R3S2_EMU_RUNG = max` with
the node-aligned bilinear lift, which on pfc is a DIFFERENT CELL from the one
the panel scores. The card therefore fixes

    R3S2_EMU_RUNG = scored_cell_lf_from_panel_data

and mandates a tripwire that asserts the family's choice equals
`round2/eval/panel_data.py`'s -- on the rung INDEX and on the lift BYTES.

IMPORT vs VENDOR
----------------
`panel_data.py` is one of `score_panel.py::_HASHED_EVAL_FILES`, so its bytes are
already inside the family's cache key: importing it READ-ONLY for the tripwire
cannot poison a cached score (the hazard that motivated vendoring in the first
place). The COMPUTE path still uses the family's own vendored `upsample.py`, so
the tripwire is a genuine two-implementation cross-check rather than a tautology.
The eval layer is never written to and never edited (program.md §5).
"""
from __future__ import annotations

import numpy as np

import upsample as uplib


class RungLiftError(RuntimeError):
    """The family's scored-cell choice disagrees with the eval layer's."""


def _panel_data():
    import panel_data                       # noqa: PLC0415  (read-only import)
    return panel_data


def scored_rung(dataset_name: str, lf_fids) -> dict:
    """The rung `panel_data.copylf_prediction` would score this cell from."""
    pd = _panel_data()
    fids = sorted(int(f) for f in lf_fids)
    if not fids:
        raise RungLiftError(f"{dataset_name}: no LF fidelity on the train split")
    override = pd.SPECTRAL_RUNG_DATASETS.get(dataset_name)
    if override is not None:
        if int(override) not in fids:
            raise RungLiftError(
                f"{dataset_name}: ADR r3-0005 designates rung {override}, but the "
                f"train ladder carries {fids}")
        return {"lf_rung": int(override), "source": "panel_data.SPECTRAL_RUNG_DATASETS",
                "adr": "r3-0005 (pfc spectral rung; rung override + spectral lift "
                       "are inseparable)", "lf_fids": fids}
    return {"lf_rung": int(max(fids)), "source": "panel_data: max(lf_fids)",
            "adr": None, "lf_fids": fids}


def lift(dataset_name: str, lf_flat: np.ndarray, lf_grid, hf_grid) -> np.ndarray:
    """The family's own lift, keyed exactly as the scored cell's is."""
    return uplib.upsample_fields(lf_flat, lf_grid, hf_grid, dataset_name)


def convention_name(dataset_name: str, lf_grid, hf_grid) -> str:
    if tuple(int(v) for v in lf_grid) == tuple(int(v) for v in hf_grid):
        return "identity_same_grid"
    if int(lf_grid[0]) == 1 and int(hf_grid[0]) == 1:
        return "legacy_cell_centred_1d"
    return uplib.resolve_convention(dataset_name)[1]


def tripwire(dataset_name: str, family_rung: int, lf_flat: np.ndarray,
             lf_grid, hf_grid, lf_fids, n_probe: int = 4) -> dict:
    """Assert (a) rung equality and (b) BIT-EXACT lift equality against
    `panel_data.py`'s own `up_fn` on real rows of this dataset."""
    pd = _panel_data()
    want = scored_rung(dataset_name, lf_fids)
    if int(family_rung) != int(want["lf_rung"]):
        raise RungLiftError(
            f"RUNG/LIFT TRIPWIRE on {dataset_name}: the family emulates rung "
            f"{family_rung} but panel_data.py scores the cell from rung "
            f"{want['lf_rung']} ({want['source']}). These are DIFFERENT CELLS; the "
            "card's R3S2_EMU_RUNG=scored_cell_lf_from_panel_data forbids the "
            "mismatch (ADR r3-0005).")

    lg = (int(lf_grid[0]), int(lf_grid[1]))
    hg = (int(hf_grid[0]), int(hf_grid[1]))
    rec = {"lf_rung": int(family_rung), "rung_source": want["source"],
           "adr": want["adr"], "lf_grid": list(lg), "hf_grid": list(hg),
           "family_convention": convention_name(dataset_name, lg, hg),
           "n_probe_rows": 0, "max_abs_lift_deviation": 0.0}

    if lg == hg or (lg[0] == 1 and hg[0] == 1):
        rec["eval_layer_up_fn"] = "n/a (identity or 1-D legacy path)"
        rec["pass"] = True
        return rec

    if dataset_name in pd.SPECTRAL_RUNG_DATASETS:
        up_fn = pd._spectral_zeropad_up
    elif dataset_name in pd.PERIODIC_NODE_DATASETS:
        up_fn = pd._node_aligned_periodic_up
    elif dataset_name in pd.DIRICHLET_NODE_DATASETS:
        up_fn = pd._dirichlet_node_up
    elif dataset_name in pd.LEGACY_CELL_DATASETS:
        up_fn = pd._legacy_cell_centred_up
    else:
        raise RungLiftError(
            f"{dataset_name!r} has no reference convention in panel_data.py "
            "(ADR r2-0001): classify it in the eval layer before scoring it")
    rec["eval_layer_up_fn"] = up_fn.__name__

    lf = np.asarray(lf_flat, dtype=np.float64)
    n = min(int(n_probe), int(lf.shape[0]))
    mine = lift(dataset_name, lf[:n], lg, hg)
    theirs = np.empty_like(mine)
    for i in range(n):
        theirs[i] = up_fn(lf[i].reshape(lg), hg).ravel()
    dev = float(np.abs(mine - theirs).max()) if n else 0.0
    rec["n_probe_rows"] = int(n)
    rec["max_abs_lift_deviation"] = dev
    if dev != 0.0:
        raise RungLiftError(
            f"RUNG/LIFT TRIPWIRE on {dataset_name}: the family's lift "
            f"({rec['family_convention']}) deviates from panel_data.py's "
            f"{up_fn.__name__} by {dev!r} on {n} real rows. The copy-LF denominator "
            "and this family's base field would be built by different operators.")
    rec["pass"] = True
    return rec
