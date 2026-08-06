# Getting the MFFP code and data onto your cluster

Written 2026-08-05 for Nicholas, against branch `mffp-trunk-eloise`.

Two separate things come from two separate places.
The **code** is the GitHub repo you already own, `nicksungg/mf_field`.
The **data** is a HuggingFace dataset — and it has moved.

> **If you already have `benchmark_42/` on your cluster, read [§4](#4-data-download-benchmark_42) before running anything.**
> A size-based sync will report success and leave you on the defective data.

If you would rather not do this by hand, `CLUSTER_SETUP_PROMPT.md` in this repo is the same procedure written as a self-contained prompt you can hand to an agent running on the cluster.

---

## 1. Code

```bash
export MFFP_ROOT=/your/path/mf_field          # pick a directory with ~10 GB free
git clone https://github.com/nicksungg/mf_field.git "$MFFP_ROOT"
cd "$MFFP_ROOT"
git checkout mffp-trunk-eloise
```

Already have a clone?
`git checkout mffp-trunk-eloise && git pull`.

The `.gitignore` excludes every heavy artifact type (`*.npz *.npy *.pt *.h5 *.png *.pdf`, plus `data/`, `.venv/`).
So a fresh clone gives you the full tree and every `.py` / `.md` / `.json`, and **zero arrays**.
Empty dataset directories are expected, not a broken clone.

## 2. Python environment

```bash
python -m venv "$MFFP_ROOT/.venv"
source "$MFFP_ROOT/.venv/bin/activate"
pip install numpy scipy h5py scikit-image matplotlib huggingface_hub
pip install torch --index-url https://download.pytorch.org/whl/cu121   # match your CUDA
```

## 3. HuggingFace access

The dataset is **gated** with `gated: auto` — access is granted the instant you accept, no manual approval wait.
But you must accept once, in a browser, as the same account whose token you use.

1. Visit <https://huggingface.co/datasets/eloisezeng/mf_field> and click **"Agree and access repository"**.
   There is no API for this step.
2. Create a **read** token at <https://huggingface.co/settings/tokens>.
3. On the cluster:

   ```bash
   hf auth login          # paste the token
   python -c "from huggingface_hub import HfApi; print(HfApi().whoami()['name'])"
   ```

The error code tells you which half is wrong.
`401 ... Please log in` means no token, or it is not being picked up.
`403 ... you are not in the authorized list` means the token is valid but *that account* never clicked through the gate — redo step 1 as the token's owner.

## 4. Data — download `benchmark_42/`

```bash
cd "$MFFP_ROOT"
python hf_download_benchmark_42.py --prune
```

405 files, 7.46 GB, mirrored 1:1 into `$MFFP_ROOT/benchmark_42/`.
The script is resumable — re-run it after any interruption.

### If you already have data from `nicksung/mf_field`

The corrected release lives at **`eloisezeng/mf_field`**.
It exists as a separate repo only because HF personal repos cannot grant collaborators write access, so the fixes could not be pushed back into your namespace.
Seven datasets differ; the other 35 are byte-identical.

**Do not sync it with any size-based tool.**
Re-pairing the ifc fidelity ladders changed *which* samples sit at each level, not the array shapes.
All 22 arrays under `core/ifc_heat/` and `core/ifc_poisson/` therefore have byte-identical sizes across the two releases and completely different contents.
Anything that skips on equal size — including the earlier version of this very script — leaves the defective disjoint data in place and reports success.

The current script verifies by sha256, so the command above does the right thing.
`--prune` additionally removes the 16 `ifc_*/scalers/*.pkl` files the old release shipped and this one deliberately omits; they were fitted on the old disjoint sample set.
Local `*backup*` directories are never touched.
Without `--prune` the orphans are listed rather than deleted.

## 5. Wire the datasets into the factory

```bash
python mf_field/akash/eval/wire_datasets.py
```

This reads `benchmark_42/MANIFEST.csv` and creates collision-safe relative symlinks in `factory_mffp/data/` (`<name>` for core, `ext__<name>`, `sharp__<name>`).
It is idempotent and repoints stale symlinks, so it is safe to re-run.
Expect `wired 42 datasets` and `missing: none`.

Two things to know.
`factory_mffp/data/` is a **guarded directory** under `factory.md` — this script is the intended mechanism for writing to it, but it is still a guarded path.
And the directory ends up with **44** entries, not 42: `chin_chun_isothermal` and `chin_chun_potential` are pre-existing dangling symlinks that predate all of this. Leave them.

## 6. Verify

Run these and read the real output rather than assuming.

```bash
cd "$MFFP_ROOT"
git rev-parse --abbrev-ref HEAD                                   # mffp-trunk-eloise

for c in core ext sharp; do echo "$c: $(ls benchmark_42/$c | grep -v '^_' | wc -l)"; done
# expect core 15, ext 8, sharp 19

python -c "
import numpy as np
d = np.load('benchmark_42/ext/helmholtz_2d/train_l2.npz')
print({k: d[k].shape for k in d.files})"
# expect {'x': (400, 3), 'y': (400, 9216)}
```

The single most useful check that you are on the **corrected** data, not the old release:

```bash
python -c "
import numpy as np
X = {f: np.load(f'benchmark_42/core/ifc_heat/train/fidelity_{f}/Xs.npy') for f in (8, 16, 32, 64)}
rows = lambda a: {tuple(np.round(r, 10)) for r in a}
print('nested:', all(rows(X[b]) <= rows(X[a]) for a, b in ((8,16), (16,32), (32,64))))
print('cond dim of sharp/fisher_kpp_2d:', np.load('benchmark_42/sharp/fisher_kpp_2d/train_l1.npz')['x'].shape[1])"
# corrected release -> nested: True   and   cond dim 50
# old release       -> nested: False  and   cond dim 2
```

Then run the contract smoke from `mf_field/factory_mffp/HOWTO.md` §1 against one dataset.

## 7. Before you trust any score

**14 of the 42 datasets are degenerate**, in one of four ways, all flagged in `benchmark_42/MANIFEST.csv` and explained in `benchmark_42/README.md`.
Each affected dataset also carries a warning at the top of its own `README.md`.

Two carry no multi-fidelity signal at all: `ext/gray_scott_2d` (LF–HF correlation 0.008) and `ext/kuramoto_sivashinsky_1d` (−0.057).
Six are solved by simply copying the coarse field onto the fine grid, to under 1% relative L2.
Two more (`sharp/fisher_kpp_2d`, `sharp/allen_cahn_2d`) are *level-dominated*: copying looks near-perfect only because the field is nearly uniform, and the structural error is 21–35× the headline number.

Also note `core/ifc_heat` and `core/ifc_poisson` ship **5** HF training samples.
Per-dataset conclusions there are anecdote, not measurement.

**These flags are not applied consistently by the code**, so do not assume you are protected.
`akash/eval/compute_elo_full.py` excludes degenerate datasets from its headline ranking.
`factory_mffp/eval/score.py` — which computes `composite_nRMSE`, the metric `factory.md` tells the CEO agent to minimize — has no such exclusion; it is a plain geomean over everything it discovers.
`factory_mffp/paper/make_figures.py` uses a hardcoded `HARD` set that matches neither.

## Where to go next

`mf_field/factory_mffp/HOWTO.md` is the operational runbook and takes over from here at its §0.
`benchmark_42/README.md` has the full revision history — what was wrong with the 2026-07-28 release and what changed.
`CLAUDE.md` at the repo root is the orientation doc for the monorepo as a whole.
