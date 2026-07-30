#!/usr/bin/env python
"""band_weight_counterfactual.py -- IS THAT SPECTACULAR BAND RATIO WORTH ANYTHING?

Per-band error-energy RATIOS (the `band_error_ratios` statistic used across
round 1) are unbounded in bands that hold almost no error, so they manufacture
"11x regressions" out of nothing.  This tool puts three things next to every
ratio:

  1. WEIGHT  -- the band's share of the REFERENCE's error, both as pooled energy
     and in the round metric's own weighting (per-sample share of rel-L2^2,
     which sums exactly to the per-sample rel^2 by Parseval).
  2. COUNTERFACTUAL -- the decisive number: replace arm A's Fourier error in one
     band by arm B's and RE-SCORE through `round1/eval/nrmse.py`.  The share of
     the A-vs-B skill gap that band actually owns.
  3. STRATA (--strata_npz) -- the same table restricted to a sample subset, so a
     pooled-energy statistic cannot be secretly a statement about two samples.

Read it as
----------
* `weights.metric_share_of_reference_error[b]` tells you the most a band can
  ever be worth.  A ratio of 11x in a band holding 5e-4 of the error is worth
  5e-4 of the score.
* `counterfactual[b].share_of_gap` is the honest attribution: what the A-vs-B
  skill gap would lose if that band were fixed.  Trust this over the ratios.
* If `strata` flips the ranking, the pooled statistic was a two-sample statement.

Worked precedent (s3_warp-B2): the scored warp arm retained 85.1% of copy-LF's
error energy in band 32-64 versus ~7.8% for both controls -- an 11x "mid-band
regression" that part 5 called the most informative signal on the card.  That
band holds 0.048% of copy-LF's error and the counterfactual gives it 0.45% of the
0.0521-skill regression; 85.7% of the regression is in band 0-16.  The same
failure mode had already appeared in s3_warp-B1 F4 (a wrap seam worth
0.12-0.74% of the metric).

Invoke
------
    source "$PROJECT_ROOT/.venv/bin/activate"
    # two model predictions (npz with an (N, n_cells) or (N,H,W) array)
    python tools/band_weight_counterfactual.py --dataset sharp__cahn_hilliard \
        --arm_a preds_warp.npz:pred --arm_b preds_warp_off.npz:pred --out b.json
    # zero-parameter built-ins need no files at all:
    #   copylf     = eval/panel_data.py::copylf_prediction (the round reference)
    #   nodealign  = ONE bilinear resample of the raw LF at k/r (B1 F3 variant C)
    python tools/band_weight_counterfactual.py --dataset sharp__cahn_hilliard \
        --arm_a nodealign --arm_b copylf --out b.json
    # restrict to a stratum (boolean or index array in an npz)
    python tools/band_weight_counterfactual.py ... --strata_npz strata.npz:matched

Bands default to the round convention `[0, .125, .25, .5, 1] * k_nyquist`
(identical to `tools/defect_correction_learnability.py::band_masks`,
`band_phase_anatomy.py` and s3_warp-B1's M7 bands).

Provenance: card `experiment_cards/s3_warp/batch_2/B2.json` part 6, findings
F5-F7; source probes `worktrees/s3_warp/B2/scratchpad/reanalysis_turn_2.py` and
`turn2_counterfactual.py`.
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


def band_masks(hw, fracs):
    h, w = int(hw[0]), int(hw[1])
    k_nyq = (max(h, w) if min(h, w) == 1 else min(h, w)) / 2.0
    ed = [f * k_nyq for f in fracs]
    ky = np.fft.fftfreq(h) * h
    kx = np.fft.rfftfreq(w) * w
    kk = np.sqrt(ky[:, None] ** 2 + kx[None, :] ** 2)
    masks = [(kk >= ed[i]) & (kk < ed[i + 1]) for i in range(len(ed) - 1)]
    masks[-1] = masks[-1] | (kk >= ed[-1])
    return masks, ed


def _herm_weights(h, w):
    """rfft2 column weights that make Parseval exact for a real field."""
    wt = np.ones((h, w // 2 + 1))
    wt[:, 1:(w + 1) // 2] *= 2.0
    if w % 2 == 0:
        wt[:, -1] = 1.0
    return wt


def band_energy(pred, target, hw, masks, sel=None):
    h, w = int(hw[0]), int(hw[1])
    e = (np.asarray(pred, np.float64) - np.asarray(target, np.float64)).reshape(-1, h, w)
    if sel is not None:
        e = e[sel]
    E = np.fft.rfft2(e)
    return np.array([float((np.abs(E[:, m]) ** 2).sum()) for m in masks])


def band_metric_shares(pred, target, hw, masks, sel=None):
    """Per-sample per-band share of rel-L2^2 (sums to rel^2 exactly)."""
    h, w = int(hw[0]), int(hw[1])
    e = (np.asarray(pred, np.float64) - np.asarray(target, np.float64)).reshape(-1, h, w)
    t = np.asarray(target, np.float64).reshape(-1, h * w)
    if sel is not None:
        e, t = e[sel], t[sel]
    E = np.fft.rfft2(e)
    wt = _herm_weights(h, w)
    den = (t ** 2).sum(1)
    return np.stack([((np.abs(E) ** 2) * wt)[:, m].sum(1) / (h * w) / den
                     for m in masks], 1)


def node_resample(lf_flat, lf_hw, hf_hw):
    h, w = lf_hw
    H, W = hf_hw
    gy, gx = np.meshgrid(np.arange(H) * h / H, np.arange(W) * w / W, indexing="ij")
    out = np.empty((lf_flat.shape[0], H * W))
    for i in range(lf_flat.shape[0]):
        out[i] = ndimage.map_coordinates(np.asarray(lf_flat[i], np.float64).reshape(h, w),
                                         [gy, gx], order=1, mode="grid-wrap").ravel()
    return out


def load_arm(spec, data, hw, n_cells):
    """`copylf` | `nodealign` | `path.npz:key` -> (N, n_cells) float64."""
    if spec == "copylf":
        return np.asarray(PD.copylf_prediction(data), np.float64), "copylf (panel_data)"
    if spec == "nodealign":
        lf_fid = max(data["lf_fids"])
        lf = np.asarray(data["field_by_fid"][lf_fid], np.float64)
        lf = lf[:np.asarray(data["field_by_fid"][data["hf_fid"]]).shape[0]]
        return node_resample(lf, data["grid_shape_by_fid"][lf_fid], hw), "node-aligned resample"
    path, _, key = spec.partition(":")
    z = np.load(path)
    if not key:
        cands = [k for k in z.files if np.asarray(z[k]).reshape(len(z[k]), -1).shape[1] == n_cells]
        if len(cands) != 1:
            raise ValueError(f"{path}: give an explicit key (candidates {cands})")
        key = cands[0]
    a = np.asarray(z[key], np.float64)
    return a.reshape(a.shape[0], -1), f"{Path(path).name}:{key}"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--split", default="test")
    ap.add_argument("--arm_a", required=True, help="copylf | nodealign | path.npz[:key]")
    ap.add_argument("--arm_b", required=True, help="the comparison arm (same syntax)")
    ap.add_argument("--reference", default="copylf",
                    help="denominator for the ratio/weight columns (default copylf)")
    ap.add_argument("--bands", default="0,0.125,0.25,0.5,1.0")
    ap.add_argument("--strata_npz", default=None,
                    help="path.npz:key with a boolean mask or index array over samples")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    d = PD.load_split(a.dataset, a.split)
    hw = d["grid_shape_by_fid"].get(d["hf_fid"])
    if hw is None:
        raise SystemExit(f"{a.dataset}: no 2-D HF grid shape")
    hf = np.asarray(d["field_by_fid"][d["hf_fid"]], np.float64)
    n_cells = hf.shape[1]
    fracs = [float(x) for x in a.bands.split(",")]
    masks, ed = band_masks(hw, fracs)

    A, na = load_arm(a.arm_a, d, hw, n_cells)
    B, nb = load_arm(a.arm_b, d, hw, n_cells)
    R, nr = load_arm(a.reference, d, hw, n_cells)
    ref_nrmse = N.nrmse(R, hf) if a.reference != "copylf" else N.nrmse(
        np.asarray(PD.copylf_prediction(d), np.float64), hf)

    sel = None
    if a.strata_npz:
        p, _, k = a.strata_npz.partition(":")
        m = np.asarray(np.load(p)[k])
        sel = m.astype(bool) if m.dtype == bool else np.isin(np.arange(hf.shape[0]), m)

    res = {"dataset": a.dataset, "split": a.split, "nrmse_def_hash": N.NRMSE_DEF_HASH,
           "arm_a": na, "arm_b": nb, "reference": nr,
           "band_edges_wavenumber": ed, "n_samples": int(hf.shape[0]),
           "n_selected": int(hf.shape[0] if sel is None else sel.sum())}

    e_ref = band_energy(R, hf, hw, masks, sel)
    m_ref = band_metric_shares(R, hf, hw, masks, sel).mean(0)
    res["weights"] = {
        "pooled_energy_share_of_reference_error": (e_ref / e_ref.sum()).tolist(),
        "metric_share_of_reference_error": (m_ref / m_ref.sum()).tolist()}
    res["ratios_vs_reference"] = {
        "arm_a": (band_energy(A, hf, hw, masks, sel) / e_ref).tolist(),
        "arm_b": (band_energy(B, hf, hw, masks, sel) / e_ref).tolist()}
    ma = band_metric_shares(A, hf, hw, masks, sel).mean(0)
    mb = band_metric_shares(B, hf, hw, masks, sel).mean(0)
    dm = ma - mb
    res["metric_weighted_a_minus_b"] = {
        "per_band": dm.tolist(),
        "share_of_total": (dm / dm.sum()).tolist() if abs(dm.sum()) > 0 else None}

    # the counterfactual honours --strata_npz too: scores are computed on the
    # selected samples with a SELECTED-stratum reference denominator.
    idx = slice(None) if sel is None else np.nonzero(sel)[0]
    hf_s, A_s, B_s, R_s = hf[idx], A[idx], B[idx], R[idx]
    ref_s = N.nrmse(R_s, hf_s)
    ska, skb = N.skill(N.nrmse(A_s, hf_s), ref_s), N.skill(N.nrmse(B_s, hf_s), ref_s)
    gap = ska - skb
    h, w = int(hw[0]), int(hw[1])
    Ea = np.fft.rfft2((A_s - hf_s).reshape(-1, h, w))
    Eb = np.fft.rfft2((B_s - hf_s).reshape(-1, h, w))
    cf = []
    for b, m in enumerate(masks):
        E = Ea.copy()
        E[:, m] = Eb[:, m]
        hyb = np.fft.irfft2(E, s=(h, w)).reshape(-1, h * w) + hf_s
        sk = N.skill(N.nrmse(hyb, hf_s), ref_s)
        cf.append({"band": [ed[b], ed[b + 1]], "skill_if_a_had_b_error_here": sk,
                   "share_of_gap": float((ska - sk) / gap) if gap != 0 else None})
    res["skill_arm_a"], res["skill_arm_b"], res["gap"] = ska, skb, gap
    res["counterfactual"] = cf

    print(f"{a.dataset}  A={na} skill {ska:.5f} | B={nb} skill {skb:.5f} | gap {gap:+.5f}"
          f"  (n_selected {res['n_selected']}/{res['n_samples']})")
    print("  band            weight(metric)   ratio_A   ratio_B   share_of_gap")
    for b in range(len(masks)):
        print("  [%6.1f,%6.1f]  %13.5g %9.4f %9.4f %14.4f" % (
            ed[b], ed[b + 1], res["weights"]["metric_share_of_reference_error"][b],
            res["ratios_vs_reference"]["arm_a"][b],
            res["ratios_vs_reference"]["arm_b"][b], cf[b]["share_of_gap"]))
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w") as f:
        json.dump(res, f, indent=1)
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
