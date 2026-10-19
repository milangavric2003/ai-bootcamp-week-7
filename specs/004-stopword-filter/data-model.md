# M2 data model

No persistent schema changes.

| Entity | Fields and constraints | Relationship |
| --- | --- | --- |
| Stopword vocabulary | Exactly 40 unique lowercase words, immutable, frozen in plan.md | Applied symmetrically to query and chunk tokens |
| Token stream | Ordered lowercase alphanumeric tokens; repetitions and numeric tokens retained unless in the vocabulary | Existing input to lexical_score |
| Evaluation run | Existing config snapshot, fingerprint, all 12 rows and aggregate metrics | Before and after share the same eval fingerprint |

Filtering may yield an empty stream. Its score is zero; with the existing positive
retrieval minimum, no such result is returned. Disabling the flag reproduces the
baseline. No new fields, migrations or state transitions are introduced.
