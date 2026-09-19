"""Surrogate-track runner: one (dataset, arm, seed) -> result JSON.  theta -> fine field; coarse data for training only.

python run_st.py --dataset core/heat_generated --arm st_koh_pod --seed 42 --out-dir raw
Arms: classical (CPU) st_mean st_knn st_hf_pod_gp st_lf_affine_pod st_koh_pod st_nargp_pod   ('classical' = all six)
      neural  (GPU)  st_mfdnn st_mfdeeponet st_dmfal
FiLM arms live in st_film.py (family script).  Classical arms use ALL training rows (no validation split needed);
neural arms hold out 10% of the fine rows for checkpoint selection.
"""
from __future__ import annotations
import argparse, sys, time, traceback
from pathlib import Path
import torch
sys.path.insert(0, str(Path(__file__).resolve().parent))
from st_common import Unpaired, evaluate_and_write, load_any, result_path, write_excluded

CLASSICAL = ["st_mean", "st_knn", "st_hf_pod_gp", "st_lf_affine_pod", "st_koh_pod", "st_nargp_pod"]
NEURAL = ["st_mfdnn", "st_mfdeeponet", "st_dmfal"]


def parse():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", default="/archive/mf_field/experiments/st_bench/data"); ap.add_argument("--dataset", required=True)
    ap.add_argument("--arm", required=True); ap.add_argument("--seed", type=int, default=42); ap.add_argument("--out-dir", required=True)
    ap.add_argument("--device", default="auto"); ap.add_argument("--force", action="store_true")
    ap.add_argument("--pod-modes", type=int, default=64); ap.add_argument("--pod-energy", type=float, default=0.999)
    ap.add_argument("--gp-restarts", type=int, default=2); ap.add_argument("--nargp-samples", type=int, default=32); ap.add_argument("--nargp-lf-modes", type=int, default=16)
    ap.add_argument("--steps", type=int, default=100000); ap.add_argument("--batch", type=int, default=16); ap.add_argument("--points", type=int, default=512)
    ap.add_argument("--hidden", type=int, nargs="+", default=[128, 128, 128, 128]); ap.add_argument("--latent", type=int, default=128)
    ap.add_argument("--sensors", type=int, default=256); ap.add_argument("--lr", type=float, default=1e-3); ap.add_argument("--wd", type=float, default=1e-4)
    ap.add_argument("--eval-every", type=int, default=500)
    return ap.parse_args()


def main():
    args = parse()
    device = torch.device(("cuda" if torch.cuda.is_available() else "cpu") if args.device == "auto" else args.device)
    arms = CLASSICAL if args.arm == "classical" else [args.arm]
    todo = [a for a in arms if args.force or not result_path(args.out_dir, a, args.dataset, args.seed).exists()]
    if not todo:
        print("all results exist; nothing to do"); return
    classical = all(a in CLASSICAL for a in todo)
    if classical:
        args.latent = 32; device = torch.device("cpu")
    def cuda_trouble(e):
        return any(k in str(e) for k in ("CUDA", "cuda", "NVML", "device-side"))
    try:
        data = load_any(args.dataset, args.data_root, args.seed, val_frac=0.0 if classical else 0.1, device=device, min_val=0 if classical else 4)
    except Exception as e:
        if cuda_trouble(e):
            traceback.print_exc(); print(f"NODE PROBLEM (no result written, feeder will retry elsewhere): {e}", flush=True); sys.exit(3)
        for a in todo:
            write_excluded(result_path(args.out_dir, a, args.dataset, args.seed), a, args.dataset, f"load failed: {e}", args.seed)
        print(f"EXCLUDED {args.dataset}: {e}"); traceback.print_exc(); return
    print(f"[data] {data['name']} paired={data['paired']} levels={data['n_levels']} grid={data['grid']} grid_lf={data['grid_lf']} reg={data['registration']} "
          f"n_hf_train={len(data['hf_tr'])} n_hf_val={len(data['hf_va'])} n_lf_train={len(data['lf_tr'])} n_test={len(data['Xtest'])} cond={data['cond_dim']} device={device}", flush=True)
    from st_classical import ARMS as CARMS, _lf_emulator
    from st_neural import ARMS as NARMS
    cache = None
    for a in todo:
        out = result_path(args.out_dir, a, args.dataset, args.seed); t0 = time.time(); n_params = 0
        try:
            if a in CARMS:
                if a in ("st_lf_affine_pod", "st_koh_pod", "st_nargp_pod"):
                    cache = cache or _lf_emulator(data, args); pred, extra = CARMS[a](data, args, cache)
                else:
                    pred, extra = CARMS[a](data, args)
            elif a in NARMS:
                if args.arm == "st_dmfal" and args.latent == 128:
                    args.latent = 32
                pred, extra, _, n_params = NARMS[a](data, args, device)
            else:
                raise SystemExit(f"unknown arm {a}")
        except Exception as e:
            traceback.print_exc()
            if cuda_trouble(e):
                print(f"[{a}] NODE PROBLEM (no result written, feeder will retry elsewhere): {e}", flush=True); sys.exit(3)
            write_excluded(out, a, args.dataset, f"failed: {type(e).__name__}: {e}", args.seed); print(f"[{a}] FAILED: {e}", flush=True); continue
        res = evaluate_and_write(out, a, data, pred, extra, time.time() - t0, n_params, str(device), args.seed)
        s = res["splits"]["test_hf"]
        print(f"[{a}] {data['name']} rel_l2_mean={s['rel_l2_mean']:.5g} (95% {s['rel_l2_ci95_lo']:.3g}-{s['rel_l2_ci95_hi']:.3g}) nRMSE={s['nRMSE']:.5g} {time.time() - t0:.0f}s -> {out}", flush=True)


if __name__ == "__main__":
    main()
