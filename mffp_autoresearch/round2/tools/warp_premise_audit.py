#!/usr/bin/env python
"""warp_premise_audit.py -- IS THERE ANY DISPLACEMENT TO WARP HERE, AND IS THE
ORACLE DISPLACEMENT AN IDENTIFIABLE TARGET?

Answers, before a displacement/warp/registration card is built, the two questions
that decided `s3_warp-B2` (a falsified one-sided warp card) after the fact:

  (A) PREMISE -- how much interface displacement is there between the moving
      image and the target, measured with a SUB-PIXEL estimator that has been
      CALIBRATED against synthetic ground truth on this very data?  Pixel-lattice
      estimators (EDT / distance-transform) report 0.0 for anything below half a
      cell, which reads as "no displacement" when it means "below my resolution".
      Also: the skill a test-fitted per-sample RIGID-SHIFT ORACLE reaches, on the
      frozen copy-LF path and on a node-aligned corrected path -- the cheapest
      upper bound on what any displacement model can buy.

  (B) GAUGE (--gauge, needs --phi_npz) -- a displacement field fitted by
      minimising image L2 is identified ONLY along grad(u) (the optical-flow
      aperture problem).  Decomposes a fitted phi into interface-NORMAL and
      TANGENTIAL parts.  If the normal share of the interface phi-energy is
      small, `|phi - phi_oracle|^2` is a supervision target made mostly of gauge
      and no head of any capacity can generalise on it.

Read it as
----------
* `levelset.corrected.median` >> 1 cell           -> a real transport dataset.
* `levelset.corrected.median` <~ 0.1 cell         -> NOTHING TO WARP; a warp can
  only add error on the bulk.  (s3_warp-B2 measured 0.0070 on
  sharp__cahn_hilliard, the panel's *best* warp candidate.)
* `levelset.copylf.median ~ |((r-1)/2, (r-1)/2)|` -> the "displacement" you are
  seeing is the round's grid-registration convention (s3_warp-B1 F1/F2), not
  physics.  Compare `rigid_oracle.copylf` with `rigid_oracle.corrected`: if the
  first is much better, the oracle was buying registration.
* `edt_calibration` -> what the pixel-lattice estimator reports for a KNOWN
  shift.  Any "0.0 cells" reading from an EDT-style diagnostic must be read
  against this table.
* `gauge.<field>.interface_normal_energy_share` << 1 -> the fitted phi is mostly
  gauge; supervise the normal projection or the warped IMAGE instead.

Invoke
------
    source "$PROJECT_ROOT/.venv/bin/activate"
    python tools/warp_premise_audit.py --datasets sharp__cahn_hilliard --out a.json
    python tools/warp_premise_audit.py --datasets PANEL --out a.json --no_rigid
    python tools/warp_premise_audit.py --datasets sharp__cahn_hilliard --out a.json \
        --gauge --phi_npz <outputs>/eval/<fam>_<ds>_phi.npz --phi_keys phi_pred_warp

Cost: ~1 min/dataset for (A) without --rigid_oracle; the rigid oracle adds ~2 min
per 100 256^2 samples (pure numpy, login-node fine).  Every nRMSE goes through
`round1/eval/nrmse.py`; copy-LF is `eval/panel_data.py::copylf_prediction`,
unedited.

Provenance: card `experiment_cards/s3_warp/batch_2/B2.json` part 6, findings
F1-F4 and F9; source probes
`worktrees/s3_warp/B2/scratchpad/reanalysis_turn_{1,3}.py`.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage


def _round_root() -> Path:
    top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                         text=True, check=True,
                         cwd=Path(__file__).resolve().parent).stdout.strip()
    return Path(top) / "mffp_autoresearch" / "round1"


ROUND = _round_root()
sys.path.insert(0, str(ROUND / "eval"))
import nrmse as N          # noqa: E402
import panel_data as PD    # noqa: E402


# ---------------------------------------------------------------- estimators
def interface_mask(u, hw, tau):
    """|u| <= tau * max|u| per sample (s3_warp-B1 / s2-B1 convention)."""
    h, w = hw
    u = np.asarray(u, np.float64).reshape(-1, h, w)
    return np.abs(u) <= tau * np.abs(u).reshape(u.shape[0], -1).max(1)[:, None, None]


def edt_interface_displacement(moving, target, hw, tau):
    """Pixel-lattice estimator: median EDT distance from each moving-image
    interface cell to the nearest target interface cell (per sample)."""
    m_mv, m_tg = interface_mask(moving, hw, tau), interface_mask(target, hw, tau)
    vals = []
    for i in range(m_mv.shape[0]):
        if not m_tg[i].any() or not m_mv[i].any():
            continue
        vals.append(np.median(ndimage.distance_transform_edt(~m_tg[i])[m_mv[i]]))
    v = np.asarray(vals)
    if v.size == 0:
        return {"n": 0}
    return {"median": float(np.median(v)), "p90": float(np.percentile(v, 90)),
            "mean": float(v.mean()), "max": float(v.max()), "n": int(v.size),
            "frac_samples_zero": float((v == 0).mean())}


def levelset_normal_disp(moving, target, hw, tau):
    """Sub-pixel first-order level-set normal displacement, in target cells:
        d = (u_moving - u_target) / |grad u_target|   on target interface cells."""
    h, w = hw
    mv = np.asarray(moving, np.float64).reshape(-1, h, w)
    tg = np.asarray(target, np.float64).reshape(-1, h, w)
    gy = 0.5 * (np.roll(tg, -1, 1) - np.roll(tg, 1, 1))
    gx = 0.5 * (np.roll(tg, -1, 2) - np.roll(tg, 1, 2))
    gm = np.sqrt(gy ** 2 + gx ** 2)
    m = interface_mask(tg, hw, tau)
    per = []
    for i in range(mv.shape[0]):
        sel = m[i] & (gm[i] > 1e-12)
        if sel.sum() < 10:
            continue
        per.append(np.median(np.abs(mv[i][sel] - tg[i][sel]) / gm[i][sel]))
    v = np.asarray(per)
    if v.size == 0:
        return {"n": 0}
    return {"median": float(np.median(v)), "p90": float(np.percentile(v, 90)),
            "mean": float(v.mean()), "max": float(v.max()), "n": int(v.size),
            "per_sample": v.tolist()}


def fourier_shift(fields, hw, sy, sx):
    h, w = hw
    F = np.fft.rfft2(np.asarray(fields, np.float64).reshape(-1, h, w))
    ky = np.fft.fftfreq(h)[:, None]
    kx = np.fft.rfftfreq(w)[None, :]
    ph = np.exp(-2j * np.pi * (ky * np.asarray(sy).reshape(-1, 1, 1)
                               + kx * np.asarray(sx).reshape(-1, 1, 1)))
    return np.fft.irfft2(F * ph, s=(h, w)).reshape(-1, h * w)


def node_resample(lf_flat, lf_hw, hf_hw):
    """ONE bilinear resample of the raw LF at node-aligned coords k/r, grid-wrap
    (s3_warp-B1 F3 variant C: the registration-corrected reference path)."""
    h, w = lf_hw
    H, W = hf_hw
    gy, gx = np.meshgrid(np.arange(H) * h / H, np.arange(W) * w / W, indexing="ij")
    out = np.empty((lf_flat.shape[0], H * W))
    for i in range(lf_flat.shape[0]):
        out[i] = ndimage.map_coordinates(np.asarray(lf_flat[i], np.float64).reshape(h, w),
                                         [gy, gx], order=1, mode="grid-wrap").ravel()
    return out


def rigid_shift_oracle(moving, target, hw, max_cells=4.0):
    """Per-sample rel-L2-optimal CONTINUOUS circular shift (coarse->fine search
    evaluated in Fourier space by Parseval).  Test-fitted: an ORACLE."""
    h, w = hw
    Fm = np.fft.fft2(np.asarray(moving, np.float64).reshape(-1, h, w))
    Ft = np.fft.fft2(np.asarray(target, np.float64).reshape(-1, h, w))
    ky, kx = np.fft.fftfreq(h)[:, None], np.fft.fftfreq(w)[None, :]
    R = int(np.ceil(max_cells))
    sh = np.zeros((Fm.shape[0], 2))
    for i in range(Fm.shape[0]):
        cy = cx = 0.0
        for g in (np.arange(-R, R + 1, 1.0), np.arange(-1.0, 1.0 + 1e-9, 0.1),
                  np.arange(-0.1, 0.1 + 1e-9, 0.02)):
            best = None
            for sy in cy + g:
                py = np.exp(-2j * np.pi * ky * sy)
                for sx in cx + g:
                    v = float((np.abs(Fm[i] * py * np.exp(-2j * np.pi * kx * sx)
                                      - Ft[i]) ** 2).sum())
                    if best is None or v < best[0]:
                        best = (v, sy, sx)
            cy, cx = best[1], best[2]
        sh[i] = (cy, cx)
    return sh, fourier_shift(moving, hw, sh[:, 0], sh[:, 1])


def gauge_decomposition(phi, image, hw, tau):
    """Split a displacement field into interface-NORMAL (identifiable) and
    TANGENTIAL (aperture-problem gauge) parts, on `image`'s interface band."""
    h, w = hw
    u = np.asarray(image, np.float64).reshape(-1, h, w)
    gy = 0.5 * (np.roll(u, -1, 1) - np.roll(u, 1, 1))
    gx = 0.5 * (np.roll(u, -1, 2) - np.roll(u, 1, 2))
    gm = np.sqrt(gy ** 2 + gx ** 2)
    ny, nx = gy / np.maximum(gm, 1e-12), gx / np.maximum(gm, 1e-12)
    p = np.asarray(phi, np.float64).reshape(-1, 2, h, w)
    dn = p[:, 0] * ny + p[:, 1] * nx
    mag = np.sqrt(p[:, 0] ** 2 + p[:, 1] ** 2)
    tg = np.sqrt(np.maximum(mag ** 2 - dn ** 2, 0.0))
    sel = interface_mask(u, hw, tau)
    q = np.quantile(gm, [0.1, 0.9])
    return {
        "interface_median_abs_phi": float(np.median(mag[sel])),
        "interface_median_abs_normal": float(np.median(np.abs(dn[sel]))),
        "interface_median_abs_tangential": float(np.median(tg[sel])),
        "interface_normal_energy_share": float((dn[sel] ** 2).sum()
                                               / max((mag[sel] ** 2).sum(), 1e-30)),
        "allpix_normal_energy_share": float((dn ** 2).sum()
                                            / max((mag ** 2).sum(), 1e-30)),
        "median_abs_phi_lowgrad_decile": float(np.median(mag[gm <= q[0]])),
        "median_abs_phi_highgrad_decile": float(np.median(mag[gm >= q[1]])),
        "energy_share_in_lowgrad_half": float((mag[gm <= np.median(gm)] ** 2).sum()
                                              / max((mag ** 2).sum(), 1e-30)),
    }


