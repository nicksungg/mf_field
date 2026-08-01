#!/usr/bin/env python
"""Acceptance verification for the ladder.py registration fix (proposal package).

Checks, per the fix-proposal spec:
  (a) HF and raw native-grid LF arrays are bit-identical between the OLD
      (defective) and NEW (patched) sample-round outputs — the fix touches
      only the derived aligned arrays, never the solves.
  (b) The NEW aligned arrays match the round-2 eval layer's independent
      reconstruction-from-raw (panel_data.py, ADR r2-0001) to near machine
      precision, including the exact-nesting invariant
      aligned[::r, ::r] == raw; the OLD aligned arrays fail exact nesting.
      Also cross-checks the patched interpolator against the eval layer on the
      REAL sharp__allen_cahn_2d dataset (stored raw LF fields).
  (c) The half-coarse-cell registration shift is visible in the OLD aligned
      arrays and gone in the NEW ones: an index-ramp probe of the two
      coordinate maps, plus a fractional-shift scan on the stored arrays.
  (d) The self-reported LF-vs-HF fidelity-gap metrics before/after
      (sample_summary.json from both runs).

Run AFTER generating the sample round twice (old code and patched code) into
sample_round/old and sample_round/new.  `--patched-src` may point at a
checkout with ladder_fix.patch applied to additionally exercise the patched
`mffp_sharp.common.ladder` directly; without it, the eval layer alone is the
independent reference (the stored NEW arrays are still fully verified).

Writes verification_results.json next to this script and exits non-zero if a
hard check fails.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent  # .../mf_field monorepo root

HARD_FAILURES: list[str] = []


def hard(ok: bool, msg: str) -> str:
    if not ok:
        HARD_FAILURES.append(msg)
    return "PASS" if ok else "FAIL"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read_h5(path: Path) -> dict:
    import h5py

    out = {"raw": {}, "aligned": {}}
    with h5py.File(path, "r") as f:
        out["hf_res"] = int(f.attrs["hf_res"])
        out["convention"] = f.attrs.get("alignment_convention", "(absent)")
        for key in f["fields"]:
            res = int(key.split("_")[1])
            out["raw"][res] = f["fields"][key][...]
            out["aligned"][res] = f["fields_hf"][key][...]
    return out


def fractional_shift_scan(a: np.ndarray, b: np.ndarray, max_shift: float = 3.0,
                          step: float = 0.05) -> float:
    """Diagonal fractional shift delta (in HF cells, periodic, order-1) that
    best maps b onto a; the registration offset between two aligned arrays."""
    from scipy.ndimage import shift as ndshift

    best, best_err = 0.0, np.inf
    for d in np.arange(0.0, max_shift + 1e-9, step):
        err = float(np.mean((a - ndshift(b, (d, d), order=1, mode="grid-wrap")) ** 2))
        if err < best_err:
            best, best_err = float(d), err
    return best


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample-old", default=str(HERE / "sample_round" / "old"))
    ap.add_argument("--sample-new", default=str(HERE / "sample_round" / "new"))
    ap.add_argument("--allen-cahn-dir",
                    default=str(REPO / "mf_field" / "factory_mffp" / "data" / "sharp__allen_cahn_2d"))
    ap.add_argument("--eval-dir", default=str(REPO / "mffp_autoresearch" / "round2" / "eval"))
    ap.add_argument("--patched-src", default=None,
                    help="optional: path to a patched mffp_sharp/src to test ladder directly")
    args = ap.parse_args()

    panel = load_module(Path(args.eval_dir) / "panel_data.py", "panel_data_ref")
    results: dict = {"checks": {}}
    conv_fn = {"node_periodic": panel._node_aligned_periodic_up,
               "node_dirichlet": panel._dirichlet_node_up}

    ladder = None
    if args.patched_src:
        sys.path.insert(0, args.patched_src)
        import mffp_sharp.common.ladder as ladder  # noqa

    datasets = sorted(p.name for p in Path(args.sample_old).glob("*_sample.h5"))
    print(f"datasets in sample round: {datasets}\n")

    # ── (a) raw solves untouched; (b) new aligned == eval-layer reconstruction ──
    for name in datasets:
        old = read_h5(Path(args.sample_old) / name)
        new = read_h5(Path(args.sample_new) / name)
        hf = new["hf_res"]
        r: dict = {"convention": str(new["convention"])}

        raw_same = all(np.array_equal(old["raw"][res], new["raw"][res])
                       for res in old["raw"])
        hf_same = np.array_equal(old["aligned"][hf], new["aligned"][hf])
        r["a_raw_bit_identical"] = hard(raw_same, f"{name}: raw arrays differ")
        r["a_hf_aligned_bit_identical"] = hard(hf_same, f"{name}: HF aligned differs")

        up_fn = conv_fn[str(new["convention"])]
        recon_max, nest_new_max, nest_old_max = 0.0, 0.0, 0.0
        for res in sorted(new["raw"]):
            if res == hf:
                continue
            for i in range(new["raw"][res].shape[0]):
                recon = up_fn(new["raw"][res][i].astype(np.float64), (hf, hf))
                recon_max = max(recon_max, float(np.max(np.abs(
                    recon.astype(np.float32) - new["aligned"][res][i]))))
            if str(new["convention"]) == "node_periodic":
                k = hf // res
                nest_new_max = max(nest_new_max, float(np.max(np.abs(
                    new["aligned"][res][:, ::k, ::k] - new["raw"][res]))))
                nest_old_max = max(nest_old_max, float(np.max(np.abs(
                    old["aligned"][res][:, ::k, ::k] - old["raw"][res]))))
        r["b_new_vs_eval_recon_maxabs"] = recon_max
        r["b_recon"] = hard(recon_max <= 1e-6,
                            f"{name}: new aligned vs eval-layer recon {recon_max}")
        if str(new["convention"]) == "node_periodic":
            r["b_exact_nesting_new_maxabs"] = nest_new_max
            r["b_exact_nesting_old_maxabs"] = nest_old_max
            r["b_nesting"] = hard(nest_new_max == 0.0,
                                  f"{name}: new aligned not exactly nested")
            r["b_old_fails_nesting"] = hard(nest_old_max > 1e-3,
                                            f"{name}: old aligned unexpectedly nested?")

        # ── (c) the shift, measured on the stored arrays ──
        r["c_shift_old_vs_new_hf_cells"] = {}
        for res in sorted(new["raw"]):
            if res == hf:
                continue
            a = old["aligned"][res].mean(axis=0).astype(np.float64)
            b = new["aligned"][res].mean(axis=0).astype(np.float64)
            r["c_shift_old_vs_new_hf_cells"][str(res)] = fractional_shift_scan(a, b)
        results["checks"][name] = r
        print(f"{name}: {json.dumps(r, indent=2)}\n")

    # ── (b, real data) patched interpolator vs eval layer on sharp__allen_cahn_2d ──
    ac = Path(args.allen_cahn_dir)
    if ac.exists():
        zl, zh = np.load(ac / "train_l2.npz"), np.load(ac / "train_l3.npz")
        n = min(8, zl["y"].shape[0])
        h = int(round(zl["y"].shape[1] ** 0.5)); H = int(round(zh["y"].shape[1] ** 0.5))
        lf = zl["y"][:n].reshape(n, h, h).astype(np.float64)
        rr: dict = {"lf_grid": h, "hf_grid": H}
        nest = 0.0; agree = 0.0
        for i in range(n):
            ev = panel._node_aligned_periodic_up(lf[i], (H, H))
            k = H // h
            nest = max(nest, float(np.max(np.abs(ev[::k, ::k] - lf[i]))))
            if ladder is not None:
                la = ladder.upsample_to_hf(lf[i], H, convention="node_periodic")
                agree = max(agree, float(np.max(np.abs(la - ev))))
        rr["eval_layer_exact_nesting_maxabs"] = nest
        rr["b_real_nesting"] = hard(nest == 0.0, "real allen_cahn: eval nesting broken")
        if ladder is not None:
            rr["patched_ladder_vs_eval_layer_maxabs"] = agree
            rr["b_real_agreement"] = hard(agree <= 1e-9,
                                          f"real allen_cahn: ladder vs eval {agree}")
        results["checks"]["real_sharp__allen_cahn_2d"] = rr
        print(f"real sharp__allen_cahn_2d: {json.dumps(rr, indent=2)}\n")
    else:
        results["checks"]["real_sharp__allen_cahn_2d"] = "SKIPPED (dir not found)"

    # ── (c) index-ramp probe of the two coordinate maps ──
    from scipy.ndimage import map_coordinates, zoom

    probe = {}
    for rfac in (2, 4):
        h = 32; H = h * rfac
        ramp = np.arange(h, dtype=np.float64)
        node = map_coordinates(ramp, [np.arange(H) * (h / H)], order=1, mode="grid-wrap")
        cell = zoom(ramp, rfac, order=1, grid_mode=True, mode="nearest")
        k = np.arange(H, dtype=np.float64)
        interior = slice(rfac, H - rfac)  # away from boundary/seam handling
        off_node = float(np.mean(node[interior] * rfac - k[interior]))
        off_cell = float(np.mean(cell[interior] * rfac - k[interior]))
        # zoom(grid_mode=True) reads output pixel k from input coord
        # (k+0.5)/r - 0.5, i.e. displaced by -(r-1)/2 HF cells on node data.
        probe[f"r={rfac}"] = {
            "old_cell_map_offset_hf_cells": round(off_cell, 6),
            "new_node_map_offset_hf_cells": round(off_node, 6),
            "expected_old_offset": -(rfac - 1) / 2.0,
        }
        hard(abs(off_node) < 1e-9, f"ramp probe r={rfac}: node map offset {off_node}")
        hard(abs(off_cell + (rfac - 1) / 2.0) < 1e-9,
             f"ramp probe r={rfac}: cell map offset {off_cell}")
    results["checks"]["c_index_ramp_probe"] = probe
    print(f"index-ramp probe: {json.dumps(probe, indent=2)}\n")

    # ── (d) self-reported fidelity-gap metrics before/after ──
    gap = {}
    for tag, d in (("old", args.sample_old), ("new", args.sample_new)):
        p = Path(d) / "sample_summary.json"
        if p.exists():
            for s in json.loads(p.read_text()):
                gap.setdefault(s["pde"], {})[tag] = s["lf_vs_hf"]
    results["checks"]["d_fidelity_gap_metrics"] = gap
    print(f"fidelity-gap self-metrics (old vs new): {json.dumps(gap, indent=2)}\n")

    results["hard_failures"] = HARD_FAILURES
    results["verdict"] = "PASS" if not HARD_FAILURES else "FAIL"
    (HERE / "verification_results.json").write_text(json.dumps(results, indent=2))
    print(f"VERDICT: {results['verdict']}"
          + (f" — {HARD_FAILURES}" if HARD_FAILURES else ""))
    return 0 if not HARD_FAILURES else 1


if __name__ == "__main__":
    sys.exit(main())
