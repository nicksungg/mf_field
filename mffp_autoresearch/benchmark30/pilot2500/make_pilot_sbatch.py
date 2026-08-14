#!/usr/bin/env python3
"""Generate the epoch-ladder pilot sbatch scripts (b30 pilot2500).

Derives every pilot script by mechanical transformation of the two certified
benchmark_30 seed-0 full-campaign scripts (rev-eac7b48e) so the 79KB frozen
--env blocks are never hand-edited.  Transforms applied per (family, epochs,
dataset-subset) job:

  1. path swap  /benchmark30/rev-eac7b48e/ -> /benchmark30/pilot2500/
     (isolates results/cache/logs/diag from the closed campaign)
  2. --epochs 200 -> --epochs {E} and _e200_ -> _e{E}_ in artifact names
  3. keep only the run_ds lines for the pilot dataset subset
  4. job-name / --time rewrite

The e200 rung is NOT rerun: seed-0 e200 results for all pilot datasets
already exist under rev-eac7b48e and are read by aggregate_ladder.py.
"""
import re
import sys
from pathlib import Path

SRC_SBATCH = Path("/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch_outputs/benchmark30/rev-eac7b48e/sbatch")
OUT_SBATCH = Path("/resnick/groups/Hippo/ezeng/mf_field/mffp_autoresearch_outputs/benchmark30/pilot2500/sbatch")

OLD_ROOT = "/benchmark30/rev-eac7b48e/"
NEW_ROOT = "/benchmark30/pilot2500/"

SRC = {
    "r3s2_route_b30": SRC_SBATCH / "b30-r3s2_route_b30-s0-full-seed0.sbatch",
    "mf_fno_transfer_film": SRC_SBATCH / "b30-mf_fno_transfer_film-s0-full-seed0.sbatch",
}

PICKS = [
    "sharp__fisher_kpp_2d",   # biggest r3s2 win (6.42x)
    "ext__helmholtz_2d",      # r3s2 win (5.16x)
    "sharp__allen_cahn_2d",   # r3s2 win (2.63x)
    "poisson_local",          # narrowest film win (0.935)
    "sharp__euler",           # narrow film win (0.924)
    "darcy_generated",        # narrow-ish film win (0.821)
    "ifc_heat",               # round-3 home turf that flipped to film (0.234)
    "poisson_generated",      # worst r3s2 blowout (0.123)
]

R3S2_E2500_A = ["sharp__fisher_kpp_2d", "ext__helmholtz_2d", "poisson_local", "ifc_heat"]
R3S2_E2500_B = ["sharp__allen_cahn_2d", "sharp__euler", "darcy_generated", "poisson_generated"]

# (family, epochs, datasets, walltime, jobname)
JOBS = [
    ("r3s2_route_b30",       600,  PICKS,        "10:00:00", "b30p-r3s2-e600"),
    ("r3s2_route_b30",       2500, R3S2_E2500_A, "16:00:00", "b30p-r3s2-e2500-a"),
    ("r3s2_route_b30",       2500, R3S2_E2500_B, "16:00:00", "b30p-r3s2-e2500-b"),
    ("mf_fno_transfer_film", 600,  PICKS,        "06:00:00", "b30p-film-e600"),
    ("mf_fno_transfer_film", 2500, PICKS,        "16:00:00", "b30p-film-e2500"),
]

RUN_DS_RE = re.compile(r"^run_ds (\S+) ")


def split_script(text: str):
    lines = text.splitlines(keepends=True)
    ds_lines = {}
    header, tail = [], []
    seen_run = False
    for ln in lines:
        m = RUN_DS_RE.match(ln)
        if m:
            seen_run = True
            ds_lines[m.group(1)] = ln
        elif not seen_run:
            header.append(ln)
        else:
            tail.append(ln)
    return "".join(header), ds_lines, "".join(tail)


def transform(chunk: str, epochs: int, jobname: str, walltime: str) -> str:
    out = chunk.replace(OLD_ROOT, NEW_ROOT)
    out = out.replace("--epochs 200 ", f"--epochs {epochs} ")
    out = out.replace("_e200_", f"_e{epochs}_")
    out = re.sub(r"(?m)^#SBATCH --job-name=.*$", f"#SBATCH --job-name={jobname}", out)
    out = re.sub(r"(?m)^#SBATCH --time=.*$", f"#SBATCH --time={walltime}", out)
    # the two r3s2 e2500 jobs would otherwise share one failures file
    out = out.replace("_failures.txt", f"_failures_{jobname}.txt")
    return out


def main() -> int:
    OUT_SBATCH.mkdir(parents=True, exist_ok=True)
    parsed = {fam: split_script(p.read_text()) for fam, p in SRC.items()}
    written = []
    for fam, epochs, datasets, walltime, jobname in JOBS:
        header, ds_lines, tail = parsed[fam]
        missing = [d for d in datasets if d not in ds_lines]
        if missing:
            sys.exit(f"source script for {fam} lacks run_ds lines for: {missing}")
        body = "".join(ds_lines[d] for d in datasets)
        script = (
            transform(header, epochs, jobname, walltime)
            + transform(body, epochs, jobname, walltime)
            + transform(tail, epochs, jobname, walltime)
        )
        for bad in ("rev-eac7b48e", "--epochs 200 ", "_e200_"):
            if bad in script:
                sys.exit(f"{jobname}: residual '{bad}' after transform")
        n_run = sum(1 for ln in script.splitlines() if RUN_DS_RE.match(ln))
        if n_run != len(datasets):
            sys.exit(f"{jobname}: expected {len(datasets)} run_ds lines, got {n_run}")
        dest = OUT_SBATCH / f"{jobname}.sbatch"
        dest.write_text(script)
        written.append((dest, len(datasets)))
        print(f"wrote {dest}  ({len(datasets)} datasets, epochs={epochs}, time={walltime})")
    print(f"{len(written)} scripts OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
