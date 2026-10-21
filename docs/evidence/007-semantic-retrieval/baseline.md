# Baseline before semantic retrieval implementation

21 October 2026, Europe/Belgrade. Commit `95657b9`, branch `feat/gemma-generation`.
All **163 tests pass**. Fresh unchanged offline evaluation gives **9/12**, matching
the retained three-chunk, stopword-filtered configuration. Original source and
historical evidence hashes are preserved in `baseline-manifest.json`.

Two concrete reproduced evaluation failures, before implementation:

| ID | Expected | Actual offline baseline | Failure type |
| --- | --- | --- | --- |
| E05 | Equipment replacement evidence and up to 5 business days | Only onboarding and annual-leave passages, no equipment hit or expected fact; answer is wrong | Lexical retrieval misses paraphrase |
| E01 | Annual-leave entitlement with relevant citations | Correct 22-day fact with two unrelated remote-work citations; precision 0.3333, FAIL | Irrelevant extra retrieval / extractive citation padding |

E11 also fails offline because annual-leave evidence is returned as an answer to a
parental-leave question. The existing hosted answerer already addresses this by
refusing. These are not claimed to be two failures of the Gemma baseline, whose
historical retained result is 11/12 with E05 as its only failing question.

The fresh hosted baseline is saved separately as `lexical-gemma-before.*`.
Prior source inspection also observed E09 prose omitting the manager-approval
timing qualification despite a passing metric; semantic retrieval is not claimed
to fix generation omissions. No scoring thresholds, prompts or question labels
are selected in response to the new experiment's results.
