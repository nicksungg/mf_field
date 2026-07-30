# Code review — s7_loss-B2 (attempt 1)

**Reviewer**: code-reviewer | **UTC**: 2026-07-30T16:28:04Z
**Card**: `experiment_cards/s7_loss/batch_2/B2.json` (`card_type: diagnostic`)
**Worktree**: `worktrees/s7_loss/B2` @ branch `round1/exp-s7_loss-B2`
**Build commit**: `ed27054323b137a09540e20392d577c84a7491a9`

## VERDICT: **PASS** — submit as-is.

### Justification (one paragraph)

This is the cleanest build the round has produced, and it is clean for a
structural reason: it invents nothing. I independently re-derived all five
sha256-16 vendor pins three ways (working tree, the committed blob at
`ed27054`, and `git cat-file blob 990f8891:models_r1/mf_fno_transfer_film_s7loss/<f>`)
and all fifteen values agree with the card's `recipe.env._source` — the
zero-edit vendor is proven, not asserted, so B1's entire verified substrate
(loss math, bit-identical default path, SIGKILL-resume drill) transfers by
byte-identity rather than by re-review. I re-ran the eval layer's own hasher
and confirm `code_hash(B1_dir, env) == code_hash(B2_dir, env) == ba08a5ef…`,
which is exactly the property the recipe predicted and exactly the reason
`--no_cache` is mandatory; `01_train_eval.sh` passes it, the run's cache key
`05306b4e…` does not yet exist on disk, and B1's amp arm hashes differently
anyway, so three independent barriers stand between this measurement and a
B1 cache hit. On the round's known `--env` trap I verified argparse behaviour
myself in the round venv (`--env A=1 --env B=2` → `['B=2']`; `--env A=1 B=2`
→ `['A=1','B=2']`): the builder correctly refused the recipe `_run` field's
two-flag shorthand — implementing it literally would have silently run the
MSE default and produced a scientifically void band-(a)-looking number — and
the committed contract-tier evidence closes the loop empirically, with the
result JSON carrying `env {MFFP_S7_LOSS: rel, MFFP_S7_STAGES: both}`,
`s7_loss_source: env:MFFP_S7_LOSS`, `s7_arm_tag: arm_rel_both`, and
nRMSE `0.36672538257500825` — bitwise equal to B1's own A0(rel) number. I
re-computed every outcome-band edge from the certified primitives and both
edges reproduce to the last printed digit (`16.334668349426035 + 1.633407079448426
= 17.968075428…` → nRMSE `0.29021625…`; `61.99787588859377 − 1.633407079448426
= 60.36446880…` → nRMSE `0.97499314…`), with both comparators verified against
their source files on disk and the edges matching the brainstormer's
`iteration_1.md` lines 195-197 character for character. `bash -n` passes on
all three scripts, every path is absolute, the SLURM header matches
`slurm_rules.md` §1 exactly with a `--time` justified by B1's own measured
575.0 s allen_cahn leg on this identical family/tier/dataset, `submit.sh`
`mkdir -p`s the log dir before `sbatch` and hard-aborts on any pin drift, and
the blast radius is thirteen files confined to `models_r1/`, `scripts/`,
`notes/`, `scratchpad/`. Nothing blocks submission; the four observations
below are advisory and all concern how the *analyzer* should read the
artefacts, not whether the run should start.

---

## Findings table (7 questions)

| # | Question | Verdict | Finding |
|---|---|---|---|
| 1 | Vendor pins re-verified | **PASS** | All 5 pins match 3 ways. See §1. |
| 2 | Recipe fidelity + the `--env` trap | **PASS** | Single-flag form; both knobs proven to reach the contract JSON. See §2. |
| 3 | Cache / ckpt separation from B1 | **PASS** | 3 independent barriers; run cache key absent from disk. See §3. |
| 4 | Outcome-band transcription integrity | **PASS** (1 advisory) | Both edges exact; non-edge sub-case pair inconsistent by 0.028 skill. See §4. |
| 5 | SLURM correctness | **PASS** | `bash -n` clean ×3; header matches slurm_rules §1; `--time` ledger-justified. See §5. |
| 6 | Blast radius | **PASS** | 13 files, all in `models_r1/ scripts/ notes/ scratchpad/`. See §6. |
| 7 | §5 immutables + contract | **PASS** (2 advisory) | No eval/ or guarded-surface writes; ckpt-resume present; stale manifest inert. See §7. |

