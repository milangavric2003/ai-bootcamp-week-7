# Implementation Plan: Grounded Gemma answering

**Date**: 2026-10-19 | **Spec**: [spec.md](spec.md)

**Feature branch**: `feat/gemma-generation`

**Status**: Live-verified on 2026-10-20; 134 tests pass. The separate lexical
comparison improves 10/12 to 11/12, fixing E11 without PASS-to-FAIL regressions.
E05 and embedding integration remain pending.

The design below was written before implementation. Actual execution evidence and
remaining checks are recorded in [the implementation report](../../docs/gemma-report.md).

## Summary

Add an optional grounded answerer using the user's Google AI Studio key and
Gemini API model `gemma-4-26b-a4b-it`. It receives the question and all retrieved
top-k chunks as text with IDs and metadata, then produces an answer with selected
citations or a refusal when those chunks do not support the question.

Embeddings select evidence; generation interprets that evidence. Vectors themselves
are not sent to the text-generation model. The current pipeline echoes selected
chunks rather than calling an LLM. `TOP_K=2` currently means at most two chunks,
not the whole corpus. Passing both as context does not mean citing both.

Keep M2 disabled. Vedran owns embedding retrieval; this feature owns answering.
Build and mock-test against the existing result contract while he works, then
integrate and measure with a frozen retrieval backend. A generator cannot recover
a fact that never reaches its context.

## Technical Context

**Language/Version**: Existing Python 3.12 project, repository-root virtual environment.

**Dependencies**: Standard-library HTTPS/JSON; add a pinned `python-dotenv` during
implementation for local environment-file loading. No Google SDK is required.

**Storage**: Existing corpus/chunks, ignored local `.env`, separate evidence JSON/JSONL.

**Testing**: Existing pytest suite plus mock HTTP/output-validation tests; live checks
only once the key is available.

**Platform/Type**: Existing local CLI and evaluation runner on Windows; hosted Google
generation is an optional network dependency.

**Scale**: Ten source documents, fixed 12-question evaluation, current top-k of two.

**Execution choices**: One request per eligible question, no retries, temperature 0,
1024 output-token cap, minimal thinking, 30-second socket timeout. These are initial
design choices, subject to a documented capability probe before freezing them.

**Constraints**: No changes to `eval/eval_set.json`, metric calculations, corpus,
chunking, retrieval ranking, top-k, thresholds or M2 state. No promised pass count,
determinism, response latency or project quota.

## Constitution Check

| Principle | Design disposition |
| --- | --- |
| One controlled change | Only answering policy changes within each comparison; embeddings have a separate baseline and measurement |
| Fixed evaluation | Same complete 12 questions, runner and metrics; matching SHA-256 required |
| Evidence before implementation | Historical E05/E11 evidence is linked in the spec; capture a fresh baseline and record actual failures before any runtime edits |
| Local and simple | Hosted LLM is outside the required local experiment, expressly requested as optional advanced work |
| Honest results and review | Report regressions, answer-review findings, remaining limitations, dependencies, latency and actual usage/cost |
| Project boundaries | Root application only; original starter and week06 references remain preserved |

**Pre-design gate**: Planning passes under the explicit user authorization for
optional LLM work. The assignment places advanced work after submission of the
required minimum; submission, peer review and demo ownership are not confirmed.
Keep that timing condition visible in the report; planning is not evidence of
submission. Do not amend the constitution to make a hosted API part of required M1.

**Post-design gate**: Same disposition. Provider, model, interface, configuration
and error-policy decisions are resolved. Credentials, live capability verification,
fresh baseline and Vedran's embedding integration remain execution prerequisites.

## Project Structure

Design artifacts, all created in this planning step:

```text
specs/005-grounded-gemma/
  spec.md
  plan.md
  research.md
  data-model.md
  quickstart.md
  contracts/
    generation.md
    .env.example
```

Planned implementation targets, not created or edited now:

```text
src/config.py          # Public nonsecret answering settings
src/rag.py             # Answerer selection after unchanged retrieval/gate
src/generation.py      # Grounding prompt, validated decision, optional answer trace
src/gemma_client.py    # Google REST request, timeout, sanitized provider errors
src/cli.py             # Clear operational-error presentation if needed
tests/test_generation.py
tests/test_gemma_client.py
.env.example           # Promote the supplied design template
.gitignore             # Ignore real environment files
requirements.txt       # Pin dotenv dependency
docs/evidence/005-gemma/
docs/gemma-report.md
```

These source targets are provisional until tasks are generated. Keep
`src/eval_runner.py`, `src/eval_compare.py` and the eval set unchanged. New
configuration keys can be included by the existing `config.snapshot()` without
changing how metrics are calculated. Never expose the key through that snapshot.

## Phase 0 - Research

Completed in [research.md](research.md): assignment interpretation, official Google
model/provider support, free-tier limits, transport, environment loading, strict
output validation, and limitations of the existing evaluator. Provider uncertainty
was resolved by the user's confirmation of Google AI Studio.

No native JSON-schema capability is assumed for this model. Prompt for JSON and
validate locally; verify the selected model/settings with a live smoke test later.
No inference request or credential access was needed for this design.

## Phase 1 - Design and contracts

Completed: [data model](data-model.md), [generation contract](contracts/generation.md),
[environment template](contracts/.env.example), [validation guide](quickstart.md).

### Retrieval and generation boundary

