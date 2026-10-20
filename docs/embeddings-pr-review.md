# Internal review of the embeddings branch

20 October 2026. Internal reviewer: **Milan**. Branch contributor: **Vedran**.
Milan requested this review before approving the PR into `main`; Codex inspected
the code and executed the checks below. On 20 October 2026, Milan confirmed his
approval in the conversation after discussing the E09 omission, E07 citation
precision and limits of tuning on the known eval set. He approved merging this
branch as an optional experiment with those limitations documented.
Milan will perform the GitHub PR approval and merge manually after committing
and pushing the documentation updates.

Reviewed head: `c290ffd9dbddb5b989409334b4c487c0d62f3d22`.
Base: `0615f72b0a3966ced38d55a76b573aac68dc6535` (`main`). A live
`git ls-remote` check confirmed both remote branch tips match these commits.
GitHub PR comments, approval state and CI checks were not inspected.

The code is suitable for merging as an **optional experiment**, with the
limitations below. The default lexical backend is preserved. The required M1
experiment remains separate; this PR contains three separately recorded advanced
stages: embeddings retrieval, backend-specific threshold calibration, and the
eval-informed adjustment from 0.50 to 0.51.

## Verification

Codex used the project virtual environment from the repository root, with Python
3.13.7 and sentence-transformers 6.1.0. All **86 tests passed**. Fresh complete
12-question runs, using `python -m src.eval_runner --out <fresh file>`, reproduced
the saved per-question rows and summaries exactly:

| Backend | Threshold | Passed | Mean citation precision |
| --- | --- | --- | --- |
| Default lexical | 0.10 | 10/12 | 0.6500 |
| Optional embeddings | 0.51 | 12/12 | 0.9444 |

`src.eval_compare` reports E05 and E11 fixed and no PASS-to-FAIL regressions.
The fresh backend comparison changes only `RETRIEVAL_BACKEND`. Comparison with
the older lexical baseline warns about newly added configuration keys; all its
existing settings, question results and aggregate metrics are unchanged.
The separate 0.50-to-0.51 comparison changes only `EMBEDDING_REFUSAL_THRESHOLD`.

Both fresh runs use eval SHA-256
`afe46db1e75a0b85bb5c9a93b6763e3b96e5cd7b289e12da6d2671e4d8650064`.
The eval set, metric runner, comparison code, corpus, chunker and original M1
before/after files are unchanged from `main`.

CLI checks covered E04, E05, E06, E07, E09, E10 and E11 with
`HF_HUB_OFFLINE=1` and socket connection attempts blocked. E05 cites the five
business day deadline; E06 uses current policy; E10/E11 refuse without citations.
The cached model loads locally and reports 384 dimensions. Code review also
checked lazy optional dependencies, the pinned model revision, cache keys,
filtering before encoding, signed cosine ranking and backend-specific refusal.

## Findings and limits

- **E09 loses part of the answer.** Lexical retrieval cites `hb-01-chunk-2`
  (`IT portal / Hardware`) and `hb-01-chunk-1` (the deadline). Embeddings instead
  cites `hb-01-chunk-1` and `hb-01-chunk-0`, so it answers how long but omits where
  to request the laptop. Both runs pass because the fixed metric checks the
  deadline only. This is an answer-content regression despite no PASS-to-FAIL
  regression; the existing metrics were preserved.
- **E07 citation precision falls from 1.00 to 0.50.** The correct IT support
  hours are accompanied by unrelated remote-work core hours. The 0.51 threshold
  applies to the leading score; it does not remove weaker secondary citations.
- **12/12 is measured on the known eval set.** The 0.51 threshold was selected
  after inspecting E11, so this is reproduction, not held-out validation.
  Semantic similarity still does not establish answer support; the calibration
  report also retains the unsupported D08 case.

These limitations are documented within the scope of this optional experiment; no
additional pipeline improvement was introduced during review. Follow-up work
would need its own specification and measurements.

## Evidence and attribution

[Verification manifest](evidence/milan-embeddings-review-20261020/verification.json),
[test output](evidence/milan-embeddings-review-20261020/pytest.txt),
[lexical run](evidence/milan-embeddings-review-20261020/lexical.json),
[embeddings run](evidence/milan-embeddings-review-20261020/embeddings.json),
[backend comparison](evidence/milan-embeddings-review-20261020/compare-backends.txt),
[lexical reproduction](evidence/milan-embeddings-review-20261020/compare-lexical-reproduction.txt),
[embeddings reproduction](evidence/milan-embeddings-review-20261020/compare-embeddings-reproduction.txt),
[threshold comparison](evidence/milan-embeddings-review-20261020/compare-thresholds.txt),
and [CLI output](evidence/milan-embeddings-review-20261020/cli-embeddings.txt).

Vedran's implementation decisions and independent verification remain attributed
in the [0.51 report](threshold-051-report.md). Milan is the internal reviewer for
this PR; the new executions and documentation in this review were performed by
Codex at his request. They are not claimed as Milan's independent manual runs.

The assignment's review by another pair and the demonstration lead are still
unrecorded in the M1 report. This internal PR review does not complete those
submission requirements. No PR approval or merge was performed by Codex.
