import argparse
import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader

from mfrnp_npz_data import MFRNPMultiStreamDataset, make_collate_fn
from model_v9 import MFTransolver_v9


def main():
	parser = argparse.ArgumentParser(description="Evaluate multi-stream MFTransolver_v9 on MFRNP NPZ datasets")
	parser.add_argument("--run_name", type=str, required=True)
	parser.add_argument("--weights", type=str, default="film_best.pth")
	parser.add_argument("--split", type=str, default="test", choices=["train", "valid", "test"])
	parser.add_argument("--n_lf", type=int, default=0)
	parser.add_argument("--n_hf", type=int, default=0)
	parser.add_argument("--results_dir", type=str, default=None)
	args = parser.parse_args()

	here = Path(__file__).resolve().parent
	ckpt_dir = here / "checkpoints" / args.run_name
	cfg = json.load(open(ckpt_dir / "train_config.json"))

	out_dir = Path(args.results_dir) if args.results_dir else ckpt_dir
	out_dir.mkdir(parents=True, exist_ok=True)
	alpha_dir = out_dir / "alpha_maps"
	alpha_dir.mkdir(parents=True, exist_ok=True)

	ds = MFRNPMultiStreamDataset(
		cfg["data_path"],
		levels=cfg["levels"],
		split=args.split,
		valid_ratio=cfg.get("valid_ratio", 0.1),
	)
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

	hf_std = float(cfg["hf_y_std"])
	rows = []
	all_sq_diffs: list = []   # squared errors, flattened per sample
	all_targets: list = []    # ground-truth values, flattened per sample
	with torch.no_grad():
		for i, (list_of_lf_toks, hf_tok, targets, sample_ids) in enumerate(loader, start=1):
			list_of_lf_toks = [t.to(device) for t in list_of_lf_toks]
			hf_tok = hf_tok.to(device)
			targets = targets.to(device)

			comps = model(list_of_lf_toks, hf_tok, return_components=True)
			pred = comps["pred"]
			alpha = comps["alpha"]

			diff = pred - targets
			# Accumulate for global nRMSE (paper formula)
			all_sq_diffs.append((diff ** 2).detach().cpu().numpy().reshape(-1))
			all_targets.append(targets.detach().cpu().numpy().reshape(-1))
			mae_norm = torch.mean(torch.abs(diff)).item()
			mse_norm = torch.mean(diff ** 2).item()
			rmse_norm = torch.sqrt(torch.mean(diff ** 2)).item()
			nrmse = rmse_norm

			diff_sq = torch.sum(diff ** 2, dim=1)
			true_sq = torch.sum(targets ** 2, dim=1)
			rel_l2 = torch.mean(torch.sqrt(diff_sq) / torch.clamp(torch.sqrt(true_sq), min=1e-12)).item()

			mae_phys = mae_norm * hf_std
			mse_phys = mse_norm * (hf_std ** 2)
			rmse_phys = rmse_norm * hf_std

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
				"mae_norm": mae_norm,
				"mse_norm": mse_norm,
				"rmse_norm": rmse_norm,
				"nrmse": nrmse,
				"rel_l2": rel_l2,
				"mae_phys": mae_phys,
				"mse_phys": mse_phys,
				"rmse_phys": rmse_phys,
				"alpha_self_mean": float(alpha_mean[0]),
			}
			for j in range(len(ds.lf_levels)):
				row[f"alpha_lf{j+1}_mean"] = float(alpha_mean[j + 1])
			rows.append(row)
			print(f"[{i:03d}/{len(ds):03d}] {sid} nrmse={nrmse:.4f} rel_l2={rel_l2:.4f}", end="\r", flush=True)

	print()

	# Global nRMSE = RMSE / std(Y_test) across all test samples and spatial points
	# Matches paper formula: sqrt(1/N * sum((yi - ŷi)^2)) / std(Y_test)
	# Computed in normalised space (scaler factors cancel identically in phys. space)
	all_sq_arr = np.concatenate(all_sq_diffs)
	all_tgt_arr = np.concatenate(all_targets)
	global_rmse = float(np.sqrt(np.mean(all_sq_arr)))
	std_y = float(np.std(all_tgt_arr))  # population std, ddof=0
	nrmse_global = global_rmse / max(std_y, 1e-12)

	df = pd.DataFrame(rows)
	summary = df.drop(columns=["sample_id"]).mean()
	summary["nrmse_global"] = nrmse_global

	weights_stem = Path(args.weights).stem
	per_csv = out_dir / f"eval_{args.split}_{weights_stem}_per_design.csv"
	summary_csv = out_dir / f"eval_{args.split}_{weights_stem}_summary.csv"
	df.to_csv(per_csv, index=False)
	summary.to_frame("value").to_csv(summary_csv)

	print("=" * 72)
	print(f"Dataset: {cfg['data_path']} | split={args.split} | weights={args.weights}")
	print(f"nRMSE_global={nrmse_global:.6f}  (RMSE={global_rmse:.6f} / std_Y={std_y:.6f})")
	print(
		f"NRMSE_per_sample_mean={summary['nrmse']:.6f} RMSE_phys={summary['rmse_phys']:.6f} "
		f"MSE_norm={summary['mse_norm']:.6f} RelL2={summary['rel_l2']:.6f}"
	)
	print(f"alpha_self_mean={summary['alpha_self_mean']:.6f}")
	for j in range(len(ds.lf_levels)):
		print(f"alpha_lf{j+1}_mean={summary[f'alpha_lf{j+1}_mean']:.6f}")
	print("=" * 72)
	print(f"Per-design: {per_csv}")
	print(f"Summary:    {summary_csv}")
	print(f"Alpha maps: {alpha_dir}")


if __name__ == "__main__":
	main()