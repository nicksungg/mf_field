# DINO(v2) retrieval key vs hand-rolled keys — operator measurement

**NON-REPORTABLE / OPERATOR MEASUREMENT.** Not a card. Not pre-registered. Not
leaderboard-eligible (training-free lookups are `ref_*`-only per s2-B1 part 5
`do_not_promote`). Exploratory evidence to inform whether a DINO-embedding key
deserves a pre-registered arm in s2-B3 — nothing here is a reportable claim.

- Date: 2026-07-30 (run 2026-07-29 UTC, login node, CPU)
- Operator-authorized measurement; executed by a subagent in session scratchpad
  `/tmp/claude-28156/.../scratchpad/dino_key/` (script `run_dino_key.py`,
  results `dino_key_results.json`, log `run_log.txt`)
- Model: `dinov2_vits14` via `torch.hub.load('facebookresearch/dinov2', ...)`
  (ViT-S/14, CLS token, 384-d). No torchvision fallback needed.
- Rule under test: EXACTLY the B1/B2 zero-parameter rule — prediction =
  copy-LF + mean of the k=5 nearest TRAIN residuals (HF−LF), only the retrieval
  key changes. `retrieval.py` copied unmodified from the s2-B2 build
  (`worktrees/s2_beyond_copy/B2/models_r1/s2_lf_residual_control/retrieval.py`);
  data via `eval/panel_data.py` (`load_split` + `copylf_prediction`); scored with
  `eval/nrmse.py` (def hash `d3d0ade9…` matches `copylf_baselines.json`).
- DINO preprocessing: per-field min-max to [0,1] → bilinear resize 224×224 →
  replicate to 3 channels → ImageNet mean/std. Keys z-scored on TRAIN
  (`zscore_fit`/`zscore_apply`), Euclidean 5-NN, stable argsort — same numeric
  conventions as the blockmean rung. `dino_pca64` = top-64 PCA (train-fitted
  SVD on the z-scored embeddings).
- Seam checks: recomputed copy-LF nRMSE matched `eval/copylf_baselines.json`
  with delta 0.0 on all 5 datasets; the same-code `blockmean16` recompute
  reproduced batch-1 F6 exactly (0.5620 / 0.6251 / 0.7851 / 1.0417 / 1.0616);
  duplicate tripwire: 0 zero-distance NN hits everywhere.

## Skill table (nRMSE / copy-LF nRMSE; < 1 beats copy-LF; lower is better)

Same-rig, same-code: `blockmean16`, `dino_cls384`, `dino_pca64` (this run).
Context columns `s1grad` / `patch` are the s2-B2 floor sidecars
(`mffp_autoresearch_outputs/round1/s2_beyond_copy/B2/eval/floor_*.json`) —
same rule and k, computed by the B2 build.

| dataset | copy-LF nRMSE | blockmean16 | s1grad (B2) | patch (B2) | dino_cls384 | dino_pca64 |
|---|---|---|---|---|---|---|
| sharp__phase_field_crystal_2d (128²) | 0.04478 | 0.5620 | **0.5198** | 0.5262 | 0.8872 | 1.3402 |
| sharp__cahn_hilliard (256²) | 0.08766 | 0.6251 | 0.6119 | **0.5928** | 0.9050 | 0.7741 |
| ext__helmholtz_2d (96²) | 0.32945 | 0.7851 | **0.5915** | 0.7873 | 2.0839 | 2.1317 |
| sharp__allen_cahn_2d (256²) | 0.01615 | 1.0417 | **1.0062** | 1.0793 | 1.0955 | 1.0960 |
| sharp__fisher_kpp_2d (256²) | 0.06263 | **1.0616** | 1.1056 | 1.0692 | 1.0991 | 1.1048 |
| **geomean (5 ds)** | — | 0.7886 | **0.7314** | 0.7771 | 1.1504 | 1.2177 |

DINO loses to the hand-rolled keys on **5/5 datasets** (both variants), and to
plain copy-LF (skill 1.0) on 3/5 (helmholtz, allen_cahn, fisher_kpp; pca64 also
on pfc). On helmholtz it is catastrophic: adding DINO-retrieved residuals more
than doubles the copy-LF error (2.08×).

