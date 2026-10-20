# Setup and validation guide

The Gemma backend is implemented and live-verified. The suite passes 163 tests;
offline mode reproduces 10/12, and the controlled live lexical run improves to
11/12 without PASS-to-FAIL regressions. See `docs/gemma-report.md` for actual
evidence. Run from the repository root using
the existing virtual environment. Use fresh evidence names/directories: the
original-before, retained and `live/` runs are already saved and must not be overwritten.
The later [retry amendment](retry-spec.md) enables two Gemma attempts followed by
two Gemini attempts with the same timeout; see `docs/evidence/005-gemma/retries/report.md`
for its separate operational verification. The 11/12 result above is Gemma-only
historical evidence, not a full mixed-model quality measurement.

## 1. Separate work and preserve the baseline

The documentation branch `feat/gemma-generation` was created at the user's
subsequent request to commit and push the plan. For implementation, use an isolated
checkout if sharing a working directory with Vedran. Do not switch his active
checkout or reuse his uncommitted changes. No additional checkout has been created.

The following unchanged baseline was captured before runtime edits. It is retained
for review; use a different directory for any new experiment:

```powershell
New-Item -ItemType Directory -Path docs/evidence/005-gemma -Force
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m src.eval_runner --out docs/evidence/005-gemma/original-before.json
.\.venv\Scripts\python.exe -m src.cli --question "How long until I get a new notebook computer?" --show-retrieved
.\.venv\Scripts\python.exe -m src.cli --question "What is the parental leave policy?" --show-retrieved
```

Save test/CLI output, commit, configuration and source/eval hashes. Document at
least two actual baseline failures before implementation. Historical expectation
is 10/12 with E05/E11 failing, but use the newly observed result as evidence.

## 2. Implement and validate offline behavior

Tasks, optional answering code, root `.env.example`, secret ignore rules and the
pinned dotenv dependency are implemented. Install requirements into your local
project environment if needed; then run the suite. Unit-test fixtures prevent
unmocked Google calls even if your real `.env` enables Gemma.

Then run the complete suite without a key:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Meaningful mocked checks cover: all top-k text/metadata supplied in order, selected
citations, valid refusal, retrieval-gate skip, invalid JSON/types/IDs, incomplete
output, missing key, timeouts, quota/authentication errors, sanitized errors,
trace records, and disabled mode with zero requests. Existing tests still pass.

## 3. Configure Google access later

Once ignore rules and the root template are implemented:

```powershell
Copy-Item -LiteralPath .env.example -Destination .env
```

Fill `GEMINI_API_KEY` locally. Leave the default `ANSWER_BACKEND=extractive` until
explicitly selecting `gemma`. Environment variables override `.env`. Never put
the key in a shell argument, public config snapshot, evidence or commit.

Use the model and settings from the contract. Set `ANSWER_BACKEND=gemma` in `.env`
and run the supplied synthetic library probe:

```powershell
.\.venv\Scripts\python.exe docs/evidence/005-gemma/live_probe.py
```

It makes at most two requests outside the fixed evaluation to check supported
answering and evidence refusal. Inspect the 17:00 fact and its citation manually;
the script's behavior check alone does not validate every claim. Use this to verify
model access, completion settings, response shape, JSON parsing and source validation.
Freeze the prompt/settings after that probe. A key does not guarantee quota or
model access; stop and record failures rather than change models automatically.

## 4. Controlled answering comparison

The following future commands compare two answerers over one frozen retrieval
backend. Run them first with lexical retrieval if useful, then in a separately
named directory after integrating Vedran's frozen embedding configuration.
The directory name below is for the primary embedding comparison.

```powershell
New-Item -ItemType Directory -Path docs/evidence/005-gemma/embedding -Force
$env:ANSWER_BACKEND = 'extractive'
$env:GEMMA_TRACE_PATH = 'docs/evidence/005-gemma/embedding/before-answers.jsonl'
.\.venv\Scripts\python.exe -m src.eval_runner --out docs/evidence/005-gemma/embedding/before.json
$env:ANSWER_BACKEND = 'gemma'
$env:GEMMA_TRACE_PATH = 'docs/evidence/005-gemma/embedding/after-answers.jsonl'
.\.venv\Scripts\python.exe -m src.eval_runner --out docs/evidence/005-gemma/embedding/after.json
.\.venv\Scripts\python.exe -m src.eval_compare docs/evidence/005-gemma/embedding/before.json docs/evidence/005-gemma/embedding/after.json
Remove-Item Env:ANSWER_BACKEND
Remove-Item Env:GEMMA_TRACE_PATH
```

Expect the same eval hash, retrieval settings and per-question retrieved IDs/scores
in this pair. Public model/prompt/settings are present in both snapshots; only the
answering backend changes. The trace path is an output destination and stays out
of behavior-setting snapshots. If comparing original code against new disabled
code, newly introduced configuration keys may also appear; explain those plumbing
differences and verify outcomes separately rather than hide the warning.

API failures invalidate an attempted full run. Do not use a partial result or call
it a successful refusal. Preserve attempted-run failures separately. Account for
any extra requests from manual checks, and record usage/latency as observed.

## 5. Review answers and report

Save comparison output. Manually review all 12 answer texts from the measured
trace, checking each claim against its citations, omissions, and unnecessary
refusals. Explicitly inspect E09's request location and deadline. Use the CLI for
at least one changed case and inspect retrieved context, preserving that output.

Report all regressions and at least one remaining limitation. Explain that fixed
metrics inspect facts in citations, not the generated prose; do not change them.
Distinguish A-to-B retrieval effects from B-to-C generation effects. Include model,
prompt hash, settings, dependencies, usage/cost, execution failures and contributors.
Submission/review/demo claims require actual human evidence, not this plan.
