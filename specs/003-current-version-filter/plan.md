# Implementation Plan: Current-version evidence (M5)

**Branch**: planning on `main`; separate implementation branch later
**Date**: 2026-10-19 | **Spec**: [spec.md](spec.md)

## Summary

Implement one intent: exclude superseded chunks before scoring when
`CURRENT_ONLY=True`. Preserve the disabled path. Target E06's contradictory
citations, without promising an increase beyond 10/12.
The wider roadmap is [advanced-plan.md](../../docs/advanced-plan.md).

## Technical Context

**Language/Version**: Existing Python virtual environment; local verification
used Python 3.13.7. Record actual versions again at implementation baseline.
**Primary Dependencies**: Standard library; pytest 8.3.3. No new dependency.
**Storage**: Existing corpus and JSON/text evidence.
**Testing**: Root pytest, fixed eval runner, compare tool and CLI.
**Target Platform**: Existing local Windows environment; no platform-specific feature.
**Project Type**: Local CLI/library.
**Performance Goals**: One eligibility pass over the existing small chunk list.
**Constraints**: Preserve scoring, top-k, thresholds, chunking, corpus, questions,
metric code and M1/M3 evidence.
**Scale/Scope**: Ten handbook documents, twelve official questions.

## Constitution Check

Pre-research and post-design checks reach the same conclusion:

- One controlled change: PASS. M5 only; M2 and embeddings are future experiments.
- Fixed evaluation: PASS. No edits to questions or metric code.
- Evidence before code: PASS for planning; implementation first saves fresh
  tests, eval and CLI E06/E05/E11 with expected/actual behavior and failure type.
- Local and simple: PASS. Existing config/architecture, no dependencies.
- Honest results: PASS by design; report contradictions, unchanged failures,
  regressions and the historical-query limitation.
- Submission sequence: planning proceeds; optional implementation is scheduled
  after minimum submission. Submission is unconfirmed. Prior M3 timing deviation
  stays documented; this plan does not waive the assignment.

## Project Structure

```text
specs/003-current-version-filter/
  spec.md
  checklists/requirements.md
  plan.md
  research.md
  data-model.md
  contracts/retrieval.md
  quickstart.md
src/config.py               # enable existing CURRENT_ONLY
src/retrieval.py            # existing searchable_chunks hook
tests/test_retrieval.py     # eligibility and compatibility
tests/test_rag.py           # E06 answer/citation checks if needed
docs/evidence/003-m5/       # measurements at implementation
docs/m5-report.md           # results at implementation
```

Root directories remain the working project. Starter and Week 6 are preserved.

## Phase 0: Research

Completed in [research.md](research.md), including a read-only research review.
Existing metadata and the eligibility hook support a small implementation.
No unresolved technical questions or external dependencies are required for M5.

## Phase 1: Design and Contracts

- [data-model.md](data-model.md): reuse source status without schema changes.
- [contracts/retrieval.md](contracts/retrieval.md): enabled/disabled semantics.
- [quickstart.md](quickstart.md): baseline, candidate and comparison procedure.

Replace the existing NotImplementedError in searchable_chunks with stable
filtering on status != "superseded" when CURRENT_ONLY is enabled, then enable
that switch. Do not sort version strings, change scores, mutate chunks or
alter tie breaking.

Meaningful tests cover mixed statuses, all-superseded/empty input, unchanged
disabled behavior and current E06 evidence. Run all existing tests and the fixed
eval. Passing E06 alone cannot establish that its stale two-day rule is gone.

## Measurement and Decision

At implementation, save fresh before/after JSON, test/eval/CLI logs, config and
source/eval hashes under docs/evidence/003-m5/. Preserve M1/M3 runs.
Compare with src.eval_compare: only CURRENT_ONLY should change. Save the code
diff before adding measurement and report artifacts.

Hypothesis: the ten current passes remain, E06 contains only current evidence,
and E05/E11 remain explicit limitations. Report any regression without adding
another improvement. Retain M5 only when its target improves without lost passes;
otherwise preserve the negative result.

## Scope of Completion

Specification, research and design only. Task generation and implementation
follow separately; no tasks.md or implementation completion is implied.
All additional work this week is conditional on available time. Keep planning
documents on main; create a new branch when starting M5. LLM generation may be
planned separately only if time remains after required submission and demo work.
