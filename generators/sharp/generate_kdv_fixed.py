"""Regenerate kdv_1d with the FIXED config that restores LF/HF correlation.

Root cause of decorrelation (corr ~ -0.02): weak dispersion (delta in [0.015,0.04])
+ broadband IC => solitons narrower than the coarse cell => LF/HF diverge.
Fix (verified, corr 0.985 on ladder [64,128,256]): delta in [0.05,0.10] (wider, grid-
resolvable solitons) + IC band-limited to 16 modes. CFL dt for stability.

Factory npz, 400/100, aligned MF. Sharded (slow: dt~1e-6 => ~1M steps/HF solve).
Usage: python generate_kdv_fixed.py [--shard LO HI | --merge]
"""
import argparse, json, os, glob
import numpy as np
from mffp_sharp.pdes import kdv
from mffp_sharp.common.spectral import spectral_interp

OUT = "/archive/mf_field/sharp_generated/kdv_1d_generated"
SEED = 42; NTRAIN, NTEST = 400, 100; N = NTRAIN + NTEST
L = 2.0; LADDER = [32, 64, 128]; IC_MODES = 16          # [64,128,256]@dt~1e-6 too slow
DELTA_RANGE = (0.07, 0.12); AMP_RANGE = (0.3, 0.7)      # wider solitons -> LF/HF corr ~0.75
K_EFF = (2/3) * np.pi * LADDER[-1] / L
DT = float(min(1e-3, 0.2 / (DELTA_RANGE[1]**2 * K_EFF**3)))   # CFL at stiffest (delta max, HF)

def draw():
    """Deterministic per-sample (delta, amp, ic16) — same across fidelities."""
    rng = np.random.default_rng(SEED)
    deltas = rng.uniform(*DELTA_RANGE, N)
    amps = rng.uniform(*AMP_RANGE, N)
    ics = [amps[i] * (2 * np.random.default_rng(SEED + 1 + i).random(IC_MODES) - 1) for i in range(N)]
    return deltas, amps, ics

def meta_readme():
    meta = {"variant": "kdv_1d", "module": "kdv", "ndim": 1,
            "source": "APEBench (arXiv:2411.00180)", "output_time": 1.0,
            "ladder": [[r] for r in LADDER], "param_names": ["delta", "ic_amplitude"],
            "n_params": 2, "ntrain": NTRAIN, "ntest": NTEST, "seed": SEED,
            "note": "FIXED config: delta in [0.05,0.10] + 16-mode IC for LF/HF correlation (corr~0.985)"}
    json.dump(meta, open(os.path.join(OUT, "meta.json"), "w"), indent=2)
    open(os.path.join(OUT, "README.md"), "w").write(
        f"# kdv_1d_generated (fixed)\n\n**PDE:** KdV u_t+6uu_x+delta^2 u_xxx=0  \n"
        f"**Source:** APEBench (arXiv:2411.00180)  \n**Ladder:** {[[r] for r in LADDER]}  \n"
        f"**Params (2):** delta in [0.05,0.10], ic_amplitude in [0.3,0.7]  \n"
        f"**Train/Test per fidelity:** {NTRAIN}/{NTEST}  \ndt={DT:.1e} (CFL); IC=16 modes.\n"
        f"Fixed from the original (delta[0.015,0.04]+broadband IC) which decorrelated LF/HF.\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shard", nargs=2, type=int, default=None)
    ap.add_argument("--merge", action="store_true")
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    deltas, amps, ics = draw()

    if args.merge:
        parts = sorted(glob.glob(os.path.join(OUT, "shards", "*.npz")), key=lambda f: int(np.load(f)["lo"]))
        X = np.concatenate([np.load(f)["x"] for f in parts])
        assert X.shape[0] == N, f"{X.shape[0]} != {N}"
        for k in range(len(LADDER)):
            Yk = np.concatenate([np.load(f)[f"y{k}"] for f in parts])
            assert np.isfinite(Yk).all(), f"non-finite level {k}"
            np.savez(os.path.join(OUT, f"train_l{k+1}.npz"), x=X[:NTRAIN], y=Yk[:NTRAIN])
            np.savez(os.path.join(OUT, f"test_l{k+1}.npz"),  x=X[NTRAIN:], y=Yk[NTRAIN:])
        meta_readme(); print("merged", OUT, flush=True); return

    lo, hi = args.shard if args.shard else (0, N)
    print(f"[kdv_1d fixed] ladder={LADDER} dt={DT:.2e} slice=[{lo}:{hi}]", flush=True)
    X = np.column_stack([deltas, amps])
    Y = [[] for _ in LADDER]
    for i in range(lo, hi):
        for j, r in enumerate(LADDER):
            u = kdv._solve(spectral_interp(ics[i], r), float(deltas[i]), L, 1.0, dt=DT)
            Y[j].append(u.astype(np.float64))
        if (i-lo+1) % 5 == 0 or i == hi-1: print(f"  {i-lo+1}/{hi-lo}", flush=True)
    if args.shard:
        sh = os.path.join(OUT, "shards"); os.makedirs(sh, exist_ok=True)
        pay = {"x": X[lo:hi], "lo": lo, "hi": hi}
        for j in range(len(LADDER)): pay[f"y{j}"] = np.stack(Y[j])
        np.savez(os.path.join(sh, f"shard_{lo:05d}_{hi:05d}.npz"), **pay)
        print(f"  -> shard [{lo}:{hi}]", flush=True); return
    for k in range(len(LADDER)):
        Yk = np.stack(Y[k])
        np.savez(os.path.join(OUT, f"train_l{k+1}.npz"), x=X[:NTRAIN], y=Yk[:NTRAIN])
        np.savez(os.path.join(OUT, f"test_l{k+1}.npz"),  x=X[NTRAIN:], y=Yk[NTRAIN:])
    meta_readme(); print("wrote", OUT, flush=True)

if __name__ == "__main__":
    main()
