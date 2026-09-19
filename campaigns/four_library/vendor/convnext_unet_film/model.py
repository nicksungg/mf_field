"""FiLM-conditioned ConvNeXt-U-Net operator (liu2022convnext + ronneberger2015unet), 1-D & rect safe.

This is the benchmark-winning FNO+FiLM-transfer model
(`factory_mffp/models/mf_fno_transfer_film/model.py` / `operator_library/common/backbone.py`)
with ONE change: the Fourier/FNO backbone is replaced by a **ConvNeXt-U-Net**
(an encoder-decoder CNN whose residual blocks are ConvNeXt blocks). Everything
else is byte-for-byte the winner:

* Input = the 2 coordinate channels ONLY (a fixed y/x meshgrid on the working
  grid). The condition vector X NEVER enters by concatenation — it modulates
  every block via FiLM.
* Conditioning = per-block `FiLMNorm(channels, cond_dim=X)` from
  `common.backbone`, used IN PLACE of ConvNeXt's usual LayerNorm, so the
  conditioning mechanism is identical to the winner.
* The multi-fidelity mechanism (LF-pretrain -> HF-finetune transfer) lives
  entirely in smoke_eval.py, unchanged.

This isolates the BACKBONE (spectral FNO vs convolutional ConvNeXt-U-Net) while
holding conditioning + transfer schedule fixed.

ConvNeXt block(C) (liu2022convnext)
-----------------------------------
depthwise Conv2d(C,C,k=7,pad=3,groups=C) -> FiLMNorm(C, cond=X) ->
pointwise Conv2d(C,4C,1) -> GELU -> pointwise Conv2d(4C,C,1), with a residual
add `x + block(x)`. A 7x7 conv with pad=3 keeps a height-1 (H==1, 1-D) input at
height 1, so the block itself is 1-D-safe.

U-Net (ronneberger2015unet)
---------------------------
lift Conv2d(2->base) ; 3-stage encoder (ConvNeXt blocks then downsample x2,
channels 48->96->192->384 bottleneck) ; 3-stage decoder (upsample x2, concat the
matching encoder skip, ConvNeXt blocks) ; head Conv2d(base->base,1)->GELU->
Conv2d(base->1,1).

1-D-SAFETY (a U-Net downsamples, which is exactly what breaks on height-1 grids)
-------------------------------------------------------------------------------
Down/up-sampling is ADAPTIVE to ndim. When H==1 (1-D, grid (1,L)) the strided
down-conv and the transposed up-conv use stride (1,2) — they NEVER touch the
height axis, so the height-1 axis survives all 3 down/up stages. When H>1 (2-D)
they use stride (2,2). A 3-level U-Net needs each downsampled axis divisible by
8; the input is circular/edge padded up to the next multiple of 8 on the
downsampled axes (W always; H only when H>1), run through the net, then cropped
back to the true (H,W). Skips are size-matched (crop/pad) defensively.

References: liu2022convnext (ConvNeXt blocks, arXiv:2201.03545); ronneberger2015unet
(U-Net encoder-decoder + skips, arXiv:1505.04597); perez2018film (FiLM);
lyu2023mffno (LF->HF transfer schedule, retained in smoke_eval.py).
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

# ── make common.backbone importable even if model.py is loaded standalone ──
_MODEL_LIBRARY = Path(__file__).resolve().parents[2]            # …/mf_field/operator_library
if str(_MODEL_LIBRARY) not in sys.path:
    sys.path.insert(0, str(_MODEL_LIBRARY))
from common.backbone import FiLMNorm, param_count        # noqa: E402  (identical conditioning)

Grid = Tuple[int, int]


def _stride(is_1d: bool) -> Tuple[int, int]:
    """Down/up-sampling stride: never touch the height axis in 1-D (H==1)."""
    return (1, 2) if is_1d else (2, 2)


def _match(z: torch.Tensor, ref: torch.Tensor) -> torch.Tensor:
    """Crop/pad z spatially to match ref's (H, W) — defensive skip alignment."""
    dh = ref.shape[-2] - z.shape[-2]
    dw = ref.shape[-1] - z.shape[-1]
    if dh > 0 or dw > 0:
        z = F.pad(z, (0, max(dw, 0), 0, max(dh, 0)))
    if z.shape[-2] > ref.shape[-2] or z.shape[-1] > ref.shape[-1]:
        z = z[..., :ref.shape[-2], :ref.shape[-1]]
    return z


class ConvNeXtBlock(nn.Module):
    """ConvNeXt block with FiLMNorm (X-conditioned) replacing the usual LayerNorm.

    dwconv7x7 -> FiLMNorm(., X) -> pwconv(C->4C) -> GELU -> pwconv(4C->C), residual.
    The 7x7 depthwise conv with pad=3 preserves H (incl. H==1), so 1-D-safe.
    """

    def __init__(self, channels: int, cond_dim: int, cond_feat_dim: int = 64,
                 expansion: int = 4):
        super().__init__()
        self.dwconv = nn.Conv2d(channels, channels, kernel_size=7, padding=3, groups=channels)
        self.norm = FiLMNorm(channels, cond_dim, cond_feat_dim=cond_feat_dim)
        self.pw1 = nn.Conv2d(channels, expansion * channels, 1)
        self.act = nn.GELU()
        self.pw2 = nn.Conv2d(expansion * channels, channels, 1)

    def forward(self, x: torch.Tensor, cond: torch.Tensor) -> torch.Tensor:
        h = self.dwconv(x)
        h = self.norm(h, cond)
        h = self.pw2(self.act(self.pw1(h)))
        return x + h


