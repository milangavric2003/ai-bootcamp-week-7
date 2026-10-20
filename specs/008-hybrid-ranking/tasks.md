# Tasks: Optional hybrid retrieval

**Input**: [spec.md](spec.md), [plan.md](plan.md), research, data model, contract.
**Tests**: Required by FR-008; write behavior tests before implementation.

## Phase 1: Setup

- [X] T001 Create branch and save full baseline tests, embeddings/lexical runs, source hashes, and answer evidence in docs/evidence/008-hybrid-ranking/.
- [X] T002 Document E09/E07 failures in docs/evidence/008-hybrid-ranking/baseline.md and write specs/008-hybrid-ranking/spec.md before pipeline edits.

## Phase 2: Foundational design

- [X] T003 Complete research, plan, contract, quickstart, and quality checklist in specs/008-hybrid-ranking/; verify .gitignore covers existing Python/cache artifacts.

## Phase 3: US1 - Complete supported answers (P1)

**Goal**: Restore E09 location and deadline while retaining E05 semantic evidence.
**Independent test**: Actual handbook text with controlled scores contains both
E09 facts; E05's semantic leader survives misleading lexical evidence.

- [X] T004 [US1] Write and run failing offline ranking/completeness tests in tests/test_hybrid.py, covering full rankings, anchor retention, deterministic ties, component membership, source filtering, and score scales.
- [X] T005 [US1] Add hybrid scoring and semantic evidence fields in src/retrieval.py and the recorded RRF constant in src/config.py.

## Phase 4: US2 - Reproducible selection and refusal (P2)

**Goal**: Expose opt-in hybrid mode with unchanged semantic confidence threshold.
**Independent test**: Refusal boundaries, missing confidence, empty inputs,
dependency failure, and CLI selection are checked without model downloads.

- [X] T006 [US2] Write and run failing confidence and CLI contract tests in tests/test_hybrid.py.
- [X] T007 [US2] Adapt hybrid confidence in src/rag.py and backend selection/diagnostic output in src/cli.py; preserve earlier modes.

## Phase 5: Verification and reporting

- [X] T008 Run the complete project suite and save docs/evidence/008-hybrid-ranking/pytest-after.txt.
- [X] T009 Run full hybrid, embeddings, and lexical evaluations and comparisons with unchanged src/eval_runner.py and src/eval_compare.py; save fresh outputs in docs/evidence/008-hybrid-ranking/.
- [X] T010 Capture actual answers and CLI checks in docs/evidence/008-hybrid-ranking/; explicitly verify E09 completeness and record every changed secondary citation.
- [X] T011 Write docs/hybrid-report.md and update README.md with measured results, invocation, design choices, regressions, attribution, and remaining limits.
- [X] T012 Review source diff, verify protected hashes, save integrity/diff evidence in docs/evidence/008-hybrid-ranking/, and finish specs/008-hybrid-ranking/tasks.md.

## Dependencies and execution order

T001 -> T002 -> T003 -> T004 -> T005 -> T006 -> T007 -> T008.
T009 -> T010 -> T011 -> T012 after T008. Both stories depend on the design.
US1 is the ranking MVP; US2 completes refusal and CLI integration.

## Parallel opportunities

After implementation, independent embeddings and lexical reproduction runs can
execute together. US1 ranking and US2 CLI test cases can be reviewed independently,
but edits to their shared test file are sequential. No parallel implementation
agents are needed; the planning skill's research review is complete.

## Implementation strategy

Keep the strongest semantic evidence, fill remaining slots by equal-weight RRF,
verify each story with offline tests, then run the actual complete evaluation.
Document secondary citation regressions rather than adding another improvement.
All task entries use sequential IDs, story labels where applicable, and paths.
