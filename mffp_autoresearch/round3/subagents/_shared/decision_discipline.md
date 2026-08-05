# Decision discipline

Several subagents must make judgment calls as part of their role — which
experiment to propose, which search terms to run, where to probe next. Make
those calls yourself, in a focused pass, grounded in the task. (Round 3 runs
without a taste oracle — program.md §7.)

## 1. Ground every decision in the task

Base your judgment on the project's own definition of the work, read from
program.md:
- **§1 Goal / §13 overview** — the research question (why multi-fidelity
  fusion fails on the critical panel; skill < 1 on the beyond-copy datasets;
  ifc_poisson at the paper bar).
- **§2 score system** — the copy-LF-skill panel geomean, CI convention, and
  the noise-floor rule.
- **§5 immutables** — the hard constraints every experiment must respect,
  including the pre-falsified levers.
- **§12 per-stream conventions** — the stream's anchor, seed directions, and
  quantified priors.

## 2. Own your decisions and record the reasoning

Where your role calls for a judgment, decide it and write down the reasoning
that led there — at a level of detail someone could audit — in the same files
your role already produces. Every decision that appears in a report must trace
back to recorded reasoning.

## 3. Keep the interfaces stable

Use exactly the output paths and filenames your role specifies, so downstream
subagents read them unchanged.

## 4. Honesty

Every claim traces to a file you actually wrote or read — verify by reading
back, don't trust memory. If you genuinely cannot make a defensible call from
the task context, say so plainly (or mark the slot `skipped` with a reason)
rather than inventing one.
