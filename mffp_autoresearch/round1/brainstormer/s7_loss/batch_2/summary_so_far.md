# Summary so far — Stream `s7_loss`, Batch 2

All paths relative to `${ROUND_ROOT}` =
`/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/round1` unless absolute.

## 1. Websearch findings + prior-art verdict

Source: `websearches/s7_loss/batch_2/report.md` (5 iterations, cap reached;
11 WebSearch + 15 WebFetch, 9 fetches succeeded).

Five candidate directions were retrieved against. **Four are flatly preempted
by fetched sources; the fifth belongs to another stream.**

- **D1** — B1 part-7's lambda=1 disambiguation (one 200-epoch A0
  `MFFP_S7_LOSS=rel` on `sharp__allen_cahn_2d` alone) — verdict **`preempted`
  (mechanism), open only as an in-repo *measurement***. "Nothing publishable.
  But no fetched source answers B1's normalization-vs-lambda question either,
  so the ~10 min run is the only way to close the standing design rule. Card
  must be framed as a measurement, never a contribution."
  Citations: https://arxiv.org/html/2410.23159v1 ;
  https://ar5iv.labs.arxiv.org/html/2108.08481 (fetched, **does not** contain
  the relative-vs-MSE claim) ; https://arxiv.org/html/2606.02997v1 (fetched,
  **does not** contain the ablation) ; batch-1 C-REL row.
