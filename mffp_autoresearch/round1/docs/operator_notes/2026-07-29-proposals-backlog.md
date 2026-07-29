# Operator note — docs/proposals backlog audit (2026-07-29)

Source: a forked session read the five pre-kickoff files in the repo-root
`docs/proposals/` (dated 2026-07-15..22) that round-1 setup never ingested
(setup used only PROMPT-7-28.md and AI_Scientist.pdf). This note is operator
input for batch-2 brainstormer dispatches; it does not modify program.md.

## Independently converged (no action — validation only)
- Round 1's single nRMSE definition + NRMSE_DEF_HASH resolves the audit's F01
  (three incompatible definitions).
- Batch 0 IS the proposed A6 noise-floor calibration (~36 runs matches).
- s5_tuning-B1 (modes_cap 12→32) IS A9/F22 — the never-tuned spectral cap.
- s1-B1's env-knob-invisible-to-cache trap was pre-warned in MODELS_TO_TRY §5.
- "Make the MF composition the thesis" (six mechanism-preempted proposals in a
  row) matches s2's copy-LF framing and the round's prior-art discipline.

## NOT ingested — candidate seeds for batch 2 (feed to brainstormers)
1. **Candidate D: warp-then-correct / registration fusion** (NEW_MODELS.md) —
   geometric misalignment mechanism; in no current stream; the only one of the
   four NEW_MODELS candidates NOT prior-art-preempted at mechanism level per
   its own scans. Natural fit: s4_hybrid_routing or s2 batch 2.
2. **D1 residual-spectrum FFT diagnostic** (MODELS_TO_TRY.md) — free,
   designed probe distinguishing H1 spectral-truncation vs H2 missing-local-
   representation. Natural fit: s2 batch 2 (complements the B1 forensics) or
   s5 (interprets the modes_cap result).
3. **A7 mf_fno_pinn_transfer attribution experiment** (MODEL_TWEAKS.md) —
   which stage of the transfer schedule carries the gain. Fit: s1/s5.
4. **F14-F18 structural-constraint ideas** (MODEL_TWEAKS_EVIDENCE.md) —
   loss/metric mismatch and constraint items not yet examined by any stream.

## Caveats
- These predate batch-0 certification; any numbers in them are uncertified and
  must not be quoted as priors — streams must re-derive through the eval layer.
- H1-vs-H2 framing (spectral capacity vs local representation) will be partly
  answered by s5-B1 + s2-B1; batch-2 dispatches should condition on those
  results rather than re-proposing the question.

## Scouting gap-mine results (2026-07-29, websearches/_scouting/2026-07-29_stream_gap_mining/)

Orchestrator adjudication of the scout's ranked candidates:
- **C1 trust-gated fallback fusion** (y = LF + g·Δ, g≡0 init = copy-LF exactly;
  open-for-MF): NOT a new stream — merged into s6_local-B1's D3 design space
  (same composition class: gated/identity-init correction consuming real LF).
  C1's citations + the gaming-risk framing (identity-init makes skill≤1 at
  init → frame as measurement; gate collapse to zero is a finding, not a win)
  forwarded to the s6 brainstormer mid-flight.
- **C2 LF-field-keyed retrieval residual transfer**: batch-2 seed (s6 or s2).
  Caveat: keyed on LF field, applied to residual — knn-in-X was 4-30x worse
  than copy-LF.
- **C3 cross-dataset/foundation pretraining = the deferred s8_data: CLOSED,
  DO NOT OPEN** (preempted 4x fetched; the champion already IS
  LF-pretrain→HF-finetune; fragments to s5 (SSL aux) and s1). Any future
  non-panel-pretraining card needs an operator fairness ruling first.
- **C5 boosting/cascades**: s4 batch-2 seed (preempted as published; MF
  composition angle only).
- **C4 in-context/meta-learning**: not worth it (preempted + wrong problem).
- **C6 per-sample amplitude calibration**: s5 batch-2 seed (verdict "novel"
  but thin; helmholtz 86.5% amplitude share motivates).
- **C0 precondition** (does the base family actually ingest a field-shaped LF
  at eval?): mandatory build-gate for any C1/C2-class card; s2 batch-2 seed.

**FACT CORRECTION (propagate everywhere)**: n_train_hf = 400 on all five
beyond-copy sharp datasets; only ifc_poisson is N_hf=5. "Few-shot" framing
applies to ifc_poisson alone; retrieval banks/exemplar methods are feasible
on 5/6 panel datasets.

## Batch-3 synthesis candidate (2026-07-29, Eloise prompted: invest in
## transfer_film as stage 1)

Champion (mf_fno_transfer_film) stage-1 + LF-consuming corrector (s4
mechanism) + identity/no-harm gate at copy-LF (s6 floor). Hold until (a)
s6-B1 200-ep result and (b) s4-B1 mechanism turns resolve the pfc stage-3
confound. Evidence basis: s4 paired control (all gains corrector-side),
s5 mechanism (backbone = DC+noise on 5/6 sharp sets; keep it for
ifc_poisson/X-path, don't invest in its capacity). Owner: s4 or s6 per
whichever mechanism the readouts favor.

## Eloise idea sweep (2026-07-29 evening): DINO / tabular FMs / diffusion

- **DINO(LF field) as retrieval key**: seed for s2-B3 — one extra key arm in
  the retrieval-floor screen (vs block-mean/S1/per-patch keys). Rationale:
  X is insufficient exactly where the LF field is informative (pfc
  realization identity); zoo already has DINO-conditioned families (check
  their bench rows first). Websearcher must check DINO-for-PDE-retrieval
  prior art.
- **TabPFN-style in-context per-sample scale prediction from X**: seed for
  s5-B3 — training-free scalar head for the amplitude channel (helmholtz 3%
  of samples = 50% of error; 408x norm spread). Territory question (knob vs
  architecture) to the websearcher; no gradient training = arguably s5-legal.
- **Diffusion (incl. low-data variants): NOT revived** — pre-falsified lever
  (§5) + this round's evidence (spurious high-k is a measured failure mode;
  winning methods are deterministic/data-light). Re-arguable only if batch-3
  plateaus and residual distributions become the question; must address the
  pre-falsification explicitly.
