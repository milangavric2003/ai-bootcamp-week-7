# Week 7: početno stanje i plan rada

Početna provera je završena 18. oktobra 2026, pre promene RAG pipeline-a.
**18/18 automatizovanih testova prolazi; eval prolazi na 6/12 pitanja.**
Zadatak traži najmanje dva propusta u kvalitetu odgovora na eval pitanjima.
Ne traži da postojeći `pytest` testovi padaju.

## Sačuvani dokazi

| Dokaz | Fajl |
| --- | --- |
| Originalni baseline sa svim rezultatima i konfiguracijom | [results/before.json](../results/before.json) |
| Eval tabela izvedena iz tog sačuvanog JSON-a | [001-eval-before.txt](evidence/001-eval-before.txt) |
| Stvarni izlaz početnih testova | [001-pytest-before.txt](evidence/001-pytest-before.txt) |
| Stvarni CLI odgovori i retrieved odlomci za svih šest propusta | [001-failures-cli-before.txt](evidence/001-failures-cli-before.txt) |
| Commit, verzije, konfiguracija i SHA-256 fajlova početnog stanja | [001-baseline-manifest.json](evidence/001-baseline-manifest.json) |

Izmereni kod: commit `d28cfcf1a1aa5f312acef2109958907fc65ce5fb`.
Svih 16 fajlova iz `src/`, `tests/` i `eval/` bajt-po-bajt je identično
sačuvanom starteru u `rag-week-7-weak-checkpoint/`.

Eval SHA-256:
`afe46db1e75a0b85bb5c9a93b6763e3b96e5cd7b289e12da6d2671e4d8650064`.

SHA-256 sačuvanog `results/before.json`:
`b5d400c79fad025926b3ef5e81a005508e32389596e8fed6e4c46d0654eac5cd`.
Ovaj fajl se više ne prepisuje. Izuzetak u `.gitignore` omogućava njegov commit.

## Komande i okruženje

Pokrenuto iz root-a repozitorijuma postojećim virtualenv interpreterom:

```powershell
.venv/Scripts/python.exe -m pytest
.venv/Scripts/python.exe -m src.eval_runner --out results/before.json
```

Python je **3.13.7**, pytest **8.3.3**. README navodi Python 3.12; postojeće
okruženje je zadržano i oba merenja treba raditi istim interpreterom.
Prvi sandbox pokušaj testova imao je `17 passed, 1 error` zbog zabrane pristupa
Windows privremenom direktorijumu pri pripremi `tmp_path` fixture-a. Ista komanda
van sandboxa prolazi svih 18 testova. To je problem izvršnog okruženja, ne eval
propust niti izmena sistema. Sačuvani log je iz uspešnog pokretanja.

## Rezultati svih 12 pitanja

| ID | Očekivano | Dobijeno | Hit | Fact | CitPrec | Ishod |
| --- | --- | --- | --- | --- | --- | --- |
| E01 | answer | answer | da | da | 0.50 | PASS |
| E02 | answer | answer | da | da | 0.50 | PASS |
| E03 | answer | answer | da | da | 0.50 | PASS |
| E04 | answer | answer | da | ne | 1.00 | FAIL |
| E05 | answer | answer | ne | ne | 0.00 | FAIL |
| E06 | answer | answer | ne | ne | 0.00 | FAIL |
| E07 | answer | answer | da | da | 1.00 | PASS |
| E08 | answer | answer | da | da | 0.50 | PASS |
| E09 | answer | answer | da | ne | 1.00 | FAIL |
| E10 | refuse | answer | — | — | 0.00 | FAIL |
| E11 | refuse | answer | — | — | 0.00 | FAIL |
| E12 | refuse | refuse | — | — | — | PASS |

Precizne zbirne metrike: `passed=6`, `total=12`,
`behaviour_accuracy=0.8333`, `retrieval_hit_rate=0.7778`,
`mean_citation_precision=0.4545`.
`Hit` meri prisustvo očekivanog dokumenta, a `Fact` činjenicu u citiranom tekstu.
Zato E04/E09 padaju iako im je preciznost citata prema dokumentu 1.00.

## Dva propusta izabrana za specifikaciju

### E04 — rok zamene laptopa nedostaje u citiranim odlomcima

- **Pitanje:** `How many business days does a laptop replacement take?`
- **Očekivano:** odgovor iz `hb-01` sa činjenicom `5 business days`.
- **Stvarno:** odgovor citira `hb-01-chunk-0` (0.217391) i
  `hb-01-chunk-2` (0.173913), bez celog traženog roka.
- **Tip:** chunkovanje / retrieval rangiranje / nepotpun odgovor.
- **Dokaz uzroka:** `hb-01-chunk-1` sadrži ceo literal `5 business days`, ali mu
  je skor 0.107143 i nije među top-2. Rečenica počinje u prvom odlomku, dok
  srednji čuva rok bez početnog izraza `replacement laptop`.

### E09 — pronađeno mesto zahteva, izostavljen rok

- **Pitanje:** `Where do I request a replacement laptop and how long does it take?`
- **Očekivano:** odgovor iz `hb-01` sa `5 business days`; priručnik mesto zahteva
  navodi kao IT portal, Hardware.
- **Stvarno:** citira `hb-01-chunk-0` (0.260870) i `hb-01-chunk-2` (0.217391).
  Drugi odlomak sadrži mesto zahteva, ali nijedan citirani odlomak ne sadrži rok.
