# Feature Specification: Optional hybrid retrieval

**Feature Branch**: `008-hybrid-ranking`

**Created**: 2026-10-20

**Status**: Implemented and verified; optional experiment with documented citation regressions

**Input**: Implement combined lexical and embeddings ranking on a new branch
to restore E09's missing request location.

## User Scenarios & Testing

### User Story 1 - Receive both parts of a supported answer (Priority: P1)

An employee asking where to request a replacement laptop and how long it takes
receives both the request location and the replacement deadline, with citations.

**Why this priority**: The present embeddings answer omits an actionable detail
even though the fixed evaluation reports PASS.

**Independent Test**: Ask E09 using the optional combined retrieval mode and
inspect the answer and cited source text for both facts.

**Acceptance Scenarios**:

1. **Given** the current handbook, **When** E09 is asked in combined mode,
   **Then** the answer includes IT portal, Hardware, and up to 5 business days
   after manager approval, with citations supporting both parts.
2. **Given** the synonymous notebook-computer question E05, **When** combined
   mode is used, **Then** the replacement deadline remains available.
3. **Given** equal relevance between candidates, **When** a question is repeated,
   **Then** selection and citations are deterministic.

### User Story 2 - Select the experiment without losing reliable refusal (Priority: P2)

A reviewer can select combined retrieval explicitly, reproduce earlier modes,
and receive a refusal when semantic evidence remains below its existing support
threshold.

**Why this priority**: A ranking position alone must not turn unrelated content
into an answer. Existing experiments must remain reproducible.

**Independent Test**: Run unsupported questions and compare unchanged single-mode
results with the saved baseline.

**Acceptance Scenarios**:

1. **Given** E10, E11, or E12, **When** combined mode is selected,
   **Then** the system refuses without citations.
2. **Given** the existing default mode, **When** no mode override is supplied,
   **Then** the earlier lexical behavior is preserved.
3. **Given** an empty question or no eligible sources, **When** queried,
   **Then** no answer or citations are invented.
4. **Given** unavailable optional model dependencies, **When** combined mode is
   selected, **Then** the existing actionable error is returned without silently
   switching retrieval mode.

### Edge Cases

- Superseded documents remain excluded before either ranking.
- A candidate appears in only one ranking, including queries without word overlap.
- No lexical matches exist but semantic evidence supports an answer.
- Combined ordering puts a weaker semantic match first: support confidence must
  remain distinct from rank, and must come from evidence actually selected.
- Invalid result limits or unsupported mode names fail clearly.
- Ties, fewer than two candidates, and repeated queries remain deterministic.

## Requirements

### Functional Requirements

- **FR-001**: Add an opt-in mode combining word matching with semantic ranking.
- **FR-002**: Select two cited chunks for E09 that together support both required
  facts, retaining the strongest semantic evidence and adding complementary
  evidence by combined relevance, without question-specific rules or source edits.
- **FR-003**: Preserve existing lexical and embeddings behavior, default mode,
  source filtering, model identity, and their established confidence thresholds.
- **FR-004**: Keep evidence confidence separate from combined rank, using the
  existing semantic threshold on the selected evidence to decide refusal.
- **FR-005**: Record the chosen mode and combination settings in saved runs, and
  expose the experiment through the existing command-line selection mechanism.
- **FR-006**: Preserve the fixed evaluation set and all metric calculation code.
  Supplement the fixed result with an explicit completeness inspection of E09.
- **FR-007**: Run locally with the existing cached optional model and dependencies.
- **FR-008**: Add offline automated checks for complementary evidence, ranking
  determinism, filtering, refusal boundaries, and mode selection.

### Key Entities

- **Candidate evidence**: a source chunk with its existing source identity,
  independent word-match and semantic relevance, and combined rank.
- **Answer evidence**: the selected chunks, their support confidence, and citations.
- **Experiment run**: mode, settings, unchanged evaluation fingerprint, metrics,
  and supplemental answer inspection.

## Success Criteria

### Measurable Outcomes

- **SC-001**: E09 includes all three literal details: `IT portal`, `Hardware`,
  and `5 business days`, with source support for location and deadline.
- **SC-002**: The complete fixed evaluation retains 12/12 with no PASS-to-FAIL
  regressions relative to the saved embeddings baseline.
- **SC-003**: The three fixed unsupported questions still refuse with no citations.
- **SC-004**: Existing lexical and embeddings per-question outcomes reproduce
  their baselines; all automated checks pass.
- **SC-005**: The report states every regression, remaining limitation, the known
  evaluation-set tuning limitation, and the separate E09 completeness result.

## Assumptions

- This is a separately measured optional experiment after the required M1 work.
- Baselines and two failures are captured in
  `docs/evidence/008-hybrid-ranking/baseline.md` before pipeline changes.
- The observed failure is ranking selection; source text already contains both
  facts. Combining complementary rankings is the sole intentional improvement.
- Expected effect: restore E09 completeness while retaining semantic paraphrase
  matching. It is a hypothesis until measured on the entire fixed set.
- Regression risks: lexical noise may displace useful semantic evidence, ranking
  can change secondary citations, and a fused rank is not evidence confidence.
- Verification uses the complete unchanged evaluation, comparison tool, existing
  mode reproduction, offline automated tests, and explicit CLI answer inspection.
- No new generation model, chunking change, stopword change, threshold tuning,
  corpus edit, or metric edit is included. Independent peer review is separate
  from Codex's implementation and checks.
