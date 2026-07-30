# Brainstormer Report — Stream `s7_loss`, Batch 2

**Stream**: `s7_loss`
**Batch**: 2
**Total iterations**: 1
**Slot filled**: 1 / 1 (no skip)
**Reopen candidates resolved**: 0 (none exist — `s7_loss-B1` is `complete`,
`reopen_candidate: false`)

## Slot

- **Category**: `objective-disambiguation-measurement` — attribute
  `s7_loss-B1`'s collapse to its two candidate ingredients (per-sample
  normalization vs the explicit gain weight lambda>1). No new mechanism is
  proposed.

- **Card type**: `diagnostic`.
  *Disclosed letter-level deviation*: program.md 4.3 defines `diagnostic` as
  "a measurement, **no training**". This card's measurement instrument is a
  200-epoch training run, because the measured quantity — does the lambda=1
  objective escape the origin? — only exists at the end of an optimization
  trajectory. B1's 2-epoch screen is the proof it cannot be read earlier (all
  arms trivial on allen_cahn, skill 61.15-62.91;
  `.../s7_loss/B1/screen/screen_table.md`). Every operational consequence of
  4.3 holds: single run, seed 0 only, no seeds 1-2, and the
  `expected_falsification` clause states what the measurement will show and
  what falsifies the motivating hypothesis. Rationale in
  [iteration_1.md](iteration_1.md) 2.1.

- **Motivation**: the batch-2 prior-art verdict row for **D1**, verbatim:
  "**preempted** (mechanism); open only as an in-repo *measurement* ...
  **Nothing publishable. But no fetched source answers B1's
  normalization-vs-lambda question either, so the ~10 min run is the only way to
  close the standing design rule. Card must be framed as a measurement, never a
  contribution.**"
  `s7_loss-B1` is **falsified + cratered** with the mechanism fully resolved
  (part 6: `amp(lambda)` has the origin as a stationary point; escape drive
  `2 lambda/(lambda-1) r -> 0` for lambda>1; 29% of allen_cahn samples in the
  perverse-descent region; **0% at lambda=1, algebraically impossible**), and it
  left exactly one binary open (part 7, verbatim): *"Is the fatal ingredient the
  PER-SAMPLE NORMALIZATION or the EXPLICIT GAIN WEIGHT lambda>1? ... the only
  lambda=1 evidence in this card is the 2-epoch screen, where every arm
  including the untouched MSE default is still trivial (allen_cahn nRMSE
  0.988-1.002), so the two hypotheses are observationally identical in
  everything actually run. Until that is settled, 'relative objectives destroy
  high-norm-spread datasets' and 'lambda>1 destroys them' are both consistent
  with every number in part 5, and they imply opposite design rules."*
  The batch-2 loop retrieval-refuted every other loss-shape direction (D2 Neural
  Radiosity 4.1; D3 FACL; D5 MFFM; D4's open MF slice is already running as
  `s1_poisson-B3`), so this is the stream's last decision-relevant act.

