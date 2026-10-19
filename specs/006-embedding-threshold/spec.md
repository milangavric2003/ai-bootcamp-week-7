# Zaseban prag odbijanja za embeddings

Datum: 19. oktobar 2026. Napisano pre kalibracije i izmene pipeline-a.
Rad na grani embeddings, po Vedranovom zahtevu.

Polazno merenje: `results/after-embeddings-20261019-231508.json`, 10/12.
E05 je popravljen, E10 regresira: cosine 0.175122 prelazi nasleđeni prag 0.10.
E11 ostaje pogrešan odgovor, cosine 0.504503. Poznati eval rezultati su već
pregledani; ne predstavljaju neviđen test niti dokaz opšte tačnosti.

Jedna namera: kalibrisati zaseban prag odbijanja za embeddings.
Leksički REFUSAL_THRESHOLD ostaje 0.10; dodati EMBEDDING_REFUSAL_THRESHOLD.
Retriever, TOP_K, minimalni retrieval skor, model, korpus i metrike su isti.

Pre izvršavanja zamrznuti zaseban mali razvojni skup sa answer/refuse oznakama,
izvan eval/eval_set.json. Skup služi za podešavanje; nije nezavisni test.
Fiksni kandidati: 0.10, 0.15, ..., 0.80. Među pragovima koji ne odbijaju
nijedno podržano razvojno pitanje izabrati onaj koji odbija najviše nepodržanih;
pri izjednačenju birati najniži prag. Ako nema takvog kandidata, sačuvati 0.10
i prijaviti da kriterijum nije ispunjen. Ne menjati skup/kandidate posle rezultata.

Hipoteza: viši cosine prag smanjuje nepodržane odgovore, uključujući E10,
uz očuvanje podržanih odgovora. E11 nije unapred garantovan. Rizik: lažno
odbijanje slabo sličnog, ali relevantnog dokaza na drugim upitima.

Provera: development score tabela i izbor, unit granice po backend-u, cela
evaluacija pre/posle na istih 12 pitanja, nepromenjena leksička evaluacija,
CLI E05/E10/E11. Sačuvati stare i nove JSON rezultate i sve regresije.
