# Implementation Plan: M1 — podela po celim rečenicama

**Branch**: `main` | **Date**: 2026-10-18 | **Spec**: [spec.md](spec.md)

**Feature directory**: `specs/001-sentence-chunking/`. Identifikator feature-a
koji helper prikazuje kao `BRANCH` nije nova Git grana; stvarna grana je `main`.

**Status**: Plan spreman za `$speckit-tasks`. Implementacija nije započeta.

## Summary

Sačuvan baseline prolazi 6/12 eval pitanja i svih 18 testova. E04/E09 ne citiraju
rok zamene laptopa, iako on postoji u `hb-01-chunk-1`. Planira se isključivo M1:
implementirati postojeću sentence strategiju i aktivirati je. Cilj je da cela
rečenica zadrži zajedno temu i rok; poboljšanje top-2 izbora ostaje hipoteza.

## Technical Context

**Language/Version**: Postojeći `.venv`, Python 3.13.7; README preporučuje 3.12.
Oba merenja koriste postojeći isti interpreter; migracija nije deo eksperimenta.

**Primary Dependencies**: Standardna biblioteka; pytest 8.3.3 za testove.
Već instalirani Spec Kit 1.2.1 je odvojeni razvojni alat.

**Storage**: Priručnik u `src/corpus.py`; lokalni JSON rezultati u `results/`.

**Testing**: Svih 18 postojećih testova, smislene provere sentence splittera,
celih 12 fiksnih eval pitanja i ručna CLI provera odgovora/citata.

**Target Platform**: Lokalni CLI; merenje na Windows-u, iz root-a repozitorijuma.

**Project Type**: Mala Python CLI aplikacija.

**Performance Goals**: Deterministička lokalna obrada 10 dokumenata i 12 pitanja.
Nema novog zahteva za latenciju ni tvrdnje o izmerenom ubrzanju.

**Constraints**: Jedna namera (M1), bez novih paketa ili servisa; ne menjati
korpus, eval pitanja, računanje metrika, retrieval ili pravila odgovora.

**Scale/Scope**: `src/chunking.py`, aktivacija u `src/config.py`, relevantni
testovi; dokumentacija i dokazni fajlovi odvojeni od implementacionog diff-a.

## Constitution Check

| Princip | Pre dizajna | Posle dizajna |
| --- | --- | --- |
| Jedna kontrolisana promena | PASS: samo M1 | PASS: jedan splitter i aktivacija strategije; bez drugih podešavanja |
| Fiksna evaluacija | PASS: sačuvan otisak i ceo baseline | PASS: isti runner, isti skup i nepromenjene metrike |
| Dokazi pre implementacije | PASS: 18 testova, 6/12 eval i konkretni propusti | PASS: spec i plan postoje pre izmena koda |
| Lokalno i jednostavno | PASS: postojeći lokalni sistem | PASS: standardna biblioteka, bez infrastrukture |
| Pošten izveštaj | PASS za plan: početni dokazi su sačuvani | PASS za dizajn: obavezne regresije, ograničenja i ljudski review; završni dokazi tek slede |

Izvor: [constitution](../../.specify/memory/constitution.md). Nema odstupanja
koja zahtevaju opravdanje. Ove provere potvrđuju plan, ne završen zadatak.

## Project Structure

### Documentation (this feature)

```text
specs/001-sentence-chunking/
  spec.md
  checklists/requirements.md
  plan.md
  research.md
  data-model.md
  contracts/chunking.md
  quickstart.md
  tasks.md                    # sledeća faza; još ne postoji
docs/
  baseline.md
  evidence/001-*
results/before.json
```

### Source Code (repository root)

```text
src/chunking.py                # implementirati postojeći sentence stub
src/config.py                  # jedina izmena podešavanja: CHUNK_STRATEGY
tests/test_chunking.py          # provere ugovora sentence splittera
tests/test_rag.py               # po potrebi provera povezivanja strategije
src/retrieval.py                # ostaje postojeći scorer
src/rag.py                      # ostaju postojeća pravila odgovora
src/eval_runner.py              # zaštićeno: ne menjati
src/eval_compare.py             # zaštićeno: ne menjati
eval/eval_set.json              # zaštićeno: ne menjati
```

**Structure Decision**: Nastaviti postojeći root projekat. `week06/` i
`rag-week-7-weak-checkpoint/` služe kao reference i ne menjaju se.

## Phase 0 — istraživačke odluke

Završeno u [research.md](research.md): tačan uzrok E04/E09, jednoznačan ugovor
granice rečenice, tretman dugih rečenica i rizici rangiranja. Nema nerešenih
tehničkih pitanja ni novih zavisnosti. Lokalni pregled je dovoljan za dizajn.

## Phase 1 — dizajn

1. U postojećem `split_text_by_sentences` normalizovati razmake, razdvojiti
   rečenice posle `.`, `!` ili `?` kada sledi whitespace, zatim redom pakovati
   cele rečenice do `CHUNK_SIZE`, računajući spojni razmak.
2. Rečenicu dužu od limita zadržati samostalno. Relevantna rečenica iz `hb-01`
   ima 163 karaktera: mora ostati cela iako je cilj 140.
3. Sentence strategija nema overlap. `CHUNK_OVERLAP=30` ostaje nepromenjen zapis
   konfiguracije i koristi se samo u postojećem `chars` putu.
4. Aktivirati `CHUNK_STRATEGY="sentences"`. Sve ostale vrednosti ostaju iz baseline-a.
5. Očuvati `build_chunks`, format ID-jeva i metapodatke. ID-jeve proveravati sa
   konfiguracijom odgovarajućeg merenja jer isti indeks može označavati drugi tekst.

Podaci i ugovor su u [data-model.md](data-model.md) i
[contracts/chunking.md](contracts/chunking.md); postupak provere u
[quickstart.md](quickstart.md).

## Nastavak i proveravanje ishoda

Sledeći korak je `$speckit-tasks`, pa `$speckit-implement`.
Najpre proveriti ugovor sentence strategije i nepromenjen `chars` put, potom
sve testove i pun eval sa `--out results/after.json`, pa `src.eval_compare`.
Ne prepisivati `results/before.json`. Završni JSON eksplicitno uključiti u Git
ili priložiti predaji, jer je podrazumevano ignorisan.

Željeni ishod su E04/E09 PASS, najmanje 8/12 i bez novih FAIL slučajeva. Ako to
izostane, sačuvati stvarni rezultat i objasniti hipotezu, bez dodavanja M2–M6.
Ručno proveriti jedan promenjen rezultat, a ako promena nema, E04. U izveštaj
uključiti sve regresije, preostala ograničenja, AI belešku, stvarne doprinose
oba člana, Week 7 demo lead i komentar drugog para.
