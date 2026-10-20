# Embeddings prag 0.51 — eksperiment uz uvid u evaluaciju

19. oktobar 2026, grana embeddings. **12/12**, prethodno 11/12; **86/86 testova**.
Jedina promena koda: EMBEDDING_REFUSAL_THRESHOLD sa 0.50 na 0.51.
Leksički prag ostaje 0.10, a svi njegovi rezultati identični prethodnim: 10/12.
Vedranova nezavisna provera završena je i potvrđena 20. oktobra 2026;
sačuvana puna merenja su iz večeri 19. oktobra.

## Razlog i metod

Vedran je odobrio pomeranje praga nakon pregleda E11 i skora 0.504503.
Hipoteza je zapisana u [specifikaciji](../specs/007-threshold-sensitivity/spec.md)
pre izmene. Razvojna kalibracija je prethodno izabrala 0.50; njen rezultat i
originalni JSON fajlovi su očuvani. **0.51 je izabran uz uvid u poznati eval
skup.** Ovo nije nezavisna kalibracija niti dokaz generalizacije na nova pitanja.
To je empirijsko podešavanje za 0.01; ograničenje se odnosi na tumačenje
rezultata, ne na legitimnost eksperimenta. Za nezavisnu procenu koriste se nova
pitanja koja nisu uticala na izbor parametra.
Nije menjan model, retrieval, korpus, TOP_K, eval skup ili kod metrika.

## Izmereno poređenje

| Metrika | 0.50 | 0.51 |
| --- | --- | --- |
| Passed | 11/12 | 12/12 |
| Behaviour accuracy | 0.9167 | 1.0000 |
| Retrieval hit rate | 1.0000 | 1.0000 |
| Mean citation precision | 0.8500 | 0.9444 |

E11 je jedini FAIL → PASS; nema regresija. CLI sada vraća `Refused: True`,
bez citata, dok retrieved odlomci o annual leave ostaju vidljivi za dijagnostiku.
Njihovi skorovi i rangiranje se ne menjaju. Prosečna preciznost citata raste
jer E11 više nije među odgovorenim pitanjima. E07 i dalje ima sporedni citat
iz drugog dokumenta i preciznost 0.50: 12/12 ne znači savršen sadržaj svih odgovora.

Naknadni [interni PR pregled za Milana](embeddings-pr-review.md), 20. oktobra,
potvrdio je reprodukciju i dodatno dokumentovao ograničenje E09: embeddings
navodi rok, ali izostavlja mesto zahteva `IT portal / Hardware`, koje lexical
odgovor sadrži. Oba prolaze jer fiksna metrika proverava samo rok. Ovo je
regresija sadržaja u odnosu na lexical, nastala promenom retrieval backend-a,
a ne pomeranjem praga 0.50 na 0.51. E07 precision u odnosu na lexical pada
sa 1.00 na 0.50. Nema PASS-to-FAIL regresija, ali ovi gubici ostaju navedeni.
Milan je 20. oktobra u razgovoru potvrdio odobrenje spajanja ovog opcionog
eksperimenta uz navedena ograničenja; GitHub PR korake izvršiće samostalno
nakon commit-a i push-a dopunjene dokumentacije.

Oba merenja imaju isti eval SHA-256:
`afe46db1e75a0b85bb5c9a93b6763e3b96e5cd7b289e12da6d2671e4d8650064`.
Poređenje prijavljuje samo `EMBEDDING_REFUSAL_THRESHOLD: 0.5 -> 0.51`.
Hash provera prethodno postojećih izvora i rezultata nalazi samo izmenu
`src/config.py`. Puni testovi prolaze 86/86, Python 3.14.7 / pytest 8.3.3.

## Dokazi i ponavljanje

- [Pre JSON, 0.50](../results/before-embedding-threshold-051.json)
- [Posle JSON, 0.51](../results/after-embedding-threshold-051.json)
- [Poređenje](evidence/007-threshold-sensitivity/compare.txt)
- [Testovi](evidence/007-threshold-sensitivity/pytest.txt)
- [E11 CLI](evidence/007-threshold-sensitivity/E11-cli.txt)
- [Lexical kontrola](evidence/007-threshold-sensitivity/lexical.json)
- [Integritet](evidence/007-threshold-sensitivity/integrity.json)

Pre-merenje je identična kopija sačuvanog završnog merenja faze 006 pri 0.50.
Nove kopije u results/ identične su onima u docs/evidence/007-threshold-sensitivity/.
Za poređenje i ručnu proveru:

```powershell
.\.venv\Scripts\python.exe -m src.eval_compare results/before-embedding-threshold-051.json results/after-embedding-threshold-051.json
.\.venv\Scripts\python.exe -m src.cli --retrieval-backend embeddings --question "What is the parental leave policy?" --show-retrieved
```

Nova puna merenja pokretati prema [quickstart-u](../specs/005-local-embeddings/quickstart.md)
sa novim nazivima fajlova. Rizik promene: podržani upiti sa najboljim skorom
u [0.50, 0.51) sada se odbijaju. Mala razlika prema E11 nije stabilna garancija
za njegove parafraze ili druge modele. Za tvrdnje o generalizaciji potreban je
zaseban skup pitanja koji nije korišćen za izbor praga.

Vedran je predložio i odobrio ovaj dodatni eksperiment. Codex je kroz lokalni
speckit-implement postupak zapisao specifikaciju, promenio prag i izvršio
testove, punu evaluaciju, CLI i proveru integriteta. Ova nova izvršavanja su
Codexova. Vedran je zatim samostalno pokrenuo testove i obe evaluacije,
izvršio oba poređenja i potvrdio ručni pregled CLI odgovora.

## Vedranova završna provera

Dokazi: [evidencija ručne provere](evidence/vedran-threshold-051-20261019-234713/verification.md).
Potvrđeno je 86/86 testova, lexical 10/12 pri 0.10 i embeddings 12/12 pri 0.51.
Korisnički JSON rezultati imaju identične redove, metrike, konfiguraciju i eval
hash kao ranije odgovarajuće merenje; razlikuje se vreme izvršavanja.

- [Vedranov lexical rezultat](../results/lexical-verification-20261019-234713.json)
- [Vedranov embeddings rezultat](../results/embeddings-051-verification-20261019-234713.json)
- [86 passed](evidence/vedran-threshold-051-20261019-234713/pytest.txt)
- [Poređenje 0.50 → 0.51](evidence/vedran-threshold-051-20261019-234713/compare-050-to-051.txt)
- [Reprodukcija 12/12](evidence/vedran-threshold-051-20261019-234713/compare-reproduction.txt)

Ručni CLI pregled je potvrđen korisnikovom porukom; zasebni CLI logovi ove
runde nisu dostavljeni. Testirani commit i necommitovani diff sačuvani su uz
logove. Codex je naknadno proverio dokaze i dopunio dokumentaciju; ova korisnička
izvršavanja pripisuju se Vedranu. Pregled drugog para ostaje zasebna obaveza.