- **D2** — eps-floored / stop-gradient relative loss: **preempted**. Neural
  Radiosity 4.1 publishes the formula verbatim
  (https://ar5iv.labs.arxiv.org/html/2105.12319); and in-repo it is
  near-vacuous — our denominator `||y||` is already parameter-independent so
  stop-grad is a no-op, and the floor touches only the 2 high-spread datasets
  whose collapse set B1 F5/F6/F8 showed is MSE-shared.
- **D3** — shape-first curriculum repair of `amp`: **preempted** (FACL
  publishes both the amplitude+correlation decomposition and the
  100%-FCL-first annealed schedule, https://arxiv.org/html/2410.23159v1) *and*
  moot, because B1's own rule is lambda <= 1, where the pathology is
  algebraically impossible.
- **D4** — target-level shape/gain reparameterization:
  **preempted-but-MF-composition-open** (DiSOL 4.1,
  https://arxiv.org/html/2601.09143v1). The one open slice (predict the
  per-sample gain *from the LF field* at N_hf <= 5) is **already running as
  `s1_poisson-B3`** (`experiment_cards/s1_poisson/batch_3/B3.json`,
  `MFFP_GAIN_HEAD=ladder_level_intercept`, status `analyzing`). s7 must not
  duplicate it.
- **D5** — residual-supervision loss: **preempted** (MFFM,
  https://arxiv.org/html/2605.16118v1) and owned in-repo by
  `s2_beyond_copy-B2` (`s2_lf_residual_control`, geomean 0.380).

Websearcher's own recommendation ("For the brainstormer", items 2 and 7): write
the D1 measurement card with B1 part 7's three pre-registered outcomes, and
"card part 7's own recommendation is to close s7_loss after the D1
measurement. This loop's retrieval evidence supports that."

Three snippet-sourced claims were **withdrawn on fetch** (Kovachki
relative-vs-MSE; DiSOL dynamic-range instability; TransportBench 9.3%
ablation) — i.e. the loop's negative evidence is verified, not recalled.

## 2. Section 12 conventions verbatim (program.md 12.7)

> ### 12.7 `s7_loss` (lever) — ADDED STREAM, see ADR 0012
>
> - **Question**: does an interface-aware training objective (scored on the
>   unchanged rel-L2 metric) fix sharp-2D fusion where architecture does not?
> - **Anchor**: champion's certified panel geomean (batch 0).
> - **Backlog ingested**: F14-F18 (docs/proposals/MODEL_TWEAKS*.md) —
>   loss/metric mismatch; rel-L2's blindness to thin sharp regions is the
>   repo's own documented metric caveat.
> - **Hard rule**: 2.1 is immutable — scoring never changes; only the training
>   objective does. Physics-agnostic losses only (ADR 0009): weights from the
>   field's own gradients/level sets.
> - **Pre-registered risk**: interface upweighting can lose on rel-L2 by
>   trading bulk accuracy; cards must state this trade-off in
>   expected_falsification.
> - ADR 0007 applies (propose 3-5 loss designs, screen at contract tier).

Also binding (program.md 4.3): "`diagnostic` — a **measurement**, no training:
single run, no seeds 2-3, its `expected_falsification` clause states what the
measurement will show and what result would falsify the motivating
hypothesis." And the ADR 0007 guardrail: "**Diagnostics and spec-pre-directed
slots are exempt** (no candidate pool)."

## 3. Within-stream prior cards

`experiment_cards/s7_loss/batch_1/B1.json` — status `complete`,
`reopen_candidate: false`, verdict **falsified + cratered**.

- Parts 1-4: 5-arm ADR-0007 design on the frozen champion substrate
  (`mf_fno_transfer_film` @ `967562e`), family
  `models_r1/mf_fno_transfer_film_s7loss`, promoted arm **A1a**
  (`MFFP_S7_LOSS=amp MFFP_S7_LAMBDA=4.0 MFFP_S7_STAGES=both`), panel, 200 ep,
  seed 0. Algebraic basis: `rel_i^2 = (1-cos^2) + (g-cos)^2` (shape + gain),
  verified to 4.4e-16.
- Part 5 (`provisional-single-seed`, job 66023542, 37.7 min H100): panel
  geomean fell; `sharp__allen_cahn_2d` **nRMSE 1.001375560628003, skill
  61.99787588859377** vs certified anchor 16.334 (floor 1.633) —
  `frac_rel_ge_0.9` = 1.00, `g_median` 0.0275, `cos_median` 0.0219. The
  helmholtz "gain" is a trivial-predictor artifact (97.75% reproduced by
  predicting zero). `hf_norm_spread_train` on allen_cahn = **22.68**.
- Part 6 mechanism (fully resolved): `amp(lambda)` reduces to
  `L = (1-c^2) + lambda(r-c)^2`; its only stationary points are the correct
  field **and the origin**; for lambda>1 the origin's escape drive is
  `2 lambda/(lambda-1) r -> 0` and 29% of allen_cahn samples sit where descent
  *reduces* the target-aligned component — **0% at lambda=1, algebraically
  impossible**. Screen 2 ep 1.00161 -> 200 ep 1.00138: it never started.
  Design rule M6: measure `hf_norm_spread` first; **lambda <= 1 always**.
- Part 6 F5/F6/F8: the pfc / cahn_hilliard bimodality is a *dataset* property —
  an MSE-trained model of the same family collapses on the same samples
  (overlap 1.00 / 0.92; Spearman 0.979 / 0.810).
- Part 7 open question + next direction: quoted verbatim in `iteration_1.md`.
- Build evidence reusable here (`build_notes`): A-def default-equivalence
  bitwise identical to the untouched factory family (|delta| = 0.0 on
  helmholtz + ifc_poisson); **A0 (`rel`) already ran clean at contract tier**
  (ifc_poisson nRMSE 0.36672538, finite, distinct from A-def); the
  checkpoint-resume drill passed bit-identically on this exact substrate.
- Screen table (`.../s7_loss/B1/screen/screen_table.md`): at 2 epochs every arm
  including A-def is trivial on allen_cahn (skill 61.15-62.91, nRMSE approx
  0.988-1.002) — which is exactly why the 2-epoch screen cannot decide this.

Handoff `worktrees/s7_loss/B1/notes/handoff_experiment_mechanism_analyzer.md`:
"**lambda=4 is the culprit, not per-sample normalisation** — but that is a
mechanism-supported *hypothesis* (M2) until someone runs A0 (lambda=1) for 200
epochs on allen_cahn alone (~10 min GPU). That is the single cheapest decisive
experiment this card exposes."

## 4. Cross-stream cards

- `s1_poisson-B3` (`experiment_cards/s1_poisson/batch_3/B3.json`, status
  `analyzing`) — post-hoc per-sample **gain head** transferred across fidelity
  levels, on `ifc_poisson`. This is the D4 open slice; s7 is explicitly barred
  from duplicating it.
- `s2_beyond_copy-B2` (`s2_lf_residual_control`) — owns the D5 residual-target
  ground in-repo (geomean 0.380).
- B1 part 7 `cross_stream_notes` exports three round-wide items (helmholtz
  fragility + the zero-predictor check; run
  `tools/collapse_set_attribution.py` before any subpopulation mechanism
  claim; the hard subpopulation is visible from the LF field, not the
  condition vector). These constrain *other* streams, not this card.

## 5. Reopen candidates

None. `s7_loss-B1` carries `reopen_candidate: false` and `status: complete`;
it is the only prior card in the stream, and it was never skipped.

## 6. What is UNKNOWN

**The one live unknown (and it is one dataset wide, one knob deep).** B1's
mechanism analysis proves the lambda>1 pathology exists and is absent at
lambda=1, but every *observation* in the card is consistent with two mutually
exclusive readings, which imply opposite design rules:

- **H-lambda**: the gain over-weight lambda>1 is the sole cause. Then the
  per-sample relative objective at lambda=1 (which *is* the scored metric)
  trains normally, and the standing rule collapses to "lambda <= 1".
- **H-norm**: per-sample normalization itself is fatal on high-`hf_norm_spread`
  data (allen_cahn train spread 22.68). Then the rule is "do not normalize when
  spread >~ 10, with or without a gain term", which would also retroactively
  justify the (retrieval-refuted) denominator-floor direction as the *only*
  repair.

Nothing run so far separates them. The 200-epoch evidence is lambda=4 only; the
lambda=1 evidence is the 2-epoch screen, where **A-def itself is trivial**
(allen_cahn skill 61.15 at 2 ep) so all arms are observationally identical.
No fetched source in the batch-2 loop answers it either (D1 row).

**What is NOT unknown any more** (so it must not be re-proposed):

- Whether the pfc / cahn_hilliard bimodality is loss-induced — no (F5/F6/F8,
  overlap 1.00/0.92 with an MSE-trained sibling). Any per-sample-normalized
  objective aimed at those two datasets is pre-falsified by B1.
- Whether a curriculum can rescue lambda>1 — irrelevant; lambda <= 1 removes
  the pathology algebraically (D3 also preempted by FACL).
- Whether a denominator floor is the fix — preempted (Neural Radiosity 4.1)
  and near-vacuous in-repo (denominator is already theta-independent).
- Whether an amplitude head is the fix — preempted (DiSOL) except for the MF
  slice, which `s1_poisson-B3` is already running.
- The ceiling on any loss-only lever: part 6 M7 + the LF-visibility finding
  (collapse label AUC 0.099/0.102 from LF, best of 19 condition coords
  |AUC-0.5| = 0.067; 0 of 27 families read test LF at inference) — a loss
  cannot make a substrate regime-aware when the substrate never sees the
  regime.

**Second-order unknowns that this batch deliberately does NOT buy** (recorded so
the omission is auditable): the exact lambda boundary between 1 and 4; whether
the `STAGES=pretrain`/`finetune` split matters; whether lambda=1 helps or hurts
the *other* five panel datasets. None of these change a decision, because after
the D1 measurement every loss-shape lever is either falsified in-repo or
retrieval-refuted, and the honest move is stream closure (B1 part 7's own
recommendation + websearch item 7).

**Therefore the only decision-relevant measurement left in this stream is D1**,
and its value is a *design rule for future rounds* (which of two rules the round
report publishes), not a score improvement. Cost ~10 min GPU (B1's allen_cahn
leg: 575.0 s of training).