---

## §1 — Vendor pins (re-verified independently, question 1)

I did **not** trust `verify_vendor_pins.sh`; I recomputed from scratch:

```
                 worktree          B1 commit blob    committed at ed27054
INSPIRATION.md   a4f96be8d8748e3d  a4f96be8d8748e3d  a4f96be8d8748e3d
manifest.json    cb1f04bea56ce342  cb1f04bea56ce342  cb1f04bea56ce342
model.py         80d8940d8b90a4ac  80d8940d8b90a4ac  80d8940d8b90a4ac
s7_losses.py     44e9b956a87aa187  44e9b956a87aa187  44e9b956a87aa187
smoke_eval.py    3969ebe420cd1e5a  3969ebe420cd1e5a  3969ebe420cd1e5a
```

All fifteen values equal the card's `recipe.env._source` pins. The third
column matters and the builder did not check it: the pins hold for the
**committed** blobs, not merely the working tree, so what SLURM will execute
from the checked-out worktree is the same bytes the gate certifies.

`scripts/verify_vendor_pins.sh` re-derives the same thing at submit time from
both the file and the B1 commit blob, exits 1 on any drift, and `submit.sh`
runs it *before* `sbatch` under `set -euo pipefail`. Gate is real, not
decorative.

**The integrity argument is sound**: byte-identity makes B1's default-path
equivalence (|Δ nRMSE| = 0.0 on `ext__helmholtz_2d` and `ifc_poisson`) and
B1's SIGKILL-resume drill inherited facts rather than re-assertions. This is
the correct substitute for a default-equivalence screen and, as the recipe
argues, it is immune to the device-mixing failure that voided s5-B2's first
screen — it compares bytes, not numbers.

## §2 — Recipe fidelity and the `--env` rendering (question 2)

Every value in `01_train_eval.sh` traces to the locked recipe: `family_dir`
`models_r1/mf_fno_transfer_film_s7loss_b2`, `--datasets sharp__allen_cahn_2d`,
`--epochs 200`, `--seed $SEED` (submit passes 0), `--no_cache`,
`--env MFFP_S7_LOSS=rel MFFP_S7_STAGES=both`, `--time 00:30:00`, partition
`gpu`, `--gres=gpu:h100:1`, job name `r1-s7_loss-B2-s0`, log dir under
`${OUTPUTS_ROOT}/s7_loss/B2/slurm/`. **No hyperparameter appears in the
scripts that is absent from recipe ∪ part 3 ∪ build_notes.** `MFFP_S7_LAMBDA`
is correctly absent per `recipe.env._note`.

I verified the trap myself in the round venv:

```
--env A=1 --env B=2   ->  Namespace(env=['B=2'])        # earlier pair LOST
--env A=1 B=2         ->  Namespace(env=['A=1','B=2'])  # both survive
```

`eval/score_panel.py:238` is `p.add_argument("--env", nargs="*", default=[])`
— no `action="append"`. The recipe `_run` field renders the flag **twice**;
a literal implementation would have dropped `MFFP_S7_LOSS=rel`, silently run
the untouched MSE default, and returned a number near the MSE comparator —
i.e. it would have *manufactured a false outcome (a)*, the single most
dangerous failure mode available to this card. The builder used the
single-flag form. This is the correct call, it is science-preserving rather
than science-neutral, and it matches B1's and s5-B2's and s1-B3's scripts.

**Both knobs are proven to reach the run**, not just the CLI. From the
committed contract evidence
(`scratchpad/contract_results/mf_fno_transfer_film_s7loss_b2/ifc_poisson_e2_s0.json`):

```
s7_loss: 'rel'   s7_loss_source: 'env:MFFP_S7_LOSS'   s7_stages: 'both'
s7_arm_tag: 'arm_rel_both'
s7_env_seen: {'MFFP_S7_LOSS': 'rel', 'MFFP_S7_STAGES': 'both'}
s7_applied_stages: ['pretrain', 'finetune']
```

and from `scratchpad/contract_smoke.json`: `"env": {"MFFP_S7_LOSS": "rel",
"MFFP_S7_STAGES": "both"}`, `"cached": false`, nRMSE
`0.36672538257500825`, `metric_source: per_sample_mean`, `split: test_hf`.

