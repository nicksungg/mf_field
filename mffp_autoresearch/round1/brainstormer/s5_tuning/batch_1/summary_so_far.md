# Summary so far — Stream `s5_tuning`, Batch 1

## 1. Websearch findings + prior-art verdict

Source: `mffp_autoresearch/round1/websearches/s5_tuning/batch_1/report.md`
(4 iterations, 11 WebSearch / 13 WebFetch calls, stopped by explicit ENOUGH).

**Prior-art verdict (verbatim, report.md "For the brainstormer" item 1):**

> **PRIOR-ART VERDICT: not novel, and must not be claimed as such — but legitimate as a
> measurement.** The mode-count question is published prior art: **iFNO**
> (https://arxiv.org/abs/2211.15188, verified first-hand this run) grows K during
> training and gets **10% lower error with 20% FEWER modes**; **AFNO** sparsifies modes;
> **MG-TFNO** factorizes them. `modes_cap` 12 -> 32 is therefore a *measurement of this
> project's own spectral bottleneck* (F22), not a mechanism contribution — which is
> exactly what a `tuning`-class card should be, and it stays inside §12.5 (a
> hyperparameter, not a new mechanism/architecture).

Other load-bearing findings:

- The literature predicts the knob will mostly NOT help: *"simply increasing the number
  of retained Fourier modes is insufficient to overcome the spectral bias"*
  (arXiv:2404.07200); plateau at 8 modes (arXiv:2311.05967); train/val divergence past a
  small mode count (arXiv:2402.11568). The websearcher explicitly frames the null as the
  informative outcome: *"it converts 'the gap is knobs' into 'the gap is not spectral
  bandwidth', which redirects `s2_beyond_copy` and `s4_hybrid_routing`."*
- Two confounds: (a) optimal LR shifts with mode count (1.8e-3 at K=3 -> 7.4e-4 at K=24,
  arXiv:2506.19396); (b) 12->32 is a **7.1x spectral-parameter increase**, capacity-matched
  control point `C=24, K=32` (the `d_c*K` convention is flagged UNVERIFIED).
- Panel-specific: E-UNO (arXiv:2509.01293v3), the source paper of `sharp__cahn_hilliard`,
  beats plain FNO at flat (16,16) modes by an order of magnitude using a per-level mode
  **schedule** [[32,32],[16,16],[8,8],[4,4]], with FNO error "spatially correlated ...
  particularly along evolving phase boundaries".
- Mechanistic downside: aliasing — unresolved high-frequency energy folded back through
  the pointwise nonlinearity (arXiv:2606.00677, arXiv:2604.00689).
- The websearch ran **before G3**, so its item 6 says the noise floor "does not exist yet".
  It does now (`state/noise_floor.json`, certified 2026-07-29) — this summary supersedes
  that caveat.

## 2. §12 conventions (program.md §12.5, verbatim)

> ### 12.5 `s5_tuning` (tuning)
>
> - **Anchor**: champion's certified panel geomean (batch 0); later batches
>   re-target the current champion card.
> - Audited knob findings to grind (from `docs/proposals/MODEL_TWEAKS*.md`):
>   **F22** `modes_cap = 12` never scales with resolution (12 of 128 modes at
>   256² — candidate M1 in MODELS_TO_TRY.md proposes 32); **F19** training loss
>   ≠ scored metric in 11 families; **F20** model-selection metric mismatch;
>   normalization choices.
> - Constraint: no new losses-as-mechanisms, no new paradigms, no architectural
>   changes — knobs on existing recipes only. Anything else belongs in another
>   stream.
> - G4's dry-run card (`s5_tuning-B1`, modes_cap 12→32 on the champion) is a
>   REAL batch-1 card for this stream.

Also binding (program.md §4.5): *"**Every falsification threshold must exceed the noise
floor for its dataset(s).** A claimed effect smaller than the floor is unfalsifiable and
the brainstormer's immutables self-check rejects it."*

**Certified anchor** (`state/anchors/s5_tuning.json`, `provisional: false`):
`mf_fno_transfer_film`, panel geomean skill **6.703**, CI95 [6.219, 7.102], per-seed
[7.102, 6.219, 6.788] (smoke tier, 200 epochs, seeds {0,1,2}).

**Certified noise floors** (`state/noise_floor.json`, `min_claimable_effect` in skill
units): `ext__helmholtz_2d` **9.695** (ALERT — seed spread from a diverging seed;
`state/gates.md` G3: "Brainstormers must treat helmholtz claims as unfalsifiable at
smoke tier unless the design addresses the instability itself"), `sharp__allen_cahn_2d`
1.633, `sharp__phase_field_crystal_2d` 1.151, `sharp__cahn_hilliard` 0.553,
`sharp__fisher_kpp_2d` 0.418, `ifc_poisson` 0.240. The file's own convention is
`min_claimable = max(seed_spread, 0.10 x mean_skill)` (verified: allen_cahn
max(0.014, 1.633); poisson max(0.240, 0.157); helmholtz max(9.695, 1.382)).

## 3. Within-stream prior cards

**None.** `experiment_cards/` contains only `.gitkeep` and `SCHEMA.md` (verified by
`find`). This is the first card of the stream and of the round; `state/gates.md` lists
**G4 — dry-run card s5_tuning-B1: PENDING**, i.e. this card is also the G4 gate.

Champion baseline read directly from the batch-0 result JSONs
(`eval/results/mf_fno_transfer_film/{dataset}_e200_s{0,1,2}.json`), per-seed skill:

| dataset | HF grid | s0 | s1 | s2 | mean | floor |
|---|---|---|---|---|---|---|
| `ext__helmholtz_2d` | 96² | 18.826 | 9.131 | 13.495 | 13.817 | 9.695 |
| `sharp__phase_field_crystal_2d` | 128² | 11.496 | 11.477 | 11.560 | 11.511 | 1.151 |
| `sharp__allen_cahn_2d` | 256² | 16.335 | 16.327 | 16.341 | 16.334 | 1.633 |
| `sharp__fisher_kpp_2d` | 256² | 4.225 | 4.133 | 4.173 | 4.177 | 0.418 |
| `sharp__cahn_hilliard` | 256² | 5.563 | 5.615 | 5.423 | 5.534 | 0.553 |
| `ifc_poisson` | 64² | 1.545 | 1.456 | 1.696 | 1.566 | 0.240 |
| **panel geomean** | — | 7.102 | 6.219 | 6.788 | **6.703** | (derived 0.884) |

`n_params` at `modes_cap=12` is **4,773,953** (helmholtz/sharp) / 4,774,465 (poisson);
`train_seconds` seed 0: poisson 41.8 s, helmholtz 453 s, allen_cahn 2660 s. Full-panel
wall time at cap 12 ~= 154 min/seed (`state/timing_ledger.json`).

## 4. Cross-stream cards

None — no cards exist in any stream yet.

## 5. Reopen candidates

None — no prior cards, hence no `reopen_candidate: true` entries.

## 6. What is UNKNOWN

1. **Does the knob even fire, and does the extra bandwidth get used?** The spectral-bias
   result (arXiv:2404.07200) says allocated high modes may stay unlearned. Unknown for
   *this* recipe: whether the cap-32 weights acquire non-trivial magnitude in bands
   12–32, or stay near their init. Nothing in-repo has ever measured it.
2. **Is bandwidth the champion's bottleneck at all?** At cap 12 the model retains 9.4% of
   Nyquist on the three 256² sharp sets, 19% at 128², 25% at 96², 38% at 64². Best-zoo
   skill is 4.2–16.3 there — the model is 4–16x *worse* than copying LF. Unknown whether
   an error that large can be attributed to truncation at all, or whether it is dominated
   by something the mode count cannot touch (amplitude scaling, the additive-vs-copy
   framing raised in §12.2).
3. **The capacity/bandwidth confound direction.** Unknown whether cap 32's 7.1x spectral
   parameters (4.77M -> ~33.6M) helps (capacity) or hurts (overfitting) on `ntrain=400`
   and especially **N_hf = 5** on `ifc_poisson`, where cap 32 is the *entire* 64²
   spectrum. Which arm of the trade-off dominates is exactly what one run resolves.
4. **The LR-shift confound.** Unknown how much of any cap-32 loss is mis-tuned LR
   (arXiv:2506.19396). This card cannot answer it and must not pretend to; it is the
   designated conditional batch-2 follow-up.
5. **The helmholtz instability.** The champion's helmholtz nRMSE per seed is 6.20 / 3.01 /
   4.45 against a copy-LF reference of 0.3295 — the model is 9–19x worse than its own
   input and the seed spread is 70% of the mean. Unknown whether this is divergence,
   an amplitude-scaler pathology (`scaler_hf = max|y|` over HF train, `smoke_eval.py:137`),
   or genuine sensitivity. It is the single largest lever on the panel geomean
   (helmholtz at skill 1.5 would move the geomean from 6.70 to ~4.6) and the largest
   source of geomean seed noise — but it is out of scope for the pre-directed batch-1
   knob and is recorded here as the leading s5 batch-2 candidate.
6. **Whether a flat cap is the right shape.** E-UNO's *schedule* beats flat modes by 10x
   on our own cahn_hilliard; a per-block schedule is precedented in-zoo
   (`fno_coreg_residual` uses (4,8,12,12)). Unknown whether "more modes" or "modes where
   the resolution is" is the operative variable — a flat cap-32 result constrains both.
7. **Runtime at cap 32.** Unknown; the spectral einsum is 7.1x but FFT-dominated, so the
   panel job may take 1.3–2.5x the measured 154 min/seed. This determines `--time`.
