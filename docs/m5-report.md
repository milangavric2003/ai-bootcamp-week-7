# Dodatni eksperiment — M5: važeće verzije dokumenata

Datum: 19. oktobar 2026. Status: implementirano i izmereno na `main`, prema
Milanovom izričitom zahtevu. **43/43 testova, 10/12 eval pitanja, bez regresija.**
M5 uklanja zastarelu politiku iz odgovora E06; ne povećava broj PASS pitanja.
M1 ostaje obavezni eksperiment, M3 i M5 su zasebno izmereni dodatni koraci.
Predaja minimuma nije potvrđena; zadatak dodatni rad predviđa posle predaje,
a korisnik je izričito zatražio da se M5 sada implementira.

## Propust, hipoteza i jedna promena

[Specifikacija](../specs/003-current-version-filter/spec.md) i
[plan](../specs/003-current-version-filter/plan.md) sačuvani su pre implementacije
u commitu `ab83d92`. Pre promene koda sačuvani su nova evaluacija, testovi,
CLI propusti i [baseline beleška](evidence/003-m5/baseline.md).

E06 pita koliko dana nedeljno može da se radi na daljinu. M1+M3 citira važeće
pravilo iz 2026. sa 3 dana i superseded pravilo iz 2024. sa 2 dana. Automatski
PASS ostaje jer je činjenica prisutna i preciznost citata iznosi 0.50.
Hipoteza: isključivanje superseded chunk-ova pre rangiranja uklanja kontradikciju
bez gubitka postojećih prolaza. Rizik: stara pravila više nisu dostupna za
istorijska pitanja. E05/E11 su zasebno dokumentovani propusti van namere M5.

Implementacija ima jednu nameru:

- `src/retrieval.py`: postojeći `searchable_chunks` pri uključenom filteru
  zadržava chunk-ove čiji status nije `superseded`, pre računanja skora i top-k.
- `src/config.py`: aktivira postojeći `CURRENT_ONLY=True`.

Ne menjaju se skorovi, top-k, pragovi odbijanja/citiranja, chunkovanje, korpus,
eval pitanja ili računanje metrika. Isključen filter čuva postojeće ponašanje.
Nema novih zavisnosti ili infrastrukture.

## Merenje pre/posle

Oba merenja: Windows, Python 3.13.7, pytest 8.3.3, komande iz root-a istim
projektnim virtualenv interpreterom. Novo pre-merenje potpuno odgovara M3
`results/after-m3.json` osim vremena kreiranja.

| Metrika | M1+M3 / pre | M1+M3+M5 / posle | Razlika |
| --- | --- | --- | --- |
| Prolazna pitanja | 10/12 | 10/12 | 0 |
| Behaviour accuracy | 0.9167 | 0.9167 | 0 |
| Retrieval hit rate | 0.8889 | 0.8889 | 0 |
| Mean citation precision | 0.6000 | 0.6500 | +0.0500 |
| E06 citation precision | 0.50 | 1.00 | +0.50 |
| Testovi | 35/35 | 43/43 | 8 novih provera |

Svih 12 PASS/FAIL ishoda je nepromenjeno: E05/E11 FAIL, ostalih deset PASS.
Nema PASS → FAIL niti smanjenja numeričkih/boolean metrika po pitanju.
Poređenje prijavljuje samo `CURRENT_ONLY: False -> True`.
Eval SHA-256 oba merenja:
`afe46db1e75a0b85bb5c9a93b6763e3b96e5cd7b289e12da6d2671e4d8650064`.

Samo E02 i E06 menjaju retrieved/cited chunk-ove; ostalih deset redova je
potpuno nepromenjeno. E02 zadržava tačan password citat i preciznost 0.50:
sporedni remote-work citat menja se iz superseded `hb-02-chunk-1` u current
`hb-03-chunk-2`, sa istim skorom 0.111111. Ovo ne rešava nebitne prateće citate.

## CLI provera i zaključak

E06 sada citira samo `hb-03-chunk-0` (3 dana nedeljno, skor 0.583333) i
`hb-03-chunk-2` (pomeranje remote dana u istoj nedelji, 0.444444), oba current,
verzija 2026. Nema superseded retrieved/cited chunk-a niti tvrdnje o 2 dana.

Kontrole: E04 čuva rok do 5 business days; E09 čuva i IT portal / Hardware i
rok; E10 i dalje odbija bez citata. E05/E11 ostaju isti pogrešni odgovori.
Pregled E02 potvrđuje tačan rok promene lozinke i preostali sporedni citat.

Hipoteza M5 je potvrđena: odgovor E06 više nije kontradiktoran, preciznost
citata raste, bez eval regresija. **Odluka: zadržati M5.** Rezultat od 10/12
sam ne pokazuje ovo poboljšanje; zato se čuvaju i konkretni citati.

## Testovi i integritet

Osam novih provera pokriva mešovite statuse i stabilan redosled bez mutacije,
isključen filter, sprečavanje da zastareli najbolji match zauzme top-k, prazne
eligible rezultate, stvarne E06 citate u oba režima i odbijanje kada postoji
samo superseded dokaz. Pre implementacije šest provera za aktivni filter pada
na postojećem NotImplementedError; sedam scoped provera prolazi. Posle promene
ceo skup ima 43 prolazna testa.

