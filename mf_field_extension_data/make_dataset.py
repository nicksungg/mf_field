"""
Generate a multi-fidelity dataset for any registered PDE, at any sample count
and ANY number of fidelity levels.

Examples
--------
List datasets:
    python make_dataset.py --list

500 samples, 2 fidelities (default grids):
    python make_dataset.py helmholtz_2d --n 500

2000 samples, FOUR fidelities:
    python make_dataset.py wave_2d --n 2000 --grids 16 32 64 128

Space-time PDE (give nx x nt per level):
    python make_dataset.py kuramoto_sivashinsky_1d --n 300 --grids 64x40 128x80 256x120

Output: <out>/<name>.npz with
    params (N,d), param_names (d,), grids (L,),
    fid0, fid1, ... (one field array per fidelity level, coarse->fine),
    plus lf/hf aliases when there are exactly 2 levels.
"""
import argparse, os, json, time
import numpy as np
from solvers import REGISTRY, sample_params


def parse_grid(tok, kind):
    if kind == "spacetime":
        nx, nt = tok.lower().split("x")
        return (int(nx), int(nt))
    return int(tok)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name", nargs="?", help="dataset name (see --list)")
    ap.add_argument("--n", type=int, default=200, help="number of samples")
    ap.add_argument("--grids", nargs="+", default=None,
                    help="fidelity grids, coarse->fine (e.g. 16 32 64 128, or 64x40 256x120)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "data"))
    ap.add_argument("--params", default=None, help="optional .npy of (N,d) params to reuse")
    ap.add_argument("--backend", choices=["default", "reference"], default="default",
                    help="'reference' uses the higher-accuracy/3rd-party solver if available")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()

    if a.list or not a.name:
        print(f"{'name':28s} {'kind':10s} {'params':40s} default_grids")
        for nm, r in REGISTRY.items():
            print(f"{nm:28s} {r['kind']:10s} "
                  f"{','.join(r['param_names']):40s} {r['default_grids']}")
        return

    reg = REGISTRY[a.name]
    if a.backend == "reference":
        if "reference" not in reg:
            ap.error(f"{a.name} has no reference backend "
                     f"(available: {[n for n in REGISTRY if 'reference' in REGISTRY[n]]})")
        solver = reg["reference"]
    else:
        solver = reg["solve"]
    grids = ([parse_grid(g, reg["kind"]) for g in a.grids]
             if a.grids else reg["default_grids"])

    P = (np.load(a.params) if a.params else
         sample_params(a.name, a.n, seed=a.seed)).astype(float)
    print(f"{a.name}: N={len(P)}  fidelities={grids}")

    os.makedirs(a.out, exist_ok=True)
    fields, meta_levels = {}, []
    for li, g in enumerate(grids):
        t = time.time()
        F = solver(P, g)
        fields[f"fid{li}"] = F.astype(np.float32)
        meta_levels.append({"level": li, "grid": g, "shape": list(F.shape[1:])})
        print(f"  fid{li} grid={g} shape={tuple(F.shape[1:])}  {time.time()-t:.1f}s "
              f"finite={np.isfinite(F).all()}")

    save = dict(params=P.astype(np.float32),
                param_names=np.array(reg["param_names"]),
                grids=np.array([str(g) for g in grids]), **fields)
    if len(grids) == 2:                                  # convenience aliases
        save["lf"], save["hf"] = fields["fid0"], fields["fid1"]
    path = os.path.join(a.out, a.name + ".npz")
    np.savez_compressed(path, **save)
    mb = os.path.getsize(path) / 1e6
    print(f"  -> {path}  ({mb:.2f} MB)")

    # update a side manifest
    mpath = os.path.join(a.out, "manifest_generated.json")
    man = json.load(open(mpath)) if os.path.exists(mpath) else {}
    man[a.name] = dict(pde=reg["pde"], param_names=reg["param_names"],
                       n_samples=len(P), levels=meta_levels, file=a.name + ".npz",
                       file_mb=round(mb, 3))
    json.dump(man, open(mpath, "w"), indent=2)


if __name__ == "__main__":
    main()
