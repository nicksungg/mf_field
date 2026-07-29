# Summary so far — Stream `s4_hybrid_routing`, Batch 2

Packed 2026-07-29 from files read (never recalled): `websearches/s4_hybrid_routing/batch_2/report.md`,
`experiment_cards/s4_hybrid_routing/batch_1/B1.json` (parts 4–7), `experiment_cards/s6_local/batch_{1,2}/B*.json`,
`state/{anchors/s4_hybrid_routing.json,noise_floor.json,timing_ledger.json}`, `eval/copylf_baselines.json`,
`eval/score_panel.py`, `tools/index.md`, `worktrees/s4_hybrid_routing/B1/models_r1/fno_transolver_seq/{smoke_eval.py,model.py}`,
`state/s4_hybrid_routing/review_B1.md`, `program.md`, `docs/adr/000{4,5,7,9}*.md`.

## 1. Websearch findings + prior-art verdict (batch 2)

Source: `websearches/s4_hybrid_routing/batch_2/report.md` (5 iterations, cap hit; 15 searches / 14 fetches).

- **(i) gate-split repair → `preempted (cite)`.** The estimator is published for neural operators: Operator Boosting
  (https://arxiv.org/html/2606.17460, fetched) selects each stage weight on a validation split over a grid *containing 0*,
  *"each stage validation-safe: if a trained correction does not reduce validation error, it can be rejected"*; its base is
  *"the empirical mean output field"* and the fetch confirms *"This is **not** multi-fidelity"*. Wolpert's rule comes through
  https://arxiv.org/pdf/1106.1684 (fetched in the s6-B2 loop): *"the combiner must be trained on predictions from base
  classifiers applied to held-out data"*. Shrinkage theory: `sum alpha_hat <= 1` (https://arxiv.org/html/2309.09880),
  two-smoother Mallows'-Cp = James–Stein (https://arxiv.org/html/2309.14596), both *"purely statistical regression"*.
  Open: the **MF instance**, the **inversion failure mode**, and **B1's measured -43% price**. Verdict instruction:
  *"**Claim ZERO mechanism novelty. The card is a protocol-defect measurement with a quantified cost**"*.
- **(ii) dense LF context → `preempted-but-MF-composition-open (cite)`.** *"Increasing M enhances contextual information ...
  thereby improving performance up to a saturation point"* (https://arxiv.org/html/2502.09692v3); sparse-anchor
  cross-attention is explicitly a learned interpolator (https://arxiv.org/pdf/2605.15305). Four independent negatives:
  nobody ablates the **spatial** density of an LF field used as corrector context. Mandatory pre-registration: the
  **skill-1.0 ceiling** and the **free scalar control** `base + a*(copylf - base)` (B1 F13: pfc 0.114384 vs 0.125893;
  fisher_kpp 0.202549 vs 0.226409).
- **(iii) attention-vs-local head-to-head for the fidelity-gap defect → `novel`**, and *"the prior art is **hostile to
  attention**"*: Physics-Attention *"can be reformulated as a special case of linear attention, and ... the slice attention
  may even hurt the model performance"*, gains from *"the slice and deslice operations themselves"*
  (https://arxiv.org/abs/2511.06294); attention beats Fourier only on *"irregular geometries"* (2605.08318); the best
  coarse-field corrector in a four-way comparison is *"a deep FiLMed residual network with spectral convolutions"*
  (2511.09729v1); P2C2Net's coarse-corrector ablation *"does not employ attention mechanisms anywhere"* (2411.00040);
  on Cahn-Hilliard *"E-UNO and UNO consistently achieve errors an order of magnitude lower than FNO"* with no attention
  baseline (2509.01293v3). *"Either outcome closes the stream's class."*
- Explicit refusals carried in: **do not resurrect routing in any spatial form** (verdict §5) and publish
  RMS/cosine next to every gate value (verdict §6).

## 2. program.md §12.4 conventions (verbatim)

> ### 12.4 `s4_hybrid_routing` (lever)
>
> - **Anchor**: champion's certified panel geomean (batch 0).
> - Quantified prior: the FNO<->Transolver **pairwise oracle is +30.6%** over FNO
>   alone (Transolver wins 16/38 despite being 2x worse on average).
>   `mf_field/akash/models/fno_transolver_seq` (sequential FNO->Transolver
>   residual hybrid) is BUILT but unbenchmarked — batch 1 should start by
>   scoring it on the panel (cheap, mostly evaluation).
> - The surviving novelty is the **MF composition** (routing, per-band/per-region
>   gating, which fidelity feeds which expert) — the base hybrids themselves are
>   published (WLNO, Park 2507.06133, SINO; see §5 pre-falsified list and the
>   prior-art reports).
> - Transolver-side caveat: `transolver_residual` is best-in-zoo on 4 of the 5
>   beyond-copy datasets — whatever routing is learned should preserve its
>   behavior there.

Anchor (`state/anchors/s4_hybrid_routing.json`): `mf_fno_transfer_film` panel geomean **6.703016262587087**,
ci95 [6.21853605194748, 7.102239525443188], 3-seed, `provisional: false`. Geomean floor convention (s5-B1) =
ci95 width **0.8836555** = 13.183% relative. Cratered = 1.5x anchor = **10.0545**.

## 3. Within-stream prior cards

`experiment_cards/s4_hybrid_routing/batch_1/B1.json` — `complete`, `reopen_candidate: false`, `anchor_reference: null`,
recipe `{fno_transolver_seq, 967562e..., models_r1/fno_transolver_seq, panel, 200, [0,1,2], MFFP_CTX_SOURCE=auto}`,
build commit `4691d1fbaaa4dc9e0e6fbaf3bf607afef203404c` (branch `round1/exp-s4_hybrid_routing-B1`).

Part 5 (provisional-single-seed): panel geomean **5.664889** (-15.5% vs anchor; below the anchor ci95 lower bound but
only -0.554 vs the anchor's best seed, inside the 0.884 floor). Per-dataset nRMSE / skill / alpha:
helmholtz 6.543507/19.8619/a=0 (a_ls=1.5, clip artifact) · ifc_poisson 0.055635/1.5454/a=0 (a_ls=0) ·
allen_cahn 0.263550/16.3171/a=0 (a_ls=0) · **cahn_hilliard 0.487628/5.5627/a=0 (a_ls=1.1027, vetoed)** ·
**fisher_kpp 0.226384/3.6145/a=0.7408** · **pfc 0.146958/3.2817/a=0.2509, stage3 fired**. 91.4% of the panel move is
pfc, 9.5% fisher_kpp; guard clean (2/3 below copy-LF at contract tier); walltime **122.93 GPU-min/panel on H100**
(per dataset: allen_cahn 31.28, cahn_hilliard 30.73, fisher_kpp 28.88, helmholtz 15.47, pfc 15.47, ifc_poisson 1.10).

Part 6 findings that set this batch: **F1** the "held-out" split is held out for the corrector only, never the base
(`smoke_eval.py:354` fine-tunes on ALL `X_hf`, split drawn at `:391-392`); **F2** the cahn_hilliard veto was WRONG —
a_ls 1.1027 is the test optimum to 0.9%, test nRMSE 0.500684->0.284617 (-43.2%, skill 5.5627->**3.1622**), correction/residual
cosine 0.629 on 50/50 samples; **F3** three a=0 modes (collapsed corrector: allen_cahn RMS ratio 0.00063 / helmholtz 0.0076;
orthogonal: ifc_poisson cosine 0.138; vetoed-good: cahn_hilliard RMS 0.778, cosine 0.629); **F6** the correction is
collinear with `copylf - base` (cosine 0.834/0.642/0.538) and orthogonal to `hf - copylf` (<=0.023) => ceiling skill 1.0;
**F7** one scalar `base + a*(copylf - base)` matches/beats the whole corrector; **F10** the correction is genuinely
per-sample-LF-keyed (permuting LF inverts the pfc gain to +46.5%); **F11** per-pixel/per-sample gates buy <=5.3% and are
negative on 2/3 => routing refused; **F12** repaired-gate panel accounting 5.664889->5.137357 (**inside** the 0.884 floor)
=> cahn_hilliard is a per-dataset claim, not a geomean claim; **F13** using a_ls instead of the line search costs **8.47x**
on pfc (0.125893->1.066448) => the shrinkage is load-bearing. Coverage (from the family JSONs): ctx grids 128^2=16384 pts at
n_ctx 1024 -> **6.25%** on allen_cahn/cahn_hilliard/fisher_kpp, 64^2 -> **25%** on pfc, and **100%** already on
helmholtz (576) and ifc_poisson (1024). N_hf = 400 on all five sharp/ext datasets (val split = 80), 5 on ifc_poisson.

Part 7: LICENSED-1 (gate-split repair, shrinkage KEPT), LICENSED-2 (dense LF input), **REFUSED** spatially-resolved
routing, **DEFERRED** C5 boosting/cascades; standing reporting requirement (RMS ratio + cosines beside every gate value).

## 4. Cross-stream cards touching this stream

- `s6_local-B1` (`complete`): trust-gated **local** corrector on the real LF field, panel geomean **0.234572**; seed-0
  test nRMSE pfc 0.00134416 / allen_cahn 0.00130074 / **fisher_kpp 0.00595834 (skill 0.09513)** / cahn_hilliard 0.04107603 /
  helmholtz 0.32945013 (= copy-LF exactly) / ifc_poisson 0.05563172. Its F6/F14 zero-parameter closed-form **LSI** floor:
  pfc 0.00061247, allen_cahn 0.00083196, **fisher_kpp 0.00769508 (skill 0.122861)**, cahn_hilliard 0.03856875 — promoted as
  `tools/defect_correction_learnability.py` (`rho_val > 0.9` => the defect is mostly a linear filter).
- `s6_local-B2` (`drafted`, builder running): control-and-repair sweep (`b1_replica`, `circ_repair`, `lsi_ctrl`,
  `trust_head_circ`, `pointwise_ctrl_circ`); predicts `lsi_ctrl` geomean 0.197223. Establishes the round's convention for
  multi-arm sweeps, per-arm `ROUND1_EVAL_RESULTS`, vendored-not-imported LSI, and relative-floor accounting at a
  skill scale far below the anchor's.
- `s2_beyond_copy-B1` part 7 / B2 (in review): owns the trained LF-residual FNO and the training-free retrieval floors
  (L5 kNN-in-LF 0.55-0.61 on pfc/cahn_hilliard, 1.068 on fisher_kpp = Class B).
- Boundary that follows: **s6 owns the local/closed-form corrector's standalone use; s2 owns the LF-residual FNO;
  s4 uniquely owns the ATTENTION corrector class and the head-to-head that decides it.**

## 5. Reopen candidates

**None.** `s4_hybrid_routing-B1` is `status: complete`, `reopen_candidate: false`, and it is the stream's only prior card
(`ls experiment_cards/s4_hybrid_routing/` -> `batch_1` only). Two *parked branches* from B1 part 7 must still be resolved
by this batch's design: (a) REFUSED spatially-resolved routing (headroom-priced under every floor, F11), (b) DEFERRED C5
boosting/cascades (gated on stage 1 reaching skill < 1, which B1 did not).

## 6. What is UNKNOWN (the section that decides the design)

1. **Does the repaired gate keep the shrinkage where shrinkage is what saved the card?** The repair makes both halves of
   `_fit_alpha` score against an out-of-sample base. On cahn_hilliard that recovers -43%. On **pfc** the shipped a=0.2509
   *is* the test optimum while a_ls=0.9944 costs 8.47x — and a_ls is precisely the base-OOF-consistent estimate. So the
   direction of the pfc move under repair is genuinely unknown, and the two candidate gate protocols have **opposite,
   one-sided biases**: scoring on the memorised base biases a -> 0 (cost measured: -43% forgone on cahn_hilliard); scoring
   on an out-of-sample base biases a up because the deployed base is stronger than the base the gate saw (cost bounded by
   F13's 8.47x on pfc). Nobody has priced both sides on one substrate; 2606.17460 itself *"does not explicitly confirm
   whether validation data is withheld"*.
2. **Is 1024 context points a capacity limit or the wrong target?** B1's part-7 open question states both readings predict
   opposite designs, and its coverage correlation (25% -> cosine 0.834 / R^2 0.906 vs 6.25% -> 0.54-0.64 / R^2 0.30-0.43) is
   n=3 and MEDIUM confidence, with helmholtz a counterexample at 100% coverage.
3. **Does content-adaptive nonlocality add ANYTHING over the local/closed-form class on the same substrate?** Unknown and
   unpublished (verdict iii). One pro-attention datapoint exists (B1's fisher_kpp -12.2%, band-1 nonlinearity); the fetched
   prior predicts attention loses; and s6 has a zero-parameter filter at skill 0.1229 and a trained local corrector at
   0.0951 on that dataset. Unknown *sub-question* that decides the interpretation of a loss: is it that nonlocality does not
   pay, or that this corrector never *sees* local LF structure (its per-query LF view is one soft-interpolated scalar plus
   32 global slice tokens)?
4. **Structurally unknowable at N_hf = 400 with an 80-sample val split**: the deployed full-data base's out-of-sample
   residual scale. Every gate estimator must proxy it, and each proxy's bias is one-sided (unknown #1).
5. Not unknown, do not re-measure: routing granularity (F11), a_ls-without-line-search (F13), whether the correction is
   LF-keyed (F10), whether the base inside the hybrid is the champion (part-5 sanity gate, 16-digit agreement).
