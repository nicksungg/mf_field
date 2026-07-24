"""Smoke + fair-eval for `fno_transolver_seq` — sequential FNO -> Transolver hybrid.

    y_hat = FNO_FiLM(X)  +  alpha * TransolverCorrector(X, ctx, coords)

Pipeline
--------
STAGE 1  base.  The benchmark winner verbatim (`mf_fno_transfer_film`): FiLM-FNO
         pretrained on the abundant LF fidelity, fine-tuned on the scarce HF
         fidelity, on the 256-capped working grid with a per-stage max|Y| scaler.
         Reported as `base_only_rel_l2`.

STAGE 1b out-of-fold base.  Training the corrector on the residual of a model
         that has already fitted those very samples would give a target of ~0 and
         the correction would collapse. So the HF train split is K-folded: from
         the SHARED LF-pretrained weights, one FNO per fold is fine-tuned on the
         other folds and predicts its own fold. That yields an honest,
         out-of-sample residual field R = Y_hf - base_oof for every HF training
         sample (classic stacking). The final base stays the full-data FNO.

STAGE 2  correction.  The FNO is FROZEN. A point-based TransolverCorrector is
         trained to regress R at working-grid query coordinates, conditioned on
         (coords, X, base prediction at that point) and cross-attending to a
         context point cloud (n_ctx=1024). The correction head is zero-init, so
         it starts at exactly 0.

         Context stream: the real LF field when the *test* split also carries it
         (npz_l datasets), otherwise the FNO's own base prediction resampled to
         the LF grid. Never the HF field of the sample being predicted — the
         `eval_v9` habit of synthesising test LF by downsampling the HF target
         would leak the answer, and this family refuses to do that.

STAGE 2b gate.  alpha (init 0) is chosen by a least-squares projection of the
         out-of-fold residual onto the predicted correction on a held-out split,
         refined by a line search that includes alpha=0. Both the corrector and
         alpha therefore see only data that is out-of-sample for them, and a
         useless correction yields exactly alpha=0 -> the hybrid IS the FNO.

STAGE 3  optional joint fine-tune of FNO + corrector + alpha at lr 1e-4 on the
         summed output; kept only if the held-out rel-L2 improves.

Contract: --dataset_dir --dataset_name --epochs --out --ckpt_dir --seed.
Resume: ckpt_dir/last.pt keyed on (epochs_target, grid, recipe_hash).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

AKASH = Path(__file__).resolve().parents[2]                 # …/mf_field/akash
sys.path.insert(0, str(AKASH))
sys.path.insert(0, str(Path(__file__).resolve().parent))    # local model.py

from common.backbone import FNO2d                                        # noqa: E402
from common.mffp import (load_mf_dataset, resolve_grid, finalize_and_write,  # noqa: E402
                         SMOKE, _cap_grid, _modes, _to_grid, train_loop)
from model import (TransolverCorrector, SeqHybrid, param_count,          # noqa: E402
                   grid_coords, gamma_init_for)

# Transolver-side hyperparameters: identical to transolver_residual's
# SMOKE_DEFAULTS where they exist (hidden_dim/n_slices/num_heads/layers/pos-enc,
# n_lf=1024 context points, n_hf=2048 query points, lr=3e-4, batch=4).
TR = dict(hidden_dim=192, n_slices=32, num_heads=6, encoder_layers=2,
          residual_layers=3, pos_enc_freqs=6, n_ctx=1024, n_query=2048,
          lr_corr=3e-4, lr_joint=1e-4, corr_batch=4, weight_decay=1e-5,
          grad_clip=1.0, val_frac=0.2, n_folds=4, eval_batch=1)

# Minimum RELATIVE held-out gain required to switch the gate on / keep stage 3.
MIN_GAIN = 1e-3


def recipe_hash(ctx_source: str = "auto") -> str:
    return hashlib.sha256(
        json.dumps({"fno": SMOKE, "tr": TR, "ctx": ctx_source, "min_gain": MIN_GAIN},
                   sort_keys=True).encode()
    ).hexdigest()[:12]


# ─────────────────────────────────────────────────────────────────────────────
# small utilities
# ─────────────────────────────────────────────────────────────────────────────
def _rel_l2(pred: np.ndarray, target: np.ndarray) -> float:
    """Mean per-sample relative L2 (the benchmark metric)."""
    num = np.linalg.norm(pred - target, axis=1)
    den = np.maximum(np.linalg.norm(target, axis=1), 1e-12)
    return float(np.mean(num / den))


def _jsonable(x: float):
    """JSON-strict: NaN/Inf -> None so the emitted file always parses."""
    return float(x) if np.isfinite(x) else None


def _align(arr: np.ndarray, n: int, what: str) -> np.ndarray:
    """Row-align a per-fidelity array to n samples (index modulo, documented)."""
    if arr.shape[0] == n:
        return arr
    print(f"[warn] {what}: N={arr.shape[0]} != {n}; aligning by index modulo", flush=True)
    return arr[np.arange(n) % arr.shape[0]]


def _fno_predict(model, X: np.ndarray, scaler: float, device, bs: int) -> np.ndarray:
    """(N, d) cond -> (N, H, W) field in RAW units."""
    model.eval()
    out = []
    with torch.no_grad():
        for i in range(0, X.shape[0], bs):
            xb = torch.from_numpy(X[i:i + bs]).float().to(device)
            out.append((model(xb) * scaler).cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32) if out else np.zeros((0,), np.float32)


def _new_fno(cond_dim, grid, device):
    mh, mw = _modes(grid, SMOKE["modes_cap"])
    return FNO2d(cond_dim, hidden_channels=SMOKE["hidden_channels"],
                 n_blocks=SMOKE["n_blocks"], modes_h=mh, modes_w=mw, grid=grid).to(device)


def _tokens(cond: torch.Tensor, coords: torch.Tensor, vals: torch.Tensor) -> torch.Tensor:
    """cond (B,d), coords (P,3), vals (B,P) -> (B, P, 3+d+1)."""
    B, P = vals.shape
    c = coords.unsqueeze(0).expand(B, P, 3)
    x = cond.unsqueeze(1).expand(B, P, cond.shape[1])
    return torch.cat([c, x, vals.unsqueeze(-1)], dim=-1)


def _corr_full_field(corrector, cond_s, base_n, ctx_n, q_coords, c_coords,
                     c_idx, device, bs) -> np.ndarray:
    """Correction on the FULL working grid, in residual-scaler units. (N, H*W)."""
    corrector.eval()
    outs = []
    cc = c_coords[c_idx]
    with torch.no_grad():
        for i in range(0, cond_s.shape[0], bs):
            cb = torch.from_numpy(cond_s[i:i + bs]).float().to(device)
            qb = torch.from_numpy(base_n[i:i + bs]).float().to(device)
            xb = torch.from_numpy(ctx_n[i:i + bs]).float().to(device)[:, c_idx]
            q_tok = _tokens(cb, q_coords, qb)
            c_tok = _tokens(cb, cc, xb)
            outs.append(corrector(c_tok, q_tok).squeeze(-1).cpu().numpy())
    return np.concatenate(outs, 0).astype(np.float32)


# ─────────────────────────────────────────────────────────────────────────────
# stage 2: train the corrector on residual fields
# ─────────────────────────────────────────────────────────────────────────────
def _train_corrector(corrector, cond_s, base_n, ctx_n, R_n, q_coords, c_coords,
                     epochs, lr, device, gen, tag):
    n = cond_s.shape[0]
    if n == 0 or epochs <= 0:
        return
    HW = q_coords.shape[0]
    Mc = c_coords.shape[0]
    nq = min(TR["n_query"], HW)
    nc = min(TR["n_ctx"], Mc)
    opt = torch.optim.AdamW(corrector.parameters(), lr=lr, weight_decay=TR["weight_decay"])
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(epochs, 1), eta_min=1e-6)
    bs = min(TR["corr_batch"], n)
    Ct = torch.from_numpy(cond_s).float()
    Bt = torch.from_numpy(base_n).float()
    Xt = torch.from_numpy(ctx_n).float()
    Rt = torch.from_numpy(R_n).float()
    for ep in range(epochs):
        corrector.train()
        perm = torch.randperm(n, generator=gen)
        tot, nb = 0.0, 0
        for i in range(0, n, bs):
            idx = perm[i:i + bs]
            qi = torch.randperm(HW, generator=gen)[:nq] if nq < HW else torch.arange(HW)
            ci = torch.randperm(Mc, generator=gen)[:nc] if nc < Mc else torch.arange(Mc)
            cb = Ct[idx].to(device)
            q_tok = _tokens(cb, q_coords[qi.to(device)], Bt[idx][:, qi].to(device))
            c_tok = _tokens(cb, c_coords[ci.to(device)], Xt[idx][:, ci].to(device))
            tgt = Rt[idx][:, qi].to(device).unsqueeze(-1)
            opt.zero_grad(set_to_none=True)
            loss = F.mse_loss(corrector(c_tok, q_tok), tgt)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(corrector.parameters(), TR["grad_clip"])
            opt.step()
            tot += float(loss.detach()); nb += 1
        sched.step()
        if (ep + 1) % max(1, epochs // 5) == 0 or ep == epochs - 1:
            print(f"[{tag} {ep+1:04d}/{epochs}] mse={tot/max(nb,1):.4e}", flush=True)


def _fit_alpha(R_val: np.ndarray, C_val: np.ndarray, base_val: np.ndarray,
               Y_val: np.ndarray, scaler_r: float):
    """Least-squares gate + line search including 0 (so alpha=0 is always allowed).

    R_val : out-of-fold residual (Nv, HW), raw units — what the corrector was fit to
    C_val : predicted correction (Nv, HW), residual-scaler units
    base/Y: the FINAL base prediction and truth on the val split, raw units
    """
    corr = C_val * scaler_r
    denom = float((corr * corr).sum())
    a_ls = float((R_val * corr).sum() / denom) if denom > 1e-20 else 0.0
    a_ls = float(np.clip(a_ls, 0.0, 1.5))
    cands = sorted({0.0} | {float(np.clip(f * a_ls, 0.0, 1.5))
                            for f in (0.25, 0.5, 0.75, 1.0, 1.25)}
                   | {0.25, 0.5, 1.0})
    base_r = _rel_l2(base_val, Y_val)
    # a non-zero gate must buy a MEANINGFUL held-out gain, not a noise-level one:
    # without this the search happily picks alpha=1 for a 1e-5 relative "win".
    ceiling = base_r * (1.0 - MIN_GAIN)
    best, best_r = 0.0, base_r
    for a in cands:
        r = _rel_l2(base_val + a * corr, Y_val)
        if r < min(best_r, ceiling):
            best, best_r = a, r
    return best, a_ls, best_r


# ─────────────────────────────────────────────────────────────────────────────
def run(args, out_path: Path) -> dict:
    torch.manual_seed(args.seed); np.random.seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    gen = torch.Generator().manual_seed(args.seed)
    rh = recipe_hash(args.ctx_source)
    p = SMOKE
    ds_dir = Path(args.dataset_dir)

    train = load_mf_dataset(ds_dir, "train")
    test = load_mf_dataset(ds_dir, "test")
    hf = train["hf_fid"]
    lf_fids = list(train["lf_fids"])
    lf = min(lf_fids) if lf_fids else hf          # abundant LF for FNO pretraining
    ctx_fid = max(lf_fids) if lf_fids else hf     # finest LF = corrector context
    if hf not in test["fids"]:
        hf = test["hf_fid"]

    hf_native = resolve_grid(args.dataset_name, int(train["n_cells_by_fid"][hf]))
    lf_native = resolve_grid(args.dataset_name, int(train["n_cells_by_fid"][lf]))
    grid = _cap_grid(hf_native)
    H, W = grid
    HW = H * W

    X_lf = train["cond_by_fid"][lf].astype(np.float32)
    Y_lf = _to_grid(train["field_by_fid"][lf], lf_native, grid)
    X_hf = train["cond_by_fid"][hf].astype(np.float32)
    Y_hf = _to_grid(train["field_by_fid"][hf], hf_native, grid)
    X_te = test["cond_by_fid"][hf].astype(np.float32)
    Y_te = _to_grid(test["field_by_fid"][hf], hf_native, grid)
    cond_dim = int(X_hf.shape[1])
    N_hf, N_te = X_hf.shape[0], X_te.shape[0]

    scaler_lf = max(float(np.abs(Y_lf).max()), 1e-8) if Y_lf.size else 1.0
    scaler_hf = max(float(np.abs(Y_hf).max()), 1e-8) if Y_hf.size else 1.0

    # ── corrector context source ────────────────────────────────────────────
    # real LF only if the TEST split carries it too (no HF-derived synthetic LF:
    # that would leak the target). Otherwise the FNO's own base prediction.
    real_ctx = bool(lf_fids) and (ctx_fid in test["fids"]) and args.ctx_source == "auto"
    # The context CLOUD always lives on the finest LF grid (the resolution a real
    # LF stream would have); only the VALUES differ between the two sources.
    ctx_native = (resolve_grid(args.dataset_name, int(train["n_cells_by_fid"][ctx_fid]))
                  if lf_fids else hf_native)
    ctx_grid = _cap_grid(ctx_native)
    Hc, Wc = ctx_grid
    ctx_source = "real_lf" if real_ctx else "fno_base"

    print(f"[data] {args.dataset_name} loader={train['loader']} LF={lf} HF={hf} "
          f"ctx_fid={ctx_fid} ctx_source={ctx_source} hf_native={hf_native} "
          f"work_grid={grid} ctx_grid={ctx_grid} N_lf={X_lf.shape[0]} N_hf={N_hf} "
          f"N_test={N_te} cond_dim={cond_dim} device={device} recipe={rh}", flush=True)

    # ── working-grid + context coordinates (v9 `field_to_points` convention) ──
    q_coords = grid_coords(H, W).to(device)
    c_coords = grid_coords(Hc, Wc).to(device)
    gamma0 = gamma_init_for(Hc, Wc, TR["n_ctx"])
    # ONE fixed context subsample, shared by the gate fit, stage-3 check and eval
    # (training resamples it every batch, so any fixed draw is in-distribution).
    _g = torch.Generator().manual_seed(args.seed)
    c_idx = (torch.randperm(Hc * Wc, generator=_g)[:TR["n_ctx"]].sort().values
             if Hc * Wc > TR["n_ctx"] else torch.arange(Hc * Wc)).to(device)

    # ── condition standardisation (corrector only; the FNO's FiLM sees raw X) ──
    mu = X_hf.mean(0, keepdims=True) if N_hf else np.zeros((1, cond_dim), np.float32)
    sd = X_hf.std(0, keepdims=True) if N_hf else np.ones((1, cond_dim), np.float32)
    sd = np.maximum(sd, 1e-6).astype(np.float32)
    std = lambda X: ((X - mu) / sd).astype(np.float32)

    fno = _new_fno(cond_dim, grid, device)
    corrector = TransolverCorrector(
        cond_dim, hidden_dim=TR["hidden_dim"], n_slices=TR["n_slices"],
        num_heads=TR["num_heads"], encoder_layers=TR["encoder_layers"],
        residual_layers=TR["residual_layers"], pos_enc_freqs=TR["pos_enc_freqs"],
        interp_gamma=gamma0).to(device)
    hybrid = SeqHybrid(fno, corrector).to(device)
    n_params = param_count(hybrid)

    # ── resume ──────────────────────────────────────────────────────────────
    ckpt_dir = Path(args.ckpt_dir); ckpt_dir.mkdir(parents=True, exist_ok=True)
    last = ckpt_dir / "last.pt"
    state, trained = None, False
    if last.exists():
        try:
            sd_ck = torch.load(last, map_location=device, weights_only=False)
            if (sd_ck.get("epochs_target") == args.epochs
                    and sd_ck.get("grid") == list(grid)
                    and sd_ck.get("recipe_hash") == rh):
                hybrid.load_state_dict(sd_ck["hybrid"])
                state = sd_ck; trained = True
                print("[resume] loaded finished checkpoint", flush=True)
            else:
                print("[resume] key mismatch — training fresh", flush=True)
        except Exception as e:
            print(f"[resume] failed ({e}); fresh", flush=True)

    t_train = time.time()
    if trained:
        fno_stage2 = _new_fno(cond_dim, grid, device)
        fno_stage2.load_state_dict(state["fno_stage2"])
        alpha = float(state["alpha"]); scaler_r = float(state["scaler_r"])
        scaler_ctx = float(state["scaler_ctx"]); alpha_ls = float(state["alpha_ls"])
        stage3_kept = bool(state["stage3_kept"]); fold_ids = state["fold_ids"]
        val_idx = np.asarray(state["val_idx"], dtype=np.int64)
        val_rel_base = float(state["val_rel_base"]); val_rel_hyb = float(state["val_rel_hyb"])
    else:
        # ── STAGE 1: LF pretrain -> HF finetune (the winner's recipe verbatim) ──
        print(f"[stage 1] FNO pretrain on LF ({X_lf.shape[0]} samples)", flush=True)
        train_loop(fno, X_lf, Y_lf, scaler_lf, args.epochs, p["lr_pretrain"], p, device, "LF-pretrain")
        lf_state = {k: v.detach().clone() for k, v in fno.state_dict().items()}
        print(f"[stage 1] FNO fine-tune on HF ({N_hf} samples)", flush=True)
        train_loop(fno, X_hf, Y_hf, scaler_hf, args.epochs, p["lr_finetune"], p, device, "HF-finetune")
        fno_stage2 = _new_fno(cond_dim, grid, device)
        fno_stage2.load_state_dict(fno.state_dict())     # winner-equivalent snapshot

        # ── STAGE 1b: out-of-fold HF fine-tunes -> honest residual targets ──
        K = int(min(TR["n_folds"], N_hf))
        base_oof = np.zeros((N_hf, HW), np.float32)
        fold_ids = (np.arange(N_hf) % K).tolist() if K >= 2 else [0] * N_hf
        if K >= 2:
            f_arr = np.asarray(fold_ids)
            for k in range(K):
                tr_i = np.where(f_arr != k)[0]; te_i = np.where(f_arr == k)[0]
                fk = _new_fno(cond_dim, grid, device)
                fk.load_state_dict(lf_state)             # share the LF pretraining
                s_k = max(float(np.abs(Y_hf[tr_i]).max()), 1e-8)
                train_loop(fk, X_hf[tr_i], Y_hf[tr_i], s_k, args.epochs,
                           p["lr_finetune"], p, device, f"OOF-fold{k}")
                base_oof[te_i] = _fno_predict(fk, X_hf[te_i], s_k, device,
                                              p["batch_size"]).reshape(len(te_i), HW)
                del fk
            print(f"[stage 1b] out-of-fold base ready (K={K})", flush=True)
        else:
            base_oof = _fno_predict(fno, X_hf, scaler_hf, device, p["batch_size"]).reshape(N_hf, HW)
            print("[stage 1b] N_hf too small to fold — in-sample base used", flush=True)

        # ── residual targets + context fields ──
        R = Y_hf.reshape(N_hf, HW) - base_oof                    # (N_hf, HW) raw
        if real_ctx:
            C_all = _to_grid(train["field_by_fid"][ctx_fid], ctx_native, ctx_grid)
            ctx_hf = _align(C_all.reshape(C_all.shape[0], -1), N_hf, "train ctx")
        else:
            ctx_hf = _to_grid(base_oof, grid, ctx_grid).reshape(N_hf, -1)
        scaler_ctx = max(float(np.abs(ctx_hf).max()), 1e-8)

        # ── train/val split for the gate (val is out-of-sample for the corrector) ──
        n_val = int(max(1, round(TR["val_frac"] * N_hf))) if N_hf >= 2 else 0
        n_val = min(n_val, max(N_hf - 1, 0))
        perm = torch.randperm(N_hf, generator=gen).numpy()
        val_idx, fit_idx = perm[:n_val], perm[n_val:]
        scaler_r = max(float(np.abs(R[fit_idx]).max()), 1e-8) if len(fit_idx) else 1.0

        # ── STAGE 2: train the corrector on the residual field ──
        print(f"[stage 2] corrector on residuals: fit={len(fit_idx)} val={len(val_idx)} "
              f"scaler_r={scaler_r:.4e} (|Y|max={scaler_hf:.4e}) gamma0={gamma0:.1f}", flush=True)
        _train_corrector(corrector, std(X_hf[fit_idx]),
                         base_oof[fit_idx] / scaler_hf, ctx_hf[fit_idx] / scaler_ctx,
                         R[fit_idx] / scaler_r, q_coords, c_coords,
                         args.epochs, TR["lr_corr"], device, gen, "corrector")

        # ── STAGE 2b: the gate ──
        alpha, alpha_ls, val_rel_base, val_rel_hyb = 0.0, 0.0, float("nan"), float("nan")
        if len(val_idx):
            base_val_final = _fno_predict(fno, X_hf[val_idx], scaler_hf, device,
                                          p["batch_size"]).reshape(len(val_idx), HW)
            C_val = _corr_full_field(corrector, std(X_hf[val_idx]),
                                     base_oof[val_idx] / scaler_hf,
                                     ctx_hf[val_idx] / scaler_ctx,
                                     q_coords, c_coords, c_idx, device, TR["eval_batch"])
            val_rel_base = _rel_l2(base_val_final, Y_hf.reshape(N_hf, HW)[val_idx])
            alpha, alpha_ls, val_rel_hyb = _fit_alpha(
                R[val_idx], C_val, base_val_final, Y_hf.reshape(N_hf, HW)[val_idx], scaler_r)
            print(f"[stage 2b] alpha_ls={alpha_ls:.4f} alpha={alpha:.4f} "
                  f"val_rel_base={val_rel_base:.6f} val_rel_hybrid={val_rel_hyb:.6f}", flush=True)
        with torch.no_grad():
            hybrid.alpha.fill_(alpha)

        # ── STAGE 3: optional joint fine-tune, kept only if val improves ──
        stage3_kept = False
        e3 = max(1, args.epochs // 4)
        if len(val_idx) and len(fit_idx) and alpha > 0.0:
            snap = {k: v.detach().clone() for k, v in hybrid.state_dict().items()}
            try:
                _joint_finetune(hybrid, X_hf, std(X_hf), Y_hf.reshape(N_hf, HW), ctx_hf,
                                fit_idx, q_coords, c_coords, scaler_hf, scaler_r,
                                scaler_ctx, e3, device, gen)
                bv = _fno_predict(hybrid.fno, X_hf[val_idx], scaler_hf, device,
                                  p["batch_size"]).reshape(len(val_idx), HW)
                Cv = _corr_full_field(hybrid.corrector, std(X_hf[val_idx]), bv / scaler_hf,
                                      ctx_hf[val_idx] / scaler_ctx, q_coords, c_coords,
                                      c_idx, device, TR["eval_batch"])
                r3 = _rel_l2(bv + hybrid.alpha_value * Cv * scaler_r,
                             Y_hf.reshape(N_hf, HW)[val_idx])
                if np.isfinite(r3) and r3 < val_rel_hyb * (1.0 - MIN_GAIN):
                    stage3_kept = True; val_rel_hyb = r3; alpha = hybrid.alpha_value
                    print(f"[stage 3] KEPT (val {r3:.6f}) alpha={alpha:.4f}", flush=True)
                else:
                    hybrid.load_state_dict(snap)
                    print(f"[stage 3] discarded (val {r3:.6f} >= {val_rel_hyb:.6f})", flush=True)
            except Exception as e:                       # never let stage 3 kill the run
                hybrid.load_state_dict(snap)
                print(f"[stage 3] failed ({e}) — discarded", flush=True)
        else:
            print("[stage 3] skipped (alpha=0 or no val split)", flush=True)

        torch.save({"epochs_target": args.epochs, "grid": list(grid), "recipe_hash": rh,
                    "hybrid": hybrid.state_dict(), "fno_stage2": fno_stage2.state_dict(),
                    "alpha": float(alpha), "alpha_ls": float(alpha_ls),
                    "scaler_r": float(scaler_r), "scaler_ctx": float(scaler_ctx),
                    "stage3_kept": bool(stage3_kept), "fold_ids": fold_ids,
                    "val_idx": val_idx.tolist(), "val_rel_base": float(val_rel_base),
                    "val_rel_hyb": float(val_rel_hyb)}, last)
    train_seconds = time.time() - t_train

    # ── EVAL: full HF field on the working grid ─────────────────────────────
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(); torch.cuda.synchronize()
    t_eval = time.time()

    base_te = _fno_predict(hybrid.fno, X_te, scaler_hf, device, p["batch_size"]).reshape(N_te, HW)
    if real_ctx:
        C_te = _to_grid(test["field_by_fid"][ctx_fid], ctx_native, ctx_grid)
        C_te = _align(C_te.reshape(C_te.shape[0], -1), N_te, "test ctx")
    else:
        C_te = _to_grid(base_te, grid, ctx_grid).reshape(N_te, -1)
    alpha_f = hybrid.alpha_value
    if abs(alpha_f) > 0.0:
        corr_te = _corr_full_field(hybrid.corrector, std(X_te), base_te / scaler_hf,
                                   C_te / scaler_ctx, q_coords, c_coords, c_idx,
                                   device, TR["eval_batch"])
        pred = base_te + alpha_f * corr_te * scaler_r
    else:
        corr_te = None
        pred = base_te
    if device.type == "cuda":
        torch.cuda.synchronize()
    eval_seconds = time.time() - t_eval

    target = Y_te.reshape(N_te, HW).astype(np.float64)
    pred = pred.astype(np.float64)
    # `base_only_rel_l2` is ALWAYS the stage-1/2 FNO, i.e. `mf_fno_transfer_film`
    # trained with the identical recipe — the number to compare against the
    # published FNO+FiLM result and the reference for "did the correction help".
    base_final = _rel_l2(base_te.astype(np.float64), target)
    base_only = base_final
    if stage3_kept:                        # stage 3 co-adapts the FNO, so re-measure
        base_only = _rel_l2(
            _fno_predict(fno_stage2, X_te, scaler_hf, device, p["batch_size"]
                         ).reshape(N_te, HW).astype(np.float64), target)
    latency = 1000.0 * eval_seconds / max(N_te, 1)
    peak_mem = (torch.cuda.max_memory_allocated() / 1e6) if device.type == "cuda" else None
    corr_rms = float(np.sqrt(np.mean((alpha_f * corr_te * scaler_r) ** 2))) if corr_te is not None else 0.0

    res = finalize_and_write(
        out_path=out_path, model="fno_transolver_seq", dataset=args.dataset_name,
        pred=pred, target=target, work_grid=grid, n_params=int(n_params),
        train_seconds=train_seconds, eval_seconds=eval_seconds,
        latency_ms_per_sample=latency, peak_mem_mb=peak_mem, seed=args.seed,
        extra={
            "alpha": float(alpha_f),
            "base_only_rel_l2": float(base_only),
            "stage3_joint": bool(stage3_kept),
            "alpha_least_squares": float(alpha_ls),
            "base_only_rel_l2_final_fno": float(base_final),
            "val_rel_l2_base": _jsonable(val_rel_base),
            "val_rel_l2_hybrid": _jsonable(val_rel_hyb),
            "correction_rms_raw_units": corr_rms,
            "residual_scaler": float(scaler_r),
            "hf_scaler": float(scaler_hf),
            "ctx_source": ctx_source,
            "ctx_grid": list(ctx_grid),
            "ctx_fidelity": int(ctx_fid) if isinstance(ctx_fid, (int, np.integer)) else str(ctx_fid),
            "n_ctx_points": int(min(TR["n_ctx"], Hc * Wc)),
            "n_query_points_train": int(min(TR["n_query"], HW)),
            "n_oof_folds": int(min(TR["n_folds"], N_hf)),
            "mf_mechanism": "sequential_residual_FNO_base_plus_transolver_correction",
            "device": str(device), "hf_fidelity": int(hf), "lf_fidelity": int(lf),
            "hf_grid_native": list(hf_native), "work_grid": list(grid),
            "recipe_hash": rh,
        },
    )
    s = res["splits"]["test_hf"]
    print(f"[done] {args.dataset_name}: rel_l2={s['rel_l2_mean']:.6f} "
          f"base_only={base_only:.6f} (final-fno {base_final:.6f}) "
          f"alpha={alpha_f:.4f} stage3={stage3_kept} ctx={ctx_source}", flush=True)
    return res


def _joint_finetune(hybrid, X_hf_raw, X_hf_std, Y_flat, ctx_hf, fit_idx, q_coords,
                    c_coords, scaler_hf, scaler_r, scaler_ctx, epochs, device, gen):
    """Stage 3: optimise FNO + corrector + alpha on the SUMMED output (lr 1e-4)."""
    n = len(fit_idx)
    if n == 0 or epochs <= 0:
        return
    HW = q_coords.shape[0]; Mc = c_coords.shape[0]
    nq = min(TR["n_query"], HW); nc = min(TR["n_ctx"], Mc)
    opt = torch.optim.AdamW(hybrid.parameters(), lr=TR["lr_joint"], weight_decay=TR["weight_decay"])
    Xr = torch.from_numpy(X_hf_raw[fit_idx]).float()
    Xs = torch.from_numpy(X_hf_std[fit_idx]).float()
    Ct = torch.from_numpy(ctx_hf[fit_idx] / scaler_ctx).float()
    Yt = torch.from_numpy(Y_flat[fit_idx] / scaler_hf).float()
    bs = min(TR["corr_batch"], n)
    for ep in range(epochs):
        hybrid.train()
        perm = torch.randperm(n, generator=gen)
        tot, nb = 0.0, 0
        for i in range(0, n, bs):
            idx = perm[i:i + bs]
            qi = torch.randperm(HW, generator=gen)[:nq] if nq < HW else torch.arange(HW)
            ci = torch.randperm(Mc, generator=gen)[:nc] if nc < Mc else torch.arange(Mc)
            qi_d, ci_d = qi.to(device), ci.to(device)
            xb = Xr[idx].to(device); sb = Xs[idx].to(device)
            base = hybrid.fno(xb).reshape(len(idx), -1)          # y/scaler_hf units
            base_q = base[:, qi_d]
            q_tok = _tokens(sb, q_coords[qi_d], base_q)
            c_tok = _tokens(sb, c_coords[ci_d], Ct[idx][:, ci].to(device))
            delta = hybrid.corrector(c_tok, q_tok).squeeze(-1)
            pred = base_q + hybrid.alpha * delta * (scaler_r / scaler_hf)
            loss = F.mse_loss(pred, Yt[idx][:, qi].to(device))
            opt.zero_grad(set_to_none=True)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(hybrid.parameters(), TR["grad_clip"])
            opt.step()
            tot += float(loss.detach()); nb += 1
        if (ep + 1) % max(1, epochs // 3) == 0 or ep == epochs - 1:
            print(f"[joint {ep+1:04d}/{epochs}] mse={tot/max(nb,1):.4e} "
                  f"alpha={hybrid.alpha_value:.4f}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset_dir", required=True)
    ap.add_argument("--dataset_name", required=True)
    ap.add_argument("--epochs", type=int, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ckpt_dir", required=True)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--ctx_source", choices=["auto", "fno_base"], default="auto",
                    help="'auto' = real LF point cloud as corrector context when the "
                         "TEST split carries that fidelity (mirrors transolver_residual, "
                         "the family whose complementarity this hybrid exploits); "
                         "'fno_base' = never use test-time LF, context is the FNO's own "
                         "base prediction (strict cond-only ablation).")
    args = ap.parse_args()
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    run(args, out)
    print(f"[wrote] {out}", flush=True)


if __name__ == "__main__":
    main()
