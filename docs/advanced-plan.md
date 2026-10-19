# Plan naprednog rada: M2, embeddings i grounded LLM

Datum: 19. oktobar 2026. Status: dogovoren redosled dodatnih eksperimenata.

Preporuka: birati eksperimente prema propustu, ne prolaziti M1–M6 kao obaveznu
listu. M5 je implementiran i izmeren. Korisnik je odobrio M2 na `main`,
zatim sopstveni human review i implementaciju embeddings kao sledeći korak.
Ne čekati 12/12 da bi se probali embeddings i ne obećavati da će ih oni dati.

M2 se radi sada čak i ako ne popravi nijedan PASS/FAIL ishod. Njegov cilj je
izmeriti uticaj uklanjanja stopwords na šum, citate i odbijanje. Ne pretpostavljati
rezultat pre merenja. Posle M2 Codex predaje dokaze korisniku za human review;
ne započinje embeddings ili LLM implementaciju u ovom koraku.
Korisnik potom radi embeddings. Grounded LLM sa procenom dovoljnog dokaza i
odbijanjem ostaje poseban kasniji eksperiment, ako bude vremena.
Obavezna predaja i demonstracija imaju prednost. Plan i M2 ostaju na `main`,
bez nove grane, na izričit zahtev korisnika.

## Šta je već završeno

- Obavezni M1: 6/12 → 9/12, zaseban [izveštaj](m1-report.md).
- Dodatni M3: 9/12 → 10/12, zaseban [izveštaj](m3-report.md).
- Dodatni M5: 10/12 → 10/12 bez regresija, 43 testa; E06 precision 0.50 → 1.00,
  mean citation precision 0.60 → 0.65. [Izveštaj](m5-report.md).
- Dodatni M2: implementiran i izmeren na `main`, 53 testa u oba režima.
  Uključen: 10/12 → 9/12, regresija E09, mean citation precision 0.65 → 0.70.
  Korisnik je izabrao da M2 ostane implementiran ali isključen: zadržano stanje
  ponovo daje 10/12 i reprodukuje baseline. [Izveštaj](m2-report.md).
- M3 već predstavlja drugu, posebno izmerenu promenu kakvu dopušta napredni cilj.
  Nisu obavezni svi M koraci niti embedding tehnika.
- Zadatak napredni deo predviđa posle predaje minimuma. M3, M5 i M2 su urađeni na
  izričit zahtev pre potvrđene predaje; odstupanje ostaje dokumentovano. Komentar
  drugog para, demo lead i predaja minimuma ostaju za ljudsku potvrdu.

## Polazni problemi

Stanje u tabeli je polazno M1+M3, pre M5. Aktuelni E06 odgovor sada sadrži
samo current izvore; E05/E11 ostaju isti neuspešni slučajevi.

| Slučaj | Trenutno stanje | Šta treba proveriti |
| --- | --- | --- |
| E05 | FAIL; notebook computer ne pronalazi dokaz o zameni laptopa | Semantičko poklapanje i ceo rok u citatu |
| E11 | FAIL; annual leave se daje kao odgovor o parental leave | Da li dokaz podržava konkretno pitanje |
| E06 | PASS, ali citira staru politiku sa 2 i važeću sa 3 dana | Uklanjanje superseded izvora, ne samo PASS |
| E09 | PASS, ali pita i mesto zahteva i rok | Ručno proveriti oba dela; eval proverava rok |

M3 prag ne može sam rešiti E11 uz očuvanje E04: najbolji skor E11 je
0.222222, a podržanog E04 0.206897. Viši globalni prag koji odbija E11
odbio bi i E04 pri sadašnjem ocenjivanju.

## Redosled eksperimenata

| Korak | Jedna namera | Cilj i rizik | Odluka |
| --- | --- | --- | --- |
| 0 | Sačuvati trenutno M1+M3+M5 stanje za M2 | Potvrditi 10/12; sačuvati testove, eval, konfiguraciju, commit i CLI E05/E11 | Ne prepisivati prethodne dokaze |
| 1: M5, završeno | Isključiti superseded izvore pre rangiranja | E06 bez zastarele politike; istorijska pitanja gube stare izvore | Zadržan: CLI potvrđuje poboljšanje, nema regresija |
| 2: M2, završen i isključen | Ukloniti unapred zadate česte engleske reči iz oba toka tokena | Bolji E02 citati, ali E09 gubi rok; 10/12 → 9/12 | Po izboru korisnika implementacija ostaje, STOPWORDS_ENABLED=False; zadržano 10/12 |
| 2a: human review | Pregledati M2 diff, specifikaciju i rezultate | Potvrditi šta se stvarno promenilo i koje stanje se zadržava | Korisnik radi review pre svog embedding koraka; Codex ga ne označava završenim |
| 3: embeddings | Uporediti jedan lokalni retrieval model sa zadržanim leksičkim stanjem | E05 je semantički cilj; E11 može dobiti sličan, nepodržan kontekst | Korisnik implementira posle M2 i review-a; zasebno merenje, vreme, zavisnosti i cena |
| 4: grounded LLM, kasnije | Proceniti da li retrieved dokaz podržava konkretan odgovor; odgovoriti ili odbiti | E11: razlikovati annual od parental leave; moguć je i pogrešan odgovor ili odbijanje | Posebna specifikacija i merenje; bez tvrdnje da LLM garantuje PASS |

