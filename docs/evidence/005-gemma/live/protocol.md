# Frozen live comparison protocol

Date: 2026-10-20. Branch: `feat/gemma-generation`; implementation commit `0335610`.
The user supplied the key locally and authorized live verification. It is ignored
by Git and is not recorded in evidence.

## Capability check before the fixed evaluation

The first attempt was blocked by the sandbox's network policy, recorded separately
as `probe-sandbox.*`. The two-case real Google probe then passed (`probe-01.*`):
the fictional library closes at 17:00 on Fridays, with the supplied citation;
weekend childcare is unsupported and is refused without citations.

A local compatibility fix was necessary before making requests: the old key
validator rejected dots in Google's newer authorization-key format. Credentials
are now treated as opaque printable ASCII header values; whitespace, control
characters and non-ASCII remain invalid. This does not change the model, prompt,
retrieval or answering policy. Seven new regression cases pass; the full suite
passes 134 tests. No credential value is written into the fix or tests.

New live console logs are normalized to UTF-8 without changing their text, so the
saved comparison and CLI output are readable in repository viewers.

## Frozen design and hypothesis

Use `gemma-4-26b-a4b-it`, temperature 0, 1024 output tokens, minimal thinking,
30-second socket timeout and the existing prompt. Preserve all retrieval settings,
including lexical retrieval, top-k=2, current-only sources and M2=False.
`run-manifest.json` records the public configuration and runtime source hashes.

Compare `before.json` (extractive) and `after.json` (Gemma), using the unchanged
`src.eval_runner` over all 12 questions, followed by `src.eval_compare`. Only
`ANSWER_BACKEND` changes in the public settings. Use distinct same-run answer
traces. No evaluation question or metric calculation is modified.

The pre-existing hypothesis is better answerability/citation selection, especially
refusing E11's parental-leave question when only annual-leave evidence is present.
E05 remains a retrieval limitation if the equipment evidence is absent. No pass
count is promised. Do not tune prompt or retrieval using the fixed evaluation.

Inspect all generated answers against their actual cited passages, including E09's
request location and deadline. A correct citation ID alone does not establish
support. Preserve every regression or remaining omission, even when metrics pass.
Use one changed question in the CLI after the measured run.

Operational failures stop a run; they are not correct refusals. Preserve partial
attempts separately. Model/prompt changes, if ever needed, require a new labeled
experiment rather than overwriting or relabeling this one. Vedran's embeddings
are outside this comparison and still need a separate integration measurement.
