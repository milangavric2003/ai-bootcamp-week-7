# Verify optional hybrid retrieval

Run from repository root using the existing venv and prepared cached model.

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider --basetemp=.cache/pytest-hybrid-local
.\.venv\Scripts\python.exe -m src.cli --retrieval-backend hybrid --question "Where do I request a replacement laptop and how long does it take?" --show-retrieved
```

Check `IT portal`, `Hardware`, and `5 business days` in the answer, citing
`hb-01-chunk-1` and `hb-01-chunk-2`. Diagnostics distinguish RRF from cosine.

```powershell
$env:HF_HUB_OFFLINE='1'
$env:RAG_RETRIEVAL_BACKEND='hybrid'
.\.venv\Scripts\python.exe -m src.eval_runner --out results/hybrid-local-check.json
.\.venv\Scripts\python.exe -m src.eval_compare docs/evidence/008-hybrid-ranking/before.json results/hybrid-local-check.json
Remove-Item Env:RAG_RETRIEVAL_BACKEND
```

Use fresh filenames. Target 12/12 retained; E09 completeness improves, while
E01/E05 secondary-citation precision may regress. E05 must retain its deadline;
E10/E11/E12 must refuse. Reproduce both existing modes against their saved
baselines. Fixed metrics alone do not prove E09 completeness or general quality.

See [contract](contracts/retrieval.md), [plan](plan.md), and
[report](../../docs/hybrid-report.md) for policy and limitations.
