# Lokalni embeddings — implementacija koraka 2 i 3

Datum: 19. oktobar 2026. Specifikacija zapisana pre implementacije.
Korisnik je potvrdio postojeći baseline i zatražio uvođenje lokalnog modela
i pretrage u memoriji. Puna uporedna evaluacija i kalibracija slede zasebno.

## Propusti i hipoteza

Polazno stanje M1+M3+M5, M2=False: 10/12, 53 testa.
E05 (`How long until I get a new notebook computer?`) očekuje `hb-01` i
`5 business days`, ali citira onboarding/annual leave. Tip: neuspeh parafraze.
E11 (`What is the parental leave policy?`) treba odbiti, ali citira annual
leave. Tip: nepodržan odgovor. Embeddings ciljaju E05; za E11 nema garancije
jer semantički sličan tekst ne mora podržavati konkretan odgovor.

Jedna namera: opcioni embeddings retrieval backend umesto leksičkog skora.
Model `sentence-transformers/all-MiniLM-L6-v2`, zamrznuta javna revizija
`1110a243fdf4706b3f48f1d95db1a4f5529b4d41`, CPU, normalizovani vektori,
tačna cosine pretraga u memoriji. Bez vektorske baze ili API poziva za upite.

## Ugovor

- Podrazumevana leksička putanja mora reprodukovati sve postojeće rezultate.
- Embeddings se uključuju kroz `RAG_RETRIEVAL_BACKEND=embeddings` ili CLI
  `--retrieval-backend embeddings`. Model i parametri ulaze u config snapshot.
- Isti Chunk objekti i tekstovi; M5 filter prethodi kodiranju. TOP_K, minimalni
  skor, pravila odgovora, prag odbijanja, eval pitanja i metrike se ne menjaju.
- Normalizovati vektore i računati dot product kao cosine; veći skor prvi,
  izjednačenja razrešava chunk_id. Negativne sličnosti ne pretvarati u pozitivne.
- Jednom učitati model i jednom kodirati dati niz eligible tekstova po procesu.
  Promena sadržaja, redosleda ili identiteta modela mora osvežiti indeks.
- Offline rad: preuzimanje je posebna eksplicitna setup komanda; runtime koristi
  isključivo lokalni cache, bez tihog fallback-a na lexical pri grešci.
- Leksička putanja ne zahteva sentence-transformers niti preuzima model.
- Prazni upiti/eligible skupovi vraćaju prazne rezultate bez učitavanja modela.
- Ne označavati punu evaluaciju ili ljudski review završenim na osnovu testova.

## Provera i rizici

Testovi sa kontrolisanim vektorima proveravaju ranking, granice skorova,
izjednačenja, filter, cache, osvežavanje, greške i tok do odgovora/citata.
Realni model proveriti jednim offline CLI upitom i dokazati leksičku regresiju
jednakošću sa sačuvanim baseline-om. Ne tvrditi PASS rast pre pune evaluacije.
Nasleđeni pragovi 0.01/0.10 nisu kalibrisani za cosine: novo značenje skorova
može pogoršati odbijanje. Model može skratiti duge ulaze na 256 wordpieces.

Ovo je opcioni napredni rad na korisnikov zahtev; M1 ostaje obavezna osnova.
