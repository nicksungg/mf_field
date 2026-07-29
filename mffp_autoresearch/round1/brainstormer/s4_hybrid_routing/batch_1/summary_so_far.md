# Summary so far — Stream `s4_hybrid_routing`, Batch 1

All paths below are relative to `${ROUND_ROOT}` =
`/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch/round1` unless absolute.

## 1. Websearch findings + prior-art verdict

Source: `websearches/s4_hybrid_routing/batch_1/report.md` (4 iterations, 12
searches, 8 successful fetches).

Three candidate directions were carried to a verdict:

- **D1** — panel-benchmark the already-built `fno_transolver_seq`
  (FNO-FiLM base + zero-init alpha-gated Transolver corrector on out-of-fold
  LF→HF residuals). Verdict `preempted-but-MF-composition-open`; the report's
  own instruction: *"**D1 is a measurement card — it should claim no novelty at
  all**, only that it measures whether the +30.6% oracle survives against
  copy-LF on sharp 2-D."* Citations: https://arxiv.org/html/2602.11197 (FNO
  smooth background + ViT high-contrast corrector), https://arxiv.org/abs/2311.12902
  (hierarchical FNO + conv-residual + attention, frequency-complementary,
  sequential, **not** multi-fidelity).
- **D2** — LF-conditioned spatially-resolved routing FNO↔Transolver. Same
  verdict; *"the ONLY defensible novelty is the router's input"* (LF field /
  LF-HF disagreement); spatially-variant gating over heterogeneous operator
  experts is published (https://arxiv.org/abs/2508.21249), per-location hard
  spectral-vs-local routing is published (https://arxiv.org/pdf/2605.12965),
  and the leading MF operator-learning paper explicitly disclaims routing
  (https://arxiv.org/pdf/2507.07292). Any routing card must carry an
  **identity-safe construction**, and the in-repo `alpha` least-squares +
  line-search-containing-0 is named as the differentiator no published router
  offers.
- **D3** — per-band fidelity routing with `k_c` from LF/HF coherence. Same
  verdict **plus a pre-falsified-lever flag**: the hard-constraint form *is*
  program.md §5's falsified "LF low-mode freezing" (`mf_fno_spectral`).
- Cross-cutting hook (report item 5): FNO *"approximates kernels primarily in a
  relatively low-frequency domain"* (2311.12902) and SPAMoE assigns sharp
  interfaces to a dedicated **local** expert — both support "the spectral expert
  is the wrong expert near interfaces".
- Report item 6 is now stale: it says no anchor/noise floor exists. G3 is PASS
  as of 2026-07-29 (`state/gates.md`), so numeric thresholds ARE available.

## 2. program.md §12.4 conventions (verbatim)

> ### 12.4 `s4_hybrid_routing` (lever)
>
> - **Anchor**: champion's certified panel geomean (batch 0).
> - Quantified prior: the FNO↔Transolver **pairwise oracle is +30.6%** over FNO
>   alone (Transolver wins 16/38 despite being 2× worse on average).
>   `mf_field/akash/models/fno_transolver_seq` (sequential FNO→Transolver
>   residual hybrid) is BUILT but unbenchmarked — batch 1 should start by
>   scoring it on the panel (cheap, mostly evaluation).
> - The surviving novelty is the **MF composition** (routing, per-band/per-region
>   gating, which fidelity feeds which expert) — the base hybrids themselves are
>   published (WLNO, Park 2507.06133, SINO; see §5 pre-falsified list and the
>   prior-art reports).
> - Transolver-side caveat: `transolver_residual` is best-in-zoo on 4 of the 5
>   beyond-copy datasets — whatever routing is learned should preserve its
>   behavior there.

Anchor (`state/anchors/s4_hybrid_routing.json`, `provisional: false`):
`mf_fno_transfer_film`, panel geomean skill **6.703** CI95 [6.219, 7.102],
per-seed [7.102, 6.219, 6.788], smoke tier 200 epochs, seeds {0,1,2}.

Noise floor (`state/noise_floor.json`, `min_claimable_effect` in skill units):
helmholtz **9.695** (on mean skill 13.82 — a diverging seed; ~70% relative),
pfc **1.151** (11.51), allen_cahn **1.633** (16.33), fisher_kpp **0.418**
(4.18), cahn_hilliard **0.553** (5.53), ifc_poisson **0.240** (1.566, 15.3%).
Four sharp floors are exactly 10% relative; helmholtz is unfalsifiable at smoke
tier unless a design attacks the instability itself (`state/gates.md` alert).

## 3. Within-stream prior cards

**None.** `find experiment_cards -name '*.json'` returns nothing — batch 1 is
the stream's first card. `state/s4_hybrid_routing/current_batch.txt` = `1`,
`current_stage.txt` = `brainstormer_running`.

## 4. Cross-stream prior cards

**None** (no cards exist anywhere yet). Relevant sibling context that is not a
card: `s3_testtime` shares the "frozen certified-strong base + corrector" shape
(program.md §12.3), and ADR 0003 records that `mf_fno_ptr`'s refinement bought
−1.5% inside the CI at 163× latency — a caution that "corrector on a frozen
base" is not automatically a win.

## 5. Reopen candidates

**None** — no prior cards, hence no `reopen_candidate: true` entries.

## 6. What is UNKNOWN (the load-bearing section)

**U1 — the champion never sees the LF field at test time.** Verified by reading
`mf_field/factory_mffp/models/mf_fno_transfer_film/smoke_eval.py`:
`model = FNO2d(cond_dim, ...)`; the LF field appears only as *pretraining
targets* (`_train(model, X_lf, Y_lf, ...)` then `_train(model, X_hf, Y_hf, ...)`).
So the certified champion is a **parametric surrogate**, not a test-time
multi-fidelity field model, while the copy-LF reference *is* the LF field.
Nobody in this round has yet measured what happens when a model consumes the
real test-time LF field on the panel. That is the single biggest unknown behind
"skill 4–16 on sharp 2-D", and it is exactly what `fno_transolver_seq` changes:
its corrector cross-attends to a 1024-point **real LF context cloud** whenever
the test split carries LF (all five npz_l panel datasets do; verified
`test_l1/l2/l3.npz` present for each).

**U2 — does the +30.6% pairwise oracle survive on sharp 2-D?** The oracle is a
factory-bench number over 38 mostly-smooth datasets; nothing measures it on the
five sharp panel sets against copy-LF. Unknown, and cheap to settle.

**U3 — what does the gate actually select?** `fno_transolver_seq` fits `alpha`
by least-squares + a line search containing 0 on a held-out split with
`MIN_GAIN = 1e-3`, so `alpha` is a *measured, self-testing* scalar: `alpha = 0`
means the correction failed its own held-out test. Per-dataset `alpha` values
are the routing prior any D2 card needs and nobody has them.

**U4 — cost of the composition.** Unknown before measurement: the hybrid runs
LF-pretrain + HF-finetune + K=4 out-of-fold refits + corrector + optional joint
stage ≈ 5.25× the champion's epoch budget. Batch-0 timings
(`state/timing_ledger.json`): champion 200-epoch runs took 44.4 min on each of
allen_cahn/fisher_kpp/cahn_hilliard, 12.3 min pfc, 7.7 min helmholtz, 0.8 min
ifc_poisson (p100). Naive ×5 puts the three 256² datasets near 3.5–4 h/seed.

**U5 — plumbing risk (partly retired).** I ran the family at contract tier on
`ifc_poisson` (CPU, `--epochs 2`): it completed, printed
`ctx_source=fno_base` (ifc test ships HF only, so it falls back to the base
prediction as context — expected), `alpha=1.5001`, and
`rel_l2=0.438569 base_only=0.490003` — i.e. even a 2-epoch corrector beat its
own base by 10.5% on the test split. Still unknown: whether the 256² sharp sets
fit in p100 memory at `n_query=2048 / n_ctx=1024 / corr_batch=4`, and whether
the worktree copy resolves `from common.mffp import ...` (the family does
`sys.path.insert(0, Path(__file__).resolve().parents[2])`, which points at
`<worktree>` rather than `<repo>/mf_field/akash` once copied to
`models_r1/<family>/`).

**U6 — where routing should be applied.** Whether the correction concentrates
near interfaces (SPAMoE's prior) or is spread uniformly is unmeasured; the
family already records `correction_rms_raw_units`, but not a spatial map.

**U7 — helmholtz instability.** The 9.695-unit floor comes from a diverging
seed at 200 epochs (`state/gates.md`). Whether the hybrid inherits that
divergence (it reuses the identical FNO recipe) is unknown, and no helmholtz
claim is falsifiable until someone fixes it (that is a `s5_tuning`-shaped
problem, not this stream's).
