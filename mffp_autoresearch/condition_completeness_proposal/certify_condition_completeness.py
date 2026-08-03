#!/usr/bin/env python
"""Condition-completeness certificate for the sharp panel datasets.

Two training-free tests, run per dataset:

1. NEAREST-PAIR WITNESS (works on any npz dataset, no generator needed).
   Standardize the condition vectors per dim over the train split, find the
   closest pair, and report the relative field difference between the two
   samples. If two samples sitting at ~0 standardized condition distance have an
   O(1) relative field difference, the condition vector does NOT determine the
   field: some driver of the solution is absent from it. This is the measurement
   ADR r2-0003 made by hand; here it runs for every dataset from one entry point.

2. RECONSTRUCTION CERTIFICATE (decisive, needs the generator).
   Rebuild the initial condition from the stored condition vector alone, re-solve,
   and compare to the on-disk field. A rel-L2 at solver precision PROVES
   completeness — the field is a deterministic function of x, so any "the
   condition vector cannot reach this" reading is a statement about
   identifiability at the given row count and condition dimension, not about
   missing information. A control run (right physics, another sample's IC
   coefficients) shows what an actually-missing driver looks like.

Only `cahn_hilliard` currently admits test 2, because it is the one panel dataset
generated through `generate_learnable.py`, which draws the IC FROM the condition
vector. pfc / fisher_kpp / allen_cahn went through the `mffp_sharp` package path,
which draws a fresh white-noise IC from a per-sample seed that is never exported —
so for them there is nothing to reconstruct from, which is the finding.

    python certify_condition_completeness.py [--root <benchmark dir>] [--out results.json]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

# generate_learnable.py constants for the IC-encoded datasets (M2D=3 -> 8 modes -> 16 coeffs)
M2D = 3
CH_RECIPE = dict(scale=0.1, dt=2.5e-4, output_time=5.0, domain_size=1.0)

PANEL_SHARP = ["cahn_hilliard", "phase_field_crystal_2d", "fisher_kpp_2d", "allen_cahn_2d"]


# ----------------------------------------------------------------- test 1
def nearest_pair_witness(x: np.ndarray, y: np.ndarray) -> dict:
    """Closest pair in standardized condition space vs their relative field difference."""
    mu, sd = x.mean(0), x.std(0)
    sd = np.where(sd > 0, sd, 1.0)
    z = (x - mu) / sd
    # full pairwise distance (N ~ 400, cheap)
    d2 = ((z[:, None, :] - z[None, :, :]) ** 2).sum(-1)
    np.fill_diagonal(d2, np.inf)
    i, j = np.unravel_index(np.argmin(d2), d2.shape)
    dist = float(np.sqrt(d2[i, j]))
    scale = 0.5 * (np.linalg.norm(y[i]) + np.linalg.norm(y[j]))
    rel = float(np.linalg.norm(y[i] - y[j]) / scale)
    return {"closest_pair": [int(i), int(j)],
            "standardized_condition_distance": dist,
            "relative_field_difference": rel,
            "median_pair_distance": float(np.sqrt(np.median(d2[np.isfinite(d2)])))}


# ----------------------------------------------------------------- test 2
def ic_2d(coeffs: np.ndarray, res: int, scale: float) -> np.ndarray:
    """Band-limited IC built from the stored ic_c* coefficients (generate_learnable.ic_2d)."""
    xs = 2 * np.pi * np.arange(res) / res
    X, Y = np.meshgrid(xs, xs, indexing="ij")
    modes = [(a, b) for a in range(M2D) for b in range(M2D) if not (a == 0 and b == 0)]
    f = np.zeros((res, res))
    for idx, (kx, ky) in enumerate(modes):
        f += coeffs[2 * idx] * np.cos(kx * X + ky * Y) + coeffs[2 * idx + 1] * np.sin(kx * X + ky * Y)
    return f / (np.max(np.abs(f)) + 1e-12) * scale


def ch_solve(c0, eps, mobility, domain_size, output_time, dt):
    """Semi-implicit Fourier Cahn-Hilliard (mffp_sharp.pdes.cahn_hilliard._solve)."""
    res = c0.shape[0]
    h = domain_size / res
    cx = np.cos(2 * np.pi * np.fft.fftfreq(res))
    MX, MY = np.meshgrid(cx, cx, indexing="ij")
    mlap = (2.0 / h ** 2) * (2.0 - MX - MY)
    nsteps = int(np.ceil(output_time / dt))
    dt = output_time / nsteps
    denom = 1.0 / dt + mobility * eps ** 2 * mlap ** 2
    c = c0.astype(np.float64).copy()
    for _ in range(nsteps):
        ch = np.fft.fft2(c)
        rhs = ch * (1.0 / dt + mobility * mlap) - mobility * mlap * np.fft.fft2(c ** 3)
        c = np.real(np.fft.ifft2(rhs / denom))
    return c


def ch_reconstruction_certificate(x: np.ndarray, y: np.ndarray, res: int, n: int = 3) -> dict:
    """Re-solve cahn_hilliard from the condition vector alone; compare to the on-disk field."""
    rels = []
    for i in range(n):
        eps, mob, mean = x[i, 0], x[i, 1], x[i, 2]
        u0 = ic_2d(x[i, 3:], res, CH_RECIPE["scale"]) + mean
        pred = ch_solve(u0, eps, mob, CH_RECIPE["domain_size"],
                        CH_RECIPE["output_time"], CH_RECIPE["dt"])
        truth = y[i].reshape(res, res)
        rels.append(float(np.linalg.norm(pred - truth) / np.linalg.norm(truth)))
    # control: sample 0's physics with sample 1's IC coefficients
    u0 = ic_2d(x[1, 3:], res, CH_RECIPE["scale"]) + x[0, 2]
    pred = ch_solve(u0, x[0, 0], x[0, 1], CH_RECIPE["domain_size"],
                    CH_RECIPE["output_time"], CH_RECIPE["dt"])
    truth = y[0].reshape(res, res)
    ctrl = float(np.linalg.norm(pred - truth) / np.linalg.norm(truth))
    return {"n_samples": n, "rel_L2_per_sample": rels, "rel_L2_max": max(rels),
            "control_wrong_ic_rel_L2": ctrl,
            "verdict": "COMPLETE" if max(rels) < 1e-9 else "NOT_REPRODUCED"}


# ----------------------------------------------------------------- driver
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="/Users/nicholassung/Documents/mf_field/benchmark_42/sharp")
    ap.add_argument("--out", default=str(Path(__file__).with_name("certificate_results.json")))
    ap.add_argument("--level", default="l1", help="ladder level to read (l1 = coarsest)")
    a = ap.parse_args()

    root = Path(a.root)
    out = {"_protocol": "nearest-pair witness (all) + reconstruction certificate (IC-encoded only)",
           "_level": a.level, "datasets": {}}

    for name in PANEL_SHARP:
        meta = json.load(open(root / name / "meta.json"))
        d = np.load(root / name / f"train_{a.level}.npz")
        x, y = d["x"], d["y"]
        res = int(round(np.sqrt(y.shape[1])))
        names = meta["param_names"]
        ic_dims = [n for n in names if n.startswith("ic_")]
        rec = {
            "n_params": len(names),
            "param_names": names if len(names) <= 6 else names[:3] + ["…", names[-1]],
            "ic_parameters_exported": len(ic_dims),
            "generator_path": "mffp_sharp package (generate.py)" if "module" in meta
                              else "generate_learnable.py (IC-encoded)",
            "witness": nearest_pair_witness(x, y),
        }
        if ic_dims and name == "cahn_hilliard":
            print(f"[{name}] running reconstruction certificate at {res}² "
                  f"(~{CH_RECIPE['output_time'] / CH_RECIPE['dt']:.0f} steps/sample)…", flush=True)
            rec["reconstruction"] = ch_reconstruction_certificate(x, y, res)
        else:
            rec["reconstruction"] = {
                "verdict": "NOT_POSSIBLE",
                "reason": "no IC parameters in the condition vector — the realised IC is a "
                          "white-noise field drawn from an unexported per-sample seed",
            }
        w = rec["witness"]
        rec["verdict"] = (
            "COMPLETE (reconstructs from x at solver precision)"
            if rec["reconstruction"]["verdict"] == "COMPLETE"
            else "INCOMPLETE (near-identical conditions, O(1) different fields)"
            if w["relative_field_difference"] > 0.1 and w["standardized_condition_distance"] < 0.5
            else "UNDECIDED by these tests")
        out["datasets"][name] = rec
        print(f"{name:26s} ic_params={len(ic_dims):2d}  closest pair d={w['standardized_condition_distance']:.4f} "
              f"-> rel field diff {w['relative_field_difference']:.3f}   {rec['verdict']}")

    Path(a.out).write_text(json.dumps(out, indent=2) + "\n")
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
