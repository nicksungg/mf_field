# code-reviewer — s2_beyond_copy-B3 (attempt 1)

**Verdict: SUGGEST (`reviewed_suggest`)** — submit as-is, screen first (ADR 0007);
three evidence/provenance findings must be carried by the next stage, none of which
touches the code or blocks the run.

Reviewed 2026-07-30T19:17–19:25Z. **Build commit reviewed: `71d4e7b3c3f3f743bc57d7e5b92520e80ee3d3de`**
(branch `round1/exp-s2_beyond_copy-B3`, worktree `round1/worktrees/s2_beyond_copy/B3`).

> **Note on the moving target.** My dispatch named
> `1df8d635f9170518d720f8b14e5dab2199a7ebb7` / "build note 16". While the review was
> in flight the second builder instance (on `hpc-54-03`) reset and re-committed the
> branch at 12:13:47 PDT as `71d4e7b`, the card's `build_commit` was re-pinned to it
> at 12:14, and `state/s2_beyond_copy/current_stage.txt` was updated to
> `reviewer_running (build 71d4e7b; evidence-incident scrutiny priority)`. **I verified
> that this changed nothing I had reviewed**: the `models_r1` tree object is
> `be6324b963576db9f91a296fba8bce2775ba6da1` and the `scripts` tree object is
> `ced8c7467fe53fc8a2b2b1980755ed8d46ce7258` in **both** commits, and
> `git diff 1df8d63..HEAD -- models_r1 scripts` is empty. The delta is purely
> additive evidence (`scratchpad/{contract_smoke_A1_fluid.json,
> contract_smoke_A1_ifcpoisson.json, diag/floor_fluid.json, results/…/{fluid,
> ifc_poisson}_e2_s0.json, par.sh, log_A1_*.txt}`) plus a reworded builder handoff and
> a new build note 17. The findings below are stated against `71d4e7b`.

## Justification (one paragraph)

The build implements card part 3 with unusual literalness and its `build_notes` claims
survive independent re-derivation. An AST function diff against the `recipe.base_commit`
blob reproduces build note 2 exactly (`model.py` and `retrieval.py` byte-identical to
`5bf0e86c`; only `_scale`/`_train`/`_predict`/`_floor_cache_key`/`compute_floors`/
`read_knobs`/`run` modified, `_as_denominator`/`_gate_split` added, `_blend`/
`blockmean_retrieved` removed); the `_train` and `_predict` bodies differ from B2 only
by routing the scaler through `_as_denominator`, whose scalar branch returns a float32
0-d tensor so A0's *training* divide stays bit-identical to B2's. All 46 `recipe.env`
knobs appear byte-equal in a single `--env` invocation in both job scripts, are
re-asserted at runtime by `assert_env.py` against the card itself, and
`REQUIRED_ENV ∪ SCREEN_ENV` equals `recipe.env` set-for-set — no silent default, no
unrecorded knob. Test isolation is structural rather than conventional: the HF test
array is tainted at load with three detectors, every fit entry point is
`assert_clean`'d, and A3 is the sole `fence()`d use — which I confirmed *empirically*
on a per-run JSON produced by this exact code (8 fit-entry checks, exactly 1 fenced
oracle use, both `ref_*` splits `reportable=false`, scored split `test_hf` only). The
resume drill's exact-equality claim is re-derivable from committed artifacts (summing
`resumed_A0_helm.json`'s 100 per-sample values the way
`score_panel._extract_test_metric` does gives `15.35039754106132`, identical to the
uninterrupted A0 value). The branch is one commit whose parent is `round1-substrate`
HEAD, the tracked tree is clean, blast radius is `models_r1/ scripts/ notes/
scratchpad/` only, and the sbatch walltimes come from `sacct` entries I re-queried
(66023543 = 00:17:34, 66011965 = 00:06:28). The verdict is SUGGEST rather than PASS
solely because of the evidence-handling incident the builder himself records in note
17: build note 16 is now factually stale (it asserts HEAD is `1df8d63`), the note
numbering collides, and the helmholtz/pfc per-run instrumentation figures quoted in
note 12 — including the F10 cross-validation that was the strongest "the diagnosis is
real" signal — no longer have a committed file behind them and must be treated as
unverified until the first 200-epoch run reproduces them.

## Findings table (7 review questions)

