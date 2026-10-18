# Tasks: M1 — celovite rečenice kao RAG dokaz

**Input**: spec.md, plan.md, research.md, data-model.md, contracts/chunking.md.
**Scope**: samo M1; testovi i puna evaluacija prema quickstart.md.

## Phase 1: Setup

- [X] T001 Proveriti postojeći `.venv`, `.gitignore` i početnih 18 testova iz root-a; pročitati `docs/baseline.md`.

## Phase 2: Foundational

- [X] T002 Proveriti SHA-256 `results/before.json` i zaštićenih fajlova prema `docs/evidence/001-baseline-manifest.json`; očuvati baseline i potvrditi specifikaciju pre koda.

## Phase 3: US1 — potpun dokaz o zameni laptopa (P1, MVP)

**Independent test**: ugovor splittera, metadata i povezivanje strategije prolaze;
cilj kvaliteta E04/E09 proverava se evaluacijom, bez pretpostavljenog uspeha.

- [X] T003 [US1] Dodati i pokrenuti testove ugovora u `tests/test_chunking.py`: prazni ulazi, whitespace, `. ! ?`, završni fragment, tačan limit i spojni razmak, duge rečenice, nepozitivan limit, očuvan sadržaj, deterministički ID/metapodaci i chars put; potvrditi pad sentence testova pre implementacije.
- [X] T004 [US1] Implementirati `split_text_by_sentences` u `src/chunking.py`: cele uzastopne rečenice, pohlepno pakovanje bez overlap-a; „Chunk može preći ciljnu veličinu samo kao jedna preduga rečenica.“; „ID ostaje `<doc_id>-chunk-<index>`, od indeksa 0, u redosledu izvornog teksta.“
- [X] T005 [US1] Aktivirati samo `CHUNK_STRATEGY="sentences"` u `src/config.py`; potvrditi povezivanje kroz `tests/test_chunking.py` i pokrenuti sve testove, izlaz sačuvati u `docs/evidence/001-pytest-after.txt`.

## Phase 4: US2 — proverljivo poređenje evaluacije (P2)

**Independent test**: oba JSON-a imaju svih 12 pitanja i isti eval SHA-256;
poređenje navodi sve promene i regresije, a CLI potvrđuje bar jedan promenjen ishod.

- [X] T006 [US2] Pokrenuti neizmenjen `src.eval_runner` u `results/after.json` i sačuvati izlaz u `docs/evidence/001-eval-after.txt`; očuvati JSON tačnim izuzetkom u `.gitignore`.
- [X] T007 [US2] Pokrenuti `src.eval_compare` nad `results/before.json` i `results/after.json`, sačuvati `docs/evidence/001-eval-compare.txt`; potvrditi isti otisak i samo jedno izmenjeno podešavanje.
- [X] T008 [US2] Ručno pregledati E04/E09 i bar jedan promenjeni ishod kroz `src.cli --show-retrieved`; sačuvati odgovore i citate u `docs/evidence/001-cli-after.txt`.
- [X] T009 [US2] Napisati izmereni izveštaj u `docs/m1-report.md`: hipoteza, sve metrike, regresije, preostala ograničenja, AI i provera; jasno ostaviti ljudski peer review, doprinose i demo lead za stvarne učesnike.

## Phase 5: Polish

- [X] T010 Pregledati diff i hash zaštitu za `eval/eval_set.json`, metrics kod, baseline i reference; sačuvati implementacioni diff u `docs/evidence/001-implementation.diff` i ažurirati status u `specs/001-sentence-chunking/plan.md` i `spec.md`.

## Dependencies & execution

T001 → T002 → T003 → T004 → T005 → T006 → T007 → T008 → T009 → T010.
US2 meri rezultat US1. Nema novih modela niti infrastrukture.
MVP je US1; obavezni eksperiment uključuje i US2 i završni pregled.

## Parallel opportunities

US1: provere sentence ugovora i chars puta mogu se izvršiti zajedno u pytest-u.
US2: posle T006 poređenje i CLI čitanje mogu teći paralelno, u različite logove.
Zbog malog obima zadaci su planirani sekvencijalno, bez delegiranja.

## Implementation strategy

Najpre potvrditi početne dokaze; napisati testove pre splittera, aktivirati M1,
zatim izmeriti ceo skup i dokumentovati stvarni ishod. Negativna hipoteza ne
pokreće dodatno podešavanje ili M2–M6. Ljudski review nije simuliran AI-jem.
