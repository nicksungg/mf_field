"""pressure_poisson (Hagen-Poiseuille) at the standardized 400/100, factory format.
Faithful to generate_pressure_poisson_mf.py (analytic linear-axial pressure, masked;
LF = block-mean(HF) + uniform noise). Ladder L1..L4 = 8,16,32,64 (coarse->fine)."""
import json, os
import numpy as np

OUT = "/archive/mf_field_extension_data/data_400_100/pressure_poisson_poiseuille_generated"
SEED = 42; NTRAIN, NTEST = 400, 100; N = NTRAIN + NTEST
HF = 64; LADDER = [8, 16, 32, 64]            # coarse -> fine (HF=64 is exact analytic)
R_RANGE = (0.15, 0.33); VMAX_RANGE = (0.6, 1.6)
P_AMP_LO, P_AMP_HI = 0.02, 0.08; LF_NOISE = 0.05

def block_mean(img, k):
    n = img.shape[0] // k
    return img[:n*k, :n*k].reshape(n, k, n, k).mean((1, 3))

rng = np.random.default_rng(SEED)
r = rng.uniform(*R_RANGE, N); vmax = rng.uniform(*VMAX_RANGE, N)
params = np.column_stack([r, vmax]).astype(np.float64)
yn = (np.arange(HF) + 0.5) / HF; Y = yn[:, None]; X = (np.arange(HF) + 0.5)[None, :] / HF
g = vmax / r**2; lg = np.log(g)
A_all = P_AMP_LO + (P_AMP_HI - P_AMP_LO) * (lg - lg.min()) / (lg.max() - lg.min())

p_hf = np.empty((N, HF, HF))
for i in range(N):
    in_fluid = np.broadcast_to(np.abs(Y - 0.5) <= r[i], (HF, HF))
    p_lin = 0.5 + A_all[i] * (1.0 - 2.0 * X)
    p_hf[i] = np.where(in_fluid, np.broadcast_to(p_lin, (HF, HF)), 0.5)

# per-fidelity fields: HF exact; coarser = block-mean(HF)+noise (aligned MF)
Y_by_level = []
for k in LADDER:
    if k == HF:
        Y_by_level.append(p_hf.reshape(N, -1).copy())
    else:
        ksz = HF // k; arr = np.empty((N, k, k))
        for i in range(N):
            c = block_mean(p_hf[i], ksz); amp = c.max() - c.min()
            arr[i] = c + rng.uniform(0, LF_NOISE * amp, (k, k))
        Y_by_level.append(arr.reshape(N, -1))

os.makedirs(OUT, exist_ok=True)
for k, Yk in enumerate(Y_by_level, start=1):
    np.savez(os.path.join(OUT, f"train_l{k}.npz"), x=params[:NTRAIN], y=Yk[:NTRAIN])
    np.savez(os.path.join(OUT, f"test_l{k}.npz"),  x=params[NTRAIN:], y=Yk[NTRAIN:])
meta = {"name": "pressure_poisson_poiseuille", "source": "Partin et al. 2022 (arXiv:2205.05187)",
        "ladder": [[k, k] for k in LADDER], "param_names": ["radius_r", "v_max"], "n_params": 2,
        "ntrain": NTRAIN, "ntest": NTEST, "seed": SEED}
json.dump(meta, open(os.path.join(OUT, "meta.json"), "w"), indent=2)
open(os.path.join(OUT, "README.md"), "w").write(
    f"# pressure_poisson_poiseuille_generated\n\n**Source:** Partin et al. 2022 (arXiv:2205.05187)  \n"
    f"**Ladder:** {[[k,k] for k in LADDER]} (coarse->fine)  \n**Params (2):** radius_r, v_max  \n"
    f"**Train/Test per fidelity:** {NTRAIN}/{NTEST}\n\nFactory npz (x,y); aligned MF.\n")
print("wrote", OUT, "finite:", all(np.isfinite(Y).all() for Y in Y_by_level))
