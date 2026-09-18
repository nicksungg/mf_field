"""Standardized multi-fidelity dataset generator for the eloise sharp-field PDEs.

Emits the factory npz convention used by the mf_field models:
  <out>/<variant>_generated/{train,test}_l{k}.npz  with keys
    x : (N, d)  condition/parameter vector (SAME across fidelities -> aligned MF)
    y : (N, prod(grid_k))  flattened field at fidelity k
  + README.md  (paper, ladder, counts)

Ladder per variant = ablation-driven HF (grid where the sharp feature is resolved)
with 3 dyadic rungs [HF/4, HF/2, HF], clamped so the coarsest rung >= MIN_LF.
Sample size standardized to NTRAIN/NTEST across ALL datasets.

Usage:  python generate_standardized.py <variant> [--ntrain 400 --ntest 100]
"""
from __future__ import annotations
import argparse, json, os
import numpy as np
import yaml
from mffp_sharp.pdes import (euler, cahn_hilliard, kuramoto_sivashinsky, allen_cahn,
    fisher_kpp, swift_hohenberg, kdv, nls, sine_gordon, gray_scott,
    phase_field_crystal, burgers, sod, shallow_water, helmholtz, porous_medium)

MODS = {m.__name__.split('.')[-1]: m for m in (euler, cahn_hilliard, kuramoto_sivashinsky,
    allen_cahn, fisher_kpp, swift_hohenberg, kdv, nls, sine_gordon, gray_scott,
    phase_field_crystal, burgers, sod, shallow_water, helmholtz, porous_medium)}

ROOT = "/archive/mf_field_eloise_data"
CFG = f"{ROOT}/SURF_2026-main/mffp_sharp/configs/sample.yaml"
ABLATION = f"{ROOT}/grid_ablation_results.json"
OUT_ROOT = "/archive/mf_field/sharp_generated"
SEED = 42
MIN_LF = 16

# Per-PDE provenance for the README (matches DATASET_SUMMARY_FOR_MFFIELD.md / PDE_SOLVERS).
SOURCE = {
 "euler":"The Well (arXiv:2412.00568); Schulz-Rinne 1993","sod":"Sod 1978, JCP 27:1",
 "burgers":"APEBench (arXiv:2411.00180)","shallow_water":"PDEBench (arXiv:2210.07182)",
 "cahn_hilliard":"E-UNO (arXiv:2509.01293); Cahn-Hilliard 1958","allen_cahn":"APEBench (arXiv:2411.00180)",
 "porous_medium":"Vazquez 2007 (Barenblatt)","fisher_kpp":"Fisher 1937 / KPP 1937",
 "gray_scott":"The Well; Pearson 1993, Science 261:189","swift_hohenberg":"Swift & Hohenberg 1977",
 "phase_field_crystal":"Elder & Grant 2004","kuramoto_sivashinsky":"APEBench; Kuramoto-Tsuzuki 1976 / Sivashinsky 1977",
 "kdv":"APEBench (arXiv:2411.00180)","nls":"classical (split-step)","sine_gordon":"classical (Strang)",
 "helmholtz":"classical (sparse-direct BVP)",
}

