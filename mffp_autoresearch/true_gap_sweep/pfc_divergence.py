#!/usr/bin/env python
"""true_gap_sweep Task 2 follow-up: pfc predictability-horizon check.

For crystalline-box samples, re-solve at HF with the HF initial condition
perturbed by ~1e-6 relative (rms-scaled) noise and record the relative
divergence at T=200. If divergence is comparable to the LF32-vs-HF gap
(~1e-2), the gap is chaotic decorrelation, not learnable structure.
MEASUREMENT ONLY; writes one JSON under --out_dir.
"""
from __future__ import annotations

import argparse
import json
import os

import numpy as np

from mffp_sharp.pdes import phase_field_crystal as pfc
from mffp_sharp.common import ic_encoding
from mffp_sharp.common.spectral import spectral_interp

HF = 128
T = 200.0
SEED = 42
DIV_EPS = 1e-6

CRYST_SAMPLING = {
    "r_range": [-0.4, -0.3],
    "mean_density_range": [-0.25, -0.2],
    "ic_amplitude": 0.05,
    "domain_size": 32.0,
}


def rel_l2(a, b):
    return float(np.linalg.norm(a - b) / np.linalg.norm(b))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--n", type=int, default=3)
    args = ap.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)

    specs = pfc.sample_configs(8, CRYST_SAMPLING, 2, SEED)[: args.n]
    rows = []
    for i, spec in enumerate(specs):
        coeffs = ic_encoding.coeffs_from_spec(spec, 2)
        ic32 = spec["mean_density"] + ic_encoding.build_ic(
            coeffs, 32, spec["ic_amplitude"], 2)
        u0 = spectral_interp(ic32, HF)
        base = pfc._solve(u0, spec["r"], spec["domain_size"], T)
        rng = np.random.default_rng(20_000 + i)
        scale = DIV_EPS * float(np.sqrt(np.mean(u0 * u0)))
        pert = pfc._solve(u0 + scale * rng.standard_normal(u0.shape),
                          spec["r"], spec["domain_size"], T)
        row = {"sample": i, "r": float(spec["r"]),
               "psi_bar": float(spec["mean_density"]),
               "divergence_rel_l2": rel_l2(pert, base)}
        rows.append(row)
        print(f"  [pfc div] sample {i}: r={row['r']:.3f} "
              f"psi={row['psi_bar']:.3f} div={row['divergence_rel_l2']:.3e}",
              flush=True)

    out = {"dataset": "phase_field_crystal_2d", "tag": "cryst_divergence",
           "T": T, "hf_res": HF, "eps": DIV_EPS,
           "sampling": CRYST_SAMPLING,
           "divergence_median": float(np.median(
               [r["divergence_rel_l2"] for r in rows])),
           "rows": rows}
    path = os.path.join(args.out_dir, "pfc_cryst_divergence.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"[pfc div] median={out['divergence_median']:.3e} -> {path}")


if __name__ == "__main__":
    main()
