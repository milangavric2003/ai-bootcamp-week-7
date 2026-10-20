# Feature Specification: Verify the retained retrieval configuration

**Feature Branch**: `feat/gemma-generation`

**Created**: 2026-10-21 (Europe/Belgrade)

**Status**: Verified retrospective follow-up; one hosted intermediate mode has a documented operational failure

**Input**: The user committed a three-chunk context limit and enabled stopword
filtering, then requested testing, evidence and amendment of that commit before
starting a fresh embeddings implementation.

## User Scenarios & Testing

### User Story 1 - Establish a measured starting point (Priority: P1)

The experiment owner needs a reproducible record of the previous and retained
settings, so a later embeddings experiment has an honest starting point.

**Why this priority**: A good score on known questions alone does not show which
setting helped, whether information was lost, or whether a later change helps.

**Independent Test**: Evaluate the same twelve questions with both settings
individually and together, preserving actual results and generated answers.

**Acceptance Scenarios**:

1. **Given** the previous two-chunk configuration without stopword filtering,
   **When** it is reconstructed, **Then** only those two choices differ from the
   retained three-chunk configuration with filtering.
2. **Given** each of the four combinations, **When** the complete evaluation runs,
   **Then** its settings, results, citations and any failures remain reviewable.
3. **Given** any unchanged pass count, **When** evidence is reviewed, **Then** the
   report describes changed context and limitations without claiming improvement
   from the pass count alone.

### User Story 2 - Preserve supported facts and honest refusals (Priority: P2)

Handbook readers need the request route and deadline together for equipment
replacement, and a refusal when retrieved material does not support an answer.

**Why this priority**: Selecting related passages can still omit a required fact.

**Independent Test**: Inspect actual answers and sources for E05, E09 and E11,
plus the current remote-work policy and supported facts in all answered cases.

**Acceptance Scenarios**:

1. **Given** the retained settings, **When** E09 is answered, **Then** inspect both
   the IT portal / Hardware route and up to five business days after manager
   approval against their cited sources; report any omission.
2. **Given** E05's notebook-computer wording, **When** the equipment source is
   absent from retrieved evidence, **Then** record the retrieval miss rather than
   claiming that the underlying corpus lacks an answer.
3. **Given** annual-leave passages for E11's parental-leave question, **When** the
   answer is reviewed, **Then** record whether the system correctly refuses.

### Edge Cases

- Filtering can remove the acronym IT after lowercasing; the vocabulary is fixed.
- An all-stopword question can retrieve nothing and should refuse.
- Three results can introduce irrelevant context or dilute extractive citations.
- Model retries or fallback can change the actual answering model; retain traces.
- Provider errors are operational failures, not correct evidence refusals.

## Requirements

### Functional Requirements

- **FR-001**: Retain the user's three-chunk limit and enabled filtering; change no
  scoring rule, stopword list, corpus, chunk boundary, threshold or grounding rule.
- **FR-002**: Preserve the unchanged preceding configuration and user's saved run.
- **FR-003**: Measure all four combinations with the existing offline answerer and
  the existing opted-in hosted answerer; preserve complete question sets and traces.
- **FR-004**: Compare the combined change and isolated setting changes, retaining
  the warning that two settings changed in the combined comparison.
- **FR-005**: Keep evaluation questions and metric calculations unchanged.
- **FR-006**: Run the existing tests, fixing only any assumptions about configurable
  defaults; do not add tests that merely assert constant values.
- **FR-007**: Record all regressions, remaining limitations and actual answer review.
- **FR-008**: Amend the user-authorized current commit with explicitly selected
  files, excluding caches, credentials, reference folders and embeddings work.

### Key Entities

- **Configuration combination**: Context limit of two or three, with filtering off
  or on; all other experimental settings fixed within each answering mode.
- **Measurement**: Twelve question outcomes, settings and evaluation fingerprint.
- **Answer evidence**: Actual text, selected source IDs, refusal, model and attempts.

## Success Criteria

### Measurable Outcomes

- **SC-001**: All existing tests pass under the retained defaults after any needed
  isolation of test-specific settings; all initial failures are documented.
- **SC-002**: All eight complete measurements have the same evaluation fingerprint,
  or an operational blocker is explicitly reported without inventing a score.
- **SC-003**: Every newly failing question and every observed answer omission is
  listed; all generated supported answers are inspected against their sources.
- **SC-004**: A reviewer can distinguish the effects of each setting from the
  combined result and locate the exact retained starting configuration.

## Assumptions

- This specification follows user commit `f108726`; it did not precede that change.
  It governs this verification work and any further edits only.
- The required M1 homework remains a separate historical experiment. This optional
  follow-up contains two settings and is not presented as one required change.
- Historical failures: E05 misses the laptop source; the earlier M2 experiment
  loses E09's deadline with filtering on and a two-chunk limit. They are documented
  in `docs/m2-report.md`. They are not two failures of the preceding Gemma run,
  which already scored 11/12 with E05 as its only failing evaluation question.
- The user's known-evaluation tuning is exploratory; no held-out accuracy claim is
  made and no setting will be selected in response to these new measurements.
- Existing local hosted-answer credentials and retry/fallback policy are reused.
  There is no new infrastructure or embedding work in this step.
