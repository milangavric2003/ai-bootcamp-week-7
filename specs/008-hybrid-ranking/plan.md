# Implementation Plan: Optional hybrid retrieval

**Branch**: `008-hybrid-ranking` | **Date**: 2026-10-20 | **Spec**: [spec.md](spec.md)

**Input**: User-approved hybrid experiment to restore E09 completeness.

## Summary

Add opt-in `hybrid` retrieval using semantically anchored reciprocal rank fusion.
Retain the leading semantic candidate first, then fill remaining slots from
equal-weight fusion of complete lexical and semantic rankings. This is one ranking
policy. Preserve the default lexical backend and the existing two modes.

Plain RRF loses E05's deadline in the saved planning diagnostic (11/12 predicted).
The anchor preserves that semantic match (12/12 predicted), with a secondary
citation tradeoff: predicted mean precision 0.8333 versus embeddings 0.9444.
These diagnostics do not replace actual before/after pipeline measurements.

## Technical Context

**Language/Version**: Python; project venv Python 3.13.7.
**Primary Dependencies**: Existing standard library, pytest 8.3.3, optional
sentence-transformers 6.1.0 and pinned cached all-MiniLM-L6-v2.
**Storage**: In-memory chunks/vectors; existing model cache and JSON evidence.
**Testing**: Controlled-score offline tests and full actual-model evaluation.
**Target Platform**: Existing Windows PowerShell environment.
**Project Type**: Local Python CLI.
**Performance Goals**: One semantic scoring call per query; reuse vector cache.
**Constraints**: No downloads, dependencies, threshold tuning, corpus edits,
metric edits, query rewriting, chunking changes, or generation changes.
**Scale/Scope**: Rank all eligible candidates in the existing small handbook.

## Constitution Check

Before research: PASS. Saved 86-test baseline, complete embeddings and lexical
runs, source hashes, two failures, and specification precede pipeline edits.
This optional ranking experiment is separate from the required M1 experiment.

After design: PASS. Preserve fixed eval and metric modules, sources, reference
directories, and historical evidence. The answering edit only adapts confidence
handling to a new score scale using the unchanged semantic threshold. Report all
regressions, including secondary citation quality. No extension hooks are installed.
Independent peer review remains distinct from Codex implementation and checks.

## Project Structure

```text
specs/008-hybrid-ranking/
  spec.md, plan.md, research.md, data-model.md, quickstart.md, tasks.md
  checklists/requirements.md
  contracts/retrieval.md
src/config.py        # Recorded RRF constant
src/retrieval.py     # Hybrid ranking and optional raw semantic score
src/rag.py           # Hybrid semantic confidence gate
src/cli.py           # Explicit mode selection and score diagnostics
tests/test_hybrid.py # Offline behavior, edge, and refusal contracts
docs/hybrid-report.md
docs/evidence/008-hybrid-ranking/
```

**Structure Decision**: Extend existing local modules; no new pipeline or framework.

## Design

1. Filter current sources before scoring. Blank/empty inputs return no results.
2. Compute existing lexical and cosine scores over the same eligible chunks.
3. Independently filter each component with `RETRIEVAL_MIN_SCORE`; sort by
   descending raw score and chunk ID. Keep complete rankings, not just TOP_K.
4. For the union, sum `1 / (60 + one_based_rank)` per ranking membership. Missing
   membership contributes zero. Resolve fused ties by chunk ID.
5. Select the leading semantic candidate as anchor, then fill remaining requested
   slots by fused rank excluding the anchor. With no semantic candidate, use the
   lexical union; semantic confidence will normally refuse. Do not reapply the
   component raw-score minimum to fused scores.
6. Append `semantic_score: float | None = None` to `RetrievalResult`. Hybrid
   `.score` remains pure RRF; `.semantic_score` is original cosine even when below
   the semantic retrieval minimum. Anchor-first output need not descend by RRF.
7. Use maximum selected cosine and existing `EMBEDDING_REFUSAL_THRESHOLD=0.51`
   for hybrid refusal. Missing semantic confidence fails closed. Neither lexical
   overlap nor relative rank authorizes an answer. Existing modes stay unchanged.
8. Add `hybrid` to CLI choices; label RRF and semantic scores under
   `--show-retrieved`. Record `HYBRID_RRF_CONSTANT=60` in snapshots. Backend
   `hybrid` identifies this fixed anchored policy; no weight or depth tuning.

## Verification

Write offline tests before code for E09 completeness and E05 anchor retention
using actual handbook text with controlled semantic scores. Cover k=1, full
rankings, component-only candidates, ties, raw/fused scale separation, filtering
before encoding, empty inputs, error propagation, CLI selection, and refusal edges.

Run full pytest with fresh `.cache/` basetemp and cacheprovider disabled. Run the
unchanged full eval runner for hybrid, embeddings, and lexical; compare each with
its saved baseline using `src.eval_compare`. Save answer text and CLI evidence.
Inspect E09 completeness, E05 paraphrase support, E07 secondary evidence, and
E10/E11/E12 refusals. Review all supported answers for changed citations.

Expect E01/E05 may gain irrelevant secondary evidence; report rather than bundle
another fix. Recheck protected hashes, source diff, and task completion.
