# Cluster setup prompt — MFFP repo + HuggingFace data

Hand the block below to an agent running **on the cluster**.
It provisions the code and all 42 benchmark datasets from scratch, up to the point where `mf_field/factory_mffp/HOWTO.md` takes over at its §0.

Written 2026-07-28 against branch `mffp-trunk-eloise` and HF commit `56c1328149`.

---

## The prompt

````
Set up the MFFP research monorepo and its 42 benchmark datasets on this cluster, from scratch.

## What you are provisioning

Two separate things from two separate places:

1. **Code** — GitHub repo `https://github.com/nicksungg/mf_field.git`, branch `mffp-trunk-eloise`.
2. **Data** — HuggingFace dataset `eloisezeng/mf_field`, which is **gated**. 405 files, 7.46 GB.

   > This supersedes `nicksung/mf_field` (the 2026-07-28 release), which still carries the
   > grid-registration, condition-incompleteness, and ifc-pairing defects. Do not mix the two —
   > seven datasets differ. See `benchmark_42/README.md` § Revision history.

The repo's `.gitignore` excludes every heavy artifact type (`*.npz *.npy *.pt *.h5 *.tar.gz *.zip *.png *.pdf`, plus `data/`, `logs/`, `checkpoints/`, `.venv/`).
A fresh clone therefore gives you the full directory tree and every `.py` / `.md` / `.json`, and **zero arrays**.
Empty dataset directories are expected, not a broken clone.

## Step 1 — Choose a root and clone

Pick a root with **at least 40 GB free** (7.5 GB data, plus checkpoints).
Use the group data volume, not your home directory.

    export MFFP_ROOT=/orcd/data/faez/001/<you>/mf_field    # adjust to your allocation
    git clone --branch mffp-trunk-eloise \
        https://github.com/nicksungg/mf_field.git "$MFFP_ROOT"
    cd "$MFFP_ROOT"
    git rev-parse --abbrev-ref HEAD    # must print: mffp-trunk-eloise

**Layout gotcha — read before following HOWTO.md.**
This branch uses a *nested* layout: the repo root holds `mf_field/`, `mf_field_eloise_data/`, `mf_field_extension_data/`, and the factory lives at `$MFFP_ROOT/mf_field/factory_mffp`.
`mf_field/factory_mffp/HOWTO.md` hardcodes a *flat* layout (`/orcd/data/faez/001/nick/mf_field/factory_mffp`), which is missing that extra `mf_field/` level.
Insert it into every HOWTO path, or you will get confusing "not a factory directory" errors.

## Step 2 — Python environment

    module load python/3.11 2>/dev/null || module load anaconda
    python3 -m venv "$MFFP_ROOT/.venv"
    source "$MFFP_ROOT/.venv/bin/activate"
    pip install --upgrade pip
    pip install numpy scipy h5py matplotlib scikit-image huggingface_hub

Install PyTorch with the CUDA build matching this cluster's driver (check `nvidia-smi` first) — do not accept the default CPU wheel.
Verify on a **GPU node**, not the login node:

    srun --gres=gpu:1 --time=5 python -c "import torch; print(torch.__version__, torch.cuda.is_available())"

## Step 3 — HuggingFace authentication

The dataset is gated with `gated: auto`: access is granted the instant you accept, with no manual approval wait — but you must accept once, in a browser, as the account whose token you use.

1. Log in to HuggingFace, visit `https://huggingface.co/datasets/eloisezeng/mf_field`, click **"Agree and access repository"**. There is no API for this.
2. Create a **read** token at `https://huggingface.co/settings/tokens`.
3. On the cluster:

       hf auth login          # paste the token
       python -c "from huggingface_hub import HfApi; print(HfApi().whoami()['name'])"

**The error code tells you which half is wrong:**
- `401 ... Please log in` — no token, or it is not being picked up.
- `403 ... you are not in the authorized list` — token is valid, but *that account* never clicked through the gate. Redo 3.1 as the token's owner.

## Step 4 — Download `benchmark_42/`

Everything lives under one top-level directory. Mirror it 1:1 into the repo root:

| HF path | Size | Files | Contents |
|---|---|---|---|
| `benchmark_42/core/` | 3.78 GB | 193 | 15 datasets |
| `benchmark_42/sharp/` | 3.38 GB | 172 | 19 datasets |
| `benchmark_42/ext/` | 0.30 GB | 52 | 8 datasets |
| `benchmark_42/MANIFEST.csv` | 4 KB | 1 | per-dataset stats + quality flags |
| `benchmark_42/README.md` | 8 KB | 1 | collection tables |

Each dataset is a folder of aligned/nested `train_l*.npz` / `test_l*.npz` (`l1` = coarsest), with keys `x` (conditions) and `y` (flattened field).
Fidelity counts range from 2 to 9 levels depending on the dataset.
Some carry `meta.json`, `README.md`, and an `ood/` split; the 15 core datasets have no `meta.json`, which is expected — their grids are already in the harness's `KNOWN_GRIDS`.

Write a script that enumerates with `HfApi().list_repo_files(...)` and fetches each file via `hf_hub_download(repo_id=..., repo_type="dataset", filename=..., local_dir=<staging>)`, then copies into place.
Make it **resumable** — skip files already present at the identical byte size.

Do **not** use `snapshot_download(allow_patterns=["**/*.npz"])`: on `huggingface_hub` 1.8.0 those glob patterns match nothing and the call dies with `ValueError: min() arg is an empty sequence`.

Budget 15–45 min. Run it under `tmux`/`screen` or as a batch job, not a bare SSH session.

