"""Assemble cavity shards -> mf_field_v2/core/lid_driven_cavity_generated (paired 400/100, 4 levels)
and lid_driven_cavity_generated_lfabund (train_l1/l2 with 4000 rows). Reports missing shards instead of writing partial sets."""
import json, os, sys, time
import numpy as np
sys.path.insert(0, "/archive/mf_field/experiments/datafix"); from gen_cav import re_list, SHARDS
OUT = "/archive/mf_field_v2/core"; LEVELS = [32, 64, 128, 256]; Re = re_list()
def shard(res, s):
    for f in (f"{s:04d}.npy", f"{s:03d}.npy"):
        p = os.path.join(SHARDS, str(res), f)
        if os.path.exists(p): return np.load(p)
    return None
def stack(res, idx):
    ys = [shard(res, s) for s in idx]; miss = [s for s, y in zip(idx, ys) if y is None]
    if miss: raise SystemExit(f"res {res}: missing {len(miss)} shards, e.g. {miss[:5]}")
    return np.stack(ys)
paired = list(range(500)); extra = list(range(500, 4100)); x = Re.reshape(-1, 1)
for variant in ("", "_lfabund"):
    d = os.path.join(OUT, f"lid_driven_cavity_generated{variant}"); os.makedirs(d, exist_ok=True)
    for li, res in enumerate(LEVELS, 1):
        Yp = stack(res, paired)
        if variant and res in (32, 64):
            Ye = stack(res, extra); xtr = np.concatenate([x[:400], x[500:4100]]); ytr = np.concatenate([Yp[:400], Ye])
        else:
            xtr, ytr = x[:400], Yp[:400]
        np.savez(os.path.join(d, f"train_l{li}.npz"), x=xtr, y=ytr); np.savez(os.path.join(d, f"test_l{li}.npz"), x=x[400:500], y=Yp[400:500])
        print(f"[wrote] {d} L{li} res={res} train={len(xtr)} test=100")
    json.dump(dict(dataset=f"lid_driven_cavity_generated{variant}", solver="gen_cavity/lid_driven_cavity.py v2 (MAX_STEPS 200000, tol 1e-5, RK2 vorticity-streamfunction)",
                   levels=LEVELS, seed=42, n_train=400, n_test=100, n_lf_train=4000 if variant else 400, note="samples 0..49 reused from the 2026-08 v2 shards; 50..4099 generated 2026-09-06",
                   generated=time.strftime("%Y-%m-%d %H:%M")), open(os.path.join(d, "meta.json"), "w"), indent=1)
print("CAV_OK")
