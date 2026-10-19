# Week 7 RAG checkpoint

A small local question-answering tool over a fictional employee handbook. It retrieves chunks, answers with chunk citations and refuses questions the handbook does not cover. It runs offline: no API keys, no network, no paid services.

This week you will **measure** this system on a fixed eval set, find failures, apply **exactly one** improvement and compare results before and after.

## Current state: M1 + M3 + M5; M2 implemented but disabled

The required M1 experiment improved evaluation from **6/12 to 9/12**.
The separate optional M3 experiment raises `REFUSAL_THRESHOLD` from 0.02 to
0.10 and improves **9/12 to 10/12**, fixing E10 without PASS-to-FAIL regressions.
The saved M3 test run passes **35/35** tests. Vedran has confirmed completing
manual M3 evaluation; see the [M3 report](docs/m3-report.md) for evidence and
the distinction between his confirmation and Codex-generated execution logs.

The optional M5 experiment now excludes superseded sources before ranking.
Evaluation remains **10/12 without regressions**, while E06 citation precision
improves **0.50 → 1.00** and mean citation precision **0.60 → 0.65**.
The M5 suite passed **43/43** tests; see the [M5 report](docs/m5-report.md).

M2 stopword filtering is now implemented and separately measured on `main`.
Enabled, it improves mean citation precision **0.65 → 0.70** but regresses E09,
reducing evaluation **10/12 → 9/12**. At the user's request it remains
**disabled** (`STOPWORDS_ENABLED=False`). The retained pipeline reproduces
**10/12**, and **53/53 tests pass** in both modes. See the [M2 report](docs/m2-report.md).

An optional local embeddings backend is now implemented for a separate advanced
experiment. The default remains lexical retrieval; the expanded offline unit
suite now passes **86/86** tests. The lexical results still match the retained 10/12
baseline. The first embeddings run at threshold 0.10 gave 10/12 (E05 fixed,
E10 regressed). A separate development-set calibration selected cosine refusal
threshold **0.50**, yielding **11/12** with E10 fixed and no new regressions.
E11 remains a failure. Lexical refusal stays at **0.10**. See the
[threshold report](docs/embedding-threshold-report.md),
[implementation notes](docs/embeddings-status.md) and
[quickstart](specs/005-local-embeddings/quickstart.md).

| Experiment | Before | After | Report |
| --- | --- | --- | --- |
| Required M1: sentence chunking | [before.json](results/before.json), 6/12 | [after.json](results/after.json), 9/12 | [M1 report](docs/m1-report.md) |
| Optional M3: refusal threshold | [before-m3.json](results/before-m3.json), 9/12 | [after-m3.json](results/after-m3.json), 10/12 | [M3 report](docs/m3-report.md) |
| Optional M5: current versions | [before-m5.json](results/before-m5.json), 10/12 | [after-m5.json](results/after-m5.json), 10/12 | [M5 report](docs/m5-report.md) |
| Optional M2: stopwords (disabled after measurement) | [before.json](docs/evidence/004-m2/before.json), 10/12 | [after.json](docs/evidence/004-m2/after.json), 9/12; [retained.json](docs/evidence/004-m2/retained.json), 10/12 | [M2 report](docs/m2-report.md) |

The current code includes all three improvements. E05 and E11 still fail;
E06 now cites only the current policy. Irrelevant padding citations remain
possible elsewhere. Preserve every saved experiment JSON; use fresh filenames.

For further optional work, see the [advanced-work plan](docs/advanced-plan.md):
M5 is complete and M2 is measured but disabled. The local embeddings component
targeting E05 is implemented and measured, including separate threshold calibration. Grounded LLM answering
and refusal for E11 remain a separate later experiment. No 12/12 result is
promised. The [M2 specification](specs/004-stopword-filter/spec.md) and
[implementation plan](specs/004-stopword-filter/plan.md) document the completed
experiment. Keep the plan and M2 on `main`, as requested; future work depends on time.

## Setup

Python 3.12.

```bash
python3 -m venv .venv
. .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m pytest              # or ./scripts/run_tests.sh
```

