# Hybrid ranking research

20 October 2026. Completed before pipeline implementation.

## Decision: semantically anchored equal-weight RRF

**Rationale**: E09 ranks deadline lexical 2 / semantic 1, location 1 / 3, general
description 3 / 2. RRF promotes deadline and location. Use all eligible ranked
candidates so early TOP_K truncation cannot discard complementary evidence.

[Microsoft's RRF documentation](https://learn.microsoft.com/en-us/azure/search/hybrid-search-ranking)
supports the reciprocal-rank sum and constant 60. It does not prove our answer
quality or establish the custom anchoring policy.

**Alternatives considered**: Plain equal-weight RRF fixes E09 but drops E05's
deadline in `docs/evidence/008-hybrid-ranking/planning-diagnostic.json`, predicting
11/12. A generic semantic anchor retains the best semantic evidence and fills
the other slot from fused candidates, predicting 12/12. This preimplementation
design decision uses known eval questions; it is not held-out validation.
No weights or thresholds were tuned.

Increasing TOP_K adds context globally. Candidate-depth restrictions, score
normalization, stopword filtering, and a new reranker add choices or alter other
experiments; they are outside this change.

## Decision: separate rank from evidence confidence

**Rationale**: Two RRF contributions with constant 60 total at most 2/61, about
0.0328. Existing 0.51 cosine / 0.10 lexical thresholds cannot apply to that scale.
Carry raw cosine and gate on the maximum among selected evidence using existing
0.51. Missing scores fail closed. This is backend scale adaptation, not tuning.

**Alternatives considered**: Fused rank measures relative relevance, not support.
An unselected strong source cannot ground weaker selected evidence. Per-query
normalization would create high confidence even on unrelated questions.

## Decision: preserve optionality and report secondary regressions

**Rationale**: The anchored diagnostic predicts citation precision 0.8333 versus
embeddings 0.9444: E01/E05 gain unrelated secondary citations; E07 retains its
remote-hours citation. Document this tradeoff and retain lexical as default.

**Research review**: The speckit-plan research agent reviewed component filtering,
union/tie/minimum semantics, anchoring, and the confidence gate. Codex ran the
saved diagnostic. No pipeline code was edited during research; no unresolved
design questions remain.
