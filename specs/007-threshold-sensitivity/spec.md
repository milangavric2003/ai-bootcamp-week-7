# Prag 0.51 — dodatni eksperiment na poznatom eval skupu

19. oktobar 2026. Vedran je izričito odobrio pomeranje embeddings praga
sa 0.50 na 0.51 nakon pregleda E11 (cosine 0.504503).
Ovo je podešavanje uz uvid u eval skup, ne nezavisna kalibracija ili holdout.
Razvojna kalibracija 0.50 i njeni dokazi ostaju istorijski rezultat.

Hipoteza: E11 postaje ispravno odbijanje; svih ostalih 11 prolaza ostaje,
jer najniži vodeći skor podržanih eval pitanja iznosi 0.632196.
Promeniti samo EMBEDDING_REFUSAL_THRESHOLD na 0.51. Lexical ostaje 0.10.
Rizik: podržana pitanja sa skorom u [0.50, 0.51) sada se odbijaju.
Sačuvati pre/posle, pokrenuti pune testove, isti eval, poređenje i E11 CLI;
proveriti nepromenjene lexical rezultate, retrieval, metrike i istorijske JSON-e.
