"""Small array checks of provenance failures and evaluation isolation."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest import mock

import numpy as np

SPEC = importlib.util.spec_from_file_location(
    "era5_baseline_collector", Path(__file__).resolve().parents[1] / "collect_baselines.py")
collector = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(collector)


def json_file(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, allow_nan=False))


class CollectorTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        for folder in ["predictions", "metadata", "answers/era5", "results"]:
            (self.root / folder).mkdir(parents=True)
        self.records = [{"id": f"B{i+1}", "model": name}
                        for i, name in enumerate(collector.BASELINE_MODELS)]
        self.info = dict(n_query=17, n_base_hf_train=55, work_grid=[2, 3],
                         n_original_test=7, calibration_from_original_hf_train=list(range(55, 65)))
        self.theta = np.arange(17 * 12, dtype=np.float32).reshape(17, 12)
        self.manifests = {"source_manifest_sha256": "source-fixed",
                          "plan_sha256": "plan-fixed", "input_manifest_sha256": "input-fixed"}
        for i, row in enumerate(self.records):
            self.write_prediction(row["model"], np.full((17, 6), 1 + i / 10, np.float32))

    def write_prediction(self, model, prediction, theta=None, grid=None, **meta_changes):
        pred_path = self.root / "predictions" / f"{model}__era5.npz"
        np.savez_compressed(pred_path, pred=prediction, theta=self.theta if theta is None else theta,
                            work_grid=self.info["work_grid"] if grid is None else grid)
        metadata = dict(model=model, dataset="era5", smoke=False, scientific_result=True,
                        n_base_hf_train=55, prediction_sha256=collector.digest(pred_path),
                        **self.manifests)
        metadata.update(meta_changes)
        json_file(self.root / "metadata" / f"{model}__era5.json", metadata)

    def update_metadata(self, model, **changes):
        path = self.root / "metadata" / f"{model}__era5.json"
        data = json.loads(path.read_text())
        data.update(changes)
        json_file(path, data)

    def validate(self):
        return collector.validate_predictions(self.root, self.records, self.info, self.theta, self.manifests)

    def make_answers(self, reverse_eval=False):
        hashes = {}
        for split, rows, value in [("calibration", np.arange(10), 10.),
                                   ("evaluation", np.arange(10, 17), 2.)]:
            theta = self.theta[rows]
            if split == "evaluation" and reverse_eval:
                theta = theta[::-1]
            path = self.root / "answers" / "era5" / f"{split}.npz"
            np.savez_compressed(path, theta=theta, target=np.full((len(rows), 6), value),
                                query_rows=rows, work_grid=[2, 3])
            hashes[split] = collector.digest(path)
        return hashes

    def test_complete_roster_and_provenance_pass(self):
        collector.validate_roster({"models": self.records})
        predictions, metadata, hashes, aliases = self.validate()
        self.assertEqual(len(predictions), 12)
        self.assertEqual(len(hashes), 12)
        self.assertEqual(aliases, {})

    def test_missing_baseline_does_not_count_as_completed(self):
        (self.root / "predictions" / "st_knn__era5.npz").unlink()
        with self.assertRaisesRegex(collector.CollectionError, "Incomplete campaign.*st_knn"):
            self.validate()

    def test_modified_prediction_hash_rejected(self):
        with (self.root / "predictions" / "st_koh_pod__era5.npz").open("ab") as handle:
            handle.write(b"changed")
        with self.assertRaisesRegex(collector.CollectionError, "prediction hash mismatch"):
            self.validate()

    def test_different_training_protocol_rejected(self):
        for changes, match in [({"plan_sha256": "wrong"}, "plan_sha256 mismatch"),
                               ({"n_base_hf_train": 65}, "base HF count mismatch"),
                               ({"smoke": True}, "not an explicit full run"),
                               ({"scientific_result": False}, "not a scientific result")]:
            with self.subTest(changes=changes):
                self.write_prediction("st_koh_pod", np.ones((17, 6), np.float32), **changes)
                with self.assertRaisesRegex(collector.CollectionError, match):
                    self.validate()

    def test_reordered_prediction_rows_rejected_even_with_valid_hash(self):
        self.write_prediction("st_mfdnn", np.ones((17, 6), np.float32), theta=self.theta[::-1])
        with self.assertRaisesRegex(collector.CollectionError, "input correspondence"):
            self.validate()

    def test_wrong_grid_and_nonfinite_fields_rejected(self):
        self.write_prediction("st_dmfal", np.ones((17, 6), np.float32), grid=[3, 2])
        with self.assertRaisesRegex(collector.CollectionError, "work grid"):
            self.validate()
        prediction = np.ones((17, 6), np.float32)
        prediction[8, 0] = np.nan
        self.write_prediction("st_dmfal", prediction)
        with self.assertRaisesRegex(collector.CollectionError, "nonfinite prediction"):
            self.validate()

    def test_alias_is_reported_as_reused_and_must_be_identical(self):
        source = np.full((17, 6), 3., np.float32)
        self.write_prediction("mf_fno_transfer", source)
        self.write_prediction("mf_fno_transfer_bar", source, reused_from="mf_fno_transfer")
        _, _, _, aliases = self.validate()
        self.assertEqual(aliases, {"mf_fno_transfer_bar": "mf_fno_transfer"})
        self.write_prediction("mf_fno_transfer_bar", source + 1, reused_from="mf_fno_transfer")
        with self.assertRaisesRegex(collector.CollectionError, "reused prediction"):
            self.validate()

    def test_unexpected_alias_rejected(self):
        self.update_metadata("st_knn", reused_from="st_koh_pod")
        with self.assertRaisesRegex(collector.CollectionError, "undeclared recipe reuse"):
            self.validate()

    def test_declared_alias_cannot_be_counted_as_an_independent_fit(self):
        self.records[9]["alias_of"] = "mf_fno_transfer"
        with self.assertRaisesRegex(collector.CollectionError, "declared recipe alias"):
            self.validate()

    def test_answer_hash_and_input_order_are_both_required(self):
        hashes = self.make_answers()
        hashes["evaluation"] = "wrong"
        with self.assertRaisesRegex(collector.CollectionError, "sealed answer hash mismatch"):
            collector.load_answers(self.root, self.info, self.theta, hashes)
        hashes = self.make_answers(reverse_eval=True)
        with self.assertRaisesRegex(collector.CollectionError, "evaluation: answer input correspondence"):
            collector.load_answers(self.root, self.info, self.theta, hashes)

    def test_evaluation_mean_does_not_include_calibration_errors(self):
        predictions, metadata, _, aliases = self.validate()
        answers = collector.load_answers(self.root, self.info, self.theta, self.make_answers())
        rows, per_case, means, calibration = collector.assemble_results(
            self.records, predictions, metadata, aliases, answers, np.ones(6), self.info)
        self.assertEqual(len(rows), 26)
        self.assertAlmostEqual(means["st_koh_pod"], .5)
        self.assertAlmostEqual(calibration["st_koh_pod"], .9)
        np.testing.assert_allclose(per_case["evaluation__st_koh_pod"], np.full(7, .5))
        np.testing.assert_array_equal(per_case["evaluation__query_rows"], np.arange(10, 17))

    def test_missing_run_stops_main_before_opening_answers_and_preserves_prior_results(self):
        info = {**self.info, "work_grid": [128, 256]}
        for name in ["SOURCE.json", "PLAN.json", "INPUT_MANIFEST.json"]:
            json_file(self.root / name, {})
        json_file(self.root / "BASELINES.json", {"models": self.records})
        query_dir = self.root / "data/core/era5"
        query_dir.mkdir(parents=True)
        np.savez_compressed(query_dir / "test_l9.npz", x=self.theta, y=np.zeros((17, 1)))
        prior = self.root / "results/era5_baselines__summary.json"
        prior.write_text('{"previous_result": true}')
        (self.root / "predictions" / "st_knn__era5.npz").unlink()
        fake_common = types.SimpleNamespace(ROOT=self.root, verify_source=lambda: {},
                                             verify_inputs=lambda: {},
                                             load_plan=lambda: {"datasets": {"era5": info}},
                                             write_json=json_file)
        loaded_paths = []
        original_load = np.load

        def observed_load(path, *args, **kwargs):
            loaded_paths.append(str(path))
            self.assertNotIn("answers/", str(path))
            return original_load(path, *args, **kwargs)

        with mock.patch.dict(sys.modules, {"baseline_common": fake_common}), \
                mock.patch.object(collector.np, "load", side_effect=observed_load):
            with self.assertRaisesRegex(collector.CollectionError, "Incomplete campaign"):
                collector.main()
        self.assertEqual(len(loaded_paths), 1)
        self.assertEqual(prior.read_text(), '{"previous_result": true}')
        status = json.loads((self.root / "results/era5_baselines__status.json").read_text())
        self.assertFalse(status["complete"])
        self.assertFalse((self.root / "results/era5_baselines.csv").exists())


if __name__ == "__main__":
    unittest.main()
