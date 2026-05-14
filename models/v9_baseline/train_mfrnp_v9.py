import argparse
import json
import os
import random
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader

from mfrnp_npz_data import MFRNPMultiStreamDataset, make_collate_fn
from model_v9 import MFTransolver_v9, param_count


def hybrid_loss(pred: torch.Tensor, targets: torch.Tensor):
	diff = pred - targets
	mse = torch.mean(diff ** 2)
	diff_sq = torch.sum(diff ** 2, dim=1)
	true_sq = torch.sum(targets ** 2, dim=1)
	rel_l2 = torch.sqrt(diff_sq) / torch.clamp(torch.sqrt(true_sq), min=1e-12)
	rmse = torch.sqrt(torch.mean(diff ** 2, dim=1))
	return mse + torch.mean(rel_l2), mse, torch.mean(rmse), torch.mean(rel_l2)


def get_prior_weight(epoch: int, init_w: float, final_w: float, decay_epochs: int) -> float:
	if epoch >= decay_epochs:
		return final_w
	t = epoch / max(decay_epochs, 1)
	return init_w + (final_w - init_w) * t


def linear_schedule(epoch_idx: int, start: float, end: float, anneal_epochs: int) -> float:
	if epoch_idx >= anneal_epochs:
		return end
	t = epoch_idx / max(anneal_epochs, 1)
	return start + (end - start) * t


def set_seed(seed: int):
	random.seed(seed)
	np.random.seed(seed)
	torch.manual_seed(seed)
	torch.cuda.manual_seed_all(seed)


