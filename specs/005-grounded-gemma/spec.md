# Feature Specification: Grounded Gemma answering

**Created**: 2026-10-19

**Status**: Live-verified on 2026-10-20: 11/12, E11 fixed; E05 and embedding integration pending

**Feature branch**: `feat/gemma-generation`

**Input**: Keep M2 disabled. Vedran owns embedding retrieval. Plan a separate
Google AI Studio / Gemini API integration for Gemma 4 26B; provide an environment
template now, with the real key supplied later.

## User Scenarios & Testing

### User Story 1 - Answer from retrieved evidence (Priority: P1)

As a handbook reader, I receive a readable answer supported by the retrieved
handbook passages, with citations I can inspect.

**Independent test**: Supply a question and known retrieved passages to the
answering component using a mocked provider response, without an embedding model.

**Acceptance scenarios**:

1. Given sufficient evidence, generation receives the question and every returned
   top-k passage, including its ID and metadata. The result answers the question
   and cites only passages actually supplied.
2. Given a question with several parts, the answer covers supported parts and
   identifies missing evidence for any unsupported part.
3. Given an unrelated passage among the retrieved results, it can be supplied as
   context without being cited in the final answer.

### User Story 2 - Refuse when evidence is insufficient (Priority: P1)

As a reader, I am told when the supplied evidence does not support my question.

**Independent test**: Ask about parental leave with only annual-leave evidence;
the expected grounded result is a refusal with no citations.

**Acceptance scenarios**:

1. Given no retrieved evidence or failure of the existing retrieval score gate,
   the existing refusal occurs without a generation request.
2. Given evidence about a different policy, the model is instructed to refuse,
   and a valid model refusal becomes `refused=True`, with no citations.
3. Given an unknown citation ID, malformed response, empty answer or contradictory
   refusal fields, the system reports an invalid generation result and does not
   display it as a successful grounded answer.

### User Story 3 - Keep optional generation separate (Priority: P2)

As a contributor, I can run the existing offline system and tests without a key,
then explicitly select Gemma for a separate experiment.

**Acceptance scenarios**:

1. With generation disabled, the existing answer behavior and M2-disabled setting
   are retained, and no provider request is made.
2. With generation enabled and no key, configuration fails clearly before an
   evaluation starts. Keys do not appear in saved configuration or logs.
3. An unavailable service is reported as an execution failure, distinguishable
   from a genuine evidence-based refusal; evaluation must not count it as correct.

### Edge cases

- Fewer than k passages: send all available passages; never fabricate padding.
- Context exceeds the chosen input budget: fail explicitly rather than silently
  dropping passages or changing top-k during the experiment.
- Source text contains instructions: treat source content as evidence, not commands.
- Unknown, duplicate or fabricated citation IDs: reject unknown IDs and normalize
  repeated valid IDs; verify support manually as ID validity alone is insufficient.
- Timeout, authentication error, quota exhaustion, blocked/truncated output or an
  unsupported model: fail visibly; no automatic model change or extractive fallback.

## Requirements

### Functional requirements

- **FR-001**: The only experimental intent is replacing the existing extractive
  answering policy with grounded generation and evidence-based refusal.
- **FR-002**: Consume the existing retrieved-result structure after retrieval;
  embedding vectors themselves are not generation input.
- **FR-003**: Supply question, chunk text, chunk ID, document ID, title, version
  and status for all passages returned by retrieval, in returned order.
- **FR-004**: Require answers grounded only in supplied passages and citations
  limited to the subset used for the answer. Insufficient evidence requires refusal.
- **FR-005**: Validate the response before returning the existing `RagAnswer` type.
  Keep retrieved results intact for the CLI and fixed evaluator.
- **FR-006**: Keep generation opt-in; use the confirmed Google provider and a
  configurable Gemma model ID. Provide a placeholder environment template.
- **FR-007**: Load the real key privately, exclude it from configuration snapshots
  and errors, and ignore the local secret file before users create it.
- **FR-008**: Keep M2 disabled. Do not implement or tune embeddings, chunking,
  current-version filtering, top-k, retrieval thresholds or evaluation metrics.
- **FR-009**: Preserve existing experiment artifacts. Measure generation against
  the same frozen retrieval configuration before and after the answering change.
- **FR-010**: Save generated answer text and execution metadata separately because
  the existing evaluation JSON does not include answer text.

### Key entities

- **Retrieved evidence**: Ordered scored chunks, with text and source metadata.
- **Generation request**: Question, supplied evidence, fixed prompt and settings.
- **Generation decision**: Answer or evidence refusal, text and selected chunk IDs.
- **Execution record**: Provider/model, prompt fingerprint, generation settings,
  request outcome, latency, token usage if returned, answer and citations; no key.

## Observed failure and experiment hypothesis

The retained current baseline is saved at
`docs/evidence/004-m2/retained.json`: 10/12, M2 disabled. The historical failures
below are documented in `docs/evidence/004-m2/baseline.md`; this design does not
claim to have rerun the evaluation or inspected a future embedding baseline.

| ID | Expected | Recorded actual | Failure type |
| --- | --- | --- | --- |
| E05 | Equipment replacement, citing `5 business days` | Onboarding and annual-leave chunks; expected equipment evidence not retrieved | Retrieval vocabulary mismatch |
| E11 | Refuse the parental-leave question | Answers using annual-leave chunks | Unsupported answering |

**Hypothesis**: With retrieval held fixed, a grounded model can recognize that
annual-leave evidence does not establish parental-leave policy, improving E11,
and produce useful answers with selective citations on supported questions.

**Expected effect**: Better answerability decisions and clearer supported answers;
not a promised pass count. E05 remains retrieval's responsibility when its evidence
is missing. If embeddings already fix E11, document that and measure other quality
effects without changing the hypothesis to fit outcomes.

**Regression risk**: Invented facts, incomplete answers, misplaced citations,
unnecessary refusal, nondeterminism, remote service failures and additional latency.
Prompting and valid citation IDs alone do not establish factual support.

## Success Criteria

- **SC-001**: Every accepted response uses only supplied citation IDs, and every
  evidence refusal has an empty citation list.
- **SC-002**: Disabled mode produces no remote requests and reproduces the retained
  baseline on the same frozen retrieval configuration.
- **SC-003**: Complete the unchanged 12-question before/after evaluation with equal
  evaluation hashes; report every regression and remaining limitation honestly.
- **SC-004**: Manually review all 12 generated answers for factual support and
  completeness, including E09's location and deadline; preserve the answer text.
- **SC-005**: Distinguish provider failures from evidence refusals in every error
  scenario. Interrupted or failed evaluation runs are not quality evidence.

## Assumptions and scope

- The user requested a separate branch and publication of this plan, then authorized
  implementation on 2026-10-20. Local implementation and offline verification are
  recorded in `docs/gemma-report.md`; the user then supplied a local key and live
  lexical verification completed at 11/12 without PASS-to-FAIL regressions.
- Google AI Studio access was confirmed with the user's local key during the live
  probe and fixed evaluation. Future project quota/access is not guaranteed.
- Vedran implements embeddings separately. Generation can be built using mocked
  retrieved evidence before that work is ready, then integrated through the same
  retrieved-result contract.
- The assignment's LLM allowance is optional advanced work, after submission of
  the required minimum. Submission/review/demo completion is not confirmed here.
  Earlier optional work already records this timing deviation; this plan does not
  silently redefine the required local homework.
- Live execution has an external dependency even when tokens are free. No new
  vector database, web service, agent, search tool or query rewriting is in scope.
