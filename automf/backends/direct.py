"""Portable adapters for the seven direct AutoMF library models.

This is a generic, training-only API. It reuses the archived architectures and
multifidelity mechanisms, with a common minibatch training loop. It does not
claim to replay every historical benchmark's data processing, validation split,
working-grid cap or training budget. See each fitted object's metadata.

Only NumPy and SciPy are required to import this module or fit M7. Neural
dependencies are imported when their models are requested.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
import os
from typing import Any
import numpy as np
from scipy.spatial.distance import cdist


DEFAULTS = {
    "epochs": 100, "batch_size": 16, "seed": 0, "device": "auto",
    "width": 64, "blocks": 4, "modes": 12, "lr": 1e-3,
    "finetune_lr": 3e-4, "weight_decay": 1e-5, "grad_clip": 1.0,
    "coarse_members": 5, "correction_steps": 100,
}


def _torch():
    try:
        import torch
    except ImportError as error:
        raise ImportError("Neural models require PyTorch. Install automf-fields[neural] or pip install -e '.[neural]'.") from error
    return torch


def _device(p):
    torch = _torch()
    choice = p["device"]
    if choice == "auto":
        choice = "cuda" if torch.cuda.is_available() else "cpu"
    if str(choice).startswith("cuda") and not torch.cuda.is_available():
        raise ValueError("A CUDA device was requested but PyTorch cannot access CUDA.")
    return torch.device(choice)


def _resize(Y, grid):
    if tuple(Y.shape[1:]) == tuple(grid):
        return np.asarray(Y, dtype=np.float32)
    torch = _torch()
    tensor = torch.as_tensor(np.ascontiguousarray(Y), dtype=torch.float32, device="cpu")[:, None]
    return torch.nn.functional.interpolate(
        tensor, size=grid, mode="bilinear", align_corners=False)[:, 0].numpy()


def _scale(Y):
    return max(float(np.abs(Y).max()), 1e-8)


def _checked_pair(pair, name, dimension=None):
    X, Y = (np.asarray(value) for value in pair)
    if X.ndim != 2 or Y.ndim != 3 or not len(X) or len(X) != len(Y):
        raise ValueError(f"{name} requires X=(N,D), Y=(N,H,W), with matching nonempty rows.")
    if not X.shape[1] or min(Y.shape[1:]) < 1:
        raise ValueError(f"{name} has an empty feature dimension or grid.")
    if dimension is not None and X.shape[1] != dimension:
        raise ValueError("All fidelities must share the same parameter dimension.")
    if not np.isfinite(X).all() or not np.isfinite(Y).all():
        raise ValueError(f"{name} contains nonfinite values.")
    return np.array(X, dtype=np.float64, copy=True), np.array(Y, dtype=np.float64, copy=True)


def _train_network(model, X, Y, p, device, *, epochs=None, lr=None,
                   scale=1.0, aug=None, trunk=None, seed=None):
    torch = _torch()
    model.to(device)
    epochs = p["epochs"] if epochs is None else epochs
    generator = torch.Generator(device="cpu").manual_seed(p["seed"] if seed is None else seed)
    Xt = torch.as_tensor(np.asarray(X), dtype=torch.float32, device="cpu")
    Yt = torch.as_tensor(np.asarray(Y), dtype=torch.float32, device="cpu") / scale
    At = None if aug is None else torch.as_tensor(aug, dtype=torch.float32, device="cpu")
    Tt = None if trunk is None else torch.as_tensor(trunk, dtype=torch.float32, device=device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=p["lr"] if lr is None else lr,
                                  weight_decay=p["weight_decay"])
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=max(epochs, 1), eta_min=1e-6)
    history = []
    updates = 0
    for _ in range(epochs):
        model.train()
        total = 0.0
        order = torch.randperm(len(X), generator=generator, device="cpu")
        for start in range(0, len(X), p["batch_size"]):
            index = order[start:start + p["batch_size"]]
            x, target = Xt[index].to(device), Yt[index].to(device)
            optimizer.zero_grad(set_to_none=True)
            if Tt is not None:
                prediction = model((x, Tt))
            elif At is not None:
                prediction = model(x, At[index].to(device))
            else:
                prediction = model(x)
            loss = torch.nn.functional.mse_loss(prediction, target)
            if not bool(torch.isfinite(loss)):
                raise FloatingPointError("Training produced a nonfinite loss. Check data scales and learning rate.")
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), p["grad_clip"])
            optimizer.step()
            total += float(loss.detach().cpu()) * len(index)
            updates += 1
        scheduler.step()
        history.append(total / len(X))
    model.cpu().eval()
    return {"epochs": epochs, "gradient_updates": updates,
            "training_rows": len(X), "final_training_mse": history[-1] if history else None,
            "learning_rate": p["lr"] if lr is None else lr, "target_scale": scale}


def _predict_network(model, X, grid, batch_size, scale=1.0, aug=None, trunk=None):
    torch = _torch()
    if len(X) == 0:
        return np.empty((0, *grid), dtype=np.float64)
    model.cpu().eval()
    outputs = []
    Tt = None if trunk is None else torch.as_tensor(trunk, dtype=torch.float32, device="cpu")
    with torch.no_grad():
        for start in range(0, len(X), batch_size):
            end = start + batch_size
            x = torch.as_tensor(np.asarray(X[start:end]), dtype=torch.float32, device="cpu")
            if Tt is not None:
                prediction = model((x, Tt))
            elif aug is not None:
                prediction = model(x, torch.as_tensor(aug[start:end], dtype=torch.float32, device="cpu"))
            else:
                prediction = model(x)
            outputs.append(prediction.numpy().astype(np.float64).reshape(len(x), *grid) * scale)
    return np.concatenate(outputs)


def _fno(dimension, grid, p, distribution=False, aug_ch=None):
    if distribution:
        from models.paper.fno_fire_distcond.model import FNO2d, FNO2dAug
        constructor = FNO2d if aug_ch is None else FNO2dAug
    else:
        from models.paper.mf_fno_transfer_film.model import FNO2d
        constructor = FNO2d
    kwargs = {"cond_dim": dimension, "hidden_channels": p["width"],
              "n_blocks": p["blocks"], "modes_h": min(p["modes"], max(grid[0] // 2, 1)),
              "modes_w": min(p["modes"], grid[1] // 2 + 1), "grid": grid}
    if aug_ch is not None:
        kwargs["aug_ch"] = aug_ch
    return constructor(**kwargs)


def _query(X, dimension):
    X = np.asarray(X, dtype=np.float64)
    if X.ndim != 2 or X.shape[1] != dimension or not np.isfinite(X).all():
        raise ValueError(f"Prediction inputs must be finite with shape (N, {dimension}).")
    return X


@dataclass
class DirectPredictor:
    model: Any
    grid: tuple[int, int]
    dimension: int
    scale: float
    batch_size: int
    metadata: dict
    fidelity_query: tuple[float, float] | None = None

    def predict(self, X):
        X = _query(X, self.dimension)
        if self.fidelity_query is not None:
            X = np.column_stack([X, np.tile(self.fidelity_query, (len(X), 1))])
        return _predict_network(self.model, X, self.grid, self.batch_size, self.scale)


@dataclass
class PODPredictor:
    model: Any
    grid: tuple[int, int]
    dimension: int
    metadata: dict

    def predict(self, X):
        X = _query(X, self.dimension)
        return self.model.predict(X).reshape(len(X), *self.grid)


def _summaries(members, X, grid, batch_size, scale):
    predictions = np.stack([_predict_network(m, X, grid, batch_size, scale) for m in members])
    mean = predictions.mean(0)
    spread = np.sqrt(predictions.var(0) + 1e-12)
    quantiles = np.quantile(predictions, [0.1, 0.5, 0.9], axis=0)
    augmentation = np.stack([mean, spread, *quantiles], axis=1) / scale
    return mean, augmentation.astype(np.float32)


@dataclass
class DistributionPredictor:
    members: list
    correction: Any
    coarse_scale: float
    residual_scale: float
    grid: tuple[int, int]
    dimension: int
    batch_size: int
    metadata: dict

    def predict(self, X):
        X = _query(X, self.dimension)
        if not len(X):
            return np.empty((0, *self.grid), dtype=np.float64)
        mean, aug = _summaries(self.members, X, self.grid, self.batch_size, self.coarse_scale)
        residual = _predict_network(self.correction, X, self.grid, self.batch_size,
                                    self.residual_scale, aug=aug)
        return mean + residual


def _retrieve(X, reference):
    result = np.empty(len(X), dtype=np.int64)
    for start in range(0, len(X), 512):
        result[start:start + 512] = cdist(X[start:start + 512], reference, "sqeuclidean").argmin(1)
    return result


@dataclass
class RetrievalPredictor:
    model: Any
    reference_X: np.ndarray
    reference_Y: np.ndarray
    branch_mean: np.ndarray
    branch_std: np.ndarray
    residual_mean: float
    residual_std: float
    trunk: np.ndarray
    grid: tuple[int, int]
    dimension: int
    batch_size: int
    metadata: dict
    network_spec: dict | None = None

    def __getstate__(self):
        state = self.__dict__.copy()
        if self.network_spec is not None:
            # Pickling the DeepXDE object directly imports its module before any
            # adapter code can run on load. DeepXDE may then change the caller's
            # default Torch device. Serialize weights and rebuild under our guard.
            state.pop("model")
            state["_network_state"] = {
                name: value.detach().cpu() for name, value in self.model.state_dict().items()}
        return state

    def __setstate__(self, state):
        weights = state.pop("_network_state", None)
        self.__dict__.update(state)
        if weights is not None:
            torch = _torch()
            dde = _deepxde()
            with torch.random.fork_rng(devices=[]), torch.device("cpu"):
                self.model = dde.nn.DeepONetCartesianProd(**self.network_spec)
            self.model.load_state_dict(weights)
            self.model.cpu().eval()

    def predict(self, X):
        X = _query(X, self.dimension)
        if not len(X):
            return np.empty((0, *self.grid), dtype=np.float64)
        reference = self.reference_Y[_retrieve(X, self.reference_X)]
        branch = np.concatenate([X, reference.reshape(len(X), -1)], axis=1)
        normalized = (branch - self.branch_mean) / self.branch_std
        residual = _predict_network(self.model, normalized, self.grid, self.batch_size,
                                    self.residual_std, trunk=self.trunk) + self.residual_mean
        return _resize(reference, self.grid).astype(np.float64) + residual


def _deepxde():
    """Load the required backend without changing the caller's Torch device."""
    if os.environ.get("DDE_BACKEND", "pytorch") != "pytorch":
        raise RuntimeError("M6 requires DeepXDE's PyTorch backend. Set DDE_BACKEND=pytorch before importing deepxde.")
    os.environ.setdefault("DDE_BACKEND", "pytorch")
    torch = _torch()
    default_device = torch.get_default_device()
    try:
        import deepxde as dde
    except ImportError as error:
        raise ImportError("M6 requires DeepXDE with the PyTorch backend. Install automf-fields[neural] or pip install -e '.[neural]'.") from error
    finally:
        # DeepXDE selects CUDA as the process default on import when available.
        # The adapter must honor its own requested device without changing its caller.
        if torch.get_default_device() != default_device:
            torch.set_default_device(default_device)
    if dde.backend.backend_name != "pytorch":
        raise RuntimeError("DeepXDE is already using another backend. Start a new process with DDE_BACKEND=pytorch.")
    return dde


