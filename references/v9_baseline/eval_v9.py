import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset

from model_v9 import MFTransolver_v9


def field_to_points(field: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
	if field.ndim == 2:
		field = field[None, ...]
	if field.ndim != 3:
		raise ValueError(f"Expected 2D or 3D field, got shape {field.shape}")

	c, h, w = field.shape
	xs = np.linspace(-1.0, 1.0, w, dtype=np.float32)
	zs = np.linspace(-1.0, 1.0, h, dtype=np.float32)
	xx, zz = np.meshgrid(xs, zs)
	y_levels = np.zeros((c,), dtype=np.float32) if c == 1 else np.linspace(-1.0, 1.0, c, dtype=np.float32)

	coords_list, vals_list = [], []
	for i in range(c):
		yy = np.full_like(xx, y_levels[i], dtype=np.float32)
		coords = np.stack([xx, yy, zz], axis=-1).reshape(-1, 3)
		vals = field[i].reshape(-1).astype(np.float32)
		coords_list.append(coords)
		vals_list.append(vals)

	return np.concatenate(coords_list, axis=0), np.concatenate(vals_list, axis=0)


def sample_points(coords: np.ndarray, values: np.ndarray, n_points: int) -> tuple[np.ndarray, np.ndarray]:
	n_total = coords.shape[0]
	if n_points <= 0 or n_points >= n_total:
		return coords, values
	replace = n_total < n_points
	idx = np.random.choice(n_total, n_points, replace=replace)
	return coords[idx], values[idx]


class IFCRawMultiStreamDataset(Dataset):
	def __init__(self, dataset_dir: Path, split: str):
		self.dataset_dir = Path(dataset_dir)
		self.split = split
		self.synthetic_lf_from_hf = False

		split_dir = self.dataset_dir / split
		fid_dirs = sorted(
			[p for p in split_dir.iterdir() if p.is_dir() and p.name.startswith("fidelity_")],
			key=lambda p: int(p.name.split("_")[1]),
		)
		if len(fid_dirs) < 2 and split == "test":
			train_dir = self.dataset_dir / "train"
			train_fid_dirs = sorted(
				[p for p in train_dir.iterdir() if p.is_dir() and p.name.startswith("fidelity_")],
				key=lambda p: int(p.name.split("_")[1]),
			)
			if len(train_fid_dirs) < 2:
				raise ValueError(
					f"Need >=2 train fidelities in {train_dir} to synthesize LF for test eval, found {len(train_fid_dirs)}"
				)
			self.fids = [int(p.name.split("_")[1]) for p in train_fid_dirs]
			self.hf_fid = max(self.fids)
			self.lf_fids = [f for f in self.fids if f != self.hf_fid]
			self.synthetic_lf_from_hf = True
		else:
			if len(fid_dirs) < 2:
				raise ValueError(f"Need >=2 fidelities in {split_dir}, found {len(fid_dirs)}")
			self.fids = [int(p.name.split("_")[1]) for p in fid_dirs]
			self.hf_fid = max(self.fids)
			self.lf_fids = [f for f in self.fids if f != self.hf_fid]

		self.x_by_fid = {}
		self.y_by_fid = {}
		if self.synthetic_lf_from_hf:
			hf_path = split_dir / f"fidelity_{self.hf_fid}"
			self.x_by_fid[self.hf_fid] = np.load(hf_path / "Xs.npy").astype(np.float32)
			self.y_by_fid[self.hf_fid] = np.load(hf_path / "ys.npy").astype(np.float32)
		else:
			for f in self.fids:
				p = split_dir / f"fidelity_{f}"
				self.x_by_fid[f] = np.load(p / "Xs.npy").astype(np.float32)
				self.y_by_fid[f] = np.load(p / "ys.npy").astype(np.float32)

		self.n_samples = self.x_by_fid[self.hf_fid].shape[0]
		self.cond_dim = self.x_by_fid[self.hf_fid].shape[1]
		self.sample_ids = [f"{self.dataset_dir.name}_{split}_{i:04d}" for i in range(self.n_samples)]

	def __len__(self):
		return self.n_samples

	def __getitem__(self, idx):
		cond = self.x_by_fid[self.hf_fid][idx]
		hf_field = self.y_by_fid[self.hf_fid][idx]
		if self.synthetic_lf_from_hf:
			lf_fields = [downsample_field_to_fidelity(hf_field, f) for f in self.lf_fids]
		else:
			lf_fields = [self.y_by_fid[f][idx] for f in self.lf_fids]
		return {
			"cond": cond,
			"lf_fields": lf_fields,
			"hf_field": hf_field,
			"sample_id": self.sample_ids[idx],
		}


def downsample_field_to_fidelity(field: np.ndarray, target_fid: int) -> np.ndarray:
	if field.ndim == 2:
		x = torch.from_numpy(field[None, None, ...]).float()
		y = F.interpolate(x, size=(target_fid, target_fid), mode="bilinear", align_corners=False)
		return y[0, 0].numpy().astype(np.float32)
	if field.ndim == 3:
		x = torch.from_numpy(field[None, ...]).float()
		y = F.interpolate(x, size=(target_fid, target_fid), mode="bilinear", align_corners=False)
		return y[0].numpy().astype(np.float32)
	raise ValueError(f"Unsupported field shape for downsample: {field.shape}")


def make_collate_fn(n_lf: int, n_hf: int):
	def collate_fn(batch):
		n_streams = len(batch[0]["lf_fields"])

		lf_stream_batches = [[] for _ in range(n_streams)]
		hf_batch, tgt_batch, ids = [], [], []

		for s in batch:
			cond = s["cond"].astype(np.float32)

			hf_coords, hf_vals = field_to_points(s["hf_field"])
			hf_coords, hf_vals = sample_points(hf_coords, hf_vals, n_hf)
			cond_hf = np.tile(cond, (hf_coords.shape[0], 1))
			hf_tok = np.concatenate([hf_coords, cond_hf], axis=-1)

			for i, lf_field in enumerate(s["lf_fields"]):
				lf_coords, lf_vals = field_to_points(lf_field)
				lf_coords, lf_vals = sample_points(lf_coords, lf_vals, n_lf)
				cond_lf = np.tile(cond, (lf_coords.shape[0], 1))
				lf_tok = np.concatenate([lf_coords, cond_lf, lf_vals[:, None]], axis=-1)
				lf_stream_batches[i].append(lf_tok)

			hf_batch.append(hf_tok)
			tgt_batch.append(hf_vals[:, None])
			ids.append(s["sample_id"])

		list_of_lf_toks = [torch.from_numpy(np.stack(stream, axis=0)).float() for stream in lf_stream_batches]
		hf_toks = torch.from_numpy(np.stack(hf_batch, axis=0)).float()
		tgts = torch.from_numpy(np.stack(tgt_batch, axis=0)).float()

		return list_of_lf_toks, hf_toks, tgts, ids

	return collate_fn


def main():
	parser = argparse.ArgumentParser(description="Evaluate multi-stream MFTransolver_v9 on IFC raw datasets")
	parser.add_argument("--run_name", type=str, required=True)
	parser.add_argument("--weights", type=str, default="film_best.pth")
	parser.add_argument("--split", type=str, default="test", choices=["train", "test"])
	parser.add_argument("--n_lf", type=int, default=2048)
	parser.add_argument("--n_hf", type=int, default=4096)
	parser.add_argument("--results_dir", type=str, default=None)
	args = parser.parse_args()

	here = Path(__file__).resolve().parent
	ckpt_dir = here / "checkpoints" / args.run_name
	cfg = json.load(open(ckpt_dir / "train_config.json"))
	dataset_dir = Path(cfg["dataset_dir"])

	out_dir = Path(args.results_dir) if args.results_dir else ckpt_dir
	out_dir.mkdir(parents=True, exist_ok=True)
	alpha_dir = out_dir / "alpha_maps"
	alpha_dir.mkdir(parents=True, exist_ok=True)

	ds = IFCRawMultiStreamDataset(dataset_dir, split=args.split)
	loader = DataLoader(ds, batch_size=1, shuffle=False, collate_fn=make_collate_fn(args.n_lf, args.n_hf), num_workers=0)

	m = cfg["model"]
	model = MFTransolver_v9(
		cond_dim=m["cond_dim"],
		hidden_dim=m["hidden_dim"],
		n_slices=m["n_slices"],
		num_heads=m["num_heads"],
		encoder_layers=m["encoder_layers"],
		residual_layers=m["residual_layers"],
		pos_enc_freqs=m["pos_enc_freqs"],
		rbf_gamma_init=m.get("rbf_gamma_init", 1.0),
		num_lf_streams=m["num_lf_streams"],
	)

	device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
	model.to(device)
	model.load_state_dict(torch.load(ckpt_dir / args.weights, map_location=device, weights_only=True))
	model.eval()

	rows = []
	with torch.no_grad():
		for i, (list_of_lf_toks, hf_tok, targets, sample_ids) in enumerate(loader, start=1):
			list_of_lf_toks = [t.to(device) for t in list_of_lf_toks]
			hf_tok = hf_tok.to(device)
			targets = targets.to(device)

			comps = model(list_of_lf_toks, hf_tok, return_components=True)
			pred = comps["pred"]
			alpha = comps["alpha"]

			diff = pred - targets
			mae = torch.mean(torch.abs(diff)).item()
			mse = torch.mean(diff ** 2).item()

			diff_sq = torch.sum(diff ** 2, dim=1)
			true_sq = torch.sum(targets ** 2, dim=1)
			rel_l2 = torch.mean(torch.sqrt(diff_sq) / torch.clamp(torch.sqrt(true_sq), min=1e-12)).item()

			alpha_mean = alpha.mean(dim=(0, 1)).detach().cpu().numpy()

			sid = sample_ids[0]
			np.savez_compressed(
				alpha_dir / f"alpha_{sid}.npz",
				alpha=alpha.squeeze(0).detach().cpu().numpy().astype(np.float32),
				pred=pred.squeeze(0).squeeze(-1).detach().cpu().numpy().astype(np.float32),
				target=targets.squeeze(0).squeeze(-1).detach().cpu().numpy().astype(np.float32),
			)

			row = {
				"sample_id": sid,
				"mae": mae,
				"mse": mse,
				"rel_l2": rel_l2,
				"alpha_self_mean": float(alpha_mean[0]),
			}
			for j in range(len(ds.lf_fids)):
				row[f"alpha_lf{j+1}_mean"] = float(alpha_mean[j + 1])
			rows.append(row)
			print(f"[{i:03d}/{len(ds):03d}] {sid} rel_l2={rel_l2:.4f}", end="\r", flush=True)

	print()
	df = pd.DataFrame(rows)
	summary = df.drop(columns=["sample_id"]).mean()

	weights_stem = Path(args.weights).stem
	per_csv = out_dir / f"eval_{args.split}_{weights_stem}_per_design.csv"
	summary_csv = out_dir / f"eval_{args.split}_{weights_stem}_summary.csv"
	df.to_csv(per_csv, index=False)
	summary.to_frame("value").to_csv(summary_csv)

	print("=" * 72)
	print(f"Dataset: {dataset_dir.name} | split={args.split} | weights={args.weights}")
	print(f"MAE={summary['mae']:.6f} MSE={summary['mse']:.6f} RelL2={summary['rel_l2']:.6f}")
	print(f"alpha_self_mean={summary['alpha_self_mean']:.6f}")
	for j in range(len(ds.lf_fids)):
		print(f"alpha_lf{j+1}_mean={summary[f'alpha_lf{j+1}_mean']:.6f}")
	print("=" * 72)
	print(f"Per-design: {per_csv}")
	print(f"Summary:    {summary_csv}")
	print(f"Alpha maps: {alpha_dir}")


if __name__ == "__main__":
	main()
