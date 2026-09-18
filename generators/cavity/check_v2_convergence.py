import numpy as np, torch, torch.nn.functional as F
D="/archive/mf_field/lid_driven_cavity_generated_v2"
def load(split,lvl): d=np.load(f"{D}/{split}_l{lvl}.npz"); return d["x"], d["y"]
def up(y,res,target):
    t=torch.from_numpy(y.reshape(-1,res,res)).unsqueeze(1).float()
    return F.interpolate(t,size=(target,target),mode="bilinear",align_corners=False).squeeze(1).numpy()
def rel(a,b): return np.sqrt(((a-b)**2).sum())/max(np.sqrt((b**2).sum()),1e-30)
RES=[32,64,128,256]
# Use L4 (256) as the converged reference; measure each coarser level vs it (all upsampled to 256)
X,y4=load("test",4); ref=y4.reshape(-1,256,256)
errs={}
for li,res in [(1,32),(2,64),(3,128)]:
    _,y=load("test",li); yi=up(y,res,256); n=min(len(yi),len(ref))
    errs[res]=np.mean([rel(yi[i],ref[i]) for i in range(n)])
print("=== CAVITY v2 CONVERGENCE (vs L4=256 reference, all upsampled to 256) ===")
print(f"  err(L1=32  vs L4) = {errs[32]:.4e}")
print(f"  err(L2=64  vs L4) = {errs[64]:.4e}")
print(f"  err(L3=128 vs L4) = {errs[128]:.4e}")
print(f"  ratio err(L3)/err(L2) = {errs[128]/errs[64]:.3f}  (want <1 => CONVERGING toward L4)")
print(f"  ratio err(L2)/err(L1) = {errs[64]/errs[32]:.3f}")
order = -np.log2(max(errs[128]/errs[64],1e-9))
print(f"  observed order p ~ {order:.2f}")
conv = errs[128]/errs[64] < 1
print(f"  => {'CONVERGED (HF is valid ground truth)' if conv else 'STILL NOT CONVERGING'}")
# Ghia physical check on a Re~100 sample at L4
Re=X[:,0]; i=int(np.argmin(np.abs(Re-100)))
omega=ref[i]
# recover u on centerline via streamfunction solve
import scipy.sparse as sp, scipy.sparse.linalg as spla
n=256; h=1/(n-1); m=n-2
e=np.ones(m); T=sp.diags([-e,2*e,-e],[-1,0,1],shape=(m,m))
A=(sp.kron(sp.identity(m),T)+sp.kron(T,sp.identity(m)))/h**2
psi=np.zeros((n,n)); psi[1:-1,1:-1]=spla.spsolve(A.tocsc(), omega[1:-1,1:-1].reshape(-1)).reshape(m,m)
u=np.zeros((n,n)); u[1:-1,1:-1]=(psi[2:,1:-1]-psi[:-2,1:-1])/(2*h)
print(f"\n  Ghia check: closest sample Re={Re[i]:.0f}, centerline u_min={u[:,128].min():.4f} (Ghia Re100 ~ -0.206)")
