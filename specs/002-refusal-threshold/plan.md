# Plan M3

Postojeći lokalni Python pipeline, Python 3.14.7 / pytest 8.3.3.
Bez novih zavisnosti ili infrastrukture. Jedna izmena u `src/config.py`.
Postojeći testovi i puna evaluacija proveravaju promenu konfiguracije;
nema potrebe za testom koji samo ponavlja novu vrednost konstante.

Dokazi: `docs/evidence/002-m3/`, uključujući before/after JSON tako da nisu
obuhvaćeni pravilom `results/*.json`. Privremeni pytest direktorijumi su u
`.venv/`, uz `-p no:cacheprovider`, zbog prethodno potvrđenih Windows dozvola.
Sačuvati hash-eve izvora i postojećih M1 rezultata pre i posle; jedini izmenjen
izvor treba da bude `src/config.py`. Dokumentovati rezultat u `docs/m3-report.md`.
