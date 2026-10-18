# Week 7 — M1: rezultat pre/posle

Datum: 18. oktobar 2026. Implementacija i merenje završeni; Milanov doprinos i
ljudski review evidentirani. Vedranov doprinos, osoba koja vodi demonstraciju
i peer review drugog para čekaju dopunu pre predaje.

## Propust, hipoteza i jedna promena

Početni pipeline prolazi 18 testova i 6/12 eval pitanja. Konkretni propusti
E04/E09 i ostali početni neuspesi dokumentovani su u [baseline.md](baseline.md).
Oba ciljana pitanja pronalaze `hb-01`, ali ne citiraju odlomak sa rokom.
Podela po znakovima odvaja početak rečenice sa `replacement laptop` od roka.

[Specifikacija](../specs/001-sentence-chunking/spec.md) i
[plan](../specs/001-sentence-chunking/plan.md) sačuvani su pre implementacije
u commitu `56d9289`. Hipoteza: celovita rečenica može dovesti rok u top-2
citirana odlomka. Rizik: promenjene granice utiču na rangiranje svih pitanja.

Primenjena je samo M1: `split_text_by_sentences` normalizuje whitespace,
razdvaja posle `. ! ?` praćenih razmakom i pakuje cele uzastopne rečenice do
postojećeg limita 140. Preduga rečenica ostaje samostalna; nema overlap-a.
Aktiviran je `CHUNK_STRATEGY="sentences"`. Ostala podešavanja, korpus, scorer,
odgovaranje, pitanja i metrike nisu menjani. Izuzetak za završni JSON u
`.gitignore` služi samo očuvanju dokaza.

## Provera i dokazi

Sve komande izvršene su iz root-a istim `.venv` interpreterom, Python 3.13.7,
pytest 8.3.3:

```powershell
.venv/Scripts/python.exe -m pytest
.venv/Scripts/python.exe -m src.eval_runner --out results/after.json
.venv/Scripts/python.exe -m src.eval_compare results/before.json results/after.json
```

Pre koda ponovo je potvrđeno 18/18 testova i poklapanje svih početnih hash-eva.
Novih 16 sentence provera prvo je palo zbog neimplementirane strategije;
postojeći chars put prolazio je. Posle implementacije prolazi **35/35** testova,
uključujući sve početne. Pytest je zahtevao pokretanje van sandboxa zbog zabrane
pristupa Windows privremenom direktorijumu; podešavanja sistema nisu menjana.

Oba puna merenja sadrže istih 12 pitanja i SHA-256
`afe46db1e75a0b85bb5c9a93b6763e3b96e5cd7b289e12da6d2671e4d8650064`.
Originalni `results/before.json` nije prepisan.

| Dokaz | Fajl |
| --- | --- |
| Početni rezultat | [before.json](../results/before.json) |
| Završni rezultat | [after.json](../results/after.json) |
| Testovi posle | [001-pytest-after.txt](evidence/001-pytest-after.txt) |
| Eval tabela posle | [001-eval-after.txt](evidence/001-eval-after.txt) |
| Izlaz poređenja | [001-eval-compare.txt](evidence/001-eval-compare.txt) |
| CLI odgovori i citati E04/E09/E06 | [001-cli-after.txt](evidence/001-cli-after.txt) |
| Implementacioni diff (src/tests) | [001-implementation.diff](evidence/001-implementation.diff) |
| Hash i scope provera | [001-integrity-after.json](evidence/001-integrity-after.json) |

## Izmereni rezultat

| Metrika | Pre | Posle | Razlika |
| --- | --- | --- | --- |
| Prolazna pitanja | 6/12 | 9/12 | +3 |
| Behaviour accuracy | 0.8333 | 0.8333 | 0 |
| Retrieval hit rate | 0.7778 | 0.8889 | +0.1111 |
| Mean citation precision | 0.4545 | 0.5455 | +0.0910 |

