# == RE-VENDORED (round-3 card r3s2_field_reach-B2) ==========================
# SOURCE : round3/worktrees/r3s2_field_reach/B1/models_r3/r3s2_stack_ic/front_end.py
# COMMIT : d5069a74bb63da837b89b16508ae25a2164780cc  (tip of branch
#          round3/exp-r3s2_field_reach-B1; recipe.env._vendor_source. The
#          recipe's `base_commit` 76d15c2d is a TRUNK commit that carries NO
#          models_r3/ tree at all -- see notes/handoff_experiment_builder.md.)
# SHA256 : 1861cb03149e0030163543617fd1ef413f37e4fc0dc1d10cf722d60bf6b672da
# STATUS : byte-identical below this header.
#          Copied, never imported: score_panel.py::code_hash hashes only
#          family_dir/**/*.py, so logic outside the family dir is invisible to
#          the eval cache key.
# ROLE   : declared reuse role (a), round-2 program 5.10a -- the DC-lineage
#          corrector stays a FROZEN test-time sub-component behind a
#          condition->pseudo-LF front end. The B2 contribution is the ROUTE
#          SWITCH + budget accountant, not this code.
# ============================================================================
"""The three emulator FRONT ENDS of card `r3s2_field_reach-B1` (E0 / E1 / E1n).

  E0  `film_only`   FiLM on the WHOLE condition vector, coordinate channels only.
                    This is the LITERAL round-2 replay: `FNO2d` from `model.py`
                    is used unmodified, so E0 is the pre-registered null and the
                    replication check against certified `r2s2_stacked-B1`.
  E1  `ic_synth`    the exact analytic IC field (`ic_synth.py`) enters as an EXTRA
                    INPUT CHANNEL next to the two coordinate channels, and FiLM
                    conditions on the NON-`ic_*` dims only.
  E1n `ic_shuffle`  E1 fed row-shuffled IC coefficients — the zero-information
                    null for the channel. Structurally identical to E1.

Where a dataset has no `ic_c*` dims (ifc_poisson, ifc_heat, sod_1d, helmholtz),
E1 and E1n ARE E0 by construction; the caller records `ic_synth_applicable:
false` (knob `R3S2_IC_FALLBACK=film_only_recorded`) rather than silently
substituting.

WHY AN INPUT CHANNEL AND NOT MORE FiLM
--------------------------------------
`model.py`'s FNO2d feeds the network two sample-INDEPENDENT coordinate channels
and injects the condition only as a per-channel affine (FiLM). A global affine
cannot create spatial structure that is not already in the coordinate channels,
which is exactly the round-2 ceiling this card re-measures. The IC field is
spatially varying and sample specific, so it must enter where the spectral
convolutions can act on it — the lift. Nothing else about the backbone changes:
same width, blocks, modes, projection head, and the same FiLM MLPs (on a shorter
condition vector).
"""
from __future__ import annotations

from typing import Tuple

import torch
import torch.nn as nn

from model import FNO2d, FNOBlock  # vendored backbone, unmodified

Grid = Tuple[int, int]


class FNO2dIC(nn.Module):
    """cond vector + a fixed extra field channel -> field on a working grid.

    Identical to `FNO2d` except the lift consumes `2 + n_extra` channels and
    `forward` takes `(cond, extra)` with `extra` of shape (B, n_extra, H, W).
    """

    def __init__(self, cond_dim: int, n_extra: int = 1, hidden_channels: int = 64,
                 n_blocks: int = 4, modes_h: int = 12, modes_w: int = 12,
                 grid: Grid = (64, 64), cond_feat_dim: int = 64):
        super().__init__()
        self.cond_dim = int(cond_dim)
        self.n_extra = int(n_extra)
        self.grid = (int(grid[0]), int(grid[1]))
        self.lift = nn.Conv2d(2 + self.n_extra, hidden_channels, 1)
        self.blocks = nn.ModuleList(
            FNOBlock(hidden_channels, modes_h, modes_w, self.cond_dim,
                     cond_feat_dim=cond_feat_dim)
            for _ in range(n_blocks)
        )
        self.proj = nn.Sequential(
            nn.Conv2d(hidden_channels, hidden_channels, 1), nn.GELU(),
            nn.Conv2d(hidden_channels, 1, 1),
        )
        H, W = self.grid
        ys = torch.linspace(-1.0, 1.0, H)
        xs = torch.linspace(-1.0, 1.0, W)
        gy, gx = torch.meshgrid(ys, xs, indexing="ij")
        self.register_buffer("coord_grid", torch.stack([gy, gx], dim=0).unsqueeze(0))

    def forward(self, x: torch.Tensor, extra: torch.Tensor) -> torch.Tensor:
        B = x.shape[0]
        H, W = self.grid
        if extra.shape[1:] != (self.n_extra, H, W):
            raise ValueError(
                f"extra channel shape {tuple(extra.shape)} != (B, {self.n_extra}, {H}, {W})")
        coords = self.coord_grid.expand(B, 2, H, W)
        z = self.lift(torch.cat([coords, extra.to(coords.dtype)], dim=1))
        for blk in self.blocks:
            z = blk(z, x)
        return self.proj(z).squeeze(1)  # (B, H, W)


class Emulator(nn.Module):
    """Uniform call surface over the two backbones: `net(cond_full, extra_or_None)`.

    Holds the FiLM column selection so the rest of the pipeline never has to
    know which front end it is driving. `film_idx=None` means "all columns"
    (E0); otherwise the non-`ic_*` columns (E1 / E1n).
    """

    def __init__(self, front_end: str, cond_dim: int, film_idx, grid: Grid,
                 hidden_channels: int, n_blocks: int, modes_h: int, modes_w: int):
        super().__init__()
        self.front_end = str(front_end)
        self.uses_ic_channel = film_idx is not None
        if film_idx is None:
            self.register_buffer("film_idx", torch.zeros(0, dtype=torch.long))
            self.film_dim = int(cond_dim)
            self.net = FNO2d(int(cond_dim), hidden_channels=hidden_channels,
                             n_blocks=n_blocks, modes_h=modes_h, modes_w=modes_w,
                             grid=grid)
        else:
            idx = torch.as_tensor(list(film_idx), dtype=torch.long)
            if idx.numel() == 0:
                raise ValueError(
                    "the IC front end needs at least one non-ic_* condition column "
                    "to FiLM on; got none")
            self.register_buffer("film_idx", idx)
            self.film_dim = int(idx.numel())
            self.net = FNO2dIC(self.film_dim, n_extra=1,
                               hidden_channels=hidden_channels, n_blocks=n_blocks,
                               modes_h=modes_h, modes_w=modes_w, grid=grid)

    def forward(self, cond: torch.Tensor, extra: torch.Tensor = None) -> torch.Tensor:
        if not self.uses_ic_channel:
            return self.net(cond)
        if extra is None:
            raise ValueError(f"front end {self.front_end!r} requires the IC channel")
        return self.net(cond.index_select(1, self.film_idx), extra)
