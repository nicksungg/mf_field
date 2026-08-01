# Summary so far — stream `r2s3_lf_train_signal`, batch 4

## 1. Websearch findings and prior-art verdict

Source: `mffp_autoresearch/round2/websearches/r2s3_lf_train_signal/batch_4/report.md` (5/5 iterations, cap hit; 15 WebSearch calls, 12 curl fetches because `WebFetch` is disabled in this environment).

Verdict row (a), the only cardable direction, verbatim:

> | **(a)** LF-free **gain/amplitude head** conditioned on the condition vector, fitted on the same 5 HF rows, used as a **substitution test** for LF's train-time value (training-free probe on shipped dumps first, then one confirmatory arm) | **preempted-but-MF-composition-open** | https://arxiv.org/abs/2601.09143 (**curl-fetched**; DiSOL Methods §4.1: per-sample amplitude u_lim, dimensionless pattern, "optional **amplitude regressor**" — the mechanism verbatim, in PDE operator learning); https://arxiv.org/abs/2508.01341 (**curl-fetched**; LCC = affine de-shrinkage on a small held-out calibration split, Tweedie local de-shrinkage, no new labels, domain-general); https://distill.pub/2018/feature-wise-transformations/ (search return; FiLM γ = learned scale, "specialized HyperNetwork"); https://arxiv.org/abs/2606.20771 (**curl-fetched**; controlled amplitude normalization + "mean relative L² … may obscure"); https://arxiv.org/abs/2202.03365 (**curl-fetched**; control-baseline discipline) | Only the **composition**: using the head as a **control that prices auxiliary low-fidelity training data**. … **The deliverable is the measured share of the ±LF effect the LF-free head absorbs — never the head itself.** |

Row (b) (budget-matched no-LF ensemble) is `preempted-but-MF-composition-open` (weak) — "admissible as an arm inside (a)'s card, never as the card's claim".
Row (c) (claimability-protocol repair) is `preempted` by Bouthillier et al. (arXiv:2103.03098): "**Bootstrapping data stands out as the most important source of variance … model initialization generally is less than 50% of the variance of bootstrap**"; adopt as methodology, do not card.
Row (S): the regime is named — LUPI / privileged-information distillation, 2026 surrogate instance Mazloom et al., DOI 10.1016/j.engappai.2025.113398 (metadata Crossref-verified, body unobtainable); what still differentiates this stream is batch 3's P1 list: copy-LF denominator, N_hf = 5, genuine coarse consistent solves, condition-completeness-varying panel.

## 2. Program §12.3 conventions (verbatim)

> ### 12.3 `r2s3_lf_train_signal` (lever)
>
> - **Question**: LF as training-only signal. Candidate mechanisms (spec §6):
>   distillation from an LF-consuming teacher (round-1 families in role §5.10b
>   — teacher at train, absent at test), LF-pretrain → HF-finetune, auxiliary
>   multi-fidelity losses (predict LF and HF jointly from condition).
> - **The stream has a mandatory declared baseline**: `mf_fno_transfer_film`
>   (factory zoo champion) IS LF-pretrain→HF-finetune from the condition
>   vector (verified 2026-07-31: its test input is `cond_by_fid` only; it runs
>   on the stripped view unmodified). Any r2s3 pretrain/finetune proposal must
>   either score it as the baseline arm or cite how it differs — an
>   undifferentiated re-proposal is a rebadge (reviewer FAIL, §5.10).
> - **revin_lf two-scaler finding** (r1 s5): exact at LF-pretrain, 3.1% proxy
>   at HF — normalization transfer across fidelities is a solved sub-problem;
>   reuse it, don't rediscover it.
> - **Nested-ladder degeneracy** (r1 report §6) directly constrains this
>   stream: with aligned/nested ladders, "multi-fidelity" training pairs
>   degenerate toward top-rung replication — LF-as-signal designs must state
>   what information the LF rungs add that the HF rung does not already
>   contain (spectral truncation structure, more samples at low rungs on
>   ifc_poisson: 70 lower-fidelity vs 5 HF).
> - The **unified normalization eligibility rule** (r1 s2, checks 0–6) governs
>   any per-sample normalization proposal; spread is not the decider.
> - Uses the existing 400 aligned samples only (§5.11).

Common §12 conventions also bind: quote the launch anchor (best-floor panel geomean **23.063616857615774**, `state/anchors/r2s3_lf_train_signal.json`) and the per-dataset floor table; thresholds must clear the certified noise floor; floor arms mandatory on model cards; every proposal carries a complete `recipe`.
`state/noise_floor.json` is no longer provisional (`_provisional: false`, `_source: r2s4_diag-B1`), so per-dataset `min_claimable_effect` is now a real numeric gate: ifc 0.9377041289531141, ch 0.09124535322300886, fk 0.0007136812826775696, ac 0.8797047190126648, pfc 0.21302734961699343, hz 2.95299157437233, panel geomean 1.1418668211296108.

## 3. Within-stream prior cards