All tests pass on the starting state. Tests check mechanics, not quality; quality is measured by the eval runner.

### Optional local embeddings

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-embeddings.txt
.\.venv\Scripts\python.exe -m src.prepare_embeddings
.\.venv\Scripts\python.exe -m src.cli --retrieval-backend embeddings --question "How long until I get a new notebook computer?" --show-retrieved
```

The setup commands need network access. Subsequent retrieval uses only the
local pinned model cache in `.cache/embeddings`, on CPU. Embeddings map texts
to 384-dimensional vectors and rank the same eligible chunks by cosine
similarity in memory. The M5 filter runs before encoding. TOP_K, citation rules
and the retrieval minimum keep their existing values. Refusal uses 0.10 for
lexical scores and the separately calibrated 0.50 for embeddings cosine scores.
See the quickstart above before running full evaluation.

## Commands

| Command | What it does |
| --- | --- |
| `python -m src.cli --question "How often do passwords need to be changed?"` | Answer or refusal with citations (title, version, status) |
| `python -m src.cli --question "..." --show-retrieved` | Also prints retrieved chunks with their scores |
| `python -m src.cli --retrieval-backend embeddings --question "..." --show-retrieved` | Offline local semantic retrieval after explicit model setup |
| `python -m src.eval_runner --out results/current-verification.json` | Runs the current M1+M3+M5 code on all 12 questions; use a fresh filename for repeats |
| `python -m src.eval_compare results/before.json results/after.json` | Fixed, regressed and unchanged questions, metric deltas, changed settings |
| `python -m src.eval_compare results/before-m3.json results/after-m3.json` | Compares M1 with M1+M3: E10 fixed, no regressions, only refusal threshold changed |
| `python -m src.eval_compare results/before-m5.json results/after-m5.json` | M5: no changed pass/fail outcomes, improved citation precision, only CURRENT_ONLY changed |
| `python -m src.eval_compare docs/evidence/004-m2/before.json docs/evidence/004-m2/after.json` | Enabled M2: E09 regresses, no fixes, mean citation precision increases |
| `python -m src.eval_compare docs/evidence/004-m2/before.json docs/evidence/004-m2/retained.json` | Final state: M2 disabled; full baseline reproduced |

## Project layout

- `src/config.py`: every tunable setting in one place. The eval runner saves all values with each run.
- `src/corpus.py`: ten handbook documents with title, section, version and status.
- `src/chunking.py`, `src/retrieval.py`, `src/rag.py`: the pipeline.
- `src/embeddings.py`, `src/prepare_embeddings.py`: optional local model and in-memory cosine retrieval; explicit first-time download.
- `src/eval_runner.py`, `src/eval_compare.py`: evaluation and comparison.
- `eval/eval_set.json`: the fixed eval set.
- `docs/improvement-menu.md`: one-change options.

## Metrics

| Column | Meaning |
| --- | --- |
| `Hit` | For questions that should be answered: at least one retrieved chunk comes from an expected document |
| `Fact` | The expected fact appears in at least one cited chunk |
| `CitPrec` | Cited chunks from expected documents divided by all cited chunks (0.00 when answering a question that should be refused) |
| `Pass` | Correct behaviour (answer or refuse) and, for answered questions, the fact is cited and `CitPrec` is at least 0.50 |

## Rules for this week

1. **Do not edit `eval/eval_set.json`.** Every run prints its SHA-256; runs with different hashes cannot be compared.
2. Save the unchanged baseline before implementation. This is already preserved in `results/before.json`; do not overwrite it using the current code.
3. Measure each intentional change separately. M1 uses `before.json` / `after.json`; optional M3 uses `before-m3.json` / `after-m3.json`; M5 uses `before-m5.json` / `after-m5.json`.
4. Compare with `eval_compare` and put both runs and the comparison output in your report.

The six experiment JSON files above have exceptions in `.gitignore` and can be
tracked. Other `results/*.json` files are ignored unless explicitly added.
Include the JSON results and comparison output in the submission.
The M2 source runs and comparisons are under `docs/evidence/004-m2/`, where
they are not covered by the `results/*.json` ignore rule.

## Spec Kit

This repository uses [GitHub Spec Kit](https://github.com/github/spec-kit) 1.2.1
as optional development tooling. The Codex integration installs skills in
`.agents/skills/`; shared templates, PowerShell helpers, and project principles
are in `.specify/`. The RAG pipeline still uses only `requirements.txt`.

To reproduce the tooling installation, activate the project virtual environment
and run from the repository root:

```powershell
python -m pip install -r requirements-dev.txt
specify version
specify integration status --json
```

The repository already contains the initialized files. A fresh clone needs the
CLI installation above, not another `specify init`. The original initialization
command was:

```powershell
specify init --here --force --non-interactive --integration codex --script ps
```

The [project constitution](.specify/memory/constitution.md) records the assignment
constraints. The repository-root project is the working copy;
`rag-week-7-weak-checkpoint/` and `week06/` are preserved references.

### Use for this homework

Current experiment: [baseline, documented failures, and work order](docs/baseline.md),
[change specification](specs/001-sentence-chunking/spec.md), and
[implementation plan](specs/001-sentence-chunking/plan.md). The baseline is saved;
M1 improvement is implemented in commit `be8a881`.

M1 replaces character-based chunking with whole sentence packing
(`CHUNK_STRATEGY="sentences"`), using the existing target size of 140 characters.
Oversized sentences remain whole, without overlap. Retrieval, answering, the
corpus, evaluation questions and metrics are unchanged.

The saved [M1 report](docs/m1-report.md) records 35/35 passing tests and an
evaluation improvement from 6/12 to 9/12. E04, E06 and E09 changed from FAIL to
PASS, with no PASS-to-FAIL regressions. At the M1 stage E05, E10 and E11 fail; E06 passes
the metric but still cites both current and superseded remote-work policies.

Vedran's independent M1 verification and contributions are recorded. The optional
[M3 specification](specs/002-refusal-threshold/spec.md) and
[M3 report](docs/m3-report.md) document the subsequent threshold change and his
confirmation of manual M3 evaluation. The other pair's review and demonstration
lead remain to be finalized. M2-M6 are alternatives, not additional required
improvements; M3 is recorded separately as optional work.

The subsequent [M5 report](docs/m5-report.md) records current-version filtering,
43 passing tests, improved E06 citations and unchanged 10/12 outcomes.

The implementation workflow uses the following skills after baseline measurement
and failure documentation. These are chat skills, not PowerShell commands:

| Skill | Use |
| --- | --- |
| `$speckit-specify` | Specify one chosen improvement using observed evaluation failures. Include the hypothesis, expected effect, regression risk, and verification. |
| `$speckit-plan` | Plan that change using the existing local Python pipeline. |
| `$speckit-tasks` | Break the plan into implementation and verification tasks. |
| `$speckit-implement` | Implement the specified change and verify it. |
| `$speckit-converge` | Check whether the implementation and evidence satisfy the specification. |

`$speckit-constitution` is already applied for initial setup. Reuse it when project
principles need an amendment. The installed clarification, analysis, and checklist
skills are available when useful. There is no need to invoke every installed skill.

No extra integrations, extensions, or community presets are enabled. Git branches
and commits can be managed with ordinary Git commands. The bundled workflow is
available, but the homework can be completed using the individual skills above.

The completed measurements are linked above. Keep the required M1 and optional
M3 and M5 comparisons separate, and save any new verification to a fresh filename.
Include the actual JSON files and comparison output in the submission. The report must explain
regressions and remaining limitations. Two documented failures do not require two
fixes, and a measured hypothesis may turn out to be unconfirmed.

The skills are installed locally. If a running Codex session does not list them,
start a new session in this repository. If Windows blocks a `.ps1` helper, run
that helper with a process-local execution policy, for example:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .specify/scripts/powershell/resolve-template.ps1 constitution-template -Json
```

This does not change the persistent Windows execution policy. For upstream setup
details, see the [existing-project guide](https://github.github.io/spec-kit/guides/existing-projects.html).
