import unittest
import numpy as np
from prepare_era5 import coarse_folds, grouped_split
from era5_common import input_keys

class UnpairedCaseRoles(unittest.TestCase):
    def test_ninth_expert_is_available_to_every_rule(self):
        from ensemble_rules import gram, fit_auto
        rng = np.random.default_rng(21)
        target = 2 + rng.normal(size=(5, 12))
        pred = target[:, None, :] + rng.normal(size=(5, 9, 12))
        pred[:, 8] = target
        weights, choice = fit_auto(gram(pred, target))
        for name, w in weights.items():
            self.assertEqual(w.shape, (9,), name)
            self.assertAlmostEqual(w.sum(), 1)
        self.assertEqual(weights['selected_single'][8], 1)
        self.assertGreater(weights['inverse_mse'][8], .999)

    def test_coarse_folds_use_identity_not_row_order_and_exclude_duplicates(self):
        hf = np.array([[1], [2], [3], [4], [5], [1]], np.float32)
        lf = np.array([[99], [2], [1], [88], [1], [5], [3], [4]], np.float32)
        folds = coarse_folds(lf, hf)
        assigned = {}
        for f in folds:
            held = set(input_keys(hf[f['hold_hf_rows']]))
            trained = set(input_keys(lf[f['train_lf_rows']]))
            self.assertFalse(held & trained)
            for i in f['hold_hf_rows']:
                assigned[i] = f['fold']
            for key in [input_keys(np.array([[99]], np.float32))[0],
                        input_keys(np.array([[88]], np.float32))[0]]:
                self.assertIn(key, trained)
        self.assertEqual(assigned[0], assigned[5])
        order = np.array([7, 2, 0, 4, 1, 5, 3, 6])
        shuffled = coarse_folds(lf[order], hf)
        for first, second in zip(folds, shuffled):
            self.assertEqual(set(input_keys(lf[first['train_lf_rows']])),
                             set(input_keys(lf[order][second['train_lf_rows']])))

    def test_corrector_validation_keeps_duplicate_inputs_together(self):
        x = np.array([[i] for i in range(10)] + [[1], [1], [7]], np.float32)
        split = grouped_split(x)
        self.assertFalse(set(input_keys(x[split['train_rows']])) &
                         set(input_keys(x[split['val_rows']])))
        self.assertEqual(sorted(split['train_rows'] + split['val_rows']), list(range(len(x))))

if __name__ == '__main__':
    unittest.main()
