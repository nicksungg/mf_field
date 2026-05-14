from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import Dataset


class StandardScaler:
	def __init__(self, mean: float, std: float):
		self.mean = float(mean)
		self.std = float(std) if float(std) > 0 else 1.0

	def transform(self, data: np.ndarray) -> np.ndarray:
		return (data - self.mean) / self.std

	def inverse_transform(self, data: np.ndarray) -> np.ndarray:
		return (data * self.std) + self.mean


@dataclass
class SplitData:
	xs: list[np.ndarray]
	ys: list[np.ndarray]
	x_scaler: StandardScaler
	y_scalers: list[StandardScaler]
	grid_sides: list[int]


def _infer_side(n_outputs: int) -> int:
	side = int(round(math.sqrt(n_outputs)))
	if side * side != n_outputs:
		raise ValueError(f"Expected square flattened field, got output dimension {n_outputs}")
	return side


def field_to_points(field: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
	if field.ndim != 1:
		raise ValueError(f"Expected flattened 1D field, got shape {field.shape}")
	side = _infer_side(field.shape[0])
	vals_2d = field.reshape(side, side).astype(np.float32)
	xs = np.linspace(-1.0, 1.0, side, dtype=np.float32)
	zs = np.linspace(-1.0, 1.0, side, dtype=np.float32)
	xx, zz = np.meshgrid(xs, zs)
	yy = np.zeros_like(xx, dtype=np.float32)
	coords = np.stack([xx, yy, zz], axis=-1).reshape(-1, 3)
	vals = vals_2d.reshape(-1)
	return coords, vals


def sample_points(coords: np.ndarray, values: np.ndarray, n_points: int) -> tuple[np.ndarray, np.ndarray]:
	n_total = coords.shape[0]
	if n_points <= 0 or n_points >= n_total:
		return coords, values
	idx = np.random.choice(n_total, n_points, replace=False)
	return coords[idx], values[idx]


def load_mfrnp_splits(data_path: str | Path, levels: int, valid_ratio: float = 0.1) -> dict[str, SplitData]:
	data_path = Path(data_path)
	train_xs_raw, train_ys_raw = [], []
	test_xs_raw, test_ys_raw = [], []
	grid_sides = []

	for level in range(1, levels + 1):
		train_npz = np.load(data_path / f"train_l{level}.npz")
		test_npz = np.load(data_path / f"test_l{level}.npz")
		train_x = train_npz["x"].astype(np.float32)
		train_y = train_npz["y"].astype(np.float32)
		test_x = test_npz["x"].astype(np.float32)
		test_y = test_npz["y"].astype(np.float32)
		train_xs_raw.append(train_x)
		train_ys_raw.append(train_y)
		test_xs_raw.append(test_x)
		test_ys_raw.append(test_y)
		grid_sides.append(_infer_side(train_y.shape[1]))

	train_size = int((1.0 - valid_ratio) * len(train_xs_raw[0]))
	train_size = max(1, min(train_size, len(train_xs_raw[0]) - 1))

	x_scaler = StandardScaler(np.mean(train_xs_raw[0][:train_size]), np.std(train_xs_raw[0][:train_size]))
	y_scalers = [
		StandardScaler(np.mean(train_y[:train_size]), np.std(train_y[:train_size]))
		for train_y in train_ys_raw
	]

	def transform_split(xs_raw: list[np.ndarray], ys_raw: list[np.ndarray], split_name: str) -> SplitData:
		if split_name == "train":
			xs_part = [x[:train_size] for x in xs_raw]
			ys_part = [y[:train_size] for y in ys_raw]
		elif split_name == "valid":
			xs_part = [x[train_size:] for x in xs_raw]
			ys_part = [y[train_size:] for y in ys_raw]
		else:
			xs_part = xs_raw
			ys_part = ys_raw

		xs_scaled = [x_scaler.transform(x).astype(np.float32) for x in xs_part]
		ys_scaled = [s.transform(y).astype(np.float32) for s, y in zip(y_scalers, ys_part)]
		return SplitData(xs=xs_scaled, ys=ys_scaled, x_scaler=x_scaler, y_scalers=y_scalers, grid_sides=grid_sides)

	return {
		"train": transform_split(train_xs_raw, train_ys_raw, "train"),
		"valid": transform_split(train_xs_raw, train_ys_raw, "valid"),
		"test": transform_split(test_xs_raw, test_ys_raw, "test"),
	}


class MFRNPMultiStreamDataset(Dataset):
	def __init__(self, data_path: str | Path, levels: int, split: str = "train", valid_ratio: float = 0.1):
		if levels < 2:
			raise ValueError("levels must be at least 2")
		if split not in {"train", "valid", "test"}:
			raise ValueError(f"Unsupported split: {split}")

		self.data_path = Path(data_path)
		self.levels = levels
		self.split = split
		self.splits = load_mfrnp_splits(self.data_path, levels=levels, valid_ratio=valid_ratio)
		self.data = self.splits[split]

		self.cond_dim = self.data.xs[-1].shape[1]
		self.lf_levels = list(range(1, levels))
		self.hf_level = levels
		self.n_samples = self.data.xs[-1].shape[0]
		self.hf_y_std = self.data.y_scalers[-1].std
		self.sample_ids = [f"{self.data_path.name}_{split}_{i:04d}" for i in range(self.n_samples)]

	def __len__(self) -> int:
		return self.n_samples

	def __getitem__(self, idx: int) -> dict:
		cond = self.data.xs[-1][idx]
		lf_fields = [self.data.ys[level - 1][idx] for level in self.lf_levels]
		hf_field = self.data.ys[self.hf_level - 1][idx]
		return {
			"cond": cond,
			"lf_fields": lf_fields,
			"hf_field": hf_field,
			"sample_id": self.sample_ids[idx],
		}


def make_collate_fn(n_lf: int, n_hf: int):
	def collate_fn(batch):
		n_streams = len(batch[0]["lf_fields"])
		lf_stream_batches = [[] for _ in range(n_streams)]
		hf_batch, tgt_batch, ids = [], [], []

		for sample in batch:
			cond = sample["cond"].astype(np.float32)
			hf_coords, hf_vals = field_to_points(sample["hf_field"])
			hf_coords, hf_vals = sample_points(hf_coords, hf_vals, n_hf)
			cond_hf = np.tile(cond, (hf_coords.shape[0], 1))
			hf_tok = np.concatenate([hf_coords, cond_hf], axis=-1)

			for i, lf_field in enumerate(sample["lf_fields"]):
				lf_coords, lf_vals = field_to_points(lf_field)
				lf_coords, lf_vals = sample_points(lf_coords, lf_vals, n_lf)
				cond_lf = np.tile(cond, (lf_coords.shape[0], 1))
				lf_tok = np.concatenate([lf_coords, cond_lf, lf_vals[:, None]], axis=-1)
				lf_stream_batches[i].append(lf_tok)

			hf_batch.append(hf_tok)
			tgt_batch.append(hf_vals[:, None])
			ids.append(sample["sample_id"])

		list_of_lf_toks = [torch.from_numpy(np.stack(stream, axis=0)).float() for stream in lf_stream_batches]
		hf_toks = torch.from_numpy(np.stack(hf_batch, axis=0)).float()
		tgts = torch.from_numpy(np.stack(tgt_batch, axis=0)).float()
		return list_of_lf_toks, hf_toks, tgts, ids

	return collate_fn


__all__ = [
	"MFRNPMultiStreamDataset",
	"StandardScaler",
	"field_to_points",
	"load_mfrnp_splits",
	"make_collate_fn",
	"sample_points",
]