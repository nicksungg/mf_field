"""LF-uncertainty methods for the FIRE ablation. Each class:
    .fit(X_lf, Y_lf, s_lf, epochs, seed)
    .summaries(X, s_lf) -> (mu (N,H,W), var (N,H,W), aug (N,5,H,W))
    .n_params() -> int
All produce the same [mu,sigma,q10,q50,q90] conditioning fields; they differ only
in how the LF predictive distribution is obtained.
"""
from __future__ import annotations

import copy
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from _common.fire_core import (FNO2d, FNOTrunk, _broadcast_cond, param_count, train_mse,
                       summaries_from_samples, gaussian_summaries, QUANTILES, _Z)


def _cfg(p):
    return dict(hidden=p["hidden_channels"], n_blocks=p["n_blocks"])


@torch.no_grad()
def _field(model, X, s, device, bs):
    model.eval(); out = []
    for i in range(0, X.shape[0], bs):
        out.append((model(torch.from_numpy(X[i:i + bs]).float().to(device)) * s).cpu().numpy())
    return np.concatenate(out, 0).astype(np.float32)


# ───────── A. sampling-based ─────────
class SnapshotLF:
    """One FNO, cyclic-cosine LR, K snapshots at the cycle minima (Huang 2017)."""
    def __init__(self, cond_dim, grid, mh, mw, device, p, K=5):
        self.p = p; self.device = device; self.K = K
        self.model = FNO2d(cond_dim, p["hidden_channels"], p["n_blocks"], mh, mw, grid).to(device)
        self.snaps = []

    def fit(self, X, Y, s_lf, epochs, seed):
        p = self.p; epc = max(1, epochs // self.K)
        Xt = torch.from_numpy(X).float(); Yt = torch.from_numpy(Y).float() / s_lf
        n = X.shape[0]; bs = min(p["batch_size"], n); g = torch.Generator().manual_seed(seed)
        opt = torch.optim.AdamW(self.model.parameters(), lr=p["lr"], weight_decay=p["weight_decay"])
        for cyc in range(self.K):
            for pg in opt.param_groups:
                pg["lr"] = p["lr"]
            sch = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epc, eta_min=1e-6)
            for _ in range(epc):
                self.model.train()
                for i in range(0, n, bs):
                    idx = torch.randperm(n, generator=g)[i:i + bs]
                    opt.zero_grad(set_to_none=True)
                    loss = F.mse_loss(self.model(Xt[idx].to(self.device)), Yt[idx].to(self.device))
                    loss.backward(); torch.nn.utils.clip_grad_norm_(self.model.parameters(), p["grad_clip"]); opt.step()
                sch.step()
            self.snaps.append(copy.deepcopy(self.model.state_dict()))

    def summaries(self, X, s_lf):
        samples = []
        for sd in self.snaps:
            self.model.load_state_dict(sd)
            samples.append(_field(self.model, X, s_lf, self.device, self.p["batch_size"]))
        return summaries_from_samples(np.stack(samples, 0), s_lf)

    def n_params(self):
        return param_count(self.model) * self.K


def _flat_real(params):
    """Flatten params (incl. complex spectral weights) into ONE real vector + meta."""
    parts, meta = [], []
    for prm in params:
        d = prm.detach()
        if d.is_complex():
            r = torch.view_as_real(d).reshape(-1); meta.append((d.shape, True, r.numel()))
        else:
            r = d.reshape(-1); meta.append((d.shape, False, r.numel()))
        parts.append(r)
    return torch.cat(parts), meta


def _unflat_real(vec, params, meta):
    i = 0
    for prm, (shape, iscplx, nel) in zip(params, meta):
        chunk = vec[i:i + nel]; i += nel
        if iscplx:
            prm.data.copy_(torch.view_as_complex(chunk.reshape(*shape, 2).contiguous()))
        else:
            prm.data.copy_(chunk.reshape(shape))