def main():
	parser = argparse.ArgumentParser(description="Train multi-stream MFTransolver_v9 on MFRNP NPZ datasets")
	parser.add_argument("--data_path", type=str, required=True)
	parser.add_argument("--levels", type=int, required=True)
	parser.add_argument("--run_name", type=str, required=True)
	parser.add_argument("--epochs", type=int, default=200)
	parser.add_argument("--batch_size", type=int, default=4)
	parser.add_argument("--lr", type=float, default=3e-4)
	parser.add_argument("--n_lf", type=int, default=2048)
	parser.add_argument("--n_hf", type=int, default=4096)
	parser.add_argument("--val_n_lf", type=int, default=0)
	parser.add_argument("--val_n_hf", type=int, default=0)
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
	parser.add_argument("--gate_temp_init", type=float, default=3.0)
	parser.add_argument("--gate_temp_final", type=float, default=1.0)
	parser.add_argument("--gate_temp_anneal_epochs", type=int, default=200)
	parser.add_argument("--entropy_reg_init", type=float, default=3e-3)
	parser.add_argument("--entropy_reg_final", type=float, default=0.0)
	parser.add_argument("--entropy_reg_epochs", type=int, default=200)
	parser.add_argument("--gate_collapse_threshold", type=float, default=0.995)
	parser.add_argument("--gate_collapse_patience", type=int, default=10)
	parser.add_argument("--gate_collapse_warmup", type=int, default=50)
	parser.add_argument("--valid_ratio", type=float, default=0.1)
	parser.add_argument("--seed", type=int, default=1)
	args = parser.parse_args()

	set_seed(args.seed)

	data_path = Path(args.data_path)
	out_dir = Path(__file__).resolve().parent / "checkpoints" / args.run_name
	out_dir.mkdir(parents=True, exist_ok=True)

	best_path = out_dir / "film_best.pth"
	final_path = out_dir / "film_final.pth"
	cfg_path = out_dir / "train_config.json"
	loss_csv = out_dir / "loss_history.csv"

	device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
	use_amp = torch.cuda.is_available()
	scaler = torch.amp.GradScaler("cuda", enabled=use_amp)

	train_ds = MFRNPMultiStreamDataset(data_path, levels=args.levels, split="train", valid_ratio=args.valid_ratio)
	val_ds = MFRNPMultiStreamDataset(data_path, levels=args.levels, split="valid", valid_ratio=args.valid_ratio)

	tr_loader = DataLoader(
		train_ds,
		batch_size=args.batch_size,
		shuffle=True,
		collate_fn=make_collate_fn(args.n_lf, args.n_hf),
		num_workers=0,
	)
	val_loader = DataLoader(
		val_ds,
		batch_size=1,
		shuffle=False,
		collate_fn=make_collate_fn(args.val_n_lf, args.val_n_hf),
		num_workers=0,
	)

	model = MFTransolver_v9(
		cond_dim=train_ds.cond_dim,
		hidden_dim=args.hidden_dim,
		n_slices=args.n_slices,
		num_heads=args.num_heads,
		encoder_layers=args.encoder_layers,
		residual_layers=args.residual_layers,
		pos_enc_freqs=args.pos_enc_freqs,
		rbf_gamma_init=args.rbf_gamma_init,
		num_lf_streams=len(train_ds.lf_levels),
	).to(device)

	trainable_p, total_p = param_count(model)
	print(f"Device: {device}")
	print(f"Dataset: {data_path}")
	print(f"Levels: {train_ds.lf_levels} -> {train_ds.hf_level}")
	print(f"Params: {total_p:,} total ({trainable_p:,} trainable)")

	opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-5)
	scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=args.epochs, eta_min=1e-6)

	cfg = {
		"model_type": "MFTransolver_v9",
		"data_path": str(data_path),
		"dataset_name": data_path.name,
		"run_name": args.run_name,
		"epochs": args.epochs,
		"batch_size": args.batch_size,
		"lr": args.lr,
		"n_lf": args.n_lf,
		"n_hf": args.n_hf,
		"val_n_lf": args.val_n_lf,
		"val_n_hf": args.val_n_hf,
		"levels": args.levels,
		"valid_ratio": args.valid_ratio,
		"seed": args.seed,
		"hf_y_std": train_ds.hf_y_std,
		"lf_levels": train_ds.lf_levels,
		"hf_level": train_ds.hf_level,
		"num_lf_streams": len(train_ds.lf_levels),
		"cond_dim": train_ds.cond_dim,
		"model": {
			"cond_dim": train_ds.cond_dim,
			"hidden_dim": args.hidden_dim,
			"n_slices": args.n_slices,
			"num_heads": args.num_heads,
			"encoder_layers": args.encoder_layers,
			"residual_layers": args.residual_layers,
			"pos_enc_freqs": args.pos_enc_freqs,
			"rbf_gamma_init": args.rbf_gamma_init,
			"num_lf_streams": len(train_ds.lf_levels),
		},
	}
	json.dump(cfg, open(cfg_path, "w"), indent=2)

	best_val_nrmse = float("inf")
	history = []
	t0 = time.time()
	collapse_streak = 0

	for epoch in range(1, args.epochs + 1):
		lam_prior = get_prior_weight(epoch, args.prior_weight_init, args.prior_weight_final, args.prior_decay_epochs)
		gate_temp = linear_schedule(epoch, args.gate_temp_init, args.gate_temp_final, args.gate_temp_anneal_epochs)
		entropy_reg = linear_schedule(epoch, args.entropy_reg_init, args.entropy_reg_final, args.entropy_reg_epochs)

		model.train()
		tr_mse_sum, tr_nrmse_sum, tr_rel_sum, tr_cnt = 0.0, 0.0, 0.0, 0
		alpha_sum = np.zeros((len(train_ds.lf_levels) + 1,), dtype=np.float64)
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

				loss_main, mse_t, nrmse_t, rel_t = hybrid_loss(pred, targets)
				loss_prior, _, _, _ = hybrid_loss(prior, targets)
				entropy = -(alpha * torch.log(alpha.clamp_min(1e-8))).sum(dim=-1).mean()
				loss = loss_main + lam_prior * loss_prior - entropy_reg * entropy

			scaler.scale(loss).backward()
			scaler.unscale_(opt)
			torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
			scaler.step(opt)
			scaler.update()

			bsz = hf_tok.size(0)
			tr_mse_sum += mse_t.item() * bsz
			tr_nrmse_sum += nrmse_t.item() * bsz
			tr_rel_sum += rel_t.item() * bsz
			tr_cnt += bsz
			alpha_sum += alpha.mean(dim=(0, 1)).detach().cpu().numpy() * bsz
			entropy_sum += entropy.item() * bsz

		scheduler.step()
		train_mse = tr_mse_sum / max(tr_cnt, 1)
		train_nrmse = tr_nrmse_sum / max(tr_cnt, 1)
		train_rel_l2 = tr_rel_sum / max(tr_cnt, 1)
		alpha_mean_vec = alpha_sum / max(tr_cnt, 1)
		alpha_entropy = entropy_sum / max(tr_cnt, 1)

		model.eval()
		val_mse_sum, val_nrmse_sum, val_rel_sum, val_cnt = 0.0, 0.0, 0.0, 0
		with torch.no_grad(), torch.amp.autocast("cuda", enabled=use_amp):
			for list_of_lf_toks, hf_tok, targets, _ in val_loader:
				list_of_lf_toks = [t.to(device) for t in list_of_lf_toks]
				hf_tok = hf_tok.to(device)
				targets = targets.to(device)
				pred = model(list_of_lf_toks, hf_tok, gate_temperature=gate_temp)
				_, vm, vn, vr = hybrid_loss(pred, targets)
				bsz = hf_tok.size(0)
				val_mse_sum += vm.item() * bsz
				val_nrmse_sum += vn.item() * bsz
				val_rel_sum += vr.item() * bsz
				val_cnt += bsz

		val_mse = val_mse_sum / max(val_cnt, 1)
		val_nrmse = val_nrmse_sum / max(val_cnt, 1)
		val_rel_l2 = val_rel_sum / max(val_cnt, 1)
		gamma_val = torch.exp(model.log_gamma).item()

		row = {
			"epoch": epoch,
			"train_mse": train_mse,
			"train_nrmse": train_nrmse,
			"train_rel_l2": train_rel_l2,
			"val_mse": val_mse,
			"val_nrmse": val_nrmse,
			"val_rel_l2": val_rel_l2,
			"lambda_prior": lam_prior,
			"gate_temperature": gate_temp,
			"entropy_reg": entropy_reg,
			"alpha_entropy": alpha_entropy,
			"gamma": gamma_val,
			"alpha_self_mean": float(alpha_mean_vec[0]),
		}
		for j in range(len(train_ds.lf_levels)):
			row[f"alpha_lf{j+1}_mean"] = float(alpha_mean_vec[j + 1])
		history.append(row)
		pd.DataFrame(history).to_csv(loss_csv, index=False)

		if val_nrmse < best_val_nrmse:
			best_val_nrmse = val_nrmse
			torch.save(model.state_dict(), best_path)
			best_tag = "  <-- BEST"
		else:
			best_tag = ""

		max_alpha = float(alpha_mean_vec.max())
		if epoch >= args.gate_collapse_warmup and max_alpha >= args.gate_collapse_threshold:
			collapse_streak += 1
		else:
			collapse_streak = 0

		if epoch == 1 or epoch % 10 == 0 or best_tag:
			msg = (
				f"[{epoch:04d}] train_mse={train_mse:.4e} train_nrmse={train_nrmse:.4e} "
				f"val_nrmse={val_nrmse:.4e} val_rel={val_rel_l2:.4e} tau={gate_temp:.3f} "
				f"H={alpha_entropy:.3f} gamma={gamma_val:.4f} alpha_self={alpha_mean_vec[0]:.4f}{best_tag}"
			)
			print(msg)

		if collapse_streak >= args.gate_collapse_patience:
			print(
				f"Stopping early: gate collapse detected for {collapse_streak} consecutive epochs "
				f"(threshold={args.gate_collapse_threshold:.3f})."
			)
			break

	torch.save(model.state_dict(), final_path)
	print(f"Done in {(time.time() - t0) / 60.0:.1f} min")
	print(f"Best val NRMSE: {best_val_nrmse:.6e}")
	print(f"Best weights: {best_path}")
	print(f"Final weights: {final_path}")


if __name__ == "__main__":
	main()