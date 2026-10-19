# Lokalni embeddings — pokretanje

Iz korena projekta, PowerShell, postojeći `.venv`:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-embeddings.txt
.\.venv\Scripts\python.exe -m src.prepare_embeddings
.\.venv\Scripts\python.exe -m src.cli --retrieval-backend embeddings --question "How long until I get a new notebook computer?" --show-retrieved
```

Prve dve komande zahtevaju mrežu. Model se preuzima u ignorisani
`.cache/embeddings` u korenu projekta; revizija je zamrznuta u `src/config.py`.
Normalni CLI učitava isključivo lokalni cache; dostupan internet nije potreban.
Bez `--retrieval-backend` i bez promenljive okruženja ostaje leksička pretraga.
Leksički režim zahteva samo originalni `requirements.txt`.

Za standardni eval runner, bez menjanja koda/metrika, backend birati procesnom
promenljivom okruženja. Sledeći blok ponavlja poređenje trenutne konfiguracije
sa zasebnim pragovima: lexical 0.10 i embeddings 0.50.

```powershell
$previousBackend = $env:RAG_RETRIEVAL_BACKEND
try {
    $env:RAG_RETRIEVAL_BACKEND = "lexical"
    $runId = Get-Date -Format "yyyyMMdd-HHmmss"
    $beforeFile = "results/before-embeddings-$runId.json"
    $afterFile = "results/after-embeddings-$runId.json"
    .\.venv\Scripts\python.exe -m src.eval_runner --out $beforeFile
    $env:RAG_RETRIEVAL_BACKEND = "embeddings"
    .\.venv\Scripts\python.exe -m src.eval_runner --out $afterFile
    .\.venv\Scripts\python.exe -m src.eval_compare $beforeFile $afterFile
} finally {
    $env:RAG_RETRIEVAL_BACKEND = $previousBackend
}
```

U ovom paru konfiguracija treba da se razlikuje samo po RETRIEVAL_BACKEND;
identitet modela se beleži u oba snapshot-a. Ne porediti nove konfiguracione
ključeve sa istorijskim run-om kao da su dodatne merene promene pipeline-a.
Istorijski baseline ostaje referenca za jednakost leksičkih rezultata.

Prvo istorijsko embeddings merenje koristilo je zajednički prag 0.10.
Sada `REFUSAL_THRESHOLD=0.10` važi samo za lexical, a
`EMBEDDING_REFUSAL_THRESHOLD=0.50` za embeddings. Retrieval minimum ostaje 0.01.
Zasebna [kalibracija](../../docs/embedding-threshold-report.md) daje 11/12;
E11 ostaje problem. Semantički sličan odlomak ne garantuje podršku odgovoru.

Testovi ne preuzimaju model i ne zahtevaju opcione biblioteke:

```powershell
$pytestTemp = Join-Path (Get-Location) ('.venv/pytest-embeddings-' + [guid]::NewGuid().ToString('N'))
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider --basetemp $pytestTemp
```

Model se učitava jednom po procesu, kao i vektori datih eligible tekstova.
Svako novo CLI pokretanje je novi proces i ponovo gradi mali indeks u memoriji.
Nema trajnog vektorskog indeksa, vektorske baze, hibridnog spajanja ili LLM-a.
