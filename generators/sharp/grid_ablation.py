"""Mesh-convergence ablation for the eloise sharp-field PDE solvers.

For each dataset variant in sample.yaml: draw a few samples, solve on a dyadic
resolution sweep, and measure self-convergence (restrict the finer grid to the
coarser by block-mean, then relL2). The coarsest grid whose step-to-step change
is below tol is "resolved" -> HF candidate; two rungs below -> the LF ladder.

Writes grid_ablation_results.json + prints a table. Read-only on the repo.
"""
import json, time, sys
import numpy as np
import yaml
from mffp_sharp.pdes import (euler, cahn_hilliard, kuramoto_sivashinsky, allen_cahn,
    fisher_kpp, swift_hohenberg, kdv, nls, sine_gordon, gray_scott,
    phase_field_crystal, burgers, sod, shallow_water, helmholtz, porous_medium)

MODS = {m.__name__.split('.')[-1]: m for m in (euler, cahn_hilliard, kuramoto_sivashinsky,
    allen_cahn, fisher_kpp, swift_hohenberg, kdv, nls, sine_gordon, gray_scott,
    phase_field_crystal, burgers, sod, shallow_water, helmholtz, porous_medium)}

PYCLAW = {"euler", "burgers", "sod", "shallow_water"}

CFG = "/archive/mf_field_eloise_data/SURF_2026-main/mffp_sharp/configs/sample.yaml"

def restrict(fine, factor, ndim):
    """Block-mean restrict a fine field to a coarser grid by integer factor."""
    if ndim == 1:
        n = fine.shape[0] // factor
        return fine[:n * factor].reshape(n, factor).mean(1)
    n = fine.shape[0] // factor
    return fine[:n * factor, :n * factor].reshape(n, factor, n, factor).mean((1, 3))

def rel(a, b):
    return float(np.linalg.norm(a - b) / (np.linalg.norm(b) + 1e-30))

def sweep_for(ndim, module):
    # dyadic sweeps; cap the expensive PyClaw 2D solves
    if ndim == 1:
        return [64, 128, 256, 512]
    if module in PYCLAW:
        return [32, 64, 128, 256]
    return [32, 64, 128, 256]

def main():
    top = yaml.safe_load(open(CFG))
    nsamp = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    only = sys.argv[2] if len(sys.argv) > 2 else None
    results = {}
    for name, block in top["pdes"].items():
        if only and name != only:
            continue
        mod = MODS[block["module"]]
        ndim = int(block.get("ndim", 2))
        T = block["output_time"]
        res = sweep_for(ndim, block["module"])
        hf = res[-1]
        t0 = time.time()
        try:
            specs = mod.sample_configs(nsamp, block["sampling"], ndim, top["seed"])
            # accumulate per-pair convergence across samples
            pair_err = {f"{res[i]}->{res[i+1]}": [] for i in range(len(res) - 1)}
            sharp_cells = []   # for interface PDEs: estimate feature width in cells at HF
            for spec in specs:
                fields, cond, names = mod.generate_sample(spec, res, hf, T)
                for i in range(len(res) - 1):
                    lo, hiR = res[i], res[i + 1]
                    f_hi = fields[hiR]; f_lo = fields[lo]
                    rfac = hiR // lo
                    pair_err[f"{lo}->{hiR}"].append(rel(restrict(f_hi, rfac, ndim), f_lo))
            conv = {k: float(np.mean(v)) for k, v in pair_err.items()}
            # resolved grid = the finer grid of the first pair whose change < tol
            tol = 0.05
            resolved = hf
            for i in range(len(res) - 1):
                if conv[f"{res[i]}->{res[i+1]}"] < tol:
                    resolved = res[i + 1]
                    break
            results[name] = {"ndim": ndim, "module": block["module"], "sweep": res,
                             "convergence_relL2": conv, "resolved_grid": resolved,
                             "secs": round(time.time() - t0, 1)}
            print(f"[{name:22s}] ndim={ndim} sweep={res} conv={ {k:round(v,4) for k,v in conv.items()} } "
                  f"-> resolved~{resolved}  ({results[name]['secs']}s)", flush=True)
        except Exception as e:
            results[name] = {"error": f"{type(e).__name__}: {e}"}
            print(f"[{name:22s}] ERROR {type(e).__name__}: {e}", flush=True)
    base = "/archive/mf_field_eloise_data"
    if only:
        outp = f"{base}/ablation_{only}.json"          # per-variant (array task)
    else:
        outp = f"{base}/grid_ablation_results.json"     # combined (serial)
    json.dump(results, open(outp, "w"), indent=2)
    print("\nwrote", outp)

if __name__ == "__main__":
    main()
