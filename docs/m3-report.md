# Dodatni eksperiment — M3: prag odbijanja

Datum: 19. oktobar 2026. Status: implementirano i izmereno, 10/12 bez regresija.
Ovo je dodatni eksperiment u odnosu na M1, ne deo jedne obavezne M1 promene.
[M1 izveštaj](m1-report.md) i njegovi originalni JSON rezultati ostaju sačuvani.
Predaja minimuma nije potvrđena; po Vedranovom izričitom zahtevu eksperiment
je urađen sada, iako zadatak napredni deo predviđa posle predatog minimuma.

## Specifikacija i promena

[Specifikacija](../specs/002-refusal-threshold/spec.md),
[plan](../specs/002-refusal-threshold/plan.md) i
[zadaci](../specs/002-refusal-threshold/tasks.md) napisani su pre promene koda.
Nisu posebno commitovani pre implementacije; redosled je zabeležen u ovoj sesiji.

E10 (`What is the current company stock price?`) nije pokriven korpusom, ali
M1 odgovara odlomcima o MFA i parkingu. Najbolji skor 0.076923 prelazi stari
prag 0.02. Hipoteza: podizanje praga na 0.10 odbija E10 bez gubitka devet
postojećih prolaza. Rizik je pogrešno odbijanje podržanog pitanja sa slabim skorom.

Jedina implementaciona promena u `src/config.py`:

```diff
-REFUSAL_THRESHOLD = 0.02
+REFUSAL_THRESHOLD = 0.10
```

M1 sentence chunking, TOP_K=2, rangiranje, korpus, eval skup i metrike ostaju
nepromenjeni. M3 ne filtrira pojedinačne citate i ne poboljšava rangiranje.

## Rezultati pre/posle

Okruženje oba nova merenja: Windows, Python 3.14.7, pytest 8.3.3.
Novo pre-merenje u potpunosti odgovara sačuvanom M1 `results/after.json`
po konfiguraciji, otisku skupa, zbirnim metrikama i svim rezultatima pitanja.

| Metrika | M1 / pre | M1 + M3 / posle | Razlika |
| --- | --- | --- | --- |
| Prolazna pitanja | 9/12 | 10/12 | +1 |
| Behaviour accuracy | 0.8333 | 0.9167 | +0.0834 |
| Retrieval hit rate | 0.8889 | 0.8889 | 0 |
| Mean citation precision | 0.5455 | 0.6000 | +0.0545 |
| Testovi | 35/35 | 35/35 | 0 |

Jedini FAIL → PASS je **E10**. Nema PASS → FAIL regresija.
E01–E04, E06–E09 i E12 ostaju PASS; E05 i E11 ostaju FAIL.
Jedino promenjeno podešavanje u poređenju: `REFUSAL_THRESHOLD: 0.02 -> 0.1`.
Zbirna preciznost citata raste zato što se odbijeni E10 više ne računa među
odgovorenim pitanjima; citati ostalih odgovora nisu postali precizniji.

Oba nova rezultata imaju eval SHA-256:
`afe46db1e75a0b85bb5c9a93b6763e3b96e5cd7b289e12da6d2671e4d8650064`.
Hash provera izvora, testova, eval skupa i originalnih M1 JSON rezultata
potvrđuje da je izmenjen samo `src/config.py`.

## CLI provera

- E10: sada `Refused: True`, `Citations: None` i poruka
  `I do not have enough grounded evidence in the provided corpus to answer that question.`
  Retrieved i dalje prikazuje iste slabe odlomke, ali oni nisu citirani kao odgovor.
- E04: ostaje odgovor sa celom rečenicom o roku do pet radnih dana nakon
  odobrenja menadžera. Najbolji skor 0.206897 ostaje iznad novog praga.
- E11: i dalje odgovara o godišnjem odmoru umesto da odbije pitanje o
  roditeljskom odsustvu; skor 0.222222 je iznad praga.

## Dokazi i reprodukcija

Svi novi dokazi su u [evidence/002-m3](evidence/002-m3/), izvan ignorisanih
`results/*.json`, tako da mogu normalno da se dodaju u Git.

| Dokaz | Fajlovi |
| --- | --- |
| Nova puna merenja | [before.json](evidence/002-m3/before.json), [after.json](evidence/002-m3/after.json) |
| Eval tabele | [pre](evidence/002-m3/eval-before.txt), [posle](evidence/002-m3/eval-after.txt) |
| Poklapanje polaznog stanja sa M1 | [compare-m1.txt](evidence/002-m3/compare-m1.txt) |
| Poređenje M3 pre/posle | [compare.txt](evidence/002-m3/compare.txt) |
| Testovi | [pre](evidence/002-m3/pytest-before.txt), [posle](evidence/002-m3/pytest-after.txt) |
| E10 CLI | [pre](evidence/002-m3/E10-before.txt), [posle](evidence/002-m3/E10-after.txt) |
| Kontrolni CLI slučajevi | [E04](evidence/002-m3/E04-after.txt), [E11](evidence/002-m3/E11-after.txt) |
| Integritet | [polazni manifest](evidence/002-m3/before-manifest.json), [završna provera](evidence/002-m3/after-integrity.json) |
| Izmena koda | [implementation.diff](evidence/002-m3/implementation.diff) |

Pre i posle korišćen je isti `src.eval_runner --out <fajl>` sa različitim
odredištima. Za novo nezavisno ponavljanje trenutnog M1+M3 stanja, iz root-a:

```powershell
$pytestTemp = Join-Path (Get-Location) ('.venv/pytest-m3-' + [guid]::NewGuid().ToString('N'))
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider --basetemp $pytestTemp
$evalFile = "results/m3-verification-$(Get-Date -Format 'yyyyMMdd-HHmmss').json"
.\.venv\Scripts\python.exe -m src.eval_runner --out $evalFile
.\.venv\Scripts\python.exe -m src.eval_compare docs/evidence/002-m3/before.json $evalFile
.\.venv\Scripts\python.exe -m src.cli --question "What is the current company stock price?" --show-retrieved
```

Pytest koristi nov privremeni direktorijum i isključen cache zbog ranije
potvrđenih Windows dozvola. Ne prepisivati originalne M1 rezultate niti ove dokaze.

## Ograničenja i doprinosi

- E05: parafraza `notebook computer` i dalje pronalazi pogrešan dokument.
- E11: zajedničke reči sa godišnjim odmorom daju visok skor; samo globalni prag
  ne može odbiti E11 i istovremeno zadržati E04 sa nižim skorom.
- E06 i dalje citira aktuelnu i zastarelu politiku. M3 ne filtrira verzije.
- Prag je odabran uz uvid u ovaj mali eval skup; 10/12 nije dokaz opšte tačnosti
  niti nezavisna procena na neviđenim pitanjima.

Vedran je analizirao opcije M6/M3 sa Codexom, izabrao M3 i prag 0.10 i zatražio
implementaciju i evidenciju. Codex je napisao specifikaciju, promenio konfiguraciju,
izvršio testove, merenja i CLI provere i sastavio ovaj izveštaj koristeći lokalni
`speckit-implement` postupak. Ovde prikazana nova M3 izvršavanja uradio je Codex;
Vedranova nezavisna ručna provera M3 još nije evidentirana. Njegova prethodna
nezavisna M1 provera ostaje dokumentovana u M1 izveštaju. Pregled drugog para i
osoba koja vodi demonstraciju i dalje čekaju dogovor.