- **B1** (`experiment_cards/r2s3_lf_train_signal/batch_1/B1.json`, complete): established the declared-baseline gate — `mf_fno_transfer_film` on ifc_poisson, 200 ep, seed 0, nRMSE 0.055637439592454, skill 1.5454844331237223, hashes `d3d0ade9…`/`9753ff24…`.
- **B2** (batch_2/B2.json, complete): null-supply arms; M1 priced the null-direction penalty as net harmful; the coverage arm `A1_lf_cov` was the arm that carried the effect.
- **B3** (batch_3/B3.json, complete, job 66196690, 33 legs, 55 min): matched budget-equal ±LF contrast at N_hf = 5 over the full panel, 3 HF-subset draws, training seed 0. Per-leg skills (read from the shipped result JSONs under `mffp_autoresearch_outputs/round2/r2s3_lf_train_signal/B3/eval/`): ifc A0 8.1344 / A1 2.1501; ch A0 30.0783/27.2499/24.7591, A1 12.6346/12.5199/12.6042; fk A0 16.9436/16.1862/15.7831, A1 15.2504/15.4330/14.2898; ac A0 974.6846/248.6262/311.2808, A1 212.7816/212.3721/212.7306; pfc A0 61.4735/57.5015/65.3019, A1 65.2111/63.1476/63.5946; hz A0 7.6311/18.1430/5.0380, A1 3.5959/5.9591/4.1065. F1 and F2 **falsified**; F3 and F5 held; F4 fired on a single-member antecedent set.
  Mechanism (part 6): **M1** LF-at-train is an amplitude-calibration signal first (96.9% of A0's allen_cahn draw-range is one scalar per sample); **M1b** LF pins the *scale*, not the *map* (ac's three A1 models score within 0.41 skill units while sitting 100.5 apart in function space); **M2** shrinkage reward at the conditional-mean bound (pfc's −2.56 is the predicted sign); **M3** capacity is not binding (a 12-mode truncation of the true HF field scores skill 0.09 on pfc); **M4** the residual structural value of LF does not follow the affine-coverage partition; **M5** a 3-draw no-LF ensemble beats A1 on fk (−1.61) and pfc (−9.43) but loses badly on ac (+219.17) and ch (+11.78); **M6** helmholtz is a ratio between two non-learners.
  Part 7 ranks the B4 candidates: (a) *is the gain channel LF-free?* — "cheap, training-free on the shipped dumps first"; (b) budget-matched ensemble; (c) claimability-protocol repair. Explicit do-not: "Do NOT propose more LF-supply engineering on fisher_kpp or pfc." Promoted tools: `effect_threshold_readings.py`, `map_dispersion_scale_shape.py`.

## 4. Cross-stream cards

Light scan of parts 7 for references to this stream: B3's own `cross_stream_notes` pushes four items *out* (scale-not-map, clause-writing/threshold provenance, capacity-not-binding, shrinkage reward).
No round-2 card in `r2s1_direct`, `r2s2_stacked` or `r2s4_diag` carries a part 7 that attacks a constraint this stream owns; `r2s4_diag-B2` (value-of-LF accounting with LF as an auxiliary *target*) came back **falsified** — |T1−T0| inside the operative threshold in 15/15 cells — which is why B3 was the round's only live route to criterion 1.
`r2s1_direct-B3` is still `running` and `r2s2_stacked-B3` is `drafted`, so neither can feed this batch.

## 5. Reopen candidates

None.
Every round-2 card in all four streams has `reopen_candidate: false` and `skipped_reason: null` (verified by reading all 12 card JSONs).

## 6. What is UNKNOWN

1. **Is the amplitude channel LF-free?** B3's M1 says LF's dominant action is pinning per-sample output scale, and a per-sample *oracle* gain collapses A0's draw ranges by 1.5–73×. What no one has measured is whether an **achievable** LF-free head — keyed on the condition vector, supervised only by the 5 HF rows the arm already has — recovers a material share. This is the round's central open question because the answer changes the character of the deployment claim in both directions (part 7's own framing).
2. **What the achievable head can even be fitted on.** The only honest supervision for an LF-free head is the 5 HF train rows. Whether those rows expose *any* calibration error is unknown a priori: if the arm interpolates them, the in-sample gain is identically 1 and the head degenerates to the identity map. (A read-only pre-flight on the shipped dumps settles this; see `iteration_1.md` § Pre-flight — the answer is sharp and it reshapes the design.)
3. **Whether the ±LF effect is priced against the right control at all.** B3 uses A0_nolf as the control. The card's own leg JSONs already contain *stronger* LF-free controls (`ref_linear_hfonly`, `ref_zero`, `ref_train_mean_n5`, `ref_nn_condition_n5`) that were reported as floors and never as substitutes. Nothing in the round has yet asked "how much of the ±LF effect survives when the control is the **best** LF-free alternative rather than the matched arm" — which is exactly the composition arXiv:2202.03365 prescribes, and the websearcher's most valuable dead end ("is the auxiliary-data gain just calibration?" → no usable results) leaves it open.
4. **Which criterion-1 legs survive that substitution.** B3's three claimable datasets are unequal by construction (ch strong; ifc single native draw, mce-only by construction; fk fragile — M5 shows an LF-free ensemble beats A1 there). Whether the claimable set is still of size 3 after substitution, and whether its membership changes, is unknown and decidable from artifacts already on disk.
5. **How much of the effect is a ceiling artifact vs an achievable alternative.** The gap between the achievable head and the test-fitted ceilings (global gain, condition-keyed ridge, per-sample oracle) is the honest error bar on "LF does something no free post-hoc fix can do". None of the three ceilings has been computed in the *control-substitution* framing: B3 T3-4 corrected **both** arms, which answers the different question M4 asks.
6. **Whether a B5 is warranted or the stream closes.** Unknown until (1)–(5) are measured; the measurement costs minutes on shipped dumps and no GPU training, which is why the B4-or-close decision resolves toward carding a training-free diagnostic rather than closing blind.
