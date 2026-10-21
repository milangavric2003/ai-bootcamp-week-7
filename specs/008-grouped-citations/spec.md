# Feature Specification: Accept validated grouped inline citations

**Feature Branch**: `feat/gemma-generation`
**Created**: 2026-10-21
**Status**: Specified before implementation
**Input**: Fix the citation validation crash so the current embeddings pipeline
completes evaluation. Report the measured score; do not add hybrid retrieval.

## User Scenarios & Testing

### User Story 1 - Read an answer citing multiple supplied sources (Priority: P1)

A reader receives an answer when the model groups two valid source IDs in one
inline citation rather than formatting them as separate bracket pairs.

**Why this priority**: E09 retrieves complete evidence but evaluation crashes on
`[hb-01-chunk-1, hb-01-chunk-2]`, despite both IDs being selected and supplied.

**Independent Test**: Replay the preserved actual model decision through the
parser, checking it yields the same facts and individually formatted citations.

**Acceptance Scenarios**:

1. **Given** selected, supplied source IDs in a comma-separated inline group,
   **When** the answer is parsed, **Then** validate each ID and normalize the group
   into individual inline citations without changing factual prose.
2. **Given** unknown or unselected IDs in any group, **When** parsing runs,
   **Then** reject the decision rather than removing or guessing identifiers.
3. **Given** empty, nested, unbalanced or malformed brackets, **When** parsing runs,
   **Then** report an invalid response rather than ignoring unvalidated text.

### User Story 2 - Complete the unchanged embeddings evaluation (Priority: P2)

The experiment owner can run all twelve questions on the implemented embeddings
backend and see the actual results, even if some quality checks still fail.

**Independent Test**: Run the full semantic Gemma evaluation and original lexical
control, inspect E09 and unsupported answers, and preserve all failures.

**Acceptance Scenarios**:

1. **Given** the existing embeddings backend and frozen settings, **When** the
   complete evaluation runs, **Then** save all twelve outcomes and actual answers.
2. **Given** normal single inline citations or no inline citations, **When** the
   parser runs, **Then** keep previously valid behavior and grounding checks.
3. **Given** failed quality questions, **When** reporting, **Then** state the
   observed score without adding hybrid retrieval, threshold tuning or prompt edits.

### Edge Cases

- Whitespace between IDs, repeated IDs and several groups in one answer.
- Empty comma elements, unsupported separators, newlines and nested brackets.
- Valid IDs in the supplied evidence but absent from the selected citations array.
- Unknown IDs in the citations array even if the inline marker looks valid.
- A refusal still requires empty answer text and citations.

## Requirements

### Functional Requirements

- **FR-001**: Accept comma-separated groups only when every member is a selected,
  supplied ID; normalize to individual bracketed markers in the same order.
- **FR-002**: Preserve actual source identifiers, citation-array validation, strict
  JSON/schema checks, nonempty-answer rules and refusal invariants.
- **FR-003**: Reject malformed or unvalidated brackets; do not drop bad members,
  invent source IDs, or fall back to an answer from invalid output.
- **FR-004**: Keep retrieval, existing settings, model, prompt, retries, corpus,
  fixed evaluation and metric code unchanged. No hybrid implementation.
- **FR-005**: Add focused offline regression tests, replay the captured E09
  decision, run the full suite, full live evaluation and independent E09 CLI check.
- **FR-006**: Record this authorized compatibility fix separately from the earlier
  embeddings experiment, preserving its original failed executions and measurements.
- **FR-007**: Leave all changes uncommitted and unstaged, with a commit message and
  source/evidence paths ready for the user; keep credentials/caches excluded.

### Key Entities

- **Inline group**: One or more comma-separated selected source IDs in balanced
  square brackets; normalized into individual markers, with duplicate members removed.
- **Selected source set**: Valid citations already confirmed to have been supplied
  as evidence; each inline member must belong to this set.

## Success Criteria

- **SC-001**: The captured E09 response parses and preserves the original source IDs
  and all factual prose while yielding separate inline markers.
- **SC-002**: Unknown/unselected sources and malformed brackets still fail focused
  tests; the full existing suite passes.
- **SC-003**: The fixed twelve-question embeddings evaluation completes, with its
  real score, answer/source review and unchanged fingerprint saved as evidence.
- **SC-004**: Hosted testing stays below 30 requests in every rolling minute.

## Assumptions and observed baseline failures

The user explicitly authorizes this next fix after the embeddings experiment.
E09 is the targeted operational failure, reproduced in the user's command and two
earlier full semantic executions; the actual raw response is preserved under
`docs/evidence/007-semantic-retrieval/e09-raw-decision.json`. No complete semantic
Gemma baseline score exists and none is invented.

Two other concrete existing offline failures, E07 (irrelevant remote-work citations,
precision 0.3333) and E10 (stock-price question answered from unrelated policies),
are preserved in the preceding complete semantic offline result. They are not
targets of this parser fix and are not claimed as two parser failures. Prior
required homework remains separate; this is an explicitly requested optional fix.
