# ADR r2-0004: Round-2 hardware tier is gpu:nvidia_h200:1 (uniform)

Date: 2026-07-31. Status: accepted (orchestrator logistics decision, pre-any-result).

## Context

project.yaml carried `gres: gpu:h100:1` from round-1 ADR 0005. At first
submission the gpu partition had 169 pending jobs and SLURM estimated
**2026-08-07** (a full week) for our h100 requests, while 3 nvidia_h200
nodes sat idle. H200 is the same Hopper sm90 architecture as H100 (same
kernels, same nondeterminism envelope class per the r1 §7 finding — which
keys tolerance to hardware TIER, satisfied by keeping one tier); the round-2
slurm_rules already rank `nvidia_h200 ≥ h100` in the fast tier.

## Decision

Switch the ENTIRE round to `gpu:nvidia_h200:1`, uniformly, before any
round-2 job produced a number (all four queued jobs were still PENDING —
`scontrol update Gres=` applied in place; they started within minutes).
Every subsequent submission uses `SBATCH_GRES=gpu:nvidia_h200:1` at submit
time (env var overrides the in-script `#SBATCH --gres`, so builder scripts
need no edits). project.yaml `sbatch.gres` updated to match reality; this
ADR is the §5.3 paper trail (logistics config, not a scoring surface;
same precedent as r1 ADR 0005).

## Consequences

- Single-tier comparability preserved: zero jobs ran on h100.
- Timing-ledger entries are h200-calibrated; walltime defaults unchanged.
- If h200 contention ever mirrors h100's, the fallback order is
  slurm_rules §3 (h100, then l40s); any further switch needs the same
  pre-result or between-batch discipline plus an ADR.
