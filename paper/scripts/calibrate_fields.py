#!/usr/bin/env python3
"""Fit a mixture on calibration fields, then apply its saved weights to queries.

This is the calibration stage only. Base predictor training and construction of
scientifically valid calibration and evaluation splits are outside this CLI.
"""

import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "data"))
import ensemble_rules  # noqa: E402

RULE_NAMES = {"selected": "selected_single", "inverse": "inverse_mse", "fitted": "full"}
PUBLIC_NAMES = {value: key for key, value in RULE_NAMES.items()}
SCHEMA_VERSION = 1


def digest(path):
    hasher = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(block)
    return hasher.hexdigest()


def real_array(value, name):
    value = np.asarray(value)
    if not np.issubdtype(value.dtype, np.number) or np.iscomplexobj(value):
        raise ValueError(f"{name} must be a real numeric array")
    value = np.asarray(value, dtype=np.float64)
    if not np.isfinite(value).all():
        raise ValueError(f"{name} contains a nonfinite value")
    return value


def model_names(value, count):
    value = np.asarray(value)
    if value.shape != (count,) or value.dtype.kind not in "US":
        raise ValueError("model_names must be a one dimensional string array of length M")
    names = value.astype(str).tolist()
    if any(not name.strip() for name in names) or len(set(names)) != count:
        raise ValueError("model_names must contain distinct, nonempty names")
    return names


def load_predictions(archive):
    if "predictions" not in archive.files:
        raise ValueError("NPZ must contain predictions with shape (N, M, ...)")
    predictions = real_array(archive["predictions"], "predictions")
    if predictions.ndim < 2 or any(size == 0 for size in predictions.shape):
        raise ValueError("predictions must have nonempty shape (N, M, ...)")
    count = predictions.shape[1]
    names = model_names(archive["model_names"], count) if "model_names" in archive.files else None
    return predictions, names


def valid_weights(value, count):
    weights = real_array(value, "weights")
    if weights.shape != (count,) or np.any(weights < 0):
        raise ValueError("weights must have shape (M,) and be nonnegative")
    if not np.isclose(weights.sum(), 1.0, rtol=0.0, atol=1e-8):
        raise ValueError("weights must sum to one")
    return weights


def fit(calibration_path, rule, output_path):
    """Fit only on the calibration archive and write a fixed weights record."""
    calibration_path, output_path = Path(calibration_path), Path(output_path)
    with np.load(calibration_path, allow_pickle=False) as archive:
        predictions, names = load_predictions(archive)
        if "targets" not in archive.files:
            raise ValueError("calibration NPZ must contain targets")
        targets = real_array(archive["targets"], "targets")
    required_shape = (predictions.shape[0],) + predictions.shape[2:]
    if targets.shape != required_shape:
        raise ValueError(f"targets must have shape {required_shape}, got {targets.shape}")
    if rule == "auto" and len(targets) < 2:
        raise ValueError("auto requires at least two calibration cases")

    count = predictions.shape[1]
    with np.errstate(over="raise", invalid="raise", divide="raise"):
        gram = ensemble_rules.gram(
            predictions.reshape(len(targets), count, -1), targets.reshape(len(targets), -1)
        )
    if not np.isfinite(gram).all():
        raise ValueError("calibration error Gram matrix contains a nonfinite value")
    if rule == "auto":
        fitted, selection = ensemble_rules.fit_auto(gram)
        chosen = PUBLIC_NAMES[selection["chosen"]]
        weights = fitted["auto"]
        scores = {PUBLIC_NAMES[key]: value for key, value in selection["leave_one_out_scores"].items()}
    else:
        chosen, scores = rule, None
        weights = ensemble_rules.rules(gram)[RULE_NAMES[rule]]
    weights = valid_weights(weights, count)
    record = {
        "schema_version": SCHEMA_VERSION,
        "requested_rule": rule,
        "chosen_rule": chosen,
        "reference_rule_name": RULE_NAMES[chosen],
        "weights": weights.tolist(),
        "model_names": names if names is not None else [f"model_{index}" for index in range(count)],
        "model_names_provided": names is not None,
        "field_shape": list(predictions.shape[2:]),
        "calibration_shape": {"predictions": list(predictions.shape), "targets": list(targets.shape)},
        "calibration_sha256": digest(calibration_path),
        "ensemble_rules_sha256": digest(ROOT / "data" / "ensemble_rules.py"),
        "fit_settings": {
            "weight_scope": "one fixed weight per model, shared by all cells and query cases",
            "target_norm_floor": 1e-8,
            "inverse_squared_error_floor": 1e-30,
            "selected_objective": "mean relative L2 error",
            "fitted_objective": "mean squared relative L2 error",
            "optimizer": "SLSQP with uniform and best diagonal starts, retaining both starts as candidates",
            "optimizer_ftol": 1e-12,
            "optimizer_maxiter": 300,
            "auto_scoring": "leave one calibration case out, mean relative L2 error",
            "auto_tie_order": ["selected", "inverse", "fitted"],
        },
        "leave_one_out_scores": scores,
    }
    serialized = json.dumps(record, indent=2, allow_nan=False) + "\n"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("x", encoding="utf-8") as stream:
        stream.write(serialized)
    return record


