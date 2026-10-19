# M2 validation and human review

Run from the repository root using its existing virtual environment. No install.

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -B -m src.eval_runner --out results/m2-review-fresh.json
.\.venv\Scripts\python.exe -B -m src.eval_compare docs/evidence/004-m2/before.json results/m2-review-fresh.json
.\.venv\Scripts\python.exe -B -m src.cli --question "How long until I get a new notebook computer?" --show-retrieved
.\.venv\Scripts\python.exe -B -m src.cli --question "What is the parental leave policy?" --show-retrieved
```

The default is now M2 disabled, as selected after the E09 regression. The fresh
run above should reproduce the 10/12 baseline. To independently reproduce the
enabled 9/12 experiment without editing the retained configuration:

```powershell
.\.venv\Scripts\python.exe -B -c "from src import config; from src.eval_runner import main; config.STOPWORDS_ENABLED = True; main()" --out results/m2-enabled-review-fresh.json
.\.venv\Scripts\python.exe -B -m src.eval_compare docs/evidence/004-m2/before.json results/m2-enabled-review-fresh.json
.\.venv\Scripts\python.exe -B -c "from src import config; from src.cli import main; config.STOPWORDS_ENABLED = True; main()" --question "Where do I request a replacement laptop and how long does it take?" --show-retrieved
```

Only the temporary process enables filtering; the source default stays False.
Expect no fixes, E09 regression, mean citation precision 0.70, and unchanged
evaluation fingerprint. Tests still pass; they verify mechanics, not answer quality.

Use a fresh output name; never overwrite saved experiment runs. If sandbox temp
permissions prevent pytest, rerun with normal temp access, preserving both logs.

Read docs/m2-report.md and docs/evidence/004-m2/compare.txt; review the implementation
diff against the frozen list in plan.md. Check the unchanged evaluation fingerprint,
all regressions and remaining limitations. Independently inspect E04/E06/E09 and
changed supporting citations; E09 asks both request location and replacement time.

This review is pending until a human records it. Embeddings are the user's next
separate experiment after review; the later LLM experiment assesses evidence and
refusal. See docs/advanced-plan.md. Neither is implemented by M2.
