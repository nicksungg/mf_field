"""Checkpoint-only adaptations for the frozen ERA5 paper baselines.

These changes preserve each training objective, network, optimizer, split and
sample ordering. They make interrupted jobs continue the same trajectory.
Frozen vendor files are never edited; the asserted replacements are applied to
their source in memory by worker_paper.py.
"""
from __future__ import annotations

import copy
import os
import random
from pathlib import Path

import numpy as np
import torch


def capture_rng():
    return dict(torch=torch.get_rng_state(), numpy=np.random.get_state(),
                python=random.getstate(),
                cuda=torch.cuda.get_rng_state_all() if torch.cuda.is_available() else [])


def restore_rng(state):
    torch.set_rng_state(state['torch'].cpu())
    np.random.set_state(state['numpy'])
    random.setstate(state['python'])
    if torch.cuda.is_available():
        torch.cuda.set_rng_state_all([x.cpu() for x in state['cuda']])


def atomic_save(state, path):
    path = Path(path)
    temp = path.with_name(path.name + f'.tmp.{os.getpid()}')
    torch.save(state, temp)
    os.replace(temp, path)


def resumable_mf_loader(original):
    """The frozen MFRNP permutation sequence with a compact order checkpoint."""
    class ResumableMFLoader(original):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.order = [np.arange(len(x)) for x in self.Xs]

        def __iter__(self):
            if self.shuffle:
                for lvl in range(len(self.Xs)):
                    idx = self.rng.permutation(self.Xs[lvl].shape[0])
                    self.Xs[lvl] = self.Xs[lvl][idx]
                    self.ys[lvl] = self.ys[lvl][idx]
                    self.order[lvl] = self.order[lvl][idx]
            for b in range(0, self.n_iter, self.batch_size):
                xs = [torch.from_numpy(x[b:b+self.batch_size]).to(self.device)
                      for x in self.Xs]
                ys = [torch.from_numpy(y[b:b+self.batch_size]).to(self.device)
                      for y in self.ys]
                yield xs, ys

        def state_dict(self):
            return dict(order=[x.copy() for x in self.order],
                        rng=copy.deepcopy(self.rng.bit_generator.state))

        def load_state_dict(self, state):
            assert all(np.array_equal(x, np.arange(len(x))) for x in self.order), \
                'Restore loader only before the first iteration'
            for lvl, order in enumerate(state['order']):
                order = np.asarray(order)
                assert np.array_equal(np.sort(order), np.arange(len(self.Xs[lvl])))
                self.Xs[lvl] = self.Xs[lvl][order]
                self.ys[lvl] = self.ys[lvl][order]
                self.order[lvl] = order.copy()
            self.rng.bit_generator.state = copy.deepcopy(state['rng'])
    return ResumableMFLoader


def replace_once(source, old, new):
    assert source.count(old) == 1, f'Frozen source changed around {old[:100]!r}'
    return source.replace(old, new, 1)


def adapt_mfrnp(source):
    source = replace_once(source, '    start_epoch = 0\n', '    start_epoch = 0\n    sd = None\n')
    source = replace_once(source,
        '        sd = torch.load(last_ckpt, map_location=device)\n',
        '        sd = torch.load(last_ckpt, map_location=device, weights_only=False)\n'
        '        assert sd.get("run_identity") == _RUN_IDENTITY, "Checkpoint identity mismatch"\n')
    source = replace_once(source,
        '    # ---- training -------------------------------------------------------\n',
        '    if sd is not None:\n'
        '        assert sd["epochs_target"] == args.epochs\n'
        '        train_loader.load_state_dict(sd["loader_state"])\n'
        '        restore_rng(sd["rng_state"])\n'
        '\n    # ---- training -------------------------------------------------------\n')
    source = replace_once(source, '        torch.save({\n', '        atomic_save({\n')
    source = replace_once(source,
        '            "epochs_target": args.epochs,\n',
        '            "epochs_target": args.epochs,\n'
        '            "run_identity": _RUN_IDENTITY,\n'
        '            "rng_state": capture_rng(),\n'
        '            "loader_state": train_loader.state_dict(),\n'
        '            "elapsed_train_seconds": (sd.get("elapsed_train_seconds", 0.) if sd else 0.) + time.time() - t_train,\n')
    source = replace_once(source, '    train_seconds = time.time() - t_train\n',
        '    train_seconds = (sd.get("elapsed_train_seconds", 0.) if sd else 0.) + time.time() - t_train\n')
    source = replace_once(source, '            loss_val.backward()\n',
        '            if not torch.isfinite(loss_val):\n'
        '                raise RuntimeError(f"Nonfinite MFRNP loss at epoch {epoch}")\n'
        '            loss_val.backward()\n')
    return source


