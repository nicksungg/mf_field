# Does the pre-round-1 benchmark need re-running?

**Companion to** `MFFP_registration_defect_2026-08-01.pdf` (and its HTML source `REGISTRATION_DEFECT_NOTE_2026-08-01.html`).
That note repaired the round-2 scoring reference and listed what was left open.
This note asks a question the original did not: **what does the unrepaired remainder do to the 42-dataset ELO benchmark that was run before round 1?**

**Short answer.**
The pre-round-1 benchmark never had a copy-LF reference or a skill metric, so the defect note's headline correction — inflated denominators — has no counterpart here and cannot be what damages it.
That is precisely why this note is needed: reading the defect note and concluding this benchmark is out of scope would be the wrong inference.
The exposure runs through the note's *open* items instead, in three separate ways, and one of them is literal — on 7 of 42 datasets the models were trained and scored against a field that is not the high-fidelity solution.
The ranking is also not robust: the champion changes when the affected datasets are removed.
Separately, and unrelated to the defect, **two of the 42 datasets are the same dataset**, so the ELO double-counts it.

**What is being asked of you.**
Nothing here is a retraction, and nothing has been edited — `data/`, `eval/` and the frozen round-1 numbers are all guarded surfaces.
The decision is whether the pre-round-1 ELO can still be cited as-is, cited with a restricted dataset scope, or has to be re-run.
Cost of a full re-run is given in §9.

---

## 1. What the ELO measures, and why the defect note appears not to cover it

The artifact in question is `mf_field/akash/results/bench_full_elo.csv` — 12 models over 42 datasets, 2500 epochs, seed 42, produced by `mf_field/akash/eval/compute_elo_full.py`.

It is built from **raw rel-L2 against the HF target**, compared pairwise between models on the same dataset:

```python
ra, rb = rel[(a, d)], rel[(b, d)]        # compute_elo_full.py:130
```

**There was no copy-LF reference and no skill metric at this stage of the project.**
Across all 975 result JSONs the split-level metric keys are only `nRMSE`, `rel_l2_mean`, `rel_l2_std`, `rel_l2_ci95_*`, `rel_l2_per_sample`, `n_samples`.
No `skill` key exists, and `akash/eval/` and `akash/results/` contain no copy-LF baseline artifact at all.
Skill against copy-LF was introduced later, for round 1.

This is worth stating explicitly because it sets up the wrong inference.
The defect note is organised around the copy-LF reference — the repair, the $1.1\times$–$9.1\times$ denominator inflation, the "every skill number flattered its model" conclusion.
A reader could reasonably finish that note and decide it says nothing about the pre-round-1 benchmark, since that benchmark has no denominator to inflate.

That conclusion is right about the mechanism and wrong about the outcome.
The pre-round-1 ELO is exposed through the note's **open** items rather than its repaired one — item 1 (models still upsample LF with the defective map) and item 2 (the generators still write shifted arrays).
Those act on the training signal and, on 7 datasets, on the scored target itself.
Sections 3 through 6 are those channels.

---

## 2. Finding A — the ranking is not robust to removing the affected datasets

I recomputed the ELO with the identical pairwise procedure from `bench_full_metrics.csv`, varying only which datasets enter the match pool.

| rank | all 40 learnable | non-sharp (20) | core only (15) |
|---|---|---|---|
| 1 | mf_fno_transfer_film 1692 | **convnext_unet_film 1775** | **convnext_unet_film 1780** |
| 2 | convnext_unet_film 1657 | mf_fno_transfer_film 1748 | mf_fno_transfer_film 1743 |
| 3 | mf_fno_allpairs 1639 | mf_fno_allpairs 1635 | mf_fno_allpairs 1592 |
| 4 | transolver_residual 1566 | mf_fno_transfer_bar 1581 | mf_fno_transfer_bar 1561 |
| 8 | wno_transfer_film 1502 | transolver_residual 1480 | transolver_residual 1479 |

The reported champion changes, and `transolver_residual` drops four places.

