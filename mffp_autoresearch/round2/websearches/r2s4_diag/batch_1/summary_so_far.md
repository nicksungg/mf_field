# Summary so far — `r2s4_diag`, batch 1

## Stream question and what batch 1 must do

`project.yaml streams[3]`: "what is the value of LF as a training signal
(matched with/without arms), what does overfitting at N_hf=5 look like, and
where do the training-free floors sit?" Class: `diag`.

program.md §12.4 **pre-directs B1**: (a) verify the frozen floors reproduce
(zero-predictor column included); (b) train ONE minimal condition→HF baseline
(smallest reasonable FiLM-FNO decoder or MLP→field) at smoke tier, seeds
{0,1,2}, on the panel — its per-dataset seed spread REPLACES the provisional
`state/noise_floor.json`. Diagnostic card *with* training; cheap by design.
Later batches: value-of-LF accounting (matched ± LF arms; r2s4 measures,
r2s3 optimizes) and overfitting anatomy at N_hf ∈ {5, 20, 50} (ifc ladder)
and N = 400 (sharp), incl. train/test gap decomposition and effective sample
counts under the **drift-class rule** (`../round1/docs/round1_report.md:95` —
when n_eff/N < 1%, only in-job paired controls are controls).

## Current numeric state (read, not recalled)

`state/anchors/r2s4_diag.json` — launch anchor is the **best-floor panel
geomean 23.063616857615774**, `anchor_type: best_floor_panel_geomean`,
`provisional: false`, source `training_free_floors`, certified
2026-07-31T14:20:17Z. Per-dataset best floors: helmholtz 3.344 (zero), pfc
59.81 (train_mean), allen_cahn 269.20 (nn_condition), fisher_kpp 11.99
(train_mean), cahn_hilliard 23.18 (nn_condition), ifc_poisson 10.05
(nn_condition).

`state/anchors/floors.json` carries all three arms per dataset plus
`nn_index_hist_top5` and `cond_dim`/`n_train_hf`/`n_test`. Two facts already
visible there that shape B1: (i) `ifc_poisson` has `n_train_hf: 5` and its NN
histogram shows all 128 test points collapsing onto 5 train fields
(41/17/20/38/12) — NN-in-condition there is a 5-atom dictionary, so its
"floor" is an artifact of dictionary size, not of condition-space geometry;
(ii) on guards `fluid` (NN skill 0.2048) and `heat_local` the floor ordering
differs from the panel, consistent with program.md §2.3's warning that a guard
"win" below those floors is floor-level.

`state/noise_floor.json` is **provisional** (`_source:
round1-batch0-rescaled`, `_provisional: true`) and derived from
*LF-consuming* families (`mf_fno_transfer_film`, `mf_fno_pinn_transfer`).
Its spreads are wildly heterogeneous: helmholtz spread 10.68 skill units on a
mean skill of 15.22 (70% of the mean), vs allen_cahn spread 0.128 on a mean
of 148.15 (0.09%). The `min_claimable_effect` fields mix two rules (max(spread,
10% of mean)). Per program.md §4.3 these are NOT numeric thresholds until B1
certifies a condition→HF 3-seed spread. **Anything inside the anchor's CI or
below the floor is noise, not signal** — and right now we do not have a
trustworthy CI for this regime at all. That is exactly the gap B1 closes.

## Relevant prior websearch (in-repo, cite don't re-derive)

- `docs/reports/MF_Sharp_HighFreq_Report.md:61-62, 335, 349` — the
  **spectral truncation floor**: for a discontinuity, Fourier coefficients
  decay as k^-1, so a <=12-mode FNO is floored at ~3-10% rel-L2 on shock fields
  regardless of training; a Cahn-Hilliard interface of width eps is floored
  whenever the ladder under-resolves eps. The report already recommends
  plotting "distance-to-floor" (per-family error vs best-possible K-mode
  truncation floor) to split *representation floor* from *model error*. This
  is a fourth floor arm r2s4 should consider alongside NN/mean/zero, and it is
  training-free.
- `docs/reports/MF_Leaderboard_Beaters_2026_Report.md:56, 189, 327` — HF
  scarcity (4-32 HF samples) plus an accuracy floor is the named bottleneck;
  "fewer trainable parameters directly cut HF overfitting" is the report's own
  prescription, and it flags `mf_fno_transfer_film`'s full fine-tune as the
  overfitting-prone reference. Relevant to B1's "smallest reasonable" model
  choice and to the later overfitting-anatomy batch.

## Existing probe library

`tools/` (37 files, seeded verbatim from round 1; header warns they were
written against round-1 eval paths and `registration_audit.py` asserts the OLD
frozen baseline). Directly reusable-after-adaptation for r2s4:
`field_error_decomposition.py` (amplitude vs structure split + per-sample-gain
oracle), `dc_pattern_split.py` (is the score just the DC level? — a
constant-field oracle, i.e. a floor arm in disguise), `lf_at_inference_audit.py`
(does a family actually consume LF at inference — the stripped-view enforcement
analogue), `residual_gain_learnability.py`, `interface_locality_profile.py`,
`paired_arm_displacement.py`, `checkpoint_divergence_audit.py`.

## Open questions this search must inform

1. Is there a **published protocol** for certifying a seed-spread-based
   minimum-claimable-effect in neural-operator / PDE-surrogate benchmarking, or
   is per-benchmark ad-hoc practice the norm? (Determines whether B1's
   certification is a methodological contribution or a hygiene step.)
2. Is the **trivial-baseline panel** (nearest-neighbor-in-parameter,
   train-mean, zero/persistence) already standard for parametric PDE
   surrogates — and has anyone shown published surrogates losing to it?
3. Is there an established **value-of-information / matched-arm accounting**
   framework for *auxiliary training-only* signals (privileged information,
   distillation) that r2s4 should adopt rather than invent?
4. What is the state of the art on **train/test gap decomposition and
   effective sample size** for tiny-N operator learning?
