# Reliability amendment: bounded retries and Gemini fallback

Date: 2026-10-20. Requested by the user on `feat/gemma-generation` after a CLI
network/timeout failure. This amendment supersedes the original no-retry/no-model-
fallback contract for optional generation. It does not change the required M1
experiment or reinterpret the saved Gemma-only 11/12 result.

## Failure, hypothesis and one intent

The user reported `Gemma network request failed or timed out; no automatic retry`
when asking the parental-leave question. The current client makes one request and
immediately aborts on a network failure. This is an operational failure, not a
claim that the earlier E11 answer-quality fix regressed.

Hypothesis: retrying transient failures and then using an explicitly identified
fallback model will recover some temporary failures while retaining bounded work
and the current per-attempt timeout. A broken local network or invalid credentials
can still prevent every attempt from working.

## Acceptance contract

1. Attempt the configured Gemma model at most twice (initial call plus one retry).
   Only after both transiently fail, attempt `gemini-3.5-flash-lite` at most twice.
   Stop immediately on success, including a valid evidence refusal.
2. Preserve `GEMMA_TIMEOUT_SECONDS` (default 30) for every attempt. Use short bounded
   backoff between retryable failures: 0.25, 0.5 and 1 second. Four timeouts may
   therefore take roughly 120 seconds plus backoff/transport overhead; this is not
   a 30-second total deadline and does not increase the per-attempt timeout.
3. Retry timeouts, temporary connection errors and HTTP 408/429/500/502/503/504.
   Authentication/permission/configuration errors, redirects, other HTTP errors,
   certificate verification failures and malformed/blocked/unsupported responses
   stop immediately. Never turn exhausted attempts into `refused=True`.
4. Reuse the same question, full retrieved context, grounding prompt and decision
   validation. Gemini fallback omits explicit candidate count and otherwise keeps
   the same minimal thinking/output settings. No native JSON schema dependency.
5. Public config records fallback model, attempt limits and backoff. The default
   fallback is `gemini-3.5-flash-lite`; an empty `GEMMA_FALLBACK_MODEL` disables it.
   The real key stays private and no `.env` edit is needed for the default.
6. Return and trace actual answering model, ordered sanitized attempts and whether
   fallback was used. CLI output identifies the answering model. Failed attempts
   are recorded too, without raw provider error bodies or credentials.
7. Keep optional inline citation behavior as accepted by the user. Do not alter
   retrieval, M2=False, corpus, chunking, fixed eval questions or metric code.
8. Implement locally and provide a commit message; the user will commit/push.

## Risks and verification

Retries consume additional time and potentially quota; a timed-out request may
have been processed by the server. Report returned usage only, since token usage
for failed requests can be unknown. A different model can produce different prose
or refusals. A fallback-enabled run is a separate policy from historical Gemma-only
measurements, and traces must disclose the model actually used.

Save a fresh unchanged offline test/eval baseline before runtime edits. Earlier
E05/E11 failures remain documented in `docs/evidence/005-gemma/baseline.md`; the
fresh offline baseline again exhibits those failures. Do not invent a second live
quality failure: the saved live Gemma-only result still has only E05 failing.

Use deterministic fault-injection tests for Gemma retry success, fallback success
on its first/second attempt, four failures, permanent errors and trace provenance.
Run the whole suite and disabled-mode fixed evaluation/comparison. Reproduce the
reported CLI question live and exercise fallback with local injected failures on
the primary route, clearly distinguishing synthetic failures from real requests.
No claim of changed fixed-set quality follows from those operational probes.

## Implementation plan and sources

Extend `src/gemma_client.py` with a bounded attempt loop around one-request parsing,
reuse strict validation, and adapt the Gemini payload. Carry model/attempt metadata
through `src/generation.py`, `src/rag.py`, `src/generation_errors.py` and traces.
Add optional defaulted result fields to preserve existing caller compatibility.
Add config/example documentation and tests before implementation; leave history intact.

Google documents the [model ID](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite),
[minimal thinking](https://ai.google.dev/gemini-api/docs/generate-content/thinking),
[retry guidance](https://ai.google.dev/gemini-api/docs/troubleshooting) and
[free-tier availability](https://ai.google.dev/gemini-api/docs/pricing).
Project access is verified live rather than assumed from the model listing.