class SWAGLF:
    """One FNO; collect diagonal SWAG (weight mean + variance) over the SGD tail, sample K."""
    def __init__(self, cond_dim, grid, mh, mw, device, p, K=10, collect_frac=0.5):
        self.p = p; self.device = device; self.K = K; self.collect_frac = collect_frac
        self.model = FNO2d(cond_dim, p["hidden_channels"], p["n_blocks"], mh, mw, grid).to(device)
        self.mean = None; self.sq = None; self.meta = None

    def fit(self, X, Y, s_lf, epochs, seed):
        p = self.p
        opt = torch.optim.AdamW(self.model.parameters(), lr=p["lr"], weight_decay=p["weight_decay"])
        sch = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(epochs, 1), eta_min=p["lr"] * 0.1)
        Xt = torch.from_numpy(X).float(); Yt = torch.from_numpy(Y).float() / s_lf
        n = X.shape[0]; bs = min(p["batch_size"], n); g = torch.Generator().manual_seed(seed)
        start = int((1 - self.collect_frac) * epochs); cnt = 0
        for ep in range(epochs):
            self.model.train()
            for i in range(0, n, bs):
                idx = torch.randperm(n, generator=g)[i:i + bs]
                opt.zero_grad(set_to_none=True)
                loss = F.mse_loss(self.model(Xt[idx].to(self.device)), Yt[idx].to(self.device))
                loss.backward(); torch.nn.utils.clip_grad_norm_(self.model.parameters(), p["grad_clip"]); opt.step()
            sch.step()
            if ep >= start:
                w, self.meta = _flat_real(list(self.model.parameters()))
                self.mean = w.clone() if self.mean is None else self.mean + w
                self.sq = w * w if self.sq is None else self.sq + w * w
                cnt += 1
        self.mean /= max(cnt, 1); self.sq /= max(cnt, 1)
        self.var = torch.clamp(self.sq - self.mean ** 2, min=1e-12)
        _unflat_real(self.mean, list(self.model.parameters()), self.meta)

    def summaries(self, X, s_lf):
        params = list(self.model.parameters())
        samples = []; gen = torch.Generator(device=self.device).manual_seed(0)
        std = (0.5 * self.var).sqrt()  # scale-down for stability
        for _ in range(self.K):
            eps = torch.randn(self.mean.shape, generator=gen, device=self.device)
            _unflat_real(self.mean + std * eps, params, self.meta)
            samples.append(_field(self.model, X, s_lf, self.device, self.p["batch_size"]))
        _unflat_real(self.mean, params, self.meta)
        return summaries_from_samples(np.stack(samples, 0), s_lf)

    def n_params(self):
        return param_count(self.model)


class BatchEnsembleLF:
    """Shared FNO trunk + K independent linear output heads (cheap multi-head ensemble)."""
    class Net(nn.Module):
        def __init__(self, cond_dim, hidden, n_blocks, mh, mw, grid, K):
            super().__init__()
            self.cond_dim = cond_dim; self.grid = (int(grid[0]), int(grid[1])); self.K = K
            self.trunk = FNOTrunk(cond_dim, hidden, n_blocks, mh, mw, grid)
            self.heads = nn.ModuleList(
                nn.Sequential(nn.Conv2d(hidden, hidden, 1), nn.GELU(), nn.Conv2d(hidden, 1, 1)) for _ in range(K))

        def forward(self, x):  # -> (B, K, H, W)
            z = self.trunk(_broadcast_cond(x, self.cond_dim, self.grid))
            return torch.cat([h(z) for h in self.heads], 1)

    def __init__(self, cond_dim, grid, mh, mw, device, p, K=5):
        self.p = p; self.device = device; self.K = K
        self.model = self.Net(cond_dim, p["hidden_channels"], p["n_blocks"], mh, mw, grid, K).to(device)

    def fit(self, X, Y, s_lf, epochs, seed):
        p = self.p
        opt = torch.optim.AdamW(self.model.parameters(), lr=p["lr"], weight_decay=p["weight_decay"])
        sch = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(epochs, 1), eta_min=1e-6)
        Xt = torch.from_numpy(X).float(); Yt = torch.from_numpy(Y).float() / s_lf
        n = X.shape[0]; bs = min(p["batch_size"], n); g = torch.Generator().manual_seed(seed)
        for _ in range(epochs):
            self.model.train()
            for i in range(0, n, bs):
                idx = torch.randperm(n, generator=g)[i:i + bs]
                opt.zero_grad(set_to_none=True)
                pred = self.model(Xt[idx].to(self.device))           # (b,K,H,W)
                yb = Yt[idx].to(self.device).unsqueeze(1)
                loss = F.mse_loss(pred, yb.expand_as(pred))
                loss.backward(); torch.nn.utils.clip_grad_norm_(self.model.parameters(), p["grad_clip"]); opt.step()
            sch.step()

    @torch.no_grad()
    def summaries(self, X, s_lf):
        self.model.eval(); outs = []
        for i in range(0, X.shape[0], self.p["batch_size"]):
            xb = torch.from_numpy(X[i:i + self.p["batch_size"]]).float().to(self.device)
            outs.append((self.model(xb) * s_lf).cpu().numpy())       # (b,K,H,W)
        preds = np.concatenate(outs, 0).transpose(1, 0, 2, 3)        # (K,N,H,W)
        return summaries_from_samples(preds, s_lf)

    def n_params(self):
        return param_count(self.model)


