# Lokalni embeddings — status implementacije

Naknadni status: Vedran je izvršio punu evaluaciju pri pragu 0.10 (10/12,
E05 popravljen, E10 regresija). Zatim je uvedena zasebna
[kalibracija praga](embedding-threshold-report.md): embeddings 0.50 daje 11/12,
lexical ostaje 0.10 i 10/12; 86/86 testova prolazi. Tekst ispod čuva istorijsku
evidenciju prvobitne implementacije koraka 2/3, pre tih merenja.

Datum: 19. oktobar 2026. Na Vedranov zahtev implementirani su koraci 2/3 plana:
lokalni model i tačna pretraga istih odlomaka u memoriji. **70/70 testova prolazi.**
Leksička putanja ostaje podrazumevana i reprodukuje baseline **10/12**.
Puna embeddings evaluacija, poređenje svih 12 pitanja, izbor kalibrisanih
semantičkih pragova i Vedranova nezavisna ručna provera još nisu izvršeni.

## Šta je uvedeno

- Opcioni backend `embeddings`, dostupan kroz `--retrieval-backend` u CLI-ju
  ili `RAG_RETRIEVAL_BACKEND` za postojeći eval runner i druge pozive.
- Lokalni `sentence-transformers/all-MiniLM-L6-v2`, javna zamrznuta revizija
  `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`, CPU, 384 dimenzije.
- Isti normalizovani query/document vektori i dot product kao cosine sličnost.
  Nema dodatnog pomeranja skale skorova ili podešavanja prema pojedinačnim pitanjima.
- M5 filter pre kodiranja, isti Chunk objekti i metapodaci za citate.
- Model se učitava jednom po procesu. Indeks vektora kešira se prema modelu,
  reviziji, uređaju, putanji i tekstovima eligible odlomaka. Izmena tekstova ili
  filtera pravi drugi indeks; identifikatori/citati dolaze iz aktuelnih objekata.
- Preuzimanje je eksplicitno kroz `python -m src.prepare_embeddings`.
  Normalni retrieval koristi samo lokalni cache; neuspeh ne prelazi tiho na lexical.

Hibridno spajanje rang-lista, LLM generisanje i nova infrastruktura nisu
deo ovog koraka. [Specifikacija](../specs/005-local-embeddings/spec.md) i
[plan](../specs/005-local-embeddings/plan.md) zapisani su pre implementacije;
nisu posebno commitovani pre koda. [Quickstart](../specs/005-local-embeddings/quickstart.md)
sadrži setup, CLI i komande za sledeći korak pune evaluacije.

## Provere

17 novih offline provera plus 53 postojeće: **70 passed** na Windows-u,
Python 3.14.7, pytest 8.3.3. Novi testovi koriste kontrolisane vektore i ne
zahtevaju opcione pakete ili mrežu. Pokrivaju semantičko rangiranje, negativne
cosine skorove, granicu minimuma, top-k i izjednačenja, filter verzija,
keširanje/osvežavanje, offline učitavanje, greške, CLI izbor i tok do citata.
Prvi red run pre implementacije pada pri importu tada nepostojećeg modula.

Ponovna provera podrazumevanog lexical režima potvrđuje identične rezultate
svih 12 pitanja i zbirne metrike kao `docs/evidence/004-m2/retained.json`.
Novi config snapshot dodaje backend i identitet modela; stari ključevi su isti.
Eval skup, obračun metrika, runner i originalni JSON rezultati nisu izmenjeni.

Sa pravim modelom pokrenut je samo smoke upit E05, dva puta u istom procesu,
uz `HF_HUB_OFFLINE=1` i blokirane `socket.connect`/`connect_ex` pozive:

```text
How long until I get a new notebook computer?
0.6322 hb-01-chunk-1: ... handover can take up to 5 business days.
0.4767 hb-01-chunk-0: Laptop replacement: broken, lost or stolen laptops can be replaced.
Refused: False
```

Oba citata su current, verzija 2026. Model za ovaj upit pronalazi traženi rok;
**to nije tvrdnja o ukupnom PASS broju** niti dokaz da nema regresija.
Procesni cache beleži jedno učitavanje modela, jedno kodiranje odlomaka i hit
pri ponovljenom upitu.

Zabeleženo pripremanje/preuzimanje: 17.34 s; prvi offline upit sa učitavanjem
modela: 7.11 s; ponovljeni upit: 0.0148 s. Ovo su pojedinačni smoke brojevi,
ne ponovljeni benchmark. Model cache sadrži 91,578,610 bajtova fajlova
(oko 91.6 MB), bez Python paketa. Preuzimanje i instalacija su uspeli;
lokalni runtime nema naplatu API poziva, ali koristi CPU, memoriju i disk.

## Zavisnosti i ograničenja

Opcioni `requirements-embeddings.txt` pin-uje sentence-transformers 6.1.0.
Instalirani su između ostalog torch 2.14.1, transformers 5.20.2 i numpy 2.5.4;
potpun spisak je u dokazima. Osnovni `requirements.txt` ostaje neizmenjen.
Model/cache se ne verzioniše; na drugom računaru treba ponoviti setup.

Model je engleski, Apache-2.0; dugi ulazi se podrazumevano skraćuju na 256
wordpieces. Izvori: [model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
i [SentenceTransformer API](https://www.sbert.net/docs/package_reference/sentence_transformer/model.html).

Nasleđeni pragovi 0.01/0.10 nisu kalibrisani za cosine. Na semantičkoj skali
mogu prihvatiti nepodržana pitanja; blizina annual/parental leave ne garantuje
da postoji dokaz za E11. Pragove ne menjati tiho tokom prvog poređenja.

## Dokazi i doprinos

| Dokaz | Fajl |
| --- | --- |
| Polazno stanje i hash-evi | [before-manifest.json](evidence/005-embeddings/before-manifest.json) |
| Red test pre implementacije | [pytest-red.txt](evidence/005-embeddings/pytest-red.txt) |
| Cela test provera | [pytest-after.txt](evidence/005-embeddings/pytest-after.txt) |
| Leksička kompatibilnost | [lexical-compatibility.json](evidence/005-embeddings/lexical-compatibility.json) |
| Instalirane verzije | [installed-packages.txt](evidence/005-embeddings/installed-packages.txt) |
| Model setup | [model-setup.txt](evidence/005-embeddings/model-setup.txt) |
| Pravi offline upit i cache | [offline-smoke.txt](evidence/005-embeddings/offline-smoke.txt) |
| Integritet postojećih fajlova | [integrity.json](evidence/005-embeddings/integrity.json) |

Vedran je izabrao embeddings kao sledeći eksperiment i odobrio implementaciju
modela i pretrage u memoriji. Codex je napisao specifikaciju i kod, instalirao
zavisnosti, preuzeo model i izvršio ovde navedene provere koristeći lokalni
`speckit-implement` postupak. Ova izvršavanja se pripisuju Codexu; Vedranova
nova nezavisna provera nije pretpostavljena. Sledeći koraci su puna evaluacija,
poređenje i pregled citata prema quickstart-u, zatim odluka o kalibraciji ili
hibridnom eksperimentu na osnovu izmerenih rezultata.
