"""Inference-only re-evaluation of the already-trained `transolver_residual`.

Why this exists
---------------
`factory_mffp/models/transolver_residual/smoke_eval.py` reported only a
*validation* nRMSE on 2048 randomly sampled points (its test loop silently
skipped every npz_l dataset because `ds_dir/"test"` does not exist there).  That
number is not comparable with the rest of the benchmark, which reports per-sample
relative-L2 on the **HF test split, full field, on the 256-capped working grid**
via `data_adapters.metrics.finalize_and_write`.

This script loads the saved `best.pt` weights (NO training) and re-evaluates them
under the unified protocol:

  * working grid  = `_cap_grid(resolve_grid(dataset_name, n_cells_of_HF))`
  * target        = the benchmark HF test field, bilinearly resampled to that grid
                    (identical to what every other family scores against)
  * prediction    = the point-based Transolver queried at *all* working-grid
                    coordinates (`n_hf = 10**9` makes `sample_points` a no-op),
                    with the LF context sampled exactly as in training (n_lf=1024)

Fields are raw in this loader (no normalisation anywhere), so nothing is inverted.

Usage:
    python transolver_reeval.py --dataset_name ifc_heat \
        --dataset_dir /.../factory_mffp/data/ifc_heat \
        --out /.../akash/results/reeval_transolver/ifc_heat.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader, Dataset

# ── import shim ──────────────────────────────────────────────────────────────
MF_ROOT = Path(__file__).resolve().parents[2]          # …/mf_field
AKASH = MF_ROOT / "akash"
FACTORY = MF_ROOT / "factory_mffp"
TRANSOLVER = FACTORY / "models" / "transolver_residual"
V9 = FACTORY / "references" / "v9_baseline"
for p in (str(AKASH), str(FACTORY), str(V9), str(TRANSOLVER)):
    if p not in sys.path:
        sys.path.insert(0, p)

# import the family's own smoke_eval FIRST so `model`/`train_v9`/`eval_v9`
# resolve to the transolver copies (it inserts its own dir at sys.path[0]).
from smoke_eval import (  # noqa: E402
    SMOKE_DEFAULTS, TransolverResidual, param_count, make_collate_fn,
    EvalDataset,
)
from common.mffp import (  # noqa: E402
    load_mf_dataset, resolve_grid, finalize_and_write, _cap_grid, _to_grid,
)

PE_DIM = None  # filled in from SMOKE_DEFAULTS at runtime


# ── dataset wrapper: HF field replaced by the benchmark target on the work grid ─
class WorkGridEvalDataset(Dataset):
    """Wraps the family's EvalDataset.

    `lf_fields` and `cond` are passed through untouched (so the model sees the
    exact context distribution it was trained on).  `hf_field` is replaced by the
    benchmark HF test field resampled to the working grid, which makes the
    collate function emit (a) query coordinates on the working grid and (b) the
    unified target values — the same field every other family is scored against.
    """

    def __init__(self, base: EvalDataset, target_grid_fields: np.ndarray):
        self.base = base
        self.tgt = target_grid_fields          # (N, H, W) float32 on work grid

    def __len__(self):
        return self.tgt.shape[0]

    def __getitem__(self, i):
        s = self.base[i]
        return {
            "cond": np.asarray(s["cond"], dtype=np.float32),
            "lf_fields": s["lf_fields"],
            "hf_field": self.tgt[i],
            "sample_id": s["sample_id"],
        }


def cond_dim_from_state_dict(sd: dict, pos_enc_freqs: int) -> int:
    """hf_encoder input = 3 coords + cond_dim + 1 lf_interp + pos-enc dims."""
    w = sd["hf_encoder.0.weight"]
    pe_dim = 3 * pos_enc_freqs * 2
    return int(w.shape[1]) - 3 - 1 - pe_dim


def run(args) -> dict:
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    p = dict(SMOKE_DEFAULTS)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    ds_dir = Path(args.dataset_dir)

    # ── benchmark HF test field + working grid (identical recipe to every family) ──
    test = load_mf_dataset(str(ds_dir), "test")
    hf_fid = test["hf_fid"]
    n_cells_hf = int(test["n_cells_by_fid"][hf_fid])
    hf_native = resolve_grid(args.dataset_name, n_cells_hf)
    grid = _cap_grid(hf_native)
    Y_te = _to_grid(np.asarray(test["field_by_fid"][hf_fid], dtype=np.float32),
                    hf_native, grid)                      # (N, H, W)

    # ── the family's own test loader (LF context + cond exactly as trained) ──
    base = EvalDataset(ds_dir, split="test")
    if len(base) != Y_te.shape[0]:
        raise RuntimeError(
            f"sample-count mismatch: EvalDataset={len(base)} vs benchmark={Y_te.shape[0]}")

    # the fidelity the family treats as HF may differ from the benchmark HF for a
    # few 1-D datasets (npz_compat keys fidelities by max(H,W) of a *square*
    # reshape). Record it; the target always stays the benchmark HF.
    fam_hf_shape = tuple(np.asarray(base[0]["hf_field"]).shape)
    fam_hf_matches_bench = (int(np.prod(fam_hf_shape)) == n_cells_hf)

    ds = WorkGridEvalDataset(base, Y_te)
    collate = make_collate_fn(p["n_lf"], 10 ** 9)   # all HF query points
    loader = DataLoader(ds, batch_size=args.batch_size, shuffle=False,
                        collate_fn=collate, num_workers=0)

    # ── model + strict weight load ──
    ckpt_path = Path(args.ckpt)
    blob = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    sd = blob["model"] if isinstance(blob, dict) and "model" in blob else blob
    cd_ckpt = cond_dim_from_state_dict(sd, p["pos_enc_freqs"])
    cd_ds = int(base.cond_dim)
    if cd_ckpt != cd_ds:
        raise RuntimeError(
            f"cond_dim mismatch: checkpoint implies {cd_ckpt}, dataset reports {cd_ds}")

    model = TransolverResidual(
        cond_dim=cd_ckpt,
        hidden_dim=p["hidden_dim"], n_slices=p["n_slices"],
        num_heads=p["num_heads"], encoder_layers=p["encoder_layers"],
        residual_layers=p["residual_layers"], pos_enc_freqs=p["pos_enc_freqs"],
        interp_gamma=p["interp_gamma"],
    ).to(device)
    model.load_state_dict(sd, strict=True)   # raises loudly on any key/shape mismatch
    _, n_params = param_count(model)
    model.eval()

    print(f"[data] {args.dataset_name} loader={test['loader']} hf_fid={hf_fid} "
          f"hf_native={hf_native} work_grid={grid} N={len(ds)} cond_dim={cd_ckpt} "
          f"n_lf_streams={len(base[0]['lf_fields'])} fam_hf_shape={fam_hf_shape} "
          f"fam_hf_is_bench_hf={fam_hf_matches_bench} device={device}", flush=True)

    # ── inference ──
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize()
    preds = []
    t0 = time.time()
    with torch.no_grad():
        for list_of_lf_toks, hf_tok, targets, _ids in loader:
            list_of_lf_toks = [t.to(device) for t in list_of_lf_toks]
            hf_tok = hf_tok.to(device)
            out = model(list_of_lf_toks, hf_tok)          # (B, N, 1)
            preds.append(out.squeeze(-1).float().cpu().numpy())
    if device.type == "cuda":
        torch.cuda.synchronize()
    eval_seconds = time.time() - t0

    pred = np.concatenate(preds, 0).astype(np.float64)      # (N, H*W)
    target = Y_te.reshape(Y_te.shape[0], -1).astype(np.float64)
    if pred.shape != target.shape:
        raise RuntimeError(f"shape mismatch pred={pred.shape} target={target.shape}")

    n_samples = int(target.shape[0])
    latency = 1000.0 * eval_seconds / max(n_samples, 1)
    peak_mem = (torch.cuda.max_memory_allocated() / 1e6) if device.type == "cuda" else None

    return finalize_and_write(
        out_path=Path(args.out), model="transolver_residual",
        dataset=args.dataset_name, pred=pred, target=target, work_grid=grid,
        n_params=int(n_params), train_seconds=0.0, eval_seconds=eval_seconds,
        latency_ms_per_sample=latency, peak_mem_mb=peak_mem, seed=args.seed,
        extra={
            "reeval": "unified_HF_test_rel_l2",
            "note": "inference-only re-eval of saved best.pt; replaces the val-based metric",
            "device": str(device),
            "checkpoint": str(ckpt_path),
            "hf_fidelity": int(hf_fid) if isinstance(hf_fid, (int, np.integer)) else str(hf_fid),
            "hf_grid_native": list(hf_native),
            "work_grid": list(grid),
            "n_lf_context_points": int(p["n_lf"]),
            "n_hf_query_points": int(grid[0] * grid[1]),
            "family_hf_field_shape": list(fam_hf_shape),
            "family_hf_is_benchmark_hf": bool(fam_hf_matches_bench),
        },
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset_name", required=True)
    ap.add_argument("--dataset_dir", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ckpt", default=None,
                    help="path to best.pt (default akash/checkpoints/transolver_residual/<ds>/best.pt)")
    ap.add_argument("--batch_size", type=int, default=1)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    if args.ckpt is None:
        args.ckpt = str(AKASH / "checkpoints" / "transolver_residual" / args.dataset_name / "best.pt")
    if not Path(args.ckpt).exists():
        raise SystemExit(f"[fatal] no checkpoint at {args.ckpt}")
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    res = run(args)
    s = res["splits"]["test_hf"]
    print(f"[done] {args.dataset_name}: rel_l2_mean={s['rel_l2_mean']:.6f} "
          f"nRMSE_agg={s['nRMSE']:.6f} n={s['n_samples']} -> {out}", flush=True)


if __name__ == "__main__":
    main()
