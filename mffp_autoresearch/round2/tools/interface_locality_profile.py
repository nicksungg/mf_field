#!/usr/bin/env python
"""Is a predictor's error INTERFACE-LOCAL or BULK? Error binned by |grad HF|.

Provenance: promoted from `s1_poisson-B2` mechanism analysis turn 2
(`worktrees/s1_poisson/B2/scratchpad/reanalysis_turn_2.py`). There it overturned
the default assumption for the stream: on `ifc_poisson` every trained arm's
relative error is LARGEST in the smoothest decile of |grad HF| and falls
monotonically toward the steepest (`allpairs__per_level` 0.0569 -> 0.0232,
`two_level__per_level` 0.1812 -> 0.0509), i.e. the failure is in the smooth bulk
and interface-aware losses / local branches are the wrong lever there.

Round 1's mechanism claims lean heavily on "the error is concentrated in thin
sharp regions" (the whole rel-L2-hides-blur argument, CLAUDE.md's metric-panel
rule). That claim is measurable in one pass and is often false. This is the
SPATIAL complement to `tools/field_error_decomposition.py`'s SPECTRAL bands:
bands say which wavenumbers, this says which pixels.

WHAT IT REPORTS, per prediction file
  error_by_grad_decile[10]     sqrt(sum e^2 / sum y^2) restricted to each decile
                               of |grad(HF target)| (decile 0 = smoothest)
  target_energy_by_decile[10]  where the target's energy actually lives, so a
                               big relative error on 2 % of the energy is not
                               mistaken for the dominant term
  locality_ratio               error_by_grad_decile[9] / [0]. > 1 = the error IS
                               interface-local (concentrated at steep gradients);
                               < 1 = BULK-dominated; ~1 = spatially flat
  monotone_increasing          whether the profile rises with gradient at all
  frac_sq_error_in_top_decile  share of total squared error in the steepest 10 %
                               of cells, next to that decile's energy share

Deciles are computed on the pooled |grad HF| of the whole test split so all
files (and all arms of one card) share identical bins. The gradient uses
`np.gradient` on the 2-D work grid — a proxy for interface proximity, not a
level-set distance; for a signed-distance version thin-band mask, threshold this
profile's top decile.

USAGE
  python tools/interface_locality_profile.py \
      --pred_npz <a.npz> [<b.npz> ...] [--labels a b] \
      [--pred_key pred --target_key target] [--grid 64 64] \
      [--deciles 10] [--out results.json] [--plot out.png]
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
import nrmse as nrmse_mod   # noqa: E402


def grad_bins(target: np.ndarray, grid, nb: int):
    n = len(target)
    H, W = grid
    Y = target.reshape(n, H, W)
    if H == 1 or W == 1:                       # 1-D signal laid out as a row
        g = np.abs(np.gradient(Y.reshape(n, -1), axis=1))
    else:
        gy = np.gradient(Y, axis=1)
        gx = np.gradient(Y, axis=2)
        g = np.sqrt(gy ** 2 + gx ** 2).reshape(n, -1)
    q = np.quantile(g, np.linspace(0, 1, nb + 1))
    binid = np.clip(np.searchsorted(q[1:-1], g, side="right"), 0, nb - 1)
    return binid, q


def profile(pred, target, binid, nb):
    p = np.asarray(pred, np.float64)
    y = np.asarray(target, np.float64)
    e2 = (p - y) ** 2
    y2 = y ** 2
    rel, esh, ysh = [], [], []
    for k in range(nb):
        m = binid == k
        rel.append(float(np.sqrt(e2[m].sum() / max(y2[m].sum(), 1e-300))))
        esh.append(float(e2[m].sum() / max(e2.sum(), 1e-300)))
        ysh.append(float(y2[m].sum() / max(y2.sum(), 1e-300)))
    lr = rel[-1] / max(rel[0], 1e-300)
    return dict(
        nRMSE=float(nrmse_mod.nrmse(p, y)),
        error_by_grad_decile=rel,
        sq_error_share_by_decile=esh,
        target_energy_by_decile=ysh,
        locality_ratio=float(lr),
        verdict=("INTERFACE-LOCAL" if lr > 1.25 else
                 "BULK-DOMINATED" if lr < 0.8 else "SPATIALLY FLAT"),
        monotone_increasing=bool(all(rel[i] <= rel[i + 1] for i in range(nb - 1))),
        monotone_decreasing=bool(all(rel[i] >= rel[i + 1] for i in range(nb - 1))),
        frac_sq_error_in_top_decile=esh[-1],
        target_energy_in_top_decile=ysh[-1],
    )


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--pred_npz", nargs="+", required=True)
    ap.add_argument("--labels", nargs="*", default=None)
    ap.add_argument("--pred_key", default="pred")
    ap.add_argument("--target_key", default="target")
    ap.add_argument("--grid", nargs=2, type=int, default=None)
    ap.add_argument("--deciles", type=int, default=10)
    ap.add_argument("--out", default=None)
    ap.add_argument("--plot", default=None)
    args = ap.parse_args()

    labels = args.labels or [Path(f).parent.name or Path(f).stem
                             for f in args.pred_npz]
    if len(labels) != len(args.pred_npz):
        raise SystemExit("--labels must match --pred_npz in length")

    res = {"nrmse_def_hash": nrmse_mod.NRMSE_DEF_HASH,
           "n_deciles": args.deciles, "per_file": {}}
    binid = grid = None
    target = None
    for lab, f in zip(labels, args.pred_npz):
        z = np.load(f)
        p, y = z[args.pred_key], np.asarray(z[args.target_key], np.float64)
        if args.grid:
            g = (int(args.grid[0]), int(args.grid[1]))
        elif "work_grid" in z:
            g = tuple(int(v) for v in z["work_grid"])
        else:
            s = int(round(np.sqrt(p.shape[1])))
            g = (s, s) if s * s == p.shape[1] else (1, p.shape[1])
        if target is None:
            target, grid = y, g
            binid, q = grad_bins(target, grid, args.deciles)
            res["work_grid"] = list(grid)
            res["grad_decile_edges"] = q.tolist()
        elif not np.array_equal(target, y):
            raise SystemExit(f"{lab}: target array differs from {labels[0]}'s; "
                             "the profiles would not be comparable")
        rec = profile(p, target, binid, args.deciles)
        rec["path"] = str(f)
        res["per_file"][lab] = rec

    if len(labels) > 1:
        ref = labels[0]
        res["ratio_vs_" + ref] = {
            lab: [res["per_file"][lab]["error_by_grad_decile"][k]
                  / max(res["per_file"][ref]["error_by_grad_decile"][k], 1e-300)
                  for k in range(args.deciles)] for lab in labels[1:]}

    txt = json.dumps(res, indent=1)
    print(txt)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(txt + "\n")
        print(f"[wrote] {args.out}")
    if args.plot:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
        for lab in labels:
            ax.plot(range(args.deciles),
                    res["per_file"][lab]["error_by_grad_decile"], "o-", label=lab)
        ax.plot(range(args.deciles), res["per_file"][labels[0]]["target_energy_by_decile"],
                "k--", alpha=.4, label="target energy share")
        ax.set_yscale("log"); ax.set_xlabel("|grad HF| decile (0 = smoothest)")
        ax.set_ylabel("relative error in decile"); ax.legend(fontsize=8)
        ax.set_title("interface-locality profile")
        fig.tight_layout(); fig.savefig(args.plot)
        print(f"[wrote] {args.plot}")


if __name__ == "__main__":
    main()
