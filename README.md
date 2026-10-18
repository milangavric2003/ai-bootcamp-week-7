# Week 7 RAG checkpoint

A small local question-answering tool over a fictional employee handbook. It retrieves chunks, answers with chunk citations and refuses questions the handbook does not cover. It runs offline: no API keys, no network, no paid services.

This week you will **measure** this system on a fixed eval set, find failures, apply **exactly one** improvement and compare results before and after.

## Setup

Python 3.12.

```bash
python3 -m venv .venv
. .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m pytest              # or ./scripts/run_tests.sh
```

All tests pass on the starting state. Tests check mechanics, not quality; quality is measured by the eval runner.

## Commands

| Command | What it does |
| --- | --- |
| `python -m src.cli --question "How often do passwords need to be changed?"` | Answer or refusal with citations (title, version, status) |
| `python -m src.cli --question "..." --show-retrieved` | Also prints retrieved chunks with their scores |
| `python -m src.eval_runner --out results/before.json` | Runs all 12 questions, prints the table and summary, saves the run |
| `python -m src.eval_compare results/before.json results/after.json` | Fixed, regressed and unchanged questions, metric deltas, changed settings |

## Project layout

- `src/config.py`: every tunable setting in one place. The eval runner saves all values with each run.
- `src/corpus.py`: ten handbook documents with title, section, version and status.
- `src/chunking.py`, `src/retrieval.py`, `src/rag.py`: the pipeline.
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
2. Run the baseline first: `python -m src.eval_runner --out results/before.json`.
3. Change one thing (see `docs/improvement-menu.md`), then run the same command with `--out results/after.json`.
4. Compare with `eval_compare` and put both runs and the comparison output in your report.

Result files in `results/` are ignored by git. Copy the printed tables into your report.

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
PASS, with no PASS-to-FAIL regressions. E05, E10 and E11 still fail; E06 passes
the metric but still cites both current and superseded remote-work policies.

Implementation and measurement are complete. Independent verification, the
other pair's review, contributor details and the demonstration lead remain to
be finalized for submission. M2-M6 are alternatives, not additional required
improvements.

First run the unchanged baseline and document at least two failures. Then invoke
the skills in Codex chat, one step at a time. These are chat skills, not PowerShell
commands:

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

Before implementation, save `results/before.json`. After the single change, run
the tests, save `results/after.json`, and compare both runs using the commands
above. Include the actual JSON files and comparison output in the submission;
the JSON files are ignored by Git unless explicitly added. The report must explain
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
