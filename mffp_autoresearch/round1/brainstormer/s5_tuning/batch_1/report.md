# Brainstormer Report — Stream `s5_tuning`, Batch 1

**Stream**: s5_tuning
**Batch**: 1
**Total iterations**: 1
**Slot filled**: 1 / 1
**Reopen candidates resolved**: 0 (none existed)

## Slot

- **Category**: `tuning_spectral_bandwidth`
- **Card type**: `model`
- **Motivation**: F22 (`modes_cap = 12` never scales with resolution — 12 of 128 modes at
  256²) with candidate M1's proposed 32, measured on the certified champion
  `mf_fno_transfer_film`. This is the card program.md §12.5 pre-directs
  (*"G4's dry-run card (`s5_tuning-B1`, modes_cap 12→32 on the champion) is a REAL
  batch-1 card for this stream."*) and the one `state/gates.md` G4 is PENDING on. The
  websearcher's prior-art verdict licenses it as a **measurement, not a novelty claim**:
  *"`modes_cap` 12 -> 32 is therefore a measurement of this project's own spectral
  bottleneck (F22), not a mechanism contribution — which is exactly what a `tuning`-class
  card should be, and it stays inside §12.5 (a hyperparameter, not a new
  mechanism/architecture)."* Four streams currently reason under the unexamined
  assumption that a 9.4%-of-Nyquist truncation is part of why fusion loses to copy-LF;
  one 3-seed run confirms or removes that assumption for all of them.
- **Concrete config**:
  1. Copy `mf_field/factory_mffp/models/mf_fno_transfer_film/` (substrate commit
     `967562e`, tree `5f62eaa`) into `<worktree>/models_r1/mf_fno_transfer_film_modes/`;
     rename in `manifest.json` and in the `finalize_and_write(model=...)` string.
  2. Fix the relocated import root: `REPO_ROOT = HERE.parents[1] / "mf_field" /
     "factory_mffp"` (the current `HERE.parent.parent` at smoke_eval.py:37 resolves to the
     worktree root from `models_r1/<family>/` and would fail to import `data_adapters`).
  3. Only behavioural change: `SMOKE["modes_cap"] = int(os.environ.get("MFFP_MODES_CAP",
     12))` — default 12 must reproduce the anchor path exactly.
  4. Record `modes_cap` and `modes: [modes_h, modes_w]` in the result JSON `extra`
     (audit that the knob fired: `n_params` must go 4,773,953 -> ~3.36e7, ratio
     32·32/12·12 = 7.11 on the spectral weights); write test predictions to
     `<ckpt_dir>/preds_test.npz` for the mechanism-analyzer's per-band probe.
  5. Add periodic in-training checkpointing to `<ckpt_dir>/last.pt` (stage, epoch,
     model/opt/sched/generator state) with the no-preemption path numerically identical
     to the anchor's (slurm_rules §5: restart-from-epoch-0 after requeue is an ALGO bug).
  6. Contract-tier gate before any submit (login node, 2 epochs, seed 0): (a) default
     (env unset) on `ext__helmholtz_2d,ifc_poisson` must match the untouched factory
     family — the equivalence proof that licenses comparing against the batch-0 anchor;
     (b) `MFFP_MODES_CAP=32` on the same two, reporting `modes [32,32]`; (c)
     `--datasets guard --epochs 2 --seed 0` with the arm's env (§2.3, required before any
     panel-win claim).
  7. SLURM: one job per seed, `--datasets panel --epochs 200 --env MFFP_MODES_CAP=32`
     mirroring `recipe.env` exactly; `--time 08:00:00` (cap-12 panel = 154 min/seed in
     `state/timing_ledger.json`; the spectral einsum is 7.1× but FFT-dominated, expect
     1.3–2.5×).
