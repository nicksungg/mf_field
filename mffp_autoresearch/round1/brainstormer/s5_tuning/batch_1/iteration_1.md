# Iteration 1 — Stream `s5_tuning`, Batch 1

## Design context considered

- `summary_so_far.md` §6 unknowns 1–3 (does the knob fire; is bandwidth the bottleneck;
  which arm of the capacity/overfit trade-off dominates) — the three this card can settle.
- **Prior-art verdict** (websearches/s5_tuning/batch_1/report.md, "For the brainstormer"
  item 1): the mode-count question is published prior art (iFNO / AFNO / MG-TFNO), so the
  card is a *measurement of this project's own spectral bottleneck*, not a novelty claim.
- **program.md §12.5** (quoted verbatim in summary §2): knobs only; and *"G4's dry-run
  card (`s5_tuning-B1`, modes_cap 12→32 on the champion) is a REAL batch-1 card for this
  stream."* `state/gates.md` lists G4 as PENDING on exactly this card.
- **Anchor** `state/anchors/s5_tuning.json`: `mf_fno_transfer_film`, panel geomean skill
  **6.703**, per-seed [7.102, 6.219, 6.788], `provisional: false`.
- **Noise floors** `state/noise_floor.json`: helmholtz **9.695** (ALERT), allen_cahn
  1.633, pfc 1.151, cahn_hilliard 0.553, fisher_kpp 0.418, ifc_poisson 0.240.
- **Immutables block (program.md §5)** held verbatim in view; see the self-check below.
- **Pre-falsified levers (§5)**: WNO backbone swap, LF low-mode freezing
  (`mf_fno_spectral`), diffusion prior.
- Code read first-hand this run (not recalled):
  `mf_field/factory_mffp/models/mf_fno_transfer_film/smoke_eval.py:47-49` (`WORK_CAP=256`,
  `SMOKE = dict(hidden_channels=64, n_blocks=4, modes_cap=12, batch_size=16,
  lr_pretrain=1e-3, lr_finetune=3e-4, weight_decay=1e-5, grad_clip=1.0)`), `:61-63`
  (`_modes(grid, cap) = (min(cap, H//2), min(cap, W//2+1))`), `:148-159` (resume from
  `last.pt`), `model.py:51-69` (`SpectralConv2d`, `scale = 1/(in_ch*out_ch)`,
  `if H >= 2*mh` negative-frequency branch);
  `round1/eval/score_panel.py:51-72` (`code_hash` includes the env dict), `:75-103`
  (child env, `--dataset_dir` resolved from the MAIN repo via `repo_root()`), `:238`
  (`--env KEY=VAL`), `:243-244` (`panel`/`guard` expansion).

## Proposal reasoning

### The decision the card must make

§12.5 pre-directs the knob. The open design decisions are (i) which single arm to run,
(ii) how to control it, (iii) how to make BOTH outcomes reportable given that the
literature predicts a null.

### Control comes free from batch 0 — so spend the whole budget on the treatment

The batch-0 anchor is the same family, same eval layer, same tier (200 epochs), same
seeds {0,1,2}, same nRMSE definition. Re-running a cap-12 control would burn ~7.7 GPU-h
to reproduce a certified number, which is precisely what §4.5 anchors exist to prevent.
Decision: **one arm only (cap 32), compared to `state/anchors/s5_tuning.json`.**

Requirement this imposes: the worktree family must be a *copy* of
`mf_fno_transfer_film` whose ONLY change is reading `MFFP_MODES_CAP` (default 12), so
that the default path is numerically the anchor's path. The builder must demonstrate
that at contract tier before any SLURM submit.

### Alternatives weighed and rejected

- **A. Capacity-matched single arm (`hidden_channels=24`, cap 32, `d_c*K` held at 768).**
  Rejected: it changes two knobs at once relative to the anchor, so a loss is
  attributable to width-24 rather than to bandwidth, and it does not answer the
  pre-directed F22 question ("does the champion recipe's `modes_cap` cost it anything?").
  Also, the `d_c*K = C` convention is flagged **UNVERIFIED** in the websearch report
  (iteration_4, attribution fetch failed) — designing the round's first card on an
  unattributable convention is bad discipline. Retained as the batch-2 branch IF cap 32
  wins.
