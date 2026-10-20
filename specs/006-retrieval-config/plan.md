# Plan: Verify the committed retrieval configuration

Date: 2026-10-21. Branch: `feat/gemma-generation`.

This is a small retrospective follow-up to user commit `f108726`, whose parent is
`b55b320`. Runtime settings are already implemented. Use the existing Python
virtual environment, pytest, evaluator, comparator and CLI from repository root.

## Scope and governance

Keep TOP_K=3 and STOPWORDS_ENABLED=True. Correct the stale stopword comment only.
Do not alter scoring, corpus, chunking, prompt, models, retry policy, thresholds,
evaluation data or metric code. No embeddings, branch merges or code imports.
Do not reinterpret the two settings as the required one-change homework. The
specification is retrospective; earlier M1 and optional experiment evidence stays
unchanged. No peer review, learner work or submission is invented.

## Execution

1. Save a manifest of starting Git identity and hashes, the parent config, and an
   unchanged copy of `results/manualLLM.json` under a fresh evidence directory.
2. Run the suite on parent settings in process memory and on committed defaults.
   If default-dependent tests fail, pin only the settings those tests require.
3. Add a small evidence driver under `docs/evidence/006-retrieval-config/` which
   invokes the unchanged module entry points in subprocesses. Config overrides
   affect only each child process; never rewrite src/config.py to measure a mode.
4. Run the four combinations in order: two/off, three/off, two/on, three/on. Run
   offline first and then Gemma. Set the answering mode explicitly for each child;
   use fresh JSONL trace paths, never append to historical evidence.
5. Compare parent -> retained plus one-setting edges using `src.eval_compare`.
   Preserve the multi-setting warning on the parent -> retained comparison.
6. Inspect all actual hosted answers against cited chunk texts. Use the existing
   CLI for retained E09 and E05, preserving independent actual traces and console.
7. Report observations, latency/usage/actual models, regressions and limitations.
   Verify protected hashes, snapshots, all twelve question IDs and trace alignment.
8. Run the final suite if tests change, review the staged diff and amend only the
   explicitly selected files. Do not push or stage caches / reference folders.

## Artifacts

- `specs/006-retrieval-config/{spec,plan,tasks}.md` and quality checklist.
- `docs/evidence/006-retrieval-config/`: manifest, original configuration, user run,
  driver, tests, eight result/trace/console sets, comparisons and CLI evidence.
- `docs/retrieval-config-report.md`: measured findings and retained-state decision.
- `src/config.py`: accurate explanatory comment; same configuration values.
- Existing tests: only if baseline-specific assumptions need explicit settings.

No new unit tests are planned: existing retrieval, grounding, current-source,
all-stopword and request-contract tests cover the behavior. Full evaluations and
source inspection provide the relevant evidence for the configuration choices.

## Verification boundaries

Use fixed settings regardless of measured score. No repeated score-seeking runs.
An unavailable provider is recorded as a failed execution and does not substitute
an offline score for Gemma quality. Network access can use the ordinary sandbox
approval path if necessary. Traces preserve actual model and fallback attempts.
Known-set results and one live run per mode do not establish generalization or
determinism, even at temperature zero. Citation precision is document-level, and
the fact check searches citation text rather than the generated answer.

## Live approval and request limit

After automatic review rejected network execution, the user explicitly approved
sending the fixed questions, grounding prompt and up to three sample handbook
chunks per question to Google's existing Gemini API, and specified a maximum of
30 Gemma requests per minute. The evidence helper spaces all transport attempts
by at least 2.1 seconds across sequential subprocesses, including retries and
fallback. Hosted module entry points run through this process-local wrapper;
production code and experimental snapshots do not change. Audit the request-start
log and record that timing includes intentional pacing.

## Final disposition

All four configurations were attempted for each answerer. Seven complete runs
were saved. Hosted three/off failed inline-citation validation at E09, including
one recovery attempt; preserve both failures and leave its comparisons unavailable.
The retained hosted run reproduces 11/12, and offline regresses 10/12 to 9/12.
The report records the omitted E09 approval qualification and all other findings.
No further tuning or scoring/prompt/validator implementation is part of this step.