### `helmholtz_2d` and `kuramoto_sivashinsky_1d` appear twice

Both exist in **`ext/` and `sharp/`**, as genuinely different datasets from different generators.
They are distinguished by collection folder, and by the `ext__` / `sharp__` prefixes the harness uses.
Confirm they differ before assuming a duplicate: `ext/helmholtz_2d` is a 96x96 HF grid, `sharp/helmholtz_2d` is 256x256.
Never flatten the collections into one namespace.

## Step 5 — Wire the datasets into the factory

Run the wiring script:

    cd "$MFFP_ROOT"
    python mf_field/akash/eval/wire_datasets.py

It reads `benchmark_42/MANIFEST.csv`, creates collision-safe relative symlinks in `factory_mffp/data/` (`<name>` for core, `ext__<name>`, `sharp__<name>`), writes `factory_mffp/data_adapters/known_grids_extra.json`, and regenerates `akash/eval/bench_datasets.txt`.
It derives the repo root from its own location, so no path editing is needed; `$MFFP_ROOT` overrides it if you want to be explicit.
It is idempotent and repoints stale symlinks, so it is safe to re-run.

Expect `wired 42 datasets (27 ext/sharp grid entries)` and `missing: none`.
If it reports anything under `SKIPPED`, a real directory is sitting where a symlink belongs — stop and report rather than deleting it.

**`factory_mffp/data/` is a guarded directory** under `factory.md` (alongside `baselines/`, `eval/`, `references/`, `scripts/`).
Creating these symlinks is exactly what this script exists to do, but it does modify a guarded path — **confirm with the repo owner before running it on a shared checkout**, and report that you ran it either way.

Note `data/` will contain **44** entries, not 42: `chin_chun_isothermal` and `chin_chun_potential` are pre-existing dangling symlinks, absent from the roster and from `benchmark_42/` but still listed in `loaders.py`. Leave them alone and mention them in your report.

## Step 6 — Know which datasets are degraded before you trust any score

`benchmark_42/MANIFEST.csv` carries `lf_hf_pearson` plus boolean `mf_useless`, `operator_hard`, `degenerate`.
**11 of 42 datasets are flagged `degenerate`; 2 are flagged `mf_useless`.**

Two carry no usable multi-fidelity signal at all:

- `ext/gray_scott_2d` — LF-HF correlation **0.008**
- `ext/kuramoto_sivashinsky_1d` — LF-HF correlation **-0.057** (negative)

On those, LF tells you nothing about HF, so no multi-fidelity method can win and any good score is single-fidelity fitting.

Five sharp datasets sit at the opposite extreme — `allen_cahn_1d`, `fisher_kpp_1d`, `kuramoto_sivashinsky_1d`, `nls_1d`, `sine_gordon_1d` all have correlation **1.000** and are flagged `operator-hard, degenerate`.
There LF is essentially identical to HF, so copying LF is near-optimal and there is no headroom to demonstrate anything.

Also note `core/ifc_heat` and `core/ifc_poisson` have **N_hf = 5**.
Five HF samples: per-dataset conclusions there are anecdote, not measurement.

**Handling of these flags is inconsistent across the codebase — do not assume you are protected:**

- `akash/eval/compute_elo_full.py` **does** exclude MF-useless and empirically-unlearnable datasets from its headline ranking.
- `factory_mffp/eval/score.py` — which computes `composite_nRMSE`, the metric `factory.md` tells the CEO agent to minimize — has **no such exclusion**. It is a plain geomean over best-per-dataset across everything discovered.
- `factory_mffp/paper/make_figures.py` uses a hardcoded `HARD = {ifc_poisson, era5, pm_test, burgers_generated, burgers_param_generated}` that does not match the manifest flags.

So the autonomous loop optimizes an objective in which roughly a quarter of the cells cannot reward a multi-fidelity method.
**Surface this to the repo owner rather than silently working around it.**

## Step 7 — Verify, and report honestly

Run these and paste the real output. Do not report success on a check you did not run.

    cd "$MFFP_ROOT" && git rev-parse --abbrev-ref HEAD
    git status --porcelain | grep -v '^??' | wc -l          # expect 0

    du -sh benchmark_42/core benchmark_42/ext benchmark_42/sharp
    for c in core ext sharp; do echo "$c: $(ls benchmark_42/$c | wc -l) datasets"; done
    # expect core 15, ext 8, sharp 19

    python -c "
    import numpy as np
    d=np.load('benchmark_42/ext/helmholtz_2d/train_l2.npz')
    print({k:d[k].shape for k in d.files})"
    # expect {'x': (400, 3), 'y': (400, 9216)}

    ls "$MFFP_ROOT/mf_field/factory_mffp/data" | wc -l      # 44 after step 5 (42 + 2 chin_chun)

Then run the contract smoke from HOWTO.md §1 against one dataset and report the resulting nRMSE.

Finally summarise: dataset counts per collection, whether the symlink wiring was done and with whose approval, any verification that failed, and anything you changed in `wire_datasets.py`.
````

---

## Notes for Eloise (not part of the prompt)

Three things most likely to bite, in order:

1. **`factory_mffp/data/` is guarded**, and the wiring step writes 42 symlinks into it. The script is the intended mechanism, but it is still a guarded path — worth clearing with the repo owner before it runs on a shared checkout.
2. **The `score.py` / `compute_elo_full.py` inconsistency.** The leaderboard filters degenerate datasets; the factory's own objective does not. That is a real question about what the autoresearch loop is optimizing, and `score.py` sits inside the guarded set, so it needs the repo owner.
3. **The nested-layout path shift**, which makes every path in `HOWTO.md` wrong by one level.
