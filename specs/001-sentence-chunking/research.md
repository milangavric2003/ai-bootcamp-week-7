# Research: M1 — cele rečenice

**Date**: 2026-10-18. Istraživanje koristi lokalni kod, baseline i assignment.
Nije implementiran alternativni pipeline niti pokrenuto završno merenje.

## 1. Izbor jedne promene

**Decision**: Predložiti M1 za E04 i E09.

**Rationale**: Oba pitanja pronalaze `hb-01`, ali citiraju odlomke 0 i 2 bez
roka. Odlomak 1 sadrži ceo `5 business days`, sa nižim skorom: E04 0.107143,
E09 0.142857. Fiksne granice odvajaju početak rečenice sa `replacement laptop`
od dela sa rokom. Scorer deli broj poklopljenih tokena ukupnim brojem tokena
odlomka; rezultat sa činjenicom zato može ostati izvan top-2.

**Alternatives considered**: M5 cilja dokazanu zastarelu verziju u E06, M3
odbijanje E10/E11, M2 zajedničke česte reči, M4 citiranje, M6 broj rezultata.
To su zasebne hipoteze; ne kombinuju se sa M1. Prezentacija, slajd 24, takođe
koristi E04/E09 i cele rečenice kao primer, ali odluka ovde ima sopstveni baseline.

## 2. Granice i pakovanje

**Decision**: Ujednačiti whitespace; granica je whitespace posle `.`, `!`, `?`.
Sačuvati interpunkciju, redom pohlepno pakovati rečenice do limita, bez overlap-a.

**Rationale**: Dovoljno za mali postojeći engleski korpus; koristi standardnu
biblioteku i postojeći stub bez nove arhitekture.

**Alternatives considered**: Jezički parser uvodi nepotrebnu zavisnost;
pravila posebno prilagođena E04/E09 ne bi bila opšta promena chunkovanja.
Skraćenice i navodnici posle interpunkcije ostaju jasno navedeno ograničenje.

## 3. Rečenica duža od limita

**Decision**: Ostaje samostalan, celovit odlomak, bez spajanja sa susedima.

**Rationale**: M1 to eksplicitno zahteva. Rečenica sa rokom u `hb-01` ima 163
karaktera, više od `CHUNK_SIZE=140`. Njeno ponovno sečenje bi kršilo izabranu ideju.

**Alternatives considered**: Povećanje limita ili nastavak sečenja po znakovima
nije deo ovog dizajna. `CHUNK_SIZE` i ostala podešavanja ostaju ista.

## 4. Hipoteza, regresije i dokaz

**Decision**: Prisustvo cele rečenice u odlomku proverava se testovima; bolji
izbor citata proverava se isključivo punom pre/posle evaluacijom i CLI pregledom.

**Rationale**: M1 obezbeđuje zajednički kontekst, ali ne garantuje bolji skor.
Duži odlomak ima veći imenilac; drugi kratki odlomci mogu ostati prvi. Menjaju
se granice svih dokumenata, preciznost citata, izbor verzija i moguća odbijanja.

**Alternatives considered**: Tvrdnja da je ispravna rečenica dovoljan dokaz
popravke ne odgovara evaluaciji. Promena scorera, top-k ili praga radi postizanja
8/12 predstavljala bi dodatnu nameru. Negativan ishod je dozvoljen i dokumentuje se.

## 5. Zaštita početnog stanja

**Decision**: Sačuvati baseline JSON, stvarne CLI izlaze, log testova i SHA-256
manifest pre implementacije. Pred kraj proveriti diff za zaštićene fajlove.

**Rationale**: Omogućava proveru i kasnije poređenje. `results/before.json` je
izričito izuzet iz ignorisanja; za završni JSON isto treba obezbediti pri predaji.

**Alternatives considered**: Sam opis broja prolazaka gubi konkretne rezultate,
konfiguraciju i citate. Novo pokretanje preko početnog fajla uništilo bi dokaz.

Read-only istraživački agent dodatno je pregledao ovaj lokalni ugovor i rizike
kao deo istraživačkog koraka `$speckit-plan`; rezultati kvaliteta potiču iz runner-a.
