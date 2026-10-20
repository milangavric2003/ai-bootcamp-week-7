# Retry update: unchanged baseline

Date: 2026-10-20. Starting commit `aa17fc0`, branch `feat/gemma-generation`.
The user explicitly requests Gemma twice, then Gemini 3.5 Flash-Lite twice, with
the same timeout. Specification: `specs/005-grounded-gemma/retry-spec.md`, written
before runtime changes.

The unchanged suite passes 134/134 tests. Fresh disabled-mode fixed evaluation
passes 10/12; results, full answer trace, console output and runtime/history hashes
are saved alongside this file. The earlier live Gemma-only result is 11/12 and is
preserved separately; no new live quality baseline is invented for this transport fix.

| ID | Expected | Actual fresh offline baseline | Failure type |
| --- | --- | --- | --- |
| E05 | Equipment replacement, citing 5 business days | Onboarding and annual-leave retrieval, expected fact absent | Retrieval vocabulary mismatch |
| E11 | Refuse parental leave without evidence | Answers using annual-leave evidence | Unsupported extractive answering |

The new failure motivating this update is the user's reported network/timeout
error. The original client has no second attempt or fallback route. Controlled
tests will demonstrate that limitation without claiming to reproduce the exact
cause of the user's intermittent connection failure.