- **B. Two-arm card (cap32/C64 + cap32/C24) in one batch.** Rejected on structure, not
  taste: `experiment_cards/SCHEMA.md` gives `recipe` exactly ONE `env` dict and the
  starter transcribes it verbatim; program.md §4.2 defines one batch = one experiment =
  one card = one SLURM chain. Two env sets would be two cards.
- **C. Bump modes AND muP-rescale the LR in the same arm** (sqrt(log12/log32) = 0.847, i.e.
  lr_pretrain 1e-3 -> 8.5e-4). Rejected for batch 1: it makes the measured quantity a
  two-knob package, and the muTransfer-FNO evidence (arXiv:2506.19396) is about *optimal*
  LR at each K, not a proven correction for this recipe. Designated the batch-2 branch IF
  cap 32 loses (it converts "bandwidth doesn't help" into "bandwidth doesn't help even
  when re-tuned").
- **D. Per-block mode schedule, E-UNO style [[32],[16],[8],[4]].** Strong prior (E-UNO
  beats flat modes by ~10x on our own `sharp__cahn_hilliard`, arXiv:2509.01293v3) and
  precedented in-zoo (`fno_coreg_residual` uses (4,8,12,12)). Rejected for batch 1:
  making the mode count block-dependent changes the model's structure across depth, which
  sits on the wrong side of §12.5's *"no architectural changes"* line, and it would leave
  the pre-directed flat-cap question unanswered. Recorded as an s5 batch-2/3 candidate,
  and as a handoff to whichever stream owns architecture.
- **E. Re-target the card at the `ext__helmholtz_2d` instability instead.** Scientifically
  the largest single lever on the objective: the champion's helmholtz nRMSE is 6.20 /
  3.01 / 4.45 vs a copy-LF reference of 0.3295, and moving helmholtz skill from 13.8 to
  ~1.5 would move the panel geomean from 6.70 to ~4.6 (2.1 units, >2x the geomean floor).
  Rejected for batch 1 because §12.5 names this card explicitly and `state/gates.md` G4
  is PENDING on it — a §12 anchor is ground truth, not a suggestion. It is recorded as
  the leading s5 batch-2 candidate (LR / output-scaler knobs are squarely in-stream), and
  the ALERT is honored here by excluding helmholtz from every per-dataset claim.

### Why cap 32 is still worth a card even though the literature predicts a null

program.md §1: an experiment is genuine if we learn either way. The websearch verdict
states the null explicitly: *"A null or negative result is the expected result and is a
genuine finding under program.md §1 — it converts 'the gap is knobs' into 'the gap is not
spectral bandwidth', which redirects `s2_beyond_copy` and `s4_hybrid_routing`."* Four
streams are currently reasoning under the unexamined assumption that a 9.4%-of-Nyquist
truncation is part of why fusion loses to copy-LF; one 3-seed run removes or confirms
that assumption for all of them. And the panel is *not* the generic Darcy/NS setting the
plateau results come from: on the three 256² sharp sets 12 modes is 9.4% of Nyquist,
far below where those ablations plateaued, and E-UNO's schedule evidence on our own
cahn_hilliard points the other way. The prior is genuinely two-sided per dataset even
though the aggregate prior favours a null.

### Design details that make both outcomes readable

1. **Proof the knob fired.** The result JSON must carry the realized
   `modes_cap`/`(modes_h, modes_w)` in `extra`, and `n_params` must move from 4,773,953
   to ~33.6M (ratio 32*32/12*12 = 7.11 on the spectral weights, derived from
   `SpectralConv2d`: two `(64,64,mh,mw)` complex tensors x 4 blocks; 4x2x64x64x144 =
   4.72M at cap 12, matching the observed 4.77M total). Without this, a silently
   unpropagated env var would look exactly like a null.
2. **Per-dataset table, never the geomean alone** (§2.3), with helmholtz marked
   `unfalsifiable (floor 9.695)`.
3. **Divergence is a result, not a bug.** `SpectralConv2d` uses `scale = 1/(in_ch*out_ch)`
   independent of mode count, so the initial output variance grows ~sqrt(7.1) ~= 2.7x at
   cap 32. If seed 0 craters (§4.4), that IS the finding — the recipe's mode count is
   coupled to its init scale — and it must be recorded, not "fixed" by adding knobs the
   card did not plan (that would leave the tuning stream).
4. **Walltime and resume.** Panel at cap 12 = 154 min/seed (timing ledger). The spectral
   einsum is 7.1x but FFT-dominated, so expect 1.3–2.5x -> recommend `--time 08:00:00`.
   Two independent recovery layers: `score_panel` writes its cache per dataset as it goes
   (score_panel.py:199-206), so a requeue skips finished datasets; and within a dataset
   the card requires periodic in-training saves to `<ckpt_dir>/last.pt` (slurm_rules §5:
   *"A job that restarts from epoch 0 after requeue is an ALGO bug"*), with the strict
   constraint that the no-preemption code path stays numerically identical to the anchor's.
5. **Predictions dump.** `smoke_eval.py` should additionally write the test predictions
   next to the result JSON so the mechanism-analyzer can run the per-band error-vs-copy-LF
   probe the websearch recommends (item 4) without a re-run. It must not touch the scored
   numbers.

## Proposal

- **Category**: `tuning_spectral_bandwidth`
- **Card type**: `model`
- **Motivation**: F22 (`modes_cap = 12` never scales with resolution; 12 of 128 modes at
  256²) and candidate M1's proposal of 32, tested on the certified champion. The
  websearcher's prior-art verdict, verbatim: *"**PRIOR-ART VERDICT: not novel, and must
  not be claimed as such — but legitimate as a measurement.** The mode-count question is
  published prior art: **iFNO** (https://arxiv.org/abs/2211.15188, verified first-hand
  this run) grows K during training and gets **10% lower error with 20% FEWER modes**;
  **AFNO** sparsifies modes; **MG-TFNO** factorizes them. `modes_cap` 12 -> 32 is
  therefore a *measurement of this project's own spectral bottleneck* (F22), not a
  mechanism contribution — which is exactly what a `tuning`-class card should be, and it
  stays inside §12.5 (a hyperparameter, not a new mechanism/architecture)."*
- **Concrete config**:
  1. Copy `mf_field/factory_mffp/models/mf_fno_transfer_film/` (at substrate commit
     `967562e`, tree `5f62eaa`) to `<worktree>/models_r1/mf_fno_transfer_film_modes/`
     (`manifest.json`, `model.py`, `smoke_eval.py`). Update `manifest.json.name` and the
     `finalize_and_write(model=...)` string to `mf_fno_transfer_film_modes`.
  2. Fix the import path for the new location: the copy sits at
     `<worktree>/models_r1/<family>/`, so `REPO_ROOT` must become
     `HERE.parents[1] / "mf_field" / "factory_mffp"` (the worktree is a full checkout);
     the current `HERE.parent.parent` resolves to the worktree root and would fail to
     import `data_adapters`.
  3. The ONLY behavioural change: `SMOKE["modes_cap"] = int(os.environ.get(
     "MFFP_MODES_CAP", 12))`. Default 12 must reproduce the anchor path exactly.
  4. Add to the result JSON `extra`: `modes_cap`, `modes: [modes_h, modes_w]`
     (audit that the knob fired). Write test predictions to
     `<ckpt_dir>/preds_test.npz` for the mechanism-analyzer's band probe.
  5. Add periodic in-training checkpointing to `<ckpt_dir>/last.pt` (stage + epoch +
     model/opt/sched/generator state), such that the no-preemption path is numerically
     identical to the anchor's.
  6. **Contract-tier gate before any submit** (login node, 2 epochs, seed 0):
     (a) with `MFFP_MODES_CAP` unset, `--datasets ext__helmholtz_2d,ifc_poisson` must
     match the untouched factory family run the same way (equivalence proof);
     (b) with `MFFP_MODES_CAP=32`, the same two datasets must run and report
     `modes [32,32]`, `n_params ~= 3.4e7`; (c) `--datasets guard --epochs 2 --seed 0`
     with the arm's env, required before any panel-win claim (§2.3).
  7. SLURM: one job per seed, `--datasets panel --epochs 200`, `--env MFFP_MODES_CAP=32`
     mirroring `recipe.env` exactly; `--time 08:00:00`.
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
- **Expected outcome** (metric: 3-seed mean panel geomean skill vs anchor 6.703
  [6.219, 7.102]; per-dataset skill table mandatory):

  | dataset | anchor skill | floor | predicted at cap 32 | reasoning |
  |---|---|---|---|---|
  | `sharp__allen_cahn_2d` | 16.334 | 1.633 | 15.0–16.5 (0 to -8%) | 9.4% -> 25% of Nyquist, but spectral bias (arXiv:2404.07200) says the added band goes unlearned |
  | `sharp__fisher_kpp_2d` | 4.177 | 0.418 | 3.9–4.3 | same |
  | `sharp__cahn_hilliard` | 5.534 | 0.553 | 4.6–5.7 (widest prior: E-UNO says bandwidth matters here) | arXiv:2509.01293v3 |
  | `sharp__phase_field_crystal_2d` | 11.511 | 1.151 | 10.8–11.8 | 19% -> 50% of Nyquist |
  | `ifc_poisson` | 1.566 | 0.240 | 1.6–2.0 (**worse**) | cap 32 = the FULL 64² spectrum fitted from N_hf = 5 |
  | `ext__helmholtz_2d` | 13.817 | **9.695** | uninterpretable | ALERT: claims unfalsifiable at smoke tier |
  | **panel geomean** | **6.703** | **0.884 (derived)** | **6.3–7.0 (null)** | |

  Most likely single outcome: |Δgeomean| < 0.884 -> **null**, which is the reportable
  finding "the panel gap is not spectral bandwidth". Runner-up: a clean win on
  `sharp__cahn_hilliard` (>0.553) with a regression on `ifc_poisson` (>0.240) — a
  bandwidth-vs-sample-count split that would be the most interesting outcome and would
  set batch 2 (capacity-matched `C=24, K=32`).
- **Expected falsification**: If the cap-32 arm's 3-seed mean panel geomean skill is not
  at least **0.884** skill units below the certified anchor **6.703** (i.e. not <= 5.819)
  AND no stable panel dataset improves by more than its own `min_claimable_effect`
  (`sharp__phase_field_crystal_2d` 1.151, `sharp__allen_cahn_2d` 1.633,
  `sharp__fisher_kpp_2d` 0.418, `sharp__cahn_hilliard` 0.553, `ifc_poisson` 0.240), then
  F22's `modes_cap` is NOT the champion's bottleneck and the panel gap is not spectral
  bandwidth.
- **Anchor reference**: `null` (program.md §4.5 / §12.5: batch 1 of `s5_tuning` judges
  against the own-stream certified anchor `state/anchors/s5_tuning.json`; the
  `card_id` form applies from batch >= 2, which re-targets the then-current champion card).

## Immutables self-check (program.md §5 — positive evidence per item)

1. **Data read-only** — the card writes no data path: `score_panel._run_one`
   (score_panel.py:76-80) resolves `--dataset_dir` to `<MAIN repo>/mf_field/factory_mffp/
   data/<dataset>` via `repo_root()`, and the family only *reads* it through
   `load_mf_dataset`. `N_hf` is untouched (`ifc_poisson` keeps its 5 HF train samples)
   and LF is still the dataset's own coarse solve (`lf = min(train["lf_fids"])`,
   smoke_eval.py:115) — no downsampled HF anywhere in the diff.