Two honest caveats that soften this.
`convnext_unet_film` participates in only 18 of 20 and 13 of 15 cells, so part of its gain is a participation artifact of running ELO with uneven coverage.
`transolver_residual`'s all-40 rank was already `val`-flagged in `BENCH_FULL.md` — its metric is held-out **validation** nRMSE, not the unified HF test split, which is optimistic and not directly comparable.
Neither caveat accounts for the whole swing.

The point is not that the core-only ordering is the true one.
The point is that the ordering is decided by a group of datasets that §3–§5 show to be compromised.

---

## 3. Finding B — on 7 of 42 datasets the scored target is not the HF solution

### 3.1 The mechanism is a grid cap, not anything about the physics

Every family puts all fields on one working grid before training or scoring:

```python
grid = _cap_grid(hf_grid_native)                          # WORK_CAP = 256
Y_hf = _to_grid(train[...][hf], hf_grid_native, grid)     # HF training target
Y_te = _to_grid(test[...][hf],  hf_grid_native, grid)     # HF TEST target — what rel-L2 scores against
```

and `_to_grid` interpolates only when the two grids differ:

```python
if (Hs, Ws) != (Hd, Wd):
    t = F.interpolate(t, size=(Hd, Wd), mode="bilinear", align_corners=False)
```

`align_corners=False` is the map the defect note verified bit-identical to the defective `zoom(grid_mode=True)`.

So the split is decided purely by whether the HF grid exceeds 256 in some dimension.
Every result JSON records both grids, and `eval_protocol: full_field_on_working_grid` confirms the metric is taken on the working grid.

- **35 datasets** — HF native $\le 256$, the guard skips, the target is the raw file byte-for-byte. Untouched.
- **7 datasets** — HF native $> 256$, so the *target itself* goes through the defective map:

| dataset | `hf_grid_native` | `work_grid` |
|---|---|---|
| era5 | $721 \times 1440$ | $128 \times 256$ |
| pm_test | $721 \times 1440$ | $128 \times 256$ |
| sharp__allen_cahn_1d | $1 \times 512$ | $1 \times 256$ |
| sharp__fisher_kpp_1d | $1 \times 512$ | $1 \times 256$ |
| sharp__kuramoto_sivashinsky_1d | $1 \times 512$ | $1 \times 256$ |
| sharp__nls_1d | $1 \times 512$ | $1 \times 256$ |
| sharp__sine_gordon_1d | $1 \times 512$ | $1 \times 256$ |

All four *proven* node-sampled panel datasets — allen_cahn_2d, cahn_hilliard, fisher_kpp_2d, phase_field_crystal_2d — are in the clean 35.
Their targets are fine.

### 3.2 What the resample does, measured

The defect note's index-ramp probe, run here in the **downsample** direction at $512 \to 256$:

```
source index each output pixel reads
  F.interpolate(ac=False) : 0.5, 2.5, 4.5, 6.5, 8.5, 10.5
  node-correct  y[::2]    : 0.0, 2.0, 4.0, 6.0, 8.0, 10.0
  constant offset         : 0.5 fine cells = 0.25 coarse cells
```

Every output pixel lands exactly halfway between two source samples, so bilinear returns their mean.
Verified: the output equals $\tfrac{1}{2}\left(y_{2k} + y_{2k+1}\right)$ to $6\times10^{-8}$.

That does **two** things, not one.

1. **It shifts.**
   These are pseudo-spectral solves, so fine sample $2k$ *is* the solution value at that point, and `y[::2]` is exact with zero interpolation error.
   What was stored instead sits half a fine cell off the grid it claims to be on.
2. **It blurs.**
   A two-tap average is a low-pass filter.
   On a steep $\tanh$ front at 512 points the retained energy is 99.98% in the low band, **95.2%** in the mid band, **83.6%** above $k > 64$.
   The target is softened in exactly the band the sharp panel exists to discriminate.

The correct answer was one array slice and free.
This was never a cost of choosing a 256 working grid — it was avoidable.

### 3.3 Why this is a *wrong* target and not merely a coarser one

