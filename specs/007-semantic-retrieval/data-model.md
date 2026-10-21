# Data model

## Model identity

Immutable fields: model identifier, forty-character commit revision, CPU device
and resolved local cache directory. A changed field creates a different model
identity. Revision must be a full hexadecimal commit ID, never a mutable branch.

## Corpus representation

Key: model identity plus the ordered tuple of original chunk texts.
Value: one normalized vector per text. Vectors must be nonempty, finite,
nonzero, consistently dimensioned and aligned one-to-one with input texts.
Keep at most two corpus representations and one model instance in process caches.
Zero-norm, non-finite, ragged or mismatched output is an operational error.

Chunk IDs, metadata and policy status are not cached with vectors. Retrieval
attaches each score to the current eligible Chunk instance. Thus reordered text
rebuilds the representation and metadata changes cannot return stale citations.

## Retrieval result

Reuse the existing `RetrievalResult(chunk, score)` shape. Semantic score is finite
cosine in [-1, 1]. Keep the existing minimum-score comparison and deterministic
sort `(-score, chunk.chunk_id)`, then take up to TOP_K. Source filtering occurs
before embedding. No fused score, semantic confidence estimate or probability is
introduced. The existing global refusal rule uses the top score unchanged.

## Failure and lifecycle

Unprepared -> explicit preparation -> cached local model -> query/corpus encoding
-> ranked existing chunks -> unchanged grounded answerer.
Errors in configuration, dependencies, local model data or vector shape stop
semantic retrieval with an actionable error. They never select a different
backend or fabricate a refusal. Normal runtime never downloads a model.
