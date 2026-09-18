"""
Paper-faithful multi-fidelity dataset:  PRESSURE-POISSON / HAGEN-POISEUILLE FLOW

Reproduction of the dense-regression and low-to-high-dimensional CFD test cases of

    L. Partin, G. Geraci, A. Rushdi, M.S. Eldred, D.E. Schiavazzi,
    "Multifidelity data fusion in convolutional encoder/decoder networks,"
    J. Comput. Phys. (2022) / arXiv:2205.05187.  (Secs. 2.2, 2.3, App. C.4)

RECREATE-ONLY: the paper specifies the PDE, flow case, parameterization, image
sizes, fidelity construction and sample counts, but releases no dataset or solver.

--------------------------------------------------------------------------------
PHYSICS.  Hagen-Poiseuille flow in a cylindrical fluid domain; the solution is
axisymmetric, so a 2D slice through the axis fully describes it (App. C.4.1).
The pressure obeys the incompressible pressure-Poisson equation (Eq. 5)
    Lap p = div f,   f = -rho(u_t + u.grad u) + mu Lap u,   Neumann BC = flux of f.
For fully-developed Poiseuille flow u_t=0 and u.grad u=0, so f is the constant
axial pressure gradient and the exact pressure is LINEAR along the axis and
uniform across each cross-section (the paper's "linear relative pressures").
We therefore generate the analytic Hagen-Poiseuille fields (what the FEM Poisson
solver yields for this idealized case).

GEOMETRY (per Fig. 2):  64x64 image.
    axis 1 (columns x) = axial direction  -> pressure decreases linearly in x
    axis 0 (rows y)    = transverse;  fluid band = |y - 0.5| <= r  (r in [0,1])
    axial velocity   u_x(y) = v_max (1 - ((y-0.5)/r)^2)  inside fluid, 0 outside
    transverse vel.  u_y     = 0  (unidirectional, fully developed)
    pressure gradient  dp/dz ~ v_max / r^2   (Hagen-Poiseuille: 4 mu v_max / r^2)

PARAMETERS:  r (fluid radius), v_max (max velocity).   N=200 realizations.

INPUTS provided for BOTH paper test cases:
  * dense regression (Sec 2.2): x_dense (N,3,64,64) = [noisy concentration mask,
    u_x, u_y]  ->  predict pressure.
  * low-to-high (Sec 2.3): params (N,2) = [r, v_max]  ->  predict pressure.

MULTI-FIDELITY OUTPUT (App. C.4.2), coarsest -> finest:
    LF1 8x8, LF2 16x16, LF3 32x32, HF 64x64.  LFi = HF downsampled (block-mean),
    plus uniform noise U(0, 0.05*(max-min of that LF image)).

SPLIT:  per-sample 60/20/20 -> ~116 train / 49 val / 35 test (App. C.4.2).
    hf32_idx = random 32-subset of the training set (the "HF 32/0" data).

--------------------------------------------------------------------------------
ASSUMPTIONS (not numerically fixed by the paper text, documented):
  * r in [0.15,0.33] (fraction of domain height), v_max in [0.6,1.6].
  * Axial pressure gradient ~ v_max/r^2 mapped (monotone, log) to a visible
    half-amplitude band 0.02..0.08 about 0.5 (matches Figs. 9-10 ranges),
    constant 0.5 outside the fluid (R^2 is scored only inside the fluid).
  * Concentration measurement noise: additive Gaussian sigma=0.10 on the {0,1} mask.
  * Coarsening = block-mean (restriction); paper says "subsampling".

Run:  python3 generate_pressure_poisson_mf.py
"""
import os, json
import numpy as np

OUT = "/archive/workspace/mf_field_data/data"
os.makedirs(OUT, exist_ok=True)

