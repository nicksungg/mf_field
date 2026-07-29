# Summary so far — Stream `s1_poisson`, Batch 1

All paths relative to `mffp_autoresearch/round1/` unless absolute.

## 1. Websearch findings + prior-art verdict

Source: `websearches/s1_poisson/batch_1/report.md` (5 iterations, 11 searches,
7 usable fetches, cap hit).

Verdict row for the batch-1 seed direction, verbatim:

> **D1.** All-ordered-pairs fidelity training — ONE FiLM-FNO over every
> (f_src<f_tgt) pair of the nested 100/50/20/5 ladder, queried (LF→HF) at eval
> (`akash/models/mf_fno_allpairs`) | **preempted-but-MF-composition-open** |
> … | Conditioning on fidelity, joint multi-level training, and adjacent-level
> cascades are all published. **Not found published**: (i) **all ordered pairs**
> (not just adjacent) as a data-amplification augmentation, (ii) with a
> **single shared** network rather than one net per level, (iii) at **N_hf = 5**
> on the `li2022ifc` Poisson ladder.

Directives carried into the design (report §"For the brainstormer"): frame
batch 1 "honestly as a measurement, not an invention"; "**Design the pair set as
the actual variable**" with arms (a) adjacent-only, (b) all ordered pairs,
(c) LF→HF only — "If (b) ≈ (a) the finding is 'the ladder's value is in adjacent
steps'; if (b) ≫ (a), non-adjacent pairs carry real information and that *is* the
result"; do not propose D2 (MLMC-NO / MFRNP telescoping — preempted, on FNO +
Poisson) or D3 (ensembling — preempted and collides with §4.4 seeds-as-CI); do
not assert which method owns 0.036 vs 0.018; thresholds ordinal, not absolute.

## 2. §12.1 conventions (verbatim, program.md)

> ### 12.1 `s1_poisson` (gap)
>
> - **Bar**: paper 0.036 (IFC-ODE2); stretch IFC-GPODE 0.018. Current best zoo:
>   0.042 (`mf_fno_pinn_transfer`, factory bench). Anchor: `state/anchors/s1_poisson.json`.
> - **N_hf = 5.** Every claim is anecdote-grade by sample count; the CI + noise
>   floor conventions are the only defensible reporting. Prefer designs that
>   reduce variance (ensembling across seeds, all-pairs training) or add
>   information (physics residuals) over designs that add capacity.
> - Batch-1 seed direction: **all-pairs fidelity training** applied to the gap —
>   `mf_field/akash/models/mf_fno_allpairs` was the mentor's best on the hard
>   subset (gm 0.0094 vs FiLM 0.0121, FINDINGS.md); its known failure is
>   O(L²) pair cost on many-level datasets (era5 timeout) — irrelevant here
>   (ifc ladder L=4).
> - Physics fact: Poisson is elliptic with global coupling; the IFC papers'
>   ODE/GPODE methods exploit the fidelity-ladder structure directly.

Certified anchor (`state/anchors/s1_poisson.json`): `anchor_type
best_skill_on_dataset`, family `mf_fno_transfer_film`, value **1.5656**,
per_seed [1.5447, 1.4562, 1.6961], ci95 [1.4562, 1.6961], `provisional: false`.
Noise floor (`state/noise_floor.json`, `ifc_poisson`): `min_claimable_effect`
**0.2399** skill units, per-seed nRMSE [0.05561, 0.05242, 0.06106].
Skill denominator is the paper bar 0.036, not copy-LF (ADR 0002), because
`ifc_poisson/test/` ships only `fidelity_64` — verified by `ls` on
`mf_field/factory_mffp/data/ifc_poisson/test/`.

## 3. Within-stream prior cards

None. `find experiment_cards -name "*.json"` returns nothing; `index.md`
states "No stream has an experiment card yet — `experiment_cards/` contains
only `SCHEMA.md` and `.gitkeep`." Batch 0 is the anchor-certification array
(job 65956106), not a card.

## 4. Cross-stream prior cards

