# INSPIRATION — `r3s2_ceiling` (card `r3s2_field_reach-B3`)

## What is claimed, and what is explicitly NOT

The prior-art verdict on this card is unambiguous and is reproduced on the card
verbatim.
**Nothing here is `novel`** — the project record is 0-for-10 (program.md §13.3).

- **D1, the emulator-ceiling ladder — `preempted-but-MF-composition-open (cite)`.**
  The oracle-vs-predicted-intermediate decomposition is textbook.
  What is open is the **regime**: *"In every fetched instance the oracle intermediate is a deployable counterfactual — coarsened ERA5, GT masks, GT mels, a real coarse solve. Here the LF field exists at train only and must be hallucinated from the condition vector at test, so the ladder measures a bound on what the route could ever buy, not an alternative deployment. No fetched source runs it (a) with an intermediate structurally unavailable at inference, (b) at N_hf = 5 with a closed-form corrector whose fold population C(5,3) is enumerable, or (c) priced against a certified training-free floor + certified baseline denominator in skill units. That triple is the claim."*
  The verdict also states that **the instrument may not be claimed, only the measurement in this regime**, and this family claims nothing for the instrument.
- **D2, the selection-input repair — `preempted (cite)`.**
  *"usable ONLY as an instrument repair, exactly like batch 2's E1. Presenting it as the idea is a rebadge."*
  `d2_select.py` therefore carries a `declared_role` field saying exactly that, and every run emits the paired real-LF-selected comparand so the repair is attributable rather than assumed.
- **D3, the ceiling ratio as a prospective decision rule — `preempted-but-MF-composition-open (cite)`.**
  *"Every retrieved use answers 'which stage to improve'; none answers 'should this stage exist at all'."*
  Converting the ceiling ratio into a **drop-the-intermediate** rule whose fallback is a direct condition→HF model at matched budget is registered as a **methodological** contribution (clause C2), which is what the verdict requires.

## Sources (card `prior_art.citations`, verbatim)

D1 — oracle/predicted intermediate ladders:

- https://arxiv.org/html/2602.13416
- https://arxiv.org/html/2604.12440
- https://arxiv.org/pdf/2606.07718
- https://arxiv.org/pdf/1712.05884 §3.3.1 (teacher forcing / ground-truth mel intermediate)
- https://arxiv.org/pdf/2301.10937
- https://ieeexplore.ieee.org/document/6521941/ (snippet-only, carries no verdict weight)

D2 — out-of-sample regularisation selection under a shifted selection input:

- https://arxiv.org/pdf/2305.00974
- https://arxiv.org/pdf/1712.10050
- https://arxiv.org/pdf/2506.12007

D3 — ceiling ratios read as a stage-level decision rule:

- https://arxiv.org/pdf/2606.07718
- https://arxiv.org/html/2602.13416

Carried preemption citations for the LSI instrument itself, inherited from the
base family's `lsi_filter.py` APPEND-ONLY block and restated here so the repair
stays attributed: arXiv:1810.08360 (LOOCV ridge selection), arXiv:1511.07030
(low-sample-support shrinkage), arXiv:2606.03936 (per-band weighting of a frozen
operator).

Reporting standard for the band columns: Duraisamy, arXiv:2604.20061.

## Provenance of every component

Vendored WHOLESALE from this stream's own `models_r3/r3s2_route` at
`e606a4f14f8e870fccee097ed18b6050344a4ace` (the tip of
`round3/exp-r3s2_field_reach-B2`), per-file sha256 in `_vendor_manifest.json`:
`model.py`, `front_end.py`, `ic_synth.py`, `lsi_filter.py`, `local_corrector.py`,
`direct_head.py`, `bands.py`, `periodicity.py`, `upsample.py`, `floor_arms.py`,
`selector.py`, `probes.py`, `sidecars.py`.
That family in turn vendors `r3s2_stack_ic` @ `d5069a74`, `r2s2_stack` @
`6b4e1d48`, and round-1 `s4_router` @ `b90d4662`.
No code is vendored from any round-1 family beyond what `r3s2_route` already
carried, and none from `r2s1_direct`.

The IC-synthesis mathematics remains B1's re-implementation from the READ-ONLY
generator surfaces (`mffp_sharp/common/ic_encoding.py::ic_2d` and
`common/spectral.py::spectral_interp`) with provenance comments — never
imported, never edited.

New in this family, and written for this card:

| file | what it adds |
|---|---|
| `smoke_eval.py` | the 5-rung ladder driver, the gates, the diag |
| `hot_split.py` | the held-out-TRAIN split protocols and the enumerated fold populations |
| `ladder.py` | the five statistics, the film/`tau` unit conversions, clauses C1–C4, the registration predicate, the registered falsifier |
| `d2_select.py` | the D2 selection-input repair (instrument only) |
| `rung_lift.py` | the ADR r3-0005 rung/lift tripwire against `panel_data.py` |
| `target_scale.py` | the round-2 ADR 0004 §2 target-scaler pre-flight, live because B3 scores pfc |
| `upsample.py` (append-only block) | the ADR r3-0005 spectral (FFT zero-pad) lift, verbatim from `panel_data.py` |

`models_r3/_common/ckpt_binding.py` and `tools/ckpt_data_binding.py` are vendored
byte-identically from `round3/exp-r3s4_audit-B2` @ `da855da` to satisfy batch-3
scope rule 2 (`data_binding` written into `last.pt` at every save).

## Declared reuse

Role (a), round-2 program 5.10a: the DC-lineage corrector remains a declared
FROZEN test-time sub-component behind a condition→pseudo-LF front end.
NEW in B3: the SAME frozen corrector is additionally evaluated on REAL
train-side LF (rung `R2_oracle`) as an explicitly NON-DEPLOYABLE reference arm,
in the same role class as the copy-LF reference.
It never touches test LF (immutable #9) and never enters a panel geomean.