Završeni M5 korak:
[specifikacija](../specs/003-current-version-filter/spec.md),
[plan implementacije](../specs/003-current-version-filter/plan.md).
M2 tehnički nije preduslov za embeddings. Dogovoreni M2 eksperiment je završen
bez podešavanja spiska ili pragova posle rezultata. Human review još nije urađen;
korisnikov izbor isključenog režima ne predstavlja završen pregled koda i dokaza.
Sledeći embedding baseline je zadržano M1+M3+M5 stanje sa M2=False.

## Zašto ne sve M opcije redom

M2 ne dodaje vezu notebook ↔ laptop. M4 uklanja slabe prateće citate, ali po
meniju uvek zadržava prvi: ne može odbaciti pogrešan vodeći odgovor E11.
M6 može povećati šum ili izgubiti činjenicu; top-k=1 ugrožava E09.
M4/M6 razmatrati samo ako pregled konkretnih citata opravda eksperiment.
Ni završetak celog menija ni embeddings ne garantuju 12/12.

## Malo poređenje embeddings, bez nove infrastrukture

Za deset dokumenata koristiti lokalni model, unapred izračunate vektore chunk-ova
i tačnu pretragu po sličnosti u memoriji. Posebna vektorska baza nije potrebna;
[Sentence Transformers dokumentacija](https://www.sbert.net/examples/sentence_transformer/applications/semantic-search/README.html)
opisuje direktnu pretragu za male korpuse.

Pre implementacije napisati zasebnu specifikaciju: model i revizija, verzije
paketa, CPU/memorija, licenca, preuzimanje/cache, ista pitanja i chunk-ovi,
zadržan filter verzija i pravilo citiranja. Ne dodavati istovremeno LLM
generisanje, hibridno rangiranje ili reranker.

Prvi uporedni eksperiment menja retrieval backend; ostala podešavanja su fiksna.
Nasleđeni leksički prag 0.10 nema isto značenje na cosine skali: taj run je
kontrolisana dijagnostika, ne dokaz da su oba backend-a optimalno podešena.
Ako treba kalibracija, meriti je zasebno, uz unapred dokumentovane razvojne
primere odvojene od E01–E12, pa ponoviti punu evaluaciju. Isto važi za
RETRIEVAL_MIN_SCORE i eventualni CITATION_MIN_SCORE.

Identitet modela i sva eksperimentalna podešavanja sačuvati u evidenciji i
konfiguracionom snapshot-u postojećeg runner-a; ne menjati obračun metrika.
Zabeležiti vreme učitavanja i ponovljenog upita, veličinu modela/cache-a,
zavisnosti i stvarne troškove. Lokalno izvršavanje nema naplatu API poziva,
ali troši računar i zahteva početno preuzimanje modela.

## Kasniji grounded LLM eksperiment

LLM dobija pitanje i retrieved chunk-ove, uz zahtev da odgovara samo iz dokaza,
citira podršku i odbije kada konkretan odgovor nije podržan. Hipoteza za E11:
razlikovaće annual leave od parental leave. Ne tvrditi unapred da će to uspeti.
Zaključak je da retrieved kontekst nije dovoljan, ne da odgovora nema u celom
korpusu. Odbijanje mora biti zabeleženo kao `refused=True`, bez citata.
Promena je odvojena od embeddings; zapisati model/prompt/reviziju i trošak.
Postojeći eval proverava činjenice u citatima, pa ručno pregledati i generisani
odgovor; ne menjati fiksne metrike da bi eksperiment izgledao bolje.

## Isti protokol za svaki korak

1. Zasebna specifikacija pre promene, sa hipotezom i rizikom regresije. Grana
   prema dogovoru; M5 i M2 su na izričit zahtev korisnika na `main`.
2. Testovi i kompletan eval pre promene, sačuvani u novom direktorijumu dokaza.
3. Jedna promena; testovi i kompletan isti eval posle nje.
4. `src.eval_compare` nad tim parom; isti eval SHA-256, promenjena podešavanja
   objašnjena, sve regresije navedene. Ne menjati eval skup ili metrike.
5. CLI provera cilja i E04/E06/E09/E10/E11 kao kontrola.
6. Izveštaj sa odlukom zadržati/odbaciti. Sledeći korak polazi od zadržanog
   stanja, ne automatski od poslednjeg eksperimentalnog pokušaja.

Cilj je proverljivo poboljšanje i pošteno poređenje. 12/12 je poželjan rezultat,
ali nije uslov za napredni deo niti dokaz opšte tačnosti. Pre eksperimenata
zapisati mali zaseban skup ručnih parafraza i pitanja bez odgovora, van
`eval/eval_set.json`; ne nazivati ga neviđenim testom ako služi za podešavanje.
Ne prilagođavati kod pojedinačnim ID-jevima ili formulacijama.

## Status plana

M5 je implementiran i izmeren. M2 je implementiran, izmeren i isključen po
korisnikovoj odluci zbog regresije E09; [izveštaj](m2-report.md) čuva sve rezultate.
Zadržano stanje daje 10/12; 53 testa prolaze. Human review je sledeći korisnikov
korak; embeddings zatim implementira korisnik. Grounded LLM ostaje zaseban kasniji
eksperiment. Ništa od ta tri buduća koraka nije završeno ovom promenom.
Ovaj dokument ne zamenjuje specifikaciju svakog kasnijeg eksperimenta.
Plan je pripremljen uz Codex i read-only istraživački pregled. Brojevi polaze
od sačuvanih merenja; budući efekti su hipoteze.
