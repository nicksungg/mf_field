"""Input exclusion, atomic optimizer replay, and ensemble identity checks."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import torch

import run_coarse as c


def fixture():
    hf = np.arange(5, dtype=np.float32)[:, None]
    lf = np.repeat(hf, 2, axis=0)
    query = np.asarray([[10.], [11.]], np.float32)
    folds = [dict(fold=f, hold_hf_rows=[f], train_lf_rows=[i for i in range(10) if i // 2 != f]) for f in range(5)]
    tasks = [dict(fold=f, variant=v, seed=s, tag=f'{v}_f{f}_s{s}')
             for f in range(5) for v in ['plain', 'hetero'] for s in [42, 123]]
    return dict(folds=folds, tasks=tasks), dict(x_lf=lf, x_hf=hf, x_query=query)


class CoarseSafety(unittest.TestCase):
    def test_duplicate_hf_identities_must_stay_in_one_fold(self):
        plan, data = fixture()
        data['x_hf'] = np.concatenate([data['x_hf'], data['x_hf'][:1]])
        plan['folds'][0]['hold_hf_rows'].append(5)
        c.checked_plan(plan, data)
        plan['folds'][0]['hold_hf_rows'].remove(5)
        plan['folds'][1]['hold_hf_rows'].append(5)
        with self.assertRaisesRegex(AssertionError, 'Duplicate HF identity split'):
            c.checked_plan(plan, data)

    def test_excludes_every_duplicate_lf_occurrence(self):
        plan, data = fixture()
        c.checked_plan(plan, data)
        plan['folds'][0]['train_lf_rows'].append(1)
        with self.assertRaisesRegex(AssertionError, 'identity exclusion'):
            c.checked_plan(plan, data)

    def test_rejects_query_identity_in_lf_training(self):
        plan, data = fixture()
        data['x_lf'][0] = data['x_query'][0]
        with self.assertRaisesRegex(AssertionError, 'Reserved query'):
            c.checked_plan(plan, data)

    def test_never_reads_hf_targets_and_blocks_answer_files(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path = root / 'data/training.npz'
            # This deliberately has no y_hf key. Coarse training must not need it.
            c.save_npz(path, x_lf=np.zeros((2, 1)), y_lf=np.zeros((2, 2, 2)),
                       x_hf=np.ones((1, 1)), x_query=np.full((1, 1), 2.))
            with patch.object(c, 'ROOT', root), c.restricted_load([path]):
                self.assertEqual(set(c.training_inputs()), {'x_lf', 'y_lf', 'x_hf', 'x_query'})
                with self.assertRaisesRegex(RuntimeError, 'Unauthorized'):
                    np.load(root / 'answers/evaluation.npz')

    def test_atomic_resume_replays_partial_epoch_and_rng(self):
        torch.set_num_threads(1)
        torch.manual_seed(19)
        initial = torch.nn.Sequential(torch.nn.Linear(2, 4), torch.nn.Dropout(.25), torch.nn.Linear(4, 1))
        x = torch.arange(14, dtype=torch.float32).reshape(7, 2) / 10
        y = x.sum(1, keepdim=True)
        settings = dict(lr_pretrain=.01, weight_decay=1e-5, batch_size=4, grad_clip=1.)
        key = dict(seed=123, tag='test')
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            complete = copy.deepcopy(initial)
            partial = copy.deepcopy(initial)
            torch.manual_seed(27)
            c.train_loop(complete, x, y, root / 'complete.pt', key, settings, 4, 8, 'cpu', checkpoint_every=1)
            torch.manual_seed(27)
            with patch.object(c, 'write_json', side_effect=RuntimeError('interrupted after atomic checkpoint')):
                with self.assertRaisesRegex(RuntimeError, 'interrupted'):
                    c.train_loop(partial, x, y, root / 'partial.pt', key, settings, 4, 8, 'cpu', checkpoint_every=1)
            checkpoint = torch.load(root / 'partial.pt', map_location='cpu', weights_only=False)
            self.assertEqual(checkpoint['step'], 1)
            self.assertEqual(checkpoint['offset'], 4)
            resumed = copy.deepcopy(initial)
            c.train_loop(resumed, x, y, root / 'partial.pt', key, settings, 4, 8, 'cpu', checkpoint_every=1)
            for expected, actual in zip(complete.parameters(), resumed.parameters()):
                torch.testing.assert_close(expected, actual, rtol=0, atol=0)
            with self.assertRaisesRegex(AssertionError, 'identity mismatch'):
                c.train_loop(resumed, x, y, root / 'partial.pt', dict(key, tag='wrong'), settings, 4, 8, 'cpu')

    def test_assembly_uses_four_fold_zero_queries_and_checks_theta(self):
        plan, data = fixture()
        folds = c.checked_plan(plan, data)
        config, identity = {'coarse_grid': [2, 2]}, {'smoke': True}
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder)
            for i, task in enumerate(plan['tasks']):
                hold = np.asarray(folds[task['fold']]['hold_hf_rows'], np.int64)
                train = np.asarray(folds[task['fold']]['train_lf_rows'], np.int64)
                path = out / 'preds' / (task['tag'] + '.npz')
                c.save_npz(path, hold_rows=hold, mu_hold=np.full((1, 2, 2), float(i)),
                           mu_query=np.full((2, 2, 2), float(i)), theta_hold=data['x_hf'][hold], theta_query=data['x_query'])
                masks = dict(train_lf_rows_sha256=c.array_sha(train), hold_hf_rows_sha256=c.array_sha(hold),
                             theta_hold_sha256=c.array_sha(data['x_hf'][hold]), theta_query_sha256=c.array_sha(data['x_query']))
                c.write_json(out / 'raw' / (task['tag'] + '.json'), dict(complete=True, identity=identity, task=task,
                    masks=masks, prediction_sha256=c.sha(path), query_targets_read=False, hf_targets_read=False))
            c.assemble(config, plan, data, folds, identity, out)
            with np.load(out / 'oof.npz') as z:
                np.testing.assert_array_equal(z['n_members_train'], np.full(5, 4))
                self.assertEqual(int(z['members_query']), 4)
                np.testing.assert_array_equal(z['mean_train'][:, 0, 0], [1.5, 5.5, 9.5, 13.5, 17.5])
                np.testing.assert_array_equal(z['mean_query'], np.full((2, 2, 2), 1.5))
            # Update the file hash too: identity checks must still catch corruption.
            task = plan['tasks'][0]
            path = out / 'preds' / (task['tag'] + '.npz')
            with np.load(path) as z:
                arrays = {k: z[k].copy() for k in z.files}
            arrays['theta_query'][0, 0] += 1
            c.save_npz(path, **arrays)
            mp = out / 'raw' / (task['tag'] + '.json')
            metadata = json.loads(mp.read_text())
            metadata['prediction_sha256'] = c.sha(path)
            c.write_json(mp, metadata)
            with self.assertRaises(AssertionError):
                c.assemble(config, plan, data, folds, identity, out)


if __name__ == '__main__':
    unittest.main()
