# Feature Specification: Local semantic retrieval for grounded answers

**Feature Branch**: `feat/gemma-generation`

**Created**: 2026-10-21 (Europe/Belgrade)

**Status**: Specified before pipeline implementation

**Input**: Implement and test embeddings fresh on this branch without importing
code from other branches; live testing is authorized. Leave changes uncommitted
and provide a commit message. Preserve the user's selected three-chunk context
and stopword setting and the 30 hosted requests/minute limit.

## User Scenarios & Testing

### User Story 1 - Find evidence across different wording (Priority: P1)

A handbook reader can ask about a notebook computer and retrieve the equipment
replacement policy even though the document calls the device a laptop.

**Why this priority**: E05 currently misses the equipment source; an answerer
cannot ground an answer in information it never receives.

**Independent Test**: Select semantic retrieval for the unchanged corpus and inspect
the retrieved sources and actual answer for E05, including the replacement timeline.

**Acceptance Scenarios**:

1. **Given** different wording for the same equipment concept, **When** semantic
   retrieval is selected, **Then** measure whether the relevant policy and complete
   timeline enter the selected context and report the actual outcome.
2. **Given** a question asking both where and how long, **When** context is selected,
   **Then** inspect support for both parts and report any missing source or qualifier.
3. **Given** matching scores, **When** retrieval repeats, **Then** sources have a
   stable order and retain their original citation identity.

### User Story 2 - Preserve grounding and reproducibility (Priority: P2)

The experiment owner can compare lexical and semantic retrieval with all other
choices fixed, and continue using the existing offline lexical mode.

**Why this priority**: A useful semantic match is not proof that the evidence
supports the requested policy; a fair comparison must preserve answer rules.

**Independent Test**: Run the complete evaluation in both modes and confirm lexical
reproduction, unchanged evaluation identity and actual refusals for unsupported cases.

**Acceptance Scenarios**:

1. **Given** lexical selection, **When** the program runs, **Then** existing results
   reproduce without loading an embedding model or making an embedding request.
2. **Given** semantic selection, **When** passages are ranked, **Then** original
   source text is encoded locally and only eligible current sources are returned.
3. **Given** no relevant policy, **When** related material is retrieved, **Then**
   the existing grounding and refusal policy applies, with wrong answers or
   refusals preserved as measured failures rather than hidden by threshold tuning.
4. **Given** missing dependencies or model data, **When** semantic retrieval starts,
   **Then** an actionable operational error identifies the setup step; it is not
   replaced with a successful refusal or silent lexical fallback.

### User Story 3 - Run a small local experiment (Priority: P3)

The contributor can prepare the selected model once and run local retrieval
without a vector database or an embedding API, then review the measured change.

**Why this priority**: The small corpus does not justify additional infrastructure.

**Independent Test**: Prepare the pinned model, run retrieval without network
access and inspect the saved configuration, test outputs and before/after report.

**Acceptance Scenarios**:

1. **Given** a prepared model, **When** retrieval runs offline, **Then** it reuses
   local model data and the corpus representation within the process.
2. **Given** changed corpus text or model identity, **When** retrieval next runs,
   **Then** previous representations are not silently attached to different text.
3. **Given** completed checks, **When** the user returns, **Then** source changes,
   evidence, setup instructions and suggested commit message are ready for review,
   with no commit, push or imported implementation from another branch.

### Edge Cases

- Empty queries and no eligible sources return no results without loading a model.
- Punctuation-only input contains no searchable content and returns no results.
- Stopword filtering remains a lexical choice; semantic input retains original text.
- Negative cosine scores, ties and fewer eligible chunks than requested are valid.
- Invalid, zero-norm, non-finite or mismatched vectors cause an explicit error.
- Reordered chunks or changed metadata must not return stale citations.
- Unknown backend selections fail clearly; a missing model does not trigger downloads
  during normal answering. Initial preparation is a separate explicit action.
- A hosted failure remains an operational failure and does not count as a correct refusal.

## Requirements

### Functional Requirements

- **FR-001**: Add one selectable semantic retrieval backend, implemented fresh.
  Keep lexical retrieval as the default and preserve its existing behavior.
- **FR-002**: Keep context size three, lexical stopword filtering enabled, minimum
  score 0.01 and refusal threshold 0.10; do not add or calibrate a separate threshold.
- **FR-003**: Rank complete original chunk/query text by local normalized semantic
  similarity, keeping the current source filter, stable citation IDs and tie order.
- **FR-004**: Keep the corpus, chunk boundaries, generation prompt, citation validator,
  model retry policy, evaluation questions and metric calculations unchanged.
- **FR-005**: Record model identity/revision, retrieval selection and relevant setup
  choices in the existing evaluation snapshot; encode both query and corpus with
  the same fixed model and revision.
- **FR-006**: Reuse the model and unchanged corpus representation within a process,
  with bounded caching and invalidation on text/model changes; attach fresh metadata.
- **FR-007**: Provide explicit setup, backend-selection and error instructions; keep
  model loading lazy so lexical use does not require embedding dependencies.
- **FR-008**: Test ranking, filtering, cache invalidation, errors, score boundaries,
  selection and passage delivery to the existing generator with controlled offline
  inputs; also run the real local model and complete live before/after evaluation.
- **FR-009**: Retain raw failed executions, every regression and at least one
  limitation. Do not promise 12/12 or substitute a test assertion for measurement.
- **FR-010**: Keep source changes and evidence uncommitted; exclude caches,
  credentials and reference directories from the suggested commit scope.

### Key Entities

- **Embedding identity**: Fixed model, revision, execution device and local location.
- **Corpus representation**: Original chunk texts and normalized vectors; tied to
  embedding identity and text, not permanently bound to citation metadata.
- **Retrieval result**: Existing chunk and finite cosine similarity, ordered by
  descending similarity and then source ID.
- **Measurement**: Fixed twelve-question results, settings, fingerprint and actual
  generated text/citations/refusals with actual answering model.

## Success Criteria

### Measurable Outcomes

- **SC-001**: All existing tests continue to pass; meaningful new semantic tests pass
  without network/model downloads, with lexical results reproduced exactly.
- **SC-002**: Complete before/after evaluations preserve the same twelve questions
  and fingerprint; interrupted operations are reported explicitly without a score.
- **SC-003**: E05's relevant source retrieval and grounded timeline are measured and
  inspected; all changed answers, regressions and unsupported cases are reported.
- **SC-004**: Prepared retrieval works without network access, and repeated queries
  do not re-encode an unchanged corpus within one process.
- **SC-005**: Actual live request starts stay below 30 in every rolling minute.
- **SC-006**: The user receives reviewable uncommitted files, reproduction commands
  and a commit message; no cache or credential appears in proposed source changes.

## Assumptions

- This is optional advanced work expressly requested after the separately measured
  M1 homework and later experiments; it does not replace their historical evidence.
- Before implementation the unchanged pipeline passed 163 tests and its offline
  evaluation reproduced 9/12. E05 and E01 are documented by ID in
  `docs/evidence/007-semantic-retrieval/baseline.md`; E11 also fails offline.
  Gemma already addresses E01/E11 and historically scores 11/12, with E05 open.
- The same numeric thresholds have different meanings for cosine and lexical
  scores. Preserving them isolates the backend change, not optimal calibration;
  unsupported-query regressions must remain visible. No threshold from main is reused.
- Downloading public model weights is setup; corpus/query embeddings are computed
  locally. Live authorization applies to existing hosted answering over sample text.
- The implementation will not inspect or import code from other branches/projects.
  Public model weights and official API documentation are independent resources.
