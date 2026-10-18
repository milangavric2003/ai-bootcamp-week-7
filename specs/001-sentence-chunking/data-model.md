# Data model: postojeće strukture za M1

Nema novih trajnih entiteta, promena šeme ili migracija.

| Entitet | Postojeća polja | Značenje za M1 |
| --- | --- | --- |
| `Document` | `doc_id`, `title`, `section`, `version`, `status`, `text` | Izvor ostaje isti; rečenice se ne spajaju između dokumenata. |
| `Chunk` | `chunk_id`, `doc_id`, `title`, `version`, `status`, `text` | Tekst menja granice; ostala polja prenosi postojeći `build_chunks`. |
| `RetrievalResult` | `chunk`, `score` | Dobija nove odlomke uz isti scorer i redosled sortiranja. |
| `RagAnswer` | `answer`, `citations`, `refused`, `retrieved` | Oblik ostaje isti; sadržaj može biti drugačiji zbog odlomaka. |
| Eval run | `created_at`, `eval_set_sha256`, `config`, `summary`, `results` | Šema i obračun ostaju isti; poredi se sa sačuvanim baseline-om. |

## Validacija i relacije

- Svaki chunk pripada tačno jednom dokumentu i zadržava njegove metapodatke.
- ID ostaje `<doc_id>-chunk-<index>`, od indeksa 0, u redosledu izvornog teksta.
- Isti dokument, parametri i strategija daju isti niz ID-jeva i tekstova.
- Isti ID u dva različita režima ne mora označavati isti tekst. Citati se
  tumače sa konfiguracijom konkretnog merenja.
- U sentence režimu chunk sadrži cele rečenice, bez ponavljanja putem overlap-a.
- Chunk može preći ciljnu veličinu samo kao jedna preduga rečenica.
- `CHUNK_OVERLAP` ostaje polje konfiguracije i koristi se samo u `chars` režimu.
- Eval skup i njegov SHA-256 moraju ostati identični pre i posle.

Tok podataka ostaje `Document → Chunk → RetrievalResult → RagAnswer → eval run`.
M1 menja samo način pravljenja tekstova u koraku `Document → Chunk`.
