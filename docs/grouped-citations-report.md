# Grouped citation fix and completed embeddings evaluation

**Date**: 21 October 2026, Europe/Belgrade. **Branch**: `feat/gemma-generation`.
**Status**: Fixed and verified; all work remains uncommitted and unstaged.

The current embeddings pipeline now completes the full evaluation at **12/12**:
behaviour accuracy **1.00**, supported retrieval hit rate **1.00**, mean citation
precision **1.00**. The lexical control remains **11/12**. The full suite passes
**225 tests**. No hybrid retrieval, threshold adjustment or prompt edit was added.

## Cause and bounded fix

The user reproduced the evaluation crash after selecting
`RAG_RETRIEVAL_BACKEND=embeddings`. The already captured E09 response used
`[hb-01-chunk-1, hb-01-chunk-2]`, while its citations array correctly selected both
supplied IDs. The old validator checked the entire comma-separated string as a
single source ID and rejected it.

The [spec](../specs/008-grouped-citations/spec.md),
[plan](../specs/008-grouped-citations/plan.md) and
[tasks](../specs/008-grouped-citations/tasks.md) record this separately authorized
fix after the embeddings experiment. Before the change, a fresh suite passed
195 tests, the unchanged semantic offline baseline reproduced 9/12, and the raw
E09 failure was preserved. Existing offline E07/E10 failures remain documented;
they are not misrepresented as additional parser failures or targets of this fix.

[generation.py](../src/generation.py) now validates each comma-separated member
against the selected citations, which were already checked against supplied
evidence, and renders individual inline markers. Source IDs, citation-array order
and factual prose are preserved; repeated group members are deduplicated.
Unknown/unselected IDs, empty members and unsupported separators still fail.
Malformed, nested and unbalanced brackets now fail explicitly instead of escaping
the old complete-group regex. Strict JSON, schema, answer/refusal invariants and
provider failure handling remain intact.

The model prompt is unchanged. Retrieval, weights, chunking, source filtering,
TOP_K=3, STOPWORDS_ENABLED=True, retrieval minimum 0.01 and refusal threshold 0.10
are unchanged. No separate embedding threshold or hybrid implementation exists.

## Regression tests and replay

- [Before](evidence/008-grouped-citations/pytest-before.txt): **195 passed**.
- [Red parser tests](evidence/008-grouped-citations/pytest-red.txt): 15 failures
  before implementation, including the actual saved E09 decision and previously
  unchecked malformed-bracket cases.
- [After](evidence/008-grouped-citations/pytest-after.txt): **225 passed**,
  including 30 new grouped/invalid/malformed citation regression cases.
- [Captured response replay](evidence/008-grouped-citations/captured-decision-replay.json):
  the preserved old parser rejects the same input; the current parser accepts it
  and changes only the citation group into separate valid markers.

The new integration case confirms that normalized text and the original selected
sources reach both RagAnswer and its same-run trace. Existing unknown-source,
strict-JSON, refusal and fallback validation tests continue to pass.

## Actual full evaluation

| Mode, current parser | Passed | Behaviour | Retrieval hit | Citation precision |
| --- | --- | --- | --- | --- |
| [Lexical + configured hosted answerer](evidence/008-grouped-citations/lexical-gemma-control.json) | 11/12 | 0.9167 | 0.8889 | 1.0000 |
| [Embeddings + configured hosted answerer](evidence/008-grouped-citations/semantic-gemma-after.json) | **12/12** | **1.0000** | **1.0000** | **1.0000** |

The unchanged [comparator](evidence/008-grouped-citations/compare-current-backends.txt)
reports **E05 fixed, no PASS-to-FAIL regressions**, with only RETRIEVAL_BACKEND
different. The [lexical reproduction comparison](evidence/008-grouped-citations/compare-lexical-reproduction.txt)
has no setting or metric changes from the earlier working lexical run.

There was no complete semantic hosted score before the parser fix: both earlier
executions stopped at E09. Those failures are preserved, not backfilled or turned
into a fabricated before score. The current 11-to-12 comparison uses the corrected
parser in both modes and measures their actual retrieval difference.

