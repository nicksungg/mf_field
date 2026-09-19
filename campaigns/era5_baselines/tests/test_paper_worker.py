"""Small CPU tests for scientific identity and interrupted training recovery."""
import argparse
import contextlib
import copy
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import torch

import paper_resume
from stage_train import StageTrainer
import worker_paper


def fixture_data():
    rng = np.random.default_rng(8)
    x1 = rng.normal(size=(24, 2)).astype(np.float32)
    x2 = rng.normal(size=(18, 2)).astype(np.float32)
    xq = rng.normal(size=(3, 2)).astype(np.float32)
    pattern = np.arange(32, dtype=np.float32).reshape(1, -1)/32
    def field(x):
        return (2 + x[:, :1] + x[:, 1:2]*pattern).astype(np.float32)
    def dataset(xs, ys):
        return dict(fids=[1, 2], hf_fid=2, lf_fids=[1],
                    cond_by_fid={1: xs[0], 2: xs[1]},
                    field_by_fid={1: ys[0], 2: ys[1]},
                    n_cells_by_fid={1: 32, 2: 32}, cond_dim=2,
                    loader='fixture')
    train = dataset([x1, x2], [field(x1), field(x2)])
    query = dataset([xq, xq], [np.zeros((3, 32), np.float32)]*2)
    def load(path, split='train'):
        if split == 'ood':
            raise FileNotFoundError
        return copy.deepcopy(train if split == 'train' else query)
    return load


def run_fixture(model, folder, *, original=False, interrupt_stage=None, epochs=8):
    with worker_paper.import_frozen(model, {'fixture': True, 'epochs': epochs}) as mod:
        if original:
            # Re-execute the untouched vendored recipe as the control.
            source = worker_paper.ROOT/'vendor'/model/'smoke_eval.py'
            exec(compile(source.read_text(), str(source), 'exec'), mod.__dict__)
        mod.load_mf_dataset = fixture_data()
        mod.resolve_grid = lambda *args: (4, 8)
        if model == 'fno_coregionalization':
            mod.SMOKE_DEFAULTS = dict(mod.SMOKE_DEFAULTS,
                hidden_channels=4, K=2, n_blocks=1, modes_cap=2, b_hidden=4,
                batch_size=4, ckpt_every=1, val_frac=.2)
        captured = {}
        mod.finalize_and_write = lambda **kwargs: captured.update(kwargs)
        real_save = mod.atomic_save
        if interrupt_stage is not None:
            def interrupted(state, path):
                real_save(state, path)
                is_last = Path(path).name == 'last.pt'
                current_stage = state.get('stage', 'mfrnp')
                if is_last and current_stage == interrupt_stage:
                    raise RuntimeError('simulated interruption')
            mod.atomic_save = interrupted
        args = argparse.Namespace(dataset_dir='fixture', dataset_name='era5',
            seed=42, epochs=epochs, ckpt_dir=str(folder), out=str(folder/'ignored.json'))
        with patch('torch.cuda.is_available', return_value=False):
            mod.run(args)
        return captured['pred']


class PaperWorkerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        torch.set_num_threads(1)

    def test_alias_proves_recipe_identity_and_rejects_changes(self):
        self.assertFalse(worker_paper.alias_evidence()['independent_training'])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for model in (worker_paper.ALIAS_SOURCE, worker_paper.ALIAS_TARGET):
                dest = root/'vendor'/model
                dest.mkdir(parents=True)
                for filename in ('model.py', 'smoke_eval.py'):
                    (dest/filename).write_bytes((worker_paper.ROOT/'vendor'/model/filename).read_bytes())
            changed = root/'vendor'/worker_paper.ALIAS_TARGET/'smoke_eval.py'
            changed.write_text(changed.read_text().replace('lr_finetune=3e-4', 'lr_finetune=7e-4'))
            with patch.object(worker_paper, 'ROOT', root):
                with self.assertRaisesRegex(AssertionError, 'recipes differ'):
                    worker_paper.alias_evidence()

    def test_transfer_resume_matches_original_sample_sequence(self):
        torch.manual_seed(7)
        initial = torch.nn.Linear(2, 1)
        x = np.arange(12, dtype=np.float32).reshape(6, 2)/10
        y = x.sum(1, keepdims=True)
        settings = dict(batch_size=4, weight_decay=1e-5, grad_clip=1.)
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()):
            full, partial = copy.deepcopy(initial), copy.deepcopy(initial)
            StageTrainer(Path(tmp)/'full', 'fixture')(full, x, y, 1., 30, .01, settings, 'cpu', 'stage')
            trainer = StageTrainer(Path(tmp)/'partial', 'fixture')
            with patch('stage_train.write_json', side_effect=RuntimeError('simulated interruption')):
                with self.assertRaisesRegex(RuntimeError, 'simulated interruption'):
                    trainer(partial, x, y, 1., 30, .01, settings, 'cpu', 'stage')
            resumed = copy.deepcopy(initial)
            trainer(resumed, x, y, 1., 30, .01, settings, 'cpu', 'stage')
            for a, b in zip(full.parameters(), resumed.parameters()):
                torch.testing.assert_close(a, b, rtol=0, atol=0)

    def test_coregionalization_unchanged_and_resumes_both_stages(self):
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()):
            root = Path(tmp)
            original = run_fixture('fno_coregionalization', root/'original', original=True)
            full = run_fixture('fno_coregionalization', root/'full')
            np.testing.assert_array_equal(full, original)
            for stage in (1, 2):
                folder = root/f'interrupt_{stage}'
                with self.assertRaisesRegex(RuntimeError, 'simulated interruption'):
                    run_fixture('fno_coregionalization', folder, interrupt_stage=stage)
                resumed = run_fixture('fno_coregionalization', folder)
                np.testing.assert_array_equal(resumed, full)

    def test_mfrnp_unchanged_and_resumes_rng_and_loader(self):
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()):
            root = Path(tmp)
            original = run_fixture('mfrnp', root/'original', original=True, epochs=5)
            full = run_fixture('mfrnp', root/'full', epochs=5)
            np.testing.assert_array_equal(full, original)
            with self.assertRaisesRegex(RuntimeError, 'simulated interruption'):
                run_fixture('mfrnp', root/'interrupted', interrupt_stage='mfrnp', epochs=5)
            resumed = run_fixture('mfrnp', root/'interrupted', epochs=5)
            np.testing.assert_array_equal(resumed, full)


if __name__ == '__main__':
    unittest.main()
