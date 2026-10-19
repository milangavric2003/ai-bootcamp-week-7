# Feature Specification: Current-version evidence (M5)

**Feature Branch**: `main`, per the user's explicit implementation instruction.
**Created**: 2026-10-19
**Status**: Implemented and measured on 2026-10-19; 43 tests pass, 10/12 without regressions.
**Input**: Plan advanced work from M1+M3, choosing changes by observed failures.

Results: [M5 report](../../docs/m5-report.md). The original hypothesis and
acceptance criteria below remain the preimplementation specification.

## User Scenarios & Testing

### User Story 1 - Answer from current policy (Priority: P1)

An employee asking about remote work receives the current three-day policy
without the contradictory superseded two-day policy.

**Why this priority**: E06 currently passes automatically while giving both rules.
**Independent Test**: Inspect E06's complete answer, retrieved evidence and citations.

**Acceptance Scenarios**:

1. Given current and superseded remote-work policies, when E06 is asked with
   current-only filtering enabled, then the answer cites the current policy,
   contains `3 days per week`, and neither retrieves nor cites superseded evidence.
2. Given filtering is disabled, when the same question is asked, then the
   existing M1+M3 behavior is preserved.

### User Story 2 - Assess the change honestly (Priority: P2)

The pair can attribute measured effects to this one decision and retain the
original required experiment as the submission record.

**Independent Test**: Review the before/after results, comparison, diff and report.

**Acceptance Scenarios**:

1. Given a saved 10/12 M1+M3 result, when M5 is measured, then all twelve
   questions are rerun with the same questions and metric definitions.
2. Given E05 and E11 remain unresolved, when results are reported, then those
   failures remain explicit rather than being represented as fixed by M5.

### Edge Cases

- No eligible evidence remains: the system follows its existing refusal rule.
- Fewer eligible chunks than requested: return the available eligible evidence.
- Historical questions lose access to superseded rules; document this scope limit.
- Passing E06 alone is insufficient: its answer and citations must be inspected.

## Requirements

### Functional Requirements

- **FR-001**: When enabled, the filter MUST exclude every superseded source before
  evidence is ranked and selected. It MUST retain all other existing candidates.
- **FR-002**: When disabled, existing retrieval behavior MUST remain unchanged.
- **FR-003**: The experiment MUST change only current-version eligibility; other
  retrieval, refusal, citation and chunking decisions MUST remain fixed.
- **FR-004**: The pair MUST save full before/after results, comparison, tests,
  implementation diff and a manual E06 check without overwriting M1/M3 evidence.
- **FR-005**: The report MUST list every regression and remaining limitation.
  A negative result is reportable; retaining the change requires no lost passes.

### Key Entities

- **Policy source**: identity, version and current/superseded status.
- **Evidence chunk**: text and source identity, carrying that source's status.
- **Experiment record**: parent measurement, hypothesis, results and decision.

## Success Criteria

### Measurable Outcomes

- **SC-001**: E06 cites the current three-day rule with zero superseded citations
  and zero superseded retrieved chunks.
- **SC-002**: All ten existing passing questions remain passing on the unchanged
  twelve-question set; no improvement in pass count is promised.
- **SC-003**: Every changed outcome and known limitation is explained in the report.
- **SC-004**: Another reviewer can reproduce the comparison and inspect E06.

## Assumptions

- The merged M1+M3 state (10/12) is the starting point.
- All further optional work this week depends on available time. The user
  subsequently requested M5 implementation now on main, without a new branch.
  LLM generation is a separate possible later experiment.
- Existing source statuses are authoritative; this does not infer version dates.
- M5 does not address synonyms or distinguish parental leave from annual leave.
- This is optional work, separate from the required M1 experiment. The assignment
  places optional implementation after submission of the minimum; submission is
  still unconfirmed. The user explicitly authorized implementation now; retain
  that timing caveat rather than claiming the minimum was submitted.
