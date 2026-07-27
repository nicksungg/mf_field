"""mf_fno_diffprior — latent PDE prior + conditional latent generation (OAT-style).

Pipeline
--------
1. A small PDE-native CONVOLUTIONAL autoencoder (AE) over fields on the working
   grid: encode (1,H,W) -> spatial latent (C,h,w) -> flatten -> z (zdim), and
   decode z -> field. The AE is trained to reconstruct the ABUNDANT LF fields,
   giving a learned PRIOR over field shapes.
2. A conditional latent GENERATOR: from [X, z_lf] -> z_hf. Shipped as a COMPACT
   conditional DDIM denoiser (tiny eps-MLP conditioned on [X, z_lf, t-embed],
   eps-prediction, cosine schedule, few-step DDIM sampling). A plain conditional
   MLP regressor is provided as a fallback (`LatentMLPGenerator`).
3. Decode the generated z_hf -> HF field. Sampling K times gives free
   per-pixel uncertainty (std across samples).

The AE encoder/decoder are EXPORTED (ae.pt) and exposed via importable
`encode()` / `decode()` so a future latent-analysis family can reuse the SAME
autoencoder.

Inspired by: nobari2025oat (operator-attentive / latent operator transfer),
rombach2022ldm (latent diffusion), chung2023dps (diffusion posterior /
conditional generation), ho2020ddpm (DDPM).
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F


# ───────────────────────── Convolutional Autoencoder ─────────────────────────
class ConvAE(nn.Module):
    """PDE-native conv AE: field (B,1,H,W) <-> flat latent z (B, zdim).

    Encoder downsamples to a small (C,h,w) spatial latent, flattens, and linearly
    projects to zdim. Decoder reverses it. `latent_hw` is fixed so the latent is
    grid-size-agnostic (we adaptive-pool to it), making the AE reusable across
    working grids.
    """

    def __init__(self, base_ch: int = 32, latent_ch: int = 16,
                 latent_hw: Tuple[int, int] = (4, 4), zdim: int = 64):
        super().__init__()
        self.latent_ch = latent_ch
        self.latent_hw = latent_hw
        self.zdim = zdim
        flat = latent_ch * latent_hw[0] * latent_hw[1]
        self.enc = nn.Sequential(
            nn.Conv2d(1, base_ch, 3, stride=2, padding=1), nn.GELU(),       # H/2
            nn.Conv2d(base_ch, base_ch * 2, 3, stride=2, padding=1), nn.GELU(),  # H/4
            nn.Conv2d(base_ch * 2, latent_ch, 3, stride=1, padding=1),      # latent_ch
        )
        self.to_z = nn.Linear(flat, zdim)
        self.from_z = nn.Linear(zdim, flat)
        self.dec = nn.Sequential(
            nn.Conv2d(latent_ch, base_ch * 2, 3, stride=1, padding=1), nn.GELU(),
            nn.Conv2d(base_ch * 2, base_ch, 3, stride=1, padding=1), nn.GELU(),
            nn.Conv2d(base_ch, 1, 3, stride=1, padding=1),
        )

    def encode(self, field: torch.Tensor) -> torch.Tensor:
        """(B,1,H,W) or (B,H,W) -> z (B, zdim)."""
        if field.dim() == 3:
            field = field.unsqueeze(1)
        h = self.enc(field)
        h = F.adaptive_avg_pool2d(h, self.latent_hw)        # (B, latent_ch, lh, lw)
        z = self.to_z(h.flatten(1))
        return z

    def decode(self, z: torch.Tensor, grid: Tuple[int, int]) -> torch.Tensor:
        """z (B, zdim) -> field (B, H, W) on `grid`."""
        B = z.shape[0]
        h = self.from_z(z).view(B, self.latent_ch, *self.latent_hw)
        h = F.interpolate(h, size=grid, mode="bilinear", align_corners=False)
        return self.dec(h).squeeze(1)

    def forward(self, field: torch.Tensor, grid: Tuple[int, int]) -> torch.Tensor:
        return self.decode(self.encode(field), grid)


# ───────────────────── timestep embedding (sinusoidal) ───────────────────────
def timestep_embedding(t: torch.Tensor, dim: int) -> torch.Tensor:
    half = dim // 2
    freqs = torch.exp(-math.log(10000.0) * torch.arange(half, device=t.device) / max(half, 1))
    a = t.float().unsqueeze(-1) * freqs.unsqueeze(0)
    emb = torch.cat([torch.sin(a), torch.cos(a)], dim=-1)
    if dim % 2:
        emb = F.pad(emb, (0, 1))
    return emb


# ──────────────── conditional DDIM latent generator (eps-net) ────────────────
class LatentDDIM(nn.Module):
    """Tiny conditional eps-MLP over z_hf, conditioned on [X, z_lf, t-embed].

    Cosine-schedule DDPM training (predict eps); deterministic few-step DDIM
    sampling at inference. Kept small so smoke runs in seconds.
    """

    def __init__(self, zdim: int, cond_dim: int, lf_dim: int,
                 hidden: int = 256, t_emb: int = 64, n_steps: int = 200):
        super().__init__()
        self.zdim = zdim
        self.t_emb = t_emb
        self.n_steps = n_steps
        in_dim = zdim + cond_dim + lf_dim + t_emb
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden), nn.GELU(),
            nn.Linear(hidden, hidden), nn.GELU(),
            nn.Linear(hidden, zdim),
        )
        betas = self._cosine_betas(n_steps)
        alphas = 1.0 - betas
        acp = torch.cumprod(alphas, dim=0)
        self.register_buffer("alphas_cumprod", acp)

    @staticmethod
    def _cosine_betas(T: int, s: float = 0.008) -> torch.Tensor:
        steps = torch.arange(T + 1, dtype=torch.float64)
        f = torch.cos(((steps / T) + s) / (1 + s) * math.pi / 2) ** 2
        acp = f / f[0]
        betas = 1.0 - (acp[1:] / acp[:-1])
        return betas.clamp(1e-6, 0.999).float()

    def eps(self, z_t, t, cond, z_lf):
        te = timestep_embedding(t, self.t_emb)
        return self.net(torch.cat([z_t, cond, z_lf, te], dim=-1))

    def loss(self, z0, cond, z_lf):
        B = z0.shape[0]
        t = torch.randint(0, self.n_steps, (B,), device=z0.device)
        acp = self.alphas_cumprod[t].unsqueeze(-1)
        noise = torch.randn_like(z0)
        z_t = acp.sqrt() * z0 + (1 - acp).sqrt() * noise
        pred = self.eps(z_t, t, cond, z_lf)
        return F.mse_loss(pred, noise)

    @torch.no_grad()
    def sample(self, cond, z_lf, n_ddim: int = 10, generator=None, z0_clamp: float = 4.0):
        """Few-step DDIM. Latents are assumed standardized (~unit variance), so
        the predicted z0 is clamped to +/- z0_clamp to keep the trajectory on the
        trained manifold (low-data stability)."""
        B = cond.shape[0]
        dev = cond.device
        z = torch.randn(B, self.zdim, device=dev, generator=generator)
        ts = torch.linspace(self.n_steps - 1, 0, n_ddim, device=dev).round().long()
        for i in range(len(ts)):
            t = ts[i].expand(B)
            acp_t = self.alphas_cumprod[t].unsqueeze(-1)
            eps = self.eps(z, t, cond, z_lf)
            z0 = (z - (1 - acp_t).sqrt() * eps) / acp_t.sqrt().clamp(min=1e-8)
            if z0_clamp is not None:
                z0 = z0.clamp(-z0_clamp, z0_clamp)
            if i < len(ts) - 1:
                t_next = ts[i + 1].expand(B)
                acp_n = self.alphas_cumprod[t_next].unsqueeze(-1)
                z = acp_n.sqrt() * z0 + (1 - acp_n).sqrt() * eps
            else:
                z = z0
        return z


# ───────────────────── conditional MLP fallback generator ────────────────────
class LatentMLPGenerator(nn.Module):
    """Plain [X, z_lf] -> z_hf regressor (fallback if diffusion is unstable)."""

    def __init__(self, zdim: int, cond_dim: int, lf_dim: int, hidden: int = 256):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(cond_dim + lf_dim, hidden), nn.GELU(),
            nn.Linear(hidden, hidden), nn.GELU(),
            nn.Linear(hidden, zdim),
        )

    def forward(self, cond, z_lf):
        return self.net(torch.cat([cond, z_lf], dim=-1))


def param_count(*modules) -> int:
    return sum(p.numel() for m in modules for p in m.parameters())


# ─────────────── importable encode/decode using the exported ae.pt ───────────
_AE_CACHE = {}


def _load_ae(ae_path: str | Path = None, device="cpu") -> ConvAE:
    ae_path = Path(ae_path) if ae_path else Path(__file__).resolve().parent / "ae.pt"
    key = str(ae_path)
    if key in _AE_CACHE:
        return _AE_CACHE[key]
    sd = torch.load(ae_path, map_location=device, weights_only=False)
    cfg = sd["config"]
    ae = ConvAE(base_ch=cfg["base_ch"], latent_ch=cfg["latent_ch"],
                latent_hw=tuple(cfg["latent_hw"]), zdim=cfg["zdim"]).to(device)
    ae.load_state_dict(sd["ae"])
    ae.eval()
    _AE_CACHE[key] = ae
    return ae


def encode(field: torch.Tensor, ae_path: str | Path = None, device="cpu") -> torch.Tensor:
    """Importable: field (B,H,W) -> latent z (B, zdim), using the exported ae.pt.

    Reuse this SAME autoencoder from a future latent-analysis family.
    """
    ae = _load_ae(ae_path, device)
    return ae.encode(field.to(device))


def decode(z: torch.Tensor, grid, ae_path: str | Path = None, device="cpu") -> torch.Tensor:
    """Importable: latent z (B, zdim) -> field (B,H,W) on `grid`, via ae.pt."""
    ae = _load_ae(ae_path, device)
    return ae.decode(z.to(device), (int(grid[0]), int(grid[1])))
