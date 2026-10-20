# Optional hybrid retrieval: E09 completeness experiment

20 October 2026. Branch: `008-hybrid-ranking`; baseline commit: `ed0f858`.

Hybrid now answers both parts of E09: request a replacement in **IT portal under
Hardware**, with handover taking **up to 5 business days after manager approval**.
It retains **12/12** on the fixed evaluation but introduces unrelated secondary
citations for E01 and E05, reducing mean citation precision from **0.9444 to
0.8333**. It remains an optional experiment. The default stays lexical.

## Observed failures and hypothesis

The unchanged [baseline](evidence/008-hybrid-ranking/baseline.md) records 86 passing
tests and two failures before pipeline implementation:

- E09's embeddings answer cites the deadline and replacement description, omitting
  the request route. The route ranks third, outside TOP_K=2. The fixed metric
  passes because it checks only `5 business days` and document-level relevance.
- E07 answers IT support hours but also cites unrelated remote-work core hours;
  its citation precision is 0.50.

The [specification](../specs/008-hybrid-ranking/spec.md) proposes one improvement:
combine complementary lexical and semantic evidence to restore E09 completeness.
The required M1 experiment and all earlier optional experiments remain separate.

## Implemented change

The new `hybrid` backend uses semantically anchored reciprocal rank fusion:

1. Filter eligible current sources, then compute the existing lexical and semantic
   rankings over the same chunks. Apply the existing raw minimum independently.
2. Fuse the complete ranked lists with equal weights, summing
   `1 / (60 + one_based_rank)` for each ranking membership. Break ties by chunk ID.
3. Keep the leading semantic candidate, then fill remaining slots from the fused
   ranking, excluding the anchor. TOP_K remains 2.

The anchor is intentional: the preimplementation
[planning diagnostic](evidence/008-hybrid-ranking/planning-diagnostic.json) found
that plain RRF fixes E09 but drops E05's useful notebook-computer deadline and
predicts a false refusal (11/12). Anchoring retains that semantic evidence.
This is a design choice motivated by known evaluation cases, not held-out evidence.
No fusion weights, model parameters, or thresholds were tuned.

Hybrid results retain raw cosine separately from their RRF score. Refusal uses
the highest raw cosine among selected evidence with the unchanged 0.51 threshold.
Missing semantic confidence fails closed. RRF scores are about 0.03, so applying
the old raw-score thresholds directly would be invalid. Anchor-first output need
not descend by pure RRF score; diagnostic CLI output labels both score types.

The corpus, chunker, model/revision, stopwords, TOP_K, source filtering, citation
selection, answer rendering, eval set, and metric calculations are unchanged.
There are no new dependencies, services, or model downloads.

## Measured results

Codex ran all commands from repository root with `.venv/Scripts/python.exe`.
Model runs used the pinned cached model with `HF_HUB_OFFLINE=1`; runtime model
loading retains `local_files_only=True`. Unit tests use controlled scores offline.

| Mode | Fixed evaluation | Mean citation precision | E09 answer complete |
| --- | --- | --- | --- |
| Baseline embeddings, cosine threshold 0.51 | 12/12 | 0.9444 | No |
| Hybrid, same cosine threshold | 12/12 | 0.8333 | Yes |
| Reproduced embeddings after changes | 12/12 | 0.9444 | No, baseline reproduced |
| Lexical before and after, threshold 0.10 | 10/12 | 0.6500 | Yes |

The full suite passes **113/113** (86 existing plus 27 new checks).
The [comparison](evidence/008-hybrid-ranking/compare.txt) reports no fixed or
regressed PASS status and a citation precision delta of **-0.1111**. The existing
lexical and embeddings runs reproduce every per-question row and summary exactly.

The comparison warns about two changed settings: backend `embeddings -> hybrid`
and newly recorded `HYBRID_RRF_CONSTANT: None -> 60`. Both describe the single
new ranking policy. The unchanged baseline was preserved rather than backfilled
with the new setting. Existing-mode reproduction shows that adding this constant
has no effect on either earlier backend.

