# Tasks: Grouped inline citations

## Baseline and contracts

- [X] T001 Save current source/evidence hashes and unchanged tests/offline measurement in docs/evidence/008-grouped-citations/.
- [X] T002 [US1] Add the grouped/malformed/unknown-ID regression cases in tests/test_generation.py and preserve their initial failures in docs/evidence/008-grouped-citations/.

## Implementation

- [X] T003 [US1] Validate and normalize selected source groups in src/generation.py while preserving all other grounding and JSON checks.
- [X] T004 [US1] Run the full suite and captured-decision replay, saving actual outputs in docs/evidence/008-grouped-citations/.

## End-to-end validation and handoff

- [X] T005 [US2] Run full semantic Gemma evaluation, lexical/offline controls, comparator and E09 CLI in docs/evidence/008-grouped-citations/.
- [X] T006 [US2] Review actual answers and document the measured result and remaining limitations in docs/grouped-citations-report.md; update README.md and the current handoff.
- [X] T007 Audit protected files, unchanged settings and request pacing in docs/evidence/008-grouped-citations/; leave work uncommitted with an updated commit message.

Dependencies: T001 -> T002 -> T003 -> T004 -> T005 -> T006 -> T007.