- **Recipe**:
```json
{
  "base_family": "mf_fno_transfer_film",
  "base_commit": "967562e2a4e3493515edab36b0fcb23655fce71f",
  "family_dir": "models_r1/mf_fno_transfer_film_modes",
  "datasets": "panel",
  "epochs": 200,
  "seeds": [0, 1, 2],
  "env": {"MFFP_MODES_CAP": "32"}
}
```
- **Expected outcome**: metric = 3-seed mean panel geomean skill vs the certified anchor
  **6.703** [6.219, 7.102] (`state/anchors/s5_tuning.json`), with the mandatory
  per-dataset skill table.

  | dataset | anchor skill | noise floor | predicted at cap 32 |
  |---|---|---|---|
  | `sharp__allen_cahn_2d` | 16.334 | 1.633 | 15.0–16.5 |
  | `sharp__fisher_kpp_2d` | 4.177 | 0.418 | 3.9–4.3 |
  | `sharp__cahn_hilliard` | 5.534 | 0.553 | 4.6–5.7 (widest prior; E-UNO) |
  | `sharp__phase_field_crystal_2d` | 11.511 | 1.151 | 10.8–11.8 |
  | `ifc_poisson` | 1.566 | 0.240 | 1.6–2.0 (**worse** — cap 32 = full 64² spectrum from N_hf=5) |
  | `ext__helmholtz_2d` | 13.817 | **9.695 (ALERT)** | uninterpretable; no claim made |
  | **panel geomean** | **6.703** | **0.884 derived** | **6.3–7.0 (null most likely)** |

  Δ vs anchor: predicted |Δ| < 0.884 (13.2%), i.e. **below** the geomean floor -> the
  most likely reportable finding is the null "the panel gap is not spectral bandwidth"
  (the websearch report's item 2 explicitly frames that as the genuine outcome).
  Runner-up outcome: cahn_hilliard improves > 0.553 while ifc_poisson degrades > 0.240 —
  a bandwidth-vs-sample-count split that sets batch 2 (capacity-matched `C=24, K=32`).
  **Every quoted threshold clears its dataset's floor**: the geomean threshold equals the
  measured anchor seed spread 0.884 (= max(0.884, 0.10×6.703)); per-dataset thresholds
  are `state/noise_floor.json`'s certified `min_claimable_effect` values verbatim.
- **Expected falsification**: If the cap-32 arm's 3-seed mean panel geomean skill is not
  at least 0.884 skill units below the certified anchor 6.703 (i.e. not <= 5.819) AND no
  stable panel dataset improves by more than its own `min_claimable_effect`
  (`sharp__phase_field_crystal_2d` 1.151, `sharp__allen_cahn_2d` 1.633,
  `sharp__fisher_kpp_2d` 0.418, `sharp__cahn_hilliard` 0.553, `ifc_poisson` 0.240), then
  F22's `modes_cap` is NOT the champion's bottleneck and the panel gap is not spectral
  bandwidth.
- **Prior-art verdict quoted** (verbatim from
  `websearches/s5_tuning/batch_1/report.md`, "For the brainstormer" item 1):
  > **PRIOR-ART VERDICT: not novel, and must not be claimed as such — but legitimate as a
  > measurement.** The mode-count question is published prior art: **iFNO**
  > (https://arxiv.org/abs/2211.15188, verified first-hand this run) grows K during
  > training and gets **10% lower error with 20% FEWER modes**; **AFNO** sparsifies modes;
  > **MG-TFNO** factorizes them. `modes_cap` 12 -> 32 is therefore a *measurement of this
  > project's own spectral bottleneck* (F22), not a mechanism contribution — which is
  > exactly what a `tuning`-class card should be, and it stays inside §12.5 (a
  > hyperparameter, not a new mechanism/architecture).

  Card `prior_art` should therefore read `verdict: "preempted-pivoted"` with citations:
  https://arxiv.org/abs/2211.15188 (iFNO), https://arxiv.org/abs/2404.07200 (spectral
  bias / SpecB-FNO), https://arxiv.org/html/2310.00120 (MG-TFNO),
  https://arxiv.org/html/2509.01293v3 (E-UNO, source paper of `sharp__cahn_hilliard`),
  https://arxiv.org/html/2506.19396 (muTransfer-FNO, the LR-shift confound),
  https://arxiv.org/pdf/2311.05967 and https://arxiv.org/pdf/2402.11568 (mode-count
  plateau / overfitting ablations).
- **Immutables self-check**: **pass (10/10)** on the first pass — each item carries
  positive file/line evidence in
  [iteration_1.md](iteration_1.md) §"Immutables self-check". Item 9 (floor) and item 10
  (pre-falsified levers: nearest is LF low-mode freezing `mf_fno_spectral`, which *froze*
  low modes as a fusion mechanism — this card freezes nothing and adds no mechanism) are
  spelled out there with numbers.
- **Anchor reference**: `null` (program.md §4.5: gap/lever/batch-1 cards judge against
  the own-stream certified anchor; the `card_id` form applies from `s5_tuning` batch >= 2).
- **Source iteration**: [iteration_1.md](iteration_1.md)

## Reopen candidates

| Candidate | Verdict (retry/drop) | Eased conditions | Source iteration |
|---|---|---|---|
| (none — `experiment_cards/` holds only `.gitkeep` and `SCHEMA.md`; this is the round's first card) | n/a | n/a | [iteration_1.md](iteration_1.md) |

## Skipped slot

Not applicable — the slot is filled.

## Summary table

| Slot | Category | One-liner | Status |
|---|---|---|---|
| 1 | `tuning_spectral_bandwidth` | `modes_cap` 12 -> 32 on the certified champion `mf_fno_transfer_film` via a single recorded env knob, panel @ 200 epochs, seeds {0,1,2}, judged against the batch-0 anchor 6.703 with a 0.884-unit geomean threshold | filled (`model`) |

## Notes carried forward (for batch 2 / other streams)

1. **Conditional batch-2 branch**: if cap 32 loses, batch 2 = cap 32 + muP-rescaled LR
   (arXiv:2506.19396; sqrt(log12/log32) = 0.847 -> lr_pretrain 8.5e-4, lr_finetune 2.5e-4)
   to rule out mis-tuning; if cap 32 wins, batch 2 = capacity-matched `hidden_channels=24`
   at cap 32 to separate bandwidth from the 7.1× parameter increase.
2. **Leading independent s5 candidate**: the `ext__helmholtz_2d` instability (champion
   nRMSE 6.20 / 3.01 / 4.45 vs copy-LF 0.3295; seed spread 70% of the mean). It is the
   largest single lever on the panel geomean (helmholtz at skill ~1.5 would move the
   geomean 6.70 -> ~4.6) and the dominant source of geomean seed noise; the suspect knobs
   (`lr_pretrain`/`lr_finetune`, the `scaler_hf = max|y|` output scaling at
   smoke_eval.py:136-137) are squarely in-stream. Rejected for batch 1 only because §12.5
   pre-directs the modes card.
3. **Cross-stream handoff**: E-UNO's per-block mode *schedule*
   (https://arxiv.org/html/2509.01293v3, the source paper of `sharp__cahn_hilliard`,
   ~10× over flat modes) and MG-TFNO's Tucker-factorized spectral weights
   (https://arxiv.org/html/2310.00120, matches FNO error with 50% of the samples) are the
   published *safe* ways to buy bandwidth. Both are architectural and belong outside
   `s5_tuning`; the cap-32 result determines whether they are worth a card at all.
4. **`extra.modes` + `preds_test.npz`** give `s2_beyond_copy` a ready-made input for its
   per-band error-vs-copy-LF diagnostic at two mode budgets.