2. **Panel + guard fixed** — `recipe.datasets = "panel"` expands from `project.yaml`
   `panel:` inside score_panel.py:243-244; the guard check uses `--datasets guard`
   (score_panel.py:245-246). The card names no dataset outside those two lists.
3. **Eval layer / spec untouched** — every edited byte is under
   `<worktree>/models_r1/mf_fno_transfer_film_modes/`; the arm is expressed through the
   `--env KEY=VAL` interface score_panel.py:238 *already* parses, so nothing in
   `round1/eval/`, `project.yaml`, `program.md`, ADRs or `subagents/` needs to change.
4. **One nRMSE definition** — the copy keeps `finalize_and_write` emitting
   `splits.test_hf.rel_l2_per_sample`, which `_extract_test_metric`
   (score_panel.py:149-154) reduces to the per-sample mean (`metric_source:
   per_sample_mean`), the same path G1 certified. The training loss stays `F.mse_loss`
   (smoke_eval.py:96) — unchanged, and free in any case (§5).
5. **Contract CLI fixed** — `smoke_eval.py` keeps exactly
   `--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`
   (smoke_eval.py:209-215). The single knob is the env var `MFFP_MODES_CAP`, recorded in
   `recipe.env` and therefore folded into the cache key by `code_hash`
   (score_panel.py:70-71).