def ladder_for(variant, block, ablation):
    ndim = int(block.get("ndim", 2))
    info = ablation.get(variant, {})
    hf = info.get("resolved_grid")
    if not hf:  # fallback if ablation missing/errored
        hf = 256 if ndim == 1 else 128
    rungs = [hf // 4, hf // 2, hf]
    rungs = [r for r in rungs if r >= MIN_LF] or [hf]
    return ndim, rungs

def merge_shards(args, block, ndim, rungs, out_dir):
    """Concatenate all shard files (in sample order) -> standard train/test npz + README."""
    import glob
    sh = sorted(glob.glob(os.path.join(out_dir, "shards", "shard_*.npz")))
    if not sh:
        raise SystemExit(f"no shards in {out_dir}/shards")
    parts = [np.load(f, allow_pickle=True) for f in sh]
    parts.sort(key=lambda d: int(d["lo"]))
    covered = sum(int(d["hi"]) - int(d["lo"]) for d in parts)
    N = args.ntrain + args.ntest
    X = np.concatenate([d["x"] for d in parts], axis=0)
    names = list(parts[0]["names"])
    print(f"[{args.variant}] merge: {len(parts)} shards, {covered} samples (need {N})", flush=True)
    assert X.shape[0] == N, f"shard coverage {X.shape[0]} != N {N} (gaps/overlap?)"
    nt = args.ntrain
    for k, r in enumerate(rungs, start=1):
        Yr = np.concatenate([d[f"y{k-1}"] for d in parts], axis=0)
        assert np.isfinite(Yr).all(), f"non-finite in level {k}"
        np.savez(os.path.join(out_dir, f"train_l{k}.npz"), x=X[:nt], y=Yr[:nt])
        np.savez(os.path.join(out_dir, f"test_l{k}.npz"),  x=X[nt:], y=Yr[nt:])
    grid_shape = [[r] if ndim == 1 else [r, r] for r in rungs]
    _write_meta_readme(args, block, ndim, rungs, grid_shape, names, out_dir)
    print(f"  -> merged into {out_dir}", flush=True)


def _write_meta_readme(args, block, ndim, rungs, grid_shape, names, out_dir):
    T = block["output_time"]
    meta = {"variant": args.variant, "module": block["module"], "ndim": ndim,
            "source": SOURCE.get(block["module"], "NA"), "output_time": T,
            "ladder": grid_shape, "param_names": list(names), "n_params": len(names),
            "ntrain": args.ntrain, "ntest": args.ntest, "seed": SEED}
    json.dump(meta, open(os.path.join(out_dir, "meta.json"), "w"), indent=2)
    with open(os.path.join(out_dir, "README.md"), "w") as f:
        f.write(f"# {args.variant}_generated\n\n"
                f"**PDE module:** {block['module']}  \n**Source:** {SOURCE.get(block['module'],'NA')}  \n"
                f"**ndim:** {ndim}  \n**Availability:** regenerable (eloise sharp-field solver)  \n\n"
                f"## Fidelity ladder (ablation-driven)\n\n"
                + "".join(f"- L{k}: {g}\n" for k, g in enumerate(grid_shape, 1))
                + f"\n## Inputs/outputs\n- `x`: (N,{len(names)}) condition vector "
                f"[{', '.join(names)}]\n- `y`: (N, prod(grid)) flattened field at each fidelity\n\n"
                f"## Sample counts\n- Train: **{args.ntrain}**  Test: **{args.ntest}**\n\n"
                f"## File layout\n`train_l1.npz`..`train_l{len(rungs)}.npz`, "
                f"`test_l1.npz`.. — MFRNP/factory npz convention (keys `x`,`y`).\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("variant")
    ap.add_argument("--ntrain", type=int, default=400)
    ap.add_argument("--ntest", type=int, default=100)
    ap.add_argument("--shard", nargs=2, type=int, default=None,
                    metavar=("LO", "HI"), help="generate only specs[LO:HI] -> a shard file")
    ap.add_argument("--merge", action="store_true",
                    help="merge all shard files for the variant into the standard npz")
    args = ap.parse_args()
    top = yaml.safe_load(open(CFG))
    per_variant = f"{ROOT}/ablation_{args.variant}.json"
    if os.path.exists(per_variant):
        ablation = json.load(open(per_variant))         # array-task per-variant result
    elif os.path.exists(ABLATION):
        ablation = json.load(open(ABLATION))            # combined serial result
    else:
        ablation = {}
    print(f"[{args.variant}] ablation source: "
          f"{'per-variant' if os.path.exists(per_variant) else ('combined' if os.path.exists(ABLATION) else 'DEFAULT fallback')}",
          flush=True)
    block = top["pdes"][args.variant]
    mod = MODS[block["module"]]
    T = block["output_time"]
    ndim, rungs = ladder_for(args.variant, block, ablation)

    # --- per-PDE numerical-stability overrides (eloise config dt is "TBD"/unvalidated) ---
    # kdv: integrating-factor RK4 is stiff on the tiny domain (L=2) + broadband random IC.
    # Cap HF and set a dispersive-CFL dt: dt <= safety / (delta_max^2 * k_eff^3).
    # euler / shallow_water resolve at 64 but 64^2 HF is too coarse to look sharp ->
    # bump to a [32,64,128] ladder (real LF/HF gap + visibly sharp shock/bore at HF).
    if args.variant in ("euler", "shallow_water_2d"):
        rungs = [32, 64, 128]
        print(f"[{args.variant}] HF bump -> ladder {rungs}", flush=True)
    if block["module"] == "kdv":
        rungs = [64, 128, 256]                                # cap HF at 256 (512 is too stiff)
        L = block["sampling"]["domain_size"]
        dmax = block["sampling"]["delta_range"][1]
        k_eff = (2.0 / 3.0) * np.pi * rungs[-1] / L          # 2/3-dealias cutoff wavenumber
        cfl_dt = float(min(1e-3, 0.2 / (dmax ** 2 * k_eff ** 3)))
        kdv._solve.__defaults__ = (cfl_dt,)                  # bind real default (dt=_DT was frozen at def)
        print(f"[{args.variant}] kdv override: ladder {rungs}, dt -> {cfl_dt:.2e}", flush=True)
    # cahn_hilliard: dt=2e-4 @256^2 x 25k steps is infeasible; 4e-4 is stable (verified)
    # and 2x faster -> generate in shards (see --shard).
    if block["module"] == "cahn_hilliard":
        cahn_hilliard._solve.__defaults__ = (2.5e-4,)        # 4e-4 blows up at 64^2; 2.5e-4 stable (verified)
        print(f"[{args.variant}] cahn_hilliard dt -> 2.5e-4", flush=True)

    hf = rungs[-1]
    N = args.ntrain + args.ntest
    out_dir = os.path.join(OUT_ROOT, f"{args.variant}_generated")

    if args.merge:
        return merge_shards(args, block, ndim, rungs, out_dir)

    lo, hi = (args.shard if args.shard else (0, N))
    print(f"[{args.variant}] ndim={ndim} ladder={rungs} HF={hf} N={N} slice=[{lo}:{hi}] (T={T})", flush=True)
    specs = mod.sample_configs(N, block["sampling"], ndim, SEED)
    Y = {r: [] for r in rungs}
    X, names = [], None
    for i in range(lo, hi):
        fields, cond, names = mod.generate_sample(specs[i], rungs, hf, T)
        X.append(np.asarray(cond, dtype=np.float64))
        for r in rungs:
            Y[r].append(np.asarray(fields[r], dtype=np.float64).ravel())
        if (i - lo + 1) % 5 == 0 or i == hi - 1:
            print(f"  {args.variant}: {i - lo + 1}/{hi - lo} (global {i+1})", flush=True)
    X = np.stack(X)
    os.makedirs(out_dir, exist_ok=True)

    if args.shard:                                            # save a shard, defer train/test to --merge
        sh_dir = os.path.join(out_dir, "shards"); os.makedirs(sh_dir, exist_ok=True)
        payload = {"x": X, "lo": lo, "hi": hi, "rungs": np.array(rungs),
                   "names": np.array(list(names))}
        for k, r in enumerate(rungs):
            payload[f"y{k}"] = np.stack(Y[r])
        np.savez(os.path.join(sh_dir, f"shard_{lo:05d}_{hi:05d}.npz"), **payload)
        print(f"  -> wrote shard [{lo}:{hi}] ({len(X)} samples)", flush=True)
        return

    nt = args.ntrain
    for k, r in enumerate(rungs, start=1):
        Yr = np.stack(Y[r])
        np.savez(os.path.join(out_dir, f"train_l{k}.npz"), x=X[:nt], y=Yr[:nt])
        np.savez(os.path.join(out_dir, f"test_l{k}.npz"),  x=X[nt:], y=Yr[nt:])
    grid_shape = [[r] if ndim == 1 else [r, r] for r in rungs]
    _write_meta_readme(args, block, ndim, rungs, grid_shape, names, out_dir)
    print(f"  -> wrote {out_dir}", flush=True)

if __name__ == "__main__":
    main()
