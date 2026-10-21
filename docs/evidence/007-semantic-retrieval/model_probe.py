"""Verify the actual pinned local model, token budget and within-process reuse."""

import importlib.metadata
import json
from pathlib import Path
import sys
from time import perf_counter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))

from src import config, semantic_retrieval as semantic
from src.chunking import build_chunks
from src.corpus import load_corpus
from src.retrieval import retrieve_top_k, searchable_chunks


def main():
    config.RETRIEVAL_BACKEND = "embeddings"
    identity = semantic.model_identity()
    chunks = build_chunks(load_corpus())
    eligible = searchable_chunks(chunks)
    start = perf_counter()
    model = semantic._encoder(identity)
    load_seconds = perf_counter() - start
    original_encode = model.encode
    calls = []
    def counted(texts, **kwargs):
        calls.append(len(texts))
        return original_encode(texts, **kwargs)
    model.encode = counted
    cases = ["How long until I get a new notebook computer?",
             "Where do I request a replacement laptop and how long does it take?"]
    measured = []
    for question in cases:
        start = perf_counter()
        result = retrieve_top_k(question, chunks)
        measured.append({"question": question, "seconds": perf_counter() - start,
            "top_k": [{"chunk_id": r.chunk.chunk_id, "doc_id": r.chunk.doc_id,
                       "score": r.score, "text": r.chunk.text} for r in result]})
    assert calls == [len(eligible), 1, 1], calls
    dimension = model.get_embedding_dimension()
    assert dimension == 384
    token_lengths = [len(tokens) for tokens in model.tokenizer(
        [c.text for c in eligible], truncation=False)["input_ids"]]
    cache_files = {p.resolve() for p in Path(identity.cache).rglob("*") if p.is_file()}
    value = {"identity": identity.__dict__, "versions": {name: importlib.metadata.version(name)
        for name in ["sentence-transformers", "torch", "transformers", "huggingface-hub", "numpy"]},
        "model_load_seconds": load_seconds, "dimension": dimension,
        "eligible_chunks": len(eligible), "encoding_batch_sizes": calls,
        "maximum_chunk_tokens": max(token_lengths), "model_max_sequence_length": model.max_seq_length,
        "all_chunks_fit_model": max(token_lengths) <= model.max_seq_length,
        "model_cache_bytes": sum(p.stat().st_size for p in cache_files), "queries": measured}
    with (HERE / "real-model-verification.json").open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")
    print(json.dumps(value, indent=2))


if __name__ == "__main__":
    main()
