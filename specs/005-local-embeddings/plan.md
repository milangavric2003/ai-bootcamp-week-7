# Plan lokalnih embeddings

Koristiti lokalni `speckit-implement` postupak; nema extension hook konfiguracije.
Radna grana je postojeći main; bez commitovanja ili push-a u ovom koraku.

- `requirements-embeddings.txt`: opciona, tačno verzionisana biblioteka
  sentence-transformers 6.1.0. Zabeležiti uspešno instalirane transitive verzije.
- `src/config.py`: backend iz RAG_RETRIEVAL_BACKEND (default lexical), model,
  revizija, CPU i cache direktorijum u snapshot-u.
- `src/embeddings.py`: lazy import/load, lokalni model, bounded procesni cache
  modela i matrice eligible tekstova, cosine skorovi bez promene Chunk podataka.
- `src/prepare_embeddings.py`: eksplicitno preuzimanje javnog modela u projektni
  `.cache/embeddings`; runtime ostaje local_files_only=True.
- `src/retrieval.py`: validacija izbora backenda, postojeći M5 filter i zajednički
  minimum/sort/top-k. `src/cli.py`: opcioni argument za izbor backenda.
- Testovi bez mreže/modela preko kontrolisanog encoder-a. Pravi model samo za
  lokalnu smoke proveru, ne za obavezno pokretanje testova.
- README, quickstart i kratka implementaciona beleška sa stanjem koraka 2/3.
  Ne menjati istorijske JSON rezultate, eval skup niti src/eval_runner.py.

Pragovi ostaju 0.01/0.10: ne označavati ih kao semantički kalibrisane.
Runtime cache i model fajlovi su ignorisani Git-om, dok spec i dokazi ostaju.

Izvori provereni pre implementacije:
- https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2 (Apache-2.0,
  engleski, 384 dimenzije, 256 wordpieces).
- https://www.sbert.net/docs/package_reference/sentence_transformer/model.html
  (revision, cache_folder, local_files_only, encode(normalize_embeddings=True)).
