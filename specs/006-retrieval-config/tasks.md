# Tasks: Verify the committed retrieval configuration

## Phase 1: Preserve and check

- [X] T001 Save starting hashes, parent configuration and original user result in docs/evidence/006-retrieval-config/.
- [X] T002 Run parent-settings and retained-default tests and preserve their logs in docs/evidence/006-retrieval-config/.

## Phase 2: User Story 1 - Measured starting point

- [X] T003 [US1] Implement the process-local measurement driver in docs/evidence/006-retrieval-config/run.py.
- [X] T004 [US1] Correct the stale comment in src/config.py and isolate any demonstrated default-dependent assumptions in existing tests/ files.
- [X] T005 [US1] Run all four configurations for both answer backends and save outputs in docs/evidence/006-retrieval-config/.
- [X] T006 [US1] Run combined and isolated comparisons with src.eval_compare and save outputs in docs/evidence/006-retrieval-config/.

## Phase 3: User Story 2 - Answer inspection

- [X] T007 [US2] Capture retained E09 and E05 using src.cli in docs/evidence/006-retrieval-config/.
- [X] T008 [US2] Inspect actual hosted answers and record source checks, models and regressions in docs/retrieval-config-report.md.

## Phase 4: Finish

- [X] T009 Verify protected-file hashes, result/trace alignment and final tests in docs/evidence/006-retrieval-config/.
- [X] T010 Review and amend the current config commit with only the selected src/, tests/, specs/ and docs/ artifacts.

## Current verification status

All four combinations were attempted for both backends. Seven full measurements
completed; the hosted top-k-only execution and its one recovery failed citation
validation at E09. Their failed traces are preserved, and two comparisons requiring
that missing full result are explicitly unavailable. This satisfies the spec's
operational-failure exception without inventing a score. Both hosted CLI checks
completed. All 163 tests and the integrity/rate audit pass; the peak rate was 22
requests in a rolling minute, below the user's approved 30/minute limit.