def _fit_retrieval(low, high, p, device, metadata):
    dde = _deepxde()
    X, Y = high
    reference_X, reference_Y = low
    grid = tuple(Y.shape[1:])
    retrieved = reference_Y[_retrieve(X, reference_X)]
    branch = np.column_stack([X, retrieved.reshape(len(X), -1)])
    branch_mean = branch.mean(0)
    branch_std = branch.std(0) + 1e-6
    branch = (branch - branch_mean) / branch_std
    residual = Y - _resize(retrieved, grid)
    residual_mean = float(residual.mean())
    residual_std = float(residual.std()) + 1e-12
    axes = [np.linspace(0, 1, side, dtype=np.float32) for side in grid]
    trunk = np.stack(np.meshgrid(*axes, indexing="ij"), axis=-1).reshape(-1, 2)
    network_spec = {
        "layer_sizes_branch": [branch.shape[1]] + [p["width"]] * p["blocks"],
        "layer_sizes_trunk": [2] + [p["width"]] * p["blocks"],
        "activation": "relu", "kernel_initializer": "Glorot normal",
    }
    net = dde.nn.DeepONetCartesianProd(**network_spec)
    stage = _train_network(net, branch, (residual - residual_mean).reshape(len(X), -1),
                           p, device, scale=residual_std, trunk=trunk)
    metadata.update(stages=[stage], mechanism="nearest training LF retrieval plus residual DeepONet",
                    retrieval="Euclidean nearest neighbor in caller-standardized base training parameter space",
                    training_features="parameters and flattened retrieved native LF field; target-grid coordinates",
                    reference_level=0, residual_mean=residual_mean, residual_std=residual_std,
                    differences_from_archive=["User supplied target grid without automatic 256-side cap",
                        "Common epoch-based AdamW loop replaces DeepXDE full-batch iterations",
                        "User configurable width and depth replace archived 256 by 5 networks"])
    return RetrievalPredictor(net, reference_X, reference_Y, branch_mean, branch_std,
                              residual_mean, residual_std, trunk, grid, X.shape[1],
                              p["batch_size"], metadata, network_spec)