| ID | Pre | Posle | Tumačenje |
| --- | --- | --- | --- |
| E01 | PASS | PASS | Bez promene ishoda |
| E02 | PASS | PASS | Bez promene ishoda |
| E03 | PASS | PASS | Citation precision raste 0.50 → 1.00 |
| E04 | FAIL | PASS | Citira celu rečenicu sa rokom |
| E05 | FAIL | FAIL | Parafraza i dalje ne pronalazi očekivani dokument |
| E06 | FAIL | PASS | Važeća politika ulazi u citate, ali ostaje i zastarela |
| E07 | PASS | PASS | Bez promene ishoda |
| E08 | PASS | PASS | Bez promene ishoda |
| E09 | FAIL | PASS | Citira mesto zahteva i rok |
| E10 | FAIL | FAIL | I dalje odgovara na nepodržano pitanje |
| E11 | FAIL | FAIL | I dalje odgovara na nepodržano pitanje |
| E12 | PASS | PASS | Odbijanje ostaje ispravno |

Poređenje prijavljuje popravljena E04, E06 i E09, **bez PASS → FAIL regresija**,
i tačno jedno izmenjeno podešavanje: `CHUNK_STRATEGY: 'chars' -> 'sentences'`.
Pregled svih numeričkih metrika po pitanju nije pokazao smanjenja.

## Ručna provera i zaključak hipoteze

CLI za E04 citira `hb-01-chunk-1`, verziju 2026, current: posle odobrenja
menadžera, priprema i predaja zamenskog laptopa mogu trajati **do 5 business days**.
Odlomak ima celu rečenicu sa temom i rokom; skor je 0.2069, ispred 0.2000 za
uvodnu rečenicu. To potvrđuje da činjenica sada dospeva u stvarni odgovor.

E09 citira `hb-01-chunk-2` sa IT portal / Hardware i `hb-01-chunk-1` sa rokom.
Proverena su oba dela pitanja, iako eval automatski zahteva samo rok.
Hipoteza za E04/E09 je potvrđena; cilj najmanje 8/12 bez novih padova ostvaren
je sa 9/12. Ovo je rezultat malog fiksnog skupa, bez tvrdnje o opštoj tačnosti.

## Preostala ograničenja

- E06 automatski prolazi jer citira i važeća 3 dana nedeljno. CLI istovremeno
  navodi zastarela 2 dana iz 2024. Ovo nije potpuno rešena verzionisana politika;
  M1 nije dodao filtriranje verzija, a metrika ne kažnjava svaku kontradikciju.
- E05 ostaje retrieval neuspeh za parafrazu `notebook computer`.
- E10/E11 i dalje dobijaju odgovore umesto odbijanja. Behaviour accuracy zato
  ostaje ista. Prag i način rangiranja namerno nisu dodatno podešavani.
- Pravilo rečenice ne obrađuje opšte skraćenice ili završne navodnike; veoma
  duga rečenica može preći ciljni limit. To je unapred definisani ugovor M1.

## AI, doprinosi i ljudski pregled

Codex je korišćen za lokalni pregled, Spec Kit zadatke, implementaciju M1,
pisanje testova, izvršavanje pune evaluacije i CLI provera, pregled diff-a i
ovaj nacrt izveštaja. Provera predloga zasniva se na stvarnim izlazima 35 testova,
12 eval pitanja, poređenju i čitanju citata; ne na tvrdnji asistenta.

Evidencija doprinosa prema potvrdi Milana:

- Član 1 — **Milan**: planiranje, implementacija i ljudski review, uz AI pomoć
  opisanu iznad.
- Član 2 — **Vedran**: još nema realizovanog doprinosa. Mogući naredni doprinos
  su dodatna testiranja i provere; konkretan rad i rezultate dopuniti kada budu
  završeni.
- Osoba koja vodi demonstraciju Week 7: **još nije određena**.
- Drugi par i njihov komentar (jedna promena; podrška zaključku rezultatima;
  izostavljene regresije/ograničenja): **peer review još nije pribavljen**.

Implementacija je završena; ovaj dokument nije konačna predaja dok se navedene
preostale stavke ne popune. Milanov ljudski review je evidentiran odvojeno od
zahtevanog pregleda drugog para, koji još nije pribavljen.