Coarsening on purpose is a legitimate design choice.
What makes these wrong is that the stored field is not a consistent representation of the solution at 256 points under the dataset's own convention — it is off-grid — and the *same array* serves both as the training target and as the thing rel-L2 measures against.
Nothing downstream can see the discrepancy or correct for it.
Every number reported on those seven datasets answers the question "how well do you predict a blurred, half-shifted rendering of the solution."

### 3.4 How much it actually matters — honest sizing

This cuts against the drama and should be stated plainly.
The bilinear target differs from the node-correct target by rel-L2 **0.0142** on the test front above.
The best non-`val` model errors on those five sharp 1D datasets are **0.21 to 0.48**.
The target distortion is therefore 15–35$\times$ smaller than the model errors.

**This is an integrity defect, not the cause of the failures.**
Repairing it would not rescue any of those results.

era5 and pm_test are a different and worse story.
$721\times1440 \to 128\times256$ retains **3.2%** of pixels at a $5.63 \times 5.62$ reduction through a two-pixel stencil, which aliases everything above the new Nyquist rather than filtering it.
The half-cell registration error is a rounding detail on top of a badly undersampled target.
era5 is also lat-lon reanalysis with non-uniform physical spacing, so "half a cell" is not even a fixed physical distance there.

---

## 4. Finding C — where the target is clean, the training signal still is not

This is defect-note item 1 ("the models carry the same defect"), priced against this specific benchmark.

The result JSONs record how each model consumes the LF field in an `mf_mechanism` key:

- `transfer_learning_pretrain_LF_finetune_HF` — convnext_unet_film, mf_fno_transfer, mf_fno_transfer_bar, mf_fno_transfer_film, wno_transfer_film, nomad_mf (**6 of 12**)
- `allpairs_joint_train_then_lf2hf_finetune` — mf_fno_allpairs
- `FIRE_distribution_conditioned_residual_HF=muLF+delta` — fno_fire_distcond

For all of these, `Y_lf = _to_grid(train["field_by_fid"][lf], lf_grid_native, grid)` is the defective upsample, and it is used as a **training target** or an **additive base**.

- The **transfer families** literally optimise the network to emit a half-cell-shifted field during pretraining, and the HF finetune then has to un-teach that shift before it can learn any physics.
  The stronger the pretraining, the more shift is baked in.
  The multi-fidelity signal, which is the entire point of the benchmark, is partly the artifact.
- **fno_fire_distcond** supervises $\delta = \mathrm{HF} - \mathrm{LF}_{\text{shifted}}$, so its residual target carries a spurious analytic phase ramp.
  End-to-end the shift cancels, because the same shifted base is added back, so its *score* is honest.
  But the residual it must learn is artificially harder and higher-frequency than the true fidelity gap.
  This is precisely the mechanism the defect note priced at 87–98% of one round-1 corrector's headline win.

I checked whether any family escapes.
None does — `fno_coregionalization` resamples every fidelity onto a shared working grid, and `transolver_residual` interpolates LF at the HF query coordinates as a hard residual base.

So the tax is universal across the roster.
But *how* it enters differs by family — pretrain target versus additive base versus input channel — and that difference is what makes it non-uniform, which is what moved the ranking in §2.

---

## 5. Finding D — on the 2D sharp panel, nothing beats a zero-parameter corrected resample

Copy-LF enters this section only as a **borrowed external yardstick**, not as a metric this benchmark ever used (§1).
The question is simply: how do these models compare to correctly resampling the coarse solve and stopping there?

Best model error against the corrected copy-LF denominators from the defect note §04:

| dataset | best non-`val` model | corrected copy-LF | ratio |
|---|---|---|---|
| sharp__allen_cahn_2d | nomad_mf 0.261 | 0.00178 | $147\times$ |
| sharp__phase_field_crystal_2d | nomad_mf 0.350 | 0.00738 | $47\times$ |
| sharp__fisher_kpp_2d | nomad_mf 0.248 | 0.02145 | $12\times$ |
| sharp__cahn_hilliard | mf_fno_transfer_film 0.441 | 0.04180 | $11\times$ |
| ext__helmholtz_2d | mf_fno_transfer_bar 1.124 | 0.29903 | $3.8\times$ |

