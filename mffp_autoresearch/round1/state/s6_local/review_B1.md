# code-reviewer — s6_local-B1, attempt 1

**Verdict: SUGGEST** (submit as-is; four findings must be carried into the screen /
analysis stage, none requires a code change)

**Reviewed**: `git diff round1-substrate..3abc0e30d56446148f5322787fbfd1d5f384cc82`
(40 files, +5721, 0 deletions). Build commit is clean (`git status --porcelain` empty).

## Verdict paragraph

This is the most tightly-evidenced build I have reviewed in this round. Every item in
card part 3 traces to code (depthwise K=7 / depth 4 / width 32 / GroupNorm+FiLM per block /
zero-init final 1x1 / receptive field 25 / target `R = Y_hf - LF_up` / `max(lf_fids)` /
ifc_poisson champion fallback / all four builder tripwires including the AGMF-Net re-fetch),
all 18 recipe env knobs appear verbatim in both job scripts (verified programmatically),
and the identity mechanism is not merely asserted but *structurally guaranteed*: `LF_up` is
produced by importing `round1/eval/panel_data.py::copylf_prediction` itself — a pure
function, imported read-only, with zero eval-layer bytes touched by the diff — so the
`G ≡ 0` path is the scored copy-LF reference rather than a re-implementation of it, and
the card's anticipated `scipy.zoom`-vs-`F.interpolate` kernel delta is exactly 0.0 instead
of merely small. The runtime hard-asserts are real executable code that `raise
S6ContractError` (smoke_eval.py:364-367 data-path check vs `copylf_baselines.json`;
:456-462 forward-at-init and gate-at-init checks), they run *before* checkpoint load so
they stay meaningful on resume, and I independently confirmed exact `0.0` for
`identity_delta_vs_baseline`, `identity_forward_max_abs_dev`, `gate_init_max_abs` and
`delta_init_max_abs` in all six committed sidecar JSONs covering all five variants. The
screen gate is real, not decoration: I rebuilt a synthetic screen tree myself and
re-ran `scripts/screen_report.py`, getting exit 0 / promote `lf_frozen_adapter` on the
happy path, exit **2** with `NO-HARM VIOLATION on ['pointwise_ctrl']` on an injected
skill-1.35 arm, and exit **3** on missing inputs — and `00_screen.sh` runs under
`set -euo pipefail` so a non-zero aggregator exit kills the job. The staged-training
addition stays inside the card's mandate (stages 1 and 3 are literal card text; only
stage 2 is new, and it is necessary to give variant 1's field-valued gate any parameters
at all), and the dead-init rationale is mathematically correct. I am withholding PASS
only because four items must be consciously carried forward by the orchestrator and the
analyzer — most importantly the zero-padding confound on the periodic phase-field
datasets, which cannot break the no-harm floor but can depress the card's single
informative readout on exactly the datasets the falsification clause names.

## Findings (7 questions)

