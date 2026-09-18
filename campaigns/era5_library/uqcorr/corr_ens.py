"""Stage 2b: correction from a PREDICTED coarse field (FNO ensemble mean, + spread / sigma channels) to the fine grid.

One task = (dataset, backbone, input, seed) at the finest coarse level.  Inputs:
  real          rho * prolong(real coarse solve)                     -> MF-IRNO's own setting (ceiling for predicted inputs)
  pred          rho * prolong(OOF ensemble mean)                      -> solver-free
  pred_spread   pred + the ensemble spread as an extra channel
  pred_spread_sigma  + the mean hetero sigma as a third channel
The OOF ensemble comes from oof/<name>__L<lf>.npz (assemble_oof.py): every train row's prediction is out-of-fold; the test
rows use the all-member ensemble.  Training recipe = MF-IRNO (ct_mfirno.py): damped fixed-point iteration h <- h + alpha*Phi(theta, h, extra),
K steps, IRNO loss (MSE + spectral-weighted spectrum error, fixed-point penalty), AdamW + cosine, val-selected checkpoint.
Backbones (corr_backbones.py): irno (MF-IRNO refiner), convnext (ConvNeXt-U-Net-FiLM), transolver (physics-slice attention over cell tokens, FiLM).  Resumable every 500 steps."""
from __future__ import annotations
import argparse, json, math, os, sys, time
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.checkpoint import checkpoint

HERE = Path(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, str(HERE))
from diag_coarse import ROSTER, level_files, grids_for, seed_all, CODE_VERSION  # noqa: E402
from ct_common import prolong, choose_registration, ls_gain, rel_l2_per_sample, bootstrap_ci  # noqa: E402
import corr_backbones as bb  # noqa: E402

INPUTS = {"real": [], "pred": [], "pred_spread": ["spread"], "pred_spread_sigma": ["spread", "sigma"]}


def radial(grid, device):
    hh, ww = grid
    ky = torch.fft.fftfreq(hh, device=device)[:, None] * hh; kx = torch.fft.fftfreq(ww, device=device)[None, :] * ww
    r = torch.sqrt(ky.square() + kx.square()); return r / r.max()


def spectral_weight(base, lam):
    w = 1 + base.pow(lam); return w / w.mean()


