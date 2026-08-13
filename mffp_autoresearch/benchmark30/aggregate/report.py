"""Leaderboard -> report tables (spec D9): every number comes from
`state/leaderboard.json`; nothing is hand-computed.  The narrative shell
around these tables is written at Phase B step 4 and fact-check-converged.
"""
from __future__ import annotations

import json
from pathlib import Path

MODEL, FILM = "r3s2_route_b30", "mf_fno_transfer_film"


def render_tables(lb: dict) -> str:
    lines = []
    h = lb.get("headline")
    if h:
        lines += [
            "## Headline — film-relative skill (common eligible set, "
            f"{len(lb['common_eligible_set'])} datasets)",
            "",
            f"Panel geomean of `nrmse_film / nrmse_model`, per seed: "
            + ", ".join(f"{v:.4f}" for v in h["per_seed_geomean"]) + ".",
            f"**{h['mean']:.4f}** [{h['interval'][0]:.4f}, {h['interval'][1]:.4f}] "
            f"({h['interval_kind']}; >1 means the certified stack beats film transfer).",
            "",
        ]
    if lb.get("group_geomeans"):
        lines += ["## Per-group geomeans", "",
                  "| group | n | mean | interval |", "| --- | --- | --- | --- |"]
        for g, v in sorted(lb["group_geomeans"].items()):
            lines.append(f"| {g} | {len(v['datasets'])} | {v['mean']:.4f} | "
                         f"[{v['interval'][0]:.4f}, {v['interval'][1]:.4f}] |")
        lines.append("")
    lines += ["## Per-dataset rel-L2 (3-seed mean [min, max])", "",
              f"| dataset | {MODEL} | {FILM} | skill (film/model) |",
              "| --- | --- | --- | --- |"]
    for ds in sorted(lb["per_dataset"]):
        row = lb["per_dataset"][ds]
        def cell(f):
            e = row.get(f)
            return (f"{e['mean']:.4f} [{e['min']:.4f}, {e['max']:.4f}]" if e else "—")
        skill = (f"{row[FILM]['mean'] / row[MODEL]['mean']:.4f}"
                 if MODEL in row and FILM in row else "—")
        lines.append(f"| {ds} | {cell(MODEL)} | {cell(FILM)} | {skill} |")
    lines.append("")
    cov_gaps = {ds: c for ds, c in lb["coverage"].items()
                if ds not in lb["common_eligible_set"]}
    if cov_gaps or lb.get("exclusion_ledger"):
        lines += ["## Coverage gaps and exclusions", "",
                  "| dataset | family | seeds present / reason |", "| --- | --- | --- |"]
        for ds, c in sorted(cov_gaps.items()):
            for f, n in c.items():
                if n < len(lb["seeds"]):
                    lines.append(f"| {ds} | {f} | {n}/{len(lb['seeds'])} seeds |")
        for f, entries in sorted(lb.get("exclusion_ledger", {}).items()):
            for ds, reason in sorted(entries.items()):
                lines.append(f"| {ds} | {f} | LEDGERED: {reason} |")
        lines.append("")
    lines += [f"Provenance: manifest `{lb.get('manifest_hash', '?')[:16]}`, "
              f"registry `{lb.get('registry_revision', '?')}`, "
              f"inputs `{lb['inputs']}`.", ""]
    return "\n".join(lines)


def main() -> None:
    campaign = Path(__file__).resolve().parents[1]
    lb = json.load(open(campaign / "state/leaderboard.json"))
    out = campaign / "docs/report_tables.md"
    out.write_text(render_tables(lb))
    print(f"tables -> {out}")


if __name__ == "__main__":
    main()