None (same evidence as §3). Adjacent-stream constraint noted for scope
discipline: §12.5 assigns `modes_cap 12→32` (finding F22) to `s5_tuning`-B1,
so this card must not grind `modes_cap` even though it is spectrally relevant
here (see §6).

## 5. Reopen candidates

None — no prior cards exist in this stream, hence no `reopen_candidate: true`
entries.

## 6. What is UNKNOWN (and what I verified myself)

**Verified facts about the dataset** (read from
`mf_field/factory_mffp/data/ifc_poisson/`, numpy shapes):
`train/fidelity_{8,16,32,64}/Xs.npy` have shapes (100,5), (50,5), (20,5),
(5,5); `ys.npy` (100,8,8), (50,16,16), (20,32,32), (5,64,64); `test/fidelity_64`
is (128,5)/(128,64,64). **The fidelity levels are NOT sample-aligned**:
`np.allclose(X8[:5], X64)` is `False` (max abs diff 0.581); likewise 8-vs-32
(0.709), 8-vs-16 (0.739), 16-vs-64, 32-vs-64. Same on `ifc_heat`. The
`ifc_raw` loader (`data_adapters/loaders.py::_load_ifc_raw`) passes the arrays
through verbatim — no reordering, no alignment.

**Consequence, previously unrecorded anywhere in the round**: the seed-direction
family `akash/models/mf_fno_allpairs` builds its training rows as
`Xsrc = cond_by_fid[s][:n]`, `Ytgt = field_by_fid[t][:n]`
(`smoke_eval.py::build_pairs` lines 61–74) and its LF→HF finetune as
`X_lf = cond_by_fid[lf]` against `Y_hf_tr` (lines 130–136). Its own docstring
admits the assumption: "ifc_raw aligns samples across fids … robust for ifc_heat
which is aligned so the modulo is a no-op". On `ifc_poisson` that assumption is
false, so **every** cross-fidelity row and the entire finetune stage pair a
condition vector with a field generated from *different* parameters. The akash
2500-epoch bench corroborates: `mf_fno_allpairs` scores **0.4657** on
`ifc_poisson` and **0.1457** on `ifc_heat` (`akash/results/bench_full_metrics.csv`)
versus `mf_fno_transfer_film` 0.0488 / 0.0089 — ~10× and ~16× worse, on exactly
the two non-aligned datasets, while it wins the aligned npz datasets. Unknown
until measured in-round: whether the correspondence defect *is* the whole
explanation.

**Genuinely open questions this stream owns:**

1. Does the ladder's *intermediate* information matter? The champion
   (`mf_fno_transfer_film`) uses exactly two levels — 100 rows at 8² pretrain,
   5 rows at 64² finetune (`smoke_eval.py` lines 165–170). The 50 rows at 16²
   and 20 rows at 32² are **never used by any certified model**. Spectrally this
   is the interesting part: an 8² field bilinearly lifted to 64² carries content
   only to mode ≈4, whereas the FNO represents 12 modes; the 32² level (20
   samples) is the only supervision besides the 5 HF samples that covers modes
   4–12. Nobody has measured whether that closes any of the 0.056→0.036 gap.
2. Is the fidelity *tag* (f_src, f_tgt) load-bearing, or is the eval query
   (f_src=LF, f_tgt=HF) simply an out-of-distribution label if only self-pairs
   are trained? Ordinal contrast, cheap.
3. How much of the 0.056 (200 ep) vs 0.0488 (2500 ep) difference is budget, not
   architecture? Not answerable in-round (tier fixed, §5.6) — a caveat, not an
   experiment.
4. Architectural fact worth recording: on `ifc_poisson` no model can consume an
   LF *field* at test time (test ships only fidelity_64), so every family here is
   a purely parametric map cond→field. "Multi-fidelity" on this dataset can only
   mean *training-data* fusion, never input fusion. That is why copy-LF is
   undefined (ADR 0002) and why the ladder-as-data question is the whole game.

**Cost is not a constraint here**: batch 0's `ifc_poisson` jobs took 0.78–0.98
min at 200 epochs (`state/timing_ledger.json`), so a multi-arm sweep on this one
dataset is minutes, not hours.
