# Retrieval and preparation contracts

## Selection

- `RAG_RETRIEVAL_BACKEND=lexical|embeddings` selects the backend in config;
  default `lexical`. Root `.env` loading respects existing process precedence.
- `python -m src.cli --retrieval-backend embeddings --question "..."` overrides
  selection for that invocation. Omitting the option preserves the config value.
- The unchanged eval runner uses the environment choice; no evaluator changes.
- Unknown values fail clearly. Existing k<=0 validation still raises ValueError.
- Empty/no-content query or no eligible chunks returns [] without model load.

## Encoding and output

Both corpus and question use the identical pinned model on original text. No
lexical stopword transformation is applied to semantic inputs. The current-source
filter applies before encoding, and returned objects are the original current
Chunk objects with raw cosine scores. Negative similarities are preserved until
the existing minimum filter; tie ordering and top-k semantics remain unchanged.

## Preparation

`python -m src.prepare_embeddings` explicitly downloads the configured pinned
model's safetensors/config/tokenizer files into the configured cache and reports
the prepared model/revision. It does not embed or upload corpus data. Normal
runtime passes local_files_only=True and trust_remote_code=False. Missing packages
name `requirements-embeddings.txt`; missing model files name the prepare command.

## Compatibility

`RagAnswer`, prompt, generator request shape, citation validator, retries,
thresholds and fixed metrics do not change. Gemma receives actual text/metadata
for selected chunks, never vectors. Model metadata and backend selection are
ordinary public configuration snapshot values, with no credential values added.
