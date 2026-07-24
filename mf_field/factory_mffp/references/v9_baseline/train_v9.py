import argparse
import json
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader, Dataset, random_split

from model_v9 import MFTransolver_v9, param_count


def _npz_populate(self, dataset_dir, split) -> bool:
	"""Populate an IFCRawMultiStreamDataset from an npz_l dataset.

	Returns True if `dataset_dir` is npz_l (no fidelity_* dirs) and was loaded
	via the shared data_adapters shim, else False (caller reads ifc_raw dirs).
	Fields are 2-D (N, H, W); fidelity key = native resolution, HF = max.
	"""
	import sys
	sys.path.insert(0, str(Path(dataset_dir).parent.parent))
	from data_adapters.npz_compat import has_npz_layout, per_fidelity
	if not has_npz_layout(dataset_dir, split):
		return False
	res, x_by, y_by = per_fidelity(dataset_dir, split)
	self.fids = res
	self.hf_fid = max(res)
	self.lf_fids = [f for f in res if f != self.hf_fid]
	self.x_by_fid = x_by
	self.y_by_fid = y_by
	self.n_samples = x_by[self.hf_fid].shape[0]
	self.cond_dim = x_by[self.hf_fid].shape[1]
	self.sample_ids = [f"{Path(dataset_dir).name}_{split}_{i:04d}" for i in range(self.n_samples)]
	self.synthetic_lf_from_hf = False
	return True


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

		# npz_l datasets (no fidelity_* dirs, e.g. the 256² cavity): read per-
		# fidelity arrays via the shared data_adapters shim so this model runs
		# on them unchanged. Fidelity key = native resolution, HF = max.
		if _npz_populate(self, self.dataset_dir, split):
			return

		split_dir = self.dataset_dir / split
		fid_dirs = sorted(
			[p for p in split_dir.iterdir() if p.is_dir() and p.name.startswith("fidelity_")],
			key=lambda p: int(p.name.split("_")[1]),
		)
		if len(fid_dirs) < 2:
			raise ValueError(f"Need >=2 fidelities in {split_dir}, found {len(fid_dirs)}")

		self.fids = [int(p.name.split("_")[1]) for p in fid_dirs]
		self.hf_fid = max(self.fids)
		self.lf_fids = [f for f in self.fids if f != self.hf_fid]

		self.x_by_fid = {}
		self.y_by_fid = {}
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
		lf_fields = [self.y_by_fid[f][idx] for f in self.lf_fids]
		hf_field = self.y_by_fid[self.hf_fid][idx]
		return {
			"cond": cond,
			"lf_fields": lf_fields,
			"hf_field": hf_field,
			"sample_id": self.sample_ids[idx],
		}


def make_collate_fn(n_lf: int, n_hf: int):
	def collate_fn(batch):
		bsz = len(batch)
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


def hybrid_loss(pred: torch.Tensor, targets: torch.Tensor):
	diff = pred - targets
	mse = torch.mean(diff ** 2)
	diff_sq = torch.sum(diff ** 2, dim=1)
	true_sq = torch.sum(targets ** 2, dim=1)
	rel_l2 = torch.sqrt(diff_sq) / torch.clamp(torch.sqrt(true_sq), min=1e-4)
	return mse + torch.mean(rel_l2), mse


def get_prior_weight(epoch: int, init_w: float, final_w: float, decay_epochs: int) -> float:
	if epoch >= decay_epochs:
		return final_w
	t = epoch / max(decay_epochs, 1)
	return init_w + (final_w - init_w) * t


