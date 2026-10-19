# Data Model: Current-version eligibility

No stored schema changes.

- Document retains doc_id, version and status.
- Chunk retains source metadata, including status.
- Eligibility is derived: CURRENT_ONLY disabled retains all existing candidates;
  enabled excludes status superseded.
- RetrievalResult retains its existing chunk and lexical score.
- Eval JSON retains configuration, hash, summary and rows. CURRENT_ONLY identifies
  the experiment; metric definitions remain fixed.

Filtering must not mutate the input or chunks. No version ordering,
replacement relationships or historical-query routing is introduced.
