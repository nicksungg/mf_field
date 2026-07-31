#!/usr/bin/env python
"""Diagnose a multi-fidelity dataset's LADDER before designing a model for it.

Provenance: promoted from `s1_poisson-B1` mechanism analysis turn 1
(`worktrees/s1_poisson/B1/scratchpad/reanalysis_turn_1.py`). There it showed
that `ifc_poisson`'s four levels are the SAME field shape (Pearson r >= 0.94
after nearest-condition matching) under a clean ~h^2, 42x amplitude law, and
that the levels are NOT index-aligned — which is why a shared target scaler
across levels is a trap and why "the intermediate levels carry no information"
was the wrong reading of that card's null.

WHAT IT MEASURES (per dataset, read-only, seconds):
  amplitude_law            per-level N / grid / max|Y| / RMS|Y| and the
                           consecutive RMS ratios (is the level spread a clean
                           discretization scale law or noise?)
  index_alignment          max |X^(s)[:n] - X^(t)[:n]| per pair; 0 => the
                           fidelity sample lists are index-aligned and naive
                           cross-level row construction is safe
  condition_coverage       per-level condition box + scaled nearest-neighbour
                           distance from the HF-train and TEST conditions to
                           each level's cloud (does a level cover the test
                           distribution at all?)
  cross_level_consistency  nearest-condition-matched, upsampled source vs
                           target field: rel-L2 raw, rel-L2 after ONE optimal
                           global gain, the gain itself, and Pearson r
                           (does a level carry the HF SHAPE?)
  matched_level_predictor  training-free ceiling on the real test split: nearest
                           -condition sample at level f, upsampled, times one
                           calibration gain fit on the HF TRAIN samples only,
                           scored with eval/nrmse.py; plus the zero-predictor
                           and HF-train-mean baselines for scale

USAGE
  python tools/ladder_level_diagnostic.py --dataset ifc_poisson \
      [--split train] [--out diag.json] [--paper_bar 0.036]

Any dataset the round's `eval/panel_data.py` can load works (ifc_raw and npz_l
layouts alike).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F


def _repo_root() -> Path:
    out = subprocess.run(["git", "rev-parse", "--show-toplevel"], check=True,
                         capture_output=True, text=True,
                         cwd=Path(__file__).resolve().parent)
    return Path(out.stdout.strip())


sys.path.insert(0, str(_repo_root() / "mffp_autoresearch" / "round1" / "eval"))
import nrmse as nrmse_mod  # noqa: E402
import panel_data  # noqa: E402


def _hw(n_cells: int):
    s = int(round(np.sqrt(n_cells)))
    if s * s != n_cells:
        raise ValueError(f"non-square field with {n_cells} cells; extend the tool")
    return (s, s)


def _to_grid(y_flat, src_hw, dst_hw):
    t = torch.from_numpy(np.ascontiguousarray(y_flat, dtype=np.float32))
    t = t.view(-1, 1, src_hw[0], src_hw[1])
    if tuple(src_hw) != tuple(dst_hw):
        t = F.interpolate(t, size=tuple(dst_hw), mode="bilinear", align_corners=False)
    return t.squeeze(1).numpy().astype(np.float64)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--split", default="train")
    ap.add_argument("--test_split", default="test")
    ap.add_argument("--paper_bar", type=float, default=None,
                    help="if given, also report nRMSE / paper_bar")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    tr = panel_data.load_split(args.dataset, args.split)
    te = panel_data.load_split(args.dataset, args.test_split)
    fids = sorted(int(f) for f in tr["fids"])
    HF = int(tr["hf_fid"])
    hw = {f: _hw(int(tr["n_cells_by_fid"][f])) for f in fids}
    fld = {f: tr["field_by_fid"][f].astype(np.float64) for f in fids}
    Xc = {f: tr["cond_by_fid"][f].astype(np.float64) for f in fids}

    res = {"dataset": args.dataset, "fids": fids, "hf_fid": HF,
           "nrmse_def_hash": nrmse_mod.NRMSE_DEF_HASH}

    # ---- amplitude law ----
    amp = {str(f): dict(n=int(fld[f].shape[0]), grid=list(hw[f]),
                        max_abs=float(np.abs(fld[f]).max()),
                        rms=float(np.sqrt((fld[f] ** 2).mean())))
           for f in fids}
    res["amplitude_law"] = dict(
        per_level=amp,
        consecutive_rms_ratio={f"{a}->{b}": amp[str(a)]["rms"] / amp[str(b)]["rms"]
                               for a, b in zip(fids[:-1], fids[1:])},
        max_over_min_rms=max(v["rms"] for v in amp.values())
        / min(v["rms"] for v in amp.values()),
        shared_scaler_if_pooled=max(v["max_abs"] for v in amp.values()),
    )

    # ---- index alignment ----
    align = {}
    for s, t in combinations(fids, 2):
        n = min(len(Xc[s]), len(Xc[t]))
        align[f"{s}->{t}"] = float(np.abs(Xc[s][:n] - Xc[t][:n]).max()) if n else float("nan")
    res["index_alignment"] = dict(
        max_abs_cond_diff=align,
        index_aligned=bool(all(v == 0.0 for v in align.values())))

    # ---- condition coverage ----
    pool = np.concatenate([Xc[f] for f in fids], 0)
    sd = pool.std(0)
    sd[sd == 0] = 1.0

    def nn(A, B):
        d = np.sqrt((((A[:, None, :] - B[None, :, :]) / sd) ** 2).sum(-1))
        j = d.argmin(1)
        return d[np.arange(len(A)), j], j

    Xte = te["cond_by_fid"][HF].astype(np.float64)
    cov = {"per_level_min": {str(f): Xc[f].min(0).tolist() for f in fids},
           "per_level_max": {str(f): Xc[f].max(0).tolist() for f in fids},
           "test_min": Xte.min(0).tolist(), "test_max": Xte.max(0).tolist(),
           "nn_dist_scaled": {}}
    for f in fids:
        dh, _ = nn(Xc[HF], Xc[f])
        dt, _ = nn(Xte, Xc[f])
        cov["nn_dist_scaled"][f"hf_train_to_fid{f}"] = dict(
            mean=float(dh.mean()), max=float(dh.max()))
        cov["nn_dist_scaled"][f"test_to_fid{f}"] = dict(
            mean=float(dt.mean()), max=float(dt.max()),
            frac_exact=float((dt < 1e-9).mean()))
    res["condition_coverage"] = cov

    # ---- cross-level shape consistency ----
    cons = {}
    for s, t in combinations(fids, 2):
        d, j = nn(Xc[t], Xc[s])
        src = _to_grid(fld[s][j], hw[s], hw[t])
        tgt = fld[t].reshape(-1, *hw[t])
        a = (src * tgt).sum((1, 2)) / np.maximum((src * src).sum((1, 2)), 1e-300)
        ny = np.linalg.norm(tgt.reshape(len(tgt), -1), axis=1)
        rel_raw = np.linalg.norm((src - tgt).reshape(len(tgt), -1), axis=1) / ny
        rel_g = np.linalg.norm((a[:, None, None] * src - tgt).reshape(len(tgt), -1),
                               axis=1) / ny
        r = np.array([np.corrcoef(src[i].ravel(), tgt[i].ravel())[0, 1]
                      for i in range(len(tgt))])
        cons[f"{s}->{t}"] = dict(n=int(len(tgt)), nn_cond_dist_mean=float(d.mean()),
                                 rel_l2_raw=float(rel_raw.mean()),
                                 rel_l2_after_optimal_gain=float(rel_g.mean()),
                                 optimal_gain_mean=float(a.mean()),
                                 pearson_r_mean=float(r.mean()),
                                 pearson_r_min=float(r.min()))
    res["cross_level_consistency"] = cons

    # ---- training-free matched-level predictor on the test split ----
    Yte = te["field_by_fid"][HF].astype(np.float64)
    hfhw = hw[HF]
    ceil = {}
    for f in fids:
        _, j5 = nn(Xc[HF], Xc[f])
        s5 = _to_grid(fld[f][j5], hw[f], hfhw).reshape(len(j5), -1)
        y5 = fld[HF].reshape(len(j5), -1)
        g = float(np.median((s5 * y5).sum(1) / np.maximum((s5 * s5).sum(1), 1e-300)))
        _, jt = nn(Xte, Xc[f])
        base = _to_grid(fld[f][jt], hw[f], hfhw).reshape(len(jt), -1)
        m = float(nrmse_mod.nrmse(g * base, Yte))
        rec = dict(calib_gain_from_hf_train=g, nRMSE_calibrated=m,
                   nRMSE_uncalibrated=float(nrmse_mod.nrmse(base, Yte)))
        if args.paper_bar:
            rec["skill_vs_paper_bar"] = m / args.paper_bar
        ceil[str(f)] = rec
    ceil["_zero_predictor"] = dict(nRMSE=float(nrmse_mod.nrmse(np.zeros_like(Yte), Yte)))
    ceil["_hf_train_mean_predictor"] = dict(nRMSE=float(nrmse_mod.nrmse(
        np.tile(fld[HF].mean(0), (len(Yte), 1)), Yte)))
    res["matched_level_predictor_on_test"] = ceil

    txt = json.dumps(res, indent=1)
    print(txt)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(txt + "\n")
        print(f"[wrote] {args.out}")


if __name__ == "__main__":
    main()
