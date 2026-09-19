"""Score the complete ERA5 baseline campaign without exposing answers to workers.

The three phases are deliberately separate: validate every frozen prediction,
record that validation, and only then open the sealed answer files. Missing or
invalid predictions never produce a partly populated 'complete' result table.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import os
from pathlib import Path
import time

import numpy as np


BASELINE_MODELS = [
    "st_koh_pod", "st_nargp_pod", "st_mfdnn", "st_mfdeeponet", "st_dmfal",
    "nomad_mf", "mfrnp", "fno_coregionalization", "mf_fno_transfer",
    "mf_fno_transfer_bar", "st_lf_affine_pod", "st_knn",
]


class CollectionError(RuntimeError):
    """An artifact failed a scientific provenance or correspondence check."""


def require(condition, message):
    if not condition:
        raise CollectionError(message)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text())


def exact_array(actual, expected, label):
    require(actual.shape == expected.shape and np.array_equal(actual, expected),
            f"{label}: shape, values, or row order differ")


def validate_roster(document):
    rows = document["models"]
    require([r["model"] for r in rows] == BASELINE_MODELS,
            "BASELINES.json must contain all twelve baselines in B1 to B12 order")
    require([r["id"] for r in rows] == [f"B{i}" for i in range(1, 13)],
            "Baseline identifiers differ from the paper mapping")
    return rows


def validate_predictions(root, records, info, query_theta, manifests):
    """Validate all predictions without reading calibration or evaluation files."""
    root = Path(root)
    required = [root / folder / f'{row["model"]}__era5.{suffix}'
                for row in records
                for folder, suffix in [("predictions", "npz"), ("metadata", "json")]]
    missing = [str(path.relative_to(root)) for path in required if not path.is_file()]
    require(not missing, "Incomplete campaign; missing: " + ", ".join(missing))
    grid = np.asarray(info["work_grid"])
    shape = (int(info["n_query"]), int(np.prod(grid)))
    require(query_theta.shape[0] == shape[0] and np.isfinite(query_theta).all(),
            "Invalid query input shape or values")
    require(len(np.unique(query_theta, axis=0)) == len(query_theta),
            "Duplicate query inputs prevent an unambiguous split audit")
    predictions, metadata, hashes = {}, {}, {}
    # Check every artifact identity before opening any prediction array.
    for row in records:
        model = row["model"]
        pred_path = root / "predictions" / f"{model}__era5.npz"
        meta_path = root / "metadata" / f"{model}__era5.json"
        meta = read_json(meta_path)
        require(meta.get("smoke") is False, f"{model}: not an explicit full run")
        require(meta.get("scientific_result") is True, f"{model}: not a scientific result")
        require(meta.get("n_base_hf_train") == info["n_base_hf_train"],
                f"{model}: base HF count mismatch")
        for key, value in manifests.items():
            require(meta.get(key) == value, f"{model}: {key} mismatch")
        for key, value in [("model", model), ("dataset", "era5")]:
            require(key not in meta or meta[key] == value, f"{model}: {key} mismatch")
        if "alias_of" in row:
            require(meta.get("reused_from") == row["alias_of"],
                    f"{model}: declared recipe alias must be reported as reused")
        require(meta.get("evaluation_answers_used_for_training", False) is False,
                f"{model}: metadata reports evaluation answers used for training")
        pred_hash = digest(pred_path)
        require(meta.get("prediction_sha256") == pred_hash,
                f"{model}: prediction hash mismatch")
        metadata[model] = meta
        hashes[model] = {"prediction_sha256": pred_hash,
                         "metadata_sha256": digest(meta_path)}
    for row in records:
        model = row["model"]
        with np.load(root / "predictions" / f"{model}__era5.npz", allow_pickle=False) as data:
            require({"pred", "theta", "work_grid"}.issubset(data.files),
                    f"{model}: required prediction arrays missing")
            exact_array(data["work_grid"], grid, f"{model}: work grid")
            exact_array(data["theta"], query_theta, f"{model}: input correspondence")
            pred = data["pred"].copy()
        require(pred.shape == shape, f"{model}: prediction shape {pred.shape}, expected {shape}")
        require(pred.dtype == np.float32, f"{model}: predictions must be float32 raw units")
        require(np.isfinite(pred).all(), f"{model}: nonfinite prediction")
        predictions[model] = pred
    aliases = {}
    for model, meta in metadata.items():
        original = meta.get("reused_from")
        if original is None:
            continue
        require(model == "mf_fno_transfer_bar" and original == "mf_fno_transfer",
                f"{model}: undeclared recipe reuse from {original}")
        require(not metadata[original].get("reused_from"), "Chained aliases are not independent fits")
        exact_array(predictions[model], predictions[original], f"{model}: reused prediction")
        aliases[model] = original
    return predictions, metadata, hashes, aliases


def load_answers(root, info, query_theta, expected_hashes):
    """Open sealed answers only after validate_predictions has succeeded."""
    root = Path(root)
    n_cal = len(info["calibration_from_original_hf_train"])
    n_eval = int(info["n_original_test"])
    require(n_cal + n_eval == len(query_theta), "Calibration and evaluation counts do not partition query rows")
    result = {}
    for split, rows in [("calibration", np.arange(n_cal)),
                        ("evaluation", np.arange(n_cal, n_cal + n_eval))]:
        path = root / "answers" / "era5" / f"{split}.npz"
        require(expected_hashes.get(split) == digest(path), f"{split}: sealed answer hash mismatch")
        with np.load(path, allow_pickle=False) as data:
            exact_array(data["theta"], query_theta[rows], f"{split}: answer input correspondence")
            exact_array(data["work_grid"], np.asarray(info["work_grid"]), f"{split}: answer work grid")
            if "query_rows" in data.files:
                exact_array(data["query_rows"], rows, f"{split}: query rows")
            target = np.asarray(data["target"], dtype=np.float64)
        require(target.shape == (len(rows), int(np.prod(info["work_grid"]))),
                f"{split}: answer shape mismatch")
        require(np.isfinite(target).all(), f"{split}: nonfinite answer")
        result[split] = {"rows": rows, "target": target}
    return result


def score(prediction, target):
    prediction = np.asarray(prediction, dtype=np.float64)
    target = np.asarray(target, dtype=np.float64)
    require(prediction.shape == target.shape, "Prediction and target shape mismatch")
    errors = prediction - target
    relative = np.linalg.norm(errors, axis=1) / np.maximum(np.linalg.norm(target, axis=1), 1e-8)
    require(np.isfinite(relative).all(), "Nonfinite scoring result")
    return relative, float(np.sqrt(np.mean(errors ** 2)))


def atomic_text(path, content):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".tmp.{os.getpid()}")
    temporary.write_text(content)
    os.replace(temporary, path)


def assemble_results(records, predictions, metadata, aliases, answers, training_mean, info):
    all_records = list(records) + [{"id": "B13", "model": "training_mean_control"}]
    require(training_mean.shape == (int(np.prod(info["work_grid"])),), "Training mean shape mismatch")
    rows, per_case, means, calibration_means = [], {}, {}, {}
    for split, answer in answers.items():
        query_rows, target = answer["rows"], answer["target"]
        per_case[f"{split}__query_rows"] = query_rows
        for item in all_records:
            model = item["model"]
            prediction = (np.broadcast_to(training_mean, target.shape) if item["id"] == "B13"
                          else predictions[model][query_rows])
            relative, rmse = score(prediction, target)
            per_case[f"{split}__{model}"] = relative
            row = dict(dataset="era5", baseline_id=item["id"], model=model, split=split,
                       n_cases=len(query_rows), rel_l2=float(relative.mean()), rmse_raw_units=rmse,
                       n_base_hf_train=info["n_base_hf_train"], reused_from=aliases.get(model, ""),
                       independent_fit=model not in aliases and item["id"] != "B13")
            rows.append(row)
            (means if split == "evaluation" else calibration_means)[model] = row["rel_l2"]
    return rows, per_case, means, calibration_means


def main():
    # Workers import baseline_common but never import or execute this collector.
    import baseline_common as common
    root = common.ROOT
    try:
        common.verify_source()
        input_audit = common.verify_inputs()
        plan = common.load_plan()
        info = plan["datasets"]["era5"]
        require(info["work_grid"] == [128, 256] and info["n_query"] == 17
                and info["n_base_hf_train"] == 55 and info["n_original_test"] == 7
                and len(info["calibration_from_original_hf_train"]) == 10,
                "The collector requires the frozen 55/10/7 ERA5 protocol")
        records = validate_roster(read_json(root / "BASELINES.json"))
        manifests = {"source_manifest_sha256": digest(root / "SOURCE.json"),
                     "plan_sha256": digest(root / "PLAN.json"),
                     "input_manifest_sha256": digest(root / "INPUT_MANIFEST.json")}
        with np.load(root / "data/core/era5/test_l9.npz", allow_pickle=False) as data:
            theta = data["x"].copy()
            require(theta.shape == (17, 12), "Unexpected ERA5 query input dimensions")
            require(not np.any(data["y"]), "Query placeholder contains answer values")
        predictions, metadata, hashes, aliases = validate_predictions(
            root, records, info, theta, manifests)
        common.write_json(root / "results/PREDICTIONS_LOCKED.json", dict(
            passed=True, final_answers_loaded=False, calibration_answers_loaded=False,
            models=[r["model"] for r in records], artifacts=hashes, aliases=aliases,
            manifests=manifests, input_audit=input_audit))
        # All twelve predictions and their provenance are frozen before this point.
        answer_hashes = read_json(root / "INPUT_MANIFEST.json")
        if "files" in answer_hashes:
            entries = answer_hashes["files"]
            answer_hashes = ({row["path"]: row["sha256"] for row in entries}
                             if isinstance(entries, list) else entries)
        answer_hashes = {split: answer_hashes[f"answers/era5/{split}.npz"]
                         for split in ("calibration", "evaluation")}
        answer_hashes = {split: entry["sha256"] if isinstance(entry, dict) else entry
                         for split, entry in answer_hashes.items()}
        answers = load_answers(root, info, theta, answer_hashes)
        # Match the existing ERA5 collector: average native fields in float64,
        # convert the mean to float32, then bilinearly resize with align_corners=False.
        import torch
        import torch.nn.functional as functional
        torch.set_num_threads(4)
        with np.load(root / "data/core/era5/train_l9.npz", allow_pickle=False) as data:
            require(len(data["x"]) == 55, "Training mean uses a different HF pool")
            mean = data["y"].mean(axis=0, dtype=np.float64).astype(np.float32)
        native_grid = info["levels"][str(info["hf_level"])]["grid"]
        mean = torch.from_numpy(mean).reshape(1, 1, *native_grid)
        if list(native_grid) != info["work_grid"]:
            mean = functional.interpolate(mean, size=info["work_grid"], mode="bilinear", align_corners=False)
        training_mean = mean.numpy().reshape(-1).astype(np.float64)
        rows, per_case, means, calibration_means = assemble_results(
            records, predictions, metadata, aliases, answers, training_mean, info)
        control_check = {"available": False}
        prior_control = root / "prior_training_mean.json"
        if prior_control.is_file():
            previous = float(read_json(prior_control)["rel_l2"])
            current = means["training_mean_control"]
            require(np.isclose(current, previous, rtol=1e-7, atol=1e-10),
                    f"Training mean control differs from original ERA5 evaluation: {current} versus {previous}")
            control_check = {"available": True, "passed": True,
                             "previous_rel_l2": previous, "current_rel_l2": current,
                             "reference_sha256": digest(prior_control)}
        # Recheck frozen artifacts after scoring so a concurrent replacement cannot
        # silently leave a table referring to a different prediction file.
        for model, identities in hashes.items():
            for folder, extension, key in [("predictions", "npz", "prediction_sha256"),
                                            ("metadata", "json", "metadata_sha256")]:
                require(digest(root / folder / f"{model}__era5.{extension}") == identities[key],
                        f"{model}: artifact changed during collection")
        stream = io.StringIO()
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
        common.save_npz(root / "results/era5_baselines_per_case.npz", **per_case)
        atomic_text(root / "results/era5_baselines.csv", stream.getvalue())
        common.write_json(root / "results/era5_baselines__summary.json", dict(
            complete=True, dataset="era5", models=[r["model"] for r in records],
            means=means, calibration_means=calibration_means, metadata=metadata,
            aliases=aliases, independent_baseline_fits=len(records) - len(aliases),
            n_base_hf_train=55, n_calibration=10, n_evaluation=7, work_grid=info["work_grid"],
            manifests=manifests, answer_sha256=answer_hashes,
            interpretation="Single model seed. Calibration and evaluation errors are separate. "
                           "Identical reused recipes are reported as aliases, not independent fits. "
                           "These are existing reserved inputs, not new years or forecast origins."))
        common.write_json(root / "results/BASELINES_AUDIT.json", dict(
            passed=True, complete=True, models_verified=12,
            all_predictions_verified_before_answers=True, calibration_count=10, evaluation_count=7,
            query_order="calibration rows 0:10, evaluation rows 10:17", aliases=aliases,
            source_artifacts_preserved=True, training_mean_reference_check=control_check,
            prediction_lock_sha256=digest(root / "results/PREDICTIONS_LOCKED.json"),
            results_sha256={name: digest(root / "results" / name) for name in
                           ["era5_baselines.csv", "era5_baselines_per_case.npz", "era5_baselines__summary.json"]}))
        common.write_json(root / "results/era5_baselines__status.json", dict(complete=True, passed=True))
        print("COMPLETE: twelve ERA5 baseline entries and the training mean control", flush=True)
    except Exception as error:
        common.write_json(root / "results/era5_baselines__status.json", dict(
            complete=False, passed=False, error_type=type(error).__name__, error=str(error),
            checked_at_unix=time.time(), prior_results_preserved=True))
        raise


if __name__ == "__main__":
    main()