| # | Question | Verdict | Finding |
|---|---|---|---|
| 1 | Card–implementation alignment | **PASS** | Every part-3 item traces to code. Verified: `local_corrector.py:89` dw `Conv2d(w,w,(7,7),groups=w)`; `:90` `FiLMNorm` = `nn.GroupNorm(min(8,C),C,affine=False)` + FiLM MLP (`model.py:85`), matching "GroupNorm, per-block FiLM(X)"; `:121-123` zero-init head weight **and** bias; `:128` `receptive_field = 1 + 4*(7-1) = 25` = card's "~25"; `smoke_eval.py:388` `R = Y_tr - LF_tr` = card's "Target: `R = Y_hf - LF_up`"; `:315` `lf_tr = max(train["lf_fids"])` = card's mandatory `max(lf_fids)`; `:851-853` fallback to `run_champion` iff `not test["lf_fids"]`. Tripwires (i) `:331-339`, (ii) `:353-355`, (iii) `:358-367`, (iv) recorded in `INSPIRATION.md:32-51` + build_notes. Variant table `smoke_eval.py:93-100` maps 1:1 to the card's ranked table. |
| 2 | Recipe fidelity | **PASS** | All 18 `recipe.env` knobs present verbatim in `01_train_eval.sh` and `00_screen.sh` (machine-checked, one exception below); `datasets panel`, `--epochs 200`, seed 0 only, `family_dir models_r1/s6_local_lf_corrector`, `base_family`/`base_commit 967562e…` recorded in `manifest.json`. `model.py` sha256 `80d8940d…` verified byte-identical to `factory_mffp/models/mf_fno_transfer_film/model.py`. Every non-recipe hyperparameter is either base-family-verbatim (`SMOKE` dict, lr 3e-4/1e-3, bs 16, wd 1e-5, clip 1.0) or an explicitly enumerated builder choice in build_note 7 — no silent choice found. `S6_VARIANT` is passed as `$VARIANT`/`$V` rather than the pinned `local_pixel_gate`: this is card-sanctioned (part 3 promotion rule + ADR 0007), and `S6_SCREEN_VARIANTS` enumerates the legal values. |
| 3 | §5 immutable compliance | **PASS** | (3) diff touches no `round1/eval/`, `project.yaml`, `program.md`, ADRs or agent prompts; the eval import is a pure read-only function call and I confirmed the worktree's `nrmse.py`, `panel_data.py`, `copylf_baselines.json` are byte-identical to the main tree's. (7) no guarded factory surface in the diff; `model.py` is a *copy into* `models_r1/`, not an edit of the factory. (1) no data writes; the LF-coarser-than-HF tripwire enforces repo law. (4/5) scoring routes exclusively through `score_panel.py` — no `smoke_eval.py` number enters the card, and `--env` is the only env surface (`grep os.environ` finds exactly one call site, `read_knobs`). (6) seeds `[0]`, contract 2 / smoke 200. (8) see #4. **Pre-falsified levers**: none re-proposed as-is — see SUGGEST-B below for the one adjacency worth naming. |
| 4 | Contract compliance | **PASS** | `manifest.json` has name/description/supports/frozen + entrypoint; `smoke_eval.py:856-864` exposes exactly the 6-arg CLI; `INSPIRATION.md` is a per-row citation table covering the card's `prior_art` list and the AGMF-Net threat. **Checkpoint resume**: `<ckpt_dir>/last.pt` written atomically (tmp + `os.replace`, `:216-227`) with a per-variant mirror; `_load_ckpt` (`:230-252`) rejects a checkpoint whose meta (epochs/grid/seed/variant/kernel/depth/width/path/dataset) disagrees, and `:498-503` refuses to resume on stale scalers. Mid-stage resume implemented for encoder/corrector/gate with opt+sched+shuffle-generator state, and tested (`train_seconds = 7.15e-07`, bit-identical nRMSE reproduction). Seeding `:840-844` covers random/numpy/torch/cuda from `--seed`. |
| 5 | SLURM correctness | **PASS** | `bash -n` run on all four scripts — all clean (`bash -n OK: scripts/00_screen.sh / 01_train_eval.sh / submit_seeds_2_3.sh / submit.sh`); `py_compile` clean on `screen_report.py` + the 4 family modules. Partition `gpu` and typed gres `gpu:h100:1` match `project.yaml sbatch:`; `--mem=32G`, `--cpus-per-task=4`, `--requeue`, `--exclude=hpc-93-36` match the round convention; `--output/--error` under `${OUTPUTS_ROOT}/s6_local/B1/slurm/`; all paths absolute; `01_train_eval.sh` takes `SEED=$1` (+ optional promoted variant `$2`); `submit.sh` = seed 0 only; `submit_seeds_2_3.sh` present and correctly marked not-in-round. Header job name `r1-s6_local-B1` without the seed matches the s1/s5/s7 pattern (submit.sh overrides with `-s0`); screen job `r1-s6_local-B1-screen` matches the s4/s5 `-guard`/`-agg` aux precedent. `--time` deviation ledger-verified — see SUGGEST-D. |
| 6 | Smoke-test evidence | **PASS** | build_note 3 cites the contract-tier `score_panel.py` command and `scratchpad/contract_smoke.json` exists and is real: `ext__helmholtz_2d`, epochs 2, seed 0, `--no_cache`, exit 0, nRMSE `0.32945012604380175`, skill `0.9999999999999998`, split `test_hf`, `metric_source per_sample_mean`, code_hash `3b5e3ef5…`, and its `env` block contains all 18 knobs. Backed by `SMOKE_EVIDENCE.md`, `aux_smoke.sh`, 6 diag sidecars, the ifc_poisson fallback leg, the resume test and the screen dry-run. |
| 7 | Blast radius | **PASS** | `git diff round1-substrate..3abc0e3 --name-only \| grep -Ev '^(models_r1/\|scripts/\|notes/\|scratchpad/)'` → **NONE outside allowlist**. No substrate-fix commits, no deletions, working tree clean. |