@torch.no_grad()
def refine(model, X, H, E, alpha, steps, batch):
    model.eval(); out = []
    for i in range(0, len(X), batch):
        xb, hb = X[i:i + batch], H[i:i + batch]; eb = E[i:i + batch] if E is not None else None
        for _ in range(steps):
            hb = hb + alpha * model(xb, hb, eb)
        out.append(hb)
    return torch.cat(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True, choices=sorted(ROSTER) or None)
    ap.add_argument("--backbone", choices=["irno", "convnext", "transolver"], default="irno"); ap.add_argument("--input", choices=sorted(INPUTS), default="pred")
    ap.add_argument("--seed", type=int, default=42); ap.add_argument("--val-frac", type=float, default=0.1)
    ap.add_argument("--steps", type=int, default=6000); ap.add_argument("--batch", type=int, default=16); ap.add_argument("--K", type=int, default=6)
    ap.add_argument("--alpha", type=float, default=0.2); ap.add_argument("--width", type=int, default=32); ap.add_argument("--base", type=int, default=48)
    ap.add_argument("--lr", type=float, default=3e-4); ap.add_argument("--spectral-weight", type=float, default=1.0); ap.add_argument("--fixedpoint-weight", type=float, default=0.01)
    ap.add_argument("--eval-every", type=int, default=250); ap.add_argument("--ckpt-every", type=int, default=500)
    ap.add_argument("--out-dir", required=True); ap.add_argument("--ckpt-dir", required=True); ap.add_argument("--tag", default="")
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    a = ap.parse_args(); device = torch.device(a.device); seed_all(a.seed)
    out = Path(a.out_dir); (out / "raw_corr").mkdir(parents=True, exist_ok=True); (out / "preds_corr").mkdir(parents=True, exist_ok=True)

    # ---------------- data ----------------
    d = ROSTER[a.name]; trains, tests = level_files(d); L = len(trains); lf = L - 1           # finest coarse level (1-based)
    tag = a.tag or f"{a.backbone}-{a.input}__{a.name}__L{lf}__s{a.seed}"
    with np.load(trains[lf - 1]) as z: x_tr, ylf_tr = z["x"].astype(np.float32), z["y"].astype(np.float32)
    with np.load(trains[-1]) as z: yhf_tr = z["y"].astype(np.float32)
    with np.load(tests[lf - 1]) as z: x_te, ylf_te = z["x"].astype(np.float32), z["y"].astype(np.float32)
    with np.load(tests[-1]) as z: yhf_te = z["y"].astype(np.float32)
    cells = [int(np.load(t)["y"].shape[1]) for t in trains]; grids = grids_for(a.name, cells); g_lf, g_hf = grids[lf - 1], grids[-1]
    n = len(x_tr); ylf_tr = ylf_tr.reshape(n, *g_lf); yhf_tr = yhf_tr.reshape(n, *g_hf); ylf_te = ylf_te.reshape(-1, *g_lf); yhf_te = yhf_te.reshape(-1, *g_hf)
    extras = INPUTS[a.input]; oof = None
    if a.input != "real":
        of = HERE / "oof" / f"{a.name}__L{lf}.npz"
        assert of.exists(), f"no OOF ensemble file {of}"
        oof = np.load(of); assert int(oof["n_members_train"].min()) > 0, "OOF ensemble does not cover every train row"
        for e in extras:
            assert f"{e}_train" in oof.files, f"OOF file lacks {e}_train"
    perm = np.random.default_rng(a.seed).permutation(n); n_val = max(4, int(round(a.val_frac * n))); va = np.sort(perm[:n_val]); tr = np.sort(perm[n_val:])
    scale = float(np.sqrt((ylf_tr[tr] ** 2).mean())); assert scale > 1e-12
    T = lambda z: torch.from_numpy(np.ascontiguousarray(z, dtype=np.float32))
    Ylf_tr, Yhf_tr, Ylf_te, Yhf_te = T(ylf_tr) / scale, T(yhf_tr) / scale, T(ylf_te) / scale, T(yhf_te) / scale
    reg, reg_errs = choose_registration(Ylf_tr[tr], Yhf_tr[tr], g_hf)
    inp_tr = Ylf_tr if a.input == "real" else T(oof["mean_train"]) / scale
    inp_te = Ylf_te if a.input == "real" else T(oof["mean_test"]) / scale
    up_tr, up_te = prolong(inp_tr, g_hf, reg), prolong(inp_te, g_hf, reg)
    rho = ls_gain(up_tr[tr], Yhf_tr[tr]); H_tr, H_te = rho * up_tr, rho * up_te
    rho_real = ls_gain(prolong(Ylf_tr, g_hf, reg)[tr], Yhf_tr[tr])
    real_floor_te = float(rel_l2_per_sample(rho_real * prolong(Ylf_te, g_hf, reg), Yhf_te).mean())
    E_tr = E_te = None
    if extras:
        E_tr = torch.stack([rho * prolong(T(oof[f"{e}_train"]) / scale, g_hf, reg) for e in extras], 1)
        E_te = torch.stack([rho * prolong(T(oof[f"{e}_test"]) / scale, g_hf, reg) for e in extras], 1)
    xmean, xstd = x_tr[tr].mean(0), np.maximum(x_tr[tr].std(0), 1e-6)
    X_tr, X_te = T((x_tr - xmean) / xstd), T((x_te - xmean) / xstd)
    ncell = g_hf[0] * g_hf[1]
    if a.backbone == "irno":        batch = a.batch if ncell <= 16384 else max(4, a.batch // 2)
    elif a.backbone == "convnext":  batch = a.batch if ncell <= 16384 else max(2, a.batch // 4)
    else:                           batch = (min(a.batch, 8) if ncell <= 16384 else 2)          # transolver: N = cells tokens
    use_ckpt = a.backbone in ("convnext", "transolver") and ncell > 4096
    dev = lambda t: None if t is None else t.to(device)
    X_tr, X_te, H_tr, H_te, Yhf_tr, Yhf_te, E_tr, E_te = map(dev, (X_tr, X_te, H_tr, H_te, Yhf_tr, Yhf_te, E_tr, E_te))
    print(f"[data] {a.name} L={L} coarse {g_lf} -> fine {g_hf} | {a.backbone} input={a.input} extras={extras} | train {len(tr)} val {len(va)} test {len(x_te)} "
          f"| rho {rho:.3f} reg {reg} scale {scale:.3g} | start rel-L2 val {float(rel_l2_per_sample(H_tr[va], Yhf_tr[va]).mean()):.4f} test {float(rel_l2_per_sample(H_te, Yhf_te).mean()):.4f} "
          f"(real-coarse copy floor test {real_floor_te:.4f}) | batch {batch} grad-ckpt {use_ckpt}", flush=True)

    # ---------------- model / train (MF-IRNO recipe) ----------------
    coords = bb.coordinates(g_hf, reg, device)
    model = bb.build(a.backbone, int(x_tr.shape[1]), coords, len(extras), width=a.width, base=a.base).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=1e-5)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, a.steps, eta_min=a.lr / 100)
    rng = np.random.default_rng(a.seed + 1500); r_nyq = radial(g_hf, device); K = a.K
    best = float(rel_l2_per_sample(H_tr[va], Yhf_tr[va]).mean()); best_step = 0
    best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
    log, recent, start_step, spent = [], [], 0, 0.0
    ck = Path(a.ckpt_dir); ck.mkdir(parents=True, exist_ok=True); ckf = ck / "last.pt"
    key = dict(code=CODE_VERSION, tag=tag, steps=a.steps, K=K, alpha=a.alpha, backbone=a.backbone, input=a.input, width=a.width, base=a.base)
    if ckf.exists():
        st = torch.load(ckf, map_location=device, weights_only=False)
        if st.get("key") == key:
            model.load_state_dict(st["model"]); opt.load_state_dict(st["opt"]); sched.load_state_dict(st["sched"])
            best, best_step, best_state, log, start_step, spent = st["best"], st["best_step"], st["best_state"], st["log"], st["step"], st["seconds"]
            rng.bit_generator.state = st["rng"]; print(f"[resume] step {start_step}/{a.steps}", flush=True)
    call = (lambda c, h, e: checkpoint(model, c, h, e, use_reentrant=False)) if use_ckpt else (lambda c, h, e: model(c, h, e))
    t0 = time.time()
    for step in range(start_step + 1, a.steps + 1):
        model.train()
        idx = torch.as_tensor(rng.choice(tr, batch, replace=len(tr) < batch), device=device)
        h, y, c = H_tr[idx], Yhf_tr[idx], X_tr[idx]; e = E_tr[idx] if E_tr is not None else None
        fy = torch.fft.fft2(y, norm="ortho").abs(); loss = y.new_zeros(())
        for k in range(K):
            h = h + a.alpha * call(c, h, e); lam = 1 + k / max(1, K - 1)
            loss = loss + (F.mse_loss(h, y) + a.spectral_weight * ((torch.fft.fft2(h, norm="ortho").abs() - fy).square() * spectral_weight(r_nyq, lam)).mean()) / K
        loss = loss + a.fixedpoint_weight * call(c, y, e).square().mean()
        if not torch.isfinite(loss):
            raise RuntimeError(f"nonfinite loss at step {step}")
        opt.zero_grad(set_to_none=True); loss.backward(); nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step(); sched.step()
        recent.append(float(loss.detach()))
        if step % a.eval_every == 0 or step == a.steps:
            v = refine(model, X_tr[va], H_tr[va], (E_tr[va] if E_tr is not None else None), a.alpha, K, batch); err = float(rel_l2_per_sample(v, Yhf_tr[va]).mean())
            if err < best:
                best, best_step, best_state = err, step, {k2: t.detach().cpu().clone() for k2, t in model.state_dict().items()}
            log.append(dict(step=step, train_loss=float(np.mean(recent)), val_rel_l2=err, elapsed=spent + time.time() - t0)); recent.clear()
            print(f"[{a.backbone}/{a.input}] step {step}/{a.steps} loss {log[-1]['train_loss']:.3e} val {err:.4e} best {best:.4e}@{best_step}", flush=True)
        if step % a.ckpt_every == 0 or step == a.steps:
            torch.save(dict(key=key, model=model.state_dict(), opt=opt.state_dict(), sched=sched.state_dict(), best=best, best_step=best_step,
                            best_state=best_state, log=log, step=step, seconds=spent + time.time() - t0, rng=rng.bit_generator.state), ckf)
    train_seconds = spent + time.time() - t0

    # ---------------- evaluation ----------------
    model.load_state_dict(best_state)
    preds = {k: refine(model, X_te, H_te, E_te, a.alpha, k, batch) for k in sorted(set([1, 3, K, 2 * K]))}
    per = {k: rel_l2_per_sample(p, Yhf_te).cpu().numpy() for k, p in preds.items()}
    v = per[K]; lo, hi = bootstrap_ci(v); start_te = rel_l2_per_sample(H_te, Yhf_te).cpu().numpy()
    res = dict(code_version=CODE_VERSION, name=a.name, coarse_level=lf, n_levels=L, backbone=a.backbone, input=a.input, extras=extras, seed=a.seed,
               coarse_grid=list(g_lf), fine_grid=list(g_hf), registration=reg, registration_errors=reg_errs, rho=rho, rho_real=rho_real, scale=scale,
               n_train=int(len(tr)), n_val=int(len(va)), n_test=int(len(x_te)), steps=a.steps, K=K, alpha=a.alpha, batch=batch, lr=a.lr, width=a.width, base=a.base,
               n_params=int(n_params), train_seconds=train_seconds, selected_step=best_step, best_val_rel_l2=best, grad_ckpt=use_ckpt,
               device=str(device), gpu=(torch.cuda.get_device_name(0) if device.type == "cuda" else None),
               oof_members_train=(float(oof["n_members_train"].mean()) if oof is not None else None), oof_members_test=(int(oof["members_test"]) if oof is not None else None),
               test_rel_l2=float(v.mean()), test_rel_l2_ci95=[lo, hi], test_rel_l2_median=float(np.median(v)),
               **{f"test_rel_l2_K{k}": float(p.mean()) for k, p in per.items()},
               start_rel_l2_test=float(start_te.mean()), real_copy_rel_l2_test=real_floor_te,
               gain_vs_start=float(1 - v.mean() / max(start_te.mean(), 1e-12)), per_sample=dict(test=v.tolist(), start=start_te.tolist()), training_log=log)
    np.savez_compressed(out / "preds_corr" / f"{tag}.npz", pred_test=(preds[K] * scale).cpu().numpy().astype(np.float32), start_test=(H_te * scale).cpu().numpy().astype(np.float32))
    with open(out / "raw_corr" / f"{tag}.json", "w") as f:
        json.dump(res, f, indent=1)
    print(f"[result] {tag}: test rel-L2 {v.mean():.4g} (start {start_te.mean():.4g}, real-copy floor {real_floor_te:.4g}, gain {res['gain_vs_start']*100:.1f}%) "
          f"K1 {per[1].mean():.4g} K{2*K} {per[2*K].mean():.4g} | best val {best:.4g}@{best_step} | {train_seconds/60:.1f} min, {n_params/1e6:.2f}M params", flush=True)


if __name__ == "__main__":
    main()
