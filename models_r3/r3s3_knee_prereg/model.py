"""`CoverageDecoder` — condition -> field decoder with a PINNED mode budget.

Card `r2s3_lf_train_signal-B3` part 3, verbatim:

    `CoverageDecoder(cond_dim, width=64, blocks=4)`,
    `forward(cond, out_hw) -> (B,H,W)`; coord channels at forward time; lift
    2->64; 4x [SpectralConv2d(alpha) + 1x1 conv + FiLM(cond) after GroupNorm +
    GELU]; projection 64->128->1; FFT `norm="forward"`.

PROVENANCE (card `recipe.base_family`, verbatim): this is a WITHIN-STREAM
continuation, NOT a round-1 reuse. The file is vendored byte-for-byte (modulo
the `NullSupplyDecoder` -> `CoverageDecoder` rename and the `R2S3B2_` ->
`R2S3B3_` env prefix) from this stream's own round-2 family
`worktrees/r2s3_lf_train_signal/B2/models_r2/r2s3_null_supply/model.py`
(commit 945ee65a1f47460db2cf892e0e8ead1248b58aeb, branch
`round2/exp-r2s3_lf_train_signal-B2`). The card requires the backbone to be
preserved byte-for-byte so the F3 reproduction check against B2's eight
overlapping legs is meaningful — so NOTHING numeric in this file changed.
It was NOT vendored from `mf_fno_transfer_film`, `mf_fno_ladder*` or
`models_r2/r2s3_rung_supervised`. The architectural family (spectral conv +
FiLM-conditioned normalisation) is standard published material (li2020fno,
perez2018film — see INSPIRATION.md); what is specific to this card lives in
TWO places, both of them here:

1. **THE MODE BUDGET IS A CONSTRUCTION-TIME CONSTANT, NOT A PER-GRID CLIP.**
   `alpha` is resolved ONCE per dataset by the caller under
   `R2S3B3_MODE_POLICY`:
     * `pinned_min_rung_nyquist` (card default, E3b / MG-TFNO convention,
       https://arxiv.org/html/2310.00120 "the first alpha modes in each
       direction, where alpha is independent of the discretization"):
       `alpha = min(MODES_CAP, min over ALL train rungs of floor(N_rung/2))`,
       so `alpha <= Nyquist(rung)` at EVERY rung and the clip below never
       bites: every spectral weight is exercised, and therefore supervised, at
       every rung. No weight is ever supervised by the 5 HF rows alone.
     * `grid_nyquist_clip` (card `r2s3_lf_train_signal-B1`'s configuration,
       priced in B2 by the now-deleted `A5_lf_norepair` arm): `alpha =
       MODES_CAP`, so the clip DOES bite at the coarse rungs and the
       `|k| > Nyquist(coarsest)` band is supervised by the HF rows only.
   Both policies run the identical code path below; only the value of `alpha`
   differs. NO LEG OF THIS CARD SELECTS `grid_nyquist_clip`
   (`recipe.env.R2S3B3_MODE_POLICY = pinned_min_rung_nyquist` on all 33 legs);
   the branch is retained byte-for-byte from B2 only so that `resolve_alpha`
   and this module stay identical to the code that produced B2's numbers.

2. **`norm="forward"` in every FFT.** With the forward normalisation the
   coefficients returned by `rfft2` approximate resolution-independent
   continuous Fourier coefficients, so one weight tensor means the same thing
   on a 8x8 rung and a 64x64 rung and coarse-rung gradients are informative
   about the fine-rung operator. (`norm="ortho"`, used by the round-1 / zoo
   FNO families, rescales every coefficient by sqrt(H*W).)

1-D fields are height-1 grids `(1, L)` (the repo convention,
`data_adapters/geometry.py`); `_active_modes` degenerates to the single
available dim-0 frequency with no special casing.

NO LF FIELD IS EVER AN INPUT. `forward` takes the condition vector and the
requested output grid, nothing else, so the round-2 stripped-view regime
(program.md §5.9) is structural rather than conventional.
"""
from __future__ import annotations

from typing import Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

Grid = Tuple[int, int]


