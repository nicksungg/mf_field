# Iteration 1 — s7_loss, Batch 2

## 1. Design context considered

**From `summary_so_far.md` section 6 (unknowns).** One live unknown:
H-lambda ("lambda>1 is the sole cause") vs H-norm ("per-sample normalization is
fatal at high `hf_norm_spread`"). Both are consistent with every number in
`s7_loss-B1` part 5 and they imply opposite design rules. Nothing else in the
stream is decision-relevant.

**Prior-art verdict row for the chosen direction (D1), verbatim from
`websearches/s7_loss/batch_2/report.md`:**

> **D1** — part-7 lambda=1 disambiguation: one 200-epoch A0
> (`MFFP_S7_LOSS=rel`) on `sharp__allen_cahn_2d` alone | **preempted**
> (mechanism); open only as an in-repo *measurement* | ... | Nothing
> publishable. But no fetched source answers B1's normalization-vs-lambda
> question either, so the ~10 min run is the only way to close the standing
> design rule. Card must be framed as a measurement, never a contribution.

Citations on that row: https://arxiv.org/html/2410.23159v1 ;
https://ar5iv.labs.arxiv.org/html/2108.08481 (fetched, **does not** contain the
relative-vs-MSE claim) ; https://arxiv.org/html/2606.02997v1 (fetched, **does
not** contain the ablation) ; batch-1 C-REL row.

**Immutables block (program.md section 5), held verbatim:**

> 1. **Data is read-only.** `benchmark_42/**` and `factory_root/data/**`
>    untouched; no regeneration, no extra HF samples; N_hf per dataset fixed;
>    LF is always the real coarse solve (never downsampled HF — repo law).
> 2. **The panel and guard set are fixed** for the round (2.3).
> 3. **The eval layer is byte-untouched during the round.** No agent edits
>    `round1/eval/`, `project.yaml`, `program.md`, ADRs, or subagent prompts.
> 4. **One nRMSE definition** (2.1).
> 5. **Contract CLI fixed**: families expose the factory `smoke_eval.py`
>    signature; env knobs allowed ONLY if recorded in the card `recipe` (they
>    enter the cache key).
> 6. **Seeds {0,1,2} and per-tier epoch budgets fixed** (2.4).
> 7. **Guarded factory surfaces never edited**:
>    `factory_root/{eval,baselines,references,scripts,data}/`, `factory.md`,
>    `mf_field/akash/**`.
> 8. **Checkpoint-resume mandatory**: training resumes from `<ckpt_dir>/last.pt`
>    (the SLURM partition can preempt).
>
> Pre-falsified levers: WNO backbone swap (`wno_transfer_film`); LF low-mode
> freezing (`mf_fno_spectral`); diffusion prior for point accuracy
> (`mf_fno_diffprior`).

**Stream anchor.** Lever stream; anchor = the champion's certified panel geomean
(batch 0) = 6.703 [6.219, 7.102] (`state/anchors/s5_tuning.json`). This card
makes **no panel-geomean claim** (single dataset), so the operative comparators
are the two fixed per-dataset numbers below.

**Noise floor (`state/noise_floor.json`, `sharp__allen_cahn_2d`):**
`mean_skill` 16.33407079448426, `min_claimable_effect` **1.633407079448426**,
`per_seed_nrmse` [0.2638331949457305, 0.2637054122632834, 0.26393395849093787],
`spread` 0.014149916588777955 skill units.

**The two fixed comparators (both already certified, no extra run needed):**

| comparator | source | nRMSE | skill |
|---|---|---|---|
| MSE default, SAME family/tier/seed | `mffp_autoresearch_outputs/round1/batch0/eval/mf_fno_transfer_film__sharp__allen_cahn_2d_s0.json` (`env: {}`, epochs 200, seed 0) | **0.26383384013787387** | **16.334668349426035** |
| B1 `amp` lambda=4 endpoint | `experiment_cards/s7_loss/batch_1/B1.json` part 5 | **1.001375560628003** | **61.99787588859377** |

copy-LF reference nRMSE on this dataset = 0.016151772077279084
(`eval/copylf_baselines.json`, quoted in B1 part 5).