# ───────── B. direct distribution prediction ─────────
def _pinball(pred, target, taus):
    # pred (B,Q,H,W), target (B,H,W)
    t = target.unsqueeze(1); e = t - pred
    tt = taus.view(1, -1, 1, 1)
    return torch.maximum(tt * e, (tt - 1) * e).mean()


class QuantileLF:
    """FNO with Q quantile output channels, pinball loss (direct quantile regression)."""
    def __init__(self, cond_dim, grid, mh, mw, device, p, taus=QUANTILES):
        self.p = p; self.device = device; self.taus = list(taus)
        self.model = FNO2d(cond_dim, p["hidden_channels"], p["n_blocks"], mh, mw, grid,
                           out_ch=len(self.taus)).to(device)

    def fit(self, X, Y, s_lf, epochs, seed):
        p = self.p; taus = torch.tensor(self.taus, device=self.device)
        opt = torch.optim.AdamW(self.model.parameters(), lr=p["lr"], weight_decay=p["weight_decay"])
        sch = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(epochs, 1), eta_min=1e-6)
        Xt = torch.from_numpy(X).float(); Yt = torch.from_numpy(Y).float() / s_lf
        n = X.shape[0]; bs = min(p["batch_size"], n); g = torch.Generator().manual_seed(seed)
        for _ in range(epochs):
            self.model.train()
            for i in range(0, n, bs):
                idx = torch.randperm(n, generator=g)[i:i + bs]
                opt.zero_grad(set_to_none=True)
                loss = _pinball(self.model(Xt[idx].to(self.device)), Yt[idx].to(self.device), taus)
                loss.backward(); torch.nn.utils.clip_grad_norm_(self.model.parameters(), p["grad_clip"]); opt.step()
            sch.step()

    @torch.no_grad()
    def summaries(self, X, s_lf):
        self.model.eval(); outs = []
        for i in range(0, X.shape[0], self.p["batch_size"]):
            xb = torch.from_numpy(X[i:i + self.p["batch_size"]]).float().to(self.device)
            outs.append((self.model(xb) * s_lf).cpu().numpy())       # (b,Q,H,W)
        q = np.concatenate(outs, 0)
        q = np.sort(q, axis=1)                                       # enforce monotone quantiles
        q10, q50, q90 = q[:, 0], q[:, len(self.taus) // 2], q[:, -1]
        mu = q50; sigma = np.maximum((q90 - q10) / (_Z[0.9] - _Z[0.1]), 1e-8)
        from _common.fire_core import pack_aug
        return mu.astype(np.float32), (sigma ** 2).astype(np.float32), pack_aug(mu, sigma, q10, q50, q90, s_lf)

    def n_params(self):
        return param_count(self.model)


class IQNLF:
    """Implicit Quantile Network: FNO conditioned on tau (extra input channel), pinball at random tau."""
    class Net(nn.Module):
        def __init__(self, cond_dim, hidden, n_blocks, mh, mw, grid):
            super().__init__()
            self.cond_dim = cond_dim; self.grid = (int(grid[0]), int(grid[1]))
            self.trunk = FNOTrunk(cond_dim + 1, hidden, n_blocks, mh, mw, grid)  # +1 for tau
            self.proj = nn.Sequential(nn.Conv2d(hidden, hidden, 1), nn.GELU(), nn.Conv2d(hidden, 1, 1))

        def forward(self, x, tau):  # tau: (B,)
            B = x.shape[0]; H, W = self.grid
            xg = x.view(B, self.cond_dim, 1, 1).expand(B, self.cond_dim, H, W)
            tg = tau.view(B, 1, 1, 1).expand(B, 1, H, W)
            return self.proj(self.trunk(torch.cat([xg, tg], 1))).squeeze(1)

    def __init__(self, cond_dim, grid, mh, mw, device, p):
        self.p = p; self.device = device
        self.model = self.Net(cond_dim, p["hidden_channels"], p["n_blocks"], mh, mw, grid).to(device)

    def fit(self, X, Y, s_lf, epochs, seed):
        p = self.p
        opt = torch.optim.AdamW(self.model.parameters(), lr=p["lr"], weight_decay=p["weight_decay"])
        sch = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(epochs, 1), eta_min=1e-6)
        Xt = torch.from_numpy(X).float(); Yt = torch.from_numpy(Y).float() / s_lf
        n = X.shape[0]; bs = min(p["batch_size"], n); g = torch.Generator().manual_seed(seed)
        for _ in range(epochs):
            self.model.train()
            for i in range(0, n, bs):
                idx = torch.randperm(n, generator=g)[i:i + bs]
                xb = Xt[idx].to(self.device); yb = Yt[idx].to(self.device)
                tau = torch.rand(xb.shape[0], device=self.device) * 0.98 + 0.01
                opt.zero_grad(set_to_none=True)
                pred = self.model(xb, tau); e = yb - pred
                loss = torch.maximum(tau.view(-1, 1, 1) * e, (tau.view(-1, 1, 1) - 1) * e).mean()
                loss.backward(); torch.nn.utils.clip_grad_norm_(self.model.parameters(), p["grad_clip"]); opt.step()
            sch.step()

    @torch.no_grad()
    def summaries(self, X, s_lf):
        self.model.eval(); qfields = {}
        for tau in QUANTILES:
            outs = []
            for i in range(0, X.shape[0], self.p["batch_size"]):
                xb = torch.from_numpy(X[i:i + self.p["batch_size"]]).float().to(self.device)
                tt = torch.full((xb.shape[0],), tau, device=self.device)
                outs.append((self.model(xb, tt) * s_lf).cpu().numpy())
            qfields[tau] = np.concatenate(outs, 0)
        q = np.sort(np.stack([qfields[t] for t in QUANTILES], 1), axis=1)
        q10, q50, q90 = q[:, 0], q[:, 1], q[:, 2]
        mu = q50; sigma = np.maximum((q90 - q10) / (_Z[0.9] - _Z[0.1]), 1e-8)
        from _common.fire_core import pack_aug
        return mu.astype(np.float32), (sigma ** 2).astype(np.float32), pack_aug(mu, sigma, q10, q50, q90, s_lf)

    def n_params(self):
        return param_count(self.model)


