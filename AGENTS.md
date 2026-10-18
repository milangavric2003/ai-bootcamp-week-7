# Repository guidance

Read `.specify/memory/constitution.md` and `docs/weekly-assignment.md` before
planning or implementing the Week 7 experiment.

- Work on the repository-root `src/`, `tests/`, `eval/`, and `docs/` directories.
- Preserve `rag-week-7-weak-checkpoint/` as the original starter and `week06/` as
  reference material.
- Save the unchanged baseline and document at least two evaluation failures before
  implementation. Write the specification before changing the RAG pipeline.
- Implement exactly one intentional improvement for the required homework.
  M1-M6 are alternatives; fixing every documented failure is not required.
- Do not change `eval/eval_set.json` or the code that calculates evaluation metrics.
- Run commands from the repository root with the project virtual environment:
  `python -m pytest`, the before/after eval runner, and `src.eval_compare`.
- Keep Spec Kit skills in `.agents/skills/`. Use the installed `$speckit-*` skills
  for feature work and read their instructions when invoked.
- On Windows, if script execution is restricted, invoke a reviewed Spec Kit helper
  with `powershell.exe -NoProfile -ExecutionPolicy Bypass -File <script> <args>`.
  This applies only to that process; no persistent execution-policy change is needed.
- Keep setup and tooling changes separate from the measured RAG improvement.

See the Spec Kit section of `README.md` for installation and the homework workflow.
