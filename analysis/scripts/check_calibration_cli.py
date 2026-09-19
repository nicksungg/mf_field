#!/usr/bin/env python3
"""Integration checks for the portable calibration and target free prediction CLI."""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "data"))
import ensemble_rules  # noqa: E402


class CalibrationCliChecks(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="automf_calibration_check_")
        self.root = Path(self.temporary.name)
        # Exercise an isolated copy containing exactly the portable code dependencies.
        (self.root / "scripts").mkdir()
        (self.root / "data").mkdir()
        shutil.copy2(ROOT / "scripts" / "calibrate_fields.py", self.root / "scripts")
        shutil.copy2(ROOT / "data" / "ensemble_rules.py", self.root / "data")
        self.cli = self.root / "scripts" / "calibrate_fields.py"
        self.targets = np.arange(1, 31, dtype=np.float64).reshape(5, 2, 3) / 10
        offset = np.linspace(0.5, 1.5, 6).reshape(2, 3)
        self.predictions = np.stack(
            [self.targets + offset, self.targets - offset, self.targets + 3 * offset], axis=1
        )
        self.names = np.asarray(["positive_bias", "negative_bias", "larger_bias"])
        self.calibration = self.root / "calibration.npz"
        np.savez(self.calibration, predictions=self.predictions, targets=self.targets, model_names=self.names)

    def tearDown(self):
        self.temporary.cleanup()

    def run_cli(self, *arguments, succeeds=True):
        result = subprocess.run(
            [sys.executable, str(self.cli), *map(str, arguments)],
            cwd=self.root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if succeeds:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0, "invalid input was accepted")
        return result

    def fit(self, rule="inverse", calibration=None):
        output = self.root / f"weights_{rule}.json"
        self.run_cli("fit", "--calibration", calibration or self.calibration, "--rule", rule, "--output", output)
        return output, json.loads(output.read_text())

    def test_four_rules_match_reference_and_preserve_field_shape(self):
        gram = ensemble_rules.gram(self.predictions.reshape(5, 3, -1), self.targets.reshape(5, -1))
        expected = ensemble_rules.rules(gram)
        automatic, selection = ensemble_rules.fit_auto(gram)
        expected["auto"] = automatic["auto"]
        names = {"selected": "selected_single", "inverse": "inverse_mse", "fitted": "full", "auto": "auto"}
        for rule, key in names.items():
            with self.subTest(rule=rule):
                _, record = self.fit(rule)
                np.testing.assert_allclose(record["weights"], expected[key], rtol=1e-12, atol=1e-12)
                self.assertEqual(record["field_shape"], [2, 3])
                self.assertEqual(record["calibration_shape"]["predictions"], [5, 3, 2, 3])
                self.assertEqual(record["model_names"], self.names.tolist())
                self.assertEqual(record["calibration_sha256"], hashlib.sha256(self.calibration.read_bytes()).hexdigest())
                self.assertEqual(record["fit_settings"]["target_norm_floor"], 1e-8)
                if rule == "auto":
                    self.assertEqual(record["reference_rule_name"], selection["chosen"])
                    self.assertEqual(set(record["leave_one_out_scores"]), {"selected", "inverse", "fitted"})

    def test_fitted_mixture_cancels_opposite_field_errors(self):
        weights, _ = self.fit("fitted")
        query = self.root / "query.npz"
        output = self.root / "mixture.npz"
        np.savez(query, predictions=self.predictions[:2], model_names=self.names)
        self.run_cli("predict", "--predictions", query, "--weights", weights, "--output", output)
        with np.load(output, allow_pickle=False) as result:
            np.testing.assert_allclose(result["predictions"], self.targets[:2], atol=2e-6, rtol=0)
            self.assertEqual(result["predictions"].shape, (2, 2, 3))

    def test_predict_does_not_access_query_targets_or_change_weights(self):
        weights, record = self.fit()
        frozen_weights = weights.read_bytes()
        expected = sum(weight * self.predictions[:2, index] for index, weight in enumerate(record["weights"]))
        alternatives = [None, np.full((2, 2, 3), -999.0), np.asarray([{"deliberately": "unreadable without pickle"}], dtype=object)]
        for index, targets in enumerate(alternatives):
            with self.subTest(query_targets=index):
                query, output = self.root / f"query_{index}.npz", self.root / f"mixture_{index}.npz"
                arrays = {"predictions": self.predictions[:2], "model_names": self.names}
                if targets is not None:
                    arrays["targets"] = targets
                np.savez(query, **arrays)
                self.run_cli("predict", "--predictions", query, "--weights", weights, "--output", output)
                with np.load(output, allow_pickle=False) as result:
                    np.testing.assert_allclose(result["predictions"], expected, rtol=1e-14, atol=1e-14)
                self.assertEqual(weights.read_bytes(), frozen_weights)
        rejected = self.run_cli("predict", "--predictions", query, "--weights", weights,
                                "--output", self.root / "unused.npz", "--targets", "anything.npz",
                                succeeds=False)
        self.assertIn("unrecognized arguments", rejected.stderr)

    def test_permuted_or_missing_named_models_are_rejected(self):
        weights, _ = self.fit()
        for label, arrays in [
            ("permuted", dict(predictions=self.predictions[:, [1, 0, 2]], model_names=self.names[[1, 0, 2]])),
            ("missing_names", dict(predictions=self.predictions)),
        ]:
            query, output = self.root / f"{label}.npz", self.root / f"{label}_out.npz"
            np.savez(query, **arrays)
            result = self.run_cli("predict", "--predictions", query, "--weights", weights, "--output", output, succeeds=False)
            self.assertIn("model_names", result.stderr)
            self.assertFalse(output.exists())

    def test_invalid_calibration_arrays_are_rejected_before_output(self):
        bad_predictions = self.predictions.copy()
        bad_predictions[0, 0, 0, 0] = np.nan
        cases = {
            "wrong_targets": dict(predictions=self.predictions, targets=self.targets[:, :, :2]),
            "nonfinite_predictions": dict(predictions=bad_predictions, targets=self.targets),
            "nonfinite_targets": dict(predictions=self.predictions, targets=self.targets * np.inf),
            "empty": dict(predictions=self.predictions[:0], targets=self.targets[:0]),
            "duplicate_names": dict(predictions=self.predictions, targets=self.targets, model_names=["a", "a", "b"]),
        }
        for label, arrays in cases.items():
            with self.subTest(label=label):
                source, output = self.root / f"{label}.npz", self.root / f"{label}.json"
                np.savez(source, **arrays)
                self.run_cli("fit", "--calibration", source, "--rule", "inverse", "--output", output, succeeds=False)
                self.assertFalse(output.exists())

    def test_query_shapes_nonfinite_values_and_tampered_weights_are_rejected(self):
        weights, record = self.fit()
        cases = {
            "wrong_field": self.predictions[:, :, :, :2],
            "wrong_count": self.predictions[:, :2],
            "nonfinite_query": np.full_like(self.predictions, np.inf),
        }
        for label, predictions in cases.items():
            with self.subTest(label=label):
                query, output = self.root / f"{label}.npz", self.root / f"{label}_out.npz"
                np.savez(query, predictions=predictions, model_names=self.names[:predictions.shape[1]])
                self.run_cli("predict", "--predictions", query, "--weights", weights, "--output", output, succeeds=False)
                self.assertFalse(output.exists())
        record["weights"] = [1.0, 1.0, 1.0]
        tampered = self.root / "tampered.json"
        tampered.write_text(json.dumps(record))
        self.run_cli("predict", "--predictions", self.calibration, "--weights", tampered,
                     "--output", self.root / "tampered_out.npz", succeeds=False)

    def test_unnamed_positional_library_and_existing_output_protection(self):
        unnamed = self.root / "unnamed.npz"
        np.savez(unnamed, predictions=self.predictions, targets=self.targets)
        weights, record = self.fit(calibration=unnamed)
        self.assertFalse(record["model_names_provided"])
        self.assertEqual(record["model_names"], ["model_0", "model_1", "model_2"])
        query, output = self.root / "unnamed_query.npz", self.root / "unnamed_out.npz"
        np.savez(query, predictions=self.predictions[:1])
        self.run_cli("predict", "--predictions", query, "--weights", weights, "--output", output)
        before = output.read_bytes()
        self.run_cli("predict", "--predictions", query, "--weights", weights, "--output", output, succeeds=False)
        self.assertEqual(output.read_bytes(), before)

    def test_auto_requires_two_calibration_cases(self):
        one = self.root / "one.npz"
        np.savez(one, predictions=self.predictions[:1], targets=self.targets[:1])
        result = self.run_cli("fit", "--calibration", one, "--rule", "auto",
                              "--output", self.root / "one.json", succeeds=False)
        self.assertIn("at least two calibration cases", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
