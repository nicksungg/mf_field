"""Corrector backbones for stage 2b.  Both map (theta, start field h, optional extra channels) -> correction field, are
FiLM-conditioned on theta at every block, start as the identity (zero-init output), and are 1-D safe (H == 1 grids).

  Refiner        : MF-IRNO's 3-level conv U-Net (experiments/bench_ct/ct_mfirno.py), verbatim except that the input may carry
                   extra channels (ensemble spread, hetero sigma) next to the field and the two coordinate channels.
  ConvNeXtUNet   : operator_library/models/convnext_unet_film (liu2022convnext + ronneberger2015unet) with the winner's FiLMNorm in place of
                   LayerNorm, adapted from a theta-only surrogate to a corrector: the lift takes [coords, h, extra] and the head is
                   zero-initialised so the first iterate is the start field.
"""
from __future__ import annotations
import math, os, sys
from pathlib import Path
import torch
import torch.nn as nn
import torch.nn.functional as F

MF = Path(os.environ.get("MF_ROOT", "/archive/mf_field"))
sys.path.insert(0, str(MF / "factory_mffp/models/mf_fno_transfer_film"))
from model import FiLMNorm  # noqa: E402  (GroupNorm + zero-init FiLM affine from theta)


def coordinates(grid, reg, device):
    """Same registration-aware coordinate grid as ct_mfirno.coordinates."""
    axes = []
    for n in grid:
        if reg == "interior_dirichlet":
            x = (torch.arange(n, device=device) + 1) / (n + 1)
        else:
            off = 0.5 if reg == "periodic_cell" else 0.0
            x = (torch.arange(n, device=device) + off) / n
        axes.append(x * 2 - 1)
    gy, gx = torch.meshgrid(*axes, indexing="ij")
    return torch.stack((gy, gx), 0)[None].float()


# ----------------------------------------------------------------------------- MF-IRNO refiner (ct_mfirno.py)
class ConvBlock(nn.Module):
    def __init__(self, cin, cout, cond_dim):
        super().__init__()
        self.conv1 = nn.Conv2d(cin, cout, 3, padding=1); self.norm1 = nn.GroupNorm(math.gcd(8, cout), cout, affine=False)
        self.conv2 = nn.Conv2d(cout, cout, 3, padding=1); self.norm2 = nn.GroupNorm(math.gcd(8, cout), cout, affine=False)
        self.affine = nn.Sequential(nn.Linear(cond_dim, 64), nn.SiLU(), nn.Linear(64, 4 * cout))
        nn.init.zeros_(self.affine[-1].weight); nn.init.zeros_(self.affine[-1].bias)
        self.skip = nn.Conv2d(cin, cout, 1) if cin != cout else nn.Identity()

    def forward(self, x, cond):
        g1, b1, g2, b2 = self.affine(cond)[:, :, None, None].chunk(4, 1)
        z = F.silu(self.norm1(self.conv1(x)) * (1 + g1) + b1)
        z = self.norm2(self.conv2(z)) * (1 + g2) + b2
        return F.silu(z + self.skip(x))


class Refiner(nn.Module):
    def __init__(self, cond_dim, coords, width=32, n_extra=0):
        super().__init__()
        self.register_buffer("coords", coords.clone()); self.n_extra = n_extra
        self.pool = (1 if coords.shape[-2] == 1 else 2, 2)
        self.enc = ConvBlock(3 + n_extra, width, cond_dim); self.mid = ConvBlock(width, 2 * width, cond_dim); self.low = ConvBlock(2 * width, 4 * width, cond_dim)
        self.up1 = ConvBlock(6 * width, 2 * width, cond_dim); self.up2 = ConvBlock(3 * width, width, cond_dim)
        self.out = nn.Conv2d(width, 1, 1); nn.init.zeros_(self.out.weight); nn.init.zeros_(self.out.bias)

    def forward(self, cond, h, extra=None):
        parts = [h[:, None], self.coords.expand(len(h), -1, -1, -1)] + ([extra] if extra is not None else [])
        a = self.enc(torch.cat(parts, 1), cond)
        b = self.mid(F.avg_pool2d(a, self.pool), cond)
        c = self.low(F.avg_pool2d(b, self.pool), cond)
        z = self.up1(torch.cat((F.interpolate(c, size=b.shape[-2:], mode="bilinear", align_corners=False), b), 1), cond)
        z = self.up2(torch.cat((F.interpolate(z, size=a.shape[-2:], mode="bilinear", align_corners=False), a), 1), cond)
        return self.out(z)[:, 0]