All five complete eval files have SHA-256:
`afe46db1e75a0b85bb5c9a93b6763e3b96e5cd7b289e12da6d2671e4d8650064`.

## Answer inspection and every citation change

Codex captured actual CLI output for E01, E05, E07, E09, E10, E11, and E12, plus
all 12 actual answer texts. These executions are not claimed as independent human
verification. E10/E11/E12 still refuse without citations. E06 retains current
policy evidence. Every change to cited chunks relative to embeddings is below:

| Case | Baseline second chunk | Hybrid second chunk | Effect |
| --- | --- | --- | --- |
| E01 | Annual-leave carryover, `hb-07-chunk-1` | Remote-work allowance, `hb-03-chunk-0` | Precision 1.00 to 0.50; irrelevant secondary evidence |
| E05 | Replacement description, `hb-01-chunk-0` | Onboarding plan, `hb-06-chunk-0` | Precision 1.00 to 0.50; irrelevant secondary evidence, deadline retained |
| E09 | Replacement description, `hb-01-chunk-0` | Request location, `hb-01-chunk-2` | Both location and deadline now supported; precision stays 1.00 |

All other citations are identical to the embeddings baseline. E07's unrelated
remote-hours citation remains (precision 0.50). These content and citation
regressions matter even though PASS remains unchanged.

## Remaining limits and adoption

- Hybrid fixes the targeted E09 completeness gap but reduces aggregate citation
  relevance. Keep it opt-in for review; this result does not establish that it is
  the best default backend.
- The semantic anchor preserves only the strongest semantic evidence. It cannot
  guarantee coverage of every part of a compound question.
- One sufficiently similar selected chunk permits other selected chunks to appear
  in the extractive answer. Semantic similarity is not claim-level grounding.
- Lexical matching still counts common words, which can promote irrelevant
  secondary evidence. No stopword or citation-filter change is bundled here.
- The fixed evaluation has 12 known questions and misses E09 completeness. The
  inherited 0.51 threshold was selected after inspecting E11; this experiment's
  anchor was informed by E05. No held-out generalization claim is justified.

## Evidence and reproduction

- [Spec, plan, research, and tasks](../specs/008-hybrid-ranking/plan.md);
  [validation commands](../specs/008-hybrid-ranking/quickstart.md).
- [Before JSON](evidence/008-hybrid-ranking/before.json),
  [after JSON](evidence/008-hybrid-ranking/after.json),
  [comparison](evidence/008-hybrid-ranking/compare.txt).
- [Baseline tests](evidence/008-hybrid-ranking/pytest-before.txt),
  [final tests](evidence/008-hybrid-ranking/pytest-after.txt),
  [new offline contracts](../tests/test_hybrid.py).
- [Embeddings reproduction](evidence/008-hybrid-ranking/compare-embeddings.txt),
  [lexical reproduction](evidence/008-hybrid-ranking/compare-lexical.txt), with
  their full JSON runs beside the comparisons.
- [Before CLI](evidence/008-hybrid-ranking/cli-before.txt),
  [after CLI](evidence/008-hybrid-ranking/cli-after.txt),
  [direct E09 CLI](evidence/008-hybrid-ranking/E09-after.txt),
  [all before answers](evidence/008-hybrid-ranking/answers-before.json),
  [all after answers](evidence/008-hybrid-ranking/answers-after.json).
- [Verification](evidence/008-hybrid-ranking/verification.json),
  [source integrity](evidence/008-hybrid-ranking/integrity.json),
  [pipeline diff](evidence/008-hybrid-ranking/implementation.diff).

The user selected the E09 goal and authorized the new branch. Codex wrote the
specification and implementation, used a research agent required by the planning
skill, and executed the saved checks. Earlier contributors' work remains attributed
in the earlier reports. Independent human review of this optional experiment is
pending; no new peer approval or learner work is invented. Milan remains the
demonstration lead recorded for the earlier Week 7 work.
