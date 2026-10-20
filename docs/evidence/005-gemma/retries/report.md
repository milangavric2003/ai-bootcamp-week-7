# Retry and fallback verification

Date: 2026-10-20. Starting commit: `aa17fc0`; changes are local for the user to
commit and push. This is the explicitly requested reliability update specified in
`specs/005-grounded-gemma/retry-spec.md`, not a new claimed RAG quality improvement.

## Behavior

- At most two Gemma attempts, then two `gemini-3.5-flash-lite` attempts, stopping
  immediately on success or a valid model refusal.
- Existing per-attempt timeout remains 30 seconds. Short backoff is 0.25/0.5/1
  second; no sleep follows success or exhaustion. Four timeouts can take roughly
  two minutes plus transport overhead; the timeout has not become a total deadline.
- Transient connection/timeouts and HTTP 408/429/500/502/503/504 are retryable.
  Authentication/permission/configuration, TLS certificate, invalid response and
  other HTTP failures stop immediately. Exhaustion raises an operational error.
- Actual model and ordered sanitized attempts reach the answer object and trace.
  CLI prints the answering model. Local refusals have no actual model/attempts.
- The same evidence, prompt and validators are reused. Fallback only omits the
  explicit candidate-count option; inline citations remain optional as accepted.
- Default fallback requires no `.env` edit. Empty `GEMMA_FALLBACK_MODEL` disables it.
  The user's real `.env` was not modified.

## Actual verification

The unchanged [baseline](baseline.md) passed 134 tests. Newly added contract tests
failed against the old single-request behavior (`pytest-red.txt`). After the
implementation, **163/163 tests pass** (`pytest-after.txt`). They cover success on
attempts 1-4, unchanged timeout and payload, bounded backoff, permanent errors,
certificate failures, invalid fallback citations, actual-model provenance and
failure/refusal separation.

The complete disabled-mode evaluation remains **10/12**. Every result row, retrieved
chunk/score and original configuration value is identical before/after. The
[comparison](comparison.txt) warns about four newly added settings: fallback model,
primary/fallback attempt limits and backoff. These implement one reliability policy
and do not represent multiple retrieval improvements. The eval set and metric code
are unchanged.

The [verification script](verify_retry.py) checks all 12 result rows and 37 protected
baseline files, including earlier live evidence. Its [saved result](verification.json)
also confirms the unchanged timeout/M2 setting, live attempt order, Python syntax
and no local credential matches in the checked project files. New console logs
are normalized to UTF-8 for review.

Two live operational checks passed using the existing local key:

1. [Original CLI question](parental-cli.txt), using the user's `--questi` prefix:
   Gemma answered with the expected evidence refusal and no citations. The
   [trace](parental-cli.jsonl) records one successful Gemma attempt.
2. [Fallback probe](fallback-probe.txt): the [probe script](live_fallback_probe.py)
   injected two local Gemma timeouts, then sent a real request to Gemini 3.5
   Flash-Lite. Gemini correctly refused the parental-leave question. The
   [trace](fallback-probe.jsonl) records the full three-attempt order and actual
   answering model. The injected failures never reached Google; this is not
   evidence of two real Gemma outages. Fourth-attempt success and full exhaustion
   are verified with deterministic mocked tests.

## Limits and attribution

The user-reported intermittent network failure's exact underlying cause was not
available from the original sanitized message. Retry recovery is demonstrated
under injected failures, not a guarantee against an offline computer or provider
outage. Certificate errors now identify the certificate problem and fail fast.
Retries can consume extra time/quota; timed-out server processing and its token
usage may be unknown. Reported usage describes the successful response only.

Historical Gemma-only 11/12 measurements under `../live/` are unchanged. No new full
12-question live quality score is claimed for the mixed-model fallback policy.
Prompt, retrieval, M2=False and citation behavior are preserved. E05 remains a
retrieval limitation, and Vedran's embedding integration is still separate.

Codex implemented and checked the user's explicit request. Tests and saved command
outputs establish local contracts and the two specific live outcomes. The user
will perform the commit/push; this update does not claim independent peer review.