- **Concrete config**: one seed-0, **200-epoch** run of B1's pre-registered
  control arm **A0** (`MFFP_S7_LOSS=rel`, i.e. the objective *is* the scored
  `rel^2`, equivalently `amp` at lambda=1 — B1 `build_notes` item 2 proved
  `amp(lambda=1.0)` bit-identical to `rel`) on **`sharp__allen_cahn_2d` alone**,
  on a **byte-identical, zero-edit vendored copy** of B1's family. Run through
  `eval/score_panel.py --no_cache` with a private `ROUND1_EVAL_RESULTS`.
  - **No screen job** — ADR 0007 guardrail: "Diagnostics and spec-pre-directed
    slots are exempt (no candidate pool)". This card is both, has one arm (so
    there is nothing to screen *between*), and its arm's plumbing is already
    proven at contract tier inside B1 (`build_notes` item 4: "A0(rel)
    0.36672538257500825", clean, finite, distinct from A-def; plus the full
    panel A0 row in `screen_table.md`, `valid: yes`). Re-screening would
    re-measure numbers that already exist and that ADR 0007 forbids reporting.
  - **No guard run** — the card makes no panel-win claim (program.md 2.3 gates
    guard runs on panel-win claims); it scores one dataset and reports no
    geomean.
  - **No seeds 1-2** — ADR 0004 + program.md 4.3.
  - **Pre-submit gate (CPU, seconds, no GPU)**: assert the five vendored files'
    sha256 equal B1's, listed in the recipe `_source`. This is the substrate
    equivalence proof, and being a file-content comparison it is immune to the
    device-mixing trap that voided s5-B2's first screen
    (`state/orchestrator_flow.md` 2026-07-30T03:29Z).
  - **Reported by the card**: seed-0 `sharp__allen_cahn_2d` test nRMSE +
    skill; which of the three bands it lands in and that band's **pre-stated**
    interpretation; the family's logged `hf_norm_spread_train/test` (B1
    measured 22.68 / 22.00); the endpoint shape/gain decomposition from the
    run's own `preds_test.npz`; wall-clock (B1's allen_cahn leg: 575.0 s
    training).

- **Recipe**:

```json
{
  "base_family": "mf_fno_transfer_film_s7loss",
  "base_commit": "990f88916d38a0aac3af9a96e4b13b2601596596",
  "family_dir": "models_r1/mf_fno_transfer_film_s7loss_b2",
  "datasets": "sharp__allen_cahn_2d",
  "epochs": 200,
  "seeds": [0],
  "env": {
    "MFFP_S7_LOSS": "rel",
    "MFFP_S7_STAGES": "both",
    "_note": "keys prefixed _ are card directives, NOT passed to --env. The --env set is exactly {MFFP_S7_LOSS=rel, MFFP_S7_STAGES=both}. MFFP_S7_LAMBDA is deliberately ABSENT: s7_losses.parse_env reads it only for MFFP_S7_LOSS=amp and would ignore it here; 'lambda=1' in B1 part 7 is descriptive, and B1 build_notes item 2 proved amp(lambda=1.0) is BIT-IDENTICAL to rel (19.947361769477702 == 19.947361769477702). Resulting arm_tag = arm_rel_both.",
    "_source": "VENDOR ZERO-EDIT from branch round1/exp-s7_loss-B1 @ 990f88916d38a0aac3af9a96e4b13b2601596596, path models_r1/mf_fno_transfer_film_s7loss -> models_r1/mf_fno_transfer_film_s7loss_b2. Verify each file with `git show 990f8891:models_r1/mf_fno_transfer_film_s7loss/<f> | sha256sum` (sha256-16): INSPIRATION.md a4f96be8d8748e3d, manifest.json cb1f04bea56ce342, model.py 80d8940d8b90a4ac, s7_losses.py 44e9b956a87aa187, smoke_eval.py 3969ebe420cd1e5a (all five re-confirmed against B1's live worktree). NO .py BYTE MAY CHANGE: eval/score_panel.py::code_hash hashes basename+bytes over rglob('*.py') (the parent dir name is NOT in the hash), so a zero-edit vendor keeps the code contribution to code_hash bit-identical to B1's while the rename gives collision-free out_dir/ckpt_dir (score_panel._run_one derives both from family_dir.name). The ONLY permitted edit is manifest.json's name field if the contract requires it; manifest.json is not a .py file and does not enter code_hash, and any such edit must be recorded in build_notes with the new sha256 plus the statement that no .py byte changed. Never touch mf_field/factory_mffp/{eval,baselines,references,scripts,data}, factory.md, mf_field/akash/**, or round1/{eval,tools}/.",
    "_run": "one call: score_panel.py --family_dir <worktree>/models_r1/mf_fno_transfer_film_s7loss_b2 --datasets sharp__allen_cahn_2d --epochs 200 --seed 0 --no_cache --env MFFP_S7_LOSS=rel --env MFFP_S7_STAGES=both --out <outputs>/s7_loss/B2/eval/result_allen_cahn_s0.json, with ROUND1_EVAL_RESULTS=<outputs>/s7_loss/B2/eval/results exported. --no_cache is MANDATORY (s5-B2 debug lesson) even though the env differs from B1's and therefore already yields a different code_hash.",
    "_gate": "PRE-SUBMIT, CPU-ONLY, NO GPU: the five sha256-16 values in _source must match exactly. This replaces the usual default-equivalence screen and is immune to GPU nondeterminism because it compares file bytes, not numbers. B1's own A-def bitwise default-equivalence (|delta nRMSE| = 0.0 vs the untouched factory family on ext__helmholtz_2d and ifc_poisson) is inherited unchanged by byte-identity.",
    "_no_screen": "ADR 0007: 'Diagnostics and spec-pre-directed slots are exempt (no candidate pool).' One arm, nothing to screen between; contract-tier plumbing for exactly this arm already exists in B1 build_notes (A0 ifc_poisson 0.36672538257500825) and B1's screen_table.md A0 row (valid: yes).",
    "_no_guard": "No guard run: no panel-win claim is made (program.md 2.3 gates the guard on panel-win claims). Single dataset, no geomean reported.",
    "_ckpt": "smoke_eval.py writes <ckpt_dir>/arm_rel_both/last.pt AND the literal contract path <ckpt_dir>/last.pt, with RNG-neutral periodic mid-stage saves; B1's SIGKILL-at-epoch-3/8 drill resumed BIT-IDENTICALLY (0.3469903010539124). arm_rel_both cannot collide with B1's arm_amp_lam4_both.",
    "_sbatch": "partition gpu, --gres=gpu:h100:1 (ADR 0005), --time=00:30:00, job name r1-s7_loss-B2-s0, logs under mffp_autoresearch_outputs/round1/s7_loss/B2/slurm/. Ledger basis: B1 part 5 per_dataset_train_seconds sharp__allen_cahn_2d = 575.0 s (9.6 min) on 1x H100 for this exact family/tier/dataset; 30 min is ~3x headroom including venv start, data load and eval/IO.",
    "_comparators": "TWO fixed, already-certified numbers, no extra run: (1) MSE default, SAME family/tier/seed — mffp_autoresearch_outputs/round1/batch0/eval/mf_fno_transfer_film__sharp__allen_cahn_2d_s0.json, env {}, epochs 200, seed 0: nRMSE 0.26383384013787387, skill 16.334668349426035; (2) B1's amp lambda=4 endpoint (card part 5): nRMSE 1.001375560628003, skill 61.99787588859377. copy-LF reference nRMSE 0.016151772077279084. Certified 3-seed anchor mean_skill 16.33407079448426, min_claimable_effect 1.633407079448426, seed spread 0.014149916588777955.",
    "_outcome_bands": "EXHAUSTIVE, MUTUALLY EXCLUSIVE 3-way partition of the seed-0 200-epoch sharp__allen_cahn_2d test nRMSE (splits.test_hf, metric_source per_sample_mean); each edge is exactly one certified min_claimable_effect (1.633407079448426 skill units) from its comparator. (a) nRMSE <= 0.290216 (skill <= 17.968075) -> B1 part 7: 'lambda>1 is the sole cause, the per-sample relative objective itself is safe, and the design rule collapses to lambda <= 1'. (c) 0.290216 < nRMSE < 0.974993 (17.968075 < skill < 60.364469) -> B1 part 7: 'both ingredients contribute and the stream should stop, because no further loss-shape search can beat an MSE baseline it cannot even match on one dataset'. (b) nRMSE >= 0.974993 (skill >= 60.364469) -> B1 part 7: 'the per-sample normalization is fatal on high-spread data regardless of lambda, and the rule becomes do not normalize when hf_norm_spread >= ~10, with or without a gain term'. Sub-case recorded in advance: nRMSE <= 0.237 (skill <= 14.701) is still outcome (a) 'with an incidental improvement' and is explicitly NOT claimable as an s7 win (one dataset, one seed, no panel geomean).",
    "_stream_closure": "After this card completes, s7_loss should be marked CLOSED regardless of which band fires — every loss-shape lever is now either falsified in-repo (B1 objective-level falsification; F5/F6/F8 killing the pfc/cahn_hilliard direction) or retrieval-refuted with fetched citations (D2 Neural Radiosity, D3 FACL, D4 DiSOL with the open MF slice owned by s1_poisson-B3, D5 MFFM), and B1 part 6 M7 bounds what any loss-only lever can do on a substrate that cannot see which regime a sample is in."
  }
}
```