**B1 part 7's three pre-registered outcomes, transcribed verbatim** from
`experiment_cards/s7_loss/batch_1/B1.json` -> `7_gap_and_future.next_direction`
(identical text in the mechanism-analyzer handoff's "Suggested next direction"
pointer):

> Three pre-registerable outcomes, all informative: (a) A0 reaches ~0.26 nRMSE
> (the MSE default's level) -> lambda>1 is the sole cause, the per-sample
> relative objective itself is safe, and the design rule collapses to
> 'lambda <= 1'; (b) A0 also collapses to ~1.0 -> the per-sample normalization
> is fatal on high-spread data regardless of lambda, and the rule becomes 'do
> not normalize when hf_norm_spread >= ~10, with or without a gain term'; (c)
> A0 lands in between -> both ingredients contribute and the stream should stop,
> because no further loss-shape search can beat an MSE baseline it cannot even
> match on one dataset.

And the open question it answers, verbatim:

> Is the fatal ingredient the PER-SAMPLE NORMALIZATION or the EXPLICIT GAIN
> WEIGHT lambda>1? ... the only lambda=1 evidence in this card is the 2-epoch
> screen, where every arm including the untouched MSE default is still trivial
> (allen_cahn nRMSE 0.988-1.002), so the two hypotheses are observationally
> identical in everything actually run. Until that is settled, 'relative
> objectives destroy high-norm-spread datasets' and 'lambda>1 destroys them'
> are both consistent with every number in part 5, and they imply opposite
> design rules.

## 2. Proposal reasoning — alternatives weighed and rejected

**Alt A — a lambda ladder (A0 lambda=1, plus lambda=0.5 and lambda=2) to locate
the boundary.** Rejected. B1 part 6 already proves the boundary *analytically*:
the perverse-descent region and the vanishing escape drive `2 lambda/(lambda-1)
r` exist for lambda>1 and are "0% at lambda=1, algebraically impossible". A
lambda=2 arm would locate a number that changes no decision in a closing stream;
a lambda<1 arm probes a region the algebra already declares safe. Each arm costs
~10 min but dilutes the clean 3-way outcome map: with a ladder, outcome (c)
stops being a single interpretable band. Cost of the information: not worth the
loss of pre-registration sharpness.

**Alt B — add the D2 eps-floored denominator as a second arm.** Rejected twice
over. (i) Retrieval-refuted: Neural Radiosity 4.1 publishes
`L = ||r_theta/(sg(m_theta)+eps)||_2^2` verbatim
(https://ar5iv.labs.arxiv.org/html/2105.12319). (ii) Near-vacuous in-repo: our
denominator `||y||` is a constant w.r.t. theta, so stop-grad is a no-op, and the
floor is **already in the code path being run** —
`s7_losses.NORM_FLOOR = 1e-4`, `clamp(||y||, min=1e-4)`, the
`transolver_residual/smoke_eval.py:68` precedent. Adding it as an "arm" would be
adding a knob that is already on. (The orchestrator's state note said "D1+D2
objective ladder"; the batch-2 verdict retired D2 after that note was written —
`websearches/s7_loss/batch_2/report.md` "For the brainstormer" item 4: "Do NOT
propose D2 ... as the card's substance. ... Keep it as an implementation guard
inside D1 if the card wants one." It is already inside D1.)

**Alt C — run A0 on the full panel instead of allen_cahn alone.** Rejected. B1
part 7: "s7_loss B2 should NOT be another 6-dataset panel arm." The other five
datasets cannot separate H-lambda from H-norm: four of them have
`hf_norm_spread <= 2.55` (B1 M6) where the relative objective is a measured
no-op (cahn_hilliard's weighting differs from MSE's by 1%), and helmholtz is
unfalsifiable at this tier (floor 9.695 skill units) *and* a trivial-predictor
trap. Cost would be 37.7 min instead of ~10 min for zero added discriminating
power, and it would tempt a panel-geomean read on a stream with no live
hypothesis.

**Alt D — re-enter D4 (gain head) as an s7 card.** Rejected: `s1_poisson-B3`
(`MFFP_GAIN_HEAD=ladder_level_intercept`, status `analyzing`) is already running
that exact composition. Websearch item 5 forbids duplication.

**Alt E — skip the batch and close the stream now.** Rejected, narrowly. The
cost is ~10 GPU-min; the return is the *identity of the standing design rule*
that the round report will publish ("lambda <= 1 always" vs "never
per-sample-normalize at spread >~ 10"). Those are different rules for future
rounds and one of them is currently unsupported. B1's own recommendation is to
run this and *then* close; skipping would leave the M6 rule half-asserted.

**Alt F — a CPU-only / no-training diagnostic (e.g. simulate the lambda=1
trajectory from saved artifacts).** Rejected: the quantity in question is
"does the lambda=1 objective escape the origin over 200 epochs of *this*
optimizer trajectory". That is only observable by running it. B1's own
mechanism turns were CPU-only and are exactly why the question is still open.

**Chosen: D1, single arm, single dataset, as a `diagnostic` card.**

### 2.1 Why `card_type: diagnostic` (and the one letter-level deviation, disclosed)

Epistemic role: this card proposes no mechanism, claims no improvement, and can
"win" nothing — all three outcomes are informative and none is a contribution
(the verdict row: "Card must be framed as a measurement, never a
contribution"). It makes no panel-geomean claim and therefore no guard run is
owed (program.md 2.3 requires guard only "for any experiment claiming a panel
win").

**Deviation, stated plainly:** program.md 4.3 defines `diagnostic` as "a
measurement, **no training**: single run, no seeds 2-3". This card's measurement
instrument *is* a 200-epoch training run, because the measured quantity (does
the lambda=1 objective leave the origin?) only exists at the end of an
optimization trajectory — B1's 2-epoch screen is precisely the evidence that it
cannot be read earlier (all arms trivial, allen_cahn skill 61.15-62.91).
Every operational consequence of 4.3 holds unchanged: single run, seed 0 only,
no seeds 1-2, `expected_falsification` states what the measurement will show and
what would falsify the motivating hypothesis. Recorded here so the starter and
reviewer see it as a deliberate, argued choice rather than a mislabel.

### 2.2 ADR 0007: no screen required

ADR 0007's guardrails state: "**Diagnostics and spec-pre-directed slots are
exempt** (no candidate pool)." This card is both — a diagnostic, and
spec-pre-directed by B1 part 7. There is one arm, so there is nothing to screen
*between*; and the arm's plumbing is already proven at contract tier in B1's own
build (`build_notes` item 4: "A0(rel) 0.36672538257500825", finite, clean,
distinct from A-def, provenance keys present in the result JSON) plus the whole
panel at 2 epochs in `screen_table.md` (A0 row, `valid: yes`). A fresh
contract-tier job would re-measure numbers that already exist and that ADR 0007
forbids reporting anyway. **The single pre-submit gate is CPU-only and free**:
verify the vendored family's five file sha256s equal B1's (below), which proves
byte-identity of the substrate without a GPU — and which sidesteps the s5-B2
device-mixing trap (`state/orchestrator_flow.md` 2026-07-30T03:29Z) entirely,
because it is a file-content comparison, not a numeric one.

### 2.3 The three outcome bands, and why they are decidable

Partition of the seed-0 200-epoch `sharp__allen_cahn_2d` test nRMSE
(`splits.test_hf`, `metric_source: per_sample_mean`), each edge placed exactly
one certified `min_claimable_effect` (1.633407 skill units) away from its
comparator:

| outcome | skill band | nRMSE band | pre-stated interpretation (B1 part 7) |
|---|---|---|---|
| **(a)** | skill <= **17.968075** | nRMSE <= **0.290216** | "lambda>1 is the sole cause, the per-sample relative objective itself is safe, and the design rule collapses to 'lambda <= 1'" |
| **(c)** | 17.968075 < skill < 60.364469 | 0.290216 < nRMSE < 0.974993 | "both ingredients contribute and the stream should stop, because no further loss-shape search can beat an MSE baseline it cannot even match on one dataset" |
| **(b)** | skill >= **60.364469** | nRMSE >= **0.974993** | "the per-sample normalization is fatal on high-spread data regardless of lambda, and the rule becomes 'do not normalize when hf_norm_spread >= ~10, with or without a gain term'" |

Derivation: (a) edge = 16.334668 (MSE comparator skill) + 1.633407 (floor);
(b) edge = 61.997876 (lambda=4 endpoint skill) - 1.633407. Bands are exhaustive
and mutually exclusive, so exactly one interpretation fires. A result *below*
16.334668 - 1.633407 = 14.701 (nRMSE <= 0.237) is still outcome (a), noted in
the card as "(a) with an incidental improvement" — it would NOT be claimable as
an s7 win, because it is one dataset, one seed, and the stream's hypothesis
(an interface-aware objective fixes sharp-2D fusion) is about the panel.

**Separation vs run-to-run nondeterminism.** The round's measured H100
nondeterminism convention (`state/orchestrator_flow.md` 2026-07-30T03:29Z, s5-B2
debug return): "this family's GPU runs are NOT bitwise reproducible (1.9e-4 rel
helmholtz between two identical fresh same-job H100 runs; 6e-6 heat_local; 0.0
sod)". At the MSE level (nRMSE 0.263834), 1.9e-4 relative = 5.01e-5 nRMSE =
**0.0031 skill units**. So:

- the (a)|(c) boundary sits **1.633407 skill units** = **526x** the
  nondeterminism scale away from the MSE comparator;
- the (c)|(b) boundary sits 1.633407 skill units = 139x the nondeterminism
  scale at the lambda=4 level (0.0118 skill units there) away from the lambda=4
  endpoint;
- the (a) and (b) bands are **42.396 skill units apart**, i.e. **~1.4e4x** the
  nondeterminism scale.

Independently: the certified 3-seed allen_cahn seed spread is 0.014150 skill
units, so the floor 1.633407 is already **115x** the real seed noise on this
dataset (the floor is the conservative 10%-relative convention, not the measured
spread). **The bands are orders of magnitude apart** — this measurement cannot
be decided by nondeterminism under any of the three outcomes.

### 2.4 Substrate: byte-identical vendoring, zero code edits

The measurement is only valid if the code path is B1's. Vendor
`models_r1/mf_fno_transfer_film_s7loss` from branch `round1/exp-s7_loss-B1` @
`990f88916d38a0aac3af9a96e4b13b2601596596` (B1's `build_commit`) into
`models_r1/mf_fno_transfer_film_s7loss_b2` with **zero edits**. Verified
sha256-16 per file via `git show 990f8891:models_r1/mf_fno_transfer_film_s7loss/
<f> | sha256sum` (and the same values re-computed from B1's live worktree, so
the commit and the worktree agree):

| file | sha256-16 |
|---|---|
| `INSPIRATION.md` | `a4f96be8d8748e3d` |
| `manifest.json` | `cb1f04bea56ce342` |
| `model.py` | `80d8940d8b90a4ac` |
| `s7_losses.py` | `44e9b956a87aa187` |
| `smoke_eval.py` | `3969ebe420cd1e5a` |

Renaming the directory is safe and does not change the code identity:
`eval/score_panel.py::code_hash` hashes `f.name` (basename) + file bytes over
`rglob("*.py")` plus `models/_common` plus the eval files, then the env pairs —
the parent directory name is not in the hash. So the vendored family's code
contribution to `code_hash` is bit-identical to B1's; only the env differs
(by design: `rel` vs `amp`+`lambda`). The rename buys collision-freedom:
`_run_one` derives `out_dir` and `ckpt_dir` from `family_dir.name`, so B2's
result JSONs and checkpoints cannot land on B1's.

Manifest note for the builder: `manifest.json` will need its `name` field to
match the new dir if the contract requires it; that is the ONLY permissible
edit, and if it is made, the card must record the new sha256 and state that no
`.py` byte changed (so `code_hash` is provably unchanged, since `manifest.json`
is not a `.py` file and does not enter `code_hash` at all).

### 2.5 Knob names — read from the implementation, not from memory

From `worktrees/s7_loss/B1/models_r1/mf_fno_transfer_film_s7loss/s7_losses.py`
(`parse_env`):

- `MFFP_S7_LOSS` in `("mse","rel","amp","band")`; `rel` -> `mean_i rel_i^2`,
  which is the scored metric's square. **`MFFP_S7_LAMBDA` is REQUIRED only for
  `amp`** and is *not* read for `rel` — so the recipe must NOT set it. (The
  "lambda=1" in B1 part 7 is descriptive: `amp` at lambda=1.0 is bit-identical
  to `rel`, proven in B1 `build_notes` item 2: "19.947361769477702 ==
  19.947361769477702 ... multiplying by exactly 1.0 is exact in IEEE-754".)
- `MFFP_S7_STAGES` defaults to `both`; set it explicitly to `both` to match
  B1's A0 screen row and A1a's recipe.
- Resulting `arm_tag` = `arm_rel_both` (from `parse_env`:
  `arm_tag = f"arm_rel_{stages}"`), which is also the checkpoint subdirectory
  (`smoke_eval.py`: `ckpt_dir = ckpt_root / S7["arm_tag"]`) — so B2's
  checkpoints are arm-isolated from B1's `arm_amp_lam4_both` by construction.

## 3. Proposal

**Category**: `objective-disambiguation-measurement` (loss-mechanism
attribution; no new mechanism proposed).

**Card type**: `diagnostic` (see 2.1 for the disclosed letter-level deviation
from program.md 4.3's "no training").

**Motivation**: the batch-2 prior-art verdict row for D1, verbatim —
"**preempted** (mechanism); open only as an in-repo *measurement* ... Nothing
publishable. But no fetched source answers B1's normalization-vs-lambda question
either, so the ~10 min run is the only way to close the standing design rule.
Card must be framed as a measurement, never a contribution."
`s7_loss-B1` is falsified with the mechanism fully resolved, and it left exactly
one binary open: `s7_loss-B1` part 7 — "Is the fatal ingredient the PER-SAMPLE
NORMALIZATION or the EXPLICIT GAIN WEIGHT lambda>1? ... they imply opposite
design rules." The batch-2 loop retrieval-refuted every remaining loss-shape
direction (D2/D3/D5 preempted with fetched citations; D4's open MF slice is
already running as `s1_poisson-B3`), so this measurement is the stream's last
decision-relevant act.

**Concrete config**: one seed-0, 200-epoch run of arm **A0** on
`sharp__allen_cahn_2d` **alone**, on a byte-identical vendored copy of B1's
family (2.4), env `MFFP_S7_LOSS=rel MFFP_S7_STAGES=both`, through
`eval/score_panel.py` with `--no_cache` and a private
`ROUND1_EVAL_RESULTS`. No screen job (2.2), no guard run (no panel claim), no
seeds 1-2 (ADR 0004). Pre-submit gate: the five-file sha256 byte-identity check
(CPU, seconds). The card reports: seed-0 test nRMSE + skill, which of the three
bands it lands in, the pre-stated interpretation for that band, the logged
`hf_norm_spread_train/test` (22.68 / 22.00 expected, from B1), the
`shape`/`gain` endpoint decomposition from `preds_test.npz`, and wall-clock.

**Recipe** (see report.md for the JSON the starter transcribes).

**Expected outcome**: **outcome (a)** is the mechanism-supported prediction —
B1 part 6/M2 and the handoff both say "lambda=4 is the culprit, not per-sample
normalisation", and at lambda=1 the objective IS the scored `rel^2` with escape
drive `2(1-alpha) > 0` by construction. So the point prediction is
nRMSE in [0.24, 0.29] / skill in [14.7, 18.0], i.e. within one floor of the MSE
comparator (0.263834 / 16.334668). Every band edge is >= 1.633407 skill units
(>= 526x the 0.0031-skill-unit nondeterminism scale, and 115x the certified
0.014150 seed spread) from its comparator, so all three outcomes clear the
noise floor.

**Expected falsification**: *If the run's seed-0 200-epoch
`sharp__allen_cahn_2d` test nRMSE is >= 0.974993 (skill >= 60.364469, i.e.
within one certified `min_claimable_effect` of B1's lambda=4 endpoint
1.001375560628003 / 61.99787588859377), then hypothesis M2 ("lambda=4 is the
culprit, not per-sample normalisation") is FALSIFIED — outcome (b) — and B1's
standing design rule is replaced by "do not per-sample-normalize when
`hf_norm_spread >= ~10`, with or without a gain term"; if the nRMSE is
<= 0.290216 (skill <= 17.968075, i.e. within one floor of the MSE comparator
0.26383384013787387 / 16.334668349426035) then M2 is CONFIRMED — outcome (a) —
and the rule collapses to "lambda <= 1"; if it lands strictly between
(0.290216 < nRMSE < 0.974993) then both ingredients contribute — outcome (c) —
and no loss-shape lever can be recommended.* Pre-registered risk per
program.md 12.7: this card trades nothing, because it changes only the training
objective on one dataset and makes no panel or bulk-vs-interface claim; the
program.md-12.7 interface/bulk trade-off risk is therefore not applicable and is
recorded as such rather than omitted. Pre-registered non-claim: outcome (a) with
nRMSE below 0.237 is **not** an s7 win — one dataset, one seed, no panel
geomean.

**Anchor reference**: `null` (lever stream; program.md 4.5 — own-stream anchor
implicit; the `card_id` form is reserved for `s5_tuning` batches >= 2). The two
operative comparators are named numerically in part 4 instead.

**Stream-closure recommendation** (carried into report.md for the mentor /
maintainer): after this card completes, **`s7_loss` should be marked closed
regardless of outcome** — every loss-shape lever is now either falsified in-repo
(B1: the objective-level falsification, plus F5/F6/F8 killing the
pfc/cahn_hilliard direction) or retrieval-refuted with fetched citations (D2,
D3, D4, D5), and part 6 M7 bounds what any loss-only lever can do on a substrate
that cannot see which regime a sample is in.

## 4. Status

- **Slot covered**: yes — one proposal, `card_type: diagnostic`.
- **Skipped**: no.
- **Reopen candidates resolved**: none exist for this stream (B1 is
  `complete` / `reopen_candidate: false`).
- **Immutables self-check**: see section 5 — **pass (10/10)**, no revision
  needed, so no `iteration_2.md`.

## 5. Immutables self-check (10 items, positive evidence each)

1. **Data read-only.** The run reads exactly one existing dataset directory,
   `mf_field/factory_mffp/data/sharp__allen_cahn_2d`, opened read-only by
   `eval/panel_data.py` through `score_panel._run_one` (which only passes
   `--dataset_dir`); the proposal adds no generation step, no HF samples, and no
   LF construction — it is the same dataset B1 already ran on, at the same
   N_hf, and the only "new" per-dataset quantity is `hf_norm_spread`, computed
   from the loaded arrays in memory.
2. **Panel + guard set fixed.** The card scores one dataset that is already a
   panel member (`project.yaml panel[2] == sharp__allen_cahn_2d`), does not add
   or remove any panel/guard entry, and requests no guard run because it makes
   no panel-win claim (program.md 2.3 requires guard only for panel-win
   claims).
3. **Eval layer / spec untouched.** The proposal is executed by invoking the
   existing `eval/score_panel.py` CLI with `--family_dir --datasets --epochs
   --seed --env --no_cache --out`; every knob it needs already exists in that
   CLI (verified by reading `score_panel.py` argparse: `--env nargs="*"`,
   `--no_cache`), so nothing under `round1/eval/`, `project.yaml`, `program.md`,
   `docs/adr/`, or `subagents/` requires an edit.
4. **One nRMSE definition.** The score comes from the family's
   `finalize_and_write` -> `round1/eval/nrmse.py` path with
   `nrmse_def_hash = d3d0ade9191c13bacc40702f3eb26ad290e01641cacee22a1d2233b74c035850`
   (the value recorded in B1 part 5 `_provenance` and in the batch-0 comparator
   JSON) — identical for both comparators; the `rel` training objective lives
   only inside `smoke_eval.py`'s training loop (`s7_losses.py` module docstring:
   "these functions are used ONLY inside the training loop"), and B1's A2ctl
   control already demonstrated the scored path is unaffected by the objective
   choice.
5. **Contract CLI fixed.** The family exposes the unmodified factory signature
   (`smoke_eval.py` line 21: "Contract: --dataset_dir --dataset_name --epochs
   --out --ckpt_dir --seed") and is vendored with zero edits; both env knobs
   used (`MFFP_S7_LOSS`, `MFFP_S7_STAGES`) are declared in the recipe `env`
   block and therefore enter the cache key
   (`score_panel.code_hash` hashes `f"{k}={v}"` for every sorted env pair).
6. **Seeds and tier epochs fixed.** `seeds: [0]` and `epochs: 200` — seed 0 is
   in {0,1,2} and 200 is exactly the smoke tier from `project.yaml
   tiers.smoke_epochs`; ADR 0004 (strict 1-seed in-round) and program.md 4.3
   (diagnostics: "no seeds 2-3") both forbid launching seeds 1-2 here, and the
   proposal launches none.
7. **Guarded factory surfaces untouched.** The only write target is a new
   directory `models_r1/mf_fno_transfer_film_s7loss_b2` inside the B2 worktree;
   the vendoring source is read via `git show <commit>:<path>` (a read
   operation) from the round's own `worktrees/` tree, and no path under
   `mf_field/factory_mffp/{eval,baselines,references,scripts,data}`,
   `factory.md`, or `mf_field/akash/` appears anywhere in the recipe or the
   run command.
8. **Checkpoint-resume implementable.** It is not merely implementable, it is
   already implemented and drilled on this exact code: `smoke_eval.py` writes
   `<ckpt_dir>/<arm_tag>/last.pt` plus the literal contract path
   `<ckpt_dir>/last.pt` (lines 275-278) with mid-stage RNG-neutral periodic
   saves, and B1 `build_notes` item 5 records a SIGKILL-at-epoch-3/8 drill whose
   resumed run was **bit-identical** to the uninterrupted one
   (0.3469903010539124 both). Vendoring is byte-identical, so this property
   transfers unchanged; the arm tag `arm_rel_both` keeps it isolated from B1's
   `arm_amp_lam4_both`.
9. **Falsification threshold exceeds the noise floor (numbers quoted).**
   `state/noise_floor.json` -> `sharp__allen_cahn_2d.min_claimable_effect =
   1.633407079448426` skill units (measured 3-seed `spread` 0.014149916588777955).
   Both band edges are exactly one floor from their comparator: outcome-(a) edge
   skill 17.968075 = 16.334668349426035 + 1.633407079448426 (nRMSE 0.290216);
   outcome-(b) edge skill 60.364469 = 61.99787588859377 - 1.633407079448426
   (nRMSE 0.974993). The (a) and (b) bands are 42.396 skill units apart. The
   H100 nondeterminism convention (1.9e-4 relative on outputs,
   `state/orchestrator_flow.md` 2026-07-30T03:29Z) is 0.0031 skill units at the
   MSE level — the thresholds exceed it by 526x and the band separation by
   ~1.4e4x. `sharp__allen_cahn_2d` is the only dataset cited.
10. **Not a pre-falsified lever re-proposed as-is.** The three pre-falsified
    levers are WNO backbone swap (`wno_transfer_film`), LF low-mode freezing
    (`mf_fno_spectral`), and the diffusion prior (`mf_fno_diffprior`) — all
    architecture/backbone changes; this card changes no architecture at all
    (`model.py` sha256-16 `80d8940d8b90a4ac`, byte-identical to the champion's).
    The nearest *in-round* falsification is `s7_loss-B1` itself (arm A1a,
    `amp` lambda=4, falsified + cratered); the difference is that this card
    does not re-propose that arm or any variant of it as a lever — it runs the
    A0 **control** that B1 pre-registered but never promoted, as a measurement
    with no success condition, precisely to attribute B1's failure. That is the
    "attack the mechanism behind a falsified lever" clause used in its weakest
    form: no claim, only attribution.
