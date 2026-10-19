# Feature Specification: M2 stopword filtering

**Feature Branch**: `main` (explicit user instruction; no feature branch)

**Created**: 2026-10-19

**Status**: Specified before implementation

**Input**: Update the agreed plan, implement and measure M2 on main even if no
evaluation failures are fixed, then hand off for human review. The user will
implement embeddings afterward. Grounded LLM answering is a separate later step.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Search using informative words (Priority: P1)

As a handbook user, I want common grammatical words to stop creating irrelevant
matches while meaningful words, quantities and qualifiers remain searchable.

**Why this priority**: Common-word overlap currently supplies irrelevant evidence.

**Independent Test**: A generic query and unrelated passage sharing only common
words have no match with filtering enabled; a meaningful shared term still matches.

**Acceptance Scenarios**:

1. **Given** filtering is enabled, **When** query and evidence are compared,
   **Then** the same fixed list is excluded on both sides, ignoring letter case.
2. **Given** filtering is disabled, **When** existing questions are evaluated,
   **Then** the complete saved baseline is reproduced except run creation time.
3. **Given** an input containing only excluded words, **When** it is searched,
   **Then** the system safely returns no matching evidence and refuses.

### User Story 2 - Review one measured experiment (Priority: P2)

As a reviewer, I want the before/after evidence and every regression so I can
decide whether to retain M2 before moving to embeddings.

**Why this priority**: A controlled result matters even when no failing case passes.

**Independent Test**: Compare all 12 unchanged evaluation questions and inspect
changed citations and refusal decisions against the saved baseline.

**Acceptance Scenarios**:

1. **Given** the saved unchanged baseline, **When** M2 is measured, **Then** only
   stopword filtering changes and the report lists fixes, regressions and limitations.
2. **Given** the completed evidence, **When** work is handed off, **Then** human
   review remains pending and embeddings/LLM work has not started.

### Edge Cases

- Empty text, punctuation-only text, or text reduced to no words must be safe.
- Content-word order and repeated meaningful words must be retained.
- Numbers and negative or temporal qualifiers such as `not`, `never`, `until`
  must remain available; stopword filtering is not semantic matching.
- Scores may increase or decrease; an unchanged threshold may cause regressions.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Apply one fixed general English stopword list to query and passage
  words when the existing filtering option is enabled; preserve disabled behaviour.
- **FR-002**: Freeze the list before implementation and measurement; do not tailor
  it to individual questions or edit it after observing the experiment's result.
- **FR-003**: Preserve meaningful word order, repetitions, numbers and qualifiers
  outside the list. Empty filtered input must yield no evidence rather than an error.
- **FR-004**: Change no other retrieval, chunking, version, citation or refusal
  behaviour; introduce no synonym mapping, model, service or dependency.
- **FR-005**: Preserve the complete evaluation set, metric calculations, prior
  evidence, original starter and Week 6 reference material.
- **FR-006**: Verify filtering with focused automated tests for both modes, empty
  inputs, false matches and meaningful matches; run the full existing test suite.
- **FR-007**: Save and compare both full evaluation runs, inspect changed answers,
  record every regression and leave human review explicitly pending.

### Key Entities

- **Stopword list**: The fixed common words excluded in this experiment.
- **Evidence run**: All 12 evaluation outcomes, configuration and evaluation fingerprint.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The agreed common-word-only match disappears in a focused check,
  while meaningful matches and qualifiers are retained.
- **SC-002**: Disabling filtering reproduces all 12 baseline outcomes, scores,
  citations, aggregate metrics and configuration except run creation time.
- **SC-003**: All automated checks pass and all 12 questions have saved before/after
  measurements with matching fingerprints; every regression is reported.
- **SC-004**: A reviewer receives a retain/reject recommendation, known limitations
  and the agreed next-step ownership. No minimum pass-count gain is required.

## Assumptions

- The starting state is retained M1+M3+M5: 43 tests, 10/12 eval passes.
- The observed failures and expected/actual evidence are in
  [baseline.md](../../docs/evidence/004-m2/baseline.md): E05 lacks semantic matching;
  E11 mistakes related leave text for sufficient evidence.
- Hypothesis: filtering reduces common-word noise and may improve citation
  precision. Neither E05 nor E11 is expected to be reliably fixed by this change.
- Risk: changed word counts alter scores and may affect valid answers, refusal,
  and supporting citations. Threshold recalibration is a separate experiment.
- M2 is additional work requested now despite unconfirmed minimum submission;
  human review follows M2, then the user implements embeddings.
