# Grounded Gemma implementation and verification

Date: 2026-10-20. Branch: `feat/gemma-generation`.

The optional answerer is implemented and verified offline. **Live Gemma quality
is not measured**: no local key exists yet, and Vedran's embeddings are not part
of this branch. Required M1 evidence and historical optional experiments remain
separate. Submission, peer review and demonstration ownership are not asserted.

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
by the answerer. E11 improvement is a hypothesis until measured live.

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
interfaces, not successful access with this user's future key. Environment loading
uses pinned `python-dotenv==1.2.4`; see [dotenv documentation](https://bbc2.github.io/python-dotenv/).

## Actual checks

| Check | Before | After implementation |
| --- | --- | --- |
| Full pytest suite | 53/53 | 127/127 |
| Offline fixed eval | 10/12 | 10/12 |
| PASS-to-FAIL regressions | — | None |
| Per-question rows, including retrieval/scores | Preserved | Exactly equal across all 12 |
| Original configuration values | Preserved | All equal, including M2=False |
| Same-run offline answer records | — | 12 |
| Protected baseline file hashes | Captured | 35 unchanged |
| Live requests / measured model quality | Not run | Not run; key absent |

Evidence:

- [Unchanged eval](evidence/005-gemma/original-before.json) and [retained offline eval](evidence/005-gemma/retained-extractive.json).
- [Comparison output](evidence/005-gemma/comparison-extractive.txt) and [actual answer trace](evidence/005-gemma/retained-answers.jsonl).
- [Baseline tests](evidence/005-gemma/pytest-before-unsandboxed.txt), [failing contract-test collection before code](evidence/005-gemma/pytest-red.txt), and [final tests](evidence/005-gemma/pytest-after.txt).
- [Hash/equivalence verifier](evidence/005-gemma/verify.py) and [verification output](evidence/005-gemma/verification.json).
- [Implementation diff](evidence/005-gemma/implementation.diff).

The original-versus-retained comparison reports multiple added configuration keys.
Those describe the optional answering backend, including its frozen prompt. They
are additions rather than simultaneous retrieval improvements. Every original
setting, result row and summary remains equal. For the later controlled live pair,
both runs use the new code/config schema; only `ANSWER_BACKEND` changes.

The initial sandbox pytest attempt had a temp/cache permission error; normal temp
access passed all tests. The final run intentionally set Gemma in the process
environment with a dummy key; fixtures forced offline defaults and blocked every
unmocked HTTP request. This verifies test isolation, not live behavior. No existing
test, evaluation question, metric calculation or preserved starter was edited.
Actual virtual-environment Python is 3.13.7; no interpreter upgrade was performed.

## Remaining verification and limitations

1. Add the key locally, run the two-case synthetic [live probe](evidence/005-gemma/live_probe.py),
   verify model/settings/JSON behavior, and freeze the prompt before fixed evaluation.
2. Run extraction versus Gemma with identical frozen lexical retrieval; save full
   eval outputs, comparison, same-run traces and manual review of all 12 answers.
3. After Vedran's separately measured embeddings are available, compare extraction
   versus Gemma with exactly that embedding configuration. Attribute retrieval and
   generation changes separately; do not tune thresholds during the LLM comparison.

No 12/12 result or E11 fix is claimed. Valid citation IDs alone do not prove that
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
Human answer review, peer review and demonstration contributions remain pending.
