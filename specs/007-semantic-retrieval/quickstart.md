# Quickstart: Local semantic retrieval

Run from repository root in the project virtual environment. Initial model setup:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-embeddings.txt
.\.venv\Scripts\python.exe -m src.prepare_embeddings
```

The first command installs optional local-model dependencies; the second downloads
the pinned public model. Neither sends handbook text to an embedding service.
The prepared model and local vectors are excluded from the commit scope.

Run semantic retrieval with the existing selected answerer:

```powershell
.\.venv\Scripts\python.exe -m src.cli --retrieval-backend embeddings --question "How long until I get a new notebook computer?" --show-retrieved
```

Inspect whether the equipment source and up to five business days after manager
approval are present. Check E09 for IT portal / Hardware and the timing qualifier,
E06 for the current three-day remote policy, and E11 for refusal.

For full measurements use fresh filenames and an explicit answerer:

```powershell
$env:RAG_RETRIEVAL_BACKEND = 'embeddings'
$env:ANSWER_BACKEND = 'gemma'
$env:GEMMA_TRACE_PATH = 'results/semantic-new-answers.jsonl'
.\.venv\Scripts\python.exe -m src.eval_runner --out results/semantic-new.json
.\.venv\Scripts\python.exe -m src.eval_compare docs/evidence/007-semantic-retrieval/lexical-gemma-before.json results/semantic-new.json
```

For rate-limited hosted verification, the experiment helper invokes the same
runner with 2.1-second spacing per transport attempt. Do not reuse evidence labels:

```powershell
.\.venv\Scripts\python.exe docs/evidence/007-semantic-retrieval/run.py eval --label semantic-new --backend gemma --retrieval embeddings
.\.venv\Scripts\python.exe docs/evidence/007-semantic-retrieval/run.py test --label pytest-new
```

Set `ANSWER_BACKEND=extractive` for offline answering and
`RAG_RETRIEVAL_BACKEND=lexical` to reproduce the original retrieval mode. Tests
mock model loading and hosted requests; real-model verification is separate.
