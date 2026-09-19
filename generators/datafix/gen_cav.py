"""Sharded converged lid-driven-cavity solves (v2 solver: MAX_STEPS 200000, tol 1e-5) for an extended sample set.
Re list: log-uniform seed 42, size N_ALL (the first 50 reproduce the existing v2 shards, the first 500 = paired set,
500..N_ALL-1 = extra LF-only rows).  usage: gen_cav.py --samples a:b --levels 32,64  [--shard_dir ...]"""
import argparse, os, sys, time
import numpy as np
sys.path.insert(0, "/archive/mf_field/gen_cavity")
from lid_driven_cavity import solve_cavity, RE_LO, RE_HI
N_ALL, SEED = 4100, 42
SHARDS = "/archive/mf_field/gen_cavity/shards"


def re_list():
    rng = np.random.default_rng(SEED); return np.exp(rng.uniform(np.log(RE_LO), np.log(RE_HI), size=N_ALL))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--samples", required=True); ap.add_argument("--levels", required=True); ap.add_argument("--shard_dir", default=SHARDS)
    a = ap.parse_args(); lo, hi = (int(v) for v in a.samples.split(":")); levels = [int(v) for v in a.levels.split(",")]; Re = re_list()
    for s in range(lo, hi):
        for res in levels:
            out = os.path.join(a.shard_dir, str(res)); os.makedirs(out, exist_ok=True); f = os.path.join(out, f"{s:04d}.npy")
            legacy = os.path.join(out, f"{s:03d}.npy")
            if os.path.exists(f) or os.path.exists(legacy):
                continue
            t = time.time(); omega, steps, resid = solve_cavity(float(Re[s]), res)
            np.save(f + ".tmp.npy", omega.reshape(-1).astype(np.float64)); os.replace(f + ".tmp.npy", f)
            print(f"[done] sample={s} res={res} Re={Re[s]:.0f} steps={steps} resid={resid:.2e} conv={resid < 1e-5} wall={time.time()-t:.0f}s", flush=True)


if __name__ == "__main__":
    main()
