#!/usr/bin/env python
"""Decompose a field predictor's test error into AMPLITUDE vs STRUCTURE.

Provenance: promoted from `s1_poisson-B1` mechanism analysis turn 2
(`worktrees/s1_poisson/B1/scratchpad/reanalysis_turn_2.py`). There it showed
that ~75 % of the 4-level ladder arms' squared error was per-sample amplitude
error and that a per-sample oracle gain closed 88 % of the headline
allpairs-vs-two_level gap (2.04x -> 1.13x) — i.e. the arms differed in
calibration, not in learned structure.

WHAT IT MEASURES, per prediction file:
  nRMSE                        the round's metric (eval/nrmse.py), recomputed
  frac_sq_error_from_gain      share of squared error explained by a per-sample
                               scalar gain error (p_i = a_i y_i + r_i, r_i _|_ y_i)
  nRMSE_after_per_sample_gain  nRMSE if every sample were rescaled by its own
                               oracle gain -> the STRUCTURE-only error
  nRMSE_after_global_gain      nRMSE after one oracle scalar for the whole set
                               (separates a constant bias from per-sample spread)
  var_ratio_pred_over_target   across-sample variance retained = how much of the
                               condition-dependent signal survived (1.0 ideal,
                               << 1 = collapsed toward the mean field)
  nRMSE_centered               nRMSE of the mean-removed fields
  band_rel_err[]               radial-band relative error (default 6 bands)
  target_energy_share[]        where the target's energy actually lives
  pearson_r_mean / _min        per-sample shape agreement

Two models are directly comparable when run on the same target array; pass
several files and the tool prints a comparison block.

USAGE
  python tools/field_error_decomposition.py \
      --pred_npz <a.npz> [<b.npz> ...] [--labels a b] \
      [--pred_key pred --target_key target] [--grid 64 64] [--bands 6] \
      [--out results.json]

The npz must hold 2-D (N, n_cells) prediction and target arrays (the layout
`smoke_eval.py` writes to `preds_test.npz`). `--grid` is needed only if the
file has no `work_grid` entry and n_cells is not a perfect square.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np


def _repo_root() -> Path:
    out = subprocess.run(["git", "rev-parse", "--show-toplevel"], check=True,
                         capture_output=True, text=True,
                         cwd=Path(__file__).resolve().parent)
    return Path(out.stdout.strip())


sys.path.insert(0, str(_repo_root() / "mffp_autoresearch" / "round1" / "eval"))
import nrmse as nrmse_mod  # noqa: E402


def radial_bands(F2: np.ndarray, nb: int):
    """Sum a (N, H, W_r) rfft2 power array into `nb` radial bands."""
    _, H, W = F2.shape
    ky = np.fft.fftfreq(H) * H
    kx = np.arange(W)
    KR = np.sqrt(ky[:, None] ** 2 + kx[None, :] ** 2)
    edges = np.linspace(0.0, H / 2.0, nb + 1)
    out = []
    for i in range(nb):
        m = (KR >= edges[i]) & (KR < edges[i + 1]) if i < nb - 1 else (KR >= edges[i])
        out.append(F2[:, m].sum(1))
    return np.stack(out, 1), edges


def decompose(pred: np.ndarray, target: np.ndarray, grid, bands: int) -> dict:
    p = np.asarray(pred, dtype=np.float64)
    y = np.asarray(target, dtype=np.float64)
    if p.shape != y.shape or p.ndim != 2:
        raise ValueError(f"need matching 2-D arrays, got {p.shape} vs {y.shape}")
    n = nrmse_mod.nrmse(p, y)
    a = (p * y).sum(1) / np.maximum((y * y).sum(1), 1e-300)     # y-projection gain
    b = (p * y).sum(1) / np.maximum((p * p).sum(1), 1e-300)     # oracle rescale of p
    err2 = ((p - y) ** 2).sum(1)
    gain2 = (a - 1.0) ** 2 * (y * y).sum(1)
    g = float((p * y).sum() / max((p * p).sum(), 1e-300))
    pc, yc = p - p.mean(0), y - y.mean(0)
    corr = np.array([np.corrcoef(p[i], y[i])[0, 1] for i in range(len(y))])
    rec = dict(
        n_samples=int(len(y)), n_cells=int(p.shape[1]),
        nRMSE=float(n),
        pred_rms=float(np.sqrt((p ** 2).mean())),
        target_rms=float(np.sqrt((y ** 2).mean())),
        proj_gain_mean=float(a.mean()), proj_gain_std=float(a.std()),
        frac_sq_error_from_gain=float(gain2.sum() / max(err2.sum(), 1e-300)),
        nRMSE_after_per_sample_gain=float(nrmse_mod.nrmse(b[:, None] * p, y)),
        oracle_global_gain=g,
        nRMSE_after_global_gain=float(nrmse_mod.nrmse(g * p, y)),
        var_ratio_pred_over_target=float((pc ** 2).mean() / max((yc ** 2).mean(), 1e-300)),
        nRMSE_centered=float(np.mean(np.linalg.norm(pc - yc, axis=1)
                                     / np.linalg.norm(yc, axis=1))),
        pearson_r_mean=float(corr.mean()), pearson_r_min=float(corr.min()),
    )
    if grid is not None:
        H, W = grid
        Yf = np.abs(np.fft.rfft2(y.reshape(-1, H, W))) ** 2
        Ef = np.abs(np.fft.rfft2((p - y).reshape(-1, H, W))) ** 2
        Pf = np.abs(np.fft.rfft2(p.reshape(-1, H, W))) ** 2
        yb, edges = radial_bands(Yf, bands)
        eb, _ = radial_bands(Ef, bands)
        pb, _ = radial_bands(Pf, bands)
        rec["band_edges_k"] = edges.tolist()
        rec["target_energy_share"] = (yb.sum(0) / yb.sum()).tolist()
        rec["band_rel_err"] = np.sqrt(eb.sum(0) / np.maximum(yb.sum(0), 1e-300)).tolist()
        rec["pred_over_target_band_energy"] = (
            pb.sum(0) / np.maximum(yb.sum(0), 1e-300)).tolist()
    return rec


def load(path: Path, pred_key: str, target_key: str, grid_arg):
    z = np.load(path)
    p, y = z[pred_key], z[target_key]
    grid = None
    if grid_arg:
        grid = (int(grid_arg[0]), int(grid_arg[1]))
    elif "work_grid" in z:
        grid = tuple(int(v) for v in z["work_grid"])
    else:
        s = int(round(np.sqrt(p.shape[1])))
        if s * s == p.shape[1]:
            grid = (s, s)
    return p, y, grid


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--pred_npz", nargs="+", required=True)
    ap.add_argument("--labels", nargs="*", default=None)
    ap.add_argument("--pred_key", default="pred")
    ap.add_argument("--target_key", default="target")
    ap.add_argument("--grid", nargs=2, type=int, default=None)
    ap.add_argument("--bands", type=int, default=6)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    labels = args.labels or [Path(f).parent.name or Path(f).stem
                             for f in args.pred_npz]
    if len(labels) != len(args.pred_npz):
        raise SystemExit("--labels must match --pred_npz in length")

    res = {"nrmse_def_hash": nrmse_mod.NRMSE_DEF_HASH, "per_file": {}}
    for lab, f in zip(labels, args.pred_npz):
        p, y, grid = load(Path(f), args.pred_key, args.target_key, args.grid)
        rec = decompose(p, y, grid, args.bands)
        rec["path"] = str(f)
        res["per_file"][lab] = rec

    if len(labels) > 1:
        ref = labels[0]
        res["comparison_vs_" + ref] = {
            lab: dict(
                nRMSE_ratio=res["per_file"][lab]["nRMSE"] / res["per_file"][ref]["nRMSE"],
                structure_only_nRMSE_ratio=(
                    res["per_file"][lab]["nRMSE_after_per_sample_gain"]
                    / res["per_file"][ref]["nRMSE_after_per_sample_gain"]),
                var_ratio_delta=(res["per_file"][lab]["var_ratio_pred_over_target"]
                                 - res["per_file"][ref]["var_ratio_pred_over_target"]),
            ) for lab in labels[1:]}

    txt = json.dumps(res, indent=1)
    print(txt)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(txt + "\n")
        print(f"[wrote] {args.out}")


if __name__ == "__main__":
    main()
