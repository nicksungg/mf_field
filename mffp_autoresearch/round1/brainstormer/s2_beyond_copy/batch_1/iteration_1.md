# Iteration 1 — Stream `s2_beyond_copy`, Batch 1

## Design context considered

- `summary_so_far.md` §6 unknowns U1–U6 (this directory).
- Prior-art verdict for D1: **`preempted-but-MF-composition-open`** — metrics
  published, *reference* (copy-LF) and *setting* (sharp-2D MF phase-field) open
  (`websearches/s2_beyond_copy/batch_1/report.md`).
- program.md §12.2 (quoted verbatim in `summary_so_far.md` §2), §4.3 (diagnostic
  card = a measurement, no training, single run, no seeds 1–2, `epochs: 0` legal),
  §2.1 (one nRMSE definition; no agent recomputes metrics by hand), §5 immutables.
- Anchor: `state/anchors/s2_beyond_copy.json` → **skill 1.0 = copy-LF**,
  `provisional: false`.
- Noise floor `state/noise_floor.json` (`min_claimable_effect`, skill units):
  helmholtz **9.6950**, allen_cahn **1.6334**, pfc **1.1511**, cahn_hilliard
  **0.5533**, fisher_kpp **0.4177**. `state/gates.md` G3: *"Brainstormers must
  treat helmholtz claims as unfalsifiable at smoke tier unless the design
  addresses the instability itself"*.
- Pre-falsified levers (§5): WNO backbone swap; LF low-mode freezing
  (`mf_fno_spectral`); diffusion prior for point accuracy.
- Assets: batch-0 200-epoch checkpoints at
  `round1/eval/results/<family>/ckpt_<dataset>_e200_s{0,1,2}/last.pt` for
  `mf_fno_transfer_film` and `mf_fno_pinn_transfer`, with the matching recorded
  result JSONs (`<dataset>_e200_s<seed>.json`, containing `rel_l2_per_sample`).
  Both families' `smoke_eval.py` import `finalize_and_write` at module level and
  route all training through a module-level `_train` — i.e. both are
  monkeypatchable for prediction capture and for a "no training happened" tripwire.
  Resume is keyed on `sd["epochs_target"] == args.epochs and sd["grid"] == grid`
  (+ `sd["pinn"]` for pinn_transfer), so calling `run()` with `--epochs 200` and
  the batch-0 `ckpt_dir` loads the finished checkpoint and trains nothing.

### Design-calibration probes I ran myself (NOT reportable results)

To avoid inventing thresholds, I read the raw HF training fields (read-only, no
model, no test split scoring, no eval layer) and measured condition-vector
sufficiency. Exact command shape:

```python
d = np.load(f'mf_field/factory_mffp/data/{ds}/train_l{HF}.npz')   # keys: x, y
xs = (x - x.mean(0)) / x.std(0); D = pairwise(xs); np.fill_diagonal(D, inf)
rel_NN   = ||y - y[argmin_j D]|| / ||y||          # nearest-X-neighbour, LOO
rel_rand = ||y - y[perm]|| / ||y||                 # random-pair control
rel_mean = ||y - y.mean(0)|| / ||y||               # mean-field control
```

Medians over the 400 training samples:

| dataset | cond dim | NN-in-X | random pair | mean field | copy-LF (test, eval/copylf_baselines.json) | certified model (batch 0) |
|---|---|---|---|---|---|---|
| `sharp__fisher_kpp_2d` | 2 | **0.336** | 0.359 | – | 0.0626 | 0.261 |
| `sharp__allen_cahn_2d` | 3 | **0.292** | 1.447 | – | 0.0162 | 0.264 |
| `sharp__phase_field_crystal_2d` | 2 | **0.019** | 0.808 | – | 0.0448 | 0.515 |
| `sharp__cahn_hilliard` | 19 | **1.216** | 1.405 | 0.999 | 0.0877 | 0.488 |
| `ext__helmholtz_2d` | 3 | **0.551** | 1.308 | 4.015 | 0.3295 | 3.01–6.20 |

