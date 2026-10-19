# Grounded Gemma implementation and verification

Date: 2026-10-20. Branch: `feat/gemma-generation`.

The optional answerer is implemented and live-verified: the controlled lexical
comparison improves **10/12 → 11/12**, fixing **E11**, with **no PASS-to-FAIL
regressions**. Mean citation precision improves **0.65 → 1.00**. All 12 saved
answers were reviewed against their retrieved sources; E05 remains a retrieval
miss. Vedran's embeddings are not part of this branch. Required M1 evidence and
historical optional experiments remain separate. Submission, independent peer
review and demonstration ownership are not asserted.

## Problem and one intentional change

The original answerer prints retrieved chunks as an answer, even when they only
share a topic with the question. E11 asks for parental-leave policy but receives
annual-leave text; E05 retrieves unrelated onboarding/leave passages instead of
equipment-replacement evidence. The unchanged [baseline](evidence/005-gemma/baseline.md)
records both failures before runtime edits.

The change is an opt-in grounded answering policy: send the question and all
retrieved chunks as labeled text to Gemma, then validate an answer or evidence
refusal. It does not load embeddings, rank evidence, change thresholds, enable M2
or modify the fixed evaluation. Missing retrieval evidence still cannot be supplied
by the answerer. E11's pre-existing hypothesis was confirmed in this saved live run.

## Implementation

- Root `.env.example` contains a blank key and offline default. Root `.env` loading
  respects process values and disables interpolation; local secret files are ignored.
- The Google REST client targets configurable `gemma-4-26b-a4b-it`, authenticates
  through a private header, rejects redirects, makes one request without retries,
  and sanitizes transport/provider errors.
- Initial settings: temperature 0, output cap 1024, minimal thinking, 30-second
  socket timeout; application input budget is 65,536 UTF-8 bytes including prompt
  and request structure. No context is silently dropped. The output-token control
  accepts 1-8192; that application bound does not establish model capability.
- Prompt-requested JSON is locally validated: exact fields/types, nonempty answer
  and supporting IDs, strict refusal fields, unique valid citation IDs and matching
  inline citations. Native schema support is not assumed.
- Retrieval and its existing score gate remain intact. Local refusals skip the API.
  API failures, blocked/truncated output and invalid decisions are execution errors,
  never successful evidence refusals. The unchanged evaluator stops on them.
- Optional same-run JSONL traces preserve answers, source IDs/scores, decisions,
  durations and available token usage. A new process cannot append to old evidence.
  Public config includes provider/model/settings/prompt hash; key and trace path do not.

