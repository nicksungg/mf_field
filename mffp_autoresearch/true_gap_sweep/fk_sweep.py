#!/usr/bin/env python
"""true_gap_sweep Task 1: fisher_kpp_2d solve-time sweep (MEASUREMENT ONLY).

Sweeps output_time T with the CURRENT production recipe (ic_modes=5,
D_range [1e-4, 1e-3], r_range [5, 20], domain_size 1.0, ladder 32/64/128).
Per T cell it measures, on a fixed batch of specs drawn once with the
production sampler:
  (a) canonical fidelity gap: rel-L2 of (HF - spectral_interp(LF -> HF)),
      median over the batch, for LF in {32, 64};
  (b) predictability horizon: re-solve the first N_DIV samples at HF with the
      HF initial condition perturbed by ~1e-6 relative noise, record the
      relative divergence at T;
  (c) front-structure sanity: p95 of |grad u| on the HF field, plus mean/std
      (saturation to u=1 shows up as mean -> 1, grad_p95 -> 0).

Writes one JSON per (tag, T) cell under --out_dir.
Nothing outside --out_dir is touched; no package code or config is modified.
"""
from __future__ import annotations

import argparse
import json
import os
import time

import numpy as np

from mffp_sharp.pdes import fisher_kpp
from mffp_sharp.common import ic_encoding
from mffp_sharp.common.spectral import spectral_interp

RESOLUTIONS = [32, 64, 128]
HF = 128
SEED = 42          # production seed (configs/sample.yaml)
DIV_EPS = 1e-6

PROD_SAMPLING = {
    "D_range": [1.0e-4, 1.0e-3],
    "r_range": [5.0, 20.0],
    "domain_size": 1.0,
    "ic_modes": 5,
}


def rel_l2(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(a - b) / np.linalg.norm(b))


def grad_p95(u: np.ndarray, h: float) -> float:
    gx, gy = np.gradient(u, h)
    return float(np.percentile(np.sqrt(gx * gx + gy * gy), 95))


def hf_ic(spec: dict) -> np.ndarray:
    """Reproduce generate_sample's HF initial condition exactly."""
    m2d = int(spec.get("ic_modes", 3))
    coeffs = ic_encoding.coeffs_from_spec(spec, 2, m2d)
    ic_coarse = 0.5 + ic_encoding.build_ic(coeffs, min(RESOLUTIONS), 0.5, 2)
    return spectral_interp(ic_coarse, HF)


def run_cell(T: float, specs: list[dict], n_div: int) -> dict:
    rows = []
    t0 = time.time()
    for i, spec in enumerate(specs):
        fields, _, _ = fisher_kpp.generate_sample(spec, RESOLUTIONS, HF, T)
        hf = fields[HF]
        row = {
            "sample": i,
            "D": float(spec["D"]),
            "r": float(spec["r"]),
            "gap_rel_l2_lf32": rel_l2(spectral_interp(fields[32], HF), hf),
            "gap_rel_l2_lf64": rel_l2(spectral_interp(fields[64], HF), hf),
            "grad_p95_hf": grad_p95(hf, spec["domain_size"] / HF),
            "hf_mean": float(hf.mean()),
            "hf_std": float(hf.std()),
        }
        if i < n_div:
            u0 = hf_ic(spec)
            rng = np.random.default_rng(10_000 + i)
            scale = DIV_EPS * float(np.sqrt(np.mean(u0 * u0)))
            u0p = u0 + scale * rng.standard_normal(u0.shape)
            u_pert = fisher_kpp._solve(u0p, spec["D"], spec["r"],
                                       spec["domain_size"], T)
            row["divergence_rel_l2"] = rel_l2(u_pert, hf)
        rows.append(row)
    gaps32 = [r["gap_rel_l2_lf32"] for r in rows]
    gaps64 = [r["gap_rel_l2_lf64"] for r in rows]
    divs = [r["divergence_rel_l2"] for r in rows if "divergence_rel_l2" in r]
    return {
        "dataset": "fisher_kpp_2d",
        "T": T,
        "n_samples": len(specs),
        "ladder": RESOLUTIONS,
        "hf_res": HF,
        "measure": "canonical rel-L2 of (HF - spectral_interp(LF->HF))",
        "gap_lf32_median": float(np.median(gaps32)),
        "gap_lf32_min": float(np.min(gaps32)),
        "gap_lf32_max": float(np.max(gaps32)),
        "gap_lf64_median": float(np.median(gaps64)),
        "divergence_median": float(np.median(divs)) if divs else None,
        "divergence_max": float(np.max(divs)) if divs else None,
        "grad_p95_median": float(np.median([r["grad_p95_hf"] for r in rows])),
        "hf_mean_median": float(np.median([r["hf_mean"] for r in rows])),
        "hf_std_median": float(np.median([r["hf_std"] for r in rows])),
        "wall_s": round(time.time() - t0, 1),
        "rows": rows,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--T", required=True,
                    help="comma-separated output times, e.g. 0.3,0.6,1.0")
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--n_div", type=int, default=3)
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--tag", default="prod")
    ap.add_argument("--d_range", default=None,
                    help="override D_range, e.g. 3e-5,3e-4 (D-leg sweep)")
    args = ap.parse_args()

    sampling = dict(PROD_SAMPLING)
    if args.d_range:
        lo, hi = (float(x) for x in args.d_range.split(","))
        sampling["D_range"] = [lo, hi]
    specs = fisher_kpp.sample_configs(args.n, sampling, 2, SEED)

    os.makedirs(args.out_dir, exist_ok=True)
    for T in (float(x) for x in args.T.split(",")):
        cell = run_cell(T, specs, args.n_div)
        cell["tag"] = args.tag
        cell["sampling"] = sampling
        path = os.path.join(args.out_dir,
                            f"fk_{args.tag}_T{T:g}.json")
        with open(path, "w") as f:
            json.dump(cell, f, indent=2)
        print(f"[fk {args.tag}] T={T:g}  gap32={cell['gap_lf32_median']:.3e}  "
              f"gap64={cell['gap_lf64_median']:.3e}  "
              f"div={cell['divergence_median']:.3e}  "
              f"grad_p95={cell['grad_p95_median']:.2f}  "
              f"mean={cell['hf_mean_median']:.3f}  ({cell['wall_s']}s)",
              flush=True)


if __name__ == "__main__":
    main()