# ---------------------------------------------------------------- driver
def audit_dataset(ds, tau, do_rigid, calib_shifts, gauge_npz, gauge_keys):
    out = {"dataset": ds, "tau": tau, "nrmse_def_hash": N.NRMSE_DEF_HASH}
    d = PD.load_split(ds, "test")
    hf_fid, lf_fid = d["hf_fid"], max(d["lf_fids"])
    hw = d["grid_shape_by_fid"].get(hf_fid)
    lw = d["grid_shape_by_fid"].get(lf_fid)
    if hw is None or lw is None:
        return {"dataset": ds, "error": "non-2-D dataset (no square grid shape)"}
    hf = np.asarray(d["field_by_fid"][hf_fid], np.float64)
    lf = np.asarray(d["field_by_fid"][lf_fid], np.float64)[:hf.shape[0]]
    copylf = np.asarray(PD.copylf_prediction(d), np.float64)
    corrected = node_resample(lf, lw, hw)
    out["grids"] = {"lf": list(lw), "hf": list(hw), "n_test": int(hf.shape[0])}
    out["copylf_nrmse"] = N.nrmse(copylf, hf)
    out["corrected_skill"] = N.skill(N.nrmse(corrected, hf), out["copylf_nrmse"])
    out["expected_registration_offset_cells"] = float(
        np.sqrt(2) * (hw[0] / lw[0] - 1) / 2)

    out["edt"] = {"copylf": edt_interface_displacement(copylf, hf, hw, tau),
                  "corrected": edt_interface_displacement(corrected, hf, hw, tau)}
    ls_c = levelset_normal_disp(copylf, hf, hw, tau)
    ls_r = levelset_normal_disp(corrected, hf, hw, tau)
    for v in (ls_c, ls_r):
        v.pop("per_sample", None)
    out["levelset"] = {"copylf": ls_c, "corrected": ls_r}

    cal = {}
    for s in calib_shifts:
        moved = fourier_shift(hf, hw, np.full(hf.shape[0], s), np.full(hf.shape[0], s))
        e = edt_interface_displacement(moved, hf, hw, tau)
        l = levelset_normal_disp(moved, hf, hw, tau)
        cal[f"{s}"] = {"true_disp_cells": float(np.sqrt(2) * s),
                       "edt_reports": e.get("median"),
                       "edt_frac_samples_zero": e.get("frac_samples_zero"),
                       "levelset_reports": l.get("median")}
    out["edt_calibration"] = cal

    if do_rigid:
        ro = {}
        for nm, mov in (("copylf", copylf), ("corrected", corrected)):
            sh, moved = rigid_shift_oracle(mov, hf, hw)
            mag = np.linalg.norm(sh, axis=1)
            base, orc = N.nrmse(mov, hf), N.nrmse(moved, hf)
            mu = sh.mean(0)
            gc = N.nrmse(fourier_shift(mov, hw, np.full(len(mag), mu[0]),
                                       np.full(len(mag), mu[1])), hf)
            ro[nm] = {"base_skill": N.skill(base, out["copylf_nrmse"]),
                      "oracle_skill": N.skill(orc, out["copylf_nrmse"]),
                      "share_of_base_error_removed": float(1 - orc / base),
                      "median_abs_shift_cells": float(np.median(mag)),
                      "p90_abs_shift_cells": float(np.percentile(mag, 90)),
                      "mean_shift": mu.tolist(), "sd_shift": sh.std(0).tolist(),
                      "global_const_shift_skill": N.skill(gc, out["copylf_nrmse"])}
        out["rigid_oracle"] = ro

    if gauge_npz:
        z = np.load(gauge_npz)
        keys = gauge_keys or [k for k in z.files if z[k].ndim == 4 and z[k].shape[1] == 2]
        g = {}
        for k in keys:
            ph = np.asarray(z[k], np.float64)
            if ph.ndim != 4 or ph.shape[1] != 2:
                g[k] = {"error": f"expected (N,2,H,W), got {ph.shape}"}
                continue
            if ph.shape[2:] != tuple(hw):
                g[k] = {"error": f"phi grid {ph.shape[2:]} != HF grid {tuple(hw)}"}
                continue
            g[k] = gauge_decomposition(ph[:corrected.shape[0]], corrected, hw, tau)
        out["gauge"] = g
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--datasets", required=True, help="PANEL | GUARD | comma list")
    ap.add_argument("--out", required=True)
    ap.add_argument("--tau", type=float, default=0.1, help="interface band |u| <= tau*max|u|")
    ap.add_argument("--calib_shifts", default="0.25,0.5,1.0,2.0,4.0")
    ap.add_argument("--rigid_oracle", dest="rigid", action="store_true", default=True)
    ap.add_argument("--no_rigid", dest="rigid", action="store_false")
    ap.add_argument("--gauge", action="store_true",
                    help="also run the aperture-problem decomposition (needs --phi_npz)")
    ap.add_argument("--phi_npz", default=None, help="npz with (N,2,H,W) displacement fields")
    ap.add_argument("--phi_keys", default=None, help="comma list of npz keys")
    a = ap.parse_args()

    cfg = PD.load_config()
    if a.datasets == "PANEL":
        names = list(cfg["panel"])
    elif a.datasets == "GUARD":
        names = list(cfg["guard_set"])
    else:
        names = [s for s in a.datasets.split(",") if s]
    shifts = [float(s) for s in a.calib_shifts.split(",") if s]
    keys = [s for s in a.phi_keys.split(",")] if a.phi_keys else None

    res = {"nrmse_def_hash": N.NRMSE_DEF_HASH, "datasets": {}}
    for ds in names:
        try:
            res["datasets"][ds] = audit_dataset(
                ds, a.tau, a.rigid, shifts,
                a.phi_npz if a.gauge else None, keys)
        except Exception as exc:                      # noqa: BLE001
            res["datasets"][ds] = {"dataset": ds, "error": f"{type(exc).__name__}: {exc}"}
        r = res["datasets"][ds]
        if "error" in r:
            print(f"{ds:34s} ERROR {r['error']}")
            continue
        print(f"{ds:34s} corrected_skill {r['corrected_skill']:.4f} | "
              f"levelset copylf {r['levelset']['copylf'].get('median', float('nan')):.4f} "
              f"corrected {r['levelset']['corrected'].get('median', float('nan')):.4f} cells "
              f"(expect {r['expected_registration_offset_cells']:.4f} if it is registration) | "
              f"EDT corrected median {r['edt']['corrected'].get('median')}")
        if "rigid_oracle" in r:
            ro = r["rigid_oracle"]
            print(f"{'':34s} rigid oracle: copylf {ro['copylf']['oracle_skill']:.4f} "
                  f"(med |s| {ro['copylf']['median_abs_shift_cells']:.4f}) -> corrected "
                  f"{ro['corrected']['oracle_skill']:.4f} "
                  f"(med |s| {ro['corrected']['median_abs_shift_cells']:.4f})")
        for k, v in r.get("gauge", {}).items():
            if "error" in v:
                print(f"{'':34s} gauge {k}: {v['error']}")
            else:
                print(f"{'':34s} gauge {k}: |phi| {v['interface_median_abs_phi']:.4f} = "
                      f"normal {v['interface_median_abs_normal']:.4f} + tangential "
                      f"{v['interface_median_abs_tangential']:.4f}, normal energy share "
                      f"{v['interface_normal_energy_share']:.4f}")
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w") as f:
        json.dump(res, f, indent=1)
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
