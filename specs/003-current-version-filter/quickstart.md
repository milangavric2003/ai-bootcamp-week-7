# Validation Guide: M5

M5 is implemented on main at the user's request. All 43 tests pass; evaluation
remains 10/12, E06 citation precision is 1.00, and mean precision is 0.65.
See the [report](../../docs/m5-report.md) for measured results and limitations.

Run commands from repository root with the project virtual environment.
Preserve the saved evidence; use fresh filenames when repeating evaluation.

## Compare the saved controlled experiment

```powershell
.venv/Scripts/python.exe -m src.eval_compare docs/evidence/003-m5/before.json docs/evidence/003-m5/after.json
```

Expected: no changed pass/fail outcomes, same eval hash, only CURRENT_ONLY
False → True. Mean citation precision rises 0.60 → 0.65. E05/E11 still fail.

## Verify the current implementation independently

```powershell
.venv/Scripts/python.exe -m pytest
$m5RunFile = 'results/m5-verification-' + [guid]::NewGuid().ToString('N') + '.json'
.venv/Scripts/python.exe -m src.eval_runner --out $m5RunFile
.venv/Scripts/python.exe -m src.eval_compare docs/evidence/003-m5/after.json $m5RunFile
.venv/Scripts/python.exe -m src.cli --question "How many days per week can I work remotely?" --show-retrieved
```

Expected: 43 passed and 10/12; comparison to the saved after run has no changes
in settings, outcomes or summary metrics. E06 cites 3 days per week and retrieves
and cites no superseded source. Inspect both source versions and answer text:
an automatic PASS alone cannot prove the two-day contradiction is gone.

Also inspect E04's duration, E09's request location and duration, E10's refusal,
E05/E11's remaining failures, and E02's unrelated padding citation.
Eligibility tests cover mixed statuses, ordering, empty results and disabling the
filter; the integration tests cover actual E06 citations and refusal without
eligible evidence.

The saved tests ran outside the sandbox because Windows temporary/cache access
was denied there. No project or system setting was changed to resolve that.

## Baseline provenance and compatibility

Before code changes at commit ab83d92, the same pytest and eval_runner commands
saved 35 passing tests and 10/12. The fresh before run matches M3's after run
except timestamp. Failures and CLI evidence were documented before implementation.

Do not recreate before.json with the current enabled-filter code. For a fresh
historical baseline use an isolated checkout of ab83d92 and a fresh output
directory. The saved integrity verification additionally confirms that running
the current implementation with CURRENT_ONLY disabled in an isolated process
reproduces the saved before result apart from timestamp.

The [evidence directory](../../docs/evidence/003-m5/) contains before/after JSON,
test and CLI logs, comparison, hashes and implementation diff. No official eval
questions or metric code changed. Historical questions cannot retrieve
superseded sources while the filter is enabled.
