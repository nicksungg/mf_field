"""helmholtz_2d fixed: deterministic field from (wavenumber, source_width); restrict
k to [15,25] (avoid worst resonances) + per-sample UNIT-NORM storage (the field SHAPE
is learnable; the amplitude is a resonance scalar that otherwise wrecks rel-L2)."""
import json, os, glob, numpy as np
from mffp_sharp.pdes import helmholtz as hz
OUT="/archive/mf_field/sharp_generated/helmholtz_2d_generated"
SEED=42; NTR,NTE=400,100; N=NTR+NTE; LADDER=[64,128,256]; KLO,KHI=15.0,25.0; SWLO,SWHI=0.03,0.08
rng=np.random.default_rng(SEED)
k=rng.uniform(KLO,KHI,N); sw=rng.uniform(SWLO,SWHI,N); X=np.column_stack([k,sw])
os.makedirs(OUT,exist_ok=True)
for li,res in enumerate(LADDER,1):
    Y=np.empty((N,res*res))
    for i in range(N):
        f=hz._solve(res,k[i],sw[i],1.0).ravel()
        Y[i]=f/(np.linalg.norm(f)+1e-12)            # unit-norm
    np.savez(f"{OUT}/train_l{li}.npz",x=X[:NTR],y=Y[:NTR]); np.savez(f"{OUT}/test_l{li}.npz",x=X[NTR:],y=Y[NTR:])
    print(f"  l{li} res={res} done",flush=True)
meta=dict(variant="helmholtz_2d",ndim=2,source="classical (sparse-direct BVP); k-range+unit-norm fix",
    output_time=0.0,ladder=[[r,r] for r in LADDER],param_names=["wavenumber","source_width"],
    n_params=2,ntrain=NTR,ntest=NTE,seed=SEED,note="k in [15,25], fields unit-normalized (shape-learnable)")
json.dump(meta,open(f"{OUT}/meta.json","w"),indent=2)
open(f"{OUT}/README.md","w").write("# helmholtz_2d_generated (fixed)\n\nDeterministic -lap u - k^2 u = f; "
    "k in [15,25], per-sample unit-norm fields (shape learnable; amplitude is a resonance scalar).\n")
print("wrote",OUT,flush=True)
