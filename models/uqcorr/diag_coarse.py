"""UQ-corrector diagnostic, step 1 (roster edition).

Question: how good is the FiLM-FNO's *coarse* prediction relative to the real coarse solve, and is a
heteroscedastic sigma head informative enough to feed a downstream corrector?

Datasets: the st_bench roster (30 sets: 27 paired mf_field_final sets, era5, poisson_v2, cavity_v2), read through
experiments/st_bench/data/<rel>.  Per (dataset, coarse level, variant, seed):
  * seeded 80/20 split of the TRAIN rows (paired rows, same theta at every level): train the coarse stage on the
    80 % split's coarse fields only, hold out the 20 % split and the test rows;
    (if a directory carries extra coarse-only rows beyond the paired ones -- a pool -- those join the training set)
  * report on both held-out sets:
      fno_coarse_rel_l2   FNO mean vs real coarse                    (coarse native grid)
      gap_rel_l2          rho*prolong(real coarse) vs real fine      (fine grid; = ct_copy_lf_rho, what MF-IRNO starts from)
      pred_start_rel_l2   rho*prolong(FNO mean)   vs real fine       (fine grid; what the proposed U-Net would start from)
      ratio_fno_to_gap    mean fno_coarse_rel_l2 / mean gap_rel_l2   (<1: FNO error is below the fidelity gap)
  variant 'plain'  : MSE, the winner's LF stage (lr 1e-3, batch 16, cosine, AdamW 1e-5, clip 1.0)
  variant 'hetero' : 2-channel head (mean, log-variance), beta-NLL (beta=0.5, Seitzer et al. 2022); adds
      spearman_pixel   rank corr(sigma, |err|) within a sample, mean over samples
      spearman_sample  rank corr(mean sigma per sample, sample rel-L2) across samples
      coverage_2sigma  fraction of pixels with |err| <= 2 sigma   (0.954 if calibrated Gaussian)
      nll_per_pixel    Gaussian NLL per pixel
Unpaired datasets (rows not aligned across levels, e.g. era5) and coarse grids above the 256 working cap are written
as excluded records.  Predictions (mean, logvar) for the held-out rows and the test rows go to preds/ so step 2 can
consume out-of-fold coarse predictions without retraining.  Resumable (ckpt every 20 epochs) for mit_preemptable.
"""
from __future__ import annotations
import argparse, json, math, os, sys, time
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

MF = Path(os.environ.get("MF_ROOT", "/archive/mf_field"))
ST = Path(os.environ.get("UQ_ST", str(MF / "experiments/st_bench")))          # roster.txt + data/<rel>
FAMILY = MF / "factory_mffp/models/mf_fno_transfer_film"
for p in (FAMILY, MF / "factory_mffp", MF / "experiments/bench_ct"):
    sys.path.insert(0, str(p))
from model import FNO2d, param_count                       # noqa: E402  (winner's backbone, byte-identical)
from data_adapters.geometry import resolve_grid, KNOWN_GRIDS  # noqa: E402
import smoke_eval as se                                    # noqa: E402  (SMOKE hyperparams, _modes, _cap_grid)
from ct_common import prolong, choose_registration, ls_gain, rel_l2_per_sample, bootstrap_ci, sha256  # noqa: E402

CODE_VERSION = 3
WORK_CAP = 256


def flat_name(rel: str) -> str:
    """st_bench roster entry -> leaderboard/KNOWN_GRIDS name: core/x -> x, ext/x -> ext__x, sharp/x -> sharp__x."""
    return rel[5:] if rel.startswith("core/") else rel.replace("/", "__")


def load_roster(path: Path | None = None) -> dict:
    """name -> data directory (the one that holds train_l*.npz, one level deeper for era5)."""
    path = path or ST / "roster.txt"
    out = {}
    if not path.exists():
        return out
    for rel in (l.strip() for l in path.read_text().splitlines()):
        if not rel or rel.startswith("#"):
            continue
        d = ST / "data" / rel
        if not list(d.glob("train_l*.npz")):
            sub = sorted(d.glob("*/train_l1.npz"))
            d = sub[0].parent if sub else d
        out[flat_name(rel)] = d
    return out


ROSTER = load_roster()


def lv(p: Path) -> int:
    return int(p.stem.split("_l")[1])