| # | Question | Verdict | Finding |
|---|---|---|---|
| 3.1 | Card–implementation alignment | PASS | Every part-3 item traces to code: the four B2 scaler sites (`smoke_eval.py:333` train-divide, `:290-296` predict-multiply, `:600-614` `scaler_out`, `_scale` docstring-only change), six arms via `S2B3_ARM` + two `ref_*` splits (`run():950-1023`), and all four MANDATORY instrumentation items (1 = `mechanism_instrumentation` whose `damage_stats` formulas byte-match `tools/registration_skill_split.py:140-152`; 2 = `scale_audit` before/floored/`s_hat`; 3 = `scale_table.quality` ρ + median\|log10 ratio\| + A3−A1 gap; 4 = `preds_test_<arm>_<ds>.npz`). The D3 sidecar is correctly delegated to the analyzer's post-hoc `registration_skill_split.py` call, exactly as part 3 words it. Promotion rank pinned before submit (`screen_table.py:125` walks `S2B3_PROMOTION_RANK` in order). No paraphrase drift found. |
| 3.2 | Recipe fidelity | PASS | Parsed both job scripts: 46/46 `recipe.env` keys present, zero missing, zero extra, zero mismatched; `S2B3_ARM=$ARM` is the only substitution. Exactly one literal `--env` flag per `score_panel.py` call (`00_screen.sh:64`, `01_train_eval.sh:84`) — the `nargs='*'`-without-append trap is avoided, and `assert_env.py:56-66` fails the job if it recurs. `datasets` / `epochs=200` / `seed 0` / `base_family` / `base_commit` match verbatim (`BASE_COMMIT` is also hard-coded at `smoke_eval.py:99` and shipped in every result JSON). `REQUIRED_ENV ∪ SCREEN_ENV` == `recipe.env`, so no code knob is unrecorded. Unpinned choices (MLP layer reading, `g_phi` optimiser/batch, A4 τ grid) are disclosed in `build_notes` 7 and echoed in the emitted JSON. |
| 3.3 | §5 immutable compliance | PASS | Diff touches no `round1/eval/`, `project.yaml`, `program.md`, ADR or subagent prompt; no guarded factory surface (`factory_root/{eval,baselines,references,scripts,data}`, `factory.md`, `akash/`); no data regeneration (`S2_LF_SOURCE=dataset_lf_fidelity` hard-asserted in `read_knobs`, plus a coarser-grid tripwire at `run():574-578`). All scoring flows through `eval/score_panel.py`; `assert_env.py:72-74` fails if the scored split is anything but `test_hf`, and `smoke_eval.py:1065-1067` hard-stops if a `ref_*` split masquerades as a test split. Seeds `[0]` (ADR 0004); epochs 200 scored / 2 screen = the project.yaml tiers. No pre-falsified lever re-proposed — the card attacks target normalisation, not the WNO swap, LF low-mode freezing or the diffusion prior; the nearest neighbour (s5-B2's per-*dataset* `MFFP_TARGET_SCALER=zscore`) is not a §5 lever and is explicitly differentiated in card part 4. |
| 3.4 | Contract compliance | PASS | `manifest.json` present with `name`/`description`/`supports`/`frozen` + provenance. `smoke_eval.py:1128-1135` exposes exactly the 6-arg CLI. `INSPIRATION.md` cites all seven `prior_art` URLs (grep-verified) and quotes the verdict verbatim. **Checkpoint-resume**: `<ckpt_dir>/last.pt` written by `_save_ckpt`, consumed at `run():723-739, 821-835`; the drill is not merely present but *exact* — resumed vs uninterrupted `test_hf` agree to the last bit (`15.35039754106132`) — and `g_phi` rides in the same `last.pt` under `scale_head`. Seeding uses `--seed` for numpy + torch (+CUDA via `torch.manual_seed`); no stdlib `random`. |
| 3.5 | SLURM correctness | PASS | `bash -n` run by me on all five `scripts/*.sh` **and** all four `scratchpad/*.sh` — all OK; `py_compile` OK on all three `scripts/*.py` and all four family `.py`. Partition `gpu` + typed gres `gpu:h100:1` match `project.yaml sbatch:`. Job names `r1-s2_beyond_copy-B3-s0` / `-screen`; `--output`/`--error` under `${OUTPUTS_ROOT}/s2_beyond_copy/B3/slurm/%x_%j.{out,err}`; all paths absolute; `set -euo pipefail`; `mkdir -p` before use; venv sourced. `01_train_eval.sh` takes `SEED=$1` (+ optional `PROMOTED_ARM=$2`, validated against the rank list at `:51-54`); `submit.sh` = seed 0 only; `submit_seeds_2_3.sh` present and correctly parked. `--time` derivation re-verified against live `sacct`: 00:17:34 (66023543) and 00:06:28 (66011965) as claimed, and `state/timing_ledger.json` indeed holds no s2 200-epoch entry, so sacct was the right source; 01:30:00 for a two-arm job (~2.6× headroom) and 01:00:00 for the screen are right-sized. |
| 3.6 | Smoke-test evidence | **SUGGEST** | The contract-tier command is cited (`score_panel.py --epochs 2 --seed 0 --no_cache` with the full 46-knob `--env`; driver committed at `scratchpad/smoke.sh`) and **six** result files now exist in `scratchpad/`: `contract_smoke_{A0,A1,A2}_helmholtz.json`, `contract_smoke_A1_pfc.json`, plus the post-incident replacements `contract_smoke_A1_{fluid,ifcpoisson}.json` — each with 46 env knobs, `split=test_hf`, `metric_source=per_sample_mean`, finite values, spanning `ext__`, `sharp__`, guard and `ifc_` layouts. **The gap** (self-declared in build note 17): the *per-run* JSONs for the helmholtz and pfc A1 smokes were destroyed in the incident, so build note 12's headline cross-validation figures — helmholtz `effective_n_samples_of_mse` 1.2463 vs card F10's 1.2, `energy_share_top1` 0.8920 vs 89.2 %, pfc `global_over_median_per_sample` 79460.12 vs 79460, plus ρ 0.9513/0.9753 and the A3−A1 oracle gaps — have **no committed file behind them**. I re-verified the *structure* of every one of those blocks on the committed replacement (`scratchpad/results/persample_pred/s2_resid_amplitude_norm/fluid_e2_s0.json`: `scale_table` + `scale_audit` + `mechanism_instrumentation` + `ref_oracle_truescale` all present and correctly labelled, q25 floor flooring exactly 64/256 = 25.0 %, ρ 0.9474), so the mechanism demonstrably works — but it is verified on a **guard** dataset, not on the two datasets where the pathology lives. Treat those figures as unverified priors until the 200-epoch run regenerates them. |
| 3.7 | Blast radius | PASS | `git diff round1-substrate..HEAD --name-only \| grep -v '^(models_r1\|scripts\|notes\|scratchpad)/'` returns nothing. 40 files, 9054 insertions, 0 deletions. Branch is one commit; parent `967562e` = `round1-substrate` HEAD; tracked tree clean (only my own untracked `notes/handoff_code_reviewer.md`). No substrate contamination. |

## Build-specific drill-downs requested by the orchestrator

**1. B2-continuity / A0 arithmetic.** The AST claim holds. `_train` differs from B2
only by `Yt = torch.from_numpy(Y).float() / _as_denominator(scaler, N, "cpu")`
replacing `/ scaler`, and `_as_denominator`'s scalar branch returns
`torch.tensor(float(scaler), dtype=torch.float32)`, so A0's training divide is
bit-identical to B2's. `_predict` differs only by slicing a broadcastable denominator.
The one genuine deviation is honestly recorded in `build_notes` 6 and confirmed in
code: the final `s·Δ` composition now happens in numpy float64 (`run():878-881`)
rather than float32 inside `_predict`, because the split algebra was refactored to
`LF_up + <scale>·Δ_unit` so A3 can reuse one forward pass. The drift is ~1e-7 relative
— five orders below the 2 % continuity band — and makes A0 marginally *more* accurate,
not differently trained. RNG parity is real: the FNO is constructed before `g_phi`
(`run():715`) and `fit_scale_mlp` snapshots/restores the global torch RNG at both its
own construction (`scale_norm.py:332-338`) and the caller level (`run():747, 784`), so
A0 and A1 start from identical FNO weights. The continuity gate is correctly
*recorded, not enforced as a stop* (card part 4 calls a miss a rebuild-fidelity flag):
`B2_PART5_SKILL` and `B2_CONTINUITY_TOL` (`smoke_eval.py:153-161`) equal card part 4's
A0 column and the 10 %-pfc / 2 %-elsewhere tolerances exactly; the flag is computed for
`global_ctrl` on all five datasets, printed to the slurm log, shipped in the per-run
JSON, echoed by `assert_env.py:134-137`, and carried into `paired_readout.json` under
`per_dataset[ds].a0_b2_continuity`. Observed working — and correctly failing with the
`epochs_caveat` — in the committed 2-epoch A0 artifact.

**2. Test isolation.** Drilled and confirmed, including empirically. `y_te` is tainted
the instant it is loaded (`run():567`), three detectors over 256 row digests. A1's MLP
fits on `feat_tr` (from `x_tr`, `lf_tr`) against `s_tr_vec`, guarded by
`assert_clean("fit_scale_mlp", features, targets)`; A2's closed-form `c` fits on
`lf_tr`/`s_tr_vec`, guarded by `assert_clean("fit_gradproxy", …)`; the A4 τ search uses
only holdout margins from the **HF train** split under leave-one-out neighbour
prediction (`scale_norm.py:540-561`) — the test-side `model_ps_query`/`copylf_ps_query`
enter only *after* `tau_star` is chosen, to score the gate. The true `s_i` for A3 comes
from `y_te - lf_te` at `run():954`, i.e. **after** training and after every fit has
closed, immediately preceded by `firewall.fence(...)`, and it multiplies the same
`delta_unit` from the same checkpoint — no second model, no second forward pass. The
firewall report on a real per-sample run shows the intended shape: 8 fit-entry checks
across `target_normalisation_stats`(×3) / `fit_scale_mlp`(×2) / `gate_calibration`(×3)
with exactly one fenced use (`ref_oracle_truescale`), status clean; the A0 control shows
6 checks and **0** fenced uses, the correct asymmetry. `assert_env.py:106-119` fails the
job if the report is missing, unclean, has no tainted array, no checked fit row, or if
either `ref_*` split is not `reportable=false`.

**3. The 2-epoch numbers.** Properly fenced. `build_notes` 9 stamps them "CONTRACT-TIER
… NOT reportable (ADR 0007); they live in build_notes only"; every per-run JSON carries
`screen_numbers_are_never_reportable`; `screen_summary.json` carries `reportable: false`
plus an `adr_0007_note`; card `5_actual_result` is `null`. The only consequence a screen
number has is arm selection via `S2B3_PROMOTION_RULE`, which is exactly what ADR 0007
authorises, and `screen_table.py` implements the rule verbatim with `global_ctrl` as a
*reference* (`in_promotion_rank: false`) and A5 never promotable. **Standing hazard**:
A1's 2-epoch helmholtz skill is 0.9249 — below 1, numerically the shape of round-1
success criterion #2. It is a 2-epoch plumbing artifact and must not travel into any
claim, dashboard or handoff; `ext__helmholtz_2d` is REPORT-ONLY at 200 epochs too
(rescaled floor 0.701654).

**4. Restart-duplicate consolidation.** The consolidation invariant *currently* holds
and I verified it directly: `git rev-list --count round1-substrate..HEAD` = 1, parent =
`967562e`, tracked tree clean, committed tree == working tree. But note 16's specific
assertion ("HEAD is `1df8d635…`") was falsified 8 minutes after it was written, by the
second instance's reset-and-recommit that produced `71d4e7b` — an event I observed live
(HEAD changed under me between two of my own `git status` calls) and which the builder
records from the other side in note 17 as an "external process". Reflog shows the full
sequence: `7bcfb91` → `4064f74` → reset → `1df8d63` → reset → `002e179` → reset →
`71d4e7b`. Nothing is half-merged, and the *code* was never in flux — only scratch
evidence and the handoff wording. See finding F2 for the residual documentation defect.

**5. Pruned/lost scratchpad and the replacement evidence.** The committed set supports
the resume-drill exact equality (re-derived above), the 46-knob presence in every
`score_panel` summary, the identity proof (`abs_delta_nrmse = 0.0`), the F6 floor check,
the full A0 per-run structure, and — post-incident — a complete A1 per-run JSON on
`fluid` that exercises the whole per-sample path end to end. It does **not** support the
helmholtz/pfc-specific figures in note 12. Net: the *mechanism* is verified, the
*numbers* are not. This is exactly what note 17 admits, and the admission is the right
call; the cost is that the F10 cross-validation (in-run `scale_audit` independently
reproducing the card's motivating diagnosis) has to be re-established by the first real
run instead of being already banked.

**6. Discretionary choices.** The A4 τ grid is within discretion: `recipe.env` pins
`S2B3_GATE_CALIBRATION=train_holdout_margin_quantile` and no quantile level; the search
runs over the holdout's own predicted-margin quantiles (0…1 step 0.05) plus both
degenerate gates so "no gate" is reachable (B2's `S2_BLEND_INCLUDES_ZERO` discipline);
the selection objective uses holdout data only; and A4 is a `ref_*` measurement-only
split that prior-art row D2 forbids claiming as a mechanism — so the choice cannot reach
a scored number. It is disclosed in `build_notes` 7, in the module comment, and in the
emitted `tau_grid_is_builder_choice` field, alongside an honest caveat that the trained
model saw the holdout. The inherited floor-sidecar fix (PID-unique temp names for both
`floor_<ds>.json` and the preds npz) is sound, minimal and in-scope — it repairs a
`FileNotFoundError` race the builder actually triggered — and cannot perturb any metric.

## SUGGEST findings (carry to the next stage; none blocks submission)

- **F1 — note 12's helmholtz/pfc instrumentation figures are unverified.** No committed
  file backs them (build note 17 says so explicitly). *Minimal fix, for the
  initial-analyzer:* do not quote them in card part 5 as established; instead read the
  regenerated `${OUTPUTS_ROOT}/…/B3/eval/results/<arm>/<ds>_e200_s0.json` blocks
  (`scale_audit.before_global_scaler.effective_n_samples_of_mse`,
  `energy_share_top1`, `target_normalisation.global_over_median_per_sample`) and state
  whether they reproduce card part 2's F10 diagnosis (1.2 / 89.2 % / 79460). If they do
  not, that is itself a finding about the F10 diagnosis, not about this build.
- **F2 — build note 16 is stale and contradicts note 17.** Note 16 asserts HEAD is
  `1df8d635…`; HEAD is `71d4e7b3…`. *Minimal fix:* the card's `build_commit` field is
  already correct, so the analyzer/maintainer should treat **note 17 + the
  `build_commit` field** as authoritative and, if a builder or debugger touches the card
  again, append a one-line correction to note 16 rather than leave two contradictory
  provenance claims in the permanent record.
- **F3 — build-note numbering collision.** Entries 16 and 17 both begin "16.", and note
  15(e)'s pointer "see note 16" actually means the 17th entry. Cosmetic but it will
  mislead the mechanism-analyzer's citations. *Minimal fix:* renumber on the next
  legitimate card write.

## Advisories (informational; no action required)

- **A1 — the continuity flag is not rendered in the human-readable readout.**
  `paired_readout.py` carries `a0_b2_continuity` into the JSON, but the markdown table
  and the falsification-legs block never print it, so an analyzer reading only
  `paired_readout_s0.md` could miss a rebuild-fidelity miss. Read
  `paired_readout_s0.json → per_dataset[ds].a0_b2_continuity`, or the `[B2-continuity]`
  lines in the slurm log, before writing card part 5.
- **A2 — a floor sidecar already exists in the outputs tree.**
  `${OUTPUTS_ROOT}/round1/s2_beyond_copy/B3/eval/floor_sharp__allen_cahn_2d.json`
  (written 09:47 during the build). It is key-guarded — `_floor_cache_key` hashes
  `retrieval.py` bytes + dataset + grid + floor knobs + N_train/N_test + copy-LF nRMSE +
  `nrmse_def_hash` — and its recorded env matches the final recipe with
  `f6_check.passed = true` (1.041701 vs F6 1.042, Δ 3.0e-4), so reuse is correct. For a
  fully cold run, `rm ${OUTPUTS_ROOT}/round1/s2_beyond_copy/B3/eval/floor_*.json` before
  submitting; not required.
- **A3 — `ifc_poisson` replacement evidence lands on the `champion` fallback.**
  `scratchpad/results/persample_pred/s2_resid_amplitude_norm/ifc_poisson_e2_s0.json` has
  `arm_effective = champion` (the pre-registered `S2_FALLBACK_NO_TEST_LF` path) and
  therefore carries no per-sample instrumentation. It is fine as a crash-freeness check;
  the substantive A1 evidence is the `fluid` per-run JSON.
- **A4 — inherited seed-independent batch order.** `_train`'s permutation generator is
  `torch.Generator().manual_seed(0)` (`smoke_eval.py:336`), inherited byte-identical from
  B2 / `mf_fno_transfer_film`, so mini-batch order does not vary with `--seed`.
  Irrelevant in-round (strict 1 seed, ADR 0004) and identical in A0 and A1, so the paired
  control is unaffected; changing it here would have broken B2 continuity, so leaving it
  is the right call. Flag it only if B3 reaches the end-of-round 3-seed confirmation —
  the seed spread will be narrower than a fully re-seeded model's.
- **A5 — confirm the second builder instance is gone before submitting.** It reset and
  re-committed this branch three times, most recently 12:13:47 PDT on `hpc-54-03`
  (interactive job 66060598). The branch has been stable and clean for the remainder of
  this review, and `01_train_eval.sh` reads the family directly from the worktree at job
  runtime, so a rewrite mid-flight would change the running code *and* the eval-layer
  `code_hash`. A one-line `git rev-parse HEAD` check immediately before `sbatch` (and
  again after the job starts) is cheap insurance.

## Submit-time instructions for the orchestrator

1. **Confirm the branch is quiescent**: `git -C <worktree> rev-parse HEAD` must be
   `71d4e7b3c3f3f743bc57d7e5b92520e80ee3d3de` and match the card's `build_commit`
   (advisory A5).
2. **Screen first (ADR 0007)**: `bash scripts/submit_screen.sh` → job
   `r1-s2_beyond_copy-B3-screen` (2 epochs, 4 arms × {beyond_copy5, guard},
   `--time=01:00:00`).
3. **Read the screen table before promoting**:
   `${OUTPUTS_ROOT}/round1/s2_beyond_copy/B3/screen/screen_table.md` and
   `screen_summary.json → promoted_arm`. The rule is pinned: `persample_pred` unless
   *broken* (crash / non-finite / 5-dataset geomean > 3.0× `global_ctrl`'s **on that
   same screen run**); `persample_gradproxy` is the only fallback; `global_ctrl` and
   `persample_nofloor` are never promotable; close calls never reorder. **Screen numbers
   go into `build_notes` only** — never part 5, never a dashboard.
4. **Fix the promoted identity in the card** (a note naming the promoted arm) *before*
   the scored submit.
5. **Submit seed 0 only**: `bash scripts/submit.sh <promoted_arm>` (default
   `persample_pred`) → job `r1-s2_beyond_copy-B3-s0`, `--time=01:30:00`, which runs
   **A0 `global_ctrl` first and the promoted arm second inside one allocation** — that
   co-location is what makes the control paired, so do not split it into two jobs. Do
   **not** run `submit_seeds_2_3.sh` in-round (ADR 0004).
6. **On completion** the job self-reports: `assert_env.py` after each arm (hard-fails on
   knob drift, a non-`test_hf` scored split, a dirty firewall, a failed identity proof or
   F6 floor), then `paired_readout.py` writing `eval/paired_readout_s0.{json,md}` with
   falsification legs (a)–(d). Read the `b2_continuity` flag from the JSON or the slurm
   log (advisory A1) and record any miss as a rebuild-fidelity flag, **not** a result.
   Address F1 in the same pass.
7. **Reporting fences for part 5**: every number is `provisional-single-seed`;
   `ext__helmholtz_2d` is REPORT-ONLY; `ref_oracle_truescale` (A3) and
   `ref_gate_lfkeyed` (A4) are never leaderboard-eligible and A4 carries no mechanism
   claim (prior-art row D2); a clean failure of leg (a) with (b)–(d) intact is the card's
   PRE-REGISTERED WELL-FOUNDED NEGATIVE and is a **result**, not a failed card.

**Checklist**: 7/7 review questions answered with traceable evidence; `bash -n` run on
9/9 shell scripts (all OK) and `py_compile` on 7/7 python files; verdict recorded against
the true HEAD after verifying the reviewed trees were unchanged by the re-commit; card
status set to `reviewed_suggest`; one `review_notes[]` entry appended; locked fields
untouched.
