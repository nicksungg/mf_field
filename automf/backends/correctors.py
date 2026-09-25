"""Parameter-only M8/M9 training with shared out-of-fold coarse predictions.

The two corrector architectures come from ``models/uqcorr/corr_backbones.py``.
This generic interface retains the iterative correction, spectral loss and
plain/heteroscedastic FNO ensemble. It accepts arbitrary, possibly unpaired,
fidelity tables instead of relying on the archived campaign's row ordering.
Its epoch schedule, last-epoch weights and native target grids are explicit API
settings, not a promise to reproduce a campaign checkpoint.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import logging
import math
from typing import Any

import numpy as np
try:
    import torch
    from torch import nn
    from torch.nn import functional as F
except ImportError as error:
    raise ImportError("M8/M9 require PyTorch. Install automf-fields[neural] or pip install -e '.[neural]'.") from error

from models.paper.mf_fno_transfer_film.model import FNO2d
from .corrector_components import ConvNeXtUNet, TransolverCorr, coordinates

LOG = logging.getLogger(__name__)


def _device(config):
    choice = config.get("device", "auto")
    if choice == "auto":
        choice = "cuda" if torch.cuda.is_available() else "cpu"
    if str(choice).startswith("cuda") and not torch.cuda.is_available():
        raise ValueError("A CUDA device was requested but PyTorch cannot access CUDA.")
    return torch.device(choice)


def _arrays(pair, label):
    x, y = pair
    x = np.asarray(x, dtype=np.float64)
    y = np.asarray(y, dtype=np.float32)
    if x.ndim != 2 or y.ndim != 3 or len(x) != len(y) or not len(x):
        raise ValueError(f"{label} requires X (N,D) and Y (N,H,W) with nonzero N")
    if min(y.shape[1:]) < 1 or not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError(f"{label} contains invalid field dimensions or nonfinite values")
    return x, y


def _row_keys(x):
    """Exact numeric parameter identities, independent of array memory layout."""
    rows = np.array(x, dtype="<f8", order="C", copy=True)
    rows[rows == 0] = 0.0  # +0 and -0 identify the same parameter vector.
    return [row.tobytes() for row in rows]


def _identity_hash(key):
    return hashlib.sha256(key).hexdigest()


def _coarse_folds(low_x, high_x, n_folds, seed):
    """Split HF identities and remove their complete LF groups from each fold.

    Matching uses values, never row positions. An extra LF pool may contain
    duplicates or overlap the HF table in any order. All such copies are held
    out together. Coarse-only inputs remain available in every fold.
    """
    low_keys, high_keys = _row_keys(low_x), _row_keys(high_x)
    unique = list(dict.fromkeys(high_keys))
    if len(unique) < 2:
        raise ValueError("M8/M9 need at least two distinct HF training inputs for out-of-fold references")
    if n_folds < 2:
        raise ValueError("coarse_folds must be at least 2")
    n_folds = min(n_folds, len(unique))
    order = np.random.default_rng(seed).permutation(len(unique))
    result = []
    for fold, indices in enumerate(np.array_split(order, n_folds)):
        hold_keys = {unique[int(i)] for i in indices}
        hold = np.array([i for i, key in enumerate(high_keys) if key in hold_keys], dtype=np.int64)
        train = np.array([i for i, key in enumerate(low_keys) if key not in hold_keys], dtype=np.int64)
        if len(train) == 0:
            raise ValueError(f"Coarse fold {fold} has no LF training rows after excluding held-out HF identities")
        result.append((train, hold))
    return result


class _CoarseNetwork(nn.Module):
    def __init__(self, dim, grid, config, hetero):
        super().__init__()
        modes = int(config.get("modes", 12))
        self.base = FNO2d(dim, hidden_channels=int(config.get("width", 32)),
                          n_blocks=int(config.get("blocks", 4)), modes_h=modes,
                          modes_w=modes, grid=grid)
        self.hetero = hetero
        if hetero:
            previous = self.base.proj[-1]
            head = nn.Conv2d(previous.in_channels, 2, 1)
            with torch.no_grad():
                head.weight[:1].copy_(previous.weight)
                head.bias[:1].copy_(previous.bias)
                head.weight[1].zero_()
                head.bias[1].fill_(-4.0)
            self.base.proj[-1] = head

    def forward(self, x):
        out = self.base(x)
        return (out[:, 0], out[:, 1].clamp(-14.0, 6.0)) if self.hetero else (out, None)


@dataclass
class _CoarseMember:
    network: _CoarseNetwork
    scale: float
    grid: tuple[int, int]
    batch_size: int

    def predict(self, x):
        if len(x) == 0:
            return np.empty((0, *self.grid), dtype=np.float32)
        self.network.eval()
        chunks = []
        with torch.no_grad():
            for begin in range(0, len(x), self.batch_size):
                inputs = torch.as_tensor(np.asarray(x[begin:begin + self.batch_size]),
                                         dtype=torch.float32, device="cpu")
                mean, _ = self.network(inputs)
                chunks.append(mean.numpy() * self.scale)
        return np.concatenate(chunks)


@dataclass
class _CoarseEnsemble:
    members: list[_CoarseMember]
    metadata: dict[str, Any]

    def predict(self, x):
        # Online summation avoids allocating a members x cases x grid tensor.
        mean = None
        for member in self.members:
            pred = member.predict(x)
            mean = pred.astype(np.float64) if mean is None else mean + pred
        return (mean / len(self.members)).astype(np.float32)


def _fit_coarse_member(x, y, config, seed, hetero):
    torch.manual_seed(seed)
    grid = tuple(y.shape[-2:])
    device = _device(config)
    # DeepXDE or a caller can set PyTorch's process-wide default device. Keep
    # construction and stored training arrays explicit before moving batches.
    with torch.device("cpu"):
        model = _CoarseNetwork(x.shape[1], grid, config, hetero)
    model = model.to(device)
    scale = max(float(np.max(np.abs(y))), 1e-8)
    xt = torch.as_tensor(x, dtype=torch.float32, device="cpu")
    yt = torch.as_tensor(y / scale, device="cpu")
    epochs, batch = int(config.get("epochs", 100)), int(config.get("batch_size", 16))
    lr = float(config.get("lr", 1e-3))
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=float(config.get("weight_decay", 1e-5)))
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, max(epochs, 1), eta_min=lr / 100)
    rng = torch.Generator(device="cpu").manual_seed(seed)
    model.train()
    for epoch in range(epochs):
        order = torch.randperm(len(x), generator=rng, device="cpu")
        for start in range(0, len(x), batch):
            idx = order[start:start + batch]
            mean, logvar = model(xt[idx].to(device))
            target = yt[idx].to(device)
            if hetero:
                # Same beta=0.5 NLL as the archived heteroscedastic coarse arm.
                variance = logvar.exp()
                loss = (0.5 * (logvar + (mean - target).square() / variance)
                        * variance.detach().sqrt()).mean()
            else:
                loss = F.mse_loss(mean, target)
            if not torch.isfinite(loss):
                raise RuntimeError("Nonfinite coarse FNO loss. Check input and field scales.")
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), float(config.get("grad_clip", 1.0)))
            optimizer.step()
        scheduler.step()
    return _CoarseMember(model.cpu().eval(), scale, grid, batch)


def _fit_coarse_ensemble(low_x, low_y, high_x, config):
    seed, member_count = int(config.get("seed", 42)), int(config.get("coarse_members", 4))
    folds = _coarse_folds(low_x, high_x, int(config.get("coarse_folds", 5)), seed)
    if member_count < 1:
        raise ValueError("coarse_members must be positive")
    references = np.empty((len(high_x), *low_y.shape[-2:]), dtype=np.float32)
    inference_members, fold_records = None, []
    low_keys, high_keys = _row_keys(low_x), _row_keys(high_x)
    for fold, (train, hold) in enumerate(folds):
        members = []
        for member in range(member_count):
            # With four members this is two MSE and two heteroscedastic FNOs.
            hetero = member >= math.ceil(member_count / 2)
            LOG.info("Coarse reference fold %d/%d, member %d/%d (%s)",
                     fold + 1, len(folds), member + 1, member_count, "hetero" if hetero else "plain")
            members.append(_fit_coarse_member(low_x[train], low_y[train], config,
                                             seed + 1000 * fold + member, hetero))
        ensemble = _CoarseEnsemble(members, {})
        references[hold] = ensemble.predict(high_x[hold])
        if fold == 0:
            inference_members = members
        fold_records.append({
            "fold": fold, "lf_training_rows": train.tolist(), "hf_reference_rows": hold.tolist(),
            "lf_training_identity_hashes": sorted({_identity_hash(low_keys[i]) for i in train}),
            "hf_held_out_identity_hashes": sorted({_identity_hash(high_keys[i]) for i in hold}),
            "members": member_count,
        })
    metadata = {
        "folds": fold_records, "fold_count": len(folds),
        "members_per_reference": member_count, "inference_member_count": member_count,
        "inference_fold": 0, "variants": ["plain" if i < math.ceil(member_count / 2) else "hetero"
                                           for i in range(member_count)],
        "identity_rule": "Exact standardized parameter values. All duplicate identities share a fold.",
        "inference_policy": "Fold zero fixed before fitting. Same member count as each training reference.",
    }
    return _CoarseEnsemble(inference_members, metadata), references


def _prolong(y, grid):
    tensor = torch.as_tensor(y, dtype=torch.float32, device="cpu")
    if tuple(tensor.shape[-2:]) == tuple(grid):
        return tensor
    return F.interpolate(tensor[:, None], size=grid, mode="bilinear", align_corners=False)[:, 0]


@dataclass
class CorrectorSurrogate:
    """Complete M8 or M9 inference procedure requiring parameter inputs only."""
    network: nn.Module
    coarse: _CoarseEnsemble
    scale: float
    gain: float
    grid: tuple[int, int]
    steps: int
    alpha: float
    batch_size: int
    metadata: dict[str, Any]

    def predict(self, x):
        x = np.asarray(x, dtype=np.float32)
        if x.ndim != 2 or x.shape[1] != self.metadata["input_dim"] or not np.isfinite(x).all():
            raise ValueError("predict requires finite parameter inputs with the training input dimension")
        if len(x) == 0:
            return np.empty((0, *self.grid), dtype=np.float32)
        self.network.eval()
        output = []
        with torch.no_grad():
            for begin in range(0, len(x), self.batch_size):
                inputs = x[begin:begin + self.batch_size]
                h = self.gain * _prolong(self.coarse.predict(inputs), self.grid) / self.scale
                cond = torch.as_tensor(inputs, device="cpu")
                for _ in range(self.steps):
                    h = h + self.alpha * self.network(cond, h)
                output.append((h * self.scale).numpy())
        return np.concatenate(output)


def _fit_corrector(model_id, high_x, high_y, coarse, references, config):
    seed = int(config.get("seed", 42)) + (8000 if model_id == "M8" else 9000)
    torch.manual_seed(seed)
    device, grid = _device(config), tuple(high_y.shape[-2:])
    width, blocks = int(config.get("width", 32)), int(config.get("blocks", 3))
    # Generic arrays do not encode PDE-specific registration. Cell-centered
    # bilinear prolongation is therefore explicit and fixed, never test-selected.
    coords = coordinates(grid, "periodic_cell", torch.device("cpu"))
    with torch.device("cpu"):
        if model_id == "M8":
            model = TransolverCorr(high_x.shape[1], coords, hidden=width, n_layers=blocks,
                                   heads=math.gcd(4, width))
        else:
            model = ConvNeXtUNet(high_x.shape[1], coords, base=width, blocks_per_stage=blocks)
    model = model.to(device)
    scale = max(float(np.sqrt(np.mean(high_y.astype(np.float64) ** 2))), 1e-8)
    up = _prolong(references, grid).double()
    targets = torch.as_tensor(high_y, dtype=torch.float64, device="cpu")
    denominator = float(up.square().sum())
    gain = float((up * targets).sum()) / denominator if denominator > 1e-30 else 1.0
    start = (up * gain / scale).float()
    targets = (targets / scale).float()
    inputs = torch.as_tensor(high_x, dtype=torch.float32, device="cpu")
    epochs = int(config.get("corrector_epochs", config.get("epochs", 100)))
    batch, steps = int(config.get("batch_size", 16)), int(config.get("correction_steps", 6))
    alpha = 0.2
    lr = float(config.get("finetune_lr", 3e-4))
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=float(config.get("weight_decay", 1e-5)))
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, max(epochs, 1), eta_min=lr / 100)
    rng = torch.Generator(device="cpu").manual_seed(seed)
    ky = torch.fft.fftfreq(grid[0], device=device)[:, None] * grid[0]
    kx = torch.fft.fftfreq(grid[1], device=device)[None, :] * grid[1]
    radial = (ky.square() + kx.square()).sqrt()
    radial = radial / radial.max().clamp_min(1e-12)
    model.train()
    for epoch in range(epochs):
        order = torch.randperm(len(high_x), generator=rng, device="cpu")
        for begin in range(0, len(high_x), batch):
            idx = order[begin:begin + batch]
            cond, h, target = inputs[idx].to(device), start[idx].to(device), targets[idx].to(device)
            target_spectrum = torch.fft.fft2(target, norm="ortho").abs()
            loss = target.new_zeros(())
            for step in range(steps):
                h = h + alpha * model(cond, h)
                weights = 1 + radial.pow(1 + step / max(1, steps - 1))
                weights = weights / weights.mean()
                spectral = ((torch.fft.fft2(h, norm="ortho").abs() - target_spectrum).square() * weights).mean()
                loss = loss + (F.mse_loss(h, target) + spectral) / steps
            loss = loss + 0.01 * model(cond, target).square().mean()
            if not torch.isfinite(loss):
                raise RuntimeError(f"Nonfinite {model_id} corrector loss. Check field scales and learning rate.")
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), float(config.get("grad_clip", 1.0)))
            optimizer.step()
        scheduler.step()
    metadata = {
        "model_id": model_id, "input_dim": high_x.shape[1], "target_grid": list(grid),
        "architecture": "TransolverCorr" if model_id == "M8" else "ConvNeXtUNet",
        "architecture_source": "models/uqcorr/corr_backbones.py", "coarse": coarse.metadata,
        "coarse_level": "finest supplied low fidelity level", "coarse_grid": list(references.shape[-2:]),
        "training_rows": len(high_x), "epochs": epochs, "coarse_epochs": int(config.get("epochs", 100)),
        "reference_gain": gain, "normalization_scale": scale, "correction_steps": steps,
        "correction_alpha": alpha, "spectral_loss_weight": 1.0, "fixed_point_loss_weight": 0.01,
        "extra_input_channels": [], "registration": "cell-centered bilinear",
        "training_protocol": "Generic API epochs on all supplied training rows. Last epoch, no validation checkpoint selection.",
        "campaign_differences": [
            "No fixed working-grid cap. Target grid follows supplied HF fields.",
            "Cell-centered interpolation rather than PDE-specific registration selection.",
            "Corrector RMS normalization uses the supplied HF training targets, without a separate validation subset.",
            "User-configured epochs and architecture dimensions rather than campaign-specific step budgets.",
            "Unpaired LF and HF supported by excluding held-out parameter identities from the coarse pool.",
            "CPU-stored predictors use one predetermined fold ensemble to match OOF member counts.",
        ],
    }
    return CorrectorSurrogate(model.cpu().eval(), coarse, scale, gain, grid, steps, alpha, batch, metadata)


def fit_correctors(model_ids, low_levels, high, config):
    """Fit M8/M9, sharing one identity-safe coarse ensemble and its OOF fields.

    Inputs must already be standardized using only base training parameters.
    ``low_levels`` is ordered from coarse to fine. Only its finest LF table is
    used, matching these correctors' archived model design. Neither fitting
    examples for the final ensemble weights nor evaluation labels belong here.
    """
    model_ids = list(dict.fromkeys(model_ids))
    if not model_ids:
        return {}
    if any(model_id not in {"M8", "M9"} for model_id in model_ids):
        raise ValueError("fit_correctors accepts M8 and M9 only")
    if not low_levels:
        raise ValueError("M8/M9 require at least one low fidelity training table")
    low_x, low_y = _arrays(low_levels[-1], "Low fidelity")
    high_x, high_y = _arrays(high, "High fidelity")
    if low_x.shape[1] != high_x.shape[1]:
        raise ValueError("Low and high fidelity parameter dimensions differ")
    for name, default in (("epochs", 100), ("corrector_epochs", config.get("epochs", 100)),
                          ("batch_size", 16), ("width", 32), ("blocks", 3), ("modes", 12),
                          ("correction_steps", 6)):
        if int(config.get(name, default)) < 1:
            raise ValueError(f"{name} must be a positive integer")
    width = int(config.get("width", 32))
    if width % 8:
        raise ValueError("M8/M9 width must be a multiple of 8 for the archived FiLM GroupNorm backbones")
    coarse, references = _fit_coarse_ensemble(low_x, low_y, high_x, config)
    return {model_id: _fit_corrector(model_id, high_x, high_y, coarse, references, config)
            for model_id in model_ids}
