# Feature Specification: Celovite rečenice kao RAG dokaz

**Feature Branch**: `main` (planiranje; posebna implementaciona grana još nije otvorena)

**Created**: 2026-10-18

**Status**: Implementirano i izmereno — samo M1, 35/35 testova i 9/12 eval;
E04/E09 PASS, bez novih padova. [Izveštaj](../../docs/m1-report.md);
ljudski podaci i peer review čekaju dopunu pre predaje.

**Input**: Početna analiza Week 7 zadatka, sačuvan baseline i najmanje dva
konkretna eval propusta. Predlog jedne promene je M1 iz menija poboljšanja.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Potpun dokaz o roku zamene laptopa (Priority: P1)

Zaposleni pita koliko traje zamena laptopa i dobija odgovor sa proverljivim
odlomkom koji povezuje zamenu opreme sa rokom od pet radnih dana.

**Why this priority**: E04 i E09 trenutno citiraju pravi dokument, ali izostavljaju
odlomak koji sadrži rok. Prisustvo citata samo po sebi ne dokazuje tačan odgovor.

**Independent Test**: Ponoviti E04 i E09 i proveriti da li citirani tekst iz
`hb-01` sadrži `5 business days`. To je cilj hipoteze, a ne unapred utvrđen rezultat.

**Acceptance Scenarios**:

1. **Given** priručnik sa pravilom o zameni laptopa, **When** se pripremaju odlomci,
   **Then** rečenica koja povezuje zamenu i njen rok ostaje celovita u jednom odlomku.
2. **Given** pitanje E04, **When** se prikažu odgovor i citati, **Then** cilj je da
   citirani dokaz iz `hb-01` sadrži `5 business days`.
3. **Given** pitanje E09, **When** se prikažu odgovor i citati, **Then** cilj je da
   citirani dokaz iz `hb-01` sadrži isti rok; ručno proveriti i deo o mestu zahteva,
   koji automatska provera prisustva roka ne ocenjuje zasebno.

### User Story 2 - Proverljivo poređenje cele evaluacije (Priority: P2)

Autori eksperimenta mogu da pokažu šta se promenilo na svim pitanjima, uključujući
regresije i slučajeve koji ostaju neuspešni.

**Why this priority**: Promena granica odlomaka utiče i na druga pitanja.

**Independent Test**: Uporediti dva sačuvana merenja na svih 12 istih pitanja i
ručno proveriti jedan promenjen odgovor i njegov citat.

**Acceptance Scenarios**:

1. **Given** sačuvano početno merenje, **When** se izmeri jedna promena,
   **Then** oba merenja koriste identična pitanja i pravila ocenjivanja.
2. **Given** nepovoljan ili nepromenjen ishod, **When** se piše izveštaj,
   **Then** hipoteza se označava kao nepotvrđena, uz sve regresije i ograničenja.

### Edge Cases

- Prazan tekst i tekst sa samo razmacima ne proizvode odlomke.
- Završni tekst bez završne interpunkcije ostaje sačuvan.
- Cela rečenica duža od ciljne veličine ostaje jedan samostalan odlomak.
- Spojni razmak se računa u veličinu; odlomak tačno na granici je dozvoljen.
- Redosled i sadržaj rečenica ostaju očuvani, bez preklapanja susednih odlomaka.
- Nepozitivna ciljna veličina odbija se jasnom greškom.
- Jednostavna pravila granica nisu opšti jezički parser: skraćenice i završni
  navodnici ostaju dokumentovano ograničenje van sadašnjeg priručnika.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Sistem MUST pripremati dokazne odlomke od celih, uzastopnih rečenica.
- **FR-002**: Sistem MUST spajati susedne rečenice do postojeće ciljne veličine,
  uz očuvan sadržaj, interpunkciju i redosled posle ujednačavanja razmaka.
- **FR-003**: Rečenica duža od ciljne veličine MUST ostati celovita i samostalna.
- **FR-004**: Odlomci MUST čuvati poreklo, naslov, verziju i status dokumenta i
  ponovljive identifikatore za isti tekst i način podele.
- **FR-005**: Eksperiment MUST menjati samo način podele na odlomke (M1).
  Rangiranje, pravila odgovora, korpus, pitanja i ocenjivanje ostaju isti.
- **FR-006**: Eksperiment MUST sačuvati početno i završno merenje svih 12 pitanja,
  poređenje i ručnu proveru odgovora i citata.
- **FR-007**: Izveštaj MUST navesti sve regresije, ishod hipoteze i najmanje jedno
  preostalo ograničenje, čak i ako se ciljana pitanja ne poprave.

### Key Entities

- **Dokument**: Izvorno pravilo priručnika sa naslovom, verzijom i statusom.
- **Dokazni odlomak**: Jedna ili više celih rečenica iz istog dokumenta.
- **Eval pitanje**: Fiksno pitanje sa očekivanim ponašanjem, izvorom i činjenicom.
- **Merenje**: Rezultati svih pitanja sa otiskom eval skupa i uslovima rada.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001 — cilj kvaliteta**: E04 i E09 prelaze iz neuspešnih u uspešne odgovore
  sa citiranim rokom `5 business days` iz `hb-01`.
- **SC-002 — cilj kvaliteta**: Ukupno prolazi najmanje 8/12 pitanja, uz nula novih
  neuspeha među početno uspešnim E01, E02, E03, E07, E08 i E12.
- **SC-003 — obaveza eksperimenta**: Pre i posle ocenjuje se svih 12 istih pitanja;
  izveštaj navodi 100% prelazaka iz uspeha u neuspeh.
- **SC-004 — obaveza eksperimenta**: Najmanje jedan promenjen rezultat ručno je
  proveren kroz odgovor i citat. Ako se nijedan ne promeni, proverava se E04.

SC-001 i SC-002 su unapred postavljeni ciljevi hipoteze. Njihovo neostvarivanje
ne opravdava drugu promenu u istom eksperimentu; zadatak dozvoljava pošteno
izmeren i objašnjen negativan rezultat.

## Assumptions

- M1 je predlog izabran na osnovu E04/E09, pre implementacije i završnog merenja.
- Koristi se postojeći lokalni sistem i jednostavan engleski priručnik.
- Ne očekuje se rešavanje svih šest početnih propusta jednom promenom.
- Specifikacija se oslanja na [stvarno početno merenje](../../docs/baseline.md).

## Specifikacija jedne promene

| Stavka | Dogovor pre implementacije |
| --- | --- |
| Propust | E04/E09 citiraju `hb-01-chunk-0` i `hb-01-chunk-2`, bez traženog roka. Cela činjenica postoji u neizabranom `hb-01-chunk-1`. |
| Hipoteza | Očuvanje cele rečenice spaja termine o zameni laptopa i rok u isti odlomak, što može poboljšati njegovo rangiranje. |
| Promena | Isključivo M1: podela i pakovanje celih rečenica; preduga rečenica ostaje samostalna. |
| Očekivani efekat | E04 i E09 citiraju rok, bez gubitka početno uspešnih odgovora. Ovo se tek meri. |
| Rizik regresije | Promenjene dužine i granice menjaju sve skorove, izbor dokaza, preciznost citata i moguća odbijanja. |
| Provera | Svi testovi, cela ista evaluacija, poređenje sa sačuvanim baseline-om i ručna provera jednog promenjenog odgovora i citata. Tačne komande su u [quickstart.md](quickstart.md). |