def predict(prediction_path, weights_path, output_path):
    """Apply locked weights. Query targets are neither required nor accessed."""
    weights_path, output_path = Path(weights_path), Path(output_path)
    record = json.loads(weights_path.read_text(encoding="utf-8"))
    if record.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported weights schema_version")
    expected_names = record.get("model_names")
    if not isinstance(expected_names, list) or not expected_names:
        raise ValueError("weights record must contain model_names")
    if any(not isinstance(name, str) for name in expected_names):
        raise ValueError("weights record model_names must be strings")
    expected_names = model_names(np.asarray(expected_names), len(expected_names))
    weights = valid_weights(record.get("weights"), len(expected_names))
    with np.load(prediction_path, allow_pickle=False) as archive:
        # Read these two arrays only. In particular, do not load archive['targets'].
        predictions, names = load_predictions(archive)
    if predictions.shape[1] != len(weights):
        raise ValueError("query model count differs from the fitted library")
    if list(predictions.shape[2:]) != record.get("field_shape"):
        raise ValueError("query field shape differs from the calibration field shape")
    if record.get("model_names_provided") and names is None:
        raise ValueError("query model_names are required because calibration supplied names")
    if names is not None and names != expected_names:
        raise ValueError("query model_names differ from the fitted names or their order")
    with np.errstate(over="raise", invalid="raise"):
        mixture = np.tensordot(predictions, weights, axes=([1], [0]))
    if not np.isfinite(mixture).all():
        raise ValueError("weighted predictions contain a nonfinite value")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("xb") as stream:
        np.savez_compressed(
            stream,
            predictions=mixture,
            weights=weights,
            model_names=np.asarray(expected_names),
            chosen_rule=np.asarray(record["chosen_rule"]),
            weights_sha256=np.asarray(digest(weights_path)),
        )
    return mixture.shape


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    fitter = commands.add_parser("fit", help="fit weights using only known calibration fields")
    fitter.add_argument("--calibration", type=Path, required=True)
    fitter.add_argument("--rule", choices=[*RULE_NAMES, "auto"], required=True)
    fitter.add_argument("--output", type=Path, required=True)
    predictor = commands.add_parser("predict", help="apply saved weights without query answers")
    predictor.add_argument("--predictions", type=Path, required=True)
    predictor.add_argument("--weights", type=Path, required=True)
    predictor.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "fit":
            result = fit(args.calibration, args.rule, args.output)
            print(json.dumps({"output": str(args.output), "chosen_rule": result["chosen_rule"]}))
        else:
            shape = predict(args.predictions, args.weights, args.output)
            print(json.dumps({"output": str(args.output), "prediction_shape": shape}))
    except (ValueError, KeyError, TypeError, OSError, FloatingPointError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
