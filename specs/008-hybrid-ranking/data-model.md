# Hybrid retrieval data model

- `Chunk`: unchanged source identity, version/status metadata, and text.
- `RetrievalResult`: existing `chunk` and `score`; append optional
  `semantic_score: float | None = None` for compatible construction. Existing
  modes leave it unset. Hybrid `score` is RRF, semantic score is raw cosine.
- Component rankings: complete independently minimum-filtered lists, ordered
  by descending raw score and then ascending chunk ID.
- Fused ranking: unique chunk IDs with summed reciprocal-rank contributions.
  Anchor-first selection may differ from globally descending fused score.
- `RagAnswer`: unchanged answer, citations, refusal, and retrieved evidence.
  Hybrid confidence uses only semantic values of selected results.
- Run configuration: existing snapshot plus `HYBRID_RRF_CONSTANT=60`; backend
  `hybrid` identifies semantically anchored fusion. No persisted index or migration.