def main():
	parser = argparse.ArgumentParser(description="Train multi-stream MFTransolver_v9 on IFC raw datasets")
	parser.add_argument("--dataset_dir", type=str, required=True)
	parser.add_argument("--run_name", type=str, required=True)
	parser.add_argument("--epochs", type=int, default=200)
	parser.add_argument("--batch_size", type=int, default=4)
	parser.add_argument("--lr", type=float, default=3e-4)
	parser.add_argument("--n_lf", type=int, default=2048)
	parser.add_argument("--n_hf", type=int, default=4096)
	parser.add_argument("--hidden_dim", type=int, default=256)
	parser.add_argument("--n_slices", type=int, default=32)
	parser.add_argument("--num_heads", type=int, default=8)
	parser.add_argument("--encoder_layers", type=int, default=3)
	parser.add_argument("--residual_layers", type=int, default=3)
	parser.add_argument("--pos_enc_freqs", type=int, default=6)
	parser.add_argument("--rbf_gamma_init", type=float, default=1.0)
	parser.add_argument("--prior_weight_init", type=float, default=1.0)
	parser.add_argument("--prior_weight_final", type=float, default=0.1)
	parser.add_argument("--prior_decay_epochs", type=int, default=100)
	parser.add_argument("--gate_temp_init", type=float, default=2.5)
	parser.add_argument("--gate_temp_final", type=float, default=1.0)
	parser.add_argument("--gate_temp_anneal_epochs", type=int, default=200)
	parser.add_argument("--entropy_reg_init", type=float, default=1e-3)
	parser.add_argument("--entropy_reg_final", type=float, default=0.0)
	parser.add_argument("--entropy_reg_epochs", type=int, default=200)
	parser.add_argument("--gate_collapse_threshold", type=float, default=0.995)
	parser.add_argument("--gate_collapse_patience", type=int, default=10)
	parser.add_argument("--gate_collapse_warmup", type=int, default=50)
	parser.add_argument("--val_frac", type=float, default=0.2)
	args = parser.parse_args()

	dataset_dir = Path(args.dataset_dir)
	out_dir = Path(__file__).resolve().parent / "checkpoints" / args.run_name
	out_dir.mkdir(parents=True, exist_ok=True)

	best_path = out_dir / "film_best.pth"
	final_path = out_dir / "film_final.pth"
	cfg_path = out_dir / "train_config.json"
	loss_csv = out_dir / "loss_history.csv"

	device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
	use_amp = torch.cuda.is_available()
	scaler = torch.amp.GradScaler("cuda", enabled=use_amp)

	train_full = IFCRawMultiStreamDataset(dataset_dir, split="train")
	n_val = max(1, int(len(train_full) * args.val_frac))
	n_tr = max(1, len(train_full) - n_val)
	if n_tr + n_val > len(train_full):
		n_val = len(train_full) - n_tr
	tr_ds, val_ds = random_split(train_full, [n_tr, n_val], generator=torch.Generator().manual_seed(42))

	collate = make_collate_fn(args.n_lf, args.n_hf)
	tr_loader = DataLoader(tr_ds, batch_size=args.batch_size, shuffle=True, collate_fn=collate, num_workers=0)
	val_loader = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False, collate_fn=collate, num_workers=0)

	model = MFTransolver_v9(
		cond_dim=train_full.cond_dim,
		hidden_dim=args.hidden_dim,
		n_slices=args.n_slices,
		num_heads=args.num_heads,
		encoder_layers=args.encoder_layers,
		residual_layers=args.residual_layers,
		pos_enc_freqs=args.pos_enc_freqs,
		rbf_gamma_init=args.rbf_gamma_init,
		num_lf_streams=len(train_full.lf_fids),
	).to(device)

	trainable_p, total_p = param_count(model)
	print(f"Device: {device}")
	print(f"Dataset: {dataset_dir.name}")
	print(f"LF fids: {train_full.lf_fids} | HF fid: {train_full.hf_fid}")
	print(f"num_lf_streams={len(train_full.lf_fids)}")
	print(f"Params: {total_p:,} total ({trainable_p:,} trainable)")

	opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-5)
	scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=args.epochs, eta_min=1e-6)

	cfg = {
		"model_type": "MFTransolver_v9",
		"dataset_dir": str(dataset_dir),
		"dataset_name": dataset_dir.name,
		"run_name": args.run_name,
		"epochs": args.epochs,
		"batch_size": args.batch_size,
		"lr": args.lr,
		"n_lf": args.n_lf,
		"n_hf": args.n_hf,
		"lf_fids": train_full.lf_fids,
		"hf_fid": train_full.hf_fid,
		"num_lf_streams": len(train_full.lf_fids),
		"cond_dim": train_full.cond_dim,
		"model": {
			"cond_dim": train_full.cond_dim,
			"hidden_dim": args.hidden_dim,
			"n_slices": args.n_slices,
			"num_heads": args.num_heads,
			"encoder_layers": args.encoder_layers,
			"residual_layers": args.residual_layers,
			"pos_enc_freqs": args.pos_enc_freqs,
			"rbf_gamma_init": args.rbf_gamma_init,
			"num_lf_streams": len(train_full.lf_fids),
		},
	}
	json.dump(cfg, open(cfg_path, "w"), indent=2)

	best_val = float("inf")
	history = []
	t0 = time.time()
	collapse_streak = 0

	def linear_schedule(epoch_idx: int, start: float, end: float, anneal_epochs: int) -> float:
		if epoch_idx >= anneal_epochs:
			return end
		t = epoch_idx / max(anneal_epochs, 1)
		return start + (end - start) * t

	for epoch in range(1, args.epochs + 1):
		lam_prior = get_prior_weight(
			epoch, args.prior_weight_init, args.prior_weight_final, args.prior_decay_epochs
		)
		gate_temp = linear_schedule(epoch, args.gate_temp_init, args.gate_temp_final, args.gate_temp_anneal_epochs)
		entropy_reg = linear_schedule(epoch, args.entropy_reg_init, args.entropy_reg_final, args.entropy_reg_epochs)

		model.train()
		tr_mse_sum, tr_cnt = 0.0, 0
		alpha_sum = np.zeros((len(train_full.lf_fids) + 1,), dtype=np.float64)
		entropy_sum = 0.0

		for list_of_lf_toks, hf_tok, targets, _ in tr_loader:
			list_of_lf_toks = [t.to(device) for t in list_of_lf_toks]
			hf_tok = hf_tok.to(device)
			targets = targets.to(device)

			opt.zero_grad(set_to_none=True)
			with torch.amp.autocast("cuda", enabled=use_amp):
				comps = model(list_of_lf_toks, hf_tok, gate_temperature=gate_temp, return_components=True)
				pred = comps["pred"]
				prior = comps["prior"]
				alpha = comps["alpha"]

				loss_main, mse_t = hybrid_loss(pred, targets)
				loss_prior, _ = hybrid_loss(prior, targets)
				entropy = -(alpha * torch.log(alpha.clamp_min(1e-8))).sum(dim=-1).mean()
				loss = loss_main + lam_prior * loss_prior - entropy_reg * entropy

			scaler.scale(loss).backward()
			scaler.unscale_(opt)
			torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
			scaler.step(opt)
			scaler.update()

			bsz = hf_tok.size(0)
			tr_mse_sum += mse_t.item() * bsz
			tr_cnt += bsz
			alpha_sum += alpha.mean(dim=(0, 1)).detach().cpu().numpy() * bsz
			entropy_sum += entropy.item() * bsz

		scheduler.step()
		train_mse = tr_mse_sum / max(tr_cnt, 1)
		alpha_mean_vec = alpha_sum / max(tr_cnt, 1)
		alpha_entropy = entropy_sum / max(tr_cnt, 1)

		model.eval()
		val_sum, val_cnt = 0.0, 0
		with torch.no_grad(), torch.amp.autocast("cuda", enabled=use_amp):
			for list_of_lf_toks, hf_tok, targets, _ in val_loader:
				list_of_lf_toks = [t.to(device) for t in list_of_lf_toks]
				hf_tok = hf_tok.to(device)
				targets = targets.to(device)
				pred = model(list_of_lf_toks, hf_tok, gate_temperature=gate_temp)
				_, vm = hybrid_loss(pred, targets)
				bsz = hf_tok.size(0)
				val_sum += vm.item() * bsz
				val_cnt += bsz

		val_mse = val_sum / max(val_cnt, 1)
		gamma_val = torch.exp(model.log_gamma).item()

		row = {
			"epoch": epoch,
			"train_mse": train_mse,
			"val_mse": val_mse,
			"lambda_prior": lam_prior,
			"gate_temperature": gate_temp,
			"entropy_reg": entropy_reg,
			"alpha_entropy": alpha_entropy,
			"gamma": gamma_val,
			"alpha_self_mean": float(alpha_mean_vec[0]),
		}
		for i in range(len(train_full.lf_fids)):
			row[f"alpha_lf{i+1}_mean"] = float(alpha_mean_vec[i + 1])
		history.append(row)

		if val_mse < best_val:
			best_val = val_mse
			torch.save(model.state_dict(), best_path)
			print(
				f"[{epoch:04d}] train={train_mse:.4e} val={val_mse:.4e} "
				f"tau={gate_temp:.3f} H={alpha_entropy:.3f} gamma={gamma_val:.4f} "
				f"alpha_self={alpha_mean_vec[0]:.4f}  <-- BEST"
			)
		elif epoch % 20 == 0:
			lf_msg = " ".join([f"a_lf{i+1}={alpha_mean_vec[i+1]:.4f}" for i in range(len(train_full.lf_fids))])
			print(
				f"[{epoch:04d}] train={train_mse:.4e} val={val_mse:.4e} "
				f"tau={gate_temp:.3f} H={alpha_entropy:.3f} gamma={gamma_val:.4f} "
				f"a_self={alpha_mean_vec[0]:.4f} {lf_msg}"
			)

		if epoch >= args.gate_collapse_warmup and float(alpha_mean_vec.max()) >= args.gate_collapse_threshold:
			collapse_streak += 1
		else:
			collapse_streak = 0

		if collapse_streak >= args.gate_collapse_patience:
			print(
				f"[EARLY-STOP] Gate collapse detected: max alpha mean >= {args.gate_collapse_threshold} "
				f"for {collapse_streak} consecutive epochs (epoch={epoch})."
			)
			break

	torch.save(model.state_dict(), final_path)
	pd.DataFrame(history).to_csv(loss_csv, index=False)

	dt = time.time() - t0
	print(f"Done in {dt/60:.1f} min")
	print(f"Best val MSE: {best_val:.4e}")
	print(f"Best weights: {best_path}")
	print(f"Final weights: {final_path}")


if __name__ == "__main__":
	main()