- **Tip:** chunkovanje / retrieval rangiranje / nepotpun odgovor.
- **Dokaz uzroka:** odlomak `hb-01-chunk-1` sa rokom ima skor 0.142857 i ispada
  iz top-2. Automatski eval za E09 proverava rok, a deo o mestu zahteva treba
  dodatno proveriti ručno.

Oba propusta su posebna eval pitanja sa istim mehanizmom greške. Zadatak ne
zahteva dva različita tipa propusta. Precizno: činjenica postoji u indeksu,
ali ne dospeva u citirani odgovor; nije potpuno izgubljena sečenjem teksta.

Komande za ručnu reprodukciju:

```powershell
.venv/Scripts/python.exe -m src.cli --question "How many business days does a laptop replacement take?" --show-retrieved
.venv/Scripts/python.exe -m src.cli --question "Where do I request a replacement laptop and how long does it take?" --show-retrieved
```

## Ostali uočeni propusti

| ID | Očekivano | Stvarno | Tip |
| --- | --- | --- | --- |
| E05 | `How long until I get a new notebook computer?` → `hb-01`, `5 business days` | Citira `hb-06-chunk-0` (0.153846) i `hb-07-chunk-1` (0.083333), bez očekivanog dokumenta ili roka. | Retrieval: parafraza i nepovezani odlomci. |
| E06 | `How many days per week can I work remotely?` → `hb-03`, `3 days per week` | Citira samo `hb-02-chunk-0` (0.481481) i `hb-02-chunk-1` (0.400000), politiku 2024, `superseded`, sa 2 dana. | Zastarela verzija / pogrešan odgovor. |
| E10 | `What is the current company stock price?` → odbijanje | Odgovara uz `hb-09-chunk-1` (0.058824) i `hb-05-chunk-1` (0.052632), koji nemaju cenu akcija. | Pogrešno prihvatanje nepodržanog pitanja. |
| E11 | `What is the parental leave policy?` → odbijanje | Citira godišnji odmor: `hb-07-chunk-1` (0.166667), `hb-07-chunk-0` (0.160000). Korpus ne opisuje roditeljsko odsustvo. | Pogrešan odgovor / izostalo odbijanje. |

Ove propuste pratimo u ponovnom merenju. M1 ne uvodi posebno rešavanje sinonima,
filtriranje verzija niti promenu praga odbijanja.

## Plan rada i Spec Kit

Spec Kit je već instaliran i constitution postoji. Nije potrebna nova instalacija.
Posle baseline-a napravljeni su [specifikacija](../specs/001-sentence-chunking/spec.md)
veštinom `$speckit-specify` i [tehnički plan](../specs/001-sentence-chunking/plan.md)
veštinom `$speckit-plan`. Izabrana je jedna hipoteza: M1, cele rečenice.

1. **Završeno:** pregled zadatka i prezentacije, testovi, baseline i dokumentovani
   propusti. Originalni starter i Week 6 referenca ostaju sačuvani.
2. **Završeno:** specifikacija, plan, istraživačke odluke i vodič za proveru.
   Efekat M1 još nije izmeren.
3. **Sledeće — `$speckit-tasks`:** napraviti `tasks.md` iz specifikacije i plana.
4. **Zatim — `$speckit-implement`:** realizovati isključivo M1, uz provere podele
   rečenica. Implementacioni diff ograničiti na chunking, aktivaciju strategije
   i relevantne testove.
5. Pokrenuti sve testove i isti eval runner sa `--out results/after.json`.
   Sačuvati završni JSON za predaju i izlaz `src.eval_compare`.
6. Ručno proveriti promenjeno pitanje, odgovor i citat; ako promena rezultata
   izostane, proveriti E04 i navesti nepotvrđenu hipotezu.
7. Napisati izveštaj pre/posle: sve regresije, najmanje jedno ograničenje, AI
   beleška, doprinos oba člana i demo lead. Zatim pribaviti i priložiti peer review.

Prelazak na cele rečenice može pomoći da termini pitanja i rok budu zajedno,
ali duža rečenica može imati niži leksički skor. Ne povećavamo top-k niti menjamo
prag da bismo naknadno dobili poželjan rezultat iste hipoteze.

U `docs/` trenutno nema zasebnog najavljenog šablona izveštaja pre/posle.
Dok se ne dobije, sadržaj izveštaja prati obavezne stavke nedeljnog zadatka;
ovaj dokument je početna evidencija, ne završen izveštaj za predaju.
Imena članova, njihovi stvarni doprinosi, Week 7 demo lead i komentar drugog para
popunjavaju se sa ljudima pre predaje. Ne preuzimaju se automatski iz Week 6.

Rokovi iz lokalnog zadatka, vreme Beograd: peer review 19. oktobra do 20:00;
predaja 20. oktobra 2026. do 12:00; Sesija 2 je 21. oktobra.

## AI i provera u ovoj fazi

Codex je korišćen za pregled lokalnih fajlova i Git istorije, izvršavanje testova
i evaluacije, analizu citiranih odlomaka i pisanje dokumentacije i plana.
Read-only istraživački agent proverio je ugovor M1 i regresione rizike prema
koraku istraživanja u `$speckit-plan`. Zaključci o baseline-u zasnivaju se na
sačuvanim rezultatima i stvarnom CLI izlazu. Nije menjan pipeline, fiksni eval
skup, računanje metrika, originalni starter ili Week 6 referenca.

Predlog commit poruke za ovu fazu:

```text
docs: record Week 7 baseline failures and sentence chunking plan
```
