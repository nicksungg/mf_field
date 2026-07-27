"""kdv_1d learnable: IC built from K=16 low Fourier modes stored in x (richer than the
K=8 attempt that gave MLP 1.19). cond = [delta, 32 IC coeffs]. Ladder [32,64,128], CFL dt."""
import argparse, json, os, glob, numpy as np
from mffp_sharp.pdes import kdv
OUT="/orcd/data/faez/001/nick/mf_field/sharp_generated/kdv_1d_generated"
SEED=42; NTR,NTE=400,100; N=NTR+NTE; LADDER=[32,64,128]; K=16; L=2.0; T=1.0
DMIN,DMAX=0.07,0.12
DT=float(min(1e-3, 0.2/(DMAX**2*((2/3)*np.pi*LADDER[-1]/L)**3)))
def ic1d(c,res,s):
    Ch=np.zeros(res,complex)
    for k in range(1,K+1): Ch[k]=c[k-1]+1j*c[K+k-1]; Ch[res-k]=np.conj(Ch[k])
    u=np.fft.ifft(Ch).real; return u/(np.max(np.abs(u))+1e-12)*s
def draw():
    rng=np.random.default_rng(SEED)
    return rng.uniform(DMIN,DMAX,N), rng.uniform(-1,1,(N,2*K))
def meta():
    names=["delta"]+[f"ic_c{i}" for i in range(2*K)]
    json.dump(dict(variant="kdv_1d",ndim=1,source="APEBench (arXiv:2411.00180)",output_time=T,
        ladder=[[r] for r in LADDER],param_names=names,n_params=len(names),ntrain=NTR,ntest=NTE,seed=SEED,
        note="IC from 16 Fourier modes in x (learnable fix)"),open(f"{OUT}/meta.json","w"),indent=2)
    open(f"{OUT}/README.md","w").write("# kdv_1d_generated (learnable)\nIC from 16 Fourier modes stored in x.\n")
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--shard",nargs=2,type=int); ap.add_argument("--merge",action="store_true")
    a=ap.parse_args(); os.makedirs(OUT,exist_ok=True); dl,cf=draw(); X=np.column_stack([dl,cf])
    if a.merge:
        parts=sorted(glob.glob(OUT+"/shards/*.npz"),key=lambda f:int(np.load(f)["lo"]))
        XX=np.concatenate([np.load(f)["x"] for f in parts]); assert XX.shape[0]==N
        for k in range(len(LADDER)):
            Yk=np.concatenate([np.load(f)[f"y{k}"] for f in parts]); assert np.isfinite(Yk).all()
            np.savez(f"{OUT}/train_l{k+1}.npz",x=XX[:NTR],y=Yk[:NTR]); np.savez(f"{OUT}/test_l{k+1}.npz",x=XX[NTR:],y=Yk[NTR:])
        meta(); print("merged",OUT,flush=True); return
    lo,hi=a.shard if a.shard else (0,N); print(f"kdv K={K} dt={DT:.1e} [{lo}:{hi}]",flush=True)
    Y=[[] for _ in LADDER]
    for i in range(lo,hi):
        for j,r in enumerate(LADDER): Y[j].append(kdv._solve(ic1d(cf[i],r,0.5),dl[i],L,T,dt=DT))
        if (i-lo+1)%5==0: print(f"  {i-lo+1}/{hi-lo}",flush=True)
    if a.shard:
        sh=OUT+"/shards"; os.makedirs(sh,exist_ok=True); pay={"x":X[lo:hi],"lo":lo,"hi":hi}
        for j in range(len(LADDER)): pay[f"y{j}"]=np.stack(Y[j])
        np.savez(f"{sh}/shard_{lo:05d}_{hi:05d}.npz",**pay); print(f"  ->shard[{lo}:{hi}]",flush=True); return
    for k in range(len(LADDER)): np.savez(f"{OUT}/train_l{k+1}.npz",x=X[:NTR],y=np.stack(Y[k])[:NTR]); np.savez(f"{OUT}/test_l{k+1}.npz",x=X[NTR:],y=np.stack(Y[k])[NTR:])
    meta(); print("wrote",OUT,flush=True)
if __name__=="__main__": main()
