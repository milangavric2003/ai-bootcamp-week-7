# Gemma implementation baseline

Date: 2026-10-20. Starting commit: `392652e`, branch `feat/gemma-generation`.
The specification and plan were committed before this baseline and runtime edits.
This is explicitly requested optional advanced work; required-minimum submission
and peer-review completion have not been confirmed here.

The unchanged pipeline passes **53/53 tests**, and the complete fixed evaluation
passes **10/12**. Actual project Python is **3.13.7**, although README setup targets
3.12. No interpreter or tooling upgrade is included in this feature.

The first sandbox test attempt had 52 passes and one temp-directory permission
error; the identical tests with normal temp access pass. Preserve both logs.

| ID | Expected | Actual unchanged output | Failure type |
| --- | --- | --- | --- |
| E05 | Equipment replacement with `5 business days` in cited evidence | Onboarding hb-06-chunk-0 (0.25) and annual-leave hb-07-chunk-1 (0.111111); expected fact absent, precision 0 | Retrieval vocabulary mismatch |
| E11 | Refuse a parental-leave question without evidence | Answers with annual-leave hb-07-chunk-1 (0.222222) and hb-07-chunk-0 (0.16) | Unsupported answering |

`original-before.json`, `eval-original-before.txt`, `E05-before.txt`,
`E11-before.txt`, `pytest-before.txt`, `pytest-before-unsandboxed.txt` and
`before-manifest.json` preserve the measurements, CLI context and file hashes.
The eval hash is
`afe46db1e75a0b85bb5c9a93b6763e3b96e5cd7b289e12da6d2671e4d8650064`.

M2 remains disabled; retrieval is still lexical. No root `.env` or process API key
was present at implementation start. Gemma quality measurements and embedding
integration therefore remain future checks rather than asserted improvements.
