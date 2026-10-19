# Tasks: M2 stopword filtering

**Input**: [plan.md](plan.md), [spec.md](spec.md), research, data model and contract.
**Tests**: Focused checks explicitly requested by FR-006. Branch remains `main`.

## Phase 1: Setup

- [X] T001 Save unchanged tests, full eval, configuration/hashes and two actual failures in docs/evidence/004-m2/baseline.md and before.json.

## Phase 2: Foundational

- [X] T002 Write and validate specs/004-stopword-filter/spec.md, plan.md, research.md, data-model.md, contracts/retrieval.md and quickstart.md; freeze the list and update docs/advanced-plan.md before source changes.

## Phase 3: User Story 1 - Informative-word search (P1, MVP)

**Goal**: Implement the fixed symmetric filter with a working disabled mode.
**Independent test**: Generic stopword-only overlap disappears; meaningful matches,
qualifiers, repeated words and empty-input behaviour satisfy the contract.

- [X] T003 [US1] Add focused enabled/disabled, qualifier, empty-input, filtered-score and irrelevant-match checks in tests/test_retrieval.py, and empty-query refusal in tests/test_rag.py; observe failure before implementation.
- [X] T004 [US1] Replace the placeholder in src/retrieval.py with the frozen set: "Exactly 40 unique lowercase words, immutable, frozen in plan.md"; preserve the scorer and both-input symmetry.
- [X] T005 [US1] Enable only STOPWORDS_ENABLED in src/config.py, preserving every other setting.
- [X] T006 [US1] Run the full root python -m pytest with the project virtualenv and save docs/evidence/004-m2/pytest-after.txt.

## Phase 4: User Story 2 - Reviewable measurement (P2)

**Goal**: Supply complete evidence for the user's retention decision and next step.
**Independent test**: Read both full runs and comparison; verify all regressions,
fingerprint, disabled-mode baseline reproduction and actual changed citations.

- [X] T007 [US2] Run the unchanged full eval and src.eval_compare, save docs/evidence/004-m2/after.json and compare.txt, and inspect/store CLI evidence for changed cases and E04/E05/E06/E09/E10/E11.
- [X] T008 [US2] Verify protected hashes and disabled baseline with docs/evidence/004-m2/verify.py; preserve implementation.diff and write docs/m2-report.md with all regressions, limitations and retain/reject recommendation.

## Phase 5: Polish and handoff

- [X] T009 Update README.md and docs/advanced-plan.md with measured M2 status; leave human review pending, embeddings user-owned next and grounded LLM separate later.
- [X] T010 Review scope and whitespace, complete specs/004-stopword-filter/tasks.md and report the concrete human-review handoff without starting another experiment.

## Dependencies and execution order

T001 -> T002 -> T003 -> T004 -> T005 -> T006 -> T007 -> T008 -> T009 -> T010.
US1 delivers filtering independently of reporting. US2 is independently reviewable
from saved artifacts after US1 measurement. No task implements human review,
embeddings or an LLM. All 10 task entries follow checkbox, ID and path format.

## Parallel opportunities

Research review was independent and read-only. Within US1 the two test files could
be authored independently; within US2 saved CLI checks are independent after the
run. Execution is sequential for a small change and to preserve baseline ordering.

## Implementation strategy

Finish evidence and design first. Observe requested checks failing, implement the
single filter intent, then measure once without tuning. Finalize a report even if
pass count is unchanged or worse. Hand off on main for the user's human review.

## Completion outcome

All 10 tasks are complete (US1: four; US2: two; setup/foundation/handoff: four).
Enabled M2 passes 53 tests but regresses E09, 10/12 -> 9/12. The user explicitly
selected keeping it implemented but disabled. The final default False passes all
53 tests and reproduces the entire 10/12 baseline except timestamp. Both measured
states, diffs and integrity reports are preserved. Human review is pending;
embeddings and grounded LLM work have not started. No extension hooks are installed.
