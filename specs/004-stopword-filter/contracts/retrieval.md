# M2 retrieval contract

- `tokenize(text)` retains its existing interface and lowercase regex tokenization.
  With STOPWORDS_ENABLED true, remove only the frozen words; with false, preserve
  the old stream. Preserve order, repeated remaining words and quantities.
- `lexical_score(query, chunk_text)` retains its interface and formula. Both streams
  pass through the same tokenizer. An empty stream produces 0.0 without division.
- `retrieve_top_k` keeps current-version filtering, minimum score, stable chunk-ID
  tie breaking and top-k. No stopword-only match is retrieved at current settings.
- The CLI, answer/refusal object, citations, eval rows and metric formulas do not
  change. A query filtered to nothing follows the existing refusal path.
- The existing config snapshot records only STOPWORDS_ENABLED changing. Record the
  vocabulary in plan.md and implementation.diff; do not change metric metadata code.
