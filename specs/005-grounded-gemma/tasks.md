# Tasks: Grounded Gemma answering

**Input**: `specs/005-grounded-gemma/` design artifacts.
**Branch**: `feat/gemma-generation`. Implementation authorized 2026-10-20.
**Tests**: Mocked provider, output validation and offline regression checks are
required by the specification. Live quality evidence requires the later key.

## Phase 1: Setup

- [X] T001 Save unchanged tests/eval, source hashes and E05/E11 CLI evidence in docs/evidence/005-gemma/; document two failures in docs/evidence/005-gemma/baseline.md before runtime edits.
- [X] T002 Add secret-file ignore rules in .gitignore, promote .env.example and pin/install python-dotenv in requirements.txt.

## Phase 2: Foundational

- [X] T003 Write configuration and environment-precedence tests in tests/test_generation_config.py before configuration implementation.
- [X] T004 Add nonsecret settings and root environment loading in src/config.py, a frozen prompt in src/generation_prompt.py and operational error types in src/generation_errors.py; keep the API key outside snapshots.

## Phase 3: US1 - Answer from evidence (P1)

**Independent test**: Mock a Google response for synthetic evidence and verify all
returned chunks enter the request, with only supporting IDs in the final answer.

- [X] T005 [P] [US1] Write HTTP request/response tests in tests/test_gemma_client.py, including metadata/order, timeout, complete candidate and non-thinking text handling.
- [X] T006 [P] [US1] Write decision tests in tests/test_generation.py: answer is a nonempty string; citations are an array of supplied string IDs; refused is a strict boolean; duplicates normalize in first-occurrence order.
- [X] T007 [US1] Implement one-request Google REST transport in src/gemma_client.py with explicit header authentication, bounded input/output and no fallback/retry.
- [X] T008 [US1] Implement grounded prompt serialization and strict decision parsing in src/generation.py; preserve existing retrieved results in src/rag.py.

## Phase 4: US2 - Refuse without support (P1)

**Independent test**: A mocked valid refusal becomes the existing refusal text,
empty citations and refused=True; malformed/provider errors never become refusals.

- [X] T009 [P] [US2] Add malformed JSON/types/IDs, empty/contradictory decisions and inline citation tests in tests/test_generation.py.
- [X] T010 [P] [US2] Add quota/authentication/network/blocked/truncated-output tests in tests/test_gemma_client.py, asserting sanitized errors and one attempt.
- [X] T011 [US2] Implement validation/error paths in src/generation.py and src/gemma_client.py; valid refusal answer text must be empty and citations must be empty.

## Phase 5: US3 - Optional and separate (P2)

**Independent test**: Default mode needs no key/network; enabled mode validates
before retrieval, and an operational error stops the unchanged evaluator.

- [X] T012 [US3] Write integration/trace tests in tests/test_generation.py and tests/test_generation_config.py for offline mode, score-gate skip, missing key, CLI errors and failed evaluation without a result file.
- [X] T013 [US3] Wire backend selection and trace records into src/rag.py and src/generation.py, preserving extraction/retrieval settings and RagAnswer; format operational errors in src/cli.py.
- [X] T014 [US3] Run full pytest and a new disabled-mode evaluation in docs/evidence/005-gemma/; use src.eval_compare and verify every retrieval/metric row matches the unchanged baseline.

## Phase 6: Documentation and live validation

- [X] T015 Update README.md, docs/advanced-plan.md, docs/gemma-report.md and specs/005-grounded-gemma/quickstart.md with implemented setup, actual verification and remaining limitations.
- [X] T016 Verify hashes/diff/secret ignores and save implementation evidence in docs/evidence/005-gemma/; leave eval/eval_set.json, metric code, retrieval, M2 and reference directories unchanged.
- [ ] T017 Once the local key exists, run non-eval live capability checks, freeze prompt/settings and save actual responses in docs/evidence/005-gemma/live/.
- [ ] T018 Run full fixed lexical extraction-versus-Gemma comparison with same-run traces; manually review all 12 generated answers and a CLI changed case in docs/gemma-report.md.
- [ ] T019 After Vedran's frozen embedding result is integrated separately, run extraction-versus-Gemma with that exact retrieval configuration and record the separate comparison in docs/gemma-report.md.

## Dependencies and execution order

T001 precedes all runtime edits. T002-T004 provide the shared foundation.
US1 and US2 share parsing/transport files, so execute their implementation edits
sequentially. US3 integration depends on those components. T014-T016 validate the
local implementation; T017-T018 require credentials. T019 additionally requires
Vedran's measured retrieval work. Those external prerequisites must remain visible
as incomplete tasks, not substituted with mock-based quality claims.

## Parallel examples

- US1: T005 and T006 can be written independently after the foundation.
- US2: T009 and T010 touch separate test files.
- US3: environment tests and integration tests can be checked independently after
  T013; shared runtime edits stay sequential.

These are scheduling opportunities, not a request to spawn agents. This run uses
one implementing agent.

## Implementation strategy

Capture baseline, write meaningful failing tests, implement the minimal optional
answerer, then run the complete suite and prove disabled-mode equivalence. Finish
all key-independent work now. Document missing live/embedding evidence honestly;
do not count mocks as a measured RAG quality improvement.

## Execution status (2026-10-20)

T001-T016 are complete. The suite passes 127/127; the disabled backend reproduces
all 12 original evaluation rows and 10/12 overall, with 35 protected baseline files
unchanged. See `docs/gemma-report.md` and `docs/evidence/005-gemma/verification.json`.

T017-T018 await the local Google API key. T019 additionally awaits Vedran's frozen
embedding result. No live model quality, peer review or submission is claimed.
No Spec Kit extension hooks or feature checklists were present; the shared active
feature metadata was not changed.