The hosted policy remains Gemma with the existing Gemini fallback. In the semantic
12/12 run, **E03 and E06 were answered by `gemini-3.5-flash-lite`** after transient
Gemma failures. All other generated semantic answers used `gemma-4-26b-a4b-it`;
E12 refused locally. Therefore **12/12 describes the configured pipeline, not an
all-Gemma-only run**. Actual models and ordered attempts are retained in the traces.

All result files use the unchanged evaluation SHA-256:
`afe46db1e75a0b85bb5c9a93b6763e3b96e5cd7b289e12da6d2671e4d8650064`.

## Source and actual answer review

Codex inspected all twelve semantic answers and their cited source text:

| ID | Finding |
| --- | --- |
| E01 | 22 annual-leave days per calendar year, correct leave source |
| E02 | Password changes every 90 days, correct password source |
| E03 | 800 EUR yearly for courses/conferences/certifications, correct training source; fallback model |
| E04 | Up to five business days after manager approval, equipment deadline source |
| E05 | Same qualified deadline now retrieved and answered correctly |
| E06 | Up to three remote days weekly, current policy; fallback model |
| E07 | IT support 08:00-18:00 Monday-Friday, only relevant support source cited |
| E08 | Travel receipts within 30 days of return via finance app, correct travel source |
| E09 | IT portal / Hardware plus up to five business days after manager approval, both correct supplied source IDs |
| E10 | Correct evidence-based refusal, no citations |
| E11 | Correct refusal: annual leave is not parental leave, no citations |
| E12 | Correct local refusal, no generation call |

The independent [E09 CLI](evidence/008-grouped-citations/semantic-e09-cli.txt)
again completed with both facts, the approval qualification, and separate valid
inline citations. This is an assistant source review, not independent human peer review.

## Controls, rate and remaining limitations

The [offline before/after comparison](evidence/008-grouped-citations/compare-offline-reproduction.txt)
has **identical rows and metrics**, 9/12 in both cases, with no changed settings.
E07 citation padding and unsupported E10/E11 offline answers remain; this parser
fix does not improve the extractive answer policy. No hybrid work was added.

This follow-up made **28 transport attempts**: 26 Gemma and two Gemini, including
six transient failed attempts and 22 successes. The minimum spacing was **2.10012
seconds**, and the maximum in any rolling minute was **12**, below the user limit
of 30. Reported successful-response token usage totals **12,444**; failed-request
usage may be unknown, so this is not a complete billing total.

The [checkpoint](evidence/008-grouped-citations/before-manifest.json) preserves the
already uncommitted embeddings source and prior evidence. The
[final verification](evidence/008-grouped-citations/verification.json) checks source
hash boundaries, fixed evaluator/metric files, unchanged settings and prompt,
actual result/trace alignment, citation membership and request pacing. The earlier
failed embedding measurements and their historical reports remain available.

A valid citation ID does not itself prove every claim; actual answer review still
matters. One 12-question known-set run does not prove generalization or future
model determinism. The fallback dependency and offline limitations remain visible.
Required homework and prior optional experiments remain separate. No learner work,
peer review or submission is invented.

## Reproduce and commit

The user's existing command now works with the selected hosted answerer:

```powershell
$env:RAG_RETRIEVAL_BACKEND = 'embeddings'
python -m src.eval_runner --out results/manual-embeddings-fixed.json
```

Choose a fresh result/trace filename for each measured run. The rate-limited helper
can reproduce a live run with `run.py eval --label <fresh-label> --backend gemma
--retrieval embeddings` under this evidence directory.

Suggested combined commit message:

```text
feat: add local semantic retrieval with grouped citation support
```

Stage the earlier embedding feature paths plus `src/generation.py`,
`tests/test_generation.py`, `specs/008-grouped-citations/`,
`docs/evidence/008-grouped-citations/` and this report. Keep `.cache/`, `week06/`,
the real `.env` and temporary test files out. Nothing has been staged or committed.
