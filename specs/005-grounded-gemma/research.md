# Research: Grounded Gemma answering

Date: 2026-10-19. Planning research only; no authenticated request was made.

## Assignment interpretation

**Decision**: Treat embeddings and grounded generation as separate optional
experiments, preserving the required local M1 submission and historical evidence.

**Rationale**: `docs/weekly-assignment.md`, section "Napredni cilj", explicitly
allows LLM text generation after the submitted minimum. Slides 9, 21 and 26
require fixed evaluation, one intent between measurements, and separate advanced
work. Slides 12 and 17 explain why missing evidence cannot be repaired by answering
and why final citations should support claims rather than list every retrieval hit.

**Alternative considered**: Combine embeddings and LLM into a single improvement.
Rejected because their contributions could not be distinguished.

## Provider and model

**Decision**: Use the user's confirmed Google AI Studio key with Gemini API model
`gemma-4-26b-a4b-it`; make the model ID configurable. Google documents this model,
system instructions, and a `minimal` thinking setting for disabling thinking.
[Official Gemma hosting guide](https://ai.google.dev/gemma/docs/core/gemma_on_gemini_api).

**Rationale**: This matches the requested model and provider. Gemma is the model;
Gemini API is the hosting interface. They are distinct names for different things.

**Alternatives considered**: A different provider, a Gemini model, or local model
hosting. None matches the user's selected integration as directly.

## Free tier and execution failures

**Decision**: Target the free tier without enabling billing or switching models.
Google currently lists Gemma 4 token input/output as free. Actual access and quota
must be checked in the user's project; no particular throughput is assumed.
[Pricing](https://ai.google.dev/gemini-api/docs/pricing),
[rate limits](https://ai.google.dev/gemini-api/docs/rate-limits).

**Rationale**: A key alone cannot establish model access, remaining quota or service
availability. Authentication, quota and transport failures must abort a measured
run rather than become successful evidence refusals.

**Alternative considered**: Automatic retries or a fallback model. Defer both to
keep request counts and model identity clear in the first experiment.

## Transport and configuration

**Decision**: Use a small Python standard-library HTTPS client for Google's
`generateContent` REST endpoint; add only `python-dotenv` for the requested local
`.env` workflow. Pin its version during implementation. Send the key explicitly
in `x-goog-api-key`; do not put it in a URL or public configuration.
[REST reference](https://ai.google.dev/api/generate-content),
[API-key documentation](https://ai.google.dev/gemini-api/docs/api-key).

**Rationale**: The application needs one nonstreaming text-generation operation,
not another application server or retrieval dependency. Environment variables
override `.env` values; secret loading never stores the key in `config.snapshot()`.

**Alternatives considered**: Official Google SDK, or manually setting all shell
variables. The SDK is valid but unnecessary for the small initial interface;
shell-only configuration would not load the requested `.env` file.

## Output format and validation

**Decision**: Request JSON in the prompt and strictly validate it locally. Do not
depend on native JSON-schema mode until this exact model has passed a live probe.

**Rationale**: Google's general structured-output guide does not by itself
establish that every hosted Gemma configuration supports the same native schema
controls. Invalid output must be visible even when a request succeeds.
[Structured-output documentation](https://ai.google.dev/gemini-api/docs/structured-output).

**Alternatives considered**: Parse arbitrary prose or accept citations without
validation. Rejected because the fixed evaluator dereferences citation IDs and
because malformed responses should not be treated as evidence refusals.

## Integration and evaluation

**Decision**: Consume `list[RetrievalResult]` and return the existing `RagAnswer`.
Preserve the current retrieval gate and fixed metrics. Compare extraction versus
Gemma over one frozen retrieval backend at a time. Record answer text separately.

**Rationale**: `src/rag.py` currently echoes retrieved chunks; no LLM runs today.
`src/eval_runner.py` checks facts in cited chunks and behavior, but does not inspect
the generated answer's text. Citation validity is mechanically testable; semantic
support still needs review. Embedding score calibration belongs to Vedran's work.

**Alternative considered**: Modify metrics to grade generated prose or tune
retrieval thresholds during generation work. Both violate the controlled design.

## Resolved design and deferred execution checks

There are no unanswered design choices required for this plan. Credentials,
project quota, exact live response shape, and final embedding results are future
execution checks, not facts established by documentation. A blocked capability
probe stops implementation validation; it does not justify silently changing
models, prompts, retrieval settings or the experiment definition.