def active_modes(grid: Grid, alpha: int) -> Tuple[int, int, int]:
    """(k0, n0, k1): non-negative / negative dim-0 and rfft dim-1 mode counts.

    `k0 + n0 <= H` always ((H+1)//2 + H//2 == H), so the positive and negative
    row blocks never overlap — including H == 1 (k0 = 1, n0 = 0, the 1-D case).
    """
    H, W = int(grid[0]), int(grid[1])
    a = max(1, int(alpha))
    return min(a, (H + 1) // 2), min(a, H // 2), min(a, W // 2 + 1)


class SpectralConv2d(nn.Module):
    """Channel mixing on a fixed (alpha x alpha) block of low Fourier modes."""

    def __init__(self, channels: int, alpha: int, fft_norm: str = "forward"):
        super().__init__()
        if fft_norm != "forward":
            raise ValueError(
                f"fft_norm={fft_norm!r}: this family is defined with norm='forward' "
                "(card part 3); no other normalisation is supported")
        self.channels = int(channels)
        self.alpha = max(1, int(alpha))
        self.fft_norm = fft_norm
        scale = 1.0 / self.channels
        self.w_pos = nn.Parameter(scale * torch.randn(
            self.channels, self.channels, self.alpha, self.alpha, dtype=torch.cfloat))
        self.w_neg = nn.Parameter(scale * torch.randn(
            self.channels, self.channels, self.alpha, self.alpha, dtype=torch.cfloat))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, _, H, W = x.shape
        k0, n0, k1 = active_modes((H, W), self.alpha)
        x_ft = torch.fft.rfft2(x, norm=self.fft_norm)
        out_ft = torch.zeros(B, self.channels, H, W // 2 + 1,
                             dtype=torch.cfloat, device=x.device)
        out_ft[:, :, :k0, :k1] = torch.einsum(
            "bchw,cohw->bohw", x_ft[:, :, :k0, :k1], self.w_pos[:, :, :k0, :k1])
        if n0 > 0:
            out_ft[:, :, -n0:, :k1] = torch.einsum(
                "bchw,cohw->bohw", x_ft[:, :, -n0:, :k1], self.w_neg[:, :, :n0, :k1])
        return torch.fft.irfft2(out_ft, s=(H, W), norm=self.fft_norm)


class FiLMGroupNorm(nn.Module):
    """Affine-free GroupNorm followed by a condition-dependent per-channel affine.

    `gamma`, `beta` come from a two-layer MLP whose last layer is zero-init, so
    at step 0 gamma == 1 and beta == 0 and the network is an unconditioned
    operator over the coordinate grid.
    """

    def __init__(self, channels: int, cond_dim: int, hidden: int):
        super().__init__()
        self.channels = int(channels)
        self.norm = nn.GroupNorm(min(8, self.channels), self.channels, affine=False)
        self.mlp = nn.Sequential(
            nn.Linear(int(cond_dim), int(hidden)),
            nn.GELU(),
            nn.Linear(int(hidden), 2 * self.channels),
        )
        nn.init.zeros_(self.mlp[-1].weight)
        nn.init.zeros_(self.mlp[-1].bias)

    def forward(self, z: torch.Tensor, cond: torch.Tensor) -> torch.Tensor:
        gamma, beta = self.mlp(cond).chunk(2, dim=-1)
        z = self.norm(z)
        return (1.0 + gamma).view(-1, self.channels, 1, 1) * z + beta.view(
            -1, self.channels, 1, 1)


class DecoderBlock(nn.Module):
    """GELU(FiLM(GroupNorm(SpectralConv(z) + 1x1Conv(z)), cond))."""

    def __init__(self, channels: int, alpha: int, cond_dim: int, film_hidden: int,
                 fft_norm: str = "forward"):
        super().__init__()
        self.spectral = SpectralConv2d(channels, alpha, fft_norm=fft_norm)
        self.pointwise = nn.Conv2d(channels, channels, 1)
        self.film = FiLMGroupNorm(channels, cond_dim, film_hidden)

    def forward(self, z: torch.Tensor, cond: torch.Tensor) -> torch.Tensor:
        return F.gelu(self.film(self.spectral(z) + self.pointwise(z), cond))


class CoverageDecoder(nn.Module):
    """cond (B, cond_dim) + out_hw (H, W) -> field (B, H, W).

    The output grid is a FORWARD argument, so one parameter set is supervised
    on every fidelity rung at that rung's own native resolution (no
    interpolation anywhere in the training loss).
    """

    def __init__(self, cond_dim: int, width: int = 64, blocks: int = 4,
                 alpha: int = 12, film_hidden: int = None,
                 fft_norm: str = "forward"):
        super().__init__()
        self.cond_dim = int(cond_dim)
        self.width = int(width)
        self.alpha = max(1, int(alpha))
        self.film_hidden = int(film_hidden if film_hidden is not None else width)
        self.lift = nn.Conv2d(2, self.width, 1)
        self.blocks = nn.ModuleList(
            DecoderBlock(self.width, self.alpha, self.cond_dim, self.film_hidden,
                         fft_norm=fft_norm)
            for _ in range(int(blocks))
        )
        self.project = nn.Sequential(
            nn.Conv2d(self.width, 2 * self.width, 1), nn.GELU(),
            nn.Conv2d(2 * self.width, 1, 1),
        )
        self._coords: dict = {}

    def coords(self, out_hw: Grid, device, dtype) -> torch.Tensor:
        """(1, 2, H, W) normalised coordinate channels, built at forward time."""
        H, W = int(out_hw[0]), int(out_hw[1])
        key = (H, W, str(device), str(dtype))
        c = self._coords.get(key)
        if c is None:
            ys = torch.linspace(-1.0, 1.0, H, device=device, dtype=dtype)
            xs = torch.linspace(-1.0, 1.0, W, device=device, dtype=dtype)
            gy, gx = torch.meshgrid(ys, xs, indexing="ij")
            c = torch.stack([gy, gx], dim=0).unsqueeze(0)
            self._coords[key] = c
        return c

    def forward(self, cond: torch.Tensor, out_hw: Grid) -> torch.Tensor:
        B = cond.shape[0]
        H, W = int(out_hw[0]), int(out_hw[1])
        z = self.lift(self.coords((H, W), cond.device, cond.dtype).expand(B, 2, H, W))
        for blk in self.blocks:
            z = blk(z, cond)
        return self.project(z).squeeze(1)


def param_count(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters())
