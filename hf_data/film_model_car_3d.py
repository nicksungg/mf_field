"""
Larger FiLMNet for 3-D car surface pressure prediction.

Architecture overview
---------------------
FiLMModulation
  - 4-layer MLP (SiLU) → produces per-layer (gamma, beta) pairs
  - Hidden units: 512

ModulatedMLP
  - Input   : 3-D coordinates  (x, y, z)
  - FiLM layers: num_layers - 1 = 7  (apply gamma/beta after each hidden layer)
  - Extra unmodulated residual layers: extra_layers = 5
  - Output  : scalar pressure
  
  Compared to the 2-D baseline (hidden=256, num_layers=4, extra=3):
    hidden_dim  : 256  →  512         (~2× width)
    num_layers  : 4    →  8           (7 FiLM-modulated layers)
    extra_layers: 3    →  5
    coord_dim   : 2    →  3
  Total params increase roughly 6-8×.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

class ResBlock(nn.Module):
    """Simple pre-activation residual block used in the unmodulated tail."""

    def __init__(self, dim: int):
        super().__init__()
        self.fc1 = nn.Linear(dim, dim)
        self.fc2 = nn.Linear(dim, dim)
        nn.init.xavier_uniform_(self.fc1.weight)
        nn.init.xavier_uniform_(self.fc2.weight)

    def forward(self, x):
        h = F.silu(self.fc1(x))
        h = self.fc2(h)
        return x + h  # residual connection


# ---------------------------------------------------------------------------
# FiLM modulation network
# ---------------------------------------------------------------------------

class FiLMModulation3D(nn.Module):
    """
    Maps geometric condition vector → (gamma, beta) for every FiLM layer.

    gamma shape: (B, hidden_dim * n_film_layers)
    beta  shape: same
    where n_film_layers = num_layers - 1
    """

    def __init__(self, cond_dim: int, hidden_dim: int = 512, num_layers: int = 8):
        super().__init__()
        self.hidden_dim    = hidden_dim
        self.num_layers    = num_layers
        n_film             = num_layers - 1          # number of FiLM transforms
        self.num_mod_params = 2 * hidden_dim * n_film  # gamma + beta

        self.net = nn.Sequential(
            nn.Linear(cond_dim, 512),
            nn.SiLU(),
            nn.Linear(512, 512),
            nn.SiLU(),
            nn.Linear(512, 512),
            nn.SiLU(),
            nn.Linear(512, 512),
            nn.SiLU(),
        )
        self.out_layer = nn.Linear(512, self.num_mod_params)

        # Zero-init → identity mapping at the start of training
        nn.init.zeros_(self.out_layer.weight)
        nn.init.zeros_(self.out_layer.bias)

    def forward(self, cond):
        # cond: (B, cond_dim)
        feat  = self.net(cond)
        out   = self.out_layer(feat)           # (B, 2 * H * n_film)
        chunk = self.hidden_dim * (self.num_layers - 1)
        gamma = out[:, :chunk]
        beta  = out[:, chunk:]
        return gamma, beta                     # each (B, H * n_film)


# ---------------------------------------------------------------------------
# Modulated MLP
# ---------------------------------------------------------------------------

class ModulatedMLP3D(nn.Module):
    """
    Deep MLP whose hidden activations are modulated by FiLM layers, followed
    by an unmodulated residual tail.

    Forward pass:
      h = coords
      for i in range(num_layers - 1):
          h = linear_i(h)
          h = SiLU(h)
          h = (1 + gamma_i) * h + beta_i     ← FiLM
      for each extra ResBlock:
          h = ResBlock(h)                     ← unmodulated residual
      out = output_linear(SiLU(h))
    """

    def __init__(self,
                 input_dim: int  = 3,
                 output_dim: int = 1,
                 hidden_dim: int = 512,
                 num_layers: int = 8,
                 extra_layers: int = 5):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers

        # FiLM-modulated layers: layer 0…num_layers-2
        self.layers = nn.ModuleList()
        self.layers.append(nn.Linear(input_dim, hidden_dim))
        for _ in range(num_layers - 2):
            self.layers.append(nn.Linear(hidden_dim, hidden_dim))

        # Unmodulated residual tail
        self.extra = nn.ModuleList(
            [ResBlock(hidden_dim) for _ in range(extra_layers)]
        )

        self.output_layer = nn.Linear(hidden_dim, output_dim)

    def forward(self, coords, gamma, beta):
        """
        coords : (B, N, 3)
        gamma  : (B, hidden_dim * (num_layers-1))
        beta   : (B, hidden_dim * (num_layers-1))
        """
        H = self.hidden_dim
        h = coords                             # (B, N, 3)

        for i in range(self.num_layers - 1):
            h   = self.layers[i](h)            # (B, N, H)
            h   = F.silu(h)
            g_i = gamma[:, i*H : (i+1)*H].unsqueeze(1)   # (B, 1, H)
            b_i =  beta[:, i*H : (i+1)*H].unsqueeze(1)   # (B, 1, H)
            h   = (1.0 + g_i) * h + b_i       # FiLM

        for block in self.extra:
            h = block(h)                       # (B, N, H)

        return self.output_layer(F.silu(h))    # (B, N, 1)


# ---------------------------------------------------------------------------
# Full FiLMNet (3-D)
# ---------------------------------------------------------------------------

class FiLMNet3D(nn.Module):
    """
    FiLM-conditioned neural field for 3-D car surface pressure prediction.

    Default hyper-parameters
    ------------------------
    cond_dim    : number of geometric conditions (from CSV)
    coord_dim   : 3   (x=length, y=width, z=height)
    output_dim  : 1   (pressure)
    hidden_dim  : 512
    num_layers  : 8   (7 FiLM-modulated layers + 1 input projection)
    extra_layers: 5   (unmodulated residual tail)
    """

    def __init__(self,
                 cond_dim:    int = 23,
                 coord_dim:   int = 3,
                 output_dim:  int = 1,
                 hidden_dim:  int = 512,
                 num_layers:  int = 8,
                 extra_layers: int = 5):
        super().__init__()
        self.modulation_net = FiLMModulation3D(cond_dim, hidden_dim, num_layers)
        self.mlp = ModulatedMLP3D(coord_dim, output_dim, hidden_dim,
                                  num_layers, extra_layers)

    def forward(self, coords, cond):
        """
        coords : (B, N, 3)
        cond   : (B, cond_dim)
        returns: (B, N, 1)
        """
        gamma, beta = self.modulation_net(cond)
        return self.mlp(coords, gamma, beta)
