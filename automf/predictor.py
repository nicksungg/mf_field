"""Train a model library, fit fixed ensemble weights, and predict new fields."""

from __future__ import annotations

import json
import importlib.util
import os
from pathlib import Path
import tempfile
import time

import cloudpickle
import numpy as np

from .data import FieldDataset, field_pair, parameters, row_keys

MODEL_NAMES = {
    "M1": "FiLM FNO transfer", "M2": "All pairs FNO", "M3": "ConvNeXt transfer",
    "M4": "Distribution FNO", "M5": "Wavelet transfer", "M6": "Retrieved field DeepONet",
    "M7": "POD GP", "M8": "Slice attention corrector", "M9": "ConvNeXt corrector",
}
RULE_KEYS = {"selected": "selected_single", "inverse": "inverse_mse", "fitted": "full"}
PRESETS = {
    "balanced": dict(epochs=100, batch_size=16, width=64, blocks=4, modes=12,
                     coarse_members=4, coarse_folds=5, correction_steps=6),
    "smoke": dict(epochs=2, batch_size=8, width=8, blocks=1, modes=4,
                  coarse_members=2, coarse_folds=2, correction_steps=2),
}


def relative_errors(predictions, targets):
    delta = (np.asarray(predictions, np.float64) - targets).reshape(len(targets), -1)
    norms = np.linalg.norm(targets.reshape(len(targets), -1), axis=1)
    return np.linalg.norm(delta, axis=1) / np.maximum(norms, 1e-8)