Prvi baseline pokušaj u sandbox-u ima 34 passed i jednu tmp_path grešku dozvola;
ponavljanje iste komande van sandbox-a prolazi 35/35. Završni puni testovi su
takođe pokrenuti van sandbox-a. Preimplementacioni red log ima i upozorenja o
pytest cache dozvolama; šest padova je zbog nedostajuće implementacije filtera.
Podešavanja sistema i test discovery nisu menjani.

Hash provera potvrđuje da su među praćenim izvorima, testovima, eval skupom i
četiri istorijska JSON rezultata promenjeni samo `src/config.py`,
`src/retrieval.py`, `tests/test_retrieval.py`, `tests/test_rag.py`.
Eval skup, metric/compare kod i originalni M1/M3 JSON fajlovi ostaju isti.
Procesna provera sa `CURRENT_ONLY=False` reprodukuje novo početno merenje u
potpunosti osim timestamp-a; završna konfiguracija ostaje uključena.

## Dokazi i reprodukcija

Svi dokazi su u [evidence/003-m5](evidence/003-m5/), gde JSON fajlovi nisu
obuhvaćeni pravilom `results/*.json` i mogu normalno da se verzionišu.

Za isti raspored kao M1/M3, sačuvane su i bajt-po-bajt identične kopije:
[results/before-m5.json](../results/before-m5.json) i
[results/after-m5.json](../results/after-m5.json), uz izuzetke u `.gitignore`.
To su ista izvorna merenja, ne nova izvršavanja; 10/12 u oba fajla ne znači
da su rezultati identični: E06 citati i preciznost se menjaju.

| Dokaz | Fajlovi |
| --- | --- |
| Pre-implementaciona dijagnoza | [baseline.md](evidence/003-m5/baseline.md) |
| Cela merenja | [before.json](evidence/003-m5/before.json), [after.json](evidence/003-m5/after.json) |
| Eval tabele | [pre](evidence/003-m5/eval-before.txt), [posle](evidence/003-m5/eval-after.txt) |
| Poređenja | [sa M3](evidence/003-m5/compare-m3.txt), [M5 pre/posle](evidence/003-m5/compare.txt) |
| Testovi | [pre](evidence/003-m5/pytest-before.txt), [red](evidence/003-m5/pytest-red.txt), [posle](evidence/003-m5/pytest-after.txt) |
| Prvi sandbox pokušaj | [pytest-before-sandbox.txt](evidence/003-m5/pytest-before-sandbox.txt) |
| E06 citati | [pre](evidence/003-m5/E06-before.txt), [posle](evidence/003-m5/E06-after.txt) |
| Kontrolni odgovori | [E02](evidence/003-m5/E02-after.txt), [E04](evidence/003-m5/E04-after.txt), [E09](evidence/003-m5/E09-after.txt), [E10](evidence/003-m5/E10-after.txt) |
| Neuspešni slučajevi | [E05 pre](evidence/003-m5/E05-before.txt), [posle](evidence/003-m5/E05-after.txt); [E11 pre](evidence/003-m5/E11-before.txt), [posle](evidence/003-m5/E11-after.txt) |
| Integritet i diff | [manifest pre](evidence/003-m5/before-manifest.json), [provera posle](evidence/003-m5/after-integrity.json), [implementation.diff](evidence/003-m5/implementation.diff) |

Za nezavisno ponavljanje koristiti [quickstart](../specs/003-current-version-filter/quickstart.md).
Ne prepisivati sačuvani before koristeći trenutni kod. Nova merenja imaju novo ime.

## Preostala ograničenja, AI i doprinosi

- E05: filter verzija ne razume notebook/laptop parafrazu.
- E11: korpus nema parental-leave politiku; slične reči i dalje izazivaju odgovor.
- E02 i drugi odgovori mogu sadržati nebitne prateće citate; M5 ne menja citiranje.
- Istorijska pitanja ne dobijaju superseded izvore. Filter veruje statusu, ne
  zaključuje koja verzija važi po datumu ili sadržaju; nije opšti sistem verzionisanja.
- Ovo je mali poznati eval skup, bez tvrdnje o opštoj tačnosti ili nezavisnom testu.

Milan je prihvatio plan i zatražio M5 implementaciju/testiranje na main.
Codex je generisao zadatke, izvršio baseline, napisao osam provera, implementirao
filter, izvršio završna merenja/CLI, proverio integritet i pripremio izveštaj.
Tvrdnje su proverene stvarnim testovima, JSON rezultatima, poređenjem i citatima.
Ova izvršavanja se pripisuju Codexu. Novi ljudski review M5 i Vedranova
nezavisna M5 provera nisu potvrđeni; njihovi raniji doprinosi ostaju u M1/M3
izveštajima. Obavezni komentar drugog para i demo lead ostaju nepopunjeni u
evidenciji dok ih ljudi ne potvrde. Dalji M2/embedding/LLM rad zavisi od vremena.