# ----------------------------------------------------------------------------- ConvNeXt-U-Net-FiLM corrector
def _stride(is_1d): return (1, 2) if is_1d else (2, 2)


def _match(z, ref):
    dh = ref.shape[-2] - z.shape[-2]; dw = ref.shape[-1] - z.shape[-1]
    if dh > 0 or dw > 0:
        z = F.pad(z, (0, max(dw, 0), 0, max(dh, 0)))
    return z[..., :ref.shape[-2], :ref.shape[-1]]


class ConvNeXtBlock(nn.Module):
    """dwconv7x7 -> FiLMNorm(., theta) -> pw C->4C -> GELU -> pw 4C->C, residual (liu2022convnext with FiLM in place of LN)."""

    def __init__(self, channels, cond_dim, cond_feat_dim=64, expansion=4):
        super().__init__()
        self.dwconv = nn.Conv2d(channels, channels, 7, padding=3, groups=channels)
        self.norm = FiLMNorm(channels, cond_dim, cond_feat_dim=cond_feat_dim)
        self.pw1 = nn.Conv2d(channels, expansion * channels, 1); self.act = nn.GELU(); self.pw2 = nn.Conv2d(expansion * channels, channels, 1)

    def forward(self, x, cond):
        return x + self.pw2(self.act(self.pw1(self.norm(self.dwconv(x), cond))))


class Stage(nn.Module):
    def __init__(self, channels, n_blocks, cond_dim, cond_feat_dim=64):
        super().__init__()
        self.blocks = nn.ModuleList(ConvNeXtBlock(channels, cond_dim, cond_feat_dim) for _ in range(n_blocks))

    def forward(self, x, cond):
        for blk in self.blocks:
            x = blk(x, cond)
        return x