def level_files(d: Path):
    tr = sorted(d.glob("train_l*.npz"), key=lv); te = sorted(d.glob("test_l*.npz"), key=lv)
    assert tr and [lv(p) for p in tr] == [lv(p) for p in te], f"{d}: train/test level files differ"
    return tr, te


def grids_for(name: str, cells: list[int]):
    """(H, W) per level.  KNOWN_GRIDS is authoritative (it knows the 1-D sets and era5's rectangles); for unknown
    names every level must be a perfect square, else the whole ladder is treated as 1-D like ct_common does."""
    if name in KNOWN_GRIDS or all(math.isqrt(c) ** 2 == c for c in cells):
        return [tuple(int(v) for v in resolve_grid(name, c)) for c in cells]
    return [(1, int(c)) for c in cells]


def seed_all(seed: int):
    import random
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)


def rankdata(a: np.ndarray) -> np.ndarray:
    order = np.argsort(a, axis=-1, kind="stable")
    ranks = np.empty_like(order, dtype=np.float64)
    n = a.shape[-1]
    np.put_along_axis(ranks, order, np.broadcast_to(np.arange(n, dtype=np.float64), a.shape), axis=-1)
    return ranks


def spearman_rows(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    ra, rb = rankdata(a), rankdata(b)
    ra = ra - ra.mean(-1, keepdims=True); rb = rb - rb.mean(-1, keepdims=True)
    den = np.sqrt((ra * ra).sum(-1) * (rb * rb).sum(-1))
    return np.where(den > 0, (ra * rb).sum(-1) / np.maximum(den, 1e-12), 0.0)


class HeteroFNO(nn.Module):
    """Winner's FNO2d with the last 1x1 conv widened to 2 channels: (mean, log-variance)."""

    def __init__(self, base: FNO2d):
        super().__init__()
        self.base = base
        hid = base.proj[0].out_channels
        head = nn.Conv2d(hid, 2, 1)
        with torch.no_grad():
            head.weight[0].copy_(base.proj[-1].weight[0]); head.bias[0].copy_(base.proj[-1].bias[0])
            head.weight[1].zero_(); head.bias[1].fill_(-4.0)          # sigma_0 = e^-2 in scaled units
        base.proj[-1] = head

    def forward(self, x):
        out = self.base.proj(self._features(x))                        # (B, 2, H, W)
        return out[:, 0], out[:, 1].clamp(-14.0, 6.0)

    def _features(self, x):
        b = self.base; B = x.shape[0]; H, W = b.grid
        z = b.lift(b.coord_grid.expand(B, 2, H, W))
        for blk in b.blocks:
            z = blk(z, x)
        return z


def beta_nll(mu, logvar, y, beta):
    var = logvar.exp()
    nll = 0.5 * ((y - mu).square() / var + logvar)
    w = var.detach().pow(beta) if beta > 0 else 1.0
    return (w * nll).mean()


@torch.no_grad()
def predict(model, X, hetero, bs, device):
    model.eval(); mus, lvs = [], []
    for i in range(0, len(X), bs):
        xb = X[i:i + bs].to(device)
        if hetero:
            mu, lvr = model(xb); mus.append(mu.cpu()); lvs.append(lvr.cpu())
        else:
            mus.append(model(xb).cpu())
    return torch.cat(mus), (torch.cat(lvs) if hetero else None)


def write_excluded(out: Path, tag: str, name: str, level: int, reason: str, extra: dict):
    (out / "raw").mkdir(parents=True, exist_ok=True)
    with open(out / "raw" / f"{tag}.json", "w") as f:
        json.dump(dict(code_version=CODE_VERSION, name=name, coarse_level=level, excluded=reason, **extra), f, indent=1)
    print(f"[excluded] {tag}: {reason}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True, choices=sorted(ROSTER) or None)
    ap.add_argument("--lf-level", type=int, default=0, help="1-based coarse level; 0 = top coarse level")
    ap.add_argument("--variant", choices=["plain", "hetero"], default="plain")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--steps", type=int, default=30000, help="optimizer steps at batch 16 (WP1 LF stage = 30000)")
    ap.add_argument("--beta", type=float, default=0.5)
    ap.add_argument("--hold-frac", type=float, default=0.2)
    ap.add_argument("--nfolds", type=int, default=0, help="K-fold OOF mode: hold out fold k of a fixed K-way split (split seed --split-seed); 0 = seeded 80/20 split")
    ap.add_argument("--fold", type=int, default=0); ap.add_argument("--split-seed", type=int, default=1234)
    ap.add_argument("--out-dir", required=True); ap.add_argument("--ckpt-dir", required=True)
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    device = torch.device(a.device); seed_all(a.seed); p = se.SMOKE
    out = Path(a.out_dir)

    # ---------------- data ----------------
    d = ROSTER[a.name]; trains, tests = level_files(d)
    L = len(trains); k = (L - 2) if a.lf_level == 0 else (a.lf_level - 1)
    assert 0 <= k <= L - 2, f"lf level {a.lf_level} out of range for L={L}"
    fold_tag = f"F{a.fold}of{a.nfolds}__" if a.nfolds > 0 else ""
    tag = a.tag or f"{a.variant}__{a.name}__L{k+1}__{fold_tag}s{a.seed}"
    with np.load(trains[k]) as z: x_lf, y_lf = z["x"].astype(np.float32), z["y"].astype(np.float32)
    with np.load(trains[-1]) as z: x_hf, y_hf = z["x"].astype(np.float32), z["y"].astype(np.float32)
    with np.load(tests[k]) as z: xt_lf, yt_lf = z["x"].astype(np.float32), z["y"].astype(np.float32)
    with np.load(tests[-1]) as z: xt_hf, yt_hf = z["x"].astype(np.float32), z["y"].astype(np.float32)
    n_paired = len(x_hf)
    aligned = len(x_lf) >= n_paired and np.allclose(x_lf[:n_paired], x_hf) and len(xt_lf) == len(xt_hf) and np.allclose(xt_lf, xt_hf)
    if not aligned:
        write_excluded(out, tag, a.name, k + 1, "rows not aligned across levels (unpaired dataset): no coarse-to-fine gap is defined",
                       dict(variant=a.variant, seed=a.seed, n_levels=L, rows_lf=int(len(x_lf)), rows_hf=int(n_paired)))
        return
    cells = [int(np.load(t)["y"].shape[1]) for t in trains]
    grids = grids_for(a.name, cells); g_lf, g_hf = grids[k], grids[-1]
    if max(g_lf) > WORK_CAP:
        write_excluded(out, tag, a.name, k + 1, f"coarse grid {g_lf} exceeds the {WORK_CAP} working cap",
                       dict(variant=a.variant, seed=a.seed, n_levels=L, coarse_grid=list(g_lf), fine_grid=list(g_hf)))
        return
    pool_rows = np.arange(n_paired, len(x_lf))                 # coarse-only extra rows (none for the roster sets)
    if a.nfolds > 0:                                              # K-fold: same partition for every member (split seed), member differs by --seed
        assert 0 <= a.fold < a.nfolds
        perm = np.random.default_rng(a.split_seed).permutation(n_paired)
        bounds = np.linspace(0, n_paired, a.nfolds + 1).astype(int)
        hold_rows = np.sort(perm[bounds[a.fold]:bounds[a.fold + 1]]); tr_rows = np.concatenate([np.sort(np.setdiff1d(perm, hold_rows)), pool_rows])
    else:
        perm = np.random.default_rng(a.seed).permutation(n_paired)
        n_hold = max(8, int(round(a.hold_frac * n_paired)))
        hold_rows = np.sort(perm[:n_hold]); tr_rows = np.concatenate([np.sort(perm[n_hold:]), pool_rows])
    mh, mw = se._modes(g_lf, p["modes_cap"])
    xmean = x_lf[tr_rows].mean(0); xstd = np.maximum(x_lf[tr_rows].std(0), 1e-6)
    Xn = lambda x: torch.from_numpy((x - xmean) / xstd).float()
    X_tr, X_hold, X_te = Xn(x_lf[tr_rows]), Xn(x_lf[hold_rows]), Xn(xt_lf)
    Y_tr = torch.from_numpy(y_lf[tr_rows]).view(-1, *g_lf)
    scaler = max(float(Y_tr.abs().max()), 1e-8); Y_trs = Y_tr / scaler
    print(f"[data] {a.name} L={L} coarse level {k+1}/{L-1} grid {g_lf} -> fine {g_hf} | train {len(tr_rows)} "
          f"(paired {len(tr_rows)-len(pool_rows)} + pool {len(pool_rows)}) hold {len(hold_rows)} test {len(xt_lf)} | modes {mh}x{mw}", flush=True)

    # ---------------- model ----------------
    base = FNO2d(int(x_lf.shape[1]), hidden_channels=p["hidden_channels"], n_blocks=p["n_blocks"], modes_h=mh, modes_w=mw, grid=g_lf)
    hetero = a.variant == "hetero"
    model = (HeteroFNO(base) if hetero else base).to(device)
    n_params = int(param_count(model))
    bs = min(p["batch_size"], len(tr_rows)); steps_per_epoch = math.ceil(len(tr_rows) / bs)
    epochs = max(1, math.ceil(a.steps / steps_per_epoch))
    opt = torch.optim.AdamW(model.parameters(), lr=p["lr_pretrain"], weight_decay=p["weight_decay"])
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs, eta_min=1e-6)
    ck = Path(a.ckpt_dir); ck.mkdir(parents=True, exist_ok=True); ckf = ck / "last.pt"
    key = dict(code=CODE_VERSION, variant=a.variant, steps=a.steps, grid=list(g_lf), level=k, seed=a.seed, n_train=int(len(tr_rows)), fold=a.fold if a.nfolds else None, nfolds=a.nfolds)
    start_ep, spent = 0, 0.0
    if ckf.exists():
        st = torch.load(ckf, map_location=device)
        if st.get("key") == key:
            model.load_state_dict(st["model"]); opt.load_state_dict(st["opt"]); sched.load_state_dict(st["sched"])
            start_ep, spent = int(st["epoch"]), float(st.get("seconds", 0.0))
            print(f"[resume] epoch {start_ep}/{epochs} from {ckf}", flush=True)
    g = torch.Generator().manual_seed(a.seed)
    for _ in range(start_ep):
        torch.randperm(len(tr_rows), generator=g)
    t0 = time.time()
    for ep in range(start_ep, epochs):
        model.train(); perm_e = torch.randperm(len(tr_rows), generator=g); tot = 0.0
        for i in range(0, len(tr_rows), bs):
            idx = perm_e[i:i + bs]; xb = X_tr[idx].to(device); yb = Y_trs[idx].to(device)
            opt.zero_grad(set_to_none=True)
            if hetero:
                mu, lvr = model(xb); loss = beta_nll(mu, lvr, yb, a.beta)
            else:
                loss = F.mse_loss(model(xb), yb)
            loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), p["grad_clip"]); opt.step()
            tot += float(loss.detach())
        sched.step()
        if (ep + 1) % max(1, epochs // 10) == 0 or ep == epochs - 1:
            print(f"[{a.variant} {ep+1:04d}/{epochs}] loss={tot/steps_per_epoch:.4e}", flush=True)
        if (ep + 1) % 20 == 0 or ep == epochs - 1:
            torch.save(dict(key=key, model=model.state_dict(), opt=opt.state_dict(), sched=sched.state_dict(),
                            epoch=ep + 1, seconds=spent + time.time() - t0), ckf)
    train_seconds = spent + time.time() - t0

    # ---------------- evaluation ----------------
    mu_h, lv_h = predict(model, X_hold, hetero, 64, device); mu_t, lv_t = predict(model, X_te, hetero, 64, device)
    mu_h, mu_t = mu_h * scaler, mu_t * scaler
    Ylf_h = torch.from_numpy(y_lf[hold_rows]).view(-1, *g_lf); Yhf_h = torch.from_numpy(y_hf[hold_rows]).view(-1, *g_hf)
    Ylf_t = torch.from_numpy(yt_lf).view(-1, *g_lf); Yhf_t = torch.from_numpy(yt_hf).view(-1, *g_hf)
    Ylf_tr = torch.from_numpy(y_lf[tr_rows[:len(tr_rows) - len(pool_rows)]]).view(-1, *g_lf)
    Yhf_tr = torch.from_numpy(y_hf[tr_rows[:len(tr_rows) - len(pool_rows)]]).view(-1, *g_hf)
    reg, reg_errs = choose_registration(Ylf_tr, Yhf_tr, g_hf)
    rho = ls_gain(prolong(Ylf_tr, g_hf, reg), Yhf_tr)         # registration + gain fitted on the TRAIN paired rows (as ct_copy_lf_rho)

    def block(mu, lvr, Ylf, Yhf):
        d = {}
        e_fno = rel_l2_per_sample(mu, Ylf).numpy()
        e_gap = rel_l2_per_sample(rho * prolong(Ylf, g_hf, reg), Yhf).numpy()
        e_gap1 = rel_l2_per_sample(prolong(Ylf, g_hf, reg), Yhf).numpy()
        e_start = rel_l2_per_sample(rho * prolong(mu, g_hf, reg), Yhf).numpy()
        for nm, v in (("fno_coarse_rel_l2", e_fno), ("gap_rel_l2", e_gap), ("gap_rel_l2_rho1", e_gap1), ("pred_start_rel_l2", e_start)):
            lo, hi = bootstrap_ci(v); d[nm] = float(v.mean()); d[nm + "_ci95"] = [lo, hi]; d[nm + "_median"] = float(np.median(v))
        d["ratio_fno_to_gap"] = float(e_fno.mean() / max(e_gap.mean(), 1e-12))
        d["ratio_start_to_gap"] = float(e_start.mean() / max(e_gap.mean(), 1e-12))
        d["per_sample"] = dict(fno_coarse=e_fno.tolist(), gap=e_gap.tolist(), pred_start=e_start.tolist())
        if lvr is not None:
            sig = (0.5 * lvr).exp() * scaler; err = (mu - Ylf).abs()
            P = sig.flatten(1).numpy(); E = err.flatten(1).numpy()
            sp_pix = spearman_rows(P, E)
            d["spearman_pixel_mean"] = float(sp_pix.mean()); d["spearman_pixel_median"] = float(np.median(sp_pix))
            d["spearman_sample"] = float(spearman_rows(P.mean(1)[None], e_fno[None])[0])
            d["coverage_1sigma"] = float((E <= P).mean()); d["coverage_2sigma"] = float((E <= 2 * P).mean())
            d["nll_per_pixel"] = float((0.5 * (E ** 2 / P ** 2 + np.log(P ** 2) + math.log(2 * math.pi))).mean())
            d["sigma_mean"] = float(P.mean()); d["abs_err_mean"] = float(E.mean())
            d["sigma_over_rmse"] = float(np.sqrt((P ** 2).mean()) / max(np.sqrt((E ** 2).mean()), 1e-12))
        return d

    res = dict(code_version=CODE_VERSION, name=a.name, variant=a.variant, seed=a.seed, coarse_level=k + 1, n_levels=L,
               coarse_grid=list(g_lf), fine_grid=list(g_hf), registration=reg, registration_errors=reg_errs, rho=rho,
               paired=True, pool_rows=int(len(pool_rows)), pool_abundant=bool(len(pool_rows) > 0), hold_frac=a.hold_frac, nfolds=a.nfolds, fold=(a.fold if a.nfolds else None), split_seed=(a.split_seed if a.nfolds else None),
               n_train=int(len(tr_rows)), n_hold=int(len(hold_rows)), n_test=int(len(xt_lf)), steps=a.steps, epochs=epochs,
               beta=a.beta if hetero else None, n_params=n_params, train_seconds=train_seconds, device=str(device),
               gpu=(torch.cuda.get_device_name(0) if device.type == "cuda" else None), scaler=scaler, data_dir=str(d),
               hold=block(mu_h, lv_h, Ylf_h, Yhf_h), test=block(mu_t, lv_t, Ylf_t, Yhf_t),
               files={str(f): sha256(f) for f in (trains[k], trains[-1], tests[k], tests[-1])})
    (out / "raw").mkdir(parents=True, exist_ok=True); (out / "preds").mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out / "preds" / f"{tag}.npz", hold_rows=hold_rows, mu_hold=mu_h.numpy(), mu_test=mu_t.numpy(),
                        **({"logvar_hold": lv_h.numpy(), "logvar_test": lv_t.numpy(), "scaler": np.float32(scaler)} if hetero else {}))
    with open(out / "raw" / f"{tag}.json", "w") as f:
        json.dump(res, f, indent=1)
    h, t = res["hold"], res["test"]
    print(f"[result] {tag}: hold fno={h['fno_coarse_rel_l2']:.4g} gap={h['gap_rel_l2']:.4g} start={h['pred_start_rel_l2']:.4g} "
          f"ratio={h['ratio_fno_to_gap']:.2f} | test fno={t['fno_coarse_rel_l2']:.4g} gap={t['gap_rel_l2']:.4g} ratio={t['ratio_fno_to_gap']:.2f}"
          + (f" | sp_pix={h['spearman_pixel_mean']:.2f} sp_samp={h['spearman_sample']:.2f} cov2={h['coverage_2sigma']:.3f}" if hetero else ""), flush=True)


if __name__ == "__main__":
    main()
