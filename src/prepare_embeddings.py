"""Explicit first-time model download; normal retrieval stays offline."""

import json
from time import perf_counter

from .embeddings import load_model, model_key


def main() -> None:
    model_id, revision, device, cache_dir = model_key()
    started = perf_counter()
    model = load_model(model_id, revision, device, cache_dir, local_files_only=False)
    print(json.dumps({
        "model": model_id, "revision": revision, "device": device,
        "cache_dir": cache_dir,
        "dimensions": model.get_embedding_dimension(),
        "max_sequence_length": model.max_seq_length,
        "prepare_seconds": round(perf_counter() - started, 4),
    }, indent=2))


if __name__ == "__main__":
    main()