class ConvNeXtUNet(nn.Module):
    """(theta, h, extra) -> correction on the fixed grid.  3-level encoder-decoder, channels base*2^i, ConvNeXt blocks with FiLM."""

    def __init__(self, cond_dim, coords, base=48, n_levels=3, blocks_per_stage=2, n_extra=0, cond_feat_dim=64):
        super().__init__()
        self.register_buffer("coords", coords.clone()); self.n_extra = n_extra
        H, W = coords.shape[-2:]; self.grid = (int(H), int(W)); self.is_1d = (H == 1); self.n_levels = n_levels; self.mult = 2 ** n_levels
        st = _stride(self.is_1d); chs = [base * (2 ** i) for i in range(n_levels + 1)]
        self.lift = nn.Conv2d(3 + n_extra, chs[0], 1)
        self.enc_stages = nn.ModuleList(Stage(chs[i], blocks_per_stage, cond_dim, cond_feat_dim) for i in range(n_levels))
        self.downs = nn.ModuleList(nn.Conv2d(chs[i], chs[i + 1], kernel_size=st, stride=st) for i in range(n_levels))
        self.bottleneck = Stage(chs[-1], blocks_per_stage, cond_dim, cond_feat_dim)
        self.ups = nn.ModuleList(nn.ConvTranspose2d(chs[i + 1], chs[i], kernel_size=st, stride=st) for i in reversed(range(n_levels)))
        self.reduces = nn.ModuleList(nn.Conv2d(2 * chs[i], chs[i], 1) for i in reversed(range(n_levels)))
        self.dec_stages = nn.ModuleList(Stage(chs[i], blocks_per_stage, cond_dim, cond_feat_dim) for i in reversed(range(n_levels)))
        self.head = nn.Sequential(nn.Conv2d(chs[0], chs[0], 1), nn.GELU(), nn.Conv2d(chs[0], 1, 1))
        nn.init.zeros_(self.head[-1].weight); nn.init.zeros_(self.head[-1].bias)       # identity start, like the refiner

    def forward(self, cond, h, extra=None):
        B = h.shape[0]; H, W = self.grid
        parts = [self.coords.expand(B, -1, -1, -1), h[:, None]] + ([extra] if extra is not None else [])
        x = torch.cat(parts, 1)
        Wp = -(-W // self.mult) * self.mult; Hp = H if self.is_1d else -(-H // self.mult) * self.mult
        x = F.pad(x, (0, Wp - W, 0, Hp - H), mode="replicate")
        z = self.lift(x); skips = []
        for stage, down in zip(self.enc_stages, self.downs):
            z = stage(z, cond); skips.append(z); z = down(z)
        z = self.bottleneck(z, cond)
        for up, reduce, stage in zip(self.ups, self.reduces, self.dec_stages):
            z = up(z); skip = skips.pop(); z = _match(z, skip); z = reduce(torch.cat([z, skip], 1)); z = stage(z, cond)
        return self.head(z)[:, 0, :H, :W]


def build(backbone, cond_dim, coords, n_extra, width=32, base=48):
    if backbone == "irno":
        return Refiner(cond_dim, coords, width=width, n_extra=n_extra)
    if backbone == "convnext":
        return ConvNeXtUNet(cond_dim, coords, base=base, n_extra=n_extra)
    raise ValueError(backbone)


# ----------------------------------------------------------------------------- Transolver corrector (wu2024transolver, FiLM on theta)
class SinPE(nn.Module):
    """Sinusoidal encoding of grid coordinates in [-1, 1] (as transolver_residual.SinusoidalPE, 2-D)."""

    def __init__(self, coord_dim=2, num_freqs=6):
        super().__init__()
        self.register_buffer("freqs", (2.0 ** torch.arange(num_freqs)) * math.pi); self.out_dim = coord_dim * 2 * num_freqs

    def forward(self, c):                                   # (..., coord_dim) -> (..., out_dim)
        a = c[..., None] * self.freqs; return torch.cat([a.sin(), a.cos()], -1).flatten(-2)


class TokenFiLM(nn.Module):
    def __init__(self, cond_dim, dim, hidden=64):
        super().__init__(); self.net = nn.Sequential(nn.Linear(cond_dim, hidden), nn.GELU(), nn.Linear(hidden, 2 * dim))
        nn.init.zeros_(self.net[-1].weight); nn.init.zeros_(self.net[-1].bias)

    def forward(self, x, cond):                             # x (B, N, D)
        g, b = self.net(cond).chunk(2, -1); return (1.0 + g)[:, None] * x + b[:, None]


class PhysicsAttention(nn.Module):
    """Transolver physics attention: tokens -> S learned slices (softmax over tokens) -> multi-head attention from tokens to slices."""

    def __init__(self, dim, n_slices=32, heads=4):
        super().__init__(); self.h, self.hd = heads, dim // heads
        self.slice_proj = nn.Linear(dim, n_slices); self.v_proj = nn.Linear(dim, dim)
        self.q = nn.Linear(dim, dim, bias=False); self.k = nn.Linear(dim, dim, bias=False); self.v = nn.Linear(dim, dim, bias=False); self.o = nn.Linear(dim, dim)

    def forward(self, x):                                   # (B, N, D)
        B, N, D = x.shape
        sw = F.softmax(self.slice_proj(x), dim=1)           # (B, N, S): each slice is a soft group of tokens
        keys = torch.einsum("bnk,bnd->bkd", sw, x); vals = torch.einsum("bnk,bnd->bkd", sw, self.v_proj(x))
        sh = lambda t: t.reshape(B, -1, self.h, self.hd).transpose(1, 2)
        a = F.softmax(torch.einsum("bhnd,bhkd->bhnk", sh(self.q(x)), sh(self.k(keys))) / math.sqrt(self.hd), dim=-1)
        return self.o(torch.einsum("bhnk,bhkd->bhnd", a, sh(self.v(vals))).transpose(1, 2).reshape(B, N, D))


class TBlock(nn.Module):
    def __init__(self, dim, cond_dim, n_slices, heads):
        super().__init__(); self.ln1 = nn.LayerNorm(dim); self.attn = PhysicsAttention(dim, n_slices, heads); self.film1 = TokenFiLM(cond_dim, dim)
        self.ln2 = nn.LayerNorm(dim); self.mlp = nn.Sequential(nn.Linear(dim, 2 * dim), nn.GELU(), nn.Linear(2 * dim, dim)); self.film2 = TokenFiLM(cond_dim, dim)

    def forward(self, x, cond):
        x = x + self.film1(self.attn(self.ln1(x)), cond)
        return x + self.film2(self.mlp(self.ln2(x)), cond)


class TransolverCorr(nn.Module):
    """(theta, h, extra) -> correction: every fine-grid cell is a token [coords, h, extras, PE(coords)]; n_layers Transolver blocks
    (physics-slice attention + MLP, pre-LN, residual) with zero-init FiLM from theta after each sub-block; zero-init head."""

    def __init__(self, cond_dim, coords, n_extra=0, hidden=128, n_layers=3, n_slices=32, heads=4, pe_freqs=6):
        super().__init__()
        H, W = coords.shape[-2:]; self.grid = (int(H), int(W)); self.n_extra = n_extra
        c = coords[0].permute(1, 2, 0).reshape(1, H * W, 2).detach().cpu(); self.register_buffer("tok_coords", c.clone())
        self.pe = SinPE(2, pe_freqs); self.register_buffer("tok_pe", self.pe(c))        # built on CPU; .to(device) moves all buffers
        self.enc = nn.Sequential(nn.Linear(3 + n_extra + self.pe.out_dim, hidden), nn.GELU(), nn.Linear(hidden, hidden), nn.GELU(), nn.Linear(hidden, hidden))
        self.enc_ln = nn.LayerNorm(hidden); self.enc_film = TokenFiLM(cond_dim, hidden)
        self.blocks = nn.ModuleList(TBlock(hidden, cond_dim, n_slices, heads) for _ in range(n_layers))
        self.head = nn.Sequential(nn.LayerNorm(hidden), nn.Linear(hidden, hidden), nn.GELU(), nn.Linear(hidden, 1))
        for name, m in self.named_modules():
            if isinstance(m, nn.Linear) and "film" not in name and "head" not in name:
                nn.init.xavier_uniform_(m.weight); (nn.init.zeros_(m.bias) if m.bias is not None else None)
        nn.init.zeros_(self.head[-1].weight); nn.init.zeros_(self.head[-1].bias)

    def forward(self, cond, h, extra=None):
        B = h.shape[0]; H, W = self.grid; N = H * W
        parts = [self.tok_coords.expand(B, -1, -1), h.reshape(B, N, 1)]
        if extra is not None: parts.append(extra.reshape(B, extra.shape[1], N).transpose(1, 2))
        parts.append(self.tok_pe.expand(B, -1, -1))
        x = self.enc_film(self.enc_ln(self.enc(torch.cat(parts, -1))), cond)
        for blk in self.blocks:
            x = blk(x, cond)
        return self.head(x)[..., 0].reshape(B, H, W)


_build = build
def build(backbone, cond_dim, coords, n_extra, width=32, base=48, hidden=128, n_layers=3):
    if backbone == "transolver":
        return TransolverCorr(cond_dim, coords, n_extra=n_extra, hidden=hidden, n_layers=n_layers)
    return _build(backbone, cond_dim, coords, n_extra, width=width, base=base)
