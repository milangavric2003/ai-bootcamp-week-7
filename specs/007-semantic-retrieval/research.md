# Research: Fresh local semantic retrieval

21 October 2026. Read-only research required by the installed speckit-plan skill
was delegated to `embedding_research`. No other branch, reference project or
previous embedding implementation was inspected or copied.

## Model and similarity

**Decision**: `sentence-transformers/all-MiniLM-L6-v2`, immutable revision
`1110a243fdf4706b3f48f1d95db1a4f5529b4d41`, CPU, normalized vectors and exact cosine
ranking over this tiny corpus. Encode original question and chunk text. Keep
lexical tokenization and stopword filtering confined to lexical mode.

**Rationale**: The English model outputs 384-dimensional sentence representations;
the official semantic-search documentation describes direct in-memory search.
The revision was verified through the official model API, independently of any
branch. Retaining sentence context rather than removing stopwords is a design
inference from the model's documented sentence-text usage.

**Alternatives considered**: A vector database adds unnecessary infrastructure;
an embedding service adds credential/network dependencies; hybrid retrieval and
reranking combine additional intents and are outside this experiment.

Sources:

- [Model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- [Official model metadata](https://huggingface.co/api/models/sentence-transformers/all-MiniLM-L6-v2)
- [Semantic search](https://www.sbert.net/examples/sentence_transformer/applications/semantic-search/README.html)
- [Similarity](https://www.sbert.net/docs/sentence_transformer/usage/semantic_textual_similarity.html)

## Loading, setup and cache

**Decision**: Lazy SentenceTransformer import; explicit model preparation downloads
only the pinned safetensors/tokenizer/config files. Normal retrieval uses
`local_files_only=True` and `trust_remote_code=False`. Use a fresh model cache
`.cache/semantic-retrieval/`, not the earlier branch's model/cache implementation.

**Rationale**: Lexical operation must not depend on Torch or a download. Existing
cache metadata enumeration hung during research, so a distinct directory avoids
that dependency and makes model preparation explicit. Interrupted read-only
enumeration sessions were stopped. A bounded process-local cache keys model and
corpus representations by exact model identity and original text, with metadata
attached from current caller-provided chunks.

**Alternatives considered**: Runtime downloads hide setup costs and make requests
unexpectedly depend on the network. Persisted vector files add invalidation and
storage complexity without value for ten documents.

Sources:

- [SentenceTransformer API](https://www.sbert.net/docs/package_reference/sentence_transformer/model.html)
- [Hugging Face downloads](https://huggingface.co/docs/huggingface_hub/package_reference/file_download)
- [Cache identity](https://huggingface.co/docs/huggingface_hub/guides/manage-cache)

## Dependencies and boundaries

**Decision**: Optional dependency file pins the already installed and tested
sentence-transformers 6.1.0, torch 2.14.1, transformers 5.20.2,
huggingface-hub 1.33.0 and numpy 2.5.4. Keep base requirements unchanged.

The model truncates after 256 wordpieces. Record the maximum actual chunk token
count during real-model verification and report any truncation risk; do not change
chunking. Cosine and lexical score scales differ. Preserve 0.01 retrieval minimum
and 0.10 refusal threshold to isolate retrieval; do not adopt main's 0.51 or tune
on E01-E12. Gemma still has to distinguish related context from sufficient evidence.

Source: [Pinned sentence model configuration](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/blob/1110a243fdf4706b3f48f1d95db1a4f5529b4d41/sentence_bert_config.json).
