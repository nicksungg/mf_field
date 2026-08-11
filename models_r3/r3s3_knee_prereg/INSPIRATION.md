# INSPIRATION — `r3s3_knee_prereg`

Card: `r3s3_lf_value-B3` — *pre-declared knee-predictability of the coverage
ladder: a zero-anchor training-free structural prediction of the step-max knee
cap on the film-transfer cells, sealed before any leg runs and confirmed by a
minimal ratio-4 ladder, adjudicated in ADR r3-0006 film units*.

Provenance (card `recipe.base_family`, verbatim):

> `models_r3/r3s3_row_efficiency` @ `eedcc655b70471687c9b7f8e537ad206eddd437c`
> (branch `round3/exp-r3s3_lf_value-B2`, card `r3s3_lf_value-B2`), vendored
> **BYTE-FOR-BYTE** with provenance comments into the NEW family
> `models_r3/r3s3_knee_prereg`. PLUS `models_r3/_common/ckpt_binding.py`
> vendored byte-for-byte from commit `da855da` (branch
> `round3/exp-r3s4_audit-B2`, path `models_r3/_common/ckpt_binding.py`), which
> imports the UNEDITED `round3/tools/ckpt_data_binding.py`. NEW in this card:
> (1) ladders read from the sealed pre-registration instead of the hardcoded
> `CAP_LADDERS` dict; (2) dataset-general model-free stratification mask (top 27
> percent of test rows by nearest-train-HF-field rel-L2) replacing the ch-only
> imported mask; (3) `ckpt_binding` save hook (batch-3 contract requirement);
> (4) film-unit reporting through `state/anchors/film_denominator.json`. NOT a
> round-1 family, NOT `mf_fno_transfer_film` (that is the ADR r3-0006
> DENOMINATOR, never an arm here), NO teacher/distillation/pretrain-finetune/
> auxiliary-loss arm (all preempted or certified null on B1), and the B2 D-D
> mediator clause is NOT re-run (B2 part 7 item 4).

Round-2 immutable §5.10's rebadge question — "is this a rebadge of a round-1
family?" — answers **no** on both the forward signature
(`forward(cond, out_hw) -> (B,H,W)`; no field input ever) and the pathway.

## Vendoring audit (how to check the byte claim)

| file | relation to the source blob |
|---|---|
| `model.py` | BYTE-IDENTICAL to `eedcc655:models_r3/r3s3_row_efficiency/model.py` |
| `lf_reference.py` | prefix-free + **ONE forced delta**: the ADR r3-0005 pfc entry (`SPECTRAL_RUNG_DATASETS`, `_spectral_zeropad_up`, the `spectral_zeropad_rung1` convention), vendored verbatim from the amended `eval/panel_data.py`. B2's copy predates the amendment and never ran pfc; this card does, and its own per-leg seam assert (`verify_against_eval`, tol 1e-9) caught the stale classification at `max abs diff 1.400141e-01` on the first pfc smoke. Registration-of-lifts (round-2 §12 / ADR r2-0004) requires the model-side lift to BE the eval layer's. Verified in-session: max abs diff **0.0** on all six datasets this card touches. |
| `affine_probe.py` | identical modulo the `R3S3B2_`→`R3S3B3_` prefix |
| `coverage.py` | identical modulo the prefix |
| `eval_seam_binding.py` | identical modulo the prefix — RENAMED from `data_binding.py` (that module name is taken by the shipped `mffp_autoresearch/preflight/data_binding.py`, which `tools/ckpt_data_binding.py` imports read-only; a family module of the same name shadowed it and broke CARDED CHANGE 3). Contents unchanged. |
| `refs.py` | identical modulo the prefix |
| `smoke_eval.py` | prefix + THE FOUR CARDED CHANGES (each marked at its site) |
| `prereg.py` | NEW (CARDED CHANGE 1: the sealed ladder + its digest assert) |
| `reporting.py` | NEW (CARDED CHANGE 4: film units, G5 band, tolerances, mean-removed) |
| `../_common/ckpt_binding.py` | BYTE-IDENTICAL to `da855da:models_r3/_common/ckpt_binding.py` |
| `<worktree>/tools/ckpt_data_binding.py` | BYTE-IDENTICAL to the live `round3/tools/ckpt_data_binding.py` (unedited; the path `ckpt_binding.py` itself expects) |

```bash
git show eedcc655:models_r3/r3s3_row_efficiency/<f> | sed 's/R3S3B2_/R3S3B3_/g' | diff - <f>
git show da855da:models_r3/_common/ckpt_binding.py | diff - ../_common/ckpt_binding.py
diff <round3>/tools/ckpt_data_binding.py <worktree>/tools/ckpt_data_binding.py
```

## The prior-art verdict this family executes

