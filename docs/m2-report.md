# Dodatni eksperiment — M2: stopword filtering

Datum: 19. oktobar 2026. Grana: `main`, na Milanov izričit zahtev.
**Implementirano i izmereno, ali isključeno po korisnikovoj odluci.** Uključen
M2 daje **9/12**, sa regresijom E09; zadržano stanje sa isključenim M2 daje
**10/12**. Oba režima prolaze **53/53 testa**. Human review je sledeći korak.

M1 ostaje obavezni eksperiment; M3, M5 i ovaj M2 su odvojeni dodatni eksperimenti.
Zadatak ih predviđa posle predaje minimuma; predaja nije potvrđena. Korisnik je
izričito zatražio da se M2 uradi sada. Ovo odstupanje u redosledu je evidentirano.

## Specifikacija, hipoteza i jedna namera

[Specifikacija](../specs/004-stopword-filter/spec.md),
[plan](../specs/004-stopword-filter/plan.md) i
[zadaci](../specs/004-stopword-filter/tasks.md) napisani su pre izmene pipeline-a.
Sačuvani su novo početno merenje, testovi, konfiguracija, hash manifest i
[dva konkretna propusta](evidence/004-m2/baseline.md).

- E05 očekuje zamenu laptopa i rok `5 business days`; dobija onboarding i annual
  leave, bez očekivanog dokumenta ili činjenice. Retrieval ne povezuje notebook/laptop.
- E11 treba odbiti jer nema parental leave politike; dobija annual leave citate.
  Slična tema nije dovoljan dokaz za konkretno pitanje.

Hipoteza: uklanjanje čestih gramatičkih reči iz upita i chunk-a smanjuje šum i
može popraviti citate. Nije obećano popravljanje E05/E11 niti rast PASS broja.
Rizik: menjaju se broj poklopljenih reči i dužina chunk-a u imeniocu, pa se mogu
promeniti poredak, citati i odluke o odbijanju. Postojeće lowercasing pravilo
pretvara i akronim IT u stopword `it`; taj rizik je zapisan pre implementacije.

Jedina namera je M2:

- `src/retrieval.py`: fiksni nepromenljivi skup od 40 opštih engleskih reči i
  filtriranje u postojećem tokenizer-u, simetrično za oba ulaza skora.
- `src/config.py`: STOPWORDS_ENABLED je uključen za merenje; posle rezultata
  vraćen je na False po korisnikovom izričitom izboru. Komentar objašnjava razlog.
- Negacije, brojevi, `until`, redosled i ponavljanja preostalih reči se čuvaju.
  Prazan filtrirani ulaz koristi postojeći skor 0 i putanju odbijanja.

Tačan spisak je zamrznut u planu pre implementacije. Nije menjan posle merenja.
Nema promene formule, top-k=2, retrieval minimuma 0.01, refusal praga 0.10,
citiranja, sentence chunkovanja, current-version filtera, korpusa ili zavisnosti.

## Merenje pre, uključen M2 i zadržano stanje

Sva merenja: isti root, projektni virtualenv Python 3.13.7, pytest 8.3.3,
isti kompletan runner i nepromenjenih 12 pitanja.

| Metrika | Pre: M1+M3+M5 | M2 uključen | Zadržano: M2 isključen |
| --- | --- | --- | --- |
| Prolazna pitanja | 10/12 | 9/12 | 10/12 |
| Behaviour accuracy | 0.9167 | 0.9167 | 0.9167 |
| Retrieval hit rate | 0.8889 | 0.8889 | 0.8889 |
| Mean citation precision | 0.6500 | 0.7000 | 0.6500 |
| E02 citation precision | 0.50 | 1.00 | 0.50 |
| E09 fact in citations | true | false | true |
| Testovi | 43/43 | 53/53 | 53/53 |

Poređenje pre/uključen M2 prijavljuje: **fixed none; regressed E09**;
jedina promena podešavanja je `STOPWORDS_ENABLED: False -> True`.
E01–E04, E06–E08, E10 i E12 ostaju PASS; E05/E11 ostaju FAIL.
E09 je jedini novi PASS → FAIL i jedini gubitak boolean/quality metrike po pitanju.
Poređenje pre/zadržano ne prijavljuje promenu podešavanja ni rezultata.

Eval SHA-256 sva tri run-a:
`afe46db1e75a0b85bb5c9a93b6763e3b96e5cd7b289e12da6d2671e4d8650064`.

## Objašnjenje regresije i ručna CLI provera

E09 pita gde se podnosi zahtev za laptop i koliko traje zamena.
Pre M2 dobija `hb-01-chunk-2` (IT portal / Hardware, 0.294118) i
`hb-01-chunk-1` (do 5 business days, 0.241379).
Sa M2 dobija `hb-01-chunk-0` (opšti uslovi zamene, 0.285714) i
`hb-01-chunk-2` (mesto zahteva, 0.25). Chunk sa rokom ima skor 0.15 i ispada
iz top-2. Odgovor više ne sadrži rok: ovo je stvarna regresija relevantnog dokaza.

E09 i dalje ima retrieval hit i citation precision 1.00 jer oba citata pripadaju
očekivanom dokumentu. Ta preciznost ne garantuje prisustvo tražene činjenice.
Zato viša srednja citation precision nije dovoljan razlog da se M2 zadrži uključen.

E02 zaista dobija bolji prateći citat: umesto remote-work teksta, drugi citat je
password pravilo `hb-05-chunk-2`; rok od 90 dana ostaje u prvom citatu.
E04 i dalje sadrži 5 business days; E06 samo važeću politiku sa 3 dana;
E07 zadržava IT-support sate uprkos uklanjanju `it`; E10 se odbija bez citata.
E08 ostaje PASS sa nebitnim password pratećim citatom.

