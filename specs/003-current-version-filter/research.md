# Research: Current-version evidence and advanced-work order

Date: 2026-10-19. Sources: repository code, saved results, assignment,
improvement menu and a read-only research agent review.

## Decision: M5 first

Rationale: E06 passes with current hb-03 and superseded hb-02. The metric
tolerates citation precision 0.50, hiding a contradiction. Existing metadata
and searchable_chunks support excluding superseded evidence before scoring.
Alternative: target only failing eval items. Rejected because the known
contradiction matters even when the pass count cannot express improvement.

## Decision: Do not implement the menu as a checklist

Rationale: M2 cannot add notebook/laptop semantics. M4 always retains the top
citation, including a wrong leading E11 result. M6 top-k=1 risks losing E09's
duration chunk. Negative outcomes are acceptable under the assignment.
Alternative: repeat menu tuning until 12/12. Rejected as fitting twelve known
questions without a guarantee of improved general behavior.

## Decision: M2 is optional; measure calibration separately

Rationale: A fixed general stopword list is a useful noise experiment, but
changes score distributions. Freeze M3 thresholds for the first comparison;
subsequent calibration needs its own specification and measurement.
Alternative: combine stopwords and threshold tuning. Rejected as two intents.

## Decision: Small local embedding comparison after M5

Rationale: Semantic retrieval is a plausible hypothesis for E05's paraphrase;
it does not require completion of every menu option. Direct in-memory search
is supported by the official
[Sentence Transformers documentation](https://www.sbert.net/examples/sentence_transformer/applications/semantic-search/README.html).
That supports the search mechanism, not a claim that E05/E11 will pass.
Alternative: introduce a vector database now. Rejected for ten documents.

Topic similarity can retrieve annual leave for parental leave. E11 still needs
evidence sufficiency. Its current best score exceeds valid E04's score, so a
higher lexical refusal threshold cannot solve both. Embedding cosine scores
also do not inherit the lexical threshold's meaning.

## Resolved Technical Questions for M5

- Reuse Chunk.status; no new schema, dependencies or version inference.
- Exclude exactly superseded status, preserving order before existing scoring.
- Preserve disabled behavior and official evaluation/compare code.
- No extension hooks are configured in this checkout.
- Do not assume the required minimum has been submitted.