`websearches/r3s3_lf_value/batch_3/report.md`, row **K1**, reproduced verbatim
in the card's `prior_art.verdict_quoted`:

> **K1 — pre-registered knee prediction** on the film-transfer cells: emit the
> training-free surrogate's predicted step-max knee cap *before any leg runs*,
> then confirm with a minimal 3-cap ladder — **preempted-but-MF-composition-open**
> — citations: <https://arxiv.org/pdf/2201.12150> (projective early stopping;
> `b_sat`; pre-exponential point); <https://arxiv.org/pdf/2210.14891> (BNSL: no
> way to extrapolate past an unobserved break);
> <https://kneed.readthedocs.io/en/stable/> (Kneedle knee detection);
> <https://arxiv.org/html/2606.02662> (MF: fixed ratio heuristic vs reactive
> tolerance); <https://arxiv.org/pdf/2102.01293> (exchange rate `D_T`; "cheaply
> predict the ideal pre-training ratio" listed as future work) — **What remains
> open**: "Do not claim saturation-point prediction, knee detection, or an
> exchange rate. Open: **zero anchors on the target cell** (all retrieved
> predictors consume a partial curve there); a **training-free structural**
> predictor rather than meta-features or a sibling-curve corpus; the **MF
> condition-coverage** axis with LF absent from the test path; and
> **pre-declaration + adjudication** of a numeric cap."

**METHOD-ONLY CITATION IS BINDING HERE** (card `_reporting_discipline`).
`b_sat` / projective early stopping (arXiv 2201.12150), Kneedle
(kneed.readthedocs.io), the effective-data-transferred exchange rate
`D_T = k(D_F)^a N^b` (arXiv 2102.01293) and pre-registration for predictive
modelling (arXiv 2311.18807) are cited as **method**, never as findings of this
card. The novelty sentence the card permits, verbatim: BNSL states "there does
not (currently) exist a way to extrapolate the scaling behavior after that
additional break" (arXiv 2210.14891) and the survey's meta-feature branch still
consumes a partial empirical curve on the target dataset — **our prediction uses
ZERO anchors on the target cell.**

**INSTRUMENT PRICING, declared before the prediction** (card
`_reporting_discipline`): the surrogate
(`round3/tools/coverage_knee_surrogate.py`, promoted by B2) is a SHAPE/KNEE
predictor, **not a baseline** — on `sharp__cahn_hilliard` its full-pool nRMSE
0.5753 is 11 % worse in level than the trained arm's 0.5178, and
`--kernel linear` collapses to Pearson 0.622. The linear-kernel knee is carried
in the seal as a **specificity control** for exactly that reason.

Carried forward from the base families, still cited where the corresponding code
survives: **C1/C2** (the LF-count-sweep genre and the coverage sentence are
published — quote, never claim: <https://arxiv.org/pdf/2301.01699>,
<https://arxiv.org/pdf/2408.17075>, <https://arxiv.org/html/2409.07947v1>,
<https://arxiv.org/html/2402.17061v1>); **C3** (the forward-sensitive
subpopulation; the PLOS identifiability vocabulary
<https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1013553>
is used in the OPPOSITE sense in that literature and is therefore **banned** —
`smoke_eval._assert_no_banned_terms` enforces the ban on every result JSON, and
the nearest published mechanism for the subpopulation is the rarity+memorization
account <https://arxiv.org/abs/1906.05271>, cited and explicitly contrasted);
**E3b** (a discretisation-independent mode budget,
<https://arxiv.org/html/2310.00120>); **E4** (training-free gate statistics —
reported, never a switch, <https://arxiv.org/abs/2403.08118>).

## What is measured, and what may be claimed

The deliverable is a **pre-registered prediction adjudicated in film units**, not
a panel-geomean improvement: the card claims **no Δ vs anchor** and leaves the
launch best-floor geomean untouched. `A3c_lf_uncov_cap` runs at the sealed
`r1`/`r2`/`r3`; `A1_lf_all` IS `r4 = FULL`; `A0_nolf` is the numerator baseline
of `R`. The claimable object is whether the sealed `c_pred` equals the trained
step-max knee `K` on each **adjudicable** predictive cell (chance 1/3 per cell),
where adjudicable means a film-unit deciding margin above one **certified**
`tau_rel_film` AND a seed-unanimous knee. `sharp__phase_field_crystal_2d` has no
certified `tau_rel` and is registered CONDITIONALLY; the ifc cells are
pre-declared **UNRESOLVED** and that is itself a reportable metrology result.
Never the sweep genre, never the coverage sentence, never a ch copy-LF skill
delta (ch is reference-free, ADR r3-0003 D2, MDD 1.7077). Every ifc number is
reported beside `affine_on_hf_train` **with its leave-one-out fold range** and
the paper bar (program.md §2), and every `nn_condition`-priced statement carries
the G5 fit-set band (batch-3 scope rule 5).
