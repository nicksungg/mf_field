"""Regenerate the extension solver-backed datasets at the standardized 400/100
(per-fidelity, aligned) using the validated solvers.py REGISTRY.

Output: factory npz convention (matches eloise sharp_generated + mf_field core):
  <OUT>/<name>_generated/{train,test}_l{k}.npz  with x=(N,d) params, y=(N,prod(grid))
Same params across fidelities (aligned MF). Native ladders from the REGISTRY.

Usage: python generate_ext_standardized.py <name> [--ntrain 400 --ntest 100]
"""
import argparse, json, os
import numpy as np
import solvers as S

OUT = "/orcd/data/faez/001/nick/mf_field_extension_data/data_400_100"
SEED = 42
SOURCE = {
 "helmholtz_2d": "FNO arXiv:2010.08895 (representative)",
 "rayleigh_benard_2d": "de Vahl Davis 1983, IJNMF 3(3):249 (DOI 10.1002/fld.1650030305)",
 "gray_scott_2d": "Pearson 1993, Science 261:189 (DOI 10.1126/science.261.5118.189)",
 "wave_2d": "PDEBench arXiv:2210.07182 (representative)",
 "eikonal_2d": "Sethian 1996, PNAS 93(4):1591 (DOI 10.1073/pnas.93.4.1591)",
 "cahn_hilliard_2d": "Cahn & Hilliard 1958, JCP 28(2):258 (DOI 10.1063/1.1744102)",
 "kuramoto_sivashinsky_1d": "Kuramoto-Tsuzuki 1976 / Sivashinsky 1977",
}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("--ntrain", type=int, default=400)
    ap.add_argument("--ntest", type=int, default=100)
    ap.add_argument("--shard", nargs=2, type=int, default=None)
    ap.add_argument("--merge", action="store_true")
    args = ap.parse_args()
    reg = S.REGISTRY[args.name]
    solve, grids, names = reg["solve"], reg["default_grids"], reg["param_names"]
    N = args.ntrain + args.ntest
    out_dir = os.path.join(OUT, f"{args.name}_generated"); os.makedirs(out_dir, exist_ok=True)
    P = S.sample_params(args.name, N, seed=SEED)              # (N,d) deterministic

    if args.merge:
        import glob
        parts = sorted(glob.glob(os.path.join(out_dir, "shards", "*.npz")),
                       key=lambda f: int(np.load(f)["lo"]))
        X = np.concatenate([np.load(f)["x"] for f in parts])
        assert X.shape[0] == N, f"{X.shape[0]} != {N}"
        nt = args.ntrain
        for k in range(len(grids)):
            Yk = np.concatenate([np.load(f)[f"y{k}"] for f in parts])
            assert np.isfinite(Yk).all(), f"non-finite level {k}"
            np.savez(os.path.join(out_dir, f"train_l{k+1}.npz"), x=X[:nt], y=Yk[:nt])
            np.savez(os.path.join(out_dir, f"test_l{k+1}.npz"),  x=X[nt:], y=Yk[nt:])
        _readme(args, reg, grids, names, out_dir); print("merged", out_dir, flush=True); return

    lo, hi = args.shard if args.shard else (0, N)
    print(f"[{args.name}] grids={grids} d={len(names)} N={N} slice=[{lo}:{hi}]", flush=True)
    Y = [[] for _ in grids]
    for i in range(lo, hi):
        for j, g in enumerate(grids):
            f = solve(P[i:i+1], g)[0]                          # solve one sample at grid g
            Y[j].append(np.asarray(f, dtype=np.float64).ravel())
        if (i-lo+1) % 10 == 0 or i == hi-1:
            print(f"  {args.name}: {i-lo+1}/{hi-lo}", flush=True)
    if args.shard:
        sh = os.path.join(out_dir, "shards"); os.makedirs(sh, exist_ok=True)
        pay = {"x": P[lo:hi], "lo": lo, "hi": hi}
        for j in range(len(grids)): pay[f"y{j}"] = np.stack(Y[j])
        np.savez(os.path.join(sh, f"shard_{lo:05d}_{hi:05d}.npz"), **pay)
        print(f"  -> shard [{lo}:{hi}]", flush=True); return
    nt = args.ntrain
    for k in range(len(grids)):
        Yk = np.stack(Y[k])
        np.savez(os.path.join(out_dir, f"train_l{k+1}.npz"), x=P[:nt], y=Yk[:nt])
        np.savez(os.path.join(out_dir, f"test_l{k+1}.npz"),  x=P[nt:], y=Yk[nt:])
    _readme(args, reg, grids, names, out_dir); print("wrote", out_dir, flush=True)

def _readme(args, reg, grids, names, out_dir):
    gs = [[g, g] if isinstance(g, int) else list(g) for g in grids]
    meta = {"name": args.name, "pde": reg.get("pde"), "source": SOURCE.get(args.name, "NA"),
            "ladder": gs, "param_names": list(names), "n_params": len(names),
            "ntrain": args.ntrain, "ntest": args.ntest, "seed": SEED}
    json.dump(meta, open(os.path.join(out_dir, "meta.json"), "w"), indent=2)
    open(os.path.join(out_dir, "README.md"), "w").write(
        f"# {args.name}_generated\n\n**PDE:** {reg.get('pde')}  \n**Source:** {SOURCE.get(args.name,'NA')}  \n"
        f"**Ladder:** {gs}  \n**Params ({len(names)}):** {', '.join(names)}  \n"
        f"**Train/Test (per fidelity):** {args.ntrain}/{args.ntest}\n\n"
        f"Factory npz: `train_l*.npz`/`test_l*.npz`, keys `x`(N,d) params, `y`(N,prod grid). "
        f"Aligned MF (same params across fidelities).\n")

if __name__ == "__main__":
    main()
