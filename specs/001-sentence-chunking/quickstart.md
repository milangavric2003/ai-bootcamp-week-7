# Quickstart: provera M1 eksperimenta

Ovo je vodič za narednu implementacionu fazu; završno merenje još nije pokrenuto.
Sve komande pokretati iz root-a projekta postojećim `.venv` interpreterom.
U aktiviranom virtualenv-u odgovarajući poziv je `python -m ...`.

## 1. Proveriti sačuvano početno stanje

Pročitati [baseline](../../docs/baseline.md) i [specifikaciju](spec.md).
`results/before.json` ostaje sačuvani rezultat originalnog pipeline-a; ne
pokretati novi runner preko tog fajla. Baseline ima 6/12 PASS i 18 prolaznih testova.

Pre implementacije proveriti da li su početni dokazi i plan sačuvani u Git-u.
Predlog commit poruke:

```text
docs: record Week 7 baseline failures and sentence chunking plan
```

## 2. Napraviti zadatke i implementirati jednu promenu

U Codex razgovoru pozvati `$speckit-tasks`, zatim `$speckit-implement`.
To su veštine u razgovoru, ne PowerShell komande.
Pratiti [plan](plan.md) i [ugovor splittera](contracts/chunking.md).

Provere treba da obuhvate prazne ulaze, normalizaciju razmaka, granice `. ! ?`,
završni fragment, tačan limit, spojni razmak, predugu rečenicu, očuvanje sadržaja
i redosleda, nepozitivan limit i nepromenjen `chars` put. Proveriti povezivanje
strategije i prenos metapodataka. Ne menjati očekivanja da bi testovi sakrili regresije.

## 3. Testovi i završno merenje

```powershell
.venv/Scripts/python.exe -m pytest
.venv/Scripts/python.exe -m src.eval_runner --out results/after.json
.venv/Scripts/python.exe -m src.eval_compare results/before.json results/after.json
```

Sačuvati stvarni izlaz testova, eval tabelu i izlaz poređenja u `docs/evidence/`.
Ako se koristi `Tee-Object`, proveriti i native `$LASTEXITCODE`, jer uspešan upis
loga nije dokaz da je komanda prošla. U sandboxu pytest može zahtevati odobrenje
za pristup Windows privremenom direktorijumu; ne menjati sistemsku execution policy.

Oba eval rezultata moraju imati SHA-256
`afe46db1e75a0b85bb5c9a93b6763e3b96e5cd7b289e12da6d2671e4d8650064`.
Poređenje treba da prijavi samo `CHUNK_STRATEGY: 'chars' -> 'sentences'` kao
izmenjeno podešavanje. Cilj je E04/E09 PASS, najmanje 8/12 i bez novih regresija;
to nije unapred dokazan rezultat niti uslov da pošten negativan eksperiment važi.

## 4. Ručno proveriti odgovor i citat

```powershell
.venv/Scripts/python.exe -m src.cli --question "How many business days does a laptop replacement take?" --show-retrieved
.venv/Scripts/python.exe -m src.cli --question "Where do I request a replacement laptop and how long does it take?" --show-retrieved
```

Čitati stvarni odgovor i citirani tekst: `hb-01`, rok, naslov, verzija/status.
Za E09 proveriti i IT portal / Hardware, jer eval eksplicitno proverava samo rok.
Povezati pregled sa barem jednim promenjenim rezultatom. Ako nijedan nije promenjen,
eksplicitno navesti to i proveriti E04. Ako se promeni samo drugo pitanje, pokrenuti
CLI za njega i sačuvati izlaz.

## 5. Pregled diff-a i predaja

```powershell
git diff -- src tests eval
git diff d28cfcf -- eval/eval_set.json src/eval_runner.py src/eval_compare.py
git status --short
```

Drugi diff mora biti prazan. Pregledati i eventualno staged izmene pre commita.
Izmenjeni produkcioni kod treba da obuhvata jednu nameru: sentence strategiju
i njenu aktivaciju. Reference `week06/` i `rag-week-7-weak-checkpoint/` se ne menjaju.

Završni `results/after.json` je podrazumevano ignorisan: dodati tačan izuzetak u
`.gitignore`, eksplicitno ga uključiti u commit ili priložiti kao fajl predaji.
Priložiti oba stvarna JSON-a, poređenje, diff/commit, sve regresije i ograničenja,
AI belešku i proveru, stvarni doprinos oba člana, Week 7 demo lead i peer review.
Zasebni šablon izveštaja trenutno nedostaje u `docs/`; koristiti obavezne stavke
zadatka dok se šablon ne pribavi.

Hipotezu oceniti prema izmerenim rezultatima. Ako se ne potvrdi, objasniti zašto
i zadržati jednu promenu; M2–M6 ne dodavati ovom pre/posle paru.