## SUGGEST items (carry forward; no code change required now)

**A — Zero padding on periodic phase-field datasets (the requested severity call).**
`ConvNeXtLiteBlock.__init__` (`local_corrector.py:89`) uses torch's default **zero**
padding on the depthwise convs. `sharp__allen_cahn_2d`, `sharp__cahn_hilliard` (both
HF 256×256) and `sharp__phase_field_crystal_2d` (HF 128×128) are periodic spectral
solves, where circular padding is the physically correct choice. With receptive field
25 the boundary-contaminated band is 12 cells deep: **~18% of pixels on the two 256²
datasets and ~34% on pfc** (and ~44% on the 96² helmholtz, where zero padding is
defensible anyway). My judgement: **this will NOT materially distort the headline
skill/geomean result** — `Delta` enters only through `alpha * g ⊙ Delta` with `alpha`
held-out-selected from a candidate set containing 0 and a `MIN_GAIN` floor, so a
boundary-damaged correction is simply switched off, and the identity/no-harm floor is
untouchable. It **can** materially depress `contribution_d`, which is this card's *only*
informative readout, on exactly two of the four datasets named in the strong-form
falsification clause. So: acceptable-and-recorded, not a correctness bug — but if
`contribution_d` lands below 0.04 on allen_cahn / cahn_hilliard / pfc, the analyzer
**must** name zero padding as a live alternative explanation rather than concluding
"a LOCAL corrector adds nothing", and `circular` padding on periodic datasets is the
obvious batch-2 follow-up. Recorded here so the finding cannot be quietly lost.

