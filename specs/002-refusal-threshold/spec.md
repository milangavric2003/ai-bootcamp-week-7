# M3 — prag odbijanja (dodatni eksperiment)

Datum: 19. oktobar 2026. Specifikacija zapisana pre izmene konfiguracije.
Polazno stanje: M1, 9/12, `REFUSAL_THRESHOLD=0.02`.

## Propust i hipoteza

- E10: `What is the current company stock price?` treba odbiti. Sistem umesto
  toga citira MFA i parking; najbolji skor je 0.076923. Tip: pogrešno prihvatanje.
- E11: `What is the parental leave policy?` treba odbiti, ali sistem citira
  godišnji odmor sa skorom 0.222222. Ovo ostaje dokumentovano ograničenje;
  viši prag koji ga odbija ugrozio bi E04 (0.206897).

Jedina promena: `REFUSAL_THRESHOLD` sa 0.02 na 0.10. Hipoteza: E10 prelazi
u PASS, svih devet postojećih prolaza ostaje, E05/E11 ostaju FAIL: cilj 10/12.
Ne menjati TOP_K, chunking, retrieval, korpus, eval skup niti metrike.

Rizik: viši prag može odbiti podržano pitanje sa slabim leksičkim skorom.
Prag je izabran na poznatom eval skupu; rezultat nije dokaz generalizacije.

## Prihvatanje i provera

Pre izmene sačuvati novo M1 merenje i potvrditi slaganje sa `results/after.json`.
Pre i posle pokrenuti svih 35 testova i istih 12 eval pitanja. Poređenje mora
imati isti SHA-256 i samo jedno promenjeno podešavanje. Ručno pregledati CLI
E10 pre/posle, E04 kao rizik regresije i E11 kao preostalo ograničenje.
Sačuvati JSON rezultate, logove, implementacioni diff i izveštaj nezavisno od M1.

M1 ostaje obavezni deo. Korisnik izričito traži dodatni eksperiment sada;
predaja minimuma nije potvrđena, iako zadatak napredni deo predviđa posle nje.
