# Tasks: Local semantic retrieval

**Input**: [spec.md](spec.md), [plan.md](plan.md), research/data-model/contracts.
**Tests**: User explicitly requested implementation and testing; meaningful offline
contracts precede source implementation, and real-model/live checks follow.

## Phase 1: Preserve baseline

- [X] T001 Save original tracked hashes and unchanged tests/evaluation in docs/evidence/007-semantic-retrieval/.
- [X] T002 Document E05 and E01 baseline failures before source edits in docs/evidence/007-semantic-retrieval/baseline.md.

## Phase 2: Foundational contracts

- [X] T003 Write offline encoder/cache/ranking/error contracts in tests/test_semantic_retrieval.py and preserve the failing initial run in docs/evidence/007-semantic-retrieval/.
- [X] T004 Add public embedding identity/configuration and operational retrieval errors in src/config.py and src/retrieval_errors.py; keep existing numeric values unchanged.

## Phase 3: US1 - Find paraphrased evidence

**Goal**: Original query/chunk text is locally encoded and ranked through the
existing retrieval contract. **Independent test**: controlled vectors plus E05 real
model evidence, with same source-filter and citation identity.

- [X] T005 [US1] Implement ModelIdentity and lazy encoder/corpus caches in src/semantic_retrieval.py; enforce finite, nonzero, consistently dimensioned vectors with one vector per text.
- [X] T006 [US1] Dispatch lexical/embeddings in src/retrieval.py; preserve existing minimum-score, stable order, source filter and k validation.

## Phase 4: US2 - Preserve grounding and selection

**Goal**: Existing lexical behavior and grounded-answer contract remain intact.
**Independent test**: old suite plus fake semantic results delivered to Gemma, and
unchanged lexical evaluation reproduction.

- [X] T007 [US2] Expose backend selection and readable retrieval errors in src/cli.py, document environment selection in .env.example, and isolate lexical test defaults in tests/conftest.py.
- [X] T008 [US2] Run all offline contract and existing tests; fix only demonstrated implementation failures and save logs in docs/evidence/007-semantic-retrieval/.

## Phase 5: US3 - Prepare and verify locally

**Goal**: Explicit setup yields a pinned offline model without new infrastructure.
**Independent test**: prepare then real-model run with HF_HUB_OFFLINE=1 and cache
reuse/timing inspection; missing cache/dependency paths fail clearly.

- [X] T009 [US3] Add pinned optional requirements-embeddings.txt and explicit model preparation in src/prepare_embeddings.py; restrict downloads to required safetensors/config/tokenizer files.
- [X] T010 [US3] Prepare and verify the real model offline, recording identity, vector dimensions, token lengths, cache behavior and timings in docs/evidence/007-semantic-retrieval/.
- [X] T011 [US3] Save full semantic offline/live evaluation and lexical reproduction, comparisons and target CLI evidence in docs/evidence/007-semantic-retrieval/.

## Phase 6: Review and handoff

- [X] T012 Review actual sources/answers, every regression and remaining limitation in docs/semantic-retrieval-report.md and update README.md.
- [X] T013 Verify protected artifacts, all settings, request pacing and uncommitted scope in docs/evidence/007-semantic-retrieval/; provide the user a commit message without committing or pushing.

## Dependencies and execution

T001-T002 -> T003 -> T004-T006 -> T007-T008 -> T009-T011 -> T012-T013.
US1 is the minimal new behavior. US2 preserves the existing interface; US3 makes
setup and actual verification reproducible. Independent test assertions within
each story can run together in pytest; files are implemented sequentially here.
No parallel implementation agent is needed; the planning skill's read-only research
agent has completed its assignment. User instructions override template advice to
commit after tasks: all changes remain uncommitted.

## Measured disposition

195 tests pass. Full semantic offline evaluation completed at 9/12, with E01/E05
fixed and E07/E10 regressed. Both full semantic live attempts stopped at E09's
existing inline-citation format validator, so T011 records explicit operational
failures under SC-002's exception rather than a complete aggregate score. The
independent E05 answer and unsupported CLI refusals are verified. The raw E09
diagnostic identifies the grouped inline marker; no validator/prompt repair is
bundled. Both lexical controls reproduce exact result rows and summaries.