- **Expected outcome**: **outcome (a)**. B1 part 6 M2 and the mechanism-analyzer
  handoff both state "**lambda=4 is the culprit, not per-sample normalisation**";
  at lambda=1 the objective IS the scored `rel^2` and the drive on the
  target-aligned component is `2(1-alpha) > 0` by construction, so the origin
  stationary point that killed A1a does not exist. Point prediction: nRMSE in
  **[0.24, 0.29]**, skill in **[14.7, 18.0]** — i.e. within one certified floor
  of the MSE comparator (0.26383384013787387 / 16.334668349426035), a **Delta of
  ~-45.7 skill units vs B1's lambda=4 endpoint** (61.998).
  **Vs the noise floor**: every band edge sits exactly 1.633407079448426 skill
  units from its comparator, which is **115x** the certified 3-seed allen_cahn
  seed spread (0.014149916588777955) and **526x** the H100 run-to-run
  nondeterminism scale (1.9e-4 relative on outputs =
  5.01e-5 nRMSE = 0.0031 skill units at the MSE level;
  `state/orchestrator_flow.md` 2026-07-30T03:29Z, s5-B2 debug return: "this
  family's GPU runs are NOT bitwise reproducible (1.9e-4 rel helmholtz between
  two identical fresh same-job H100 runs)"). The (a) and (b) bands are
  **42.396 skill units apart = ~1.4e4x** that scale. **The bands are orders of
  magnitude apart** — no outcome of this measurement can be produced by
  nondeterminism.

- **Expected falsification**: *If the run's seed-0 200-epoch
  `sharp__allen_cahn_2d` test nRMSE is **>= 0.974993** (skill >= 60.364469,
  within one certified `min_claimable_effect` of B1's lambda=4 endpoint
  1.001375560628003 / 61.99787588859377) then B1's mechanism hypothesis M2
  ("lambda=4 is the culprit, not per-sample normalisation") is **FALSIFIED**
  (outcome b) and the standing design rule becomes "do not per-sample-normalize
  when `hf_norm_spread >= ~10`, with or without a gain term"; if it is
  **<= 0.290216** (skill <= 17.968075, within one floor of the same-substrate
  MSE comparator 0.26383384013787387 / 16.334668349426035) then M2 is
  **CONFIRMED** (outcome a) and the rule collapses to "lambda <= 1"; if it lands
  strictly between (0.290216 < nRMSE < 0.974993, outcome c) then **both**
  ingredients contribute and no loss-shape lever can be recommended.* Each of
  the three outcomes maps to a distinct, pre-stated interpretation and the
  partition is exhaustive, so exactly one fires. Pre-registered non-claim:
  outcome (a) even with nRMSE below 0.237 is **not** an s7 win (one dataset, one
  seed, no panel geomean). Pre-registered risk per program.md 12.7 (interface
  upweighting trading bulk accuracy for rel-L2): **not applicable** — this arm
  does no interface upweighting, changes only the per-sample normalization of
  the training loss, and makes no bulk-vs-interface claim; recorded explicitly
  rather than omitted.