The corrected denominators come from the round-2 panel harness, not this benchmark, so these ratios are order-of-magnitude rather than like-for-like.
`transolver_residual` is nominally best on all five (0.245 / 0.349 / 0.180 / 0.247 / 0.478) but is the `val`-flagged model, so it is excluded here.

Every model loses to a zero-parameter, correctly-registered resample of the coarse solve by $4\times$ to $147\times$.
On that panel the ELO is ranking degrees of failure.
That is a legitimate thing to rank, but "who won" carries almost no information about multi-fidelity capability there.

---

## 6. Finding E — era5 and pm_test are the same dataset

Unrelated to the registration defect, found while checking §3.

Every fidelity file matches byte-for-byte:

```
29ed988e6b39e1421aec9b40ccbfc7ce  data/era5/era5_train_test/test_l9.npz
29ed988e6b39e1421aec9b40ccbfc7ce  data/pm_test/data/test_l9.npz
```

and all 18 `train_l*`/`test_l*` files match on size across the two directories.

8 of the 9 models that ran on both return **bit-identical** rel-L2 to $10^{-12}$ — `fno_coregionalization` 0.05728000, `mf_deeponet` 0.07777700, `mf_fno_transfer_film` 0.07231200 on both.
The ninth, `mfrnp`, differs at 0.185358 vs 0.188944, which is that family's own run-to-run nondeterminism, not different data.

**Consequence.**
The 42-dataset benchmark is really 41 datasets.
Because ELO pools all pairwise matches into one rating, every era5 match is replayed a second time under the name pm_test, giving that dataset double weight in all twelve ratings.
This is independent of everything else in this note and should be fixed before any ELO is re-reported.

---

## 7. Already on the record, and still inside the ELO pool

These are from the defect note, repeated here only because they are live in *this* artifact.

- **sharp__phase_field_crystal_2d** has essentially no fidelity gap under a correct reference — the fraction of fine-grid energy outside the coarse band is $4.9\times10^{-16}$.
  Its matches are noise.
- **ext__helmholtz_2d** and **sharp__helmholtz_2d** reproduce from the condition vector in closed form to $2.2\times10^{-13}$ via two FFTs.
  A dataset a closed-form solve answers exactly cannot support a multi-fidelity claim.
- **Two target-scaling defects** (defect note item 3) hit helmholtz and phase-field-crystal specifically, and they are *per-family* — families using a single global `max|y|` scaler are crushed, families normalising per sample are not.
  That is per-model ordering noise unrelated to model quality.

`compute_elo_full.py` excluded only `ext__gray_scott_2d` and `ext__kuramoto_sivashinsky_1d` as degenerate.
None of the three above was excluded, so all of them are inside the 40-dataset match pool.

---

## 8. What is *not* affected — stated so the scope stays fair

- The copy-LF reference is simply not in scope — this benchmark predates the skill metric entirely, so the reference repair is neither a source of damage nor a source of protection here (§1).
- 35 of 42 datasets have a byte-exact, untouched HF target, including all four proven node-sampled panel datasets (§3.1).
- The 15 `core` datasets come from finite-volume solvers, where `align_corners=False` is the *correct* convention.
  There is no registration defect on them.
- Within any single dataset, every model saw the same inputs and the same target, so pairwise comparisons *inside* a dataset remain internally consistent — the same argument the defect note makes for within-card contrasts.
  What is compromised is the aggregate across datasets, and the question being asked on the seven.

---

## 9. Options, with cost

The ELO source runs are 529 jobs at 2500 epochs, single seed (s42), totalling **526 GPU-hours**, mean 60 min per run, longest single run 17.1 h.

**A. Cite with a restricted scope (recommended as the immediate step, ~0 GPU-h).**
Report the ELO with the dataset scope stated explicitly rather than as one number.
Drop pm_test as a duplicate, drop the 7 wrong-target datasets, drop phase-field-crystal and both helmholtz.
The core-only ranking in §2 is defensible today; the all-40 ranking is not, because half its match pool is measured through an unrepaired error.
This is a re-aggregation of existing JSONs and costs nothing.

