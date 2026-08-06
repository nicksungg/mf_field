#!/usr/bin/env python
"""true_gap_sweep Task 2: phase_field_crystal_2d structural audit (MEASUREMENT ONLY).

pfc's NO_GAP (8.3e-6 shipped, 1.2e-6 sample round) predates the IC repair and
is structural: the pseudo-spectral solver is near-exact at shared modes, and
part of the sampled (r, psi_bar) range sits in the uniform phase.
This audit measures two levers without touching any shipped surface:

  (a) gap vs LF resolution: LF in {8, 16, 32, 64} against HF=128 at the
      production recipe (T=200, domain 32 -> lattice wavelength 2*pi, so
      points-per-wavelength = 0.196 * res: 1.6 @8 (below Nyquist), 3.1 @16,
      6.3 @32, 12.6 @64);
  (b) crystalline-only restriction: per-sample linear-instability parameter
      sigma = -(r + 3*psi_bar^2) (uniform state unstable at k=1 iff sigma > 0)
      plus empirical pattern amplitude std(HF), aggregated over crystalline
      samples only; plus a dedicated batch drawn from a restricted
      all-crystalline (r, psi_bar) box.

The IC is built on min(resolutions); the script verifies that building on 8
vs the production 32 yields the same continuous IC (band-limited, m=3 < 4 =
Nyquist index of res 8) so adding low rungs does not change the experiment.

Writes JSON cells under --out_dir. Nothing outside --out_dir is touched.
"""
from __future__ import annotations

import argparse
import json
import os
import time

import numpy as np

from mffp_sharp.pdes import phase_field_crystal as pfc
from mffp_sharp.common import ic_encoding
from mffp_sharp.common.spectral import spectral_interp

HF = 128
LF_LIST = [8, 16, 32, 64]
T = 200.0
SEED = 42

PROD_SAMPLING = {
    "r_range": [-0.4, -0.1],
    "mean_density_range": [-0.4, -0.2],
    "ic_amplitude": 0.05,
    "domain_size": 32.0,
}
# All-crystalline box: sigma = -(r + 3*psi_bar^2) >= 0.11 over the whole box.
CRYST_SAMPLING = {
    "r_range": [-0.4, -0.3],
    "mean_density_range": [-0.25, -0.2],
    "ic_amplitude": 0.05,
    "domain_size": 32.0,
}


def rel_l2(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(a - b) / np.linalg.norm(b))


def ic_consistency_check(spec: dict) -> float:
    """Max |IC built on 8 -> 128  minus  IC built on 32 -> 128|."""
    coeffs = ic_encoding.coeffs_from_spec(spec, 2)
    a = spectral_interp(spec["mean_density"]
                        + ic_encoding.build_ic(coeffs, 8, spec["ic_amplitude"], 2), HF)
    b = spectral_interp(spec["mean_density"]
                        + ic_encoding.build_ic(coeffs, 32, spec["ic_amplitude"], 2), HF)
    return float(np.max(np.abs(a - b)))


def run_batch(tag: str, sampling: dict, n: int, out_dir: str) -> dict:
    specs = pfc.sample_configs(n, sampling, 2, SEED)
    ic_dev = ic_consistency_check(specs[0])
    rows = []
    t0 = time.time()
    for i, spec in enumerate(specs):
        fields, _, _ = pfc.generate_sample(spec, LF_LIST + [HF], HF, T)
        hf = fields[HF]
        sigma = -(spec["r"] + 3.0 * spec["mean_density"] ** 2)
        row = {
            "sample": i,
            "r": float(spec["r"]),
            "psi_bar": float(spec["mean_density"]),
            "sigma_lin_instability": float(sigma),
            "hf_std": float(hf.std()),
            "crystalline_empirical": bool(hf.std() > 0.01),
        }
        for lf in LF_LIST:
            f_lf = fields[lf]
            if np.isfinite(f_lf).all():
                row[f"gap_rel_l2_lf{lf}"] = rel_l2(spectral_interp(f_lf, HF), hf)
            else:
                row[f"gap_rel_l2_lf{lf}"] = None   # LF solve blew up (NaN/inf)
        rows.append(row)
        print(f"  [{tag}] sample {i}: sigma={sigma:+.3f} std={row['hf_std']:.4f} "
              + " ".join(
                  f"g{lf}=BLOWUP" if row[f"gap_rel_l2_lf{lf}"] is None
                  else f"g{lf}={row[f'gap_rel_l2_lf{lf}']:.2e}"
                  for lf in LF_LIST),
              flush=True)

    def agg(sel_rows: list[dict]) -> dict:
        if not sel_rows:
            return {"n": 0}
        out = {"n": len(sel_rows)}
        for lf in LF_LIST:
            g = [r[f"gap_rel_l2_lf{lf}"] for r in sel_rows
                 if r[f"gap_rel_l2_lf{lf}"] is not None]
            out[f"gap_lf{lf}_n_blowup"] = len(sel_rows) - len(g)
            out[f"gap_lf{lf}_median"] = float(np.median(g)) if g else None
            out[f"gap_lf{lf}_max"] = float(np.max(g)) if g else None
        return out

    cryst = [r for r in rows if r["crystalline_empirical"]]
    cell = {
        "dataset": "phase_field_crystal_2d",
        "tag": tag,
        "T": T,
        "hf_res": HF,
        "lf_list": LF_LIST,
        "sampling": sampling,
        "measure": "canonical rel-L2 of (HF - spectral_interp(LF->HF))",
        "ic_build_res_consistency_maxabs": ic_dev,
        "points_per_lattice_wavelength": {
            str(res): round(2 * np.pi * res / sampling["domain_size"], 2)
            for res in LF_LIST + [HF]},
        "all_samples": agg(rows),
        "crystalline_only": agg(cryst),
        "n_crystalline": len(cryst),
        "wall_s": round(time.time() - t0, 1),
        "rows": rows,
    }
    path = os.path.join(out_dir, f"pfc_{tag}.json")
    with open(path, "w") as f:
        json.dump(cell, f, indent=2)
    def fmt(v):
        return "BLOWUP" if v is None else f"{v:.2e}"
    print(f"[pfc {tag}] n={n} cryst={len(cryst)} "
          + " ".join(f"g{lf}={fmt(cell['all_samples'][f'gap_lf{lf}_median'])}"
                     for lf in LF_LIST)
          + f"  ({cell['wall_s']}s)", flush=True)
    return cell


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out_dir", required=True)
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--batch", choices=["prod", "cryst", "both"], default="both")
    args = ap.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)
    if args.batch in ("prod", "both"):
        run_batch("prod", PROD_SAMPLING, args.n, args.out_dir)
    if args.batch in ("cryst", "both"):
        run_batch("cryst", CRYST_SAMPLING, args.n, args.out_dir)


if __name__ == "__main__":
    main()