# ---- constants ---------------------------------------------------------------
N = 200
HF = 64
LF_SIZES = {"lf1": 8, "lf2": 16, "lf3": 32}     # coarsest -> finest
R_RANGE = (0.15, 0.33)
VMAX_RANGE = (0.6, 1.6)
P_AMP_LO, P_AMP_HI = 0.02, 0.08   # half-amplitude band of normalized pressure about 0.5
LF_NOISE = 0.05        # U(0, 0.05*(max-min))  on each LF image  (paper)
CONC_SIGMA = 0.10      # concentration measurement noise on the binary mask
SEED = 20220512


def block_mean(img, k):
    """Downsample (n,n)->(n/k,n/k) by averaging k x k blocks (restriction)."""
    n = img.shape[0]
    return img.reshape(n // k, k, n // k, k).mean(axis=(1, 3))


def main():
    rng = np.random.default_rng(SEED)
    r = rng.uniform(*R_RANGE, N)
    vmax = rng.uniform(*VMAX_RANGE, N)
    params = np.column_stack([r, vmax]).astype(np.float32)

    # grids in [0,1]
    yn = (np.arange(HF) + 0.5) / HF        # row centers (transverse)
    xn = (np.arange(HF) + 0.5) / HF        # col centers (axial)
    Y = yn[:, None]; X = xn[None, :]

    # Hagen-Poiseuille axial pressure gradient ~ v_max / r^2.  Its raw dynamic
    # range across (r,v_max) is highly skewed, so we map it (monotonically, via
    # log) into a visible half-amplitude band [P_AMP_LO, P_AMP_HI] about 0.5 --
    # a global affine rescaling like the paper's, keeping pressure a clean
    # increasing function of v_max/r^2 (so the low-to-high map stays learnable).
    g = vmax / r**2
    lg = np.log(g)
    A_all = P_AMP_LO + (P_AMP_HI - P_AMP_LO) * (lg - lg.min()) / (lg.max() - lg.min())

    p_hf = np.empty((N, HF, HF), np.float32)
    mask = np.empty((N, HF, HF), np.float32)
    x_dense = np.empty((N, 3, HF, HF), np.float32)

    for i in range(N):
        in_fluid = np.abs(Y - 0.5) <= r[i]                  # (HF,HF) broadcast
        in_fluid = np.broadcast_to(in_fluid, (HF, HF))

        # axial velocity: parabolic across the band, 0 outside
        prof = vmax[i] * (1.0 - ((Y - 0.5) / r[i])**2)
        ux = np.where(in_fluid, np.broadcast_to(prof, (HF, HF)), 0.0)
        uy = np.zeros((HF, HF))

        # pressure: linear in x inside fluid, 0.5 outside
        A = A_all[i]
        p_lin = 0.5 + A * (1.0 - 2.0 * X)                   # 0.5+A at x=0 .. 0.5-A at x=1
        p = np.where(in_fluid, np.broadcast_to(p_lin, (HF, HF)), 0.5)

        # noisy concentration mask
        c = in_fluid.astype(np.float64) + rng.normal(0, CONC_SIGMA, (HF, HF))

        p_hf[i] = p
        mask[i] = in_fluid
        x_dense[i, 0] = c
        x_dense[i, 1] = ux / VMAX_RANGE[1]                  # normalize vel channel ~[0,1]
        x_dense[i, 2] = uy

    # multi-fidelity LF pressure targets: block-mean downsample + uniform noise
    lf = {}
    for name, k in LF_SIZES.items():
        ksz = HF // k
        arr = np.empty((N, k, k), np.float32)
        for i in range(N):
            coarse = block_mean(p_hf[i].astype(np.float64), ksz)
            rng_amp = coarse.max() - coarse.min()
            coarse = coarse + rng.uniform(0, LF_NOISE * rng_amp, (k, k))
            arr[i] = coarse
        lf[name] = arr

    # 60/20/20 per-sample split  (App. C.4.2: probabilistic, ratios approximate)
    u = rng.uniform(0, 1, N)
    split = np.where(u < 0.60, 0, np.where(u < 0.80, 1, 2)).astype(np.int64)  # 0 tr,1 val,2 te
    train_idx = np.where(split == 0)[0]
    hf32_idx = np.sort(rng.choice(train_idx, size=min(32, len(train_idx)),
                                  replace=False)).astype(np.int64)

    out = dict(
        params=params, param_names=np.array(["radius_r", "v_max"]),
        p_hf=p_hf, p_lf3=lf["lf3"], p_lf2=lf["lf2"], p_lf1=lf["lf1"],
        mask_64=mask, x_dense=x_dense,
        split=split, hf32_idx=hf32_idx,
        channel_names=np.array(["concentration", "u_x", "u_y"]),
        lf_order=np.array(["lf1_8x8", "lf2_16x16", "lf3_32x32", "hf_64x64"]),
    )
    path = os.path.join(OUT, "pressure_poisson_poiseuille_mf.npz")
    np.savez_compressed(path, **out)
    size_mb = os.path.getsize(path) / 1e6

    counts = {"train": int((split == 0).sum()), "val": int((split == 1).sum()),
              "test": int((split == 2).sum()), "hf32": int(len(hf32_idx))}
    manifest = {
        "name": "pressure_poisson_poiseuille_mf",
        "pde": "Incompressible pressure-Poisson equation (Eq. 5); Hagen-Poiseuille flow",
        "paper": ("Partin, Geraci, Rushdi, Eldred, Schiavazzi, 'Multifidelity data "
                  "fusion in convolutional encoder/decoder networks', arXiv:2205.05187, "
                  "Secs. 2.2-2.3, App. C.4"),
        "availability": "recreate-only (no public dataset / no released solver)",
        "domain": "2D slice of an axisymmetric cylindrical fluid domain, 64x64 image",
        "parameters": {"radius_r": list(R_RANGE), "v_max": list(VMAX_RANGE)},
        "n_realizations": N,
        "tasks": {
            "dense_regression": "x_dense (N,3,64,64) [concentration,u_x,u_y] -> pressure",
            "low_to_high": "params (N,2) [r,v_max] -> pressure 64x64"},
        "fidelity": "output pressure resolution; LF = downsampled HF + noise",
        "lf_order_coarse_to_fine": ["LF1 8x8", "LF2 16x16", "LF3 32x32", "HF 64x64"],
        "lf_noise": "U(0, 0.05*(max-min)) added to each LF image",
        "split_60_20_20": counts,
        "hf32_idx": "random 32-subset of training samples (the 'HF 32/0' set)",
        "arrays": {
            "params": "(N,2) [radius_r, v_max] -- low-to-high input",
            "x_dense": "(N,3,64,64) [concentration(noisy mask), u_x, u_y] -- dense input",
            "p_hf": "(N,64,64) HF pressure (0.5 outside fluid)",
            "p_lf3/2/1": "(N,32/16/8,...) LF pressure targets (downsampled+noise)",
            "mask_64": "(N,64,64) binary fluid mask (score R^2 here)",
            "split": "(N,) 0=train,1=val,2=test", "hf32_idx": "(<=32,) HF-32 subset"},
        "assumptions": [
            "Analytic Hagen-Poiseuille fields (exact pressure-Poisson solution for "
            "fully-developed flow): parabolic velocity, linear axial pressure",
            "r in [0.15,0.33], v_max in [0.6,1.6]; axial pressure gradient ~ v_max/r^2 "
            "mapped (monotone, log) to half-amplitude 0.02..0.08 about 0.5",
            "concentration noise N(0,0.10); coarsening by block-mean restriction"],
        "file": "pressure_poisson_poiseuille_mf.npz", "file_mb": round(size_mb, 3),
    }
    with open(os.path.join(OUT, "pressure_poisson_poiseuille_mf.json"), "w") as fh:
        json.dump(manifest, fh, indent=2)

    print(f"saved pressure_poisson_poiseuille_mf.npz  ({size_mb:.2f} MB)")
    print(f"  N={N}  split train/val/test = {counts['train']}/{counts['val']}/{counts['test']}"
          f"  HF32={counts['hf32']}")
    print(f"  pressure range [{p_hf.min():.3f},{p_hf.max():.3f}]  "
          f"fluid-frac mean={mask.mean():.3f}")


if __name__ == "__main__":
    main()