These are hand-computed and therefore **not reportable under program.md §2.1**;
they exist only to calibrate the card's predictions and falsification thresholds,
and they are recorded here so the card's expectations are auditable rather than
invented. Three things they suggest (all to be *properly* measured by the card,
train→test, through `eval/nrmse.py`):

1. On `fisher_kpp` the nearest-X-neighbour field is no better than a random other
   sample (0.336 vs 0.359) — the condition vector carries almost no information
   about the realization, and the certified model (0.261) sits *at* that floor.
2. On `allen_cahn` the same pattern holds with a weaker degeneracy (0.292 vs
   1.447 random) — again the certified model (0.264) sits at the X-only floor.
3. On `pfc` the opposite: a trivial 1-NN-in-X lookup gives 0.019, **better than
   copy-LF (0.0448)**, while the certified model gives 0.515 — 27× worse than the
   lookup. Here the information is in X and the model fails to use it.

So the panel is not one failure mode, and no purely spectral diagnostic could
have told them apart.

## Proposal reasoning (alternatives weighed and rejected)

**A1 — the literal §12.2 first suggestion: a per-band + interface-distance error
decomposition of the certified models vs copy-LF, and nothing else.** Rejected as
*insufficient*, kept as components M3/M4. It presupposes the failure is a
localization; the calibration probes show that on ≥2 datasets the certified model
is at the X-only information ceiling, which no spectral or spatial decomposition
of the error can reveal (both would report "excess everywhere", an uninformative
"uniform" verdict — exactly the §12.2 falsification branch — without saying why).

