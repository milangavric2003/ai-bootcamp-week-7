# Data model: Grounded Gemma answering

## Existing evidence and answer types

Keep `Chunk`, `RetrievalResult` and `RagAnswer` compatible with current callers.
Generation consumes the ordered results already returned by retrieval.

| Entity | Fields used | Rules |
| --- | --- | --- |
| `Chunk` | `chunk_id`, `doc_id`, `title`, `version`, `status`, `text` | IDs and source text are preserved |
| `RetrievalResult` | `chunk`, `score` | Returned order and scores are preserved; no reranking |
| `RagAnswer` | `answer`, `citations`, `refused`, `retrieved` | Existing CLI and evaluator contract retained |

## Generation decision

The model returns one JSON object with exactly these fields:

| Field | Type | Validation |
| --- | --- | --- |
| `answer` | string | Nonempty for an answer; empty for a model refusal |
| `citations` | array of strings | Answer: at least one supplied chunk ID; refusal: empty |
| `refused` | boolean | Strict JSON boolean, not a string or number |

Reject missing/extra fields, invalid types, unknown IDs and contradictory fields.
Deduplicate valid citations while preserving their first occurrence. Validate any
inline chunk markers against the same selected IDs. Refusals map to the existing
`REFUSAL_MESSAGE`, `citations=[]`, `refused=True`; valid answers preserve the
generated text and selected IDs. Both retain the original `retrieved` list.

ID membership establishes source identity, not whether that source proves a claim.
The latter is part of manual answer review.

## Configuration and trace

- Public experiment settings: answering backend, provider/model identity,
  temperature, output limit, thinking level, timeout and prompt SHA-256.
- Private runtime input: `GEMINI_API_KEY`, fetched locally for the request; never
  stored as an uppercase value in `src.config`, whose snapshot captures such values.
- Optional trace destination: `GEMMA_TRACE_PATH`, an evidence-file path rather than
  a behavior setting; exclude it from configuration comparison.
- Trace record: question, retrieval IDs and scores, final answer/citations/refusal,
  backend/model, prompt fingerprint, request status, duration and returned token
  usage if available. No credential, authorization header or raw HTTP error body.
  Every evaluated question has a final record, including local gate refusals.

## State transitions

1. Select backend. Gemma configuration/key validation happens before a run's first
   request; extractive mode never requires credentials.
2. Retrieve using the existing pipeline. Empty results or the unchanged score gate
   produce a local evidence refusal and no remote request.
3. Extractive mode follows current answering. Gemma mode serializes all returned
   evidence and performs at most one request.
4. A successful, complete text response is parsed and validated, then mapped to
   `RagAnswer` and traced.
5. Configuration, network, provider or output-validation failure raises a typed
   operational error and records a sanitized failure. It produces no `RagAnswer`;
   the existing evaluator stops instead of counting it as a correct refusal.
