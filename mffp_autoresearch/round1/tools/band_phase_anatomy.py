#!/usr/bin/env python3
"""band_phase_anatomy.py -- is a corrector's per-band failure AMPLITUDE or PHASE?

Provenance: s4_hybrid_routing-B2 mechanism turns 2-3 (card part 6, F6, F9-F11).

`field_error_decomposition.py` reports a per-band RELATIVE ERROR; that cannot
tell "the correction is too small in this band" from "the correction is the right
size and points the wrong way". This tool splits exactly that, band by band,
against the round's own copy-LF reference:

for the decomposition `pred = copylf + corr` (so `err = (copylf - hf) - corr`),
inside each radial band

    cross = (E_c + E_r - E_e) / 2         E_c = copy-LF error, E_r = correction,
    cos   = cross / sqrt(E_c * E_r)       E_e = prediction error   (energies)
    g*    = cross / E_r                   the optimal band gain
    best  = E_c * (1 - cos^2)             the error an ORACLE band gain would leave

`cos ~ 1` with `g* != 1` -> AMPLITUDE: rescale the branch and the band is fixed.
`cos ~ 0` with `E_r/E_c ~ 1` -> PHASE: the branch injects full-amplitude,
phase-random energy and *doubles* the band's error (`E_e/E_c -> 1 + E_r/E_c`); no
gate, gain or capacity knob can repair it -- only a different operator class.
On `sharp__fisher_kpp_2d` this is what separated a 200-epoch attention corrector
(top-band cos 0.034, err 1.99x) from a zero-parameter LSI filter (cos 0.996).

Two input paths:
  --from_diag  a family diag JSON that already stores band ENERGIES for the three
               fields (no data loaded, instant; requires base == copy-LF for the
               identity to be exact -- the tool says so in its output).
  --pred_npz   any prediction on a panel dataset's test split; copy-LF comes from
               `eval/panel_data.py` and the score from `eval/nrmse.py`.
  --with_refs  additionally scores the two zero-parameter reference directions
               (`registration_audit.build_variants` variant C, and the s6-B1 LSI
               filter from `defect_correction_learnability`) in the same bands --
               the honest ceiling any learned corrector is competing with.

Examples
  python tools/band_phase_anatomy.py --from_diag <...>/diag_attn_gap_fkpp_..._e200_s0.json
  python tools/band_phase_anatomy.py --dataset sharp__fisher_kpp_2d \
      --pred_npz /tmp/pred.npz --pred_key pred --with_refs --out /tmp/band.json
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np


def _round_root() -> Path:
    out = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                         text=True, check=True, cwd=Path(__file__).resolve().parent)
    return Path(out.stdout.strip()) / "mffp_autoresearch" / "round1"


ROUND = _round_root()
sys.path.insert(0, str(ROUND / "eval"))
sys.path.insert(0, str(ROUND / "tools"))
import nrmse as NR                                                    # noqa: E402
import panel_data as PD                                               # noqa: E402


def band_masks(grid, edges):
    H, W = grid
    ky = np.fft.fftshift(np.fft.fftfreq(H)) * 2.0        # 1.0 == Nyquist
    kx = np.fft.fftshift(np.fft.fftfreq(W)) * 2.0
    KR = np.sqrt(ky[:, None] ** 2 + kx[None, :] ** 2)
    return [((KR >= edges[b]) & (KR < edges[b + 1])) for b in range(len(edges) - 1)]


def band_energy(flat, grid, masks):
    H, W = grid
    f = np.asarray(flat, dtype=np.float64).reshape(-1, H, W)
    P = (np.abs(np.fft.fftshift(np.fft.fft2(f, axes=(1, 2)), axes=(1, 2))) ** 2).sum(0)
    return np.array([P[m].sum() for m in masks])


def anatomy(Ec, Er, Ee):
    cross = (Ec + Er - Ee) / 2.0
    cos = cross / np.sqrt(np.maximum(Ec * Er, 1e-300))
    return dict(E_corr_over_Ec=(Er / Ec).tolist(), E_err_over_Ec=(Ee / Ec).tolist(),
                cos=cos.tolist(), g_star=(cross / np.maximum(Er, 1e-300)).tolist(),
                best_gain_residual_over_Ec=(1 - cos ** 2).tolist())


def verdict(a, i):
    c, r = a["cos"][i], a["E_corr_over_Ec"][i]
    if c > 0.9:
        return "AMPLITUDE" if abs(a["g_star"][i] - 1) > 0.15 else "clean"
    if c < 0.25 and r > 0.5:
        return "PHASE (full-amplitude, phase-random injection)"
    return "PARTIAL (mixed phase/amplitude)"


def show(label, edges, a, exact):
    print(f"\n-- {label} {'[EXACT: base == copy-LF]' if exact else '[APPROX: base != copy-LF]'}")
    print("  band (frac Nyquist)  E_corr/E_c  E_err/E_c        cos        g*  oracle-gain  verdict")
    for i in range(len(a["cos"])):
        print("  [%.3f,%.3f]       %10.4f %10.4f %10.4f %9.4f %12.4f  %s" % (
            edges[i], edges[i + 1], a["E_corr_over_Ec"][i], a["E_err_over_Ec"][i],
            a["cos"][i], a["g_star"][i], a["best_gain_residual_over_Ec"][i],
            verdict(a, i) if exact else "-"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from_diag", default=None)
    ap.add_argument("--diag_bands_key", default="sidecars.bands")
    ap.add_argument("--dataset", default=None)
    ap.add_argument("--pred_npz", default=None)
    ap.add_argument("--pred_key", default="pred")
    ap.add_argument("--n_samples", type=int, default=0, help="0 = all rows in the npz")
    ap.add_argument("--bands", default="0,0.125,0.25,0.5,1.0")
    ap.add_argument("--with_refs", action="store_true")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    edges = [float(x) for x in a.bands.split(",")]
    res = {"band_edges_frac": edges, "nrmse_def_hash": NR.NRMSE_DEF_HASH}

    if a.from_diag:
        d = json.load(open(a.from_diag))
        cur = d
        for p in a.diag_bands_key.split("."):
            cur = cur[p]
        f = cur["fields"]
        Ec = np.array(f["copylf_error"]["band_energy"], float)
        Er = np.array(f["applied_correction"]["band_energy"], float)
        Ee = np.array(f["prediction_error"]["band_energy"], float)
        exact = abs(np.array(f["copylf_minus_base"]["band_energy"], float)).sum() == 0.0
        an = anatomy(Ec, Er, Ee)
        print("=" * 108)
        print(f"band phase anatomy from {Path(a.from_diag).name}"
              f"  (dataset {d.get('dataset')}, arm {d.get('arm')})")
        print("=" * 108)
        show("applied correction vs the copy-LF error", cur["band_edges_frac"], an, exact)
        if "lsi_correction" in f:
            El = np.array(f["lsi_correction"]["band_energy"], float)
            print(f"\n  in-run LSI correction energy / copy-LF error energy by band: "
                  f"{[round(x, 4) for x in (El / Ec)]}")
        res["from_diag"] = dict(anatomy=an, exact_identity=bool(exact))

    if a.pred_npz:
        if not a.dataset:
            sys.exit("--pred_npz needs --dataset")
        te = PD.load_split(a.dataset, "test")
        hf = te["hf_fid"]
        g = te["grid_shape_by_fid"][hf]
        grid = (int(g[0]), int(g[1]))
        Y = np.asarray(te["field_by_fid"][hf], float).reshape(-1, grid[0] * grid[1])
        cl = PD.copylf_prediction(te).astype(np.float64)
        z = np.load(a.pred_npz)
        pred = np.asarray(z[a.pred_key], dtype=np.float64)
        n = pred.shape[0] if not a.n_samples else min(a.n_samples, pred.shape[0])
        pred, Y, cl = pred[:n], Y[:n], cl[:n]
        masks = band_masks(grid, edges)
        Ec = band_energy(cl - Y, grid, masks)
        Er = band_energy(pred - cl, grid, masks)
        Ee = band_energy(pred - Y, grid, masks)
        an = anatomy(Ec, Er, Ee)
        print("=" * 108)
        print(f"band phase anatomy -- {a.dataset}, {n} test samples, grid {grid}")
        print(f"  copy-LF {NR.nrmse(cl, Y):.8f} | prediction {NR.nrmse(pred, Y):.8f} "
              f"| skill {NR.nrmse(pred, Y)/NR.nrmse(cl, Y):.6f}")
        print("=" * 108)
        show(f"{Path(a.pred_npz).name}:{a.pred_key} implied correction", edges, an, True)
        res["pred"] = dict(anatomy=an, n=n,
                           nrmse=float(NR.nrmse(pred, Y)), copylf=float(NR.nrmse(cl, Y)))

        if a.with_refs:
            import registration_audit as RA
            import defect_correction_learnability as DCL
            lfd = max(te["lf_fids"]); lg = te["grid_shape_by_fid"][lfd]
            lf2d = np.asarray(te["field_by_fid"][lfd], float).reshape(-1, int(lg[0]), int(lg[1]))[:n]
            v = RA.build_variants(lf2d, grid, cl, periodic=True)
            tr = PD.load_split(a.dataset, "train")
            LF_tr = PD.copylf_prediction(tr)
            Y_tr = np.asarray(tr["field_by_fid"][tr["hf_fid"]], float)[:LF_tr.shape[0]]
            perm = np.random.default_rng(0).permutation(LF_tr.shape[0])
            fit = perm[max(1, int(round(0.2 * LF_tr.shape[0]))):][:320]
            T = DCL.fit_transfer(LF_tr[fit], (Y_tr - LF_tr)[fit], grid, ridge=0.0)
            refs = {"variantC_node_aligned": v["C_node_aligned_bilinear"],
                    "lsi_filter": cl + DCL.apply_transfer(cl, T, grid)}
            res["refs"] = {}
            for lab, P in refs.items():
                anr = anatomy(Ec, band_energy(P - cl, grid, masks), band_energy(P - Y, grid, masks))
                print(f"\n  reference `{lab}`: nRMSE {NR.nrmse(P, Y):.8f} "
                      f"skill {NR.nrmse(P, Y)/NR.nrmse(cl, Y):.6f}")
                show(f"reference {lab}", edges, anr, True)
                res["refs"][lab] = dict(anatomy=anr, nrmse=float(NR.nrmse(P, Y)))

    if not (a.from_diag or a.pred_npz):
        sys.exit("pass --from_diag and/or --dataset/--pred_npz")
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1)
        print(f"\n[wrote] {a.out}")


if __name__ == "__main__":
    main()
