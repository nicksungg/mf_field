"""Test-time PDE-residual refinement of a predicted field (NITO-style).

`refine_field` runs K Adam steps on the FIELD tensor `u` (the network's output,
de-normalized to raw units), NOT on the network weights. The objective combines
a physics residual with an anchor that pins `u` to the network prediction:

    L(u) = w_res * mean( R(u, X, grid)^2 )  +  w_anchor * mean( (u - u_pred)^2 )

R is a per-dataset residual chosen from `RESIDUAL_REGISTRY`. Datasets without an
entry get `None` -> refinement is a graceful NO-OP and the family == the winner.

Residuals available
-------------------
We did NOT have a recoverable mapping from the IFC condition vector X to the
exact PDE source term in this data copy (the upstream `generate.py` and its
source parameterization are not shipped; ifc_poisson here carries a 5-D X with
no documented source decode, ifc_heat a 3-D X). We therefore ship a GENERIC
interior-Laplacian-smoothness prior `||Δu||^2` on the interior as an honest
weak prior (it nudges the field toward harmonic/smooth interior behaviour),
NOT the true governing operator. This is clearly a PLACEHOLDER PRIOR.

The registry is structured so a true operator (e.g. Poisson  -Δu = f  with f
reconstructable from X) can be dropped in later WITHOUT touching the wrapper:
just register `dataset_name -> residual_fn(u, X, grid) -> per-sample scalar`.

Finite differences use a fixed 3x3 Laplacian conv (5-point stencil) with
replicate padding; the residual is evaluated on the interior only.
"""
from __future__ import annotations

from typing import Callable, Dict, Optional

import torch
import torch.nn.functional as F

# residual_fn: (u (B,H,W), X (B,d), grid (H,W)) -> per-sample scalar (B,)
ResidualFn = Callable[[torch.Tensor, torch.Tensor, tuple], torch.Tensor]


def _laplacian(u: torch.Tensor) -> torch.Tensor:
    """5-point discrete Laplacian of u (B,H,W) -> (B,H,W), replicate-padded."""
    k = u.new_tensor([[0.0, 1.0, 0.0],
                      [1.0, -4.0, 1.0],
                      [0.0, 1.0, 0.0]]).view(1, 1, 3, 3)
    x = u.unsqueeze(1)
    x = F.pad(x, (1, 1, 1, 1), mode="replicate")
    return F.conv2d(x, k).squeeze(1)


def laplacian_smoothness_residual(u: torch.Tensor, X: torch.Tensor, grid) -> torch.Tensor:
    """PLACEHOLDER prior: ||Δu||^2 on the interior (per-sample mean).

    Weak harmonic/smoothness prior, NOT the true PDE operator. Returns a
    per-sample scalar (B,) so the caller can sum/mean as it likes.
    """
    lap = _laplacian(u)
    interior = lap[:, 1:-1, 1:-1]
    return (interior ** 2).reshape(interior.shape[0], -1).mean(dim=1)


# dataset_name -> residual_fn | None.  Missing key => NO-OP refinement.
RESIDUAL_REGISTRY: Dict[str, Optional[ResidualFn]] = {
    # Placeholder interior-Laplacian smoothness prior (documented above).
    "ifc_poisson": laplacian_smoothness_residual,
    "ifc_heat": laplacian_smoothness_residual,
}


def get_residual_fn(dataset_name: str) -> Optional[ResidualFn]:
    return RESIDUAL_REGISTRY.get(dataset_name, None)


def refine_field(u_pred: torch.Tensor, X: torch.Tensor, grid,
                 residual_fn: Optional[ResidualFn],
                 steps: int = 20, lr: float = 1e-2,
                 w_res: float = 1.0, w_anchor: float = 1.0) -> torch.Tensor:
    """Refine `u_pred` (B,H,W) by K Adam steps on the field tensor.

    If `residual_fn is None` or `steps <= 0`, returns `u_pred` unchanged (NO-OP).

    SCALE-AWARENESS: fields across datasets span orders of magnitude (heat ~1,
    Poisson ~1e-3). To keep the residual/anchor balance and the LR meaningful we
    refine a per-sample RMS-NORMALIZED copy of the field and rescale back. The
    refinement is then a small relative perturbation regardless of field units,
    so a fixed-weight placeholder prior cannot blow the field up by orders of
    magnitude. Pure inference, no weight grads.
    """
    if residual_fn is None or steps <= 0:
        return u_pred
    B = u_pred.shape[0]
    s = u_pred.detach().pow(2).reshape(B, -1).mean(dim=1).clamp_min(1e-12).sqrt()
    s = s.view(B, 1, 1)                       # per-sample RMS
    u0 = (u_pred.detach() / s)                # normalized field (~unit RMS)
    u = u0.clone().requires_grad_(True)
    opt = torch.optim.Adam([u], lr=lr)
    for _ in range(steps):
        opt.zero_grad(set_to_none=True)
        res = residual_fn(u, X, grid).mean()
        anc = ((u - u0) ** 2).reshape(B, -1).mean(dim=1).mean()
        loss = w_res * res + w_anchor * anc
        loss.backward()
        opt.step()
    return (u.detach() * s)