class MDNLF:
    """Mixture Density Network head: M Gaussians per pixel. MSE warm-up then clamped mixture NLL."""
    def __init__(self, cond_dim, grid, mh, mw, device, p, M=3):
        self.p = p; self.device = device; self.M = M
        self.model = FNO2d(cond_dim, p["hidden_channels"], p["n_blocks"], mh, mw, grid, out_ch=3 * M).to(device)

    def _split(self, out):  # out (B,3M,H,W) -> pi, mu, sigma
        M = self.M
        logpi = out[:, :M]; mu = out[:, M:2 * M]; logsig = torch.clamp(out[:, 2 * M:], -7.0, 3.0)
        return torch.log_softmax(logpi, dim=1), mu, torch.exp(logsig)

    def fit(self, X, Y, s_lf, epochs, seed):
        p = self.p
        opt = torch.optim.AdamW(self.model.parameters(), lr=p["lr"], weight_decay=p["weight_decay"])
        sch = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=max(epochs, 1), eta_min=1e-6)
        Xt = torch.from_numpy(X).float(); Yt = torch.from_numpy(Y).float() / s_lf
        n = X.shape[0]; bs = min(p["batch_size"], n); g = torch.Generator().manual_seed(seed)
        warm = int(0.4 * epochs)
        for ep in range(epochs):
            self.model.train()
            for i in range(0, n, bs):
                idx = torch.randperm(n, generator=g)[i:i + bs]
                xb = Xt[idx].to(self.device); yb = Yt[idx].to(self.device).unsqueeze(1)
                opt.zero_grad(set_to_none=True)
                logpi, mu, sig = self._split(self.model(xb))
                if ep < warm:
                    loss = F.mse_loss(mu.mean(1, keepdim=True), yb)  # warm up the means
                else:
                    comp = -0.5 * (((yb - mu) / sig) ** 2) - torch.log(sig) - 0.5 * np.log(2 * np.pi)
                    loss = -(torch.logsumexp(logpi + comp, dim=1)).mean()
                loss.backward(); torch.nn.utils.clip_grad_norm_(self.model.parameters(), p["grad_clip"]); opt.step()
            sch.step()

    @torch.no_grad()
    def summaries(self, X, s_lf):
        self.model.eval(); mus = []; vars = []
        for i in range(0, X.shape[0], self.p["batch_size"]):
            xb = torch.from_numpy(X[i:i + self.p["batch_size"]]).float().to(self.device)
            logpi, mu, sig = self._split(self.model(xb))
            pi = logpi.exp()
            m = (pi * mu).sum(1)                                  # mixture mean
            v = (pi * (sig ** 2 + mu ** 2)).sum(1) - m ** 2       # mixture var
            mus.append((m * s_lf).cpu().numpy()); vars.append((v * s_lf * s_lf).cpu().numpy())
        mu = np.concatenate(mus, 0); var = np.clip(np.concatenate(vars, 0), 0, None)
        sigma = np.sqrt(var + 1e-12)
        return gaussian_summaries(mu.astype(np.float32), sigma.astype(np.float32), s_lf)

    def n_params(self):
        return param_count(self.model)


