"""Frozen development-only threshold selection; run from repository root."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from src import config
from src.chunking import build_chunks
from src.corpus import load_corpus
from src.retrieval import retrieve_top_k


def main():
    config.RETRIEVAL_BACKEND = "embeddings"
    folder = Path(__file__).resolve().parent
    data = (folder / "development-set.json").read_bytes()
    chunks = build_chunks(load_corpus())
    rows = []
    for item in json.loads(data):
        retrieved = retrieve_top_k(item["question"], chunks)
        rows.append({**item, "best_score": retrieved[0].score if retrieved else None,
                     "top_k": [{"id": r.chunk.chunk_id, "score": r.score,
                                "text": r.chunk.text} for r in retrieved]})
    candidates = []
    for step in range(2, 17):
        threshold = step / 20
        false_refusals = false_answers = correct_refusals = 0
        for row in rows:
            answered = row["best_score"] is not None and row["best_score"] >= threshold
            false_refusals += row["expected"] == "answer" and not answered
            false_answers += row["expected"] == "refuse" and answered
            correct_refusals += row["expected"] == "refuse" and not answered
        candidates.append(dict(threshold=threshold, false_refusals=false_refusals,
                               false_answers=false_answers, correct_refusals=correct_refusals))
    eligible = [c for c in candidates if c["false_refusals"] == 0]
    best = min(eligible, key=lambda c: (-c["correct_refusals"], c["threshold"])) if eligible else None
    result = {"development_sha256": hashlib.sha256(data).hexdigest(),
              "config": config.snapshot(), "rows": rows, "candidates": candidates,
              "criterion_satisfied": best is not None,
              "selected_threshold": best["threshold"] if best else 0.10}
    (folder / "calibration.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for row in rows:
        print(row["id"], row["expected"], round(row["best_score"], 6) if row["best_score"] is not None else None)
    print("Selected:", best)


if __name__ == "__main__":
    main()
