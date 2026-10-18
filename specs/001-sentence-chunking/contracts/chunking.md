# Contract: sentence strategija i postojeći CLI

## `split_text_by_sentences(text: str, chunk_size: int = 140) -> list[str]`

1. `chunk_size <= 0` podiže `ValueError`, uključujući slučaj praznog teksta.
2. Whitespace se normalizuje kao u postojećem splitter-u: reči odvaja jedan razmak.
3. Prazan normalizovan tekst vraća `[]`.
4. Granica rečenice je whitespace neposredno posle `.`, `!` ili `?`.
   Interpunkcija ostaje sa prethodnom rečenicom. Završni fragment bez te
   interpunkcije predstavlja poslednju rečenicu.
5. Cele rečenice dodaju se redom u trenutni odlomak dok ukupan broj karaktera,
   uključujući po jedan spojni razmak, ne bi prešao limit.
6. Dužina jednaka limitu je dozvoljena. Prekoračenje završava prethodni odlomak.
7. Rečenica duža od limita ostaje zaseban odlomak. Ne spaja se sa susedima.
8. Nema overlap-a, praznih odlomaka, preuređivanja ni gubitka sadržaja.
9. Nema posebnih pravila za eval ID-jeve, termine laptopa ili konkretne činjenice.

Rečenice se određuju jednostavnim navedenim pravilom. Skraćenice i navodnici
između interpunkcije i whitespace-a nisu cilj ovog malog lokalnog splittera.

## Povezivanje sa postojećim kodom

- `split_text` nastavlja izbor prema `CHUNK_STRATEGY`.
- Aktivacija M1 menja samo `CHUNK_STRATEGY`: `chars` → `sentences`.
- `CHUNK_SIZE=140` i `CHUNK_OVERLAP=30` ostaju zapisani; drugi se ne koristi
  u sentence strategiji. Ne postoji dodatni sentence overlap parametar.
- `split_text_with_overlap` i `chars` ponašanje ostaju isti.
- `build_chunks` zadržava format ID-jeva i prenos metapodataka.

## Spoljašnji CLI ugovor

Nema novih komandi ili opcija. Korisnik i dalje poziva:

```powershell
python -m src.cli --question "How many business days does a laptop replacement take?" --show-retrieved
python -m src.eval_runner --out results/after.json
python -m src.eval_compare results/before.json results/after.json
```

CLI nastavlja prikaz odgovora, odbijanja, ID-jeva citata, naslova, verzije i
statusa; uz `--show-retrieved` prikazuje i skorove i odlomke. Promena teksta
i odabira odlomaka je očekivana posledica M1. Šeme rezultata i metrike ostaju iste.
