# Implementation Plan: M2 stopword filtering

**Branch**: `main` | **Date**: 2026-10-19 | **Spec**: [spec.md](spec.md)

**Input**: The approved M2 experiment; embeddings belong to the user after review.

## Summary

Replace the existing stopword-option placeholder with filtering against one
frozen 40-word set, then enable that option. Preserve all other pipeline code
and settings. Save a full before/after comparison even if no failures are fixed.

## Technical Context

**Language/Version**: Existing Python; measured virtualenv is Python 3.13.7.
**Primary Dependencies**: Standard library and existing pytest 8.3.3; none added.
**Storage**: Existing in-memory corpus and JSON evidence under docs/evidence/004-m2.
**Testing**: Focused tokenizer/scoring/empty-input checks, full pytest, full eval,
existing eval_compare, CLI inspection and hash/disabled-mode verification.
**Target Platform**: Existing Windows/PowerShell environment, repository-root commands.
**Project Type**: Local CLI/library.
**Performance Goals**: No new model, network operation or external process per query.
**Constraints**: One intent; fixed eval/metrics; no scoring/threshold/top-k tuning.
**Scale/Scope**: Ten documents, 12 unchanged evaluation questions, one 40-word list.

## Constitution Check

Pre-research and post-design checks both pass within the explicitly authorized scope:

- One intent: symmetric stopword filtering, activated by the existing flag.
- Fixed evaluation: preserve eval/eval_set.json and src/eval_runner.py/eval_compare.py.
- Evidence first: 43 passing tests, fresh 10/12 baseline, source manifest and E05/E11
  failure evidence already saved before implementation.
- Local and simple: no dependency, model, service or infrastructure change.
- Honest reporting: report all regressions, unchanged failures and citation changes;
  human review is pending and is not performed by this implementation.
- Reference directories and historical experiment files remain untouched.

The assignment schedules advanced work after minimum submission. Submission is
unconfirmed; the user's explicit instruction authorizes this additional M2 work
now on main. Record that timing exception, without changing the constitution.

## Project Structure

```text
specs/004-stopword-filter/
  spec.md, plan.md, research.md, data-model.md, quickstart.md, tasks.md
  checklists/requirements.md
  contracts/retrieval.md
src/retrieval.py                 # fixed set and conditional token filtering
src/config.py                    # STOPWORDS_ENABLED=True only
tests/test_retrieval.py           # focused filtering/scoring checks
tests/test_rag.py                 # empty filtered query refusal
docs/evidence/004-m2/             # saved before/after, CLI, integrity and diff
docs/m2-report.md                 # measured outcome and handoff
docs/advanced-plan.md, README.md  # agreed sequence and current state
```

**Structure Decision**: Reuse the existing root pipeline and interfaces; no setup work.

## Phase 0: Research decisions

The read-only research agent confirmed a general 40-word list, no question-specific
terms, and risks from changed denominators and empty filtered inputs. Decisions
and alternatives are in [research.md](research.md). There are no unresolved choices.

Freeze this exact list before implementation:

```text
a an and are as at be been but by can do does for from had has have how i
in is it of on or that the their there these they this to was were what when where with
```

Preserve negation (`not`, `no`, `never`, `without`), `until`, and numeric tokens.
Do not add `new`, `leave`, `policy`, synonyms, or any per-evaluation-case rules.

## Phase 1: Design and verification

Use a module-local immutable set in retrieval.py. Apply membership filtering after
the existing regex and lowercasing. This automatically affects both scoring inputs.
Keep count-based scoring, sorting, retrieval minimum, refusal threshold, citations,
current-version filter and sentence chunks unchanged. Disabled mode retains the
old token stream; existing empty-input handling remains responsible for score zero.

Write the requested focused tests first and observe the missing implementation.
Then implement filtering and enable STOPWORDS_ENABLED. Run the full suite and
unchanged full eval, compare via src.eval_compare, and inspect changed answers
including E04/E06/E09/E10/E11 and the E05 target. Report metric and per-case
regressions without retuning. Verify historical hashes and disabled-mode baseline
reproduction using the evidence helper.

Retain M2 if the experiment has no material supported-answer/behaviour regression
and improves or preserves evidence quality. If it regresses, document a reject
recommendation and retain the implementation behind its flag; do not invent a
second change. Hand off the concrete evidence for the user's review.

## Complexity Tracking

Only the authorized timing exception above applies. Implementation introduces no
new architectural complexity. Human review and future experiments are outside
the implementation task list.
