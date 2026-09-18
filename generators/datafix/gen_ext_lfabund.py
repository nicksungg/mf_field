"""LF-abundant variants for the ext solver-backed datasets (helmholtz, rayleigh_benard, wave, eikonal, cahn_hilliard_2d):
3600 extra coarse-grid solves (seed 4242) appended to the 400 paired rows; per-level solver wall-time logged; the
paired theta and 20 HF re-solves are checked against mf_field_final.  pressure_poisson is skipped: its coarse
levels are block-mean(HF)+noise (synthetic), not solver output."""
import json, sys, time
import numpy as np
from pathlib import Path
EXT = sys.argv[1] if len(sys.argv) > 1 else "/archive/mf_field_extension_data"
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else "/archive/mf_field_v2") / "ext"
FINAL = Path("/archive/mf_field_final/ext")
sys.path.insert(0, EXT); import solvers as S
NAMES = ["helmholtz_2d", "rayleigh_benard_2d", "wave_2d", "eikonal_2d", "cahn_hilliard_2d"]
N_EXTRA, SEED_EXTRA, CHUNK = 3600, 4242, 100
for name in NAMES:
    reg = S.REGISTRY[name]; solve, grids = reg["solve"], reg["default_grids"]; src = FINAL / name
    P500 = S.sample_params(name, 500, seed=42)
    tr = {li: np.load(src / f"train_l{li}.npz") for li in (1, 2)}; te = {li: np.load(src / f"test_l{li}.npz") for li in (1, 2)}
    assert np.allclose(tr[1]["x"], P500[:400]) and np.allclose(te[1]["x"], P500[400:]), f"{name}: paired theta mismatch"
    extra = S.sample_params(name, N_EXTRA, seed=SEED_EXTRA)
    assert len(np.unique(np.concatenate([P500, extra]), axis=0)) == 500 + N_EXTRA
    # regeneration check + cost: 20 paired rows at both grids
    cost = {}
    for li, g in enumerate(grids, 1):
        t = time.perf_counter(); y20 = solve(P500[:20], g); dt = (time.perf_counter() - t) / 20
        ref = tr[li]["y"][:20].reshape(20, g, g); rel = np.linalg.norm(y20 - ref) / np.linalg.norm(ref)
        cost[f"l{li}"] = dict(grid=g, seconds_per_solve=dt, regen_rel_diff_20=float(rel)); print(f"[{name}] L{li} grid {g}: {dt*1e3:.1f} ms/solve, regen rel diff {rel:.2e}", flush=True)
        assert rel < 1e-6, f"{name} L{li}: regenerated fields differ from the shipped ones (rel {rel:.2e})"
    ys = []; t0 = time.perf_counter()
    for a in range(0, N_EXTRA, CHUNK):
        ys.append(solve(extra[a:a + CHUNK], grids[0]).reshape(-1, grids[0] * grids[0]))
    y_extra = np.concatenate(ys); cost["l1"]["extra_total_s"] = time.perf_counter() - t0
    d = OUT / f"{name}_lfabund"; d.mkdir(parents=True, exist_ok=True)
    np.savez(d / "train_l1.npz", x=np.concatenate([tr[1]["x"], extra]), y=np.concatenate([tr[1]["y"], y_extra]))
    np.savez(d / "train_l2.npz", x=tr[2]["x"], y=tr[2]["y"])
    for li in (1, 2):
        np.savez(d / f"test_l{li}.npz", x=te[li]["x"], y=te[li]["y"])
    json.dump(dict(dataset=f"{name}_lfabund", source=f"{EXT}/solvers.py REGISTRY (same solver as the shipped 400/100 set)", grids=[[g, g] for g in grids],
                   params=reg["param_names"], ranges=reg["ranges"], seed_paired=42, seed_extra=SEED_EXTRA, n_train_lf=400 + N_EXTRA, n_train_hf=400, n_test=100,
                   nested="first 400 LF rows == HF rows", cost_per_solve=cost, generated=time.strftime("%Y-%m-%d %H:%M")), open(d / "meta.json", "w"), indent=1)
    print(f"[{name}] wrote {d} (LF rows {400 + N_EXTRA}, extra solve time {cost['l1']['extra_total_s']:.0f} s)", flush=True)
print("EXT_LFABUND_OK")