Retain `RetrievalResult` and `RagAnswer`. Add an answerer consuming the already
retrieved list. Preserve all retrieval results in the answer object; final citations
are the subset the answer uses. Preserve the existing no-results/score gate before
generation. Calibrating cosine thresholds belongs to the separate retrieval
experiment; this feature neither reuses scores as probabilities nor retunes them.

### Grounding, validation and errors

The prompt permits only supplied evidence, asks for coverage of all question parts,
and distinguishes related policies such as annual and parental leave. It requests
an answer/refusal JSON object with source IDs. Validate types, fields, complete
output and citation membership before constructing `RagAnswer`.

Valid evidence refusals use the existing refusal text and empty citations.
Malformed output or API failures raise operational errors, stopping a measured run.
No failed request becomes a correct refusal, fallback answer or alternate model.
Mechanical citation checks do not prove semantic support.

### Environment and evidence

Use the example with a blank `GEMINI_API_KEY`. During implementation add ignore
rules before making the real `.env`, then load that root file with process
environment taking precedence. Default `ANSWER_BACKEND=extractive` preserves
offline use. Secrets stay out of public config, traces and errors.

Record public model/prompt/settings in the existing config snapshot in both modes;
only the selected answer backend should change in a controlled pair. Optional
`GEMMA_TRACE_PATH` records actual answer text and execution metadata from the same
run, including local refusals, without entering the behavior-setting comparison.
Use fresh evidence filenames. Do not overwrite earlier runs.

## Later implementation order

1. **Use the separate branch.** `feat/gemma-generation` has been created at the
   user's subsequent request to commit and push the plan.
   If contributors share a checkout, prefer a separate clone/worktree for actual
   simultaneous work: a branch alone does not isolate one working directory.
   Select a writable location when starting; do not move Vedran's files.
2. **Capture the unchanged baseline before runtime edits.** Run pytest and all 12
   questions on the current retrieval state, save source/config/eval hashes, and
   document at least two actual failures. E05/E11 are the historical candidates;
   if the new baseline differs, record the actual situation instead.
3. **Implement one optional answering policy.** Add config/secret loading, the
   HTTP client, grounded decision validation and answer tracing. Keep retrieval
   untouched; add mock tests for grounded/refusal decisions and provider failures.
4. **Verify offline compatibility.** No key or network is needed for default mode
   or unit tests. Reproduce the frozen baseline with generation disabled.
5. **Validate live capabilities when the key arrives.** Check model access,
   generation settings, full response extraction and strict JSON on small
   development examples outside the fixed eval set. Stop on unsupported settings;
   finalize and freeze the prompt/settings before measurement.
6. **Measure generation in isolation.** Run the fixed eval with extraction and
   Gemma over the same frozen retrieval configuration; save comparisons and
   traces. Review all generated text, not only pass/fail.
7. **Integrate Vedran's measured retrieval result.** Merge/cherry-pick deliberately,
   resolve shared config/rag changes, and verify the retrieval contract. Then
   freeze embeddings and compare extraction versus Gemma again. Keep the lexical
   comparison, if run, distinct from the embedding comparison.
8. **Report.** State whether E11 changed, every regression, unsupported facts or
   omissions, actual latency/usage, and remaining limitations. No 12/12 promise.

This is an implementation sequence, not a completed `tasks.md`. Generate detailed
tasks with the installed Spec Kit skill when implementation begins.

## Measurement design

| Run | Retrieval | Answering | Purpose |
| --- | --- | --- | --- |
| A | Retained lexical | Existing extractive | Current historical baseline is 10/12; rerun before edits |
| A-G (optional) | Same lexical config as A | Gemma | Isolate generation while embeddings are being developed |
| B | Vedran's frozen embeddings | Existing extractive | Measure retrieval separately, against the appropriate lexical baseline |
| C | Exactly B's retrieval | Gemma | Primary end-to-end LLM comparison: B versus C |

M2 remains false throughout. Embedding retrieval scores/thresholds must already be
defined in B; C does not recalibrate them. Never attribute A-versus-C gains entirely
to Gemma. Before/after outputs use separate directories and matching eval hashes.

The evaluator checks facts in cited chunks rather than factuality or completeness
of generated prose. Preserve all 12 answers, inspect each claim against its cited
source, and explicitly check E09's request location plus deadline. E04/E06/E10/E11
are useful controls; an LLM does not guarantee improvement. Record service failures
as incomplete execution, not quality results.

## Complexity Tracking

| Required-homework boundary | Why this optional feature differs | Scope control |
| --- | --- | --- |
| Required experiment is offline and local | User expressly requests hosted Gemma for advanced exploration | Keep API disabled by default, separate experiments/reports, no required-M1 claims |
| Advanced work follows submitted minimum | Submission has not been confirmed | Preserve the assignment condition and documented timing deviation; no submission claim |

## Completion record

Spec Kit setup helper ran with an explicit feature directory and
`SPECIFY_FEATURE_NO_PERSIST=1`. Its returned `BRANCH=005-grounded-gemma` is a feature
identifier, not a Git switch; Git remained on `main` during initial planning. The
user subsequently requested publication on a new branch, `feat/gemma-generation`.
Shared `.specify/feature.json` remains pinned to the previous feature. No extension hook
configuration exists, so there are no before/after-plan hooks to run.

The initial design stopped here. The user subsequently authorized implementation;
see `tasks.md` for completed local work and credential/embedding-dependent tasks.
