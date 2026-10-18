**Nedeljni zadatak: Nedelja 7**

# Jedno kontrolisano poboljšanje RAG sistema

## Zašto ovaj zadatak

Korisnik RAG sistema ne vidi chunk-ove ni pragove. Vidi samo da li je odgovor tačan, da li citat vodi do pravog izvora i da li sistem prizna kada ne zna. Vaš zadatak je da na zajedničkom slabom sistemu pronađete gde to ne radi, popravite jednu stvar i dokažete merenjem šta se promenilo.

## Početno stanje

- Slab RAG checkpoint nad priručnikom za zaposlene: arhiva `rag-week-7-weak-checkpoint.zip`, koju tutor objavljuje na Discord-u na kraju Sesije 1.
- Fiksni eval skup od 12 pitanja u `eval/eval_set.json`.
- Komande za testove, CLI, pokretanje eval skupa i poređenje dva rezultata, opisane u README-u projekta.
- Meni mogućih poboljšanja u `docs/improvement-menu.md`.
- Šablon za dokaz: dokument „Šablon za izveštaj pre/posle“.

Okruženje je isto kao u Nedelji 6: Python, virtuelno okruženje i `pytest`. Nije potreban API ključ ni internet posle instalacije.

## Obavezni rezultat

1. **Početna provera:** testovi prolaze, a eval skup je pokrenut i rezultat sačuvan, na primer kao `results/before.json`.
2. **Najmanje dva dokumentovana propusta:** za svaki navedite ID pitanja, šta se očekivalo, šta se desilo i tip propusta (chunkovanje, retrieval, citat, pogrešan odgovor, pogrešno odbijanje).
3. **Specifikacija jedne promene:** propust, hipoteza, promena, očekivani efekat, rizik regresije i provera.
4. **Tačno jedna primenjena promena** koja odgovara specifikaciji.
5. **Ponovno merenje:** ceo eval skup pokrenut istom komandom, rezultat sačuvan, na primer kao `results/after.json`.
6. **Poređenje:** izlaz alata za poređenje: popravljena pitanja, regresije i promena metrika.
7. **Izveštaj pre/posle** prema šablonu, uključujući preostala ograničenja.

## Kriterijumi prihvatanja

- Oba propusta su vezana za konkretna eval pitanja, a ne opisana uopšteno.
- Specifikacija je napisana pre izmene i promena je u skladu sa njom.
- Pregled izmena (`diff`) sadrži jednu promenu po nameri. Ako alat za poređenje upozori da se promenilo više podešavanja, objasnite zašto je to ipak jedna promena ili je razdvojite.
- Otisak eval skupa je isti pre i posle.
- Svaka regresija je navedena i objašnjena.
- Izveštaj navodi bar jedno ograničenje koje ostaje posle promene.
- Ishod može biti i da hipoteza nije potvrđena. To je prihvatljivo ako je izmereno i pošteno objašnjeno.

## Provera

- `python -m pytest` prolazi posle promene.
- Eval skup je pokrenut pre i posle istom komandom.
- Poređenje dva rezultata ne prijavljuje različit otisak eval skupa.
- Za jedno pitanje koje se promenilo, ručno pokrenite CLI i proverite da odgovor i citat izgledaju onako kako eval rezultat tvrdi.

## Pregled para

Pre predaje drugi par čita vaš izveštaj i ostavlja kratak komentar na tri pitanja:

1. Da li je promena zaista jedna i da li odgovara specifikaciji?
2. Da li rezultat pre/posle podržava zaključak?
3. Da li je neka regresija ili ograničenje izostavljeno?

Komentar ulazi u izveštaj. Vi isto tako pregledate izveštaj drugog para. Način uparivanja i mesto komentara: tutor na kraju Sesije 1 objavljuje raspored: par 1 pregleda izveštaj para 2, par 2 para 3, a poslednji par prvog. Komentar ostavite u Discord niti „Nedelja 7: pregled para“ najkasnije do ponedeljka, 19. oktobra, u 20:00.

## Dokaz za predaju

- Izveštaj pre/posle prema šablonu.
- Oba sačuvana eval rezultata (pre i posle) i izlaz poređenja.
- Pregled izmena (`diff`) ili link na `commit`.
- Komentar para koji je pregledao izveštaj.
- Beleška o korišćenju AI-ja: za šta ste koristili asistenta i kako ste proverili ono što je predložio.
- Doprinos oba člana i ime osobe koja vodi demonstraciju na Sesiji 2.

## Način rada para

Par se samostalno organizuje. Izveštaj navodi šta je ko uradio. Osoba koja vodi demonstraciju menja se svake nedelje.

## Podrška

AI asistent sme da pomogne u razumevanju koda, pisanju specifikacije ili implementaciji promene. Ne sme da zameni merenje: tvrdnja asistenta da je nešto popravljeno nije dokaz. Dokaz je eval rezultat pre i posle.

## Granica rada

- U obaveznom delu tačno jedna promena.
- Ne menjajte `eval/eval_set.json` ni kod koji računa metrike.
- Bez vektorske baze, embedding servisa, plaćenog API-ja ili nove infrastrukture.

## Napredni cilj

Tek posle predatog minimuma, i u odvojenom delu izveštaja:

- druga promena, izmerena posebno u odnosu na rezultat posle prve; ili
- kratko poređenje jedne napredne tehnike (reranking, query rewriting, hibridna pretraga ili embeddings) na istom eval skupu, uz napomenu o trošku i zavisnostima.
- ako želite, možete da eksperimentišete i sa vektorskim bazama, embedding modelima i generisanjem teksta koristeći neki LLM.

Napredni cilj ne utiče na prolaz.

## Predaja

Svaki polaznik šalje nedeljni izveštaj imejlom tutoru do **utorka, 20. oktobra 2026, u 12:00**, po standardnom šablonu nedeljnog izveštaja (naslov: `[Nedeljni izveštaj] Ime Prezime – Nedelja 7`). Izveštaj pre/posle para priložite kao `.md` fajl ili kao link ka repozitorijumu; oba člana para prilažu isti izveštaj. Rok ostavlja tutoru vreme za pregled grupe pre Sesije 2.

Sesija 2 je u sredu, 21. oktobra 2026. Demonstracija prikazuje propust, specifikaciju, `diff`, rezultat pre/posle na istom skupu, regresiju ili ograničenje i doprinos oba člana.
