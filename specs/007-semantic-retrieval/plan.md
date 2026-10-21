# Implementation Plan: Local semantic retrieval

**Branch**: `feat/gemma-generation` | **Date**: 2026-10-21
**Spec**: [spec.md](spec.md)

## Summary

Add a fresh optional local semantic backend to the existing retrieval function.
Keep the same Chunk/RetrievalResult contracts and feed selected text into the
existing grounded answerer. The only measured improvement is retrieval scoring;
no threshold, chunking, prompt, citation-validation or hybrid change is bundled.

Fresh unchanged baseline at `95657b9`: 163 passing tests, offline 9/12, Gemma 11/12.
E05 and E01 failures were documented before runtime edits. The research agent used
only installed APIs, public model documentation and model-data inspection attempts.
It did not inspect another branch/project's implementation.

## Technical Context

**Language/Version**: Python 3.13.7, existing repository-root virtual environment.
**Dependencies**: Optional pinned sentence-transformers 6.1.0, torch 2.14.1,
transformers 5.20.2, huggingface-hub 1.33.0, numpy 2.5.4. Base requirements unchanged.
**Storage**: Pinned public model files in `.cache/semantic-retrieval/`; process-local
bounded model/corpus-vector caches. No vector DB or embedding API.
**Testing**: Existing pytest plus offline fake-encoder contracts; separately verify
real local model, full offline/live evaluations, unsupported cases and CLI sources.
**Platform**: Local Python CLI and unchanged evaluation runner on Windows/CPU.
**Scale**: Ten documents, original sentence chunks, three results per query.
**Performance**: Encode an unchanged corpus once per process; keep one encoder and
at most two text representations. Record cold/warm timings without an SLA claim.
**Constraints**: Same thresholds 0.01/0.10, raw text for semantic encoding, existing
source filter and stable ties. Runtime offline-only loading, remote code disabled.
No commits, pushes, imported implementation or credential/model-cache staging.

## Constitution Check

| Principle | Disposition |
| --- | --- |
| One controlled change | Only optional retrieval backend changes; previous required M1 evidence remains historical |
| Fixed evaluation | All twelve questions and metric files retain starting hashes |
| Evidence first | Fresh tests, offline/Gemma baseline and two offline failures saved before specification and implementation |
| Local/simple | Embeddings computed locally with a small exact index; hosted answering was already explicitly authorized |
| Honest results | No target score promised; unchanged numeric threshold scale risk and every operational/content regression reported |
| Repository boundaries | Root src/tests/docs/specs only; no reference edits, merges, commits or cache inclusion |

Pre-research and post-design gates pass for the user's explicitly authorized
optional advanced experiment. Assignment submission/peer review are not inferred.
The required minimum excludes embeddings infrastructure; this separate optional
experiment does not amend that rule or claim to be the required change.

## Project Structure

```text
src/semantic_retrieval.py       # model identity, lazy loader, normalized encoding/cache
src/retrieval_errors.py         # operational retrieval error
src/prepare_embeddings.py       # explicit pinned model download
src/retrieval.py                # backend dispatch; preserve lexical scoring/ranking
src/config.py                   # backend/model metadata only; existing values fixed
src/cli.py                      # backend choice and readable setup failures
tests/test_semantic_retrieval.py
tests/conftest.py               # isolate test backend from a developer's .env
requirements-embeddings.txt
docs/semantic-retrieval-report.md
docs/evidence/007-semantic-retrieval/
specs/007-semantic-retrieval/    # spec, plan, research, model, contract, guide, tasks
```

## Design

`semantic_scores(query, chunks)` returns finite cosine scores aligned with eligible
chunks. Immutable ModelIdentity captures model/revision/device/cache. A one-entry
encoder cache and two-entry corpus cache are keyed by identity and exact ordered
text. Encoding validates count/dimensions/finite nonzero vectors and normalizes
them; scoring uses a stable dot product clipped only for numerical roundoff.
Metadata is never cached with vectors. Existing min-score/sort/top-k remains in
retrieval.py, so source eligibility and lexical mode remain easy to verify.

Normal runtime lazy-loads the exact local model. `python -m src.prepare_embeddings`
downloads only model.safetensors and required config/tokenizer files at the pinned
revision. Missing optional packages/cache produce actionable RetrievalError;
CLI reports errors and eval naturally stops without writing a quality result.
No silent fallback or semantic probability calibration is introduced.

## Verification

1. Write contract tests and save their preimplementation failure.
2. Implement source paths and run the suite offline with mocked encoders/provider.
3. Prepare the model explicitly, record versions/cache size, and verify real CPU
   ranking with HF_HUB_OFFLINE=1, cold/warm timings, dimensions and chunk token sizes.
4. Run semantic offline and live full evaluations with fresh outputs. Keep the
   lexical before/after reproduction control. Preserve unchanged thresholds even
   if unsupported questions receive positive cosine scores.
5. Run comparator unchanged. Inspect all generated answers and E05/E09/E06/E11
   citations against actual source text; capture independent target CLI checks.
6. Save integrity/provenance/request-rate evidence and implementation diff, update
   README/setup instructions and give a commit message while leaving work unstaged.

Hosted measurement uses 2.1-second minimum spacing across all attempts, including
retries and fallback, in the evidence wrapper only. One recovery for an interrupted
execution may use a fresh label; do not repeat completed runs to select a score.
Invalid citations remain a generation error rather than being repaired in this
retrieval experiment. No extra parameter is tuned on the twelve known questions.
