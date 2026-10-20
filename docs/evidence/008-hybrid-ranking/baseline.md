# Hybrid retrieval baseline

Captured by Codex on 20 October 2026, before implementation, on branch
`008-hybrid-ranking` at `ed0f858`. The project virtual environment passed
86 tests. Complete unchanged evaluation: embeddings 12/12, mean citation
precision 0.9444; lexical 10/12, mean citation precision 0.6500.
See `before.json`, `lexical-before.json`, `pytest-before.txt`, `cli-before.txt`,
`answers-before.json`, and source hashes in `before-manifest.json`.

## E09: incomplete answer, despite PASS

- Question: Where do I request a replacement laptop and how long does it take?
- Expected: request in IT portal under Hardware; handover can take up to
  5 business days after manager approval.
- Actual embeddings answer: `hb-01-chunk-1` supplies the deadline;
  `hb-01-chunk-0` describes eligible replacements. Neither supplies the location.
- Type: retrieval ranking / answer completeness regression. The location chunk
  ranks third (cosine 0.643355), behind deadline (0.676557) and description
  (0.662757). Only two chunks are selected.
- Fixed metric: PASS, because its expected fact is only `5 business days` and
  citation relevance is checked at document level. It cannot prove completeness.

## E07: unrelated second citation, despite PASS

- Question: What are the IT support hours?
- Expected: 08:00 to 18:00, Monday to Friday, with relevant support evidence.
- Actual: `hb-10-chunk-0` supplies the right hours, accompanied by
  `hb-03-chunk-3`, remote-work core hours (10:00 to 15:00).
- Type: retrieval / citation relevance failure; citation precision is 0.50.
- This is documented as a control; the proposed change is only required to fix
  E09 completeness. It need not fix every observed limitation.

## Proposed hypothesis

Equal-weight fusion of lexical and semantic rankings can bring the E09 location
chunk into the two selected chunks, preserving the deadline and paraphrase
matching. E09 diagnostic ranks are deadline (lexical 2, semantic 1), location
(1, 3), description (3, 2). Refusal must continue to use semantic evidence
confidence, because fused ranks do not measure support.
