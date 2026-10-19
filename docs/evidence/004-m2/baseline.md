# M2 baseline, before implementation

Date: 19 October 2026. Branch: `main`; starting commit: `aa643d7`.
This is optional work explicitly requested by Milan. The assignment places
advanced work after submission of the required minimum; that submission is
not confirmed. This timing exception is recorded, as for M3 and M5.

The unchanged M1+M3+M5 pipeline passes **43/43 unit tests and 10/12 evaluation
questions**. `before.json` matches `results/after-m5.json` except its timestamp.
`before-manifest.json` records the commit, configuration, Python version and
hashes of tracked source, tests, evaluation, historical results and references.

| ID | Expected | Actual before M2 | Failure type |
| --- | --- | --- | --- |
| E05 | Cite equipment replacement with `5 business days` | Answers with onboarding (`hb-06-chunk-0`, 0.25) and annual leave (`hb-07-chunk-1`, 0.111111); retrieval hit false, fact absent, precision 0 | Retrieval vocabulary mismatch and irrelevant matches |
| E11 | Refuse: no parental leave policy in the corpus | Answers with annual leave (`hb-07-chunk-1`, 0.222222; `hb-07-chunk-0`, 0.16) | Unsupported answering within the same topic |

See `E05-before.txt` and `E11-before.txt` for complete CLI output. The M2
hypothesis is reduced common-word noise, not fixing synonyms or answerability.
The 40-word list is frozen in the design before modifying source or seeing
filtered evaluation results. No threshold or list tuning is part of this run.

Commands run from the root with `.venv/Scripts/python.exe`:

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -B -m src.eval_runner --out docs/evidence/004-m2/before.json
.\.venv\Scripts\python.exe -B docs/evidence/004-m2/verify.py --capture
.\.venv\Scripts\python.exe -B -m src.cli --question "How long until I get a new notebook computer?" --show-retrieved
.\.venv\Scripts\python.exe -B -m src.cli --question "What is the parental leave policy?" --show-retrieved
```

The first sandbox test run had 42 passes and one permission error accessing
pytest's existing system temp directory; it also emitted cache permission
warnings. `pytest-before-sandbox.txt` preserves that attempt. Repeating the
same command with normal temp access passes all 43 tests (`pytest-before.txt`).
No test, discovery setting or system execution policy was changed.
