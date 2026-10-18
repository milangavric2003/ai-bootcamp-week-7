# Week 7 RAG Constitution

## Core Principles

### I. One Controlled Change

The required homework MUST apply exactly one intentional RAG improvement between
the before and after measurements. M1-M6 in `docs/improvement-menu.md` are choices,
not a checklist. Multiple edited lines or files MAY implement one intent; combining
independent changes, such as stopword filtering and threshold calibration, does not.
Any optional second improvement MUST follow the submitted minimum and be measured
separately against the result of the first.

### II. Fixed Evaluation

`eval/eval_set.json` and the code that calculates evaluation metrics MUST remain
unchanged. Before and after runs MUST use the same complete 12-question set, the
same runner, and matching evaluation SHA-256 values. Quality claims MUST rely on
these measurements; passing unit tests alone does not establish answer quality.

### III. Evidence Before Implementation

Before changing the RAG pipeline, run the tests, save the unchanged baseline, and
document at least two failures by evaluation question ID, expected result, actual
result, and failure type. Write the chosen change specification before implementing
it. The specification MUST include the observed failure, hypothesis, proposed
change, expected effect, regression risk, and verification procedure.

### IV. Local and Simple

The required experiment MUST use the existing local Python pipeline. It MUST NOT
introduce a vector database, embedding service, paid API, or new infrastructure.
Reuse the current architecture and configuration switches. Prior Week 6 work MAY
inform the selected improvement, but unrelated scoring, normalization, chunking,
or answering changes MUST NOT be copied along with it.

### V. Honest Results and Review

The report MUST include the before and after results, comparison output, every
regression, and at least one remaining limitation. Documenting two failures does
not require fixing both. An unconfirmed hypothesis is acceptable when measured
and explained honestly. Include the peer review, AI usage and verification note,
both contributors' work, and the demonstration lead required by the assignment.

## Project Boundaries

- The working project is the repository root: `src/`, `tests/`, `eval/`, and `docs/`.
- `rag-week-7-weak-checkpoint/` is the preserved original; `week06/` is reference
  material. Neither reference directory is an implementation target for Week 7.
- Run project commands from the repository root. `pytest.ini` limits normal test
  discovery to the working copy's `tests/` directory.
- Spec Kit is development tooling. Its installation does not constitute a RAG
  improvement, and feature work MUST remain separate from setup changes.
- Keep skills in `.agents/skills/` and shared templates and helpers in `.specify/`.
  Additional integrations, extensions, and automated workflows are optional.

## Experiment Workflow

1. Run `python -m pytest` and
   `python -m src.eval_runner --out results/before.json` on the unchanged pipeline.
2. Inspect retrieved evidence and document at least two concrete failures.
3. Use the specification and planning artifacts to record exactly one change and
   its regression risk before modifying implementation code.
4. Implement that change and run the tests again.
5. Run `python -m src.eval_runner --out results/after.json`, then
   `python -m src.eval_compare results/before.json results/after.json`.
6. Manually check the answer and citations with the CLI for a question whose result
   changed. If none changed, report that and verify the targeted case explicitly.
7. Prepare the before/after report and obtain the required peer review.

Saved result JSON files are ignored by the starter's `.gitignore`. Include both
actual result files in the submission, for example as attachments or by explicitly
tracking those specific files. Preserve the comparison output and implementation
diff alongside the report. Assistant claims MUST NOT replace measured evidence.

## Governance

This constitution derives from `docs/weekly-assignment.md`, the session slides,
and `docs/improvement-menu.md`. Explicit user instructions take precedence over
this document; flag conflicts with the assignment instead of silently changing
the experiment's scope. Review specifications, plans, tasks, and implementation
diffs against these principles.

Record amendments with their reason and date. Use a major version for incompatible
principle changes, a minor version for added or materially expanded principles,
and a patch version for clarifications. Update affected feature artifacts when
an amendment changes their obligations. Keep completed experiment artifacts as
the historical record of what was specified, implemented, and measured.

**Version**: 1.0.0 | **Ratified**: 2026-10-18 | **Last Amended**: 2026-10-18