That nRMSE is **bitwise equal** to B1's `build_notes[3]` A0(rel) ifc_poisson
value `0.36672538257500825`, which I read out of B1's card myself. Both were
CPU/login-node contract tier, so bitwise agreement is the expected and
strongest possible outcome.

## §3 — Cache and checkpoint separation from B1 (question 3)

The builder's own note flags the risk correctly: because the vendor is
zero-edit, `code_hash` is *shared* with B1 at equal env. I re-ran the layer's
hasher:

```
code_hash(B1_dir, {rel,both}) == code_hash(B2_dir, {rel,both}) == ba08a5ef… (True)
code_hash(B1_dir, {amp,4.0,both}) != that hash                            (True)
```

Three independent barriers stand between this run and a B1 number:

1. **`--no_cache`** is passed → `use_cache=False` → `score_panel.score_family`
   never reads a cache file. Mandated by `recipe._run`; present in the script.
2. **Env enters the hash.** B1's 200-epoch run used `{amp, λ=4.0, both}`,
   which hashes differently, so even with caching on there is no collision.
3. **The exact key does not exist.** I computed
   `sha256("ba08a5ef…|sharp__allen_cahn_2d|200|0") = 05306b4eddcf9a20…` and
   confirmed no such file in `round1/eval/cache/`. B1's only `rel` runs were
   2-epoch screens, a different key.

Directory separation is on-disk verified from the contract run: results land
under `<ROUND1_EVAL_RESULTS>/mf_fno_transfer_film_s7loss_b2/` (score_panel
derives `out_dir` and `ckpt_dir` from `Path(family_dir).name`, lines 85-88),
and the checkpoint tree is `ckpt_<ds>_e<E>_s<S>/arm_rel_both/`.
`arm_rel_both` cannot collide with B1's `arm_amp_lam4_both`.

**A cache hit on B1's numbers is not reachable.** Good.

## §4 — Outcome bands vs comparators (question 4)

I re-derived every edge from the certified primitives rather than checking
the card against itself. Copy-LF reference for `sharp__allen_cahn_2d` =
`0.016151772077279084` (`eval/copylf_baselines.json`, `reference_type:
copylf`).

Comparators, both read from their cited source files:

- MSE default, same family/tier/seed —
  `outputs/round1/batch0/eval/mf_fno_transfer_film__sharp__allen_cahn_2d_s0.json`:
  nRMSE `0.26383384013787387`, skill `16.334668349426035`, `env {}`,
  `epochs 200`, `seed 0`, `metric_source per_sample_mean`, `split test_hf`. ✓
