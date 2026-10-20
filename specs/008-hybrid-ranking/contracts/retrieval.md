# Hybrid CLI and retrieval contract

- CLI accepts `--retrieval-backend lexical|embeddings|hybrid`; explicit flags
  override `RAG_RETRIEVAL_BACKEND`. Default remains lexical.
- Evaluation selects hybrid through the existing environment variable; runner
  and JSON schema are unchanged. Snapshot includes backend and RRF constant.
- `retrieve_top_k(query, chunks, k=None)` retains its signature. Reject nonpositive
  k, unknown backend, and nonpositive hybrid RRF constant. Empty input returns
  before loading optional dependencies.
- Hybrid ranks complete eligible component lists, fuses with equal weights and
  constant 60, selects semantic anchor first, then fused candidates excluding it.
- Results are unique by chunk ID, bounded by k, deterministic. Hybrid `.score`
  means RRF, `.semantic_score` means raw cosine; anchor-first order need not be
  globally descending by RRF.
- `--show-retrieved` labels hybrid RRF and semantic scores. Existing mode output
  formatting stays unchanged.
- Refuse when no selected semantic score meets the existing embeddings threshold.
  Missing confidence fails closed; refused answers have no citations.
- Preserve existing actionable dependency/cache errors; no silent fallback.
