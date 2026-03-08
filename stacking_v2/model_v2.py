"""
model_v2.py  —  FiLMNet3D with Phase-2 layer-freezing utilities.

The architecture is the same FiLMNet3D from hf_data/film_model_car_3d.py:
  coord_dim=3  (x, y, z)  — z=0 in Phase 1, varies in Phase 3.

Freezing strategy for Phase 3 (fine-tuning)
--------------------------------------------
  With num_layers=8 there are 7 FiLM-modulated layers (mlp.layers[0..6]).

  Default: freeze layers[freeze_start .. freeze_end-1]  (middle block).
           freeze the corresponding FiLM parameters in the modulation net.

  What stays trainable
  --------------------
  * modulation_net         — always trainable (adapts gamma/beta for 3-D)
  * mlp.layers[0..freeze_start-1]   — first layers adapt to new z input
  * mlp.layers[freeze_end..]        — last FiLM-modulated layers
  * mlp.extra                       — unmodulated residual tail
  * mlp.output_layer
"""

import sys
from pathlib import Path
import torch
import torch.nn as nn

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent / "hf_data"))

from film_model_car_3d import FiLMNet3D   # re-export the existing model


# ─────────────────────────────────────────────────────────────────────────────
# Freeze / unfreeze helpers
# ─────────────────────────────────────────────────────────────────────────────

def freeze_middle_layers(model: FiLMNet3D,
                         freeze_start: int = 2,
                         freeze_end:   int = 5) -> None:
    """
    Freeze mlp.layers[freeze_start : freeze_end+1]  (inclusive of freeze_end).

    The modulation_net and all other MLP components remain trainable so the
    model can still adapt gamma/beta, the input projection, and the output tail.

    Parameters
    ----------
    model        : FiLMNet3D instance
    freeze_start : index of first layer to freeze (default 2)
    freeze_end   : index of last  layer to freeze (default 5)
                   i.e. with num_layers=8: 7 FiLM layers total, indices 0–6
                   freezing [2..5] keeps 0,1 and 6 trainable
    """
    mlp = model.mlp
    total = len(mlp.layers)
    for i, layer in enumerate(mlp.layers):
        frozen = (freeze_start <= i <= freeze_end)
        for p in layer.parameters():
            p.requires_grad_(not frozen)

    n_frozen    = sum(1 for i in range(total) if freeze_start <= i <= freeze_end)
    n_trainable = total - n_frozen
    print(f"[freeze] mlp.layers: {n_frozen} frozen  [{freeze_start}..{freeze_end}], "
          f"{n_trainable} trainable  "
          f"| modulation_net, extra, output_layer: trainable")


def unfreeze_all(model: FiLMNet3D) -> None:
    """Re-enable gradients for every parameter (for full fine-tuning)."""
    for p in model.parameters():
        p.requires_grad_(True)


def frozen_param_count(model: FiLMNet3D) -> tuple[int, int]:
    """Returns (frozen_count, trainable_count)."""
    frozen = trainable = 0
    for p in model.parameters():
        if p.requires_grad:
            trainable += p.numel()
        else:
            frozen    += p.numel()
    return frozen, trainable


__all__ = ["FiLMNet3D", "freeze_middle_layers", "unfreeze_all", "frozen_param_count"]