- B1 λ=4 endpoint — B1 card part 5: nRMSE `1.001375560628003`, skill
  `61.99787588859377`, `delta_vs_champion_seed0 45.66320753916773`. ✓
  (this last confirms part 4's "Δ ≈ −45.7 skill units".)
- `min_claimable_effect` `1.633407079448426` and seed spread
  `0.014149916588777955` — `state/noise_floor.json`, `sharp__allen_cahn_2d`. ✓

Recomputed edges:

| edge | recomputed | card | match |
|---|---|---|---|
| (a) skill | 16.334668349426035 + 1.633407079448426 = **17.96807542887446** | 17.968075 | ✓ |
| (a) nRMSE | 17.96807542887446 × ref = **0.2902162589945389** | 0.290216 | ✓ |
| (b) skill | 61.99787588859377 − 1.633407079448426 = **60.36446880914534** | 60.364469 | ✓ |
| (b) nRMSE | 60.36446880914534 × ref = **0.974993141771338** | 0.974993 | ✓ |
| (a)↔(b) gap | **42.39639338027088** | 42.396 | ✓ |
| floor/seed-spread ratio | **115.4358…** | "115×" | ✓ |
| 5.01e-5 nRMSE → skill | **0.0031018…** | 0.0031 | ✓ |

Both band edges are exact and the partition is exhaustive and mutually
exclusive as claimed (`≤ a` / `a < x < b` / `≥ b`, with the printed 6-decimal
values sitting inside the true edges by <1e-6 — irrelevant at a 42-skill-unit
separation). The edges also match the brainstormer source
`iteration_1.md:195-197` character for character, so the transcription chain
is intact end to end.

**Advisory A-1 (non-blocking, locked field, cannot be fixed by me).** The
*sub-case* pair is internally inconsistent: `nRMSE ≤ 0.237` ⇒ skill
`14.673312…`, while the card prints skill `14.701` (⇒ nRMSE `0.2374487`). A
0.028-skill / 0.4e-3-nRMSE discrepancy. This is **not** a band edge, it sits
~3.3 skill units inside band (a), it is explicitly flagged as *not claimable*
as an s7 win, and no measurement outcome can be reclassified by it. Guidance
for the initial-analyzer: **treat the nRMSE form (`0.237`) as authoritative**
(nRMSE is the measured quantity; skill is derived) and record the exact
0.237 ⇒ 14.6733 conversion in part 5 rather than reprinting 14.701.

## §5 — SLURM correctness (question 5)

`bash -n` run by me on all three scripts (output cited verbatim):

```
scripts/01_train_eval.sh: OK
scripts/submit.sh: OK
scripts/verify_vendor_pins.sh: OK
```

| slurm_rules.md §1 requirement | actual | ✓ |
|---|---|---|
| `--job-name=r1-{stream}-B{N}-s{seed}` | `r1-s7_loss-B2-s0` | ✓ |
| `--partition` = project.yaml `sbatch.partition` | `gpu` | ✓ |
| typed gres = `sbatch.gres` (ADR 0005) | `gpu:h100:1` | ✓ |
| `--nodes/--ntasks/--cpus-per-task/--mem` | 1 / 1 / 4 / 32G | ✓ |
| `--time` present, ledger-justified | `00:30:00` | ✓ |
| `--output/--error` under `${OUTPUTS_ROOT}/s7_loss/B2/slurm/` | absolute, `%x_%j.{out,err}` | ✓ |
| `set -euo pipefail` | line 1 of body | ✓ |
| `mkdir -p` slurm/ + eval/ before use | in **both** `submit.sh` (pre-`sbatch`, so the header's `--output` dir exists) and the job body | ✓ |
| activates `${PROJECT_ROOT}/.venv` | absolute path; `.venv/bin/activate` confirmed present | ✓ |
| `01_train_eval.sh` takes `SEED=$1` | `SEED="${1:?usage: …}"` | ✓ |
| `submit.sh` = seed 0 only | one `sbatch --parsable … 0` | ✓ |
| one `score_panel.py` call, no train→eval chain | ✓ | ✓ |
| paths absolute; nothing sourced relative to `$0` | verified by inspection | ✓ |

`--time=00:30:00` provenance is sound and I checked it against the ledger
myself: `state/timing_ledger.json` has **no** s7_loss entry, so the builder
correctly fell back to B1's own measured leg — B1 part 5
`per_dataset_train_seconds["sharp__allen_cahn_2d"] = 575.0224516391754` s on
1×H100 for this *identical* family, tier and dataset. 30 min is ~3.1× the
training leg with room for venv start, data load, eval and IO. It is also
right-sized rather than oversized (the round-5 backfill lesson); the nearest
ledger analog, `s4 fno_transolver_seq allen_cahn 200ep h100 = 31.28 min`, is a
heavier family and was correctly *not* used.

`--requeue` + `--exclude=hpc-93-36` match round-wide precedent
(s1-B2, s1-B3, s2-B1, s2-B2, s3-B1 all carry the same exclude). Resume is
idempotent, so requeue is safe.

`submit_seeds_2_3.sh` is **absent, and its absence is documented** in
`scripts_path._seeds_2_3_note`, `build_notes[4]`, and `submit.sh`'s header
comment (ADR 0004 + program.md §4.3; `recipe.seeds == [0]`). Correct for a
diagnostic. No `00_screen.sh` (ADR 0007 diagnostic exemption, verified
verbatim at `docs/adr/0007-propose-many-screen-cheap.md:38`: "Diagnostics and
spec-pre-directed slots are exempt (no candidate pool)") and no guard script
(`_no_guard`; program.md §2.3 gates the guard on panel-win claims and this
card makes none).

**Advisory A-2 (non-blocking).** The `#SBATCH --job-name` is hardcoded
`…-s0` while the body is seed-parameterized. Harmless here — `submit.sh`
passes `--job-name` explicitly on the command line (which overrides the
header) and seed 0 is the only seed this card will ever run — but if
end-of-round confirmation ever reuses this script for seeds 1-2, the caller
**must** pass `--job-name=r1-s7_loss-B2-s${SEED}` explicitly. B1 dodged this
by leaving the header seedless.

## §6 — Blast radius (question 6)

`git diff round1-substrate..HEAD --stat` → **13 files, 1424 insertions, 0
deletions**, all under four allowed roots:

```
models_r1/mf_fno_transfer_film_s7loss_b2/{INSPIRATION.md,manifest.json,model.py,s7_losses.py,smoke_eval.py}
notes/{handoff_experiment_starter.md,handoff_experiment_builder.md}
scratchpad/{contract_smoke.json,contract_cache/<key>.json,contract_results/…/ifc_poisson_e2_s0.json}
scripts/{01_train_eval.sh,submit.sh,verify_vendor_pins.sh}
```

No path outside `models_r1/ scripts/ notes/ scratchpad/`. **No substrate
"fix" commits** (the live round-5 lesson). `git status --short` is clean —
`last.pt` (38 MB), `preds_test.npz` and `__pycache__` are gitignored and were
not committed, so no heavy artefacts entered git.

## §7 — §5 immutables and contract compliance (question 7)

| Immutable | Status |
|---|---|
| #1 data read-only | ✓ no touch to `benchmark_42/**` or `factory_root/data/**`; no regeneration; the family only reads via `panel_data`/loaders |
| #2 panel + guard fixed | ✓ single panel dataset scored; guard set not invoked and no panel-win claim made |
| #3 eval layer byte-untouched | ✓ **no `round1/eval/` path in the diff**; `project.yaml`, `program.md`, ADRs, subagent prompts all untouched |
| #4 one nRMSE definition | ✓ everything through `score_panel.py`; `nrmse_def_hash d3d0ade9…` matches the batch-0 comparator's hash exactly |
| #5 contract CLI fixed | ✓ `--dataset_dir --dataset_name --epochs --out --ckpt_dir --seed` (smoke_eval.py:402-407); both env knobs declared in `recipe.env` |
| #6 seeds + tier epochs fixed | ✓ seed 0 ∈ {0,1,2}; `epochs 200` == `tiers.smoke_epochs` |
| #7 guarded factory surfaces | ✓ nothing under `factory_root/{eval,baselines,references,scripts,data}/`, `factory.md`, or `mf_field/akash/**` in the diff |
| #8 checkpoint-resume | ✓ **verified by grep**, smoke_eval.py:275-316: writes `<ckpt_dir>/<arm_tag>/last.pt`, and reads `src = last if last.exists() else (contract_last if contract_last.exists() else None)` where `contract_last = ckpt_root/"last.pt"` — the literal contract path is honoured as a read fallback, with config-match guards on epochs/grid/modes_cap/arm_tag and mid-stage `stage`/`epoch`/`opt`/`sched`/`gen` restore |

**Scoring routes through `score_panel.py`.** No hand-rolled metric anywhere,
and the number entering `build_notes` came from `score_panel.py`'s own output
JSON, not from a bare `smoke_eval.py` invocation.

**Pre-falsified levers (§5).** None re-proposed. The three falsified levers
are WNO backbone swap, LF low-mode freezing and diffusion prior; this card
proposes **no mechanism at all** — it is a measurement on an existing,
already-built family. No FAIL trigger.

**Seeding.** `torch.manual_seed(args.seed); np.random.seed(args.seed)`
(smoke_eval.py:222), and `score_panel._run_one` additionally sets
`PYTHONHASHSEED` and `CUBLAS_WORKSPACE_CONFIG=:4096:8` in the child env.
`torch.manual_seed` covers CUDA. Python's stdlib `random` is not seeded — an
**inherited B1 property** that the zero-edit mandate forbids changing, and
`random` is not used in the training path. Not a new finding for B2.

**Smoke-test evidence (question 3.6 equivalent).** `build_notes[2]` cites the
full contract-tier `score_panel.py` command **and** the result files exist in
`scratchpad/` and are committed: `contract_smoke.json`,
`contract_results/mf_fno_transfer_film_s7loss_b2/ifc_poisson_e2_s0.json`, plus
the isolated `contract_cache/` entry. Isolation was correct — the builder
exported private `ROUND1_EVAL_RESULTS` **and** `ROUND1_EVAL_CACHE` into the
worktree scratchpad, so the shared eval layer's `results/` and `cache/` were
not touched by the smoke test.

**Advisory A-3 (non-blocking).** `manifest.json` still carries B1's
`"name": "mf_fno_transfer_film_s7loss"` and a `description`/`env_knobs` text
that says "card recipe.env sets amp". The builder's reasoning for leaving it
is correct and I verified it: `grep -n manifest round1/eval/*.py` returns
**nothing**, and `score_panel._run_one` derives family name, `out_dir` and
`ckpt_dir` from `Path(family_dir).name` alone. The stale field is inert to
every number this card produces, and editing it (though permitted by
`recipe._source`) would have weakened the five-way pin story for zero gain —
leaving it was the better call. *Guidance for the analyzer*: read the arm
from the result JSON's `s7_arm_tag` / `s7_env_seen`, **never** from
`manifest.json`, which describes B1's card.

**Advisory A-4 (non-blocking).** `INSPIRATION.md` is B1's and therefore cites
B1's prior_art, not B2's batch-2 D1 row. The zero-edit vendor mandate
(`recipe.env._source`: "NO .py BYTE MAY CHANGE", with only `manifest.json`'s
name field exempt) forbids updating it, and the locked `recipe` outranks the
generic contract expectation. Substantively this is fine: B2 introduces **no
new mechanism**, its own prior_art verdict is `preempted` ("Nothing
publishable"), and the family's actual mechanism is B1's — which
`INSPIRATION.md` cites correctly (li2020fno, perez2018film, beggs2025pdecond,
lyu2023mffno + the objective-side sources). No action.

**Note on the eval cache directory.** `01_train_eval.sh` exports
`ROUND1_EVAL_RESULTS` but not `ROUND1_EVAL_CACHE`, so `score_panel` will
*write* its cache entry to the default `round1/eval/cache/`. This is the
round-wide convention (B1, s5-B2, s1-B3 all do the same), the directory is
gitignored (`mffp_autoresearch/round1/.gitignore:4: eval/cache/`), and it is
the eval layer's own runtime state rather than an agent edit — immutable #3
("byte-untouched", i.e. no agent edits the eval *code*) is not engaged. With
`--no_cache` the read path is skipped entirely, so this cannot contaminate
the measurement.

---

## Submit-time instructions for the orchestrator

1. **Run the gate first, and read its output.** `submit.sh` already invokes
   `scripts/verify_vendor_pins.sh` under `set -euo pipefail`, so a drifted
   byte aborts before `sbatch`. Expect the line
   `[vendor-gate] all 5 pins match B1 @ 990f8891 — zero-edit vendor confirmed.`
   If any `FAIL` line appears: **hard-stop, do not "fix" it**, and route to
   the debugger — a drifted byte voids the card's entire integrity argument.
2. Submit with `bash <worktree>/scripts/submit.sh` (seed 0 only). Do **not**
   hand-roll an `sbatch` line; the wrapper supplies the `--job-name` override
   and the pre-`sbatch` `mkdir -p`.
3. Expect **one** job named `r1-s7_loss-B2-s0`, ~10-13 min of a 30 min
   walltime. If it pends on `ReqNodeNotAvail`/reservation, slurm_rules §3
   permits a p100 fallback — but note the walltime basis is an **H100**
   measurement (575 s), and p100 runs ~2-4× slower, so a p100 fallback
   **requires raising `--time` to at least `01:30:00`**. Do not fall back to
   p100 at the current 30 min.
4. **No screen job, no guard job, no seeds 1-2.** Their absence is by design
   and documented; do not "helpfully" add them.
5. On completion, the initial-analyzer must (a) read
   `${OUTPUTS_ROOT}/s7_loss/B2/eval/result_allen_cahn_s0.json`, (b) confirm
   `"cached": false` and `"env": {"MFFP_S7_LOSS": "rel", "MFFP_S7_STAGES":
   "both"}` **before** reading the number — a `cached: true` or a one-key
   `env` would mean the measurement did not happen — (c) confirm
   `s7_arm_tag == "arm_rel_both"` in the per-dataset JSON, and (d) classify
   into exactly one band using the **nRMSE** thresholds (`≤ 0.290216` → (a);
   `≥ 0.974993` → (b); else (c)), applying advisory A-1 to the 0.237
   sub-case.
6. Per `recipe._stream_closure`, s7_loss is to be marked **CLOSED** after
   this card regardless of which band fires.

---

*Reviewed by `code-reviewer`, attempt 1. Verdict PASS. Checklist 6/6.*