class FieldPredictor:
    """An AutoGluon-style interface to the adapted AutoMF surrogate library.

    fit() trains models using base data, then fits one fixed weight per model
    on reserved fine examples. predict() requires only parameter vectors.
    The generic training presets are not exact replicas of the paper campaigns.
    """

    def __init__(self, path=None, *, models="all", rule="fitted", device="auto", random_state=42):
        if isinstance(models, str) and models == "all":
            models = list(MODEL_NAMES)
        elif isinstance(models, str):
            models = [models]
        else:
            models = list(models)
        if not models or len(set(models)) != len(models) or any(m not in MODEL_NAMES for m in models):
            raise ValueError("models must contain distinct IDs from M1 to M9, or 'all'")
        if rule not in RULE_KEYS:
            raise ValueError("rule must be 'selected', 'inverse', or 'fitted'")
        self.path = Path(path).expanduser().resolve() if path is not None else None
        self.model_ids = models
        self.rule = rule
        self.device = device
        self.random_state = int(random_state)
        self._fitted = False

    def fit(self, data, *, fitting_size=5, fitting_data=None, presets="balanced", epochs=None,
            hyperparameters=None):
        """Train once and fit the requested ensemble rule without evaluation answers.

        By default, reserve fitting_size unique HF inputs and exclude every
        matching parameter row from all base training levels before scaling.
        Alternatively, pass a separate (X_fit, Y_fit) pair with no overlap.
        hyperparameters overrides common training settings, not model selection.
        """
        if self._fitted:
            raise RuntimeError("This predictor is already fitted. Create a new FieldPredictor for a new fit.")
        if not isinstance(data, FieldDataset):
            raise TypeError("data must be a FieldDataset")
        if presets not in PRESETS:
            raise ValueError(f"presets must be one of {list(PRESETS)}")
        if self.path is not None and self.path.exists() and any(self.path.iterdir()):
            raise FileExistsError(f"Output directory is not empty: {self.path}. Choose a new path.")
        config = dict(PRESETS[presets], seed=self.random_state, device=self.device,
                      lr=1e-3, finetune_lr=3e-4, weight_decay=1e-5, grad_clip=1.0)
        allowed = set(config) | {"corrector_epochs", "gp_restarts", "gp_max_modes", "gp_energy", "gp_maxiter"}
        overrides = dict(hyperparameters or {})
        if unknown := set(overrides) - allowed:
            raise ValueError(f"Unknown hyperparameters: {sorted(unknown)}")
        # Seed and device have one explicit home in the public API.
        if set(overrides) & {"seed", "device"}:
            raise ValueError("Set random_state and device on FieldPredictor, not in hyperparameters")
        config.update(overrides)
        if epochs is not None:
            config["epochs"] = epochs
        for key in ("epochs", "batch_size", "width", "blocks", "modes", "coarse_members",
                    "coarse_folds", "correction_steps", "corrector_epochs", "gp_restarts", "gp_max_modes", "gp_maxiter"):
            if key in config and (isinstance(config[key], bool) or not isinstance(config[key], int) or config[key] < 1):
                raise ValueError(f"{key} must be a positive integer")
        for key in ("lr", "finetune_lr", "grad_clip"):
            if not np.isfinite(config[key]) or config[key] <= 0:
                raise ValueError(f"{key} must be positive and finite")
        if not np.isfinite(config["weight_decay"]) or config["weight_decay"] < 0:
            raise ValueError("weight_decay must be finite and nonnegative")
        if "gp_energy" in config and not 0 < config["gp_energy"] <= 1:
            raise ValueError("gp_energy must be in (0, 1]")
        has_correctors = any(m in ("M8", "M9") for m in self.model_ids)
        if has_correctors and (config["coarse_folds"] < 2 or config["width"] % 8):
            raise ValueError("M8/M9 require coarse_folds >= 2 and width divisible by eight")
        required = []
        if any(m != "M7" for m in self.model_ids):
            required.append("torch")
        if "M6" in self.model_ids:
            required.append("deepxde")
        missing = [name for name in required if importlib.util.find_spec(name) is None]
        if missing:
            raise ImportError(f"Missing neural dependencies: {missing}. Install with pip install -e '.[neural]' "
                              "from the repository, or select models=['M7'] for the base installation.")

        high_x, high_y = data.high_fidelity
        high_keys = row_keys(high_x)
        low_levels = list(data.low_fidelity)
        removed_lf = []
        if fitting_data is None:
            first_rows = {}
            for i, key in enumerate(high_keys):
                first_rows.setdefault(key, i)
            if (isinstance(fitting_size, bool) or not isinstance(fitting_size, int)
                    or fitting_size < 1 or fitting_size >= len(first_rows)):
                raise ValueError("fitting_size must reserve at least one unique HF input and leave training inputs")
            choices = np.random.default_rng(self.random_state).choice(list(first_rows.values()),
                                                                      size=fitting_size, replace=False)
            fit_x, fit_y = high_x[choices].copy(), high_y[choices].copy()
            fit_keys = set(row_keys(fit_x))
            keep = np.array([key not in fit_keys for key in high_keys])
            high_x, high_y = high_x[keep], high_y[keep]
            new_low = []
            for x, y in low_levels:
                keep = np.array([key not in fit_keys for key in row_keys(x)])
                removed_lf.append(int((~keep).sum()))
                new_low.append((x[keep], y[keep]))
            low_levels = new_low
            split_mode = "reserved_from_high_fidelity"
        else:
            fit_x, fit_y = field_pair(fitting_data, "fitting_data", data.parameter_dimension, data.field_shape)
            fit_keys = set(row_keys(fit_x))
            train_keys = set(high_keys)
            for x, _ in low_levels:
                train_keys.update(row_keys(x))
            if train_keys & fit_keys:
                raise ValueError("fitting_data overlaps base LF or HF training inputs. Remove these rows from "
                                 "every training fidelity, or use automatic fitting_size reservation.")
            removed_lf = [0] * len(low_levels)
            split_mode = "explicit_disjoint_fitting_data"
        if any(m != "M7" for m in self.model_ids) and (not low_levels or any(len(x) == 0 for x, _ in low_levels)):
            raise ValueError("Neural multifidelity models need nonempty LF training data after reserving fitting inputs")
        if len(high_x) < 2:
            raise ValueError("At least two base HF training rows must remain after reserving fitting examples")
        if has_correctors and len(set(row_keys(high_x))) < 2:
            raise ValueError("M8/M9 require at least two distinct base HF training inputs")

        self.parameter_dimension_ = data.parameter_dimension
        self.field_shape_ = tuple(data.field_shape)
        base_x = np.concatenate([high_x] + [x for x, _ in low_levels], axis=0)
        # HF-only statistics also keep M7 genuinely independent of the LF pool.
        self.parameter_mean_ = high_x.mean(axis=0)
        standard_deviation = high_x.std(axis=0)
        self.parameter_scale_ = np.where(standard_deviation > 1e-12, standard_deviation, 1.0)
        self._training_keys = set(row_keys(base_x))
        self._fitting_keys = fit_keys
        self.split_info_ = {
            "mode": split_mode, "fitting_rows": len(fit_x), "fitting_unique_inputs": len(fit_keys),
            "hf_training_rows": len(high_x), "lf_training_rows": [len(x) for x, _ in low_levels],
            "lf_rows_removed_for_fitting": removed_lf,
            "parameter_identity": "Exact numeric equality of parameter rows, with signed zero canonicalized",
            "training_parameter_hashes": sorted(self._training_keys),
            "fitting_parameter_hashes": sorted(fit_keys),
        }
        high = (self._transform(high_x), high_y)
        low = [(self._transform(x), y) for x, y in low_levels]
        start = time.perf_counter()
        from .backends.direct import fit_direct
        backends = {}
        for model_id in self.model_ids:
            if model_id in ("M8", "M9"):
                continue
            print(f"[AutoMF] Training {model_id}: {MODEL_NAMES[model_id]}", flush=True)
            backends[model_id] = fit_direct(model_id, low, high, config)
        corrector_ids = [m for m in self.model_ids if m in ("M8", "M9")]
        if corrector_ids:
            print(f"[AutoMF] Preparing shared coarse ensembles for {', '.join(corrector_ids)}", flush=True)
            from .backends.correctors import fit_correctors
            backends.update(fit_correctors(corrector_ids, low, high, config))
        self._models = {m: backends[m] for m in self.model_ids}
        fit_predictions = self._predict_models_array(fit_x)
        from ensemble.rules import gram, rules
        g = gram(fit_predictions.reshape(len(fit_y), len(self.model_ids), -1), fit_y.reshape(len(fit_y), -1))
        if not np.isfinite(g).all():
            raise ValueError("Fitting errors overflowed. Check field units and target magnitudes.")
        fitted_rules = rules(g)
        self.rule_weights_ = {public: np.asarray(fitted_rules[key], dtype=np.float64)
                              for public, key in RULE_KEYS.items()}
        self.weights_ = self.rule_weights_[self.rule].copy()
        if (not np.isfinite(self.weights_).all() or (self.weights_ < 0).any()
                or not np.isclose(self.weights_.sum(), 1)):
            raise ValueError("Ensemble fitting did not produce valid convex weights")
        self._leaderboard = []
        for i, model_id in enumerate(self.model_ids):
            self._leaderboard.append(dict(model=model_id, name=MODEL_NAMES[model_id],
                fitting_relative_l2=float(relative_errors(fit_predictions[:, i], fit_y).mean()),
                weight=float(self.weights_[i]), kind="surrogate"))
        for rule, weights in self.rule_weights_.items():
            pred = np.tensordot(fit_predictions, weights, axes=(1, 0))
            self._leaderboard.append(dict(model=rule, name=rule,
                fitting_relative_l2=float(relative_errors(pred, fit_y).mean()),
                weight=None, kind="ensemble_rule"))
        self.fit_info_ = dict(dataset=data.describe(), models=list(self.model_ids), rule=self.rule,
                             config=config, presets=presets, train_and_fit_seconds=time.perf_counter() - start,
                             prediction_grid=list(self.field_shape_),
                             parameter_normalization="Mean and standard deviation of base HF training inputs only",
                             training_protocol="Generic API training using archived architectures, not exact campaign replay",
                             backends={m: model.metadata for m, model in self._models.items()})
        self._fitted = True
        if self.path is not None:
            self.save()
        return self

    def _transform(self, x):
        scaled = (x - self.parameter_mean_) / self.parameter_scale_
        with np.errstate(over="ignore"):
            scaled = scaled.astype(np.float32)
        if not np.isfinite(scaled).all():
            raise ValueError("Standardized parameters exceed the supported numeric range")
        return scaled

    def _require_fitted(self):
        if not self._fitted:
            raise RuntimeError("Call fit() before prediction or load a saved predictor")

    def _predict_models_array(self, x):
        scaled = self._transform(x)
        predictions = []
        expected = (len(x), *self.field_shape_)
        for model_id, model in self._models.items():
            result = np.asarray(model.predict(scaled), dtype=np.float64)
            if result.shape != expected or not np.isfinite(result).all():
                raise ValueError(f"{model_id} returned invalid predictions. Expected finite array {expected}, got {result.shape}")
            predictions.append(result)
        return np.stack(predictions, axis=1)

    def predict_models(self, x):
        """Individual predictions, in physical field units on the supplied fine grid."""
        self._require_fitted()
        x = parameters(x, self.parameter_dimension_, allow_empty=True)
        if len(x) == 0:
            return {m: np.empty((0, *self.field_shape_)) for m in self.model_ids}
        predictions = self._predict_models_array(x)
        return {m: predictions[:, i] for i, m in enumerate(self.model_ids)}

    def predict(self, x, *, rule=None):
        """Predict from parameters alone using already fitted, fixed model weights."""
        self._require_fitted()
        rule = self.rule if rule is None else rule
        if rule not in RULE_KEYS:
            raise ValueError(f"Unknown rule: {rule}")
        pred = self.predict_models(x)
        stacked = np.stack([pred[m] for m in self.model_ids], axis=1)
        return np.tensordot(stacked, self.rule_weights_[rule], axes=(1, 0))

    def leaderboard(self):
        """Fitting errors and selected-rule weights, not independent test scores."""
        self._require_fitted()
        return sorted([dict(row) for row in self._leaderboard], key=lambda row: row["fitting_relative_l2"])

    def evaluate(self, x, y):
        """Score all models/rules on unseen input identities without changing weights."""
        self._require_fitted()
        x, y = field_pair((x, y), "evaluation", self.parameter_dimension_, self.field_shape_)
        if set(row_keys(x)) & (self._training_keys | self._fitting_keys):
            raise ValueError("Evaluation inputs overlap LF/HF training or fitting inputs. Supply unseen evaluation cases.")
        individual = self.predict_models(x)
        predictions = np.stack([individual[m] for m in self.model_ids], axis=1)
        combined = {rule: np.tensordot(predictions, w, axes=(1, 0)) for rule, w in self.rule_weights_.items()}
        errors = {m: relative_errors(pred, y) for m, pred in {**individual, **combined}.items()}
        return {"n_examples": len(x), "metric": "mean_relative_l2", "field_shape": list(self.field_shape_),
                "mean_relative_l2": {name: float(value.mean()) for name, value in errors.items()},
                "per_case_relative_l2": {name: value.tolist() for name, value in errors.items()}}

    def save(self, path=None):
        """Save weights, preprocessing and trained models. Load only trusted artifacts."""
        self._require_fitted()
        target = Path(path).expanduser().resolve() if path is not None else self.path
        if target is None:
            raise ValueError("Supply path to save() or FieldPredictor")
        if target != self.path and target.exists() and any(target.iterdir()):
            raise FileExistsError(f"Output directory is not empty: {target}")
        target.mkdir(parents=True, exist_ok=True)
        self.path = target
        record = dict(schema_version=1, **self.fit_info_, weights=self.weights_.tolist(),
                      rule_weights={rule: w.tolist() for rule, w in self.rule_weights_.items()},
                      split_info=self.split_info_, leaderboard=self.leaderboard())
        serialized = json.dumps(record, indent=2, allow_nan=False)
        with tempfile.NamedTemporaryFile(dir=target, suffix=".tmp", delete=False) as stream:
            temp_name = stream.name
            try:
                cloudpickle.dump(self, stream)
            except BaseException:
                Path(temp_name).unlink(missing_ok=True)
                raise
        os.replace(temp_name, target / "predictor.pkl")
        (target / "metadata.json").write_text(serialized + "\n")
        return str(target)

    @classmethod
    def load(cls, path):
        """Restore a predictor saved by this API. Only load artifacts you trust."""
        target = Path(path).expanduser().resolve()
        record = json.loads((target / "metadata.json").read_text())
        if record.get("schema_version") != 1:
            raise ValueError("Unsupported predictor schema")
        # Some optional neural libraries change PyTorch's default device when
        # imported during deserialization. Preserve the caller's device setting.
        torch = None
        if any(m != "M7" for m in record.get("models", [])):
            import torch
            default_device = torch.get_default_device()
        try:
            with (target / "predictor.pkl").open("rb") as stream:
                predictor = cloudpickle.load(stream)
        finally:
            if torch is not None and torch.get_default_device() != default_device:
                torch.set_default_device(default_device)
        if not isinstance(predictor, cls) or not predictor._fitted:
            raise ValueError("File does not contain a fitted FieldPredictor")
        predictor.path = target
        return predictor