**B — `lf_frozen_adapter` adjacency to a pre-falsified lever.** §5 pre-falsifies "LF
low-mode freezing (`mf_fno_spectral`)". Variant 3 freezes an entire LF-pretrained
spectral encoder. This is **not** the same mechanism — `mf_fno_spectral` froze
LF-learned low modes *inside the HF predictor*, whereas here the frozen encoder only
supplies auxiliary features to a local adapter whose base prediction is the real LF
field, and the card pre-registers F-Adapter's *opposing* prediction — so this is a
legitimate differentiated composition, not a re-proposal. But the card never cites the
`mf_fno_spectral` falsification. The screen dry-run promotes `lf_frozen_adapter`; if the
real screen does too, parts 5–7 must explicitly distinguish the promoted mechanism from
the pre-falsified lever (§5's "cite the falsification and say what is different").

**C — Two small screen-aggregator edges.** (i) `screen_report.py:144-146`: if exactly one
survivor has a non-`None` rho, it is promoted regardless of margin, which can bypass
rank order. Low probability, but if it fires the orchestrator should record it
explicitly. (ii) A plausible screen outcome is `alpha = 0` on every beyond-copy dataset
for every variant at 2 epochs (this is what happened on helmholtz in the smoke:
`alpha = 0`, `rho = 0`), giving mean rho 0 for all five and a rank-order promotion of
`local_pixel_gate`. That is a correct, pre-registered path — not a failure — and the
orchestrator should not treat it as ALGO.

**D — Directed deviations: both judged sound.** (1) `S6_DIAG_OUT` absolutized: the
recipe value is repo-relative, the scripts pass `$OUT_DIR/eval` (promoted) and
`$OUT_DIR/screen/diag` (screen) so the 2-epoch sidecars cannot overwrite the 200-epoch
ones; the family also absolutizes a relative value itself, so the recipe string alone
still works. Faithful. (2) `--time=02:00:00` vs the card's advisory 06:00:00: I verified
the ledger claim independently — `state/timing_ledger.json` entry `job_id 65988184`,
s5_tuning-B1, the same 6-dataset panel, 200 epochs, seed 0, `gpu_type h100`,
`elapsed_min 36.62`. slurm_rules §4 *requires* right-sizing from the ledger and warns
that oversized `--time` pends forever; the card's 06:00:00 came from the p100 prior.
2:00 is 3.3× the h100 analog, the corrector/gate stages are ~57k+15k params (cheap
relative to the 5M-param FNO), and the run is resumable if it ever does time out.
Correct call.

## Minor notes (no action)

- **Ambiguity resolution (a)** — variant 3's unspecified gate type resolved to the rank-1
  pixel gate: **faithful**, and the better reading, since it isolates variant 3 from
  variant 1 on exactly the frozen-encoder axis (the D2 arm's actual claim).
- **Ambiguity resolution (b)** — variant 4's band coefficients LS-fit on the FIT split with
  the scalar `alpha` still held-out selected: **faithful**. The card's held-out language
  attaches to "its scalar component", which is preserved, and `G ≡ 0` at init still holds
  (the coefficients multiply an all-zero `Delta`). Slight stretch of "4 per-band scalar
  gates … all init 0" (they are closed-form fitted, not trained from zero), but no-harm is
  carried by `alpha`, so nothing the card claims is weakened.
- **Build-note framing** — build_note 5 says the staging "is NOT in the card". Stages 1
  ("Target: `R = Y_hf - LF_up`") and 3 ("its scalar component is **finally** selected on a
  held-out slice") *are* card text; only stage 2 (gate head trained against `g⊙Delta ≈ R`
  with the corrector frozen) is the addition, and it is required for the card's own
  field-valued gate to have trainable parameters. The dead-init argument is correct
  (`∂L/∂θ_Δ ∝ g = 0`, `∂L/∂θ_g ∝ Δ = 0` — an exact zero-gradient saddle). Inside the mandate.
- **PixelGate clamp dead-zone** — `clamp(..., 0, 1)` at `local_corrector.py:185` is
  trainable at init (subgradient 0.5, verified), but pixels whose pre-activation goes
  negative receive zero gradient and can stay dead. `frac_g_gt_0.01` in the sidecar
  partially measures this; worth a glance in analysis.
- **Latent eval-layer seam** — the family imports `panel_data.py`/`nrmse.py` from the
  *worktree's* eval dir while `score_panel.py` runs from the *main tree's*. They are
  byte-identical today (checked), and the `_nrmse_def_hash` guard at `smoke_eval.py:174-178`
  catches divergence, so this is safe now; noted only because the substrate and trunk
  copies of `score_panel.py` have already drifted.
- **`write_diag` relative fallback** would write under the worktree, not into any guarded
  surface; both job scripts pass absolute paths, so it never fires in the SLURM path.

## Orchestrator checklist before submit

1. `sbatch scripts/00_screen.sh`; require exit 0 (exit 2 ⇒ ALGO ⇒ debugger, exit 3 ⇒ missing inputs).
2. Record the promoted variant + `screen_table.md` in the card's `build_notes` **before** `submit.sh`.
3. `bash scripts/submit.sh <promoted_variant>` (seed 0 only; do NOT fire `submit_seeds_2_3.sh` in-round).
4. Never quote `rho` or any screen number as evidence in card parts 5–7 (ADR 0007).
