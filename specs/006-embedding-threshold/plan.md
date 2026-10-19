# Plan

Koristiti lokalni speckit-implement, postojeći .venv i offline model cache.
Zasebni dokazi: docs/evidence/006-embedding-threshold.
Razvojni skup se upisuje pre pokretanja, a deterministički calibrate.py bira
prag prema specifikaciji. Ne pokreće eval_set za izbor praga.
src/config.py dobija novu konstantu; src/rag.py bira prag prema backend-u.
Testovi sa kontrolisanim skorovima pokrivaju granice i nezavisnost pragova.
Prilagoditi postojeći embeddings test koji menja prag odbijanja da menja novi
embeddings parametar. Eval runner/compare/metrike se ne menjaju.
Pre-posle rezultati kopiraju se i u results/ uz namenske gitignore izuzetke.
Izveštaj i README treba da razlikuju raniji rezultat pri 0.10 od kalibrisanog.
