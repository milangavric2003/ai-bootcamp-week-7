# Live verification protocol

Date: 21 October 2026 (Europe/Belgrade).

The user explicitly approved sending the twelve fixed evaluation questions,
grounding prompt and up to three sample handbook chunks per question to Google's
Gemini API at `generativelanguage.googleapis.com`, using the existing local key,
for four configurations and two retained-configuration CLI checks. They added:
"I approve, just know that you can send max 30 request per minute to gemma".

The entire source corpus was inspected and is the fictional course handbook;
`src/corpus.py` is byte-identical to the preserved starter (SHA-256
`52cceca071e43682705234713d12a4b94bbf3617e9e7c44cfcba1f6f94a6ef78`).
No real employee records, credential values or arbitrary workspace files are
included in the evidence payload. The existing API adapter authenticates normally.

Before approval, one sandbox evaluation failed at the first question because
network access was unavailable. Its `gemma-before.txt`, execution record and
error-only trace are preserved. Two subsequent requests for network access were
rejected by automatic review over destination/payload authorization; no calls
were executed by those rejected actions. No workaround was used. Live execution
resumed only after the user's explicit approval.

Measure configurations in the predetermined order: 2/off, 3/off, 2/on, 3/on. Do not
tune based on the results or repeat a complete run to seek a better score. All
other settings, fixed questions, metrics and grounding policy remain unchanged.
The first three modes override only the selected configuration in process memory;
the last uses the same retained values. All execute the unchanged evaluator entry
point. Trace actual model, retries, refusal, text and source IDs in fresh files.

The evidence driver wraps the existing transport only within hosted measurement
subprocesses. It spaces every attempted request by at least 2.1 seconds, sharing
state across the sequential child processes. It covers primary, retries and Gemini
fallback, so Gemma stays below 30 requests in any rolling minute. Request start
times and model names are saved in `rate-limit-requests.jsonl`. The local timing
state is ignored, as are pytest temporary directories. Timing in answer traces
includes any intentional pacing; it is not model-only latency. No production
rate-limit policy is introduced by this verification helper.

## Interrupted measurement disposition

The TOP_K=3 / stopwords=False execution reached E09 and failed the existing
inline-citation validator, before a complete result file was written. One recovery
execution used fresh filenames with unchanged settings; it failed at E09 with the
same error. Both attempts are retained with no quality score, and no third attempt
was made. The other combinations proceeded independently. This recovery policy
does not repeat completed runs or choose results by score. The driver preserves
completed results and refuses multiple completed candidates for one configuration.