def adapt_coregionalization(source):
    start = source.index('    # Resume guard: only a finished checkpoint')
    end = source.index('    n_params = param_count(model)', start)
    source = source[:start] + '''    # Resume training state without changing either stage's optimizer recipe.
    resume_state = None
    trained = False
    if last_ckpt.exists():
        resume_state = torch.load(last_ckpt, map_location=device, weights_only=False)
        sd = resume_state
        assert sd.get("run_identity") == _RUN_IDENTITY, "Checkpoint identity mismatch"
        assert sd["epochs_target"] == args.epochs and sd["grid"] == list(grid)
        assert sd["recipe_hash"] == rh and sd["stage"] in (1, 2)
        assert 0 <= sd["epoch"] <= args.epochs
        model.load_state_dict(sd["model"])
        best_val = sd["best_val"]
        trained = sd["stage"] == 2 and sd["epoch"] == args.epochs
        print(f"[resume] stage {sd['stage']} epoch {sd['epoch']}/{args.epochs}", flush=True)

    def _save_last(stage: int, epoch: int):
        atomic_save({
            "stage": stage, "epoch": epoch, "epochs_target": args.epochs,
            "grid": list(grid), "recipe_hash": rh, "run_identity": _RUN_IDENTITY,
            "model": model.state_dict(), "best_val": best_val,
            "optimizer": opt.state_dict(), "scheduler": sched.state_dict(),
            "rng_state": capture_rng(),
            "elapsed_train_seconds": (resume_state.get("elapsed_train_seconds", 0.) if resume_state else 0.) + time.time() - t_train,
        }, last_ckpt)

''' + source[end:]
    source = replace_once(source,
        '        if n_warmup > 0 and lf_tr_loader is not None:\n',
        '        if n_warmup > 0 and lf_tr_loader is not None and (resume_state is None or resume_state["stage"] == 1):\n')
    source = replace_once(source,
        '            for s1_epoch in range(1, n_warmup + 1):\n',
        '            stage_start = 1\n'
        '            if resume_state is not None and resume_state["stage"] == 1:\n'
        '                opt.load_state_dict(resume_state["optimizer"])\n'
        '                sched.load_state_dict(resume_state["scheduler"])\n'
        '                restore_rng(resume_state["rng_state"])\n'
        '                stage_start = resume_state["epoch"] + 1\n'
        '            for s1_epoch in range(stage_start, n_warmup + 1):\n')
    source = replace_once(source, '        elif n_warmup > 0:\n',
        '        elif n_warmup > 0 and lf_tr_loader is None:\n')
    source = replace_once(source,
        '            for s2_epoch in range(1, n_finetune + 1):\n',
        '            stage_start = 1\n'
        '            if resume_state is not None and resume_state["stage"] == 2:\n'
        '                opt.load_state_dict(resume_state["optimizer"])\n'
        '                sched.load_state_dict(resume_state["scheduler"])\n'
        '                restore_rng(resume_state["rng_state"])\n'
        '                stage_start = resume_state["epoch"] - n_warmup + 1\n'
        '            for s2_epoch in range(stage_start, n_finetune + 1):\n')
    source = replace_once(source, '    train_seconds = time.time() - t_train\n',
        '    train_seconds = (resume_state.get("elapsed_train_seconds", 0.) if resume_state else 0.) + time.time() - t_train\n')
    source = replace_once(source,
        '        model.load_state_dict(torch.load(best_ckpt, map_location=device)["model"])\n',
        '        model.load_state_dict(torch.load(best_ckpt, map_location=device, weights_only=False)["model"])\n')
    assert source.count('                    loss.backward()\n') == 2
    source = source.replace('                    loss.backward()\n',
        '                    if not torch.isfinite(loss):\n'
        '                        raise RuntimeError("Nonfinite coregionalization loss")\n'
        '                    loss.backward()\n')
    # Best-model saves are also atomic, with unchanged selection criteria.
    source = source.replace('torch.save({"model": model.state_dict()}, best_ckpt)',
                            'atomic_save({"model": model.state_dict()}, best_ckpt)')
    return source
