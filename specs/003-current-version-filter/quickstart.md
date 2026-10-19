# Validation Guide: M5

Run from repository root with the project virtual environment. These are future
implementation checks, not claims that M5 has run. Complete minimum submission
first, then use a separate implementation branch and a fresh evidence folder.
Do not overwrite an earlier experiment directory on a repeat.

## Before changing code

Save commit, Python/pytest versions, configuration and hashes. Document E06's
contradiction and E05/E11's expected/actual outcomes and failure types.

```powershell
New-Item -ItemType Directory -Path docs/evidence/003-m5
.venv/Scripts/python.exe -m pytest
.venv/Scripts/python.exe -m src.eval_runner --out docs/evidence/003-m5/before.json
.venv/Scripts/python.exe -m src.eval_compare results/after-m3.json docs/evidence/003-m5/before.json
.venv/Scripts/python.exe -m src.cli --question "How many days per week can I work remotely?" --show-retrieved
```

Baseline: 35 tests pass and 10/12 eval questions pass; comparison has no result
or configuration differences. Save command outputs as evidence.

## After implementing only M5

```powershell
.venv/Scripts/python.exe -m pytest
.venv/Scripts/python.exe -m src.eval_runner --out docs/evidence/003-m5/after.json
.venv/Scripts/python.exe -m src.eval_compare docs/evidence/003-m5/before.json docs/evidence/003-m5/after.json
.venv/Scripts/python.exe -m src.cli --question "How many days per week can I work remotely?" --show-retrieved
```

Hypothesis: no lost passes, same eval hash, only CURRENT_ONLY False → True.
E06 cites 3 days per week and retrieves/cites no superseded source. Unit tests
check mixed/empty eligibility and the disabled path. Inspect E04/E09/E10/E11/E05
as controls and preserve outputs. If results differ, report that rather than
changing thresholds in the same experiment.

Save tests, eval tables, comparisons, CLI outputs, hashes and code diff. Write
docs/m5-report.md with the decision, regressions, historical-query limitation,
AI assistance and contributions. A result of 10/12 can confirm E06's improved
citations. Official metrics must remain unchanged.
