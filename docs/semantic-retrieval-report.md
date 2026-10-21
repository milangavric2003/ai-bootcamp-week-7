# Fresh local semantic retrieval experiment

**Later follow-up**: The user authorized fixing grouped inline citations after this
experiment. That fix now completes the full hosted evaluation at **12/12** under
the existing Gemma/Gemini fallback policy, with **225 tests passing**. See the
[current citation fix report](grouped-citations-report.md) for measured results,
actual models and the current commit message. The original embeddings-only
measurements and failed executions below are preserved as historical evidence.

**Date**: 21 October 2026, Europe/Belgrade.
**Branch/baseline**: `feat/gemma-generation`, `95657b9`.
**Disposition**: Implemented and tested as an opt-in backend; leave lexical as the
default. Work is uncommitted for the user to review, commit and push.

The new local backend retrieves E05's equipment policy and deadline, where lexical
retrieval missed the source. An independent live E05 answer correctly states up to
five business days after manager approval. All **195 tests pass**. Full offline
evaluation stays **9/12**, with two fixed and two regressed questions. The full
semantic Gemma evaluation stops at **E09 citation formatting**, including one
recovery; no aggregate semantic live score is claimed.

## Scope and specification before implementation

The user requested a fresh implementation without selectively reusing code from
other branches/projects, authorized live testing, and retained the limit of 30
Gemma requests/minute. Only this branch's existing architecture and official model
APIs were used. No merge, cherry-pick, imported embedding code or earlier vector
cache was used. A public model was prepared into a new cache directory.

The [spec](../specs/007-semantic-retrieval/spec.md),
[plan](../specs/007-semantic-retrieval/plan.md),
[research](../specs/007-semantic-retrieval/research.md) and
[tasks](../specs/007-semantic-retrieval/tasks.md) precede runtime edits. Planning
used the read-only research agent required by the installed Spec Kit plan skill.
The required M1 homework and earlier optional experiments remain separate.

Before implementation, [163 tests passed](evidence/007-semantic-retrieval/pytest-before.txt),
fresh [offline evaluation](evidence/007-semantic-retrieval/lexical-extractive-before.json)
gave 9/12, and fresh [Gemma evaluation](evidence/007-semantic-retrieval/lexical-gemma-before.json)
gave 11/12. Two offline failures were documented in the
[baseline](evidence/007-semantic-retrieval/baseline.md): E05's missing equipment
evidence and E01's irrelevant remote-work citations. E11 also fails offline;
Gemma already fixes E01/E11, so they are not called Gemma baseline failures.

**Hypothesis**: Local sentence similarity retrieves the equipment-policy timeline
for notebook-computer wording. **Expected effect**: E05 gains the missing source;
generation can answer if that evidence is sufficient. **Risks**: Related but
unsupported text can score highly; extra citations can lower precision; model
loading adds dependencies and startup time; different context can trigger existing
generation/formatting failures. None of these risks is hidden by threshold tuning.

## Implementation

- [semantic_retrieval.py](../src/semantic_retrieval.py) lazily loads a pinned CPU
  model and encodes original question/chunk text. Unit-normalized vectors use exact
  cosine ranking. Vector counts, shapes, finite values and nonzero norms are checked.
- [retrieval.py](../src/retrieval.py) dispatches `lexical` or `embeddings` while
  retaining the same current-source filter, score minimum, stable tie ordering and
  top-k contract. Returned Chunk objects and metadata come from the current input.
- A bounded process-local cache retains one model and two ordered text
  representations. Model identity/text changes invalidate the relevant keys;
  citation metadata is not stored with the vectors.
- [prepare_embeddings.py](../src/prepare_embeddings.py) explicitly downloads pinned
  safetensors/config/tokenizer files. Normal runtime is `local_files_only=True`,
  `trust_remote_code=False`, with no embedding API or vector database.
- [cli.py](../src/cli.py) supports `--retrieval-backend embeddings` and actionable
  retrieval errors. `RAG_RETRIEVAL_BACKEND` selects the backend for the unchanged
  evaluator; the default remains lexical. Test fixtures isolate developer settings.
- [requirements-embeddings.txt](../requirements-embeddings.txt) records optional
  tested dependencies; base requirements and the user's real `.env` are untouched.

Model: `sentence-transformers/all-MiniLM-L6-v2`, immutable revision
`1110a243fdf4706b3f48f1d95db1a4f5529b4d41`. The pin came from official model metadata,
not another branch's implementation. See [research](../specs/007-semantic-retrieval/research.md)
for primary documentation links and alternatives.

Existing **TOP_K=3**, **STOPWORDS_ENABLED=True**, **RETRIEVAL_MIN_SCORE=0.01** and
**REFUSAL_THRESHOLD=0.10** are preserved. Stopwords affect lexical mode only;
semantic encoding uses original text. There is no separate embedding refusal
threshold, no 0.51 calibration, no hybrid/reranker or synonym dictionary, and no
prompt/citation-validator/retry/chunking/corpus/metric change.

