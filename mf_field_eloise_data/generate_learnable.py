"""Regenerate the IC-dominated eloise datasets with the INITIAL CONDITION ENCODED
in the conditioning vector x, so field = f(x) is well-posed AND learnable.

Bug (found 2026-06-28): these drew a fresh RANDOM band-limited IC per sample but
only exposed physical params (L, eps, delta, ...) as x -> the field is set by the
unseen IC seed -> rel-L2 > 1 for every model. Fix: the IC is built deterministically
from a small set of low Fourier-mode coefficients, and THOSE coefficients are stored
in x (like the working burgers/darcy datasets do).

x = [physical params...] + [IC mode coeffs...].  Output: factory npz, 400/100, aligned MF.
Usage: python generate_learnable.py <variant> [--shard LO HI | --merge]
"""
import argparse, json, os, glob
import numpy as np
from mffp_sharp.pdes import (kuramoto_sivashinsky as ks, cahn_hilliard as ch,
    sine_gordon as sg, swift_hohenberg as sh, kdv, nls)

OUT_ROOT = "/orcd/data/faez/001/nick/mf_field/sharp_generated"
SEED = 42; NTRAIN, NTEST = 400, 100; N = NTRAIN + NTEST
K1D = 8          # 1D: modes 1..8 -> 16 coeffs
M2D = 3          # 2D: (kx,ky) in 0..2 minus DC -> 8 modes -> 16 coeffs

def ic_1d(coeffs, res, scale):
    K = len(coeffs) // 2
    Ch = np.zeros(res, complex)
    for k in range(1, K + 1):
        Ch[k] = coeffs[k - 1] + 1j * coeffs[K + k - 1]
        Ch[res - k] = np.conj(Ch[k])
    u = np.fft.ifft(Ch).real
    return u / (np.max(np.abs(u)) + 1e-12) * scale

def ic_2d(coeffs, res, scale):
    xs = 2 * np.pi * np.arange(res) / res
    X, Y = np.meshgrid(xs, xs, indexing="ij")
    modes = [(a, b) for a in range(M2D) for b in range(M2D) if not (a == 0 and b == 0)]
    f = np.zeros((res, res)); idx = 0
    for (kx, ky) in modes:
        f += coeffs[idx] * np.cos(kx * X + ky * Y) + coeffs[idx + 1] * np.sin(kx * X + ky * Y)
        idx += 2
    return f / (np.max(np.abs(f)) + 1e-12) * scale

# variant -> config. phys = list of (name, lo, hi). solve(u0, phys_vals) -> field.
def _kdv_dt(L=2.0, dmax=0.12, hf=128):
    ke = (2/3)*np.pi*hf/L; return float(min(1e-3, 0.2/(dmax**2*ke**3)))

CFG = {
 "kuramoto_sivashinsky_1d": dict(ndim=1, ladder=[128,256,512], T=15.0, scale=0.1,
    phys=[("L",22.0,100.0)], src="APEBench; Kuramoto-Tsuzuki 1976 / Sivashinsky 1977",
    solve=lambda u0,p,T: ks._solve(u0, p[0], T)),
 "kuramoto_sivashinsky": dict(ndim=2, ladder=[64,128,256], T=15.0, scale=0.1,
    phys=[("L",22.0,36.0)], src="APEBench; Kuramoto-Tsuzuki 1976 / Sivashinsky 1977",
    solve=lambda u0,p,T: ks._solve(u0, p[0], T)),
 "cahn_hilliard": dict(ndim=2, ladder=[64,128,256], T=5.0, scale=0.1,
    phys=[("eps",0.012,0.018),("mobility",0.5,1.5),("mean_composition",-0.1,0.1)],
    src="E-UNO (arXiv:2509.01293); Cahn-Hilliard 1958",
    solve=lambda u0,p,T: ch._solve(u0+p[2], p[0], p[1], 1.0, T, dt=2.5e-4)),
 "sine_gordon_1d": dict(ndim=1, ladder=[128,256,512], T=5.0, scale=0.9,
    phys=[("m",0.5,2.0)], src="classical (Strang)",
    solve=lambda u0,p,T: sg._solve(u0, p[0], 40.0, T)),
 "sine_gordon_2d": dict(ndim=2, ladder=[64,128,256], T=5.0, scale=0.9,
    phys=[("m",0.5,2.0)], src="classical (Strang)",
    solve=lambda u0,p,T: sg._solve(u0, p[0], 40.0, T)),
 "swift_hohenberg_1d": dict(ndim=1, ladder=[128,256,512], T=50.0, scale=0.1,
    phys=[("r",0.1,0.6)], src="Swift & Hohenberg 1977",
    solve=lambda u0,p,T: sh._solve(u0, p[0], 64.0, T)),
 "swift_hohenberg_2d": dict(ndim=2, ladder=[64,128,256], T=50.0, scale=0.1,
    phys=[("r",0.1,0.6)], src="Swift & Hohenberg 1977",
    solve=lambda u0,p,T: sh._solve(u0, p[0], 32.0, T)),
 "kdv_1d": dict(ndim=1, ladder=[32,64,128], T=1.0, scale=0.5,
    phys=[("delta",0.07,0.12)], src="APEBench (arXiv:2411.00180)",
    solve=lambda u0,p,T: kdv._solve(u0, p[0], 2.0, T, dt=_kdv_dt())),
 "nls_1d": dict(ndim=1, ladder=[128,256,512], T=2.0, scale=0.35,
    phys=[("nonlinearity",-1.0,-0.2)], src="classical (split-step)",
    solve=lambda u0,p,T: np.abs(nls._solve(u0.astype(complex), p[0], 40.0, T))**2),
}

