# Tasks: Current-version evidence (M5)

**Input**: spec.md, plan.md, research.md, data-model.md and contracts/retrieval.md.
**Execution**: On `main`, per the user's 19 October instruction. No new branch.
**Tests**: Requested in the specification and implementation request.

## Phase 1: Setup

- [X] T001 Record the user's execution instructions in specs/003-current-version-filter/plan.md and verify the completed specification checklist.

## Phase 2: Foundational evidence before implementation

- [X] T002 Save baseline tests, complete eval, comparison to M3, CLI E06/E05/E11 and source/eval/result hashes in docs/evidence/003-m5/.
- [X] T003 Document E06's contradiction and E05/E11 failures with expected/actual outcomes and types in docs/evidence/003-m5/baseline.md before changing pipeline code.

## Phase 3: User Story 1 — Current policy evidence (P1)

Independent check: E06 answers with the current three-day rule and no superseded
retrieved or cited chunks; disabling the switch preserves previous behavior.

- [X] T004 [P] [US1] Add eligibility, ordering, disabled-path and empty-result tests in tests/test_retrieval.py, then record the preimplementation failures in docs/evidence/003-m5/pytest-red.txt.
- [X] T005 [P] [US1] Add current-policy answer and no-eligible-evidence refusal tests in tests/test_rag.py, included in the red run.
- [X] T006 [US1] Implement stable superseded filtering before scoring in src/retrieval.py and enable CURRENT_ONLY in src/config.py without changing other settings.

## Phase 4: User Story 2 — Reproducible assessment (P2)

Independent check: saved before/after measurements and the comparison support the
reported outcome; original M1/M3 results and official evaluation remain unchanged.

- [X] T007 [US2] Run all tests, the fixed eval and comparison, and CLI controls E04/E05/E06/E09/E10/E11; save outputs in docs/evidence/003-m5/.
- [X] T008 [US2] Save the implementation diff and integrity verification in docs/evidence/003-m5/; confirm disabled-mode reproduction and no changes to eval questions or metric code.
- [X] T009 [US2] Write docs/m5-report.md with results, regressions, limitations, AI execution and contributors; update README.md and docs/advanced-plan.md to reflect actual progress.

## Phase 5: Completion

- [X] T010 Reconcile status and reproduction guidance in specs/003-current-version-filter/spec.md, plan.md and quickstart.md; validate documentation, diff and completed tasks.

## Dependencies and parallel opportunities

T001 → T002 → T003 → T004/T005 → red test run → T006 → T007 → T008 → T009 → T010.
T004 and T005 affect different files and can be prepared independently after
baseline documentation. Their shared red run follows both edits. US2 needs US1's
candidate implementation for the after measurement; baseline evidence is shared.

Parallel example for US1: prepare retrieval eligibility tests and RAG integration
tests in their separate files. US2's measurements run sequentially so saved
evidence clearly identifies the same candidate. No delegated agents are needed.

## Implementation strategy

Deliver US1 as the smallest change, then validate US2 with the complete fixed
evaluation. Preserve negative results if the hypothesis fails. M2, embeddings,
LLM generation and threshold calibration remain out of scope.
