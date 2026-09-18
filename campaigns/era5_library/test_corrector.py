"""CPU checks for the ERA5 corrector's data boundary and training recipe."""
import copy
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import torch
from torch.nn import functional as F
from torch.utils.checkpoint import checkpoint

import run_corrector as corrector


class CorrectorChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_threads = torch.get_num_threads()
        torch.set_num_threads(2)

    @classmethod
    def tearDownClass(cls):
        torch.set_num_threads(cls.original_threads)

    def inputs(self):
        rng = np.random.default_rng(192)
        x = rng.normal(size=(55, 12)).astype(np.float32)
        xq = rng.normal(size=(17, 12)).astype(np.float32)
        coarse = rng.normal(size=(55, 8, 16)).astype(np.float32)
        coarse_query = rng.normal(size=(17, 8, 16)).astype(np.float32)
        fine = 2 * coarse + rng.normal(scale=.1, size=coarse.shape).astype(np.float32)
        data = {"x_hf": x, "y_hf": fine, "x_query": xq}
        return data, coarse, coarse_query, np.arange(49), np.arange(49, 55)

    def test_normalization_uses_only_corrector_training(self):
        data, coarse, query, train, val = self.inputs()
        _, expected = corrector.prepare_inputs(data, coarse, query, train)
        changed = {name: value.copy() for name, value in data.items()}
        changed["x_hf"][val] += 99
        changed["y_hf"][val] *= -50
        changed["x_query"] *= 200
        changed_coarse = coarse.copy()
        changed_coarse[val] *= 100
        _, actual = corrector.prepare_inputs(changed, changed_coarse, query * 100, train)
        self.assertEqual(expected, actual)
        self.assertLess(abs(expected["rho"] - 2), .01)
        self.assertEqual(expected["normalization_rows"], train.tolist())

    def test_parameter_groups_cannot_cross_roles(self):
        data, _, _, train, val = self.inputs()
        split = {"train_rows": train.tolist(), "val_rows": val.tolist()}
        actual_train, actual_val = corrector.validate_split(data["x_hf"], data["x_query"], split)
        np.testing.assert_array_equal(actual_train, train)
        np.testing.assert_array_equal(actual_val, val)
        bad = data["x_hf"].copy()
        bad[val[0]] = bad[train[0]]
        with self.assertRaisesRegex(ValueError, "parameter group"):
            corrector.validate_split(bad, data["x_query"], split)
        bad_query = data["x_query"].copy()
        bad_query[0] = data["x_hf"][0]
        with self.assertRaisesRegex(ValueError, "Reserved query"):
            corrector.validate_split(data["x_hf"], bad_query, split)
        with self.assertRaisesRegex(ValueError, "exactly once"):
            corrector.validate_split(data["x_hf"], data["x_query"],
                                     {"train_rows": train.tolist() + [0], "val_rows": val.tolist()})

    def test_zero_coarse_requires_explicit_smoke_stub(self):
        data, coarse, query, train, _ = self.inputs()
        with self.assertRaisesRegex(ValueError, "zero or invalid"):
            corrector.prepare_inputs(data, np.zeros_like(coarse), np.zeros_like(query), train)
        arrays, settings = corrector.prepare_inputs(
            data, np.zeros_like(coarse), np.zeros_like(query), train, synthetic_stub=True)
        self.assertTrue(settings["synthetic_normalization"])
        self.assertEqual(settings["scale"], 1)
        self.assertEqual(settings["rho"], 1)
        self.assertEqual(torch.count_nonzero(arrays["h"]).item(), 0)

    def test_both_actual_backbones_six_step_loss(self):
        bb = corrector.load_backbones()
        grid = (8, 16)
        radius = corrector.radial(grid, "cpu")
        for backbone in ("transolver", "convnext"):
            with self.subTest(backbone=backbone):
                torch.manual_seed(91)
                model = bb.build(backbone, 12, bb.coordinates(grid, "periodic_node", "cpu"),
                                 0, width=32, base=48)
                cond, h, target = torch.randn(1, 12), torch.randn(1, *grid), torch.randn(1, *grid)
                with torch.no_grad():
                    initial = model(cond, h, None)
                self.assertEqual(initial.shape, h.shape)
                self.assertEqual(torch.count_nonzero(initial).item(), 0)
                spectrum = torch.fft.fft2(target, norm="ortho").abs()
                loss = target.new_zeros(())
                for k in range(6):
                    h = h + .2 * checkpoint(model, cond, h, None, use_reentrant=False)
                    weight = 1 + radius.pow(1 + k / 5)
                    weight = weight / weight.mean()
                    spectral = ((torch.fft.fft2(h, norm="ortho").abs() - spectrum).square() * weight).mean()
                    loss = loss + (F.mse_loss(h, target) + spectral) / 6
                loss = loss + .01 * checkpoint(model, cond, target, None, use_reentrant=False).square().mean()
                self.assertTrue(torch.isfinite(loss).item())
                loss.backward()
                gradients = [parameter.grad for parameter in model.parameters() if parameter.grad is not None]
                self.assertTrue(gradients)
                self.assertTrue(all(torch.isfinite(gradient).all().item() for gradient in gradients))

    def test_atomic_resume_restores_optimizer_scheduler_and_cpu_rng(self):
        random.seed(12)
        np.random.seed(12)
        torch.manual_seed(12)
        rng = np.random.default_rng(23)
        model = torch.nn.Sequential(torch.nn.Linear(4, 8), torch.nn.Dropout(.25), torch.nn.Linear(8, 1))
        optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, 10)

        def update():
            model.train()
            x = torch.randn(3, 4) + float(rng.normal())
            target = torch.from_numpy(np.random.normal(size=(3, 1))).float() * random.random()
            loss = F.mse_loss(model(x), target)
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
            scheduler.step()
            return float(loss.detach())

        # This unit check intentionally never initializes CUDA or uses a GPU.
        with patch.object(torch.cuda, "is_available", return_value=False):
            update()
            state = {"model": copy.deepcopy(model.state_dict()),
                     "optimizer": copy.deepcopy(optimizer.state_dict()),
                     "scheduler": copy.deepcopy(scheduler.state_dict()), "rng": corrector.rng_state(rng)}
            with tempfile.TemporaryDirectory() as temporary:
                path = Path(temporary) / "checkpoint.pt"
                corrector.atomic_torch_save(path, state)
                self.assertEqual([item.name for item in Path(temporary).iterdir()], ["checkpoint.pt"])
                expected_loss = update()
                expected_state = copy.deepcopy(model.state_dict())
                expected_lr = scheduler.get_last_lr()
                state = torch.load(path, map_location="cpu", weights_only=False)
                model.load_state_dict(state["model"])
                optimizer.load_state_dict(state["optimizer"])
                scheduler.load_state_dict(state["scheduler"])
                corrector.restore_rng(state["rng"], rng)
                self.assertEqual(update(), expected_loss)
                self.assertEqual(scheduler.get_last_lr(), expected_lr)
                for key, value in model.state_dict().items():
                    self.assertTrue(torch.equal(value, expected_state[key]), key)

    def test_reserved_answer_guard_blocks_reads(self):
        # An audit hook cannot be removed, so install it in a separate process.
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)
            (path / "answers").mkdir()
            (path / "answers/target.txt").write_text("reserved")
            (path / "allowed.txt").write_text("training")
            program = (
                "from pathlib import Path\n"
                "from run_corrector import guard_reserved_answers\n"
                f"root=Path({str(path)!r})\n"
                "guard_reserved_answers()\n"
                "assert (root/'allowed.txt').read_text() == 'training'\n"
                "try: (root/'answers/target.txt').read_text()\n"
                "except PermissionError: print('blocked')\n"
                "else: raise AssertionError('Reserved answer was read')\n"
            )
            result = subprocess.run([sys.executable, "-c", program], cwd=corrector.ROOT,
                                    text=True, capture_output=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(result.stdout.strip(), "blocked")


if __name__ == "__main__":
    unittest.main()
