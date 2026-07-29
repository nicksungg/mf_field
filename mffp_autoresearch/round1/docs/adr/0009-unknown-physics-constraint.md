# ADR 0009 — Unknown-physics constraint on test-time methods (operator action)

**Status:** accepted 2026-07-29 (directed by Eloise, relaying mentor guidance:
"we have to assume we don't know the PDE sometimes or the physics is too
complicated to embed in the model, especially for weather")

## Decision

From batch 2 onward, no candidate MODEL may require the governing equations
(exact residual, known operator, known free energy) at test time. Methods
must work in the unknown-physics regime — the benchmark's era5/weather-like
setting is the canonical case.

Physics-aware constructions remain allowed ONLY as:
- diagnostics / upper-bound measurements (like s3-B1, which measures whether
  the exact residual is even a usable signal where it exists), or
- training-time regularizers on datasets where physics is known, IF the
  model degrades gracefully to a physics-free path at test time.

## Effect on s3_testtime

- s3-B1 (in flight) completes as designed: it is a diagnostic, exempt above,
  and its expected outcome is the evidence base for this ADR.
- s3 batch 2 re-scopes to PHYSICS-AGNOSTIC test-time levers: learned error
  estimators, self-consistency / cross-fidelity agreement signals, test-time
  adaptation on the LF input, ensembling-at-inference — or, if the B1
  diagnostic and prior-art landscape leave no credible direction, the stream
  retires and its slot budget returns to the pool (§4.2 skip mechanics, not
  abandonment-by-failure).

## Corroborating in-repo evidence (predates this ADR)

- s3-B1 websearch: true residual computable on 1/6 panel datasets only.
- s3-B1 brainstormer probes: helmholtz HF test fields reproducible to 2.2e-13
  from the condition vector via two FFTs (exact-operator methods trivialize
  the dataset); the 1-dof residual-optimal rescale collapses copy-LF 0.33 →
  0.996 (residual norms are roughness meters, not error meters).