E05 i dalje pogrešno odgovara onboarding tekstom (najbolji skor 0.142857).
E11 i dalje pogrešno odgovara annual leave tekstom; najbolji skor čak raste
0.222222 → 0.285714. Uklanjanje stopwords ne proverava dovoljno dobar dokaz.
CLI izlazi za ove slučajeve su sačuvani, kao i rekonstrukcija E09 pre preko
isključivanja flag-a samo unutar zasebnog procesa.

## Odluka i human review

Hipoteza je delimično potvrđena za E02 citate, ali nije prihvatljiva kao ukupno
poboljšanje: M2 gubi tačan odgovor E09. Preporuka je **ne zadržati M2 uključen**.
Korisnik je izabrao: **Keep M2 implemented but disabled**. Implementacija ostaje
na main radi pregleda, a `STOPWORDS_ENABLED=False` vraća zadržani rezultat 10/12.
To je odluka o eksperimentu, ne prećutno podešavanje spiska, top-k ili praga.

Human review koda i rezultata ostaje **pending**. Izbor isključenog režima ne
označava da je korisnik već uradio nezavisan pregled. Posle review-a korisnik radi
embeddings kao zaseban eksperiment za E05; grounded LLM za procenu dokaza i
odbijanje E11 je poseban kasniji korak. Vidi [dogovoreni plan](advanced-plan.md).

## Testovi, integritet i dokazi

Deset novih provera pokriva oba režima tokenizacije, negacije/brojeve/redosled,
ponavljanja, filtrirani imenilac, pet praznih/all-stopword slučajeva, nestanak
nebitnog stopword-only match-a i odbijanje bez citata. Pre implementacije devet
provera pada na postojećem NotImplementedError, a disabled provera prolazi.
Posle implementacije i po vraćanju default-a na False prolaze sva 53 testa.

Prvi baseline pokušaj u sandbox-u ima 42 passed i jednu tmp_path permission grešku,
uz cache upozorenja. Ista puna komanda sa normalnim temp pristupom prolazi 43/43;
oba završna puna testa koriste taj isti pristup. Podešavanja projekta nisu menjana.

Hash provera potvrđuje očuvanje eval skupa, metric/compare koda, korpusa, ranijih
specifikacija i istorijskih rezultata/referenci iz manifesta. Samo src/config.py,
src/retrieval.py i dva test fajla menjaju se među praćenim eksperimentalnim fajlovima.
Isključen M2 reprodukuje ceo pre-run, uključujući skorove, citate i metrike, osim
timestamp-a. Zadržani run potvrđuje isto na završnom kodu.

| Dokaz | Fajlovi u evidence/004-m2 |
| --- | --- |
| Preimplementacioni baseline | [baseline.md](evidence/004-m2/baseline.md), [before-manifest.json](evidence/004-m2/before-manifest.json) |
| Izvorna puna merenja | [before.json](evidence/004-m2/before.json), [after.json](evidence/004-m2/after.json), [retained.json](evidence/004-m2/retained.json) |
| Poređenja | [M2 uključen](evidence/004-m2/compare.txt), [zadržano stanje](evidence/004-m2/compare-retained.txt) |
| Testovi | [pre](evidence/004-m2/pytest-before.txt), [red](evidence/004-m2/pytest-red.txt), [uključen](evidence/004-m2/pytest-after.txt), [zadržan](evidence/004-m2/pytest-retained.txt) |
| Regresija E09 | [pre](evidence/004-m2/E09-before.txt), [uključen M2](evidence/004-m2/E09-after.txt) |
| Implementacioni diff | [mereni uključen režim](evidence/004-m2/implementation-enabled.diff), [završno stanje](evidence/004-m2/implementation.diff) |
| Integritet | [uključen](evidence/004-m2/after-integrity.json), [zadržan](evidence/004-m2/retained-integrity.json), [provera](evidence/004-m2/verify.py) |

Dokazi su pod docs/, izvan ignorisanog results/*.json, i mogu se normalno verzionisati.
Sačuvani su i eval tabele, prvobitni sandbox log i CLI E02/E04/E05/E06/E07/E08/E10/E11.
Za nezavisno ponavljanje koristiti [quickstart](../specs/004-stopword-filter/quickstart.md)
i nove nazive izlaznih fajlova; ne prepisivati izvorna merenja.

## Ograničenja, AI i doprinosi

- Nema sinonima, embeddings ili procene semantičke podrške; E05/E11 ostaju.
- Fiksni stopwords mogu ukloniti značajne akronime i promene dužine favorizuju
  kraće chunk-ove. Dokument tačan po temi može ostati bez tražene činjenice.
- Ovo je mali poznati skup, bez tvrdnje o opštoj tačnosti ili nezavisnom testu.
- Milan je odobrio plan/M2 na main i izabrao da ga ostavi isključenim; njegov
  human review i embedding implementacija tek slede. Novi Vedranov M2 doprinos
  ili nezavisno merenje nisu potvrđeni; raniji doprinosi ostaju u starim izveštajima.
- Codex je primenio Spec Kit workflow, dokumentovao baseline/spec, implementirao
  filter, napisao i izvršio testove, eval/CLI/integrity provere i pripremio izveštaj.
  Read-only istraživački agent proverio je fiksni spisak i rizike pre implementacije.
- Zaključci potiču iz stvarnih sačuvanih izvršavanja, a ne iz procene asistenta.
  Ljudski peer review, demo lead i status predaje ostaju za ljudsku potvrdu.
