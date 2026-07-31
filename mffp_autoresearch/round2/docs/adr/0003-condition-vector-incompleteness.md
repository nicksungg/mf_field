# ADR r2-0003: The condition vector is NOT complete on 3 of 5 sharp datasets

Date: 2026-07-31. Status: accepted (orchestrator correction, pre-first-card).
Source: r2s1-B1 websearcher read-only measurement
(`websearches/r2s1_direct/batch_1/`, summary + report), verified against
`state/anchors/floors.json` structure.

## Finding

Spec §4 ("grounding facts verified 2026-07-30") and the launch program's
§12.1/§13.1 claimed each sharp `meta.json` certifies the HF field is a
learnable function of the condition vector. Direct measurement contradicts
this for three datasets:

- `sharp__phase_field_crystal_2d` (`param_names: [r, mean_density]`),
  `sharp__fisher_kpp_2d` (`[D, r]`), `sharp__allen_cahn_2d`
  (`[eps, mobility, mean_composition]`) carry **no initial-condition
  parameters**. Only `sharp__cahn_hilliard` does (16 of its 19 dims are
  `ic_c*`).
- pfc: the two closest-in-condition train samples (standardized distance
  0.0124) differ by relative field 1.149 — and the SAME index pair differs
  by 1.148 in `train_l1.npz`. The per-sample random IC lives in the LF
  field, not in the condition vector. fisher_kpp: 0.343 (HF) / 0.412 (LF).

## Consequences

1. On pfc / fisher_kpp / allen_cahn, condition→HF is a **stochastic map**: a
   deterministic model can at best estimate the conditional mean. This is why
   `train_mean` beats `nn_condition` on pfc and fisher_kpp in the frozen
   floors. **Skill → 1 is unreachable** for any condition-only deterministic
   model there; the reachable floor is the conditional-mean (aleatoric)
   floor, which r2s4 should certify per dataset (prior art for the
   diagnostic: arXiv:2605.28076 "Diagnosing the Conditional-Mean Barrier",
   fetched by the websearcher).
2. Round-2 claims on those datasets must be read against the
   conditional-mean floor, not against skill 1.0. Success criterion 2
   (program §1) remains satisfiable via the other datasets (cahn_hilliard,
   helmholtz, ifc_poisson) or via criterion 1.
3. This is simultaneously the round's sharpest value-of-LF statement: the
   train-time LF field CONTAINS the missing driver (the realized IC) that
   the condition vector omits — r2s2/r2s3 designs can target exactly that
   information channel, and r2s1's D3 (identifiability certification) is the
   legitimate open composition.
4. Benchmark recommendation to the mentor (WRITTEN, not an action): sharp
   generators should either export the IC seed/parameters into `params` or
   document the stochastic-map semantics; spec §4's grounding fact needs the
   same correction. Program §12.1/§13.1 corrected at launch+0 (no card had
   been designed yet).