**A2 — LF-permutation feature importance on the certified families** (the
websearcher's mechanism (a) protocol). Rejected as *vacuous for these two
families*: reading their eval loops, no LF tensor enters the forward pass, so the
permutation Δ is identically zero by construction and proves nothing a reader
could not dispute. Replaced by **M1, a forward-hook input audit** that mechanically
records every tensor entering the model at eval and asserts whether any
field-shaped `(B, ·, H, W)` tensor appears. Same claim, dynamic proof, near-zero cost.

**A3 — include an LF-consuming family (`transolver_residual`, best-in-zoo on 4 of
5 beyond-copy datasets per §12.4) by training it inside this card.** Rejected:
that is *training*, which §4.3 forbids for a diagnostic card, and it costs ~44 min
× 5 datasets on p100 (`state/timing_ledger.json`). It is the natural **batch-2
model card**, and this diagnostic is what tells us whether to point it at the
information problem (bind an identity-to-LF path, D2) or the representation
problem (pfc). Recorded as the batch-2 successor in the report.

**A4 — skip to the §12.2 data-defect branch and write the dataset bug report
now.** Rejected as premature and, on the evidence, wrong in its likely form: the
copy-LF errors are tiny (allen_cahn 0.0162), so LF↔HF pairing is not grossly
broken. The real candidate defect is different — the *condition vector omits the
IC* on 3 of the 5 datasets, for which the repo already contains the precedent
fix (`sharp__cahn_hilliard/meta.json`: *"IC-encoded cond (low Fourier modes) so
field=f(x) is learnable; fixes rel-L2>1 bug"*). That is a claim about a data
design decision and must be *measured on the scored test split through the eval
layer* before it goes to the mentor. The card therefore keeps the branch live via
M2 (degeneracy statistic) and M5b (aligned-vs-cross-pair coherence control) and
routes the recommendation, if it fires, through card part 7 — a written
recommendation, never an action (§13.4).

**A5 — run the analysis as a standalone script instead of a contract family.**
Rejected: §2.1 requires every score to flow through `eval/nrmse.py`, and §5.5
fixes the contract CLI as the only execution seam. Packaging the diagnostic as a
contract family additionally buys a free seam check (below) and gets the headline
number into the standard result JSON the initial-analyzer already parses.

**A6 — propose D3 (band-split / hard low-band constraint) now.** Rejected
explicitly: the websearch verdict gates it (*"Do not propose D3 (band-split)
before D1 reports"*) and it is adjacent to the pre-falsified `mf_fno_spectral`
LF-low-mode-freezing lever (§5). M3's low-band ratio is designed to be the gate.

**Reference-model choice inside the family.** Two candidates for the family's
*scored* `test_hf` split: (i) copy-LF passthrough, giving skill exactly 1.000 as a
seam check, or (ii) the training-free 1-NN-in-X predictor, giving a real panel
skill line for a predictor nobody has ever scored. Chose **(ii)**, because the
calibration probes say it is the single most consequential number in the card
(pfc ≈ 0.4 ⇒ a training-free predictor beating copy-LF, i.e. success criterion 2
on one dataset, by lookup), and it must be produced by `score_panel.py` itself to
be reportable. The copy-LF seam check is preserved as an internal assertion:
the family recomputes copy-LF via `eval/panel_data.copylf_prediction` and
**hard-stops** unless its nRMSE matches `eval/copylf_baselines.json` to ≤1e-9.
All other predictors go to non-`test*` split keys (`ref_*`), which
`score_panel._extract_test_metric` ignores, so no ambiguity error.

## Proposal

- **Category**: `diagnostic / copy-LF excess-error forensics`
- **Card type**: `diagnostic` (no training; `epochs: 0`; single run, no seeds 1–2)
- **Motivation**: the websearch prior-art verdict for D1 is
  **`preempted-but-MF-composition-open`**, whose "what remains open" cell reads:
  *"(1) **The reference**: no fetched source decomposes error relative to the
  model's own LF input; 2604.20061 names the missing coarse-solution baseline as
  'a notable gap' in its own field. (2) **The setting**: 2604.20061's example is
  KS (the smooth control); 2510.17887 is single-fidelity shock flow — neither is
  sharp-2D **multi-fidelity** phase-field. (3) **The joint decomposition**: no
  source combines spectral banding + interface stratification + LF-input
  attribution on one LF/model/HF triple."* §12.2 pre-directs batch 1 to be exactly
  this diagnostic, and §4.5's noise-floor rule plus §2.1's single-definition rule
  mean the hand-probes above cannot stand as results.

### Concrete config

New contract family `models_r1/s2_copylf_forensics/` (manifest.json +
smoke_eval.py + INSPIRATION.md), run by `eval/score_panel.py` with `--epochs 0`,
`--seed 0`, over the five beyond-copy datasets (`ifc_poisson` excluded: its test
split ships no LF, reference is the paper bar — ADR 0002). Per dataset it:

- Derives the main-repo root from `--dataset_dir` (`dataset_dir.parents[3]`) and
  imports, read-only: `round1/eval/{nrmse,panel_data}.py`,
  `factory_mffp/data_adapters`, and the base families' modules under
  `factory_mffp/models/<family>/`.
- **M1 — LF-blindness audit (forward-hook).** For each base family × batch-0 seed:
  register a `forward_pre_hook` on the top-level model, invoke the base family's
  own `run()` with `--epochs 200` and `--ckpt_dir <S2B1_CKPT_ROOT>/<family>/ckpt_<ds>_e200_s<seed>`,
  and record every input tensor's shape. Emits
  `lf_at_inference: bool` (true iff any input has ndim ≥ 3 with the working-grid
  spatial shape). **Tripwire**: the family's module-level `_train` (and
  `_train_pinn`) are monkeypatched to `raise` — if resume did not take, the run
  aborts instead of silently training. **Provenance**: `sha256` + mtime of each
  `last.pt` recorded; predictions captured by monkeypatching the module-level
  `finalize_and_write`; the reproduced per-sample rel-L2 mean must equal the
  recorded batch-0 value in `<ds>_e200_s<seed>.json` to ≤1e-9 or the run aborts.
- **M2 — X-sufficiency ladder** (training-free, fit on the 400 HF train fields,
  evaluated on the 100 HF test fields, every number through `eval/nrmse.py`):
  1-NN-in-X (**the scored `test_hf` split**), k-NN-in-X for k ∈ {3,5,10}
  (`ref_knn{k}`), global mean field (`ref_meanfield`), copy-LF (`ref_copylf`,
  asserted == `copylf_baselines.json` to ≤1e-9), and the two certified models'
  reloaded predictions (`ref_model_<family>_s<seed>`). X is z-scored with train
  statistics; ties broken by index; no hyperparameter is tuned on test.
  Degeneracy statistic on the train split: median NN-in-X field disagreement vs
  random-pair and vs mean-field control.
- **M3 — spectral banding of the excess error.** Radial wavenumber bands (4 dyadic
  bands over the working grid); per band and per predictor: `||e_b||²` share,
  ratio `R_b = ||e_b(model)||² / ||e_b(copy-LF)||²`, amplitude transfer
  `H_b = <û_pred, û_hf>/<û_hf, û_hf>` (2606.03936 convention), and LF/HF magnitude-
  squared coherence per band (2605.26412 convention).
- **M4 — interface stratification.** Distance-to-interface from the HF field
  (phase fields: `|u| < τ` with τ = 0.1·max|u|; general fallback: top-decile
  `|∇u|`), Euclidean distance transform, 4 distance strata; error-mass share per
  stratum for model and copy-LF (2510.17887 convention).
- **M5 — amplitude/pattern split + pairing control.** (a) per test sample the
  optimal scalar `α_i = <pred,hf>/<pred,pred>`; report nRMSE before and after
  optimal rescale (separates normalization/amplitude failure from pattern
  failure — targets the helmholtz divergence and the QuadNorm mechanism,
  2605.07375). (b) aligned LF↔HF rel-residual vs cross-pair (index-shuffled)
  control, the §12.2 data-defect check.
- Writes the contract JSON (`model`, `dataset`, `splits.test_hf` + `ref_*`) plus a
  sidecar `diagnostics_<dataset>.json` carrying M1–M5 and `nrmse_def_hash`, under
  `${S2B1_DIAG_OUT}`.

### Recipe

```json
{
  "base_family": "mf_fno_transfer_film",
  "base_commit": "967562e2a4e3493515edab36b0fcb23655fce71f",
  "family_dir": "models_r1/s2_copylf_forensics",
  "datasets": "ext__helmholtz_2d,sharp__phase_field_crystal_2d,sharp__allen_cahn_2d,sharp__fisher_kpp_2d,sharp__cahn_hilliard",
  "epochs": 0,
  "seeds": [0],
  "env": {
    "S2B1_BASE_FAMILIES": "mf_fno_transfer_film,mf_fno_pinn_transfer",
    "S2B1_CKPT_ROOT": "mffp_autoresearch/round1/eval/results",
    "S2B1_CKPT_EPOCHS": "200",
    "S2B1_CKPT_SEEDS": "0,1,2",
    "S2B1_KNN_K": "1,3,5,10",
    "S2B1_BANDS": "4",
    "S2B1_INTERFACE_TAU": "0.1",
    "S2B1_DIAG_OUT": "mffp_autoresearch_outputs/round1/s2_beyond_copy/B1/eval"
  }
}
```

`base_commit` = `round1-substrate` HEAD (`git rev-parse round1-substrate`).
`S2B1_CKPT_ROOT` and `S2B1_DIAG_OUT` are repo-root-relative and resolved against
the root derived from `--dataset_dir`, so the worktree (which has no `data/`
symlinks — they are git-ignored) never needs them. Contract-tier plumbing check:
same command on `ext__helmholtz_2d` only (96², fastest, checkpoints present).
Walltime: no analog in `state/timing_ledger.json` for an inference-only job;
estimate 30–60 min for all five datasets (batch-0 *training* runs were 44 min per
dataset-seed), so the rules' default `04:00:00` is right with ample headroom.

### Expected outcome

No panel metric "moves" — a diagnostic measures. Predicted values (calibrated on
the probes above; the card's job is to produce them properly, train→test, through
`eval/nrmse.py`):

- **M1**: `lf_at_inference = false` for `mf_fno_transfer_film` and
  `mf_fno_pinn_transfer` on all 5 datasets × 3 seeds — the certified champions are
  structurally LF-blind at test time. (Confidence high; from reading their eval
  loops.)
- **M2 (headline, scored)**: 1-NN-in-X skill ≈ **5.4** on fisher_kpp (certified
  4.18), **18** on allen_cahn (16.33), **0.42 on pfc** (certified 11.51 — a
  training-free lookup *beating copy-LF*, i.e. skill < 1 on one beyond-copy
  dataset), **≈14** on cahn_hilliard (5.53, where 19-D X-space makes 1-NN worse
  than the trained model), **≈1.7** on helmholtz (certified 13.82).
  Interpretation: on fisher_kpp and allen_cahn the certified models sit within
  ~1 skill unit of a trivial X-only lookup — 200 epochs of FNO training buys
  almost nothing over table lookup, and the whole X-only regime is bounded far
  from copy-LF because the condition vector does not determine the realization.
- **M3**: `R_low > 1` (excess over copy-LF present even in the lowest band) on
  ≥4 of 5 datasets — i.e. the failure is *not* a high-k blur; low-k structure is
  already the wrong realization. This is the gate that would forbid D3.
- **M4**: error-mass share roughly proportional to stratum area (uniform), i.e.
  the §12.2 "concentrated in X" framing is expected to be **falsified** for the
  spatial axis on the information-limited datasets, and expected to *hold*
  (interface-concentrated) on pfc, where the model is far above its X-only floor.
- **M5**: on helmholtz, optimal-rescale nRMSE ≪ raw nRMSE would localize the
  divergence to amplitude/normalization; aligned-vs-cross-pair residual ratio
  ≪ 1 on all 5 datasets ⇒ pairing sound, no dataset bug of that kind.

### Expected falsification

**H1** ("the copy-LF gap is a conditioning-sufficiency dichotomy, not a single
localized model defect") is falsified if any of: the training-free X-only floor
fails to track the certified models where H1 says it should — `|skill(best
training-free X-only predictor) − skill(certified best family)| > 2.0` skill units
on `sharp__allen_cahn_2d` (floor 1.6334) or `> 1.0` on `sharp__fisher_kpp_2d`
(floor 0.4177); or the pfc excess `skill(certified 11.511) − skill(1-NN-in-X)` is
`< 5.0` skill units (floor 1.1511), which would mean pfc is *not* a
representation failure; or the low-band ratio `R_low ≤ 1.0` on ≥3 of the four
low-floor datasets across all three batch-0 seeds, which would relocate the
failure to high-k spectral localization and license the band-split (D3) direction
for batch 2. `ext__helmholtz_2d` carries **no numeric claim** (floor 9.6950 makes
any smoke-tier skill claim there unfalsifiable, `state/gates.md` G3); it is
reported descriptively only, and M5a is the one design element that addresses its
instability directly.

### Anchor reference

`null` — `s2_beyond_copy` is a gap stream; its own-stream anchor (copy-LF skill
1.0, `state/anchors/s2_beyond_copy.json`) is implicit (program.md §4.5).

## Immutables self-check (10 items, positive evidence)

1. **Data read-only** — the family opens datasets exclusively through
   `factory_mffp/data_adapters.load_mf_dataset` / `eval/panel_data.load_split`,
   both read-only loaders; no `np.save`/`open(...,'w')` targets any path under
   `data/`; N_hf is untouched (400 train / 100 test per `meta.json`); the LF used
   is the shipped highest-LF real coarse solve via `copylf_prediction`, never a
   downsample of HF. **PASS**
2. **Panel + guard set fixed** — the run covers exactly the five beyond-copy panel
   datasets named in `project.yaml panel` (minus `ifc_poisson`, which has no
   copy-LF reference per ADR 0002 and is out of this stream's scope); nothing is
   added, and the guard set is not touched because this card makes no panel-win
   claim. **PASS**
3. **Eval layer / spec untouched** — the family only *imports* `eval/nrmse.py` and
   `eval/panel_data.py` and *reads* `eval/copylf_baselines.json` and
   `eval/results/*/ckpt_*/last.pt`; all writes go to `models_r1/` in the worktree
   and to `${S2B1_DIAG_OUT}` under `mffp_autoresearch_outputs/`. No edit to
   `round1/eval/`, `project.yaml`, `program.md`, ADRs or subagent prompts is
   required for anything above. **PASS**
4. **One nRMSE definition** — every reported number is produced by
   `eval/nrmse.py::nrmse`; the sidecar records `NRMSE_DEF_HASH`; the family trains
   nothing, so there is no training loss at all. **PASS**
5. **Contract CLI fixed** — `smoke_eval.py` exposes exactly
   `--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed` and writes
   `model`/`dataset`/`splits.test_hf.nRMSE`; all eight knobs are env variables
   listed verbatim in `recipe.env`, which `score_panel.code_hash` folds into the
   cache key. **PASS**
6. **Seeds and tier epochs fixed** — `seeds: [0]` with `epochs: 0`, which
   §4.3 explicitly legalizes for diagnostics ("no seeds 1–2; `recipe.epochs = 0`
   is legal"); the {0,1,2} seed protocol is honoured on the *model* side by
   analyzing all three certified batch-0 checkpoints, and no new epoch budget is
   introduced (the 200 in `S2B1_CKPT_EPOCHS` selects existing batch-0 artifacts).
   **PASS**
7. **Guarded factory surfaces untouched** — `factory_root/{eval,baselines,
   references,scripts,data}`, `factory.md` and `akash/**` are only read (module
   import of `models/<family>/smoke_eval.py`, dataset loading); the monkeypatches
   (`_train`, `finalize_and_write`) are applied to the *imported module object at
   runtime*, mutating no file on disk, and `models/` is not in the guarded list
   anyway. **PASS**
8. **Checkpoint-resume from `<ckpt_dir>/last.pt`** — trivially satisfiable because
   nothing is trained: the family's own `run` is idempotent and re-runnable; it
   additionally *depends* on the batch-0 `last.pt` resume path in the base
   families and hard-stops with a specific message if `last.pt` is absent or its
   `epochs_target`/`grid` do not match, rather than retraining. **PASS**
9. **Threshold vs noise floor** — thresholds are stated in skill units and each
   exceeds its dataset's `min_claimable_effect`: allen_cahn 2.0 > **1.6334**,
   fisher_kpp 1.0 > **0.4177**, pfc 5.0 > **1.1511**; cahn_hilliard carries no
   threshold (descriptive only, floor **0.5533**); `ext__helmholtz_2d` is
   explicitly excluded from numeric claims because its floor is **9.6950**
   (diverging seed, `state/gates.md` G3). The scored quantities in the clause
   (1-NN-in-X, copy-LF) are deterministic and seed-free by construction, so the
   floor is a conservative bound on them; the model-side quantity `R_low` is
   required to hold across all three batch-0 seeds. **PASS**
10. **Not a pre-falsified lever** — nearest pre-falsified lever is **LF low-mode
    freezing (`mf_fno_spectral`)**. Difference: this card *builds nothing and
    freezes nothing*; it measures whether the LF low band is even accurate, and
    the websearch verdict makes that measurement the precondition for ever
    proposing band-split (D3). If M3 returns `R_low > 1` the card actively
    forbids the lever's re-proposal rather than repeating it. **PASS**

## Status

- Slot **covered** (one proposal, `card_type: diagnostic`, as pre-directed by
  program.md §12.2).
- Skipped: no.
- Reopen candidates resolved: none exist (no prior cards in this round).
- Immutables self-check: **pass (10/10)** on iteration 1; no revision needed.
