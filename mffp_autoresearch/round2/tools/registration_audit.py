"""registration_audit.py -- is a dataset's copy-LF reference MISREGISTERED, and what
does the free fix buy?

Promoted from `worktrees/s3_warp/B1/scratchpad/reanalysis_turn_1.py` (+ the LSI
projection from `reanalysis_turn_3.py`); provenance card
`experiment_cards/s3_warp/batch_1/B1.json` part 6, findings F1-F8, F14, F16.

WHY THIS EXISTS
---------------
`eval/panel_data.py::copylf_prediction` builds the round's skill DENOMINATOR by
`scipy.ndimage.zoom(..., order=1, grid_mode=True, mode="nearest")`, i.e. it treats
the LF field as CELL-CENTRED (finite-volume) samples. A pseudo-spectral solver's
state is a POINT sample on the node grid `x_j = j*L/n`; on a dyadic ladder LF node
`j` then coincides physically with HF node `r*j`. Reading one convention as the
other misregisters copy-LF by

        offset = (r - 1) / 2   HF cells        (0.5 at r=2, 1.5 at r=4)

which on the round-1 sharp panel is 50-100 % of copy-LF's whole error. Any skill
number, warp ceiling, LSI transfer function or "beats copy-LF" claim measured
against a misregistered reference is partly measuring the convention.

WHAT IT MEASURES (per dataset, all through `eval/nrmse.py`)
----------------------------------------------------------
| block | question |
|---|---|
| `convention.decimation` | is the raw LF closer to `HF[::r,::r]` (NODE) or to the r x r block mean of HF (CELL-CENTRE)? the data's own answer |
| `convention.ramp_probe` | EXACT coordinate map of the real `copylf_prediction`, obtained by pushing a linear index ramp through it (bilinear interpolation of a linear function is exact, so the output IS the sampled coordinate). Contains no physics |
| `variants[*].LK_global_shift_median_cells` | closed-form global Lucas-Kanade displacement of each predictor vs HF, per sample -- no optimiser, no fitting |
| `variants[*].nrmse / skill / pct_removed` | the FREE WIN: `A` eval copy-LF (seam: must equal `eval/copylf_baselines.json`), `A2` same convention with `grid-wrap` (isolates the wrap seam), `B` A + a fixed `(r-1)/2`-cell shift, `C` node-aligned bilinear from the raw LF, `D` node-aligned band-limited (FFT zero-pad), `E` Dirichlet interior-node alignment for non-nested grids |
| `hf_energy_above_lf_band` | does the HF field carry ANY information the LF grid cannot represent? |
| `lsi_ramp_projection` (`--lsi`) | LF-energy-weighted fraction of a fitted LSI transfer function `T(k)` (s6-B1's, imported from `defect_correction_learnability.py`) that the analytic half-cell phase ramp explains, and its best scalar amplitude |
| `verdict` | `MISREGISTERED_NODE_DATA` / `CONSISTENT` / `NON_NESTED_STRETCH` / `INCONCLUSIVE` |

HOW TO READ IT
--------------
* `verdict == MISREGISTERED_NODE_DATA` with `LK ~ +(r-1)/2` on variant A -> the
  dataset's copy-LF reference is inflated. Report every skill on that dataset
  against variant C or D as well, and give any model that "beats copy-LF" the
  fixed-shift arm as its control.
* `decimation.node << decimation.cell` -> node-sampled data (the round-1 sharp
  panel: 2.2x-7.7x, and 1.5e5x on pfc).
* `decimation.node ~ 0` (<= 1e-6) -> **the ladder is DEGENERATE at this level
  pair**: the coarse solve equals the fine solve and the dataset carries no
  fidelity gap (pfc). That is a dataset bug report, not a modelling target.
* `hf_energy_above_lf_band ~ 0` -> the gap is never "missing fine structure"; do
  not attribute it to bandwidth/capacity.
* `lsi_ramp_projection.frac_explained > 0.8` with `best_scalar_c ~ 1` -> whatever
  a learned linear/convolutional corrector is winning on this dataset, it is
  mostly undoing the resample.
* `NON_NESTED_STRETCH` (helmholtz: `24 -> 96` on a Dirichlet interior-node grid)
  -> the defect is a zero-mean space-varying stretch, invisible to any DC or
  mean-shift statistic; only variant `E` addresses it.

CONSTRAINTS
-----------
Read-only w.r.t. `eval/`, `models/`, `data/`. Nothing here may become a card score:
the frozen `eval/copylf_baselines.json` remains the round's reference (the eval
layer is byte-immutable during a round). The corrected variants are for
INTERPRETATION and for control arms, and the tool refuses to run if variant A does
not reproduce the frozen baseline.

INVOKE
------
    source "$PROJECT_ROOT/.venv/bin/activate"
    python tools/registration_audit.py --datasets PANEL --out reg.json [--lsi]
    python tools/registration_audit.py --datasets sharp__allen_cahn_2d,ext__helmholtz_2d \\
        --out reg.json --lsi [--n_test 100] [--n_train 400] [--seam_tol 1e-9]

Pure numpy/scipy on the login node; ~10-40 s per 256^2 dataset (+ ~30 s with
`--lsi`). Datasets whose test split ships no LF (`ifc_poisson`) return an `error`.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import yaml
from scipy.ndimage import map_coordinates, zoom


def _round_root() -> Path:
    out = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                         text=True, check=True, cwd=Path(__file__).resolve().parent)
    return Path(out.stdout.strip()) / "mffp_autoresearch" / "round1"


ROUND = _round_root()
sys.path.insert(0, str(ROUND / "eval"))
sys.path.insert(0, str(ROUND / "tools"))
from nrmse import nrmse, NRMSE_DEF_HASH  # noqa: E402
from panel_data import copylf_prediction, load_split  # noqa: E402

BASELINES = json.loads((ROUND / "eval" / "copylf_baselines.json").read_text())


# ---------------------------------------------------------------- primitives
def ramp_probe(lf_grid, hf_grid):
    """EXACT coordinate map of copylf_prediction: feed it a linear index ramp."""
    h, w = lf_grid
    H, W = hf_grid
    j = np.repeat(np.arange(h, dtype=np.float64)[:, None], w, axis=1)
    i = np.repeat(np.arange(w, dtype=np.float64)[None, :], h, axis=0)
    data = {"hf_fid": 9, "lf_fids": [1],
            "field_by_fid": {1: np.stack([j.ravel(), i.ravel()]), 9: np.zeros((2, H * W))},
            "grid_shape_by_fid": {1: (h, w), 9: (H, W)}}
    up = copylf_prediction(data).reshape(2, H, W)
    r = H / h
    k = np.arange(H, dtype=np.float64)
    sampled = up[0][:, W // 2]
    pred = (k + 0.5) / r - 0.5
    cut = int(np.ceil(r / 2))
    interior = slice(cut, H - cut)
    off_node = r * sampled[interior] - k[interior]
    return {"ratio": r,
            "max_abs_dev_from_scipy_gridmode_formula_interior":
                float(np.abs(sampled[interior] - pred[interior]).max()),
            "offset_HF_cells_if_data_is_NODE_aligned": {
                "interior_mean": float(off_node.mean()),
                "interior_min": float(off_node.min()),
                "interior_max": float(off_node.max())},
            "offset_HF_cells_if_data_is_CELL_centred_interior_mean": float(
                np.mean((r * (sampled[interior] + 0.5) - 0.5) - k[interior])),
            "isotropy_axis0_vs_axis1_max_abs_dev": float(
                np.abs(sampled - up[1][H // 2, :]).max()),
            "n_clamped_rows": int((sampled <= 0).sum() + (sampled >= h - 1).sum())}


def decimation(lf2d, hf2d, r):
    n, H = lf2d.shape[0], hf2d.shape[1]
    node = hf2d[:, ::r, ::r].reshape(n, -1)
    cell = hf2d.reshape(n, H // r, r, H // r, r).mean(axis=(2, 4)).reshape(n, -1)
    lf = lf2d.reshape(n, -1)
    return {"nrmse_lf_vs_HF_node_decimation": nrmse(lf, node),
            "nrmse_lf_vs_HF_cellmean": nrmse(lf, cell)}


def lk_global_shift(pred2d, hf2d, periodic=True):
    """Closed-form global displacement (HF cells) of pred features vs hf:
    pred(x) ~ hf(x - delta) => pred - hf ~ -delta . grad hf. (N,2), axis-0/axis-1."""
    if periodic:
        g0 = 0.5 * (np.roll(hf2d, -1, axis=1) - np.roll(hf2d, 1, axis=1))
        g1 = 0.5 * (np.roll(hf2d, -1, axis=2) - np.roll(hf2d, 1, axis=2))
        d = pred2d - hf2d
    else:
        g0, g1 = np.gradient(hf2d, axis=1), np.gradient(hf2d, axis=2)
        sl = (slice(None), slice(2, -2), slice(2, -2))
        g0, g1, d = g0[sl], g1[sl], (pred2d - hf2d)[sl]
    out = np.empty((hf2d.shape[0], 2))
    for i in range(hf2d.shape[0]):
        G = np.stack([g0[i].ravel(), g1[i].ravel()], axis=1)
        out[i], *_ = np.linalg.lstsq(G, -d[i].ravel(), rcond=None)
    return out


def band_limited_up(lf2d, hf_grid):
    n, h, _ = lf2d.shape
    H, W = hf_grid
    out = np.empty((n, H * W))
    pad = (H - h) // 2
    for i in range(n):
        Fc = np.fft.fftshift(np.fft.fft2(lf2d[i]))
        Fp = np.zeros((H, W), dtype=complex)
        Fp[pad:pad + h, pad:pad + h] = Fc
        out[i] = np.real(np.fft.ifft2(np.fft.ifftshift(Fp)) * (H / h) ** 2).ravel()
    return out


def build_variants(lf2d, hf_grid, eval_copylf, periodic):
    n, hlf, wlf = lf2d.shape
    H, W = hf_grid
    r = H / hlf
    k = np.arange(H, dtype=np.float64)
    l = np.arange(W, dtype=np.float64)
    mode = "grid-wrap" if periodic else "nearest"
    v = {"A_eval_copylf": eval_copylf}

    a2 = np.empty((n, H * W))
    for i in range(n):
        a2[i] = zoom(lf2d[i], (H / hlf, W / wlf), order=1, grid_mode=True, mode=mode).ravel()
    v["A2_same_convention_periodic_wrap"] = a2

    s = (r - 1.0) / 2.0
    cc = np.meshgrid(k + s, l + s, indexing="ij")
    b = np.empty((n, H * W))
    ec = eval_copylf.reshape(n, H, W)
    for i in range(n):
        b[i] = map_coordinates(ec[i], cc, order=1, mode=mode).ravel()
    v[f"B_evalcopylf_plus_const_shift_{s:g}cells"] = b

    if periodic:
        cn = np.meshgrid(k / r, l / r, indexing="ij")
        c = np.empty((n, H * W))
        for i in range(n):
            c[i] = map_coordinates(lf2d[i], cn, order=1, mode="grid-wrap").ravel()
        v["C_node_aligned_bilinear"] = c
        if (H - hlf) % 2 == 0:
            v["D_node_aligned_bandlimited"] = band_limited_up(lf2d, hf_grid)
    else:
        hLF, hHF = 1.0 / (hlf + 1), 1.0 / (H + 1)
        jj = ((k + 1.0) * hHF) / hLF - 1.0
        ce = np.meshgrid(jj, ((l + 1.0) * hHF) / hLF - 1.0, indexing="ij")
        e = np.empty((n, H * W))
        for i in range(n):
            e[i] = map_coordinates(lf2d[i], ce, order=1, mode="nearest").ravel()
        v["E_dirichlet_node_aligned_bilinear"] = e
    return v


def lsi_projection(ds, n_train, hf_grid, offset_cells):
    """Weighted projection of s6-B1's fitted LSI transfer function on the analytic
    half-cell phase ramp (imports the promoted tool's own fit)."""
    from defect_correction_learnability import fit_transfer
    tr = load_split(ds, "train")
    hf = np.asarray(tr["field_by_fid"][tr["hf_fid"]], dtype=np.float64)[:n_train]
    lf = copylf_prediction(tr)[:n_train]
    H, W = hf_grid
    T = fit_transfer(lf, hf - lf, (H, W), ridge=0.0)
    kx = np.fft.fftfreq(H)[:, None]
    ky = np.fft.rfftfreq(W)[None, :]
    Tref = np.exp(2j * np.pi * (kx * offset_cells + ky * offset_cells)) - 1.0
    wgt = (np.abs(np.fft.rfft2(lf.reshape(-1, H, W))) ** 2).sum(axis=0)
    num = float(np.real(np.sum(wgt * T * np.conj(Tref))))
    dref = float(np.sum(wgt * np.abs(Tref) ** 2))
    dT = float(np.sum(wgt * np.abs(T) ** 2))
    c = num / max(dref, 1e-300)
    resid = float(np.sum(wgt * np.abs(T - c * Tref) ** 2))
    return {"n_train_used": int(lf.shape[0]),
            "cosine_weighted": num / max(np.sqrt(dref * dT), 1e-300),
            "best_scalar_c": c,
            "frac_explained": 1.0 - resid / max(dT, 1e-300),
            "assumed_offset_cells": offset_cells}


# ---------------------------------------------------------------- per dataset
def one(ds, n_test, n_train, seam_tol, do_lsi):
    d = load_split(ds, "test")
    if not d["lf_fids"]:
        return {"error": "test split ships no LF fidelity (copy-LF undefined)"}
    hf_fid, lf_fid = d["hf_fid"], max(d["lf_fids"])
    hg = d["grid_shape_by_fid"].get(hf_fid)
    lg = d["grid_shape_by_fid"].get(lf_fid)
    if hg is None or lg is None:
        return {"error": "non-square / 1-D layout: this audit is 2-D only"}
    hg, lg = tuple(hg), tuple(lg)
    hf = np.asarray(d["field_by_fid"][hf_fid], dtype=np.float64)[:n_test]
    lf = np.asarray(d["field_by_fid"][lf_fid], dtype=np.float64)[:hf.shape[0]]
    n = hf.shape[0]
    hf2d, lf2d = hf.reshape(n, *hg), lf.reshape(n, *lg)
    eval_copylf = copylf_prediction(d)[:n]
    r = hg[0] / lg[0]
    nested = hg[0] % lg[0] == 0
    periodic = ds != "ext__helmholtz_2d" and nested
    base = BASELINES.get(ds, {}).get("test_nrmse")

    e = {"grid_hf": list(hg), "grid_lf": list(lg), "ratio": r, "n_test": n,
         "nested_integer_ratio": bool(nested),
         "copylf_baseline_frozen": base,
         "convention": {"ramp_probe": ramp_probe(lg, hg)}}
    # is the misregistration CONSTANT or SPACE-VARYING? LK on each half-domain.
    half = hg[0] // 2
    sh_lo = lk_global_shift(eval_copylf.reshape(n, *hg)[:, :half], hf2d[:, :half], periodic=False)
    sh_hi = lk_global_shift(eval_copylf.reshape(n, *hg)[:, half:], hf2d[:, half:], periodic=False)
    e["convention"]["halfdomain_shift_axis0_cells"] = {
        "first_half_median": float(np.median(sh_lo[:, 0])),
        "second_half_median": float(np.median(sh_hi[:, 0])),
        "difference": float(np.median(sh_hi[:, 0]) - np.median(sh_lo[:, 0]))}
    if nested:
        e["convention"]["decimation"] = decimation(lf2d, hf2d, int(hg[0] // lg[0]))

    F = np.fft.fft2(hf2d[:min(n, 20)])
    fr = np.fft.fftfreq(hg[0]) * hg[0]
    inb = (np.abs(fr) <= lg[0] / 2)[:, None] & (np.abs(fr) <= lg[1] / 2)[None, :]
    tot = (np.abs(F) ** 2).sum(axis=(1, 2))
    e["hf_energy_above_lf_band"] = float((((np.abs(F) ** 2) * ~inb).sum(axis=(1, 2)) / tot).mean())

    e["variants"] = {}
    for name, p in build_variants(lf2d, hg, eval_copylf, periodic).items():
        val = nrmse(p, hf)
        sh = lk_global_shift(p.reshape(n, *hg), hf2d, periodic=periodic)
        e["variants"][name] = {
            "nrmse": val,
            "skill_vs_frozen_copylf": (val / base) if base else None,
            "pct_of_copylf_error_removed": (100.0 * (1 - val / base)) if base else None,
            "LK_global_shift_median_cells": [float(np.median(sh[:, 0])), float(np.median(sh[:, 1]))],
            "LK_global_shift_std_cells": [float(sh[:, 0].std()), float(sh[:, 1].std())]}

    if base is not None and n == len(copylf_prediction(d)):
        delta = abs(e["variants"]["A_eval_copylf"]["nrmse"] - base)
        e["seam_A_vs_frozen_baseline_abs"] = delta
        e["seam_ok"] = bool(delta <= seam_tol)
        if not e["seam_ok"]:
            raise SystemExit(f"{ds}: variant A does not reproduce the frozen copy-LF "
                             f"baseline (|delta| {delta:.3g} > {seam_tol:g}); refusing to report")
    else:
        e["seam_A_vs_frozen_baseline_abs"] = None
        e["seam_ok"] = None
        e["seam_note"] = "test split truncated by --n_test; seam not enforceable"

    lk = e["variants"]["A_eval_copylf"]["LK_global_shift_median_cells"]
    pred = (r - 1.0) / 2.0
    dec = e["convention"].get("decimation")
    ramp = abs(e["convention"]["halfdomain_shift_axis0_cells"]["difference"]) > 0.3
    if not nested and not ramp and abs(lk[0]) < 0.1 and abs(lk[1]) < 0.1:
        e["verdict"] = ("NON_NESTED_BUT_CONSISTENT (non-integer refinement ratio, but no "
                        "measurable misregistration: global and half-domain LK shifts are "
                        "both < 0.1-0.3 cells)")
    elif not nested or (ramp and abs(lk[0]) < 0.3):
        e["verdict"] = ("NON_NESTED_STRETCH (zero-mean space-varying misregistration: "
                        "the half-domain LK shifts differ by "
                        f"{e['convention']['halfdomain_shift_axis0_cells']['difference']:+.3f} "
                        "cells while the global shift is ~0)")
    elif dec and dec["nrmse_lf_vs_HF_node_decimation"] <= 1e-6:
        e["verdict"] = "MISREGISTERED_NODE_DATA (and the ladder is DEGENERATE: " \
                       "the coarse solve equals the fine solve at this level pair)"
    elif dec and dec["nrmse_lf_vs_HF_node_decimation"] < dec["nrmse_lf_vs_HF_cellmean"] \
            and abs(lk[0] - pred) < 0.15 and abs(lk[1] - pred) < 0.15:
        e["verdict"] = "MISREGISTERED_NODE_DATA"
    elif abs(lk[0]) < 0.1 and abs(lk[1]) < 0.1:
        e["verdict"] = "CONSISTENT"
    else:
        e["verdict"] = "INCONCLUSIVE"

    if do_lsi and nested:
        e["lsi_ramp_projection"] = lsi_projection(ds, n_train, hg, pred)
    return e


def resolve(spec):
    cfg = yaml.safe_load((ROUND / "project.yaml").read_text())
    if spec.upper() == "PANEL":
        return list(cfg["panel"])
    if spec.upper() == "GUARD":
        return list(cfg["guard_set"])
    return [s for s in spec.split(",") if s]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--datasets", required=True, help="PANEL | GUARD | comma list")
    ap.add_argument("--out", required=True)
    ap.add_argument("--n_test", type=int, default=10 ** 9)
    ap.add_argument("--n_train", type=int, default=10 ** 9)
    ap.add_argument("--seam_tol", type=float, default=1e-9)
    ap.add_argument("--lsi", action="store_true",
                    help="also project a fitted LSI transfer function on the phase ramp")
    a = ap.parse_args()
    res = {"nrmse_def_hash": NRMSE_DEF_HASH, "per_dataset": {}}
    for ds in resolve(a.datasets):
        try:
            res["per_dataset"][ds] = one(ds, a.n_test, a.n_train, a.seam_tol, a.lsi)
        except SystemExit:
            raise
        except Exception as exc:                                   # noqa: BLE001
            res["per_dataset"][ds] = {"error": f"{type(exc).__name__}: {exc}"}
        e = res["per_dataset"][ds]
        print(f"[{ds}] {e.get('verdict', e.get('error'))}", flush=True)
        for k, v in e.get("variants", {}).items():
            print(f"    {k:44s} nRMSE {v['nrmse']:.6g}  skill "
                  f"{('%.6g' % v['skill_vs_frozen_copylf']) if v['skill_vs_frozen_copylf'] else 'n/a':>10s}"
                  f"  LK ({v['LK_global_shift_median_cells'][0]:+.3f},"
                  f"{v['LK_global_shift_median_cells'][1]:+.3f})", flush=True)
        if "lsi_ramp_projection" in e:
            p = e["lsi_ramp_projection"]
            print(f"    LSI transfer function: {p['frac_explained']:.4f} of its energy is the "
                  f"{p['assumed_offset_cells']:g}-cell phase ramp (c = {p['best_scalar_c']:.4f})",
                  flush=True)
    Path(a.out).write_text(json.dumps(res, indent=1))
    print("wrote", a.out)


if __name__ == "__main__":
    main()