## Tests and real model

The [red run](evidence/007-semantic-retrieval/pytest-red.txt) failed before the new
module existed. After implementation, [195/195 pass](evidence/007-semantic-retrieval/pytest-after.txt),
including 32 new offline semantic cases. They cover normalized/signed cosine,
raw-text preservation, filtering, ties, top-k/minimum, cache reuse/invalidation,
fresh metadata, empty inputs, malformed vectors, missing dependencies/cache,
immutable revision, explicit preparation, CLI errors and actual semantic evidence
delivery to a mocked Gemma request. Tests load no real model or hosted provider.

The explicit [model preparation](evidence/007-semantic-retrieval/model-prepare.txt)
completed successfully. The evidence helper initially failed while displaying
Unicode progress under Windows cp1252, after preserving the successful subprocess
exit and log. Its console encoding was corrected; no model redownload was needed.

The separate [real-model probe](evidence/007-semantic-retrieval/real-model-verification.json)
ran with `HF_HUB_OFFLINE=1`. It verifies 384-dimensional output, 24 eligible chunks,
encoding batch sizes `[24, 1, 1]` for two queries, and a 37-token maximum chunk
against a 256-token model limit. All chunks fit without truncation. Logical unique
model cache files total **91,585,009 bytes** (about 87.3 MiB).

On this machine model loading took about **5.49 seconds**; the first query/corpus
encoding took **0.149 seconds**, and the second query **0.0089 seconds**. These are
specific observations, not latency guarantees. Each new CLI process loads its own
model; within one process, repeated evaluation questions reuse corpus vectors.

## Complete offline comparison

| Metric | Lexical baseline | Semantic, same numeric thresholds |
| --- | --- | --- |
| Passed | 9/12 | 9/12 |
| Behaviour accuracy | 0.9167 | 0.8333 |
| Retrieval hit rate on supported questions | 0.8889 | 1.0000 |
| Mean citation precision | 0.6333 | 0.6364 |

Actual [after JSON](evidence/007-semantic-retrieval/semantic-extractive-after.json)
and [before/after comparator](evidence/007-semantic-retrieval/compare-extractive.txt):
**fixed E01, E05; regressed E07, E10**. The equal totals hide the tradeoff.

- E01's annual-leave citations improve 0.3333 to 0.6667, crossing the pass threshold.
- E05 now retrieves all three equipment-policy chunks; the timeline source leads
  at cosine **0.632196**, with precision 1.0 and the expected fact present.
- E07's IT-support fact remains correct, but two remote-work passages dilute
  extractive citation precision from 0.6667 to **0.3333**, causing a failure.
- E10 now answers training/onboarding/support text because its best cosine
  **0.175122** exceeds the unchanged refusal threshold 0.10. This is a wrong answer.
- E02 precision falls 1.0 to 0.6667 without a pass regression. E03/E04/E06/E08/E09
  retain their pass status and citation precision. E11 remains a wrong offline
  answer despite related annual-leave cosine 0.504503. E12 still refuses locally.

The old-snapshot comparison warns about five newly recorded configuration keys:
backend, model, revision, device and cache. Those describe one new retrieval
backend; existing values are fixed. An additional
[same-snapshot comparison](evidence/007-semantic-retrieval/compare-backends-same-snapshot.txt)
reports **only RETRIEVAL_BACKEND** changed and reproduces the same outcome.

The [offline lexical control](evidence/007-semantic-retrieval/lexical-extractive-after.json)
reproduces every original result row and summary exactly. The
[Gemma lexical control](evidence/007-semantic-retrieval/lexical-gemma-control.json)
also reproduces every original result row and summary, **11/12**, independently of
the new backend. Their comparison outputs are preserved beside the results.

## Live semantic verification and operational regression

The first [semantic live execution](evidence/007-semantic-retrieval/semantic-gemma-after.txt)
answered E01-E08, including a correct E05 answer, then stopped at E09 with
`InvalidResponseError: Gemma inline citations must match the selected source IDs.`
The one planned [recovery](evidence/007-semantic-retrieval/semantic-gemma-recovery.txt)
failed at the same question with unchanged settings. The independent
[E09 CLI check](evidence/007-semantic-retrieval/semantic-e09-cli.txt) also failed.
These are operational regressions relative to the working lexical configuration,
even though the validator itself was not changed.

The [raw decision diagnostic](evidence/007-semantic-retrieval/e09-raw-decision.json)
shows valid JSON with correct selected source IDs in the citations array, but one
combined inline marker: `[hb-01-chunk-1, hb-01-chunk-2]`. The current contract requires
individual `[chunk_id]` markers. The raw response states IT portal / Hardware and
up to five business days after manager approval; the retrieval evidence supports
both. The existing validator nevertheless correctly enforces its specified format
and stops. No validator loosening, prompt edit or hidden fallback was added to
obtain a pass. This formatting issue is recorded separately from retrieval quality.

