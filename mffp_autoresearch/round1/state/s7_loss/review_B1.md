# Handoff from code-reviewer — 2026-07-29T20:40Z

**For**: orchestrator (submit decision), experiment-debugger, initial-analyzer
**Experiment**: s7_loss-B1 (model card, ADR 0007 five-arm screen)
**Diff reviewed**: `round1-substrate..990f88916d38a0aac3af9a96e4b13b2601596596`
(23 files, +1708/-0)

## VERDICT: **PASS** — submit as-is (screen first)

The build does exactly one behavioural thing and proves it. `model.py` is md5-identical
to the substrate champion (`ebfc56ce69282984b601a806ba735b10`); the only behavioural
hunk in `smoke_eval.py` is `_train`'s `loss = F.mse_loss(pred, yb)` → `if loss_fn is
None: F.mse_loss(...) else loss_fn(...)`, with `loss_fn = None` whenever `MFFP_S7_LOSS`
is unset — so §12.7's METRIC IMMUTABLE holds structurally, not just by assertion: no
file under `round1/eval/`, no `data_adapters/metrics.py`, no guarded factory surface is
in the diff, and every number still flows through `score_panel.py` →
`finalize_and_write` → `round1/eval/nrmse.py` under the same `nrmse_def_hash`
(`d3d0ade9…`). I re-derived the load-bearing claims independently rather than trusting
build_notes: the shape/gain identity holds to 2.1e-14 (float64) across five grids
including the degenerate 1-D cases, `band(β=1) == rel` to 3.6e-15 (Parseval, incl.
odd-W and (1,64)/(64,1)), `amp(λ=1)` is **bit-identical** to `rel`
(`2.008315086364746` both), the committed A-def vs untouched-factory JSONs agree to all
17 digits on both datasets (22.613192981264614 / 0.4900025652737081, |Δ| = 0.0), all
six arms are distinct on `ifc_poisson` with A2ctl(β=1) matching A0(rel) to 1.2e-8 after
two full float32 stages, the resume drill is bit-identical across
uninterrupted/SIGKILL-resumed/re-finished (`rel_l2_mean 0.3469903010539124` ×3, mid-
pretrain epoch 3/8), and I reproduced all five promotion-rule branches plus the
gate-1 DIVERGED path and a no-survivor escalation on my own synthetic screen dirs.
All five `.sh` pass `bash -n`; `screen_table.py` and both family modules byte-compile.
Blast radius is `models_r1/ scripts/ notes/ scratchpad/` only; `git status` in the
worktree is clean (the builder's `.gitignore` overwrite-and-restore left nothing behind
— `.gitignore` is **not** in the commit, as claimed).

## Findings (7 questions)

| # | Question | Verdict | Evidence / note |
|---|---|---|---|
| 1 | Card–implementation alignment | **PASS** | Every card part-3 item traces to code: (a) `smoke_eval.py:82 REPO_ROOT = HERE.parents[1]/"mf_field"/"factory_mffp"`; (b) periodic RNG-neutral ckpt `_save_ckpt` + `CKPT_SAVES_PER_STAGE=5`, atomic `tmp`+`os.replace` (block is *identical* to s5-B1's — it does not even appear in a diff against `mf_fno_transfer_film_modes`); (c) `_train:202-205` the one loss hunk, applied to both stages via `loss_pre`/`loss_fin` and `applies_to`. Norm-spread logging present in stdout **and** result JSON (`hf_norm_spread_train/test`). Arm table maps 1:1 onto `parse_env` (`arm_amp_lam4_both`, `arm_amp_lamauto_both`, `arm_band_beta4_kc8_both`, `arm_band_beta2_kc4_both`, `arm_rel_both`, `arm_mse` — I enumerated all six). λ=auto implements `clamp(mean(shape)/(mean(gain)+1e-8), 0.25, 64)` = card text; clamp verified firing at 0.25. Denominator clamp is literally `transolver_residual/smoke_eval.py:68`'s `clamp(sqrt(sum y²), min=1e-4)`. Band edges are s2-B1 `forensics.py::band_masks` reproduced construction-for-construction (`fftfreq(H)*H`, `arange(W//2+1)`, `k_nyq=min(H,W)/2`, half-plane weight 2 except DC and even-W Nyquist) ⇒ KC=8 is dyadic band 0, KC=4 is bands 0+1 at `n_bands=4`. |
| 2 | Recipe fidelity | **PASS** | `01_train_eval.sh` `--env MFFP_S7_LOSS=amp MFFP_S7_LAMBDA=4.0 MFFP_S7_STAGES=both` = `recipe.env` verbatim, `--datasets panel`, `--epochs 200`, `SEED=$1`, `submit.sh` seed 0 only; `recipe.seeds [0]` = `project.yaml seed_protocol.seeds`; family_dir/base_family/base_commit all match (base copy md5 `bd44251c…`). No invented hyperparameter: `modes_cap 12, batch 16, lr 1e-3/3e-4, wd 1e-5, clip 1.0` are the base family's *and* `modes_cap 12` is the configuration the 6.703 anchor was certified on (`state/anchors/s5_tuning.json.family = mf_fno_transfer_film`) — comparability intact. `MFFP_S7_LAMBDA`/`BETA`/`KC` have **no defaults**: I confirmed 5/5 malformed-knob cases raise `S7LossConfigError`. Only undeclared constant is `_SQ_EPS = 1e-12` inside `sqrt(sum p²)` (documented in-code as gradient-finiteness at `pred==0`, which I verified; it perturbs the identity at ~1e-16 relative) — acceptable, not a silent hyperparameter. |
| 3 | §5 immutable compliance | **PASS** | Diff touches no `round1/eval/`, `project.yaml`, `program.md`, ADR, subagent prompt, or `factory_root/{eval,baselines,references,scripts,data}`/`factory.md`/`akash/` path (grep on `--name-only` returns nothing). No data regeneration; scoring is `score_panel.py` in both the screen and the main job; contract tier 2 / smoke tier 200 = `project.yaml tiers`; seed 0 in-round per ADR 0004 with `submit_seeds_2_3.sh` reserved for end-of-round. No hand-rolled metric anywhere in the family (it hands `pred`/`target` to `finalize_and_write`). Pre-falsified levers: the nearest one (LF low-mode freezing, `mf_fno_spectral`) is cited **and** differentiated in `INSPIRATION.md` ("A2 only re-weights training-time low-k HF error, with every mode still trainable") — not a re-proposal. ADR 0009: all objectives are field-only (norms, cos, spectra); no governing equation at train or test time. |
| 4 | Contract compliance | **PASS** | `manifest.json` (name/description/supports `["ifc_raw","npz_l"]`/frozen false + `env_knobs` doc), six-arg CLI exactly (`--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed`), `INSPIRATION.md` cites all six `prior_art.citations` URLs and marks the `preempted-pivoted` boundary. Resume: `contract_last = ckpt_root/"last.pt"` **is** read (`src = last if last.exists() else contract_last…`), so the literal contract path is honoured; writes go to `<ckpt_dir>/<arm_tag>/last.pt`. Both isolation guards present and load-bearing: (i) per-arm subdir, (ii) `sd.get("s7_arm_tag","arm_mse") == S7["arm_tag"]` in `same_cfg` ⇒ mismatch trains fresh. Seven distinct `arm_*` ckpt dirs on disk. Seeding is byte-inherited from the base (`torch.manual_seed(seed)` — seeds CUDA too — `+ np.random.seed(seed)`; `random` unused). Divergence from s6-B1, which *mirrors* to the literal path: s7 writes only the arm path. Deliberate and safer (a mirror would let the fallback serve a sibling arm's weights); resume proven bit-identical, so immutable #8 is met in substance. |
| 5 | SLURM correctness | **PASS** | `bash -n` OK on `00_screen.sh 01_train_eval.sh submit.sh submit_screen.sh submit_seeds_2_3.sh` (5/5, no output). Headers: `--partition=gpu`, `--gres=gpu:h100:1` (= `project.yaml sbatch`, typed), `--cpus-per-task=4`, `--mem=32G`, `--requeue`, `--exclude=hpc-93-36` (14-script round precedent), logs `…/outputs/round1/s7_loss/B1/slurm/%x_%j.{out,err}`. Job names `r1-s7_loss-B1-screen` (exact `r1-s6_local-B1-screen` precedent) and `r1-s7_loss-B1-s{seed}` set via `sbatch --job-name` in the wrappers (the header's bare `r1-s7_loss-B1` follows the s5/s6 pattern). Every path absolute (grep for relative paths: none). `--time`: screen 01:00:00 against the s6 5-variant panel+guard screen at 8.6 min; main 02:00:00 = ADR 0005 default against the 36.62 min panel@200 h100 analog. `00_screen.sh` deliberately omits `-e` so a crashed arm becomes the validity gate's "no result JSON" — correct, and `run_arm` always `return 0`. |
| 6 | Smoke-test evidence | **PASS** | build_notes cite the exact contract-tier `score_panel.py --no_cache` commands and the result files are committed: `scratchpad/contract_smoke_default.json`, `contract_smoke_BASE_factory_{helm,ifc}.json`, `arm_{A-def,A0,A1a,A1b,A2a,A2b,A2ctl}_ifc_poisson.json`. I re-read all of them: gate-1 equality is bitwise on both datasets; six arms distinct and finite; A2ctl is the Parseval control. Resume-drill JSONs/logs under `<outputs>/s7_loss/B1/contract_smoke/{resume_drill,logs}` confirm `[resume] mid-run checkpoint … stage=pretrain epoch=3/8` and identical finals. A1b's provenance block (`s7_loss`, `s7_loss_source`, `s7_lambda_effective`, `s7_arm_tag`, `s7_env_seen`, `s7_applied_stages`) is present in the per-dataset JSONs I inspected. |
| 7 | Blast radius | **PASS** | `git diff --stat` = `models_r1/ (5) scripts/ (6) notes/ (2) scratchpad/ (10)`; zero deletions, zero substrate edits, no `.gitignore` in the commit, worktree `git status --porcelain` empty. |

## Advisory notes (non-blocking; for the ORCHESTRATOR at screen-read time)

1. **Gate 1 is reported, not enforced, in the machine-readable decision.**
   `screen_table.py` computes `gate1_default_equivalence.pass` and prints
   **PASS/FAIL** at the top of `screen_table.md`, but `decision.recommended` is
   populated regardless — I confirmed this with a synthetic 5e-08 divergence
   (`gate1=False/DIVERGED`, `rec=A1a`). Follow the card's order-of-operations
   step (2) literally: **read gate 1 first; do not submit on a DIVERGED gate.**
   (Optional one-liner for a future build: `decision["blocked_on_gate1"] = not equiv["pass"]`.)
2. **The validity gate fails open if A-def's panel result is missing** —
   `adef_geomean_claimable = None` ⇒ `cap = None` ⇒ no arm can exceed 2×, so all
   arms read "valid" (verified). Backstop: gate 1 then reads
   "missing A-def and/or BASE factory panel result" with `pass=false`, which
   note 1 already tells you to check.
3. **The screen omits `--no_cache`, and 10 matching 2-epoch cache entries already
   exist** from the builder's login-node CPU runs (`round1/eval/cache`: base +
   A-def on `ext__helmholtz_2d`/`ifc_poisson`, and `ifc_poisson` for all five arms
   plus A2ctl). So gate 1's two carded datasets and every arm's `ifc_poisson`
   will be **cache-served CPU numbers** while the other panel datasets run fresh
   on H100. Harmless — same-basis across arms, screen numbers are never
   reportable (ADR 0007), and the builder's full-panel superset still gives gate 1
   four freshly-computed datasets — but the analyzer should not read the screen
   claimable geomean as homogeneous hardware. Consistent with s6_local-B1, which
   also omits `--no_cache` and passed review.
4. **Clause 3 can promote A0.** `RANK_ORDER` includes A0, so a control arm at
   ≤0.5× the leader's geomean is recommended by the gross-signal override
   (I reproduced this: `rec=A0`, `amend=True`, `reframe=False`). That is the
   literal card text, but A0 is "measurement only" in the arm table — if this
   fires, treat it as clause-4-style reframing, not a contribution.
5. **A non-A1a promotion needs a script edit that post-dates this review.**
   `01_train_eval.sh`'s `--env` line is hardcoded to A1a (card-mandated). If the
   screen promotes another arm, log the recipe amendment first, then the `--env`
   line must be changed — route that one-line edit back through review (and note
   `recipe` is a LOCKED card field, so the amendment lives in build_notes /
   orchestrator log, not in `recipe`).
6. `MFFP_S7_STAGES` defaulting to `both` is card-stated text, and the two screen
   supersets (gate 1 on the full panel; guard for every arm) are strictly
   stronger than the card and change no clause of the rule. The extra **A2ctl**
   arm is a control, not a sixth candidate: it is absent from `RANK_ORDER`, so it
   cannot be promoted.
7. Watch `sharp__sod_1d` for the band arms in the guard set (1-D ⇒ grid `(1, L)`).
   I verified `band_rel_sq` is Parseval-exact on `(1,64)` and `(64,1)` and does
   not raise, so this is a numerics-interest note, not a crash risk.

## Order of operations (unchanged from build_notes, endorsed)

1. `sbatch scripts/00_screen.sh` (or `scripts/submit_screen.sh`).
2. Read `<outputs>/s7_loss/B1/screen/screen_table.md` — **gate 1 PASS first**
   (`max |ΔnRMSE| <= 1e-9`), then record the promoted arm.
3. If `recommended != A1a`: log the amendment BEFORE submit (see note 5).
4. `scripts/submit.sh`.