6. **Seeds / tier epochs fixed** — `recipe.seeds = [0,1,2]` and `recipe.epochs = 200`
   equal `project.yaml seed_protocol.seeds` and `tiers.smoke_epochs`; the pre-submit
   checks use `tiers.contract_epochs = 2`; no full-tier (2500) run is requested.
7. **Guarded factory surfaces untouched** — the base family is *read* out of
   `mf_field/factory_mffp/models/mf_fno_transfer_film` and copied into the worktree;
   the card touches no path under `factory_mffp/{eval,baselines,references,scripts,data}/`,
   no `factory.md`, and no `mf_field/akash/**` (the E-lever ideas that would touch akash
   were rejected above).
8. **Checkpoint-resume** — the copy retains the `<ckpt_dir>/last.pt` load branch
   (smoke_eval.py:148-159) that all 36 batch-0 array tasks ran under, and the card
   *adds* periodic in-training saves to the same file so a requeue does not restart at
   epoch 0 (slurm_rules §5); per-dataset progress is separately protected by
   score_panel's per-dataset cache write (score_panel.py:199-206).
9. **Threshold > noise floor** — panel geomean: anchor per-seed [7.102, 6.219, 6.788] ->
   spread **0.884**; applying `noise_floor.json`'s own convention
   `max(spread, 0.10 x mean) = max(0.884, 0.670) = 0.884`, and the card's geomean
   threshold IS 0.884 (13.2% relative). Per dataset the card uses the file's certified
   `min_claimable_effect` verbatim: pfc **1.151**, allen_cahn **1.633**, fisher_kpp
   **0.418**, cahn_hilliard **0.553**, ifc_poisson **0.240**. `ext__helmholtz_2d`
   (**9.695**, ALERT) carries no per-dataset claim in this card — its floor is 70% of its
   own mean skill (13.817) and the design does not address the instability, so per
   `state/gates.md` G3 it is excluded from the falsification clause and reported for
   information only.
10. **Not a pre-falsified lever** — nearest is **LF low-mode freezing
    (`mf_fno_spectral`)**, falsified as "worst on sharp, catastrophic on lid-cavity"
    (§5). That lever *constrained/froze* low modes as a multi-fidelity fusion mechanism;
    this card freezes nothing, adds no fusion mechanism, and only widens the retained-mode
    truncation of the unchanged champion recipe. The other two (WNO backbone swap;
    diffusion prior) are untouched — the backbone stays FNO and no generative prior is
    introduced.

## Status

- Slot covered: **yes** (1 proposal, `card_type: model`).
- Skipped: no.
- Reopen candidates resolved: **none existed** (no prior cards in any stream; verified by
  `find experiment_cards -type f` returning only `.gitkeep` and `SCHEMA.md`).
- Immutables self-check: **pass (10/10)** — no revision needed, no iteration_2 required.
