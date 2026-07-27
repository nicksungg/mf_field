"""Generate ONE (sample, resolution) cavity solve and save it. For SLURM-array parallelism.

The Re list is fixed (log-uniform, seed 42, n=50) so every array task agrees on which
Re goes with which sample index — identical Re across resolutions (the MF signal).
Writes shards to gen_cavity/shards/<res>/<idx>.npy ; merge_shards.py assembles the .npz.
"""
import sys, os, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from lid_driven_cavity import solve_cavity, RE_LO, RE_HI

N_SAMPLES = 50
SEED = 42
LEVELS = [32, 64, 128, 256]


def re_list():
    rng = np.random.default_rng(SEED)
    return np.exp(rng.uniform(np.log(RE_LO), np.log(RE_HI), size=N_SAMPLES))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", type=int, required=True,
                    help="flat index in [0, N_SAMPLES*len(LEVELS)) -> (sample, level)")
    ap.add_argument("--shard_dir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "shards"))
    args = ap.parse_args()
    Re = re_list()
    nlev = len(LEVELS)
    sample = args.task // nlev
    res = LEVELS[args.task % nlev]
    out = os.path.join(args.shard_dir, str(res))
    os.makedirs(out, exist_ok=True)
    fpath = os.path.join(out, f"{sample:03d}.npy")
    if os.path.exists(fpath):
        print(f"[skip] sample={sample} res={res} exists", flush=True)
        return
    re = float(Re[sample])
    import time
    t = time.time()
    omega, steps, resid = solve_cavity(re, res)
    np.save(fpath, omega.reshape(-1).astype(np.float64))
    print(f"[done] sample={sample} res={res} Re={re:.0f} steps={steps} "
          f"resid={resid:.2e} walltime={time.time()-t:.0f}s -> {fpath}", flush=True)


if __name__ == "__main__":
    main()