- **Prior-art verdict quoted** (verbatim, from
  `websearches/s7_loss/batch_2/report.md` "Prior-art verdict", row D1):

  > **D1** — part-7 lambda=1 disambiguation: one 200-epoch A0
  > (`MFFP_S7_LOSS=rel`) on `sharp__allen_cahn_2d` alone | **preempted**
  > (mechanism); open only as an in-repo *measurement* |
  > https://arxiv.org/html/2410.23159v1 ;
  > https://ar5iv.labs.arxiv.org/html/2108.08481 (fetched, **does not** contain
  > the relative-vs-MSE claim) ; https://arxiv.org/html/2606.02997v1 (fetched,
  > **does not** contain the ablation) ; batch-1 C-REL row | Nothing
  > publishable. But no fetched source answers B1's normalization-vs-lambda
  > question either, so the ~10 min run is the only way to close the standing
  > design rule. Card must be framed as a measurement, never a contribution.

  Supporting refutation rows (why nothing else was proposed):
  D2 **preempted** — https://ar5iv.labs.arxiv.org/html/2105.12319 (Neural
  Radiosity 4.1, formula verbatim), https://arxiv.org/html/2606.02997v1;
  D3 **preempted** — https://arxiv.org/html/2410.23159v1 (FACL: decomposition
  **and** the 100%-FCL-first annealed schedule);
  D4 **preempted-but-MF-composition-open** —
  https://arxiv.org/html/2601.09143v1 (DiSOL 4.1) — "**this is architecture and
  s1_poisson-B3's gain-head card is already running it — s7 must not duplicate
  it**";
  D5 **preempted** — https://arxiv.org/html/2605.16118v1 (MFFM).