Transport/model design follows Google's [Gemma hosting guide](https://ai.google.dev/gemma/docs/core/gemma_on_gemini_api)
and [REST reference](https://ai.google.dev/api/generate-content). These document
interfaces; actual access and response handling are verified by the saved live runs.
Environment loading
uses pinned `python-dotenv==1.2.4`; see [dotenv documentation](https://bbc2.github.io/python-dotenv/).

Live setup exposed an overly strict local key-format check: it accepted only
letters, digits, underscores and hyphens, rejecting newer dotted authorization
keys. The fix treats keys as opaque printable ASCII header values, while rejecting
whitespace, control characters and non-ASCII. Seven new regression cases cover
both key formats and unsafe header characters. Google's [key documentation](https://ai.google.dev/gemini-api/docs/api-key)
describes the transition to authorization keys. No key value was added to code,
tests, logs, snapshots or commits.

## Controlled live result

The two synthetic non-eval capability cases passed before measurement. The
[frozen protocol](evidence/005-gemma/live/protocol.md) and
[manifest](evidence/005-gemma/live/run-manifest.json) record the model/settings and
runtime hashes. The prompt was not tuned against the fixed questions.

| Metric | Extractive | Gemma |
| --- | --- | --- |
| Passed | 10/12 | 11/12 |
| Behavior accuracy | 0.9167 | 0.9167 |
| Retrieval hit rate | 0.8889 | 0.8889 |
| Mean citation precision over answered questions | 0.65 | 1.00 |
| Fixed / regressed questions | — | E11 / none |

The complete [before](evidence/005-gemma/live/before.json) and
[after](evidence/005-gemma/live/after.json) use the same evaluation hash and identical
retrieved chunk IDs/scores for every question. The
[comparison](evidence/005-gemma/live/comparison.txt) reports only
`ANSWER_BACKEND: extractive → gemma`, with no multi-setting warning.

E11 now refuses instead of answering a parental-leave question with annual-leave
evidence. E05 still fails: the required equipment evidence is absent from retrieved
context. It changes from an incorrect answer to a refusal, so behavior accuracy
does not improve even though E11 and overall pass count improve. There is no
PASS-to-FAIL regression, but E05's changed behavior remains an explicit limitation.

Citation precision improves through selective citations and refusing unsupported
contexts; its denominator changes from ten answered questions to eight. This is
not a claim that retrieval improved. Inspecting the
[same-run answer trace](evidence/005-gemma/live/after-answers.jsonl) against the cited
passages found no unsupported claims or omitted requested details among the eight
generated answers in this run. The [review of all 12 cases](evidence/005-gemma/live/manual-review.md)
explicitly checks E09's IT portal/Hardware location and approval-qualified deadline.
That Codex review is separate from the assignment's independent peer review.

The [E11 CLI check](evidence/005-gemma/live/E11-cli.txt) reproduced the corrected
refusal and showed the annual-leave context. The
[live audit](evidence/005-gemma/live/verification.json) checks the fixed comparison,
all answer records and runtime hashes. Evaluation made ten Google requests and two
local refusals. Google returned 4,534 input and 426 output tokens (4,960 total) for
the evaluation; mean remote answer latency was 1.746 seconds, range 1.133-2.549.
Including the two synthetic probes and one CLI check, there were 13 successful
Google requests and 6,223 returned total tokens. A sandbox-blocked attempt is
preserved separately and is not a successful provider request. Provider billing
was not audited; no billing configuration or model substitution was performed.

## Offline compatibility and tests

| Check | Before | After implementation |
| --- | --- | --- |
| Full pytest suite | 53/53 | 134/134 |
| Offline fixed eval | 10/12 | 10/12 |
| PASS-to-FAIL regressions | — | None |
| Per-question rows, including retrieval/scores | Preserved | Exactly equal across all 12 |
| Original configuration values | Preserved | All equal, including M2=False |
| Same-run offline answer records | — | 12 |
| Protected baseline file hashes | Captured | 35 unchanged |
| Live measured pass count | Not run | 11/12; separate controlled pair above |

Evidence:

- [Unchanged eval](evidence/005-gemma/original-before.json) and [retained offline eval](evidence/005-gemma/retained-extractive.json).
- [Comparison output](evidence/005-gemma/comparison-extractive.txt) and [actual answer trace](evidence/005-gemma/retained-answers.jsonl).
- [Baseline tests](evidence/005-gemma/pytest-before-unsandboxed.txt), [failing contract-test collection before code](evidence/005-gemma/pytest-red.txt), and [initial implementation tests, 127/127](evidence/005-gemma/pytest-after.txt). The [subsequent key-format compatibility suite](evidence/005-gemma/live/test-results.md) passes 134/134.
- [Hash/equivalence verifier](evidence/005-gemma/verify.py) and [verification output](evidence/005-gemma/verification.json).
- [Initial implementation diff](evidence/005-gemma/implementation.diff) and [key-format compatibility diff](evidence/005-gemma/live/key-format.diff).

The original-versus-retained comparison reports multiple added configuration keys.
Those describe the optional answering backend, including its frozen prompt. They
are additions rather than simultaneous retrieval improvements. Every original
setting, result row and summary remains equal. For the controlled live pair,
both runs use the new code/config schema; only `ANSWER_BACKEND` changes.

The initial sandbox pytest attempt had a temp/cache permission error; normal temp
access passed all tests. The initial 127-test completion run intentionally set Gemma in the process
environment with a dummy key; fixtures forced offline defaults and blocked every
unmocked HTTP request. This verifies test isolation, not live behavior. The original
53 tests, evaluation questions, metric calculations and preserved starter remain unchanged.
Actual virtual-environment Python is 3.13.7; no interpreter upgrade was performed.

## Remaining verification and limitations

The synthetic [live probe](evidence/005-gemma/live_probe.py), frozen lexical
comparison, all-answer source review and changed-case CLI check are complete.
After Vedran's separately measured embeddings are available, compare extraction
   versus Gemma with exactly that embedding configuration. Attribute retrieval and
   generation changes separately; do not tune thresholds during the LLM comparison.

E05 remains unresolved; 12/12 is not claimed. E11 is fixed in this measured run,
which does not guarantee later responses or unseen questions. Valid IDs alone do not prove that
the text supports each claim. Existing metrics check facts in cited passages and
can miss invented prose, omitted details or a wrong final answer; manual review
must check those, particularly E09's request location and deadline. The score gate
still prevents generation on low-scoring evidence. Future embedding thresholds
must be resolved as part of that separate experiment. Remote capacity, rate limits,
malformed JSON and model variability remain dependencies even with a free key.

## AI usage and contributions

Codex read the design and assignment, generated tasks and tests, implemented the
optional adapter, and ran the preserved commands and hash checks. Verification is
the saved execution evidence; mocked tests are not model-quality evidence. The
user selected Google/Gemma and authorized this branch's implementation. Vedran
owns future embedding work; this report does not claim it is complete or included.
Codex reviewed all measured answers against their sources. Independent human/peer
review and demonstration contributions remain pending.
