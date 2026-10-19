# M2 research decisions

Prepared before implementation, 19 October 2026. No filtered evaluation variants
were run to select the word list. A read-only research agent independently checked
the proposed list and current tokenization/scoring path.

## Fixed general English list

- Decision: Freeze the exact 40 unique function/question words in plan.md and use
  the same list on both inputs. No dependency or language download.
- Rationale: Implements M2's about-40-word scope reproducibly. The existing flag
  and tokenize function are sufficient; no domain or evaluation rules are needed.
- Alternatives considered: A library list adds unnecessary dependencies; expanding
  the list after seeing eval outcomes overfits the experiment; synonyms are separate.

## Qualifiers and score scale

- Decision: Preserve negative words, `until`, and numbers. Keep thresholds unchanged.
- Rationale: They may express the fact a user needs. Filtering changes both overlap
  counts and chunk length, so scores may rise or fall; effects must be measured.
- Risk identified before implementation: existing lowercasing maps the acronym
  `IT` to the stopword `it`. The frozen generic list is still used unchanged;
  inspect IT-support and equipment answers rather than adding a domain exception.
- Alternatives considered: Joint threshold calibration would be a second intent;
  preserving the old denominator would change the defined M2 experiment.

## Failure boundaries and verification

- Decision: Expect reduced common-word noise, not a promised E05/E11 repair. Check
  empty/all-stopword inputs, both modes, content repetitions, scoring and false matches.
- Rationale: Removing words cannot infer notebook/laptop equivalence or prove that
  annual leave rules answer parental leave. An unsupported query may still score high.
- Alternatives considered: Embeddings target E05; a later grounded LLM with explicit
  refusal can test E11. Neither belongs in M2 or is guaranteed to fix its target.

No external API, model selection, package installation, or additional research is needed.
