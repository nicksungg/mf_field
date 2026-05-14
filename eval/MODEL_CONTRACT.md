# Model Family Contract

Every model family lives at `models/<family>/` and **must** expose two scripts and one manifest:

```
models/<family>/
├── manifest.json       # { "name": str, "description": str, "supports": ["ifc_raw", "npz"] }
├── smoke_eval.py       # see signature below
└── (whatever else the family needs — code, configs, etc.)
```

## `smoke_eval.py` signature

```
python smoke_eval.py \
    --dataset_dir <path>           # absolute path to a dataset under data/<name>/
    --dataset_name <name>          # short name (e.g. "ifc_heat")
    --epochs <int>                 # training epochs (smoke loop sets this small)
    --out <path>                   # where to write the results JSON
    --ckpt_dir <path>              # where to read/write checkpoints (must support resume)
    --seed <int>                   # rng seed
```

Exit code `0` on success, non-zero on failure. The runner enforces a per-call wall-time limit; on timeout the process is killed and the run is recorded as failed.

## Output JSON schema

```json
{
  "model": "v9_baseline",
  "dataset": "ifc_heat",
  "splits": {
    "test_l4": { "nRMSE": 0.0123, "n_samples": 128 },
    "ood_l4":  { "nRMSE": 0.0456, "n_samples": 64  }
  },
  "n_params": 12345678,
  "train_seconds": 612.4,
  "eval_seconds":  18.3,
  "notes": "early-stopped at epoch 87 due to gate collapse"
}
```

Required keys: `model`, `dataset`, `splits` (with at least one split entry containing `nRMSE`). Other keys are optional metadata.

## Checkpoint resume

`smoke_eval.py` **must** check `ckpt_dir` for an existing checkpoint and resume from it if found. SLURM jobs on `mit_preemptable` may be killed and requeued; without resume support, every preemption wastes the run.

Recommended pattern: save `ckpt_dir/last.pt` every 10 epochs containing `{ "epoch": int, "model_state": ..., "optim_state": ..., "best_val": float }`.
