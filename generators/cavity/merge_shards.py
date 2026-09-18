import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from gen_one import re_list, N_SAMPLES, LEVELS
OUT = "/archive/mf_field/lid_driven_cavity_generated_v2"
SHARDS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shards")
os.makedirs(OUT, exist_ok=True)
Re = re_list(); n_tr = int(round(0.8*N_SAMPLES))
ok = True
for li, res in enumerate(LEVELS, start=1):
    files = [os.path.join(SHARDS, str(res), f"{i:03d}.npy") for i in range(N_SAMPLES)]
    missing = [f for f in files if not os.path.exists(f)]
    if missing:
        print(f"L{li} res={res}: MISSING {len(missing)} shards -> {missing[:3]}..."); ok=False; continue
    Y = np.stack([np.load(f) for f in files], 0)
    X = Re.reshape(-1,1)
    np.savez(os.path.join(OUT, f"train_l{li}.npz"), x=X[:n_tr], y=Y[:n_tr])
    np.savez(os.path.join(OUT, f"test_l{li}.npz"),  x=X[n_tr:], y=Y[n_tr:])
    print(f"[wrote] L{li} res={res}: train={n_tr} test={N_SAMPLES-n_tr} y.shape={Y.shape}")
print("ALL OK" if ok else "INCOMPLETE")