**B. Re-run only the datasets whose target is wrong (7 datasets, 87 of the 529 runs).**
Raise `WORK_CAP` to 512 so the five sharp 1D sets keep their native grid, and decide deliberately what era5 should be downsampled to and with what filter.
Those 87 runs cost **127 GPU-h** as originally run; at 512 rather than 256 the sharp 1D runs will cost more, so treat that as a lower bound.
This fixes §3 but leaves §4 — the shifted LF training signal — in place.

**C. Full re-benchmark under the corrected per-dataset registration (~526 GPU-h, plus seeds).**
The model-side dispatch already exists (`models/_common/lf_registration.py`, commit `f63bcbf`, 2026-08-01), so the code is ready.
This is the only option that answers "would the ordering survive repair," which §2 shows is a real question.
It should be paired with the index-ramp probe run once per dataset, since only the sharp panel has been proven node-sampled.

My recommendation is **A now, C when there is idle cluster time**, and to treat the current ELO as provisional in any writeup until C lands.

---

## 10. Open and unverified

- **`transolver_residual`'s registration convention is unknown, and it is the sharp-panel winner.**
  It does not use `F.interpolate` — it uses a soft-nearest-neighbour interpolation over coordinate grids (`model.py:49 lf_interp_at_query`).
  Whether it is misregistered depends entirely on how the LF and HF coordinate arrays are constructed, which happens in the tokenizer and which I did not trace.
  If its coordinates happen to be node-aligned while every other family's are cell-centred, that alone would explain its sharp-panel result — and its metric is validation-based on top of that.
  This is the single highest-value check before that number is cited anywhere.
- Only 4 of the 19 `sharp__` datasets have been *proven* node-sampled.
  The rest come from the same `mffp_sharp/common/ladder.py` generator, so they are strongly suspected, but the index-ramp probe has not been run per dataset.
- The §5 ratios mix two harnesses and should be re-measured within one before being quoted as a result.

---

## Appendix A — timeline

| date | event |
|---|---|
| 2026-07-24 / 07-27 | 42-dataset benchmark run; results imported (`9da536f`) |
| 2026-07-30 | registration defect found, `s3_warp-B1` |
| 2026-07-31 | round-2 eval layer repaired |
| 2026-08-01 | model-side per-dataset registration dispatch added (`f63bcbf`) |

The benchmark predates every repair by roughly a week.

## Appendix B — reproducing the checks

```bash
cd /resnick/groups/Hippo/ezeng/mf_field

# §3.1 — which datasets had their target resampled
python3 -c "
import json,glob
for f in glob.glob('mf_field/akash/results/raw_full/*.json'):
    d=json.load(open(f)); hn,wg=d.get('hf_grid_native'),d.get('work_grid')
    if hn and wg and hn!=wg: print(d['dataset'],hn,'->',wg)
" | sort -u

# §3.2 — the index-ramp probe, downsample direction
.venv/bin/python -c "
import torch,torch.nn.functional as F
r=torch.arange(512.).view(1,1,1,512)
print(F.interpolate(r,size=(1,256),mode='bilinear',align_corners=False)[0,0,0,:6])
"

# §6 — the duplicate
md5sum mf_field/factory_mffp/data/era5/era5_train_test/test_l9.npz \
       mf_field/factory_mffp/data/pm_test/data/test_l9.npz

# §9 — GPU-hour accounting
python3 -c "
import json,glob,re,os
p=re.compile(r'^(.+?)__(.+)__e(\d+)__s(\d+)\.json$'); t=n=0
for f in glob.glob('mf_field/akash/results/raw_full/*.json'):
    m=p.match(os.path.basename(f))
    if m and m.group(3)=='2500':
        t+=json.load(open(f)).get('train_seconds') or 0; n+=1
print(n,'runs',round(t/3600,1),'GPU-h')
"
```

Nothing in this note was edited into a guarded surface.
`data/`, `eval/`, `baselines/` and the frozen round-1 numbers are untouched.
