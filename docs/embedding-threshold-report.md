# Embeddings — zaseban prag odbijanja

Istorijski izveštaj za razvojni izbor 0.50. Aktuelni prag je 0.51 iz zasebnog
[naknadnog eksperimenta](threshold-051-report.md), sa 12/12 na poznatom eval skupu.
Rezultati i metod kalibracije ispod ostaju sačuvani kao faza 006.

Datum: 19. oktobar 2026. Grana: embeddings. Rezultat: **11/12**, E10 popravljen,
bez novih padova; **86/86 testova**. Lexical ostaje **10/12** sa pragom 0.10.

## Jedna promena i polazni dokaz

Vedran je pokrenuo punu embeddings evaluaciju i proverio CLI E10. Njegov
`results/after-embeddings-20261019-231508.json` ima 10/12: E05 je popravljen,
ali E10 odgovara o budžetu obuke i onboardingu. Cosine skor 0.175122 prelazi
nasleđeni prag 0.10. E11 takođe pogrešno odgovara, sa skorom 0.504503.

Na Vedranov zahtev uveden je `EMBEDDING_REFUSAL_THRESHOLD=0.50`.
`REFUSAL_THRESHOLD=0.10` važi za leksički backend. `src/rag.py` bira odgovarajući
prag prema aktivnom backend-u. Odbija se kada je najbolji skor strogo manji
od praga; jednak skor se prihvata. Ovo je prag odluke o odgovoru, ne filter
pojedinačnih citata: niži drugi skor i dalje može biti citiran kada prvi prolazi.
Retrieval minimum 0.01, TOP_K=2, M5 filter, model, chunkovanje i metrike ostaju isti.

[Specifikacija](../specs/006-embedding-threshold/spec.md) i
[plan](../specs/006-embedding-threshold/plan.md) napisani su pre kalibracije i koda;
nisu zasebno commitovani. To je nastavak, odvojen od prvog embeddings merenja.

## Kako je izabrano 0.50

Pre merenja je zamrznut [razvojni skup](evidence/006-embedding-threshold/development-set.json)
od 18 pitanja (devet podržanih i devet nepodržanih), izvan zvaničnog eval skupa.
Oznake su izvedene iz korpusa. Na primer, D08 pita ko odobrava službeni put:
priručnik zahteva odobrenje, ali ne imenuje osobu, pa je očekivanje odbijanje.

Unapred definisano pravilo: kandidati 0.10, 0.15, ..., 0.80; zadržati sve
podržane razvojne upite, odbiti što više nepodržanih; pri izjednačenju uzeti
niži prag. [calibrate.py](evidence/006-embedding-threshold/calibrate.py)
ne čita E01–E12 niti njihove ishode prilikom izbora.

| Prag | Pogrešno odbijeni podržani | Ispravno odbijeni nepodržani | Pogrešno prihvaćeni |
| --- | --- | --- | --- |
| 0.45 | 0/9 | 7/9 | 2/9 |
| **0.50** | **0/9** | **8/9** | **1/9** |
| 0.55 | 0/9 | 8/9 | 1/9 |
| 0.60 | 2/9 | 9/9 | 0/9 |

0.50 i 0.55 su izjednačeni na razvojnom skupu; pravilo bira 0.50. D08 ostaje
pogrešno prihvaćen sa 0.596225. Najslabiji podržani razvojni skor je 0.555187.
Ovo su rezultati kalibracije ponašanja, ne potpuna provera kvaliteta razvojnih
odgovora. Skup je mali i sastavljen uz poznavanje korpusa i ranijih eval problema;
nije neviđen holdout. Prag nije univerzalna granica pouzdanosti ovog modela.

## Puna evaluacija i CLI

| Metrika | Embeddings prag 0.10 | Embeddings prag 0.50 |
| --- | --- | --- |
| Passed | 10/12 | 11/12 |
| Behaviour accuracy | 0.8333 | 0.9167 |
| Retrieval hit rate | 1.0000 | 1.0000 |
| Mean citation precision | 0.7727 | 0.8500 |

Popravljen E10, bez PASS → FAIL regresija. E11 ostaje jedini FAIL.
CLI E10 sada odbija bez citata; retrieved odlomci ostaju vidljivi za dijagnostiku.
E05 i dalje citira laptop i rok pet radnih dana. E11 i dalje citira annual leave
za parental leave. Rast prosečne citation precision nastaje izostavljanjem
pogrešnog E10 odgovora iz proseka, a ne promenom odlomaka ostalih odgovora.

Leksička kontrola daje identične redove, zbirne metrike i eval hash kao
Vedranovo leksičko merenje pre embeddings: 10/12, padovi E05/E11.
Za oba pre/posle rezultata eval SHA-256 je
`afe46db1e75a0b85bb5c9a93b6763e3b96e5cd7b289e12da6d2671e4d8650064`.
Poređenje navodi `EMBEDDING_REFUSAL_THRESHOLD: None -> 0.5`: pre nije postojao
zaseban ključ i koristio se zajednički 0.10. Originalni JSON nije naknadno menjan.

16 novih test slučajeva proverava granice oba praga, odsustvo rezultata i
nezavisnost jednog praga od drugog. Pre implementacije 4 padaju, 12 prolazi;
posle ukupno 86/86 prolazi. Postojeći embeddings test je prilagođen novom ključu.

## Dokazi i reprodukcija

- [Pre JSON](../results/before-embedding-threshold.json) i
  [posle JSON](../results/after-embedding-threshold.json) imaju identične kopije
  u [direktorijumu dokaza](evidence/006-embedding-threshold/).
- [Poređenje](evidence/006-embedding-threshold/compare.txt),
  [lexical kontrola](evidence/006-embedding-threshold/lexical.json),
  [calibration.json](evidence/006-embedding-threshold/calibration.json).
- [Testovi](evidence/006-embedding-threshold/pytest-after.txt), CLI
  [E05](evidence/006-embedding-threshold/E05-after.txt),
  [E10](evidence/006-embedding-threshold/E10-after.txt),
  [E11](evidence/006-embedding-threshold/E11-after.txt).

```powershell
.\.venv\Scripts\python.exe -m src.cli --retrieval-backend embeddings --question "What is the current company stock price?" --show-retrieved
.\.venv\Scripts\python.exe -m src.eval_compare results/before-embedding-threshold.json results/after-embedding-threshold.json
```

Za novo celo merenje koristiti novi output fajl i RAG_RETRIEVAL_BACKEND=embeddings
prema [quickstart-u](../specs/005-local-embeddings/quickstart.md). U konfiguraciji
su zabeležena oba praga; izabrani backend određuje koji se primenjuje.

Vedran je identifikovao E10 regresiju kroz sopstveno merenje/CLI i zatražio
odvojene pragove. Codex je sastavio razvojni skup, izvršio kalibraciju, napisao
kod i testove i izvršio ovde navedena završna merenja kroz lokalni
speckit-implement postupak. Vedranova nezavisna provera nove kalibracije nije
još potvrđena. E11 i D08 pokazuju preostalo ograničenje: sličan tekst ne garantuje
podršku konkretnom pitanju; viši prag može odbiti i podržan upit.