**No complete semantic Gemma result JSON exists.** The
[unavailable-comparison record](evidence/007-semantic-retrieval/compare-gemma-unavailable.txt)
explains why no full aggregate score is reported. Successful prefixes and separate
CLI checks are not stitched together into a supposed twelve-question evaluation.

## Actual answer and source review

Codex inspected the actual source text and saved answers, not just the metrics.
The semantic prefix answers in both attempts are supported:

| Case | Actual live finding |
| --- | --- |
| E01 | 22 days per calendar year, only annual-leave source cited |
| E02 | Passwords every 90 days, correct password source |
| E03 | 800 EUR yearly for courses/conferences/certifications, correct training source |
| E04 | Up to five business days after manager approval, deadline source |
| E05 | Same qualified timeline now answered from the equipment source |
| E06 | Up to three remote days weekly, current policy source |
| E07 | 08:00-18:00 Monday-Friday, only IT-support source cited despite irrelevant retrieved context |
| E08 | Receipts within 30 days of return via finance app, correct travel source |
| E09 | Complete evidence retrieved, but rejected combined inline marker; not a successful answer |

Independent [E05 CLI](evidence/007-semantic-retrieval/semantic-e05-cli.txt) again
answers with the approval qualification and deadline source. The separately
checked unsupported cases were not reached by the interrupted full run:
[E10](evidence/007-semantic-retrieval/semantic-e10-cli.txt) and
[E11](evidence/007-semantic-retrieval/semantic-e11-cli.txt) correctly refuse via
Gemma with no citations, despite positive semantic scores; [E12](evidence/007-semantic-retrieval/semantic-e12-cli.txt)
refuses through the local score gate, without a generation call. These individual
observations do not establish a complete aggregate live score.

## Integrity, resources and limits

The [final verification](evidence/007-semantic-retrieval/verification-handoff.json)
checks the original commit and all 387 existing tracked-file hashes, allowing only
the declared config/dispatch/CLI/test-fixture/template/README edits. It checks
unchanged fixed evaluation code/data, all existing config values, exact lexical
reproduction, actual result/trace alignment, E05 sources, unsupported refusals and
the diagnosed E09 error. Evaluation SHA-256:
`afe46db1e75a0b85bb5c9a93b6763e3b96e5cd7b289e12da6d2671e4d8650064`.

Live testing made **46 transport attempts**, all to the configured Gemma model,
with **2.100065 seconds** minimum spacing and **12 requests** maximum in any rolling
minute, below the user's 30/minute limit. Three transient HTTP 500 responses were
recovered on the second Gemma attempt by the existing retry policy; no fallback
model was used. Reported trace usage is **21,930 tokens**; invalid-decision traces
and failed transport attempts omit response usage, so this is an incomplete usage/billing total. No currency cost is
inferred. Embeddings are computed locally and use no embedding-service quota.

The model weights and pytest temporary files stay out of the proposed commit.
The [implementation diff](evidence/007-semantic-retrieval/implementation.diff)
captures source changes; prior homework/results and reference folders are preserved.
The work is intentionally uncommitted and unstaged.

Remaining limits: cosine scale is not calibrated evidence confidence; offline
extractive refusal/citation regressions remain; E09's model-formatting failure
prevents a complete semantic live evaluation; the general-purpose English model
may miss new paraphrases; model loading adds startup time and optional dependencies.
Known evaluation questions were used to identify the target, so no held-out
generalization claim is justified. Fixed metrics check facts in cited chunks,
not complete generated prose. No independent human peer review or assignment
submission is claimed. The user chose the scope; Codex specified, implemented,
tested and inspected sources. No learner work or contributor approval is invented.

## Run and commit

Model files are prepared on this machine. After activating the project environment:

```powershell
python -m src.cli --retrieval-backend embeddings --question "How long until I get a new notebook computer?" --show-retrieved
```

The CLI option uses the existing selected answerer; set `ANSWER_BACKEND=gemma`
explicitly when needed. Full setup, environment selection and fresh measurement
commands are in [quickstart](../specs/007-semantic-retrieval/quickstart.md).

Suggested commit message:

```text
feat: add opt-in local semantic retrieval

Add pinned CPU sentence embeddings with explicit model preparation, lazy offline
loading, bounded text caches and selectable retrieval. Preserve lexical behavior,
thresholds and grounded generation. Add 32 offline contracts and real/live evidence,
including the E05 improvement, offline regressions and E09 citation-format limit.
```

Stage only the explicit feature source/test/docs/template/requirements paths;
leave `.cache/`, `week06/`, the real `.env` and test temporary directories out.

```powershell
git add -- .env.example README.md requirements-embeddings.txt src/config.py src/retrieval.py src/cli.py src/semantic_retrieval.py src/retrieval_errors.py src/prepare_embeddings.py tests/conftest.py tests/test_semantic_retrieval.py specs/007-semantic-retrieval docs/semantic-retrieval-report.md docs/evidence/007-semantic-retrieval
```