# ───────── D. Gaussian-posterior (last-layer) ─────────
class _LastLayerBase:
    """Train an FNO (MSE), then a Bayesian last layer on its penultimate features."""
    def __init__(self, cond_dim, grid, mh, mw, device, p):
        self.p = p; self.device = device
        self.model = FNO2d(cond_dim, p["hidden_channels"], p["n_blocks"], mh, mw, grid).to(device)
        self.hidden = p["hidden_channels"]

    def fit(self, X, Y, s_lf, epochs, seed):
        train_mse(self.model, X, Y, s_lf, epochs, self.p, self.device, seed + 1)
        self.s_lf = s_lf
        self._fit_head(X, Y, s_lf)

    @torch.no_grad()
    def _feat(self, x):  # penultimate features (B, hidden, H, W) before final 1x1 conv
        z = self.model.trunk(_broadcast_cond(x, self.model.cond_dim, self.model.grid))
        return self.model.proj[1](self.model.proj[0](z))

    @torch.no_grad()
    def _collect(self, X, Y, s_lf, max_rows=20000):
        feats = []; ys = []
        for i in range(0, X.shape[0], self.p["batch_size"]):
            xb = torch.from_numpy(X[i:i + self.p["batch_size"]]).float().to(self.device)
            f = self._feat(xb)                                    # (b,hid,H,W)
            b, hid, H, W = f.shape
            feats.append(f.permute(0, 2, 3, 1).reshape(-1, hid).cpu())
            ys.append(torch.from_numpy(Y[i:i + self.p["batch_size"]]).reshape(-1) / s_lf)
        F_ = torch.cat(feats, 0); y_ = torch.cat(ys, 0)
        if F_.shape[0] > max_rows:
            sel = torch.linspace(0, F_.shape[0] - 1, max_rows).long()
            F_, y_ = F_[sel], y_[sel]
        return F_.to(self.device), y_.to(self.device)

    @torch.no_grad()
    def summaries(self, X, s_lf):
        mu_field = []; var_field = []
        for i in range(0, X.shape[0], self.p["batch_size"]):
            xb = torch.from_numpy(X[i:i + self.p["batch_size"]]).float().to(self.device)
            f = self._feat(xb); b, hid, H, W = f.shape
            phi = f.permute(0, 2, 3, 1).reshape(-1, hid)          # (P, hid)
            v = (phi @ self.Ainv * phi).sum(1) + self.sn2          # predictive var per pixel
            mu_field.append((self.model(xb) * s_lf).cpu().numpy())
            var_field.append((v.view(b, H, W) * s_lf * s_lf).cpu().numpy())
        mu = np.concatenate(mu_field, 0); var = np.clip(np.concatenate(var_field, 0), 1e-12, None)
        return gaussian_summaries(mu.astype(np.float32), np.sqrt(var).astype(np.float32), s_lf)

    def n_params(self):
        return param_count(self.model)


class LaplaceLF(_LastLayerBase):
    """Last-layer Laplace: Gaussian posterior on the final weights via the GGN, prior precision tau."""
    def _fit_head(self, X, Y, s_lf, prior_prec=1.0):
        F_, y_ = self._collect(X, Y, s_lf)
        w = self.model.proj[2].weight.view(-1).detach()           # (hid,)
        pred = F_ @ w
        self.sn2 = float(torch.clamp(((y_ - pred) ** 2).mean(), 1e-6, 10.0))
        A = (F_.t() @ F_) / self.sn2 + prior_prec * torch.eye(F_.shape[1], device=self.device)
        self.Ainv = torch.linalg.inv(A)


class DKLGPLF(_LastLayerBase):
    """Deep-kernel last-layer GP: Bayesian linear regression on FNO features with a learned
    output scale (marginal-likelihood-tuned noise). Distinct from Laplace by the noise estimate."""
    def _fit_head(self, X, Y, s_lf):
        F_, y_ = self._collect(X, Y, s_lf)
        hid = F_.shape[1]
        # ridge solution for the mean, residual-based noise (marginal-likelihood proxy)
        A0 = F_.t() @ F_ + 1.0 * torch.eye(hid, device=self.device)
        w = torch.linalg.solve(A0, F_.t() @ y_)
        self.sn2 = float(torch.clamp(((y_ - F_ @ w) ** 2).mean(), 1e-6, 10.0))
        A = (F_.t() @ F_) / self.sn2 + torch.eye(hid, device=self.device)
        self.Ainv = torch.linalg.inv(A)