def fit_direct(model_id: str, low_levels: list[tuple[np.ndarray, np.ndarray]],
               high: tuple[np.ndarray, np.ndarray], config: dict):
    """Fit M1 to M7 on base training rows and return a CPU-resident predictor.

    ``low_levels`` is ordered from lowest to highest fidelity. Input parameters
    must already share training-only standardization. Fidelity tables may have
    different row counts and input identities. Labels for ensemble fitting or
    evaluation must not be included. The target grid is exactly ``high[1].shape[1:]``.
    """
    if model_id not in {f"M{i}" for i in range(1, 8)}:
        raise ValueError(f"Unknown direct model: {model_id}. Expected M1 to M7.")
    p = {**DEFAULTS, **config}
    high = _checked_pair(high, "high")
    X, Y = high
    low_levels = [_checked_pair(pair, f"low_levels[{i}]", X.shape[1])
                  for i, pair in enumerate(low_levels)]
    if model_id != "M7" and not low_levels:
        raise ValueError(f"{model_id} requires at least one low fidelity training table.")
    for name in ("epochs", "batch_size", "width", "blocks", "modes", "coarse_members"):
        if not isinstance(p[name], (int, np.integer)) or p[name] < 1:
            raise ValueError(f"{name} must be a positive integer.")
    for name in ("lr", "finetune_lr", "grad_clip"):
        if not np.isfinite(p[name]) or p[name] <= 0:
            raise ValueError(f"{name} must be positive and finite.")
    if not np.isfinite(p["weight_decay"]) or p["weight_decay"] < 0:
        raise ValueError("weight_decay must be nonnegative and finite.")
    grid = tuple(Y.shape[1:])
    metadata = {"model_id": model_id, "implementation": "generic_fit_predict_v1",
                "exact_archived_benchmark_replay": False, "config": dict(p),
                "target_grid": list(grid), "high_training_rows": len(X),
                "low_training_rows": [len(pair[0]) for pair in low_levels],
                "low_native_grids": [list(pair[1].shape[1:]) for pair in low_levels],
                "input_standardization": "caller supplied; must use base training rows only",
                "fitting_labels_used": False, "evaluation_labels_used": False,
                "inference_inputs": ["parameters"], "stored_device": "cpu",
                "training_features": "standardized parameter vector",
                "differences_from_archive": ["Explicit caller supplied training data and target grid",
                    "No archive-specific validation split, working-grid cap or checkpoint selection",
                    "Common configurable training procedure; final epoch checkpoint"]}
    if model_id == "M7":
        from .pod_gp import PODGP
        gp = PODGP(X, Y.reshape(len(Y), -1), p["seed"],
                   energy=p.get("gp_energy", p.get("pod_energy", 0.999)),
                   max_modes=p.get("gp_max_modes", p.get("pod_modes", 64)),
                   restarts=p.get("gp_restarts", 2), maxiter=p.get("gp_maxiter", 200))
        metadata.update(mechanism="fine-only POD with shared ARD RBF Gaussian process",
                        source="models/st_bench/st_common.py", low_fidelity_used=False,
                        **gp.info())
        return PODPredictor(gp, grid, X.shape[1], metadata)
    torch = _torch()
    device = _device(p)
    if model_id != "M6" and p["width"] % min(8, p["width"]):
        raise ValueError("width must be divisible by min(8, width) for the archived GroupNorm layers.")
    torch.manual_seed(p["seed"])
    metadata["training_device"] = str(device)
    metadata["low_fidelity_used"] = True
    if model_id == "M6":
        return _fit_retrieval(low_levels[0], high, p, device, metadata)
    if model_id == "M4":
        low_X, low_Y = low_levels[0]
        low_Y = _resize(low_Y, grid)
        scale = _scale(low_Y)
        members, stages = [], []
        for i in range(p["coarse_members"]):
            torch.manual_seed(p["seed"] + i)
            network = _fno(X.shape[1], grid, p, distribution=True)
            stages.append(_train_network(network, low_X, low_Y, p, device,
                                          scale=scale, seed=p["seed"] + i))
            members.append(network)
        mean, augmentation = _summaries(members, X, grid, p["batch_size"], scale)
        residual = Y - mean
        residual_scale = _scale(residual)
        torch.manual_seed(p["seed"] + p["coarse_members"])
        correction = _fno(X.shape[1], grid, p, distribution=True, aug_ch=5)
        stages.append(_train_network(correction, X, residual, p, device,
                                      scale=residual_scale, aug=augmentation))
        metadata.update(mechanism="coarse ensemble distribution-conditioned residual FNO",
                        stages=stages, source="models/paper/fno_fire_distcond/model.py",
                        summary_channels=["mean", "standard_deviation", "q10", "q50", "q90"],
                        training_features="parameters, normalized coarse ensemble mean, spread and quantiles",
                        coarse_predictions="base LF models; no out-of-fold correction features in M4",
                        reference_level=0)
        return DistributionPredictor(members, correction, scale, residual_scale,
                                     grid, X.shape[1], p["batch_size"], metadata)
    if model_id == "M2":
        levels = low_levels + [high]
        labels = np.linspace(0.0, 1.0, len(levels))
        conditions, targets = [], []
        pairs = list(combinations(range(len(levels)), 2))
        for source, target in pairs:
            # No coarse field is consumed. A target's own X identifies its Y.
            # Never combine source row i with an unrelated target row i.
            target_X, target_Y = levels[target]
            tags = np.tile([labels[source], labels[target]], (len(target_X), 1))
            conditions.append(np.column_stack([target_X, tags]))
            targets.append(_resize(target_Y, grid))
        pooled_X, pooled_Y = np.concatenate(conditions), np.concatenate(targets)
        model = _fno(X.shape[1] + 2, grid, p)
        stages = [_train_network(model, pooled_X, pooled_Y, p, device, scale=_scale(pooled_Y))]
        query_X = np.column_stack([X, np.tile([0.0, 1.0], (len(X), 1))])
        stages.append(_train_network(model, query_X, Y, p, device,
                                      epochs=max(1, p["epochs"] // 2),
                                      lr=p["finetune_lr"], scale=_scale(Y)))
        metadata.update(mechanism="all ordered fidelity label pairs with HF query finetuning",
                        source="models/paper/mf_fno_allpairs (FiLM FNO architecture)",
                        stages=stages, pairs=[list(pair) for pair in pairs],
                        fidelity_labels=labels.tolist(),
                        low_fidelity_used=len(levels) > 2,
                        low_fidelity_target_levels=list(range(1, len(levels) - 1)),
                        training_features="target parameters plus source and target fidelity labels",
                        pairing="target-level X and Y are kept together; row correspondence is not assumed")
        metadata["differences_from_archive"] += [
            "Normalized ordinal fidelity labels replace log archive fidelity identifiers",
            "Target parameters accompany each target field, supporting unpaired fidelity tables"]
        if len(levels) == 2:
            metadata["two_level_caveat"] = (
                "With only LF and HF, the sole ordered pair has an HF target. "
                "M2 does not train on LF field values in this two-level case.")
        return DirectPredictor(model, grid, X.shape[1], _scale(Y), p["batch_size"], metadata, (0., 1.))
    if model_id == "M1":
        model = _fno(X.shape[1], grid, p)
        source = "models/paper/mf_fno_transfer_film/model.py"
    elif model_id == "M3":
        from .convnext_components import ConvNeXtUNet2d
        # Retain the archived three encoder levels; configurable blocks per stage.
        model = ConvNeXtUNet2d(X.shape[1], base=p["width"], n_levels=3,
                               blocks_per_stage=p["blocks"], grid=grid)
        source = "models/paper/convnext_unet_film/model.py"
    else:
        from .wavelet_components import WNO2d, dwt_recon_error
        wavelet = "db4"
        # PyTorch circular padding cannot wrap more than once. The archived
        # eight-tap db4 implementation needs each transformed axis >= 7.
        # Its supported Haar option preserves the architecture on tiny grids.
        transformed_sizes = [grid[1]] + ([grid[0]] if grid[0] > 1 else [])
        if min(side + side % 2 for side in transformed_sizes) < 7:
            wavelet = "haar"
            metadata["wavelet_choice_reason"] = "Tiny target grid requires the archived Haar filter option"
        error = dwt_recon_error(wavelet, device=device)
        if error >= 1e-4:
            wavelet = "haar"
            error = dwt_recon_error(wavelet, device=device)
        if not error < 1e-4:
            raise RuntimeError(f"Wavelet reconstruction check failed ({error}).")
        model = WNO2d(X.shape[1], hidden_channels=p["width"], n_blocks=p["blocks"],
                      modes_cap=p["modes"], grid=grid, wavelet=wavelet)
        metadata.update(wavelet=wavelet, wavelet_reconstruction_error=error)
        source = "models/paper/wno_transfer_film/model.py"
    low_X, low_Y = low_levels[0]
    low_Y = _resize(low_Y, grid)
    stages = [_train_network(model, low_X, low_Y, p, device, scale=_scale(low_Y))]
    stages.append(_train_network(model, X, Y, p, device, scale=_scale(Y), lr=p["finetune_lr"]))
    metadata.update(mechanism="LF pretraining followed by HF finetuning of the same network",
                    source=source, stages=stages, reference_level=0)
    return DirectPredictor(model, grid, X.shape[1], _scale(Y), p["batch_size"], metadata)
