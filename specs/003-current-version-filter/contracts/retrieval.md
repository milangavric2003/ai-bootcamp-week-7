# Contract: Current-version filtering

The existing internal searchable_chunks(chunks) hook remains the interface.

- Disabled: retain all input candidates in their existing order.
- Enabled: exclude status superseded, preserving the remaining order.
- Empty input or no eligible candidates: return an empty list.
- Do not mutate candidates or metadata.
- Filter before scoring/top-k; preserve existing scoring and tie rules.

Public CLI and evaluation syntax remain unchanged. Empty eligible retrieval
follows the existing refusal path. Both retrieved and cited chunks must exclude
superseded sources when enabled.
