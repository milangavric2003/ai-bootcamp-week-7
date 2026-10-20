# Retrieval configuration verification

Date: **21 October 2026**, Europe/Belgrade. Branch: `feat/gemma-generation`.

The user selected and committed `TOP_K=3` and `STOPWORDS_ENABLED=True` in
`f108726`, then requested verification and amendment of that commit. Those values
are retained. `RETRIEVAL_MIN_SCORE=0.01`, `REFUSAL_THRESHOLD=0.10`, source filtering,
chunking, models, prompt and retry/fallback policy remain unchanged.

This is retrospective verification of an optional **two-setting** follow-up, not
the required single-change M1 homework. The [specification](../specs/006-retrieval-config/spec.md)
and [plan](../specs/006-retrieval-config/plan.md) were written after the user's
configuration commit and before the verification edits. The known evaluation set
informed the user's choice. These results are exploratory, not held-out accuracy.

## Preserved starting point and actual edits

Evidence directory: [006-retrieval-config](evidence/006-retrieval-config/).
The [starting manifest](evidence/006-retrieval-config/starting-manifest.json) records
the original commit, parent `b55b320`, interpreter and existing tracked-file hashes.
The [parent config](evidence/006-retrieval-config/parent-config.py.txt) preserves
TOP_K=2 / stopwords=False. The [user's unchanged saved run](evidence/006-retrieval-config/user-manualLLM.json)
records **11/12**, citation precision **1.0**, at the retained settings. Its original
`results/manualLLM.json` is preserved; it is not relabeled as a new assistant run.

The user's two value changes were already implemented. Verification only:

- corrects the stale comment saying stopword filtering is disabled;
- removes `assert config.STOPWORDS_ENABLED is False` from the credential-privacy
  test, whose assertions excluding secrets and trace paths remain unchanged;
- adds measurement orchestration, documentation and actual outputs.

No embedding code, merges, new dependencies, metric changes, stopword-vocabulary
changes or further parameter tuning are included. Cache and reference folders are
excluded from staging. The [implementation diff](evidence/006-retrieval-config/implementation.diff)
records existing-file edits against the pre-config parent.

## Initial observed failures

The prior offline pipeline has two reproduced failures:

| Question | Expected | Actual with old offline settings | Failure type |
| --- | --- | --- | --- |
| E05 | Equipment policy, up to 5 business days | Onboarding/annual-leave context; no equipment document or deadline | Retrieval miss / wrong answer |
| E11 | Refuse unsupported parental-leave policy | Annual-leave passages returned as an answer | Insufficient grounding / wrong answer |

The preceding Gemma run already addresses E11; it has only E05 as a fixed-eval
failure. These are not described as two failures of that Gemma baseline.
The earlier [M2 report](m2-report.md) also documents the E09 deadline loss when
filtering is on with TOP_K=2; the new offline run reproduces it.

Hypothesis for this verification: increasing context to three restores E09's
deadline when filtering is enabled. Filtering changes ranking but cannot connect
notebook/computer with laptop. Extra context may dilute citations or mislead an
answerer; actual generated answers require separate inspection.

## Tests

Python **3.13.7**, pytest **8.3.3**, project virtual environment, repository root.

- [Parent settings](evidence/006-retrieval-config/pytest-parent.txt): **163 passed**.
- [Committed defaults before the test correction](evidence/006-retrieval-config/pytest-current.txt):
  **162 passed, 1 failed**, solely the obsolete disabled-stopwords assertion.
- [Final suite](evidence/006-retrieval-config/pytest-final.txt): **163 passed**.

The first parent test attempt encountered Windows temp-directory access errors;
these are environment errors, not RAG failures. A first workspace-temp attempt
also exposed a missing parent-directory creation in the new evidence helper.
Both failed logs are retained. The helper now creates the parent, uses a fresh
workspace-local pytest basetemp and disables pytest's cache provider. These are
test invocation choices, not application changes. No new constant-value tests
were added.

## Four-configuration offline measurement

Every row uses the existing `src.eval_runner` entry point and the complete fixed
twelve questions. Configuration overrides exist only in individual child-process
memory; the application file is not rewritten between measurements. The retained
combination uses the ordinary `python -m src.eval_runner --out ...` invocation.

| TOP_K | Stopwords | Passed | Behaviour | Retrieval hit | Mean citation precision |
| --- | --- | --- | --- | --- | --- |
| 2 | False | 10/12 | 0.9167 | 0.8889 | 0.6500 |
| 3 | False | 8/12 | 0.9167 | 0.8889 | 0.5667 |
| 2 | True | 9/12 | 0.9167 | 0.8889 | 0.7000 |
| 3 | True, retained | 9/12 | 0.9167 | 0.8889 | 0.6333 |

Full results: [before](evidence/006-retrieval-config/extractive-before.json),
[top-k only](evidence/006-retrieval-config/extractive-topk-only.json),
[stopwords only](evidence/006-retrieval-config/extractive-stopwords-only.json),
[retained](evidence/006-retrieval-config/extractive-after.json). Each has an actual
console log and aligned answer trace in the same directory.

The [combined comparison](evidence/006-retrieval-config/extractive-compare-before-to-after.txt)
reports **E01 regression**, no fixed questions, 10/12 to 9/12, and citation
precision 0.6500 to 0.6333. It correctly warns that two settings changed; that
warning is preserved. The individual comparisons show:

- [TOP_K alone](evidence/006-retrieval-config/extractive-compare-before-to-topk-only.txt):
  E01 and E08 regress because only one of three cited chunks belongs to the
  expected document; precision drops below the fixed 0.5 pass threshold.
- [Stopwords alone](evidence/006-retrieval-config/extractive-compare-before-to-stopwords-only.txt):
  E09 regresses because its deadline falls outside the two selected chunks.
- [TOP_K after filtering](evidence/006-retrieval-config/extractive-compare-stopwords-only-to-after.txt):
  E09 is repaired but E01 regresses; the equal 9/12 totals hide this tradeoff.
- [Filtering at TOP_K=3](evidence/006-retrieval-config/extractive-compare-topk-only-to-after.txt):
  E08 recovers, with no new pass-to-fail regression on that edge.

Other citation changes from old to retained offline settings are E02 0.5 to 1.0,
E03 1.0 to 0.6667, E07 1.0 to 0.6667, and E08 0.5 to 0.6667. E04/E06/E09 stay
at 1.0. E05 and E11 remain wrong offline answers with zero citation precision.
No offline answer/refusal decisions change. The retained offline mode therefore
must not be claimed to improve overall evaluation quality.

The retained [E09 CLI check](evidence/006-retrieval-config/offline-e09-cli.txt)
shows `hb-01-chunk-0` (0.285714), request route `hb-01-chunk-2` (0.25), and
deadline `hb-01-chunk-1` (0.15), in that order. The third passage restores the
complete deadline without changing the tokenizer or threshold. The
[E05 CLI check](evidence/006-retrieval-config/offline-e05-cli.txt) still shows only
onboarding and annual-leave passages; the extractive answer is wrong.

The [offline integrity check](evidence/006-retrieval-config/offline-verification.json)
confirms all four complete runs and their twelve-row traces align, every other
setting is fixed within the backend, historical tracked artifacts are preserved,
and the retained retrieval IDs/scores exactly match the user's saved hosted run.
The local credential scan found no credential in the saved artifacts.

## Fresh hosted measurements

The user explicitly approved the sample payload and Google destination, requiring
at most 30 Gemma requests per minute. See the [live protocol](evidence/006-retrieval-config/live-protocol.md)
for approval scope, the earlier blocked attempt, and measurement-only request pacing.

| TOP_K | Stopwords | Passed | Behaviour | Retrieval hit | Mean citation precision |
| --- | --- | --- | --- | --- | --- |
| 2 | False | 11/12 | 0.9167 | 0.8889 | 1.0000 |
| 3 | False | No completed score: citation validation error | — | — | — |
| 2 | True | 10/12 | 0.9167 | 0.8889 | 1.0000 |
| 3 | True, retained | 11/12 | 0.9167 | 0.8889 | 1.0000 |

Fresh complete results: [before](evidence/006-retrieval-config/gemma-live-before.json),
[stopwords only](evidence/006-retrieval-config/gemma-live-stopwords-only.json),
[retained](evidence/006-retrieval-config/gemma-live-after.json). Each has actual
same-run text, citations, models and attempts in its adjacent `*-answers.jsonl`.
The preserved user result is an independent earlier execution; the new retained
run reproduces its score without being a copy.

The [combined comparison](evidence/006-retrieval-config/gemma-live-compare-before-to-after.txt)
reports **11/12 to 11/12**, unchanged metrics and no PASS-to-FAIL regressions. It
retains the two-setting warning. [Filtering with two chunks](evidence/006-retrieval-config/gemma-live-compare-before-to-stopwords-only.txt)
regresses E09: its answer gives the request route but explicitly says the retrieved
evidence lacks the timeline. [Adding the third chunk with filtering on](evidence/006-retrieval-config/gemma-live-compare-stopwords-only-to-after.txt)
restores E09, 10/12 to 11/12, with no PASS-to-FAIL regressions on that edge.
The data supports using three chunks when enabling filtering; it does **not**
establish that the retained configuration improves over the old Gemma baseline.

The TOP_K=3 / stopwords=False measurement stopped at E09 with
`InvalidResponseError: Gemma inline citations must match the selected source IDs.`
One explicitly documented recovery execution stopped at the same question with
the same error. Both original and recovery traces and console logs are retained;
neither produced a complete result JSON. No further retries, settings changes or
validator changes were made. Two comparisons involving that mode are marked
unavailable, not assigned an inferred score. A provider transport success followed
by an invalid answer contract is an operational failure, not a correct refusal or
a completed quality evaluation. The invalid raw response is not retained by the
existing adapter, so no unsupported diagnosis of its exact formatting is claimed.

## Actual answer and source inspection

Codex inspected all text in the three completed hosted evaluations (36 question
records), the eight successful prefix answers in each interrupted run, and the two
CLI records against the actual source chunks. This is an assistant source review,
not the assignment's independent human peer review.

| ID | Source check across completed runs | Finding |
| --- | --- | --- |
| E01 | hb-07-chunk-0: 22 annual-leave days per calendar year | Supported; only relevant citation selected |
| E02 | hb-05-chunk-0: passwords every 90 days | Supported |
| E03 | hb-08-chunk-0: 800 EUR yearly for courses, conferences and certifications | Supported |
| E04 | hb-01-chunk-1: up to 5 business days after manager approval | Supported; approval qualification retained in all three runs |
| E05 | Retrieved onboarding/annual leave, no equipment source | Refusal honest about context; still a supported-question FAIL |
| E06 | hb-03-chunk-0: up to 3 remote days weekly | Supported current policy, no superseded source |
| E07 | hb-10-chunk-0: 08:00 to 18:00 Monday-Friday | Supported |
| E08 | hb-04-chunk-0: within 30 days of return via finance app | Supported |
| E09 | hb-01-chunk-2: IT portal / Hardware; hb-01-chunk-1: timeline | Baseline complete; filtering with two chunks misses deadline; retained restores route and deadline but drops the approval timing qualification from prose |
| E10 | No company stock-price evidence | Correct local refusal, no API call |
| E11 | Annual leave does not establish parental leave | Correct model refusal, no citations |
| E12 | No football evidence | Correct local refusal, no API call |

The retained [E09 hosted CLI check](evidence/006-retrieval-config/gemma-e09-cli.txt)
also gives route and deadline with the right sources, and also omits "after manager
approval" from the prose. That qualification is in the cited source. This is an
observed content limitation relative to the baseline despite identical fixed
metrics; a single pair of runs cannot attribute it confidently to the config
rather than model behavior. No prompt change is bundled to hide it. The retained
[E05 hosted CLI check](evidence/006-retrieval-config/gemma-e05-cli.txt) again refuses
with no equipment evidence or citations.

## Integrity, request rate and usage

The [final verification](evidence/006-retrieval-config/verification.json) checks all
seven complete twelve-question runs and traces, both interrupted hosted attempts,
protected existing files, unchanged settings except the two controlled choices,
and the original user's unchanged result/retrieval. Eval fingerprint throughout:
`afe46db1e75a0b85bb5c9a93b6763e3b96e5cd7b289e12da6d2671e4d8650064`.
All 293 previously tracked files are protected, with only the authorized README,
config comment and privacy-test changes allowed. Fixed metrics and questions match
their starting hashes; no local credential was found in saved artifacts.

The request-start log records **50 live transport attempts**, including both
interrupted prefixes and CLI checks. The minimum spacing is **2.10006 seconds**;
the highest count in any rolling minute is **22**, below the user's limit of 30.
All 50 used `gemma-4-26b-a4b-it`; none used fallback or needed a transport retry.
The failed preapproval sandbox attempt is separate and did not complete a request.
Reported trace usage totals **25,592 tokens** (23,530 prompt + 2,062 output), with
about **104.8 seconds** summed trace time including pacing. Invalid-decision traces
do not retain response usage, so the token total excludes those two responses and
is not a complete billing total. No billing-cost amount is inferred.

## Remaining limitations and next step

- E05 still misses the equipment source with every lexical configuration measured
  here. Future embeddings work should target that evidence gap and be implemented
  fresh on this branch as requested; none has started in this change.
- The evaluation checks expected facts in citation text and document-level citation
  relevance. It does not check generated prose or both parts of E09 automatically.
- Extra retrieved material can hurt extractive citation precision. The hosted
  answerer selected supporting citations in the completed runs, but this behavior
  is not guaranteed on later questions or model versions.
- The top-k-only mode failed the inline-citation contract twice. The retained E09
  prose omitted the manager-approval timing qualification even though fixed metrics
  passed. These limitations remain visible for later work.
- Known-set tuning and a single live run per combination would not prove robustness
  to new phrasings or guarantee future hosted-model behavior.

The retained state is a measured Gemma baseline for the next experiment, with
E05 still open. Keep its offline regression visible whenever using extractive mode.
No further configuration selection follows these measurements.

The user chose the configuration, authorized live calls and amendment of their config commit.
Codex created the retrospective specification, ran the checks and recorded the
evidence. This is not independent human peer review or confirmation of submission.

## Reproduction

Use a fresh evidence directory or fresh labels; the helper refuses to replace
existing outputs or traces. From the repository root:

```powershell
.\.venv\Scripts\python.exe docs/evidence/006-retrieval-config/run.py pytest --label pytest-new-check
```

For a fresh ordinary run at retained settings, choose an explicit backend and new
filenames. For example, offline:

```powershell
$env:ANSWER_BACKEND = 'extractive'
$env:GEMMA_TRACE_PATH = 'results/config-offline-new-answers.jsonl'
.\.venv\Scripts\python.exe -m src.eval_runner --out results/config-offline-new.json
.\.venv\Scripts\python.exe -m src.eval_compare docs/evidence/006-retrieval-config/extractive-before.json results/config-offline-new.json
```

The matrix driver's child-process bootstrap and the exact command, backend, trace
path, timestamps and exit code for each execution are saved in the adjacent
`*-execution.json` files. Process environment settings above affect later commands
in that shell until cleared or changed.