def draw(cfg):
    rng = np.random.default_rng(SEED)
    phys = np.column_stack([rng.uniform(lo,hi,N) for _,lo,hi in cfg["phys"]])
    ncoef = 2*K1D if cfg["ndim"]==1 else 2*(M2D*M2D-1)
    coeffs = rng.uniform(-1,1,(N,ncoef))
    return phys, coeffs

def build_ic(cfg, coeffs, res):
    return ic_1d(coeffs,res,cfg["scale"]) if cfg["ndim"]==1 else ic_2d(coeffs,res,cfg["scale"])

def meta_readme(variant, cfg, out_dir, names):
    grid=[[r] if cfg["ndim"]==1 else [r,r] for r in cfg["ladder"]]
    meta=dict(variant=variant, ndim=cfg["ndim"], source=cfg["src"], output_time=cfg["T"],
        ladder=grid, param_names=names, n_params=len(names), ntrain=NTRAIN, ntest=NTEST, seed=SEED,
        note="IC-encoded cond (low Fourier modes) so field=f(x) is learnable; fixes rel-L2>1 bug")
    json.dump(meta, open(os.path.join(out_dir,"meta.json"),"w"), indent=2)
    open(os.path.join(out_dir,"README.md"),"w").write(
        f"# {variant}_generated (IC-encoded, learnable)\n\n**Source:** {cfg['src']}  \n"
        f"**Ladder:** {grid}  \n**Params ({len(names)}):** {', '.join(names)}  \n"
        f"**Train/Test per fidelity:** {NTRAIN}/{NTEST}\n\nIC built from low Fourier-mode "
        f"coefficients stored in x (cond), so field=f(x) is well-posed & learnable.\n")

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("variant")
    ap.add_argument("--shard",nargs=2,type=int,default=None); ap.add_argument("--merge",action="store_true")
    a=ap.parse_args(); cfg=CFG[a.variant]; out_dir=f"{OUT_ROOT}/{a.variant}_generated"; os.makedirs(out_dir,exist_ok=True)
    phys,coeffs=draw(cfg); X=np.column_stack([phys,coeffs])
    names=[n for n,_,_ in cfg["phys"]]+[f"ic_c{i}" for i in range(coeffs.shape[1])]
    ladder=cfg["ladder"]

    if a.merge:
        parts=sorted(glob.glob(out_dir+"/shards/*.npz"), key=lambda f:int(np.load(f)["lo"]))
        XX=np.concatenate([np.load(f)["x"] for f in parts]); assert XX.shape[0]==N
        for k in range(len(ladder)):
            Yk=np.concatenate([np.load(f)[f"y{k}"] for f in parts]); assert np.isfinite(Yk).all()
            np.savez(f"{out_dir}/train_l{k+1}.npz",x=XX[:NTRAIN],y=Yk[:NTRAIN])
            np.savez(f"{out_dir}/test_l{k+1}.npz", x=XX[NTRAIN:],y=Yk[NTRAIN:])
        meta_readme(a.variant,cfg,out_dir,names); print("merged",out_dir,flush=True); return

    lo,hi=a.shard if a.shard else (0,N)
    print(f"[{a.variant}] ndim={cfg['ndim']} ladder={ladder} T={cfg['T']} slice=[{lo}:{hi}] cond_dim={X.shape[1]}",flush=True)
    Y=[[] for _ in ladder]
    for i in range(lo,hi):
        for j,r in enumerate(ladder):
            u0=build_ic(cfg,coeffs[i],r)
            Y[j].append(np.asarray(cfg["solve"](u0, phys[i], cfg["T"]),dtype=np.float64).ravel())
        if (i-lo+1)%5==0 or i==hi-1: print(f"  {i-lo+1}/{hi-lo}",flush=True)
    if a.shard:
        sh_dir=out_dir+"/shards"; os.makedirs(sh_dir,exist_ok=True)
        pay={"x":X[lo:hi],"lo":lo,"hi":hi}
        for j in range(len(ladder)): pay[f"y{j}"]=np.stack(Y[j])
        np.savez(f"{sh_dir}/shard_{lo:05d}_{hi:05d}.npz",**pay); print(f"  -> shard [{lo}:{hi}]",flush=True); return
    for k in range(len(ladder)):
        Yk=np.stack(Y[k]); np.savez(f"{out_dir}/train_l{k+1}.npz",x=X[:NTRAIN],y=Yk[:NTRAIN]); np.savez(f"{out_dir}/test_l{k+1}.npz",x=X[NTRAIN:],y=Yk[NTRAIN:])
    meta_readme(a.variant,cfg,out_dir,names); print("wrote",out_dir,flush=True)

if __name__=="__main__":
    main()
