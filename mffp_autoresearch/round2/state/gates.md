# Round-2 launch gates (append-only ledger)

## G2-r2 — corrected copy-LF baselines: PASS 2026-07-31

Command: `python eval/make_copylf_baselines.py` (venv). Output:
`eval/copylf_baselines.json` (`_copylf_def_hash` recorded; seam-checked).

| dataset | corrected | r1 frozen | ratio |
|---|---|---|---|
| ext__helmholtz_2d | 0.299033 | 0.329450 | 0.908 |
| sharp__phase_field_crystal_2d | 0.007381 | 0.044780 | 0.165 |
| sharp__allen_cahn_2d | 0.001781 | 0.016152 | 0.110 |
| sharp__fisher_kpp_2d | 0.021450 | 0.062632 | 0.342 |
| sharp__cahn_hilliard | 0.041803 | 0.087660 | 0.477 |
| ifc_poisson (paper bar) | 0.036 | 0.036 | 1.000 |
| heat_local / fluid / sharp__sod_1d | unchanged | — | 1.000 (bit-identical, asserted ≤1e-9) |

Seam checks passed in-script: corrected datasets below r1 frozen AND within
[0.7, 1.4]× of the s3-B1 audit variant values; unchanged datasets reproduce
r1 bit-for-bit; measured inflation removed 2.0–9.1× (r1 report §5 said
2.0–8.6× on an n_test subset — consistent).

## G3-r2 — floors + stream anchors frozen: PASS 2026-07-31

Command: `python eval/make_floor_anchors.py` (after G2). Artifacts:
`state/anchors/floors.json`, `state/anchors/{r2s1_direct,r2s2_stacked,
r2s3_lf_train_signal,r2s4_diag}.json`, `state/noise_floor.json`.

- Floors (NN-in-condition / train-mean / zero) computed from the FULL
  untouched datasets before any experiment ran (spec §3). Zero-floor nRMSE
  verified ≡ 1.0 on every dataset (metric seam).
- All-stream launch anchor: best-floor panel geomean **23.0636**
  (per-dataset best arms in program §2.3).
- `state/noise_floor.json` is PROVISIONAL (`_source: round1-batch0-rescaled`)
  until r2s4-B1 certifies (ADR r2-0002). Frozen-floor snapshot also committed
  to the outputs repo (`round2/batch_floors/floors_frozen_2026-07-31.json`).

## G1-r2 — eval layer + stripped-view structural enforcement: PASS 2026-07-31

1. Eval test suite: **35/35 green** (`python -m pytest tests/` in
   `round2/eval/`; includes 8 new registration-fix regression tests —
   node identity `up[::r,::r]==coarse`, k/r ramp probe, periodic seam
   averaging, Dirichlet interior-node map, per-dataset dispatch,
   unclassified-dataset raises).
2. Loader-level enforcement (script in session log): for
   sharp__allen_cahn_2d, ext__helmholtz_2d, heat_local, ifc_poisson —
   original test `lf_fids` [1,2]/[1]/[1..4]/[] → stripped test `lf_fids` []
   in every case; stripped TRAIN fids identical to original (complete).
   `score_panel.py` additionally refuses any view directory exposing >1
   test level per dir at run time.
3. Structural enforcement evidence (2026-07-31, session log). What IS
   guaranteed: **test LF is unreadable** — the loader returns
   `test["lf_fids"] == []` on every stripped view, so any code path that
   selects a test LF fidelity (`max(test["lf_fids"])`, e.g. the s6 DC
   corrector `s6_local_repair/smoke_eval.py:700`) raises unconditionally;
   `score_panel.py` independently refuses leaking view dirs. What is NOT
   universally true (spec §5 claim 1 overclaimed): transfer-style factory
   families are ALREADY condition→field at test — `mf_fno_transfer_film`
   ran to completion on stripped helmholtz reading only
   `test["cond_by_fid"]` (its smoke_eval.py:130; contract-tier rel-L2 22.6,
   no LF read, no leakage — HF y used as target only). Consequence: for
   runnable round-1 families the enforcement is the reviewer's rebadge
   check (program §5.10), and `mf_fno_transfer_film` is reclassified as a
   legitimate declared BASELINE/prior for r2s3 (program §12.3). Recorded in
   program.md §3 (corrected wording).

G1-r2 + G2-r2 + G3-r2: **all green — round 2 cleared for stream launch.**

