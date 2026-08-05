# Universal context (read at startup; memoize)

Every subagent reads these at the top of its run and keeps them in memory for
the duration of the invocation. Do NOT re-read mid-run.

## 1. project.yaml — resolve runtime variables

Parse `${ROUND_ROOT}/project.yaml` and resolve the path variables your
subagent will reference.

**Path portability**: the `paths:` section holds entries relative to
`${PROJECT_ROOT}` (the mf_field repo root), NOT absolute paths. The preamble
below auto-detects `${PROJECT_ROOT}` via `git rev-parse` and absolutifies
every path, so any checkout can run the round without editing `project.yaml`
(ADR 0001 / the quadruped round's Layer-A rationale).

A minimal preamble subagents can paste:

```bash
PROJECT_ROOT="$(git -C /resnick/groups/Hippo/ezeng/mf_field rev-parse --show-toplevel)"
ROUND_ROOT="${PROJECT_ROOT}/mffp_autoresearch/round3"

eval "$(PROJECT_ROOT="${PROJECT_ROOT}" "${PROJECT_ROOT}/.venv/bin/python" - <<'PY'
import os, yaml
root = os.environ["PROJECT_ROOT"]
cfg = yaml.safe_load(open(f"{root}/mffp_autoresearch/round3/project.yaml"))
print(f'PROJECT_ROOT={root}')
for k, v in cfg["paths"].items():
    abs_path = v if os.path.isabs(v) else os.path.normpath(os.path.join(root, v))
    print(f'{k.upper()}={abs_path}')
print(f'PANEL={",".join(cfg["panel"])}')
print(f'GUARD_SET={",".join(cfg["guard_set"])}')
print(f'SEEDS={",".join(str(s) for s in cfg["seed_protocol"]["seeds"])}')
print(f'CRATERED_SKILL_FACTOR={cfg["seed_protocol"]["cratered_skill_factor"]}')
print(f'SMOKE_EPOCHS={cfg["tiers"]["smoke_epochs"]}')
print(f'CONTRACT_EPOCHS={cfg["tiers"]["contract_epochs"]}')
print(f'SLURM_ALGO_CAP={cfg["caps"]["slurm_algo_attempts"]}')
print(f'REVIEW_FAIL_CAP={cfg["caps"]["review_fail_attempts"]}')
print(f'STREAM_ABANDON_CAP={cfg["caps"]["consecutive_skips_for_stream_abandonment"]}')
print(f'SBATCH_PARTITION={cfg["sbatch"]["partition"]}')
print(f'SBATCH_GRES={cfg["sbatch"]["gres"]}')
PY
)"
```

After this, `${PROJECT_ROOT}`, `${ROUND_ROOT}`, `${OUTPUTS_ROOT}`, `${VENV}`,
`${FACTORY_ROOT}`, `${DATA_ROOT}`, `${STRIPPED_DATA_ROOT}`, `${EVAL_DIR}`, `${PANEL}`, `${GUARD_SET}`,
`${SEEDS}`, the caps, and the sbatch settings are available (paths absolute).

## 2. program.md

Read `${ROUND_ROOT}/program.md` once. Sections every subagent needs:
- §1 Goal (and the two success criteria)
- §2 Score system (nRMSE definition, copy-LF skill, panel, tiers)
- §4 Structure (streams, batches, card types, 1+2 seeds, skip rule)
- §5 Fair-comparison immutables + pre-falsified levers — these govern every edit
- §6 Subagent roster
- §12 Per-stream conventions (anchors, seed directions, noise-floor rule)
- §13 Project overview

Subagent-specific extra reads (e.g. builder also reads §9 commands) are listed
in each subagent's §1a.

## 3. Other shared partials

| Partial | Read if you |
|---|---|
| `handoff_convention.md` | Read/write handoff memos in `<worktree>/notes/` |
| `decision_discipline.md` | Make a judgment call grounded in the task |
| `card_update.md` | Edit experiment card JSON |
| `return_format.md` | (Every subagent — the return format to the orchestrator) |
| `pre_return_checklist.md` | (Every subagent — the pre-return verification shape) |
| `env_activation.md` | Run python/bash that needs the venv or determinism env |

## 4. Subagent-specific context

After the universal reads, each subagent's own §1a lists additional reads
(the card it operates on, prior handoffs, specific configs). Those live in the
subagent's prompt, not here.