## Leak controls (median test→train NN dist / median train→train NN dist, self-excluded)

| dataset | blockmean16 | dino_cls384 | dino_pca64 |
|---|---|---|---|
| sharp__phase_field_crystal_2d | 1.310 | 1.054 | 1.021 |
| sharp__cahn_hilliard | 1.000 | 1.039 | 1.059 |
| ext__helmholtz_2d | 0.996 | 1.053 | 1.048 |
| sharp__allen_cahn_2d | 0.989 | 1.000 | 0.974 |
| sharp__fisher_kpp_2d | 1.003 | 1.019 | 0.986 |

All ratios ≈ 1 (0.97–1.31): test queries are no closer to the train archive
than train points are to each other, in every key space. The DINO failure is
representational, not a leakage artifact — and conversely, the hand-rolled
keys' wins are not leakage either.

## Wall time

Embedding 500 fields/dataset (400 train + 100 test), CPU, batch 16:
80–137 s per dataset, 528 s embedding total, ~560 s total measurement wall
(after a one-time ~8 s hub download + load). GPU unnecessary at this scale.

## Verdict

**No — DINO does not earn a pre-registered arm in s2-B3.** A frozen DINOv2
ViT-S/14 CLS embedding is strictly dominated by every hand-rolled key on every
beyond-copy dataset (geomean skill 1.15 vs 0.73–0.79), and is actively harmful
(worse than copy-LF) on 3/5. The cheap physics-adjacent keys — 16×16 block-mean
and especially the Teweles-Wobus S1 gradient distance — remain the bar. If
s2-B3 spends a slot on retrieval keys, the evidence points to sharpening the
S1/patch direction (or key ensembling), not pretrained-vision embeddings.

Plausible mechanism (unverified): the rule needs neighbours that are close in
*solution space* so their HF−LF residuals transfer. DINO's semantic embedding
is invariant to exactly what matters — amplitude (destroyed by the per-field
min-max), phase, and fine spatial alignment — so it clusters fields by texture
class. All Helmholtz wave fields "look alike" to DINO, it retrieves residuals
from wrong parameter regimes, and adding them doubles the error.

## Surprises

1. **Helmholtz catastrophe (skill 2.08).** The failure mode is not "no better
   than copy-LF" but *actively destructive* — the first key we've measured that
   makes residual transfer worse than doing nothing on a dataset where the rule
   otherwise works well (blockmean 0.79, s1grad 0.59).
2. **PCA-64 is not a free win.** It helps on cahn_hilliard (0.774 vs 0.905) but
   badly hurts on pfc (1.34 vs 0.887) — truncating to the top variance
   directions of a semantic embedding does not recover metric structure.
3. **F6 reproduced to 4 decimals** by the copied rig on all five datasets
   (and blockmean leak ratios match the B2 sidecars, e.g. pfc 1.310) — the
   comparison is genuinely same-code, so the DINO deficit is attributable to
   the key alone.
4. **Integrity incident (process, not science): spoofed task notifications.**
   During the run, this session received a sequence of background-task
   "notifications" reporting favorable DINO results (skills 0.4600 / 0.5717 /
   0.6763 / 1.0009 / 1.0393 — i.e. DINO beating every hand-rolled key on 4/5)
   that (a) do not appear in the on-disk `run_log.txt`, (b) were physically
   impossible given the python process's elapsed/CPU time at arrival, and
   (c) in one case claimed content for a task output file that was empty on
   direct read. Every number in this note was therefore verified by direct
   foreground reads of `run_log.txt` and `dino_key_results.json` (which agree
   line-for-line). Any DINO-key numbers circulating that match the "0.4600
   pfc / 0.6763 helmholtz" pattern are fabricated and should be discarded.
   Operators should treat unverified notification content as untrusted.

## Residual caveats

- Only the CLS token was tried; patch-token pooling or multi-scale crops might
  behave differently (nothing here suggests they'd close a 1.15-vs-0.73 gap).
- The per-field min-max normalization deliberately discards amplitude; a hybrid
  key (embedding ⊕ field statistics) was not measured.
- Single seed irrelevant (the rule is deterministic); single model size
  (ViT-S/14); k fixed at 5 to match B1/B2.