class Stage(nn.Module):
    """A run of ConvNeXt blocks that all share the same channel width."""

    def __init__(self, channels: int, n_blocks: int, cond_dim: int, cond_feat_dim: int = 64):
        super().__init__()
        self.blocks = nn.ModuleList(
            ConvNeXtBlock(channels, cond_dim, cond_feat_dim=cond_feat_dim)
            for _ in range(n_blocks)
        )

    def forward(self, x: torch.Tensor, cond: torch.Tensor) -> torch.Tensor:
        for blk in self.blocks:
            x = blk(x, cond)
        return x


class ConvNeXtUNet2d(nn.Module):
    """cond vector (B, cond_dim) -> field (B, H, W) on a fixed working grid.

    Backbone swap of the FNO+FiLM winner: a 3-level ConvNeXt-U-Net over the
    coordinate grid, X injected via per-block FiLM. Down/up-sampling is
    ndim-adaptive so height-1 (1-D) grids survive the encoder-decoder.
    """

    def __init__(self, cond_dim: int, base: int = 48, n_levels: int = 3,
                 blocks_per_stage: int = 2, grid: Grid = (64, 64),
                 cond_feat_dim: int = 64):
        super().__init__()
        self.cond_dim = cond_dim
        self.grid = (int(grid[0]), int(grid[1]))
        self.is_1d = (self.grid[0] == 1)
        self.n_levels = n_levels
        self.mult = 2 ** n_levels                          # divisibility requirement
        st = _stride(self.is_1d)

        # channel schedule: base, 2*base, 4*base, ... (bottleneck = base * 2**n_levels)
        chs = [base * (2 ** i) for i in range(n_levels + 1)]   # e.g. [48,96,192,384]

        self.lift = nn.Conv2d(2, chs[0], 1)                # coordinates only -> base

        # encoder: per level a Stage at chs[i] (skip), then a strided down-conv to chs[i+1]
        self.enc_stages = nn.ModuleList(
            Stage(chs[i], blocks_per_stage, cond_dim, cond_feat_dim) for i in range(n_levels)
        )
        self.downs = nn.ModuleList(
            nn.Conv2d(chs[i], chs[i + 1], kernel_size=st, stride=st) for i in range(n_levels)
        )

        # bottleneck Stage at chs[-1]
        self.bottleneck = Stage(chs[-1], blocks_per_stage, cond_dim, cond_feat_dim)

        # decoder: per level a transposed up-conv chs[i+1]->chs[i], concat skip (chs[i]),
        # a 1x1 reduce (2*chs[i] -> chs[i]), then a Stage at chs[i]. Reversed order.
        self.ups = nn.ModuleList(
            nn.ConvTranspose2d(chs[i + 1], chs[i], kernel_size=st, stride=st)
            for i in reversed(range(n_levels))
        )
        self.reduces = nn.ModuleList(
            nn.Conv2d(2 * chs[i], chs[i], 1) for i in reversed(range(n_levels))
        )
        self.dec_stages = nn.ModuleList(
            Stage(chs[i], blocks_per_stage, cond_dim, cond_feat_dim)
            for i in reversed(range(n_levels))
        )

        self.head = nn.Sequential(
            nn.Conv2d(chs[0], chs[0], 1), nn.GELU(),
            nn.Conv2d(chs[0], 1, 1),
        )

        H, W = self.grid
        ys = torch.linspace(-1.0, 1.0, H)
        xs = torch.linspace(-1.0, 1.0, W)
        gy, gx = torch.meshgrid(ys, xs, indexing="ij")
        self.register_buffer("coord_grid", torch.stack([gy, gx], dim=0).unsqueeze(0))

    def _pad_input(self, coords: torch.Tensor) -> Tuple[torch.Tensor, int, int]:
        """Pad downsampled axes up to a multiple of `mult`; return (padded, H, W)."""
        H, W = self.grid
        Wp = ((W + self.mult - 1) // self.mult) * self.mult
        Hp = H if self.is_1d else ((H + self.mult - 1) // self.mult) * self.mult
        coords = F.pad(coords, (0, Wp - W, 0, Hp - H), mode="replicate")
        return coords, H, W

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B = x.shape[0]
        H, W = self.grid
        coords = self.coord_grid.expand(B, 2, H, W)
        coords, H0, W0 = self._pad_input(coords)

        z = self.lift(coords)
        skips: List[torch.Tensor] = []
        for stage, down in zip(self.enc_stages, self.downs):
            z = stage(z, x)
            skips.append(z)
            z = down(z)

        z = self.bottleneck(z, x)

        for up, reduce, stage in zip(self.ups, self.reduces, self.dec_stages):
            z = up(z)
            skip = skips.pop()
            z = _match(z, skip)
            z = reduce(torch.cat([z, skip], dim=1))
            z = stage(z, x)

        out = self.head(z)                     # (B, 1, Hp, Wp)
        out = out[..., :H0, :W0]               # crop back to true (H, W)
        return out.squeeze(1)                  # (B, H, W)