- **Immutables self-check**: **pass (10/10)**, no revision required (single
  iteration). Full positive evidence per item in
  [iteration_1.md](iteration_1.md) section 5. Headlines: (1) one existing
  dataset dir, read-only through `score_panel._run_one`; (2) `sharp__allen_cahn_2d`
  is already `project.yaml panel[2]`, no panel/guard edit, no guard run owed;
  (3) executed entirely through the existing `score_panel.py` CLI flags
  (`--env`, `--no_cache` verified present in its argparse); (4) same
  `nrmse_def_hash d3d0ade9...c035850` as both comparators, the objective lives
  only in the training loop; (5) unmodified factory signature, both env knobs in
  the recipe and hence in `code_hash`; (6) `seeds [0]`, `epochs 200` =
  `tiers.smoke_epochs`, no seeds 1-2 launched; (7) writes only a new dir inside
  the B2 worktree, vendoring via `git show` (read); (8) resume already
  implemented **and drilled bit-identically** on this exact code (B1
  `build_notes` item 5); (9) both thresholds are exactly one
  `min_claimable_effect` = 1.633407079448426 skill units from their comparators
  vs a 0.014149916588777955 seed spread and a 0.0031-skill-unit nondeterminism
  scale; (10) nearest pre-falsified/falsified item is `s7_loss-B1` arm A1a
  itself — this card re-proposes **nothing** from it as a lever, it runs B1's
  own never-promoted A0 **control** as an attribution measurement with no
  success condition, and touches no architecture (`model.py` sha256-16
  `80d8940d8b90a4ac`, byte-identical to the champion's).

- **Anchor reference**: `null` (lever stream; program.md 4.5 — the own-stream
  anchor is implicit and the `card_id` form is reserved for `s5_tuning` batches
  >= 2). The two operative comparators are stated numerically in the recipe
  `_comparators` and in part 4 instead.

- **Source iteration**: [iteration_1.md](iteration_1.md)

## Reopen candidates

| Candidate | Verdict (retry/drop) | Eased conditions | Source iteration |
|---|---|---|---|
| *(none)* | — | `s7_loss-B1` is `status: complete`, `reopen_candidate: false`; it is the only prior card in the stream and was never skipped | [iteration_1.md](iteration_1.md) 4 |

## Skipped slot

Not applicable — the slot is filled.

## Stream-closure recommendation

**After this card completes, `s7_loss` should be marked CLOSED — regardless of
which outcome band fires.** Every loss-shape lever the stream can own is now
either falsified in-repo or retrieval-refuted with fetched citations:

| lever | status | evidence |
|---|---|---|
| shape/gain reweighted objective (lambda>1) | falsified in-repo | `s7_loss-B1` part 5 (falsified + cratered) + part 6 origin-stationary-point mechanism |
| per-sample-normalized objective aimed at pfc / cahn_hilliard | pre-falsified in-repo | B1 F5/F6/F8 — collapse set is MSE-shared (overlap 1.00 / 0.92, Spearman 0.979 / 0.810): a dataset property, not an objective property |
| eps-floored / stop-gradient relative loss (D2) | retrieval-refuted + near-vacuous in-repo | https://ar5iv.labs.arxiv.org/html/2105.12319 ; our denominator is already theta-independent and the 1e-4 floor is already in the code path |
| shape-first curriculum repair (D3) | retrieval-refuted + moot | https://arxiv.org/html/2410.23159v1 ; lambda <= 1 removes the pathology algebraically |
| target-level shape/gain reparameterization (D4) | retrieval-refuted except one MF slice, and that slice is owned elsewhere | https://arxiv.org/html/2601.09143v1 ; `s1_poisson-B3` is running it |
| residual-target supervision (D5) | retrieval-refuted + owned in-repo | https://arxiv.org/html/2605.16118v1 ; `s2_beyond_copy-B2` (geomean 0.380) |

Plus the structural bound: B1 part 6 **M7** and the LF-visibility finding (the
collapse label is readable from the LF field at AUC 0.099 / 0.102 but the best
of 19 condition coordinates reaches |AUC-0.5| = 0.067, and 0 of 27 families read
the test LF at inference) mean **no loss-only lever can make this substrate
regime-aware**, because the substrate never sees the regime. Both the B1 card's
own recommendation ("the honest recommendation is to close s7_loss after the
one-dataset lambda=1 measurement") and the batch-2 websearch ("Honest option on
the table ... This loop's retrieval evidence supports that") point the same way.

**What each outcome contributes to the round report** (all three are publishable
as *methodology*, none as a contribution):

- **(a)** — the standing design rule is confirmed and sharpened to **"lambda <= 1
  always"**: a per-sample-normalized training objective is safe when it equals
  the scored metric, and the entire B1 failure is attributable to the gain
  over-weight. Round report gets: a clean negative result with an exact,
  algebraically-derived boundary, plus the reusable rule "never weight a
  factorized term above the metric's own weighting". Also confirms B1's
  mechanism analysis prospectively — a rare validated prediction in a round
  that is 0-for-4 on novelty.
- **(b)** — M2 is falsified and the rule becomes **"do not per-sample-normalize
  when `hf_norm_spread >= ~10`"**, with allen_cahn (spread 22.68) as the worked
  counter-example. Round report gets: a dataset-property-indexed design rule
  (measure the target-norm distribution *before* choosing an objective) plus an
  honest self-correction of B1's part-6 mechanism claim — and it retroactively
  makes the (retrieval-refuted) denominator-floor direction the only known
  repair, which is itself a finding about why the stream has no open surface.
- **(c)** — both ingredients contribute; the rule is the conjunction, and the
  round report records the strongest version of the closure argument: an
  objective family that cannot match an MSE baseline on a single dataset cannot
  be the lever for panel-wide sharp-2D fusion.

In all three cases the round report should also carry B1's three cross-stream
exports (helmholtz panel fragility + the zero-predictor check; run
`tools/collapse_set_attribution.py` before any subpopulation mechanism claim;
the hard subpopulation is visible from the LF field, not the condition vector),
which outlive this stream.

## Summary table

| Slot | Category | One-liner | Status |
|---|---|---|---|
| B2 | `objective-disambiguation-measurement` (diagnostic) | 200-epoch A0 (`MFFP_S7_LOSS=rel`, i.e. lambda=1) on `sharp__allen_cahn_2d` alone, seed 0, byte-identical B1 substrate, ~10 min GPU — three pre-registered outcome bands separated by >= 1 certified floor decide "per-sample normalization" vs "lambda>1"; stream closes after it | filled |
