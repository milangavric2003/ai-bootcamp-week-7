"""Optional local sentence embeddings and a small, exact in-memory index."""

from functools import lru_cache
from math import fsum
from pathlib import Path

from . import config
from .chunking import Chunk


def model_key() -> tuple[str, str, str, str]:
    cache = Path(config.EMBEDDING_CACHE_DIR)
    if not cache.is_absolute():
        cache = Path(__file__).resolve().parents[1] / cache
    return (config.EMBEDDING_MODEL, config.EMBEDDING_REVISION,
            config.EMBEDDING_DEVICE, str(cache))


def load_model(model_id: str, revision: str, device: str, cache_dir: str,
               *, local_files_only: bool):
    # Keep the standard-library-only lexical pipeline usable without this extra.
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise RuntimeError(
            "Install optional embeddings dependencies with "
            "python -m pip install -r requirements-embeddings.txt"
        ) from exc
    return SentenceTransformer(
        model_id, revision=revision, device=device, cache_folder=cache_dir,
        local_files_only=local_files_only, trust_remote_code=False,
    )


@lru_cache(maxsize=1)
def _model(key: tuple[str, str, str, str]):
    try:
        return load_model(*key, local_files_only=True)
    except OSError as exc:
        raise RuntimeError(
            "Cannot load the pinned embeddings model from local cache. "
            "Run python -m src.prepare_embeddings with network access first."
        ) from exc


def _encode(model, texts: tuple[str, ...]) -> tuple[tuple[float, ...], ...]:
    vectors = model.encode(
        list(texts), normalize_embeddings=True, show_progress_bar=False,
    )
    return tuple(tuple(float(value) for value in vector) for vector in vectors)


@lru_cache(maxsize=2)
def _document_vectors(key: tuple[str, str, str, str], texts: tuple[str, ...]):
    # Text and model identity determine vectors; current Chunk metadata is attached
    # by retrieval.py, so cached vectors never return stale citation metadata.
    return _encode(_model(key), texts)


def score_chunks(query: str, chunks: list[Chunk]) -> list[float]:
    """Cosine scores in input order; both sides are encoded with the same model."""
    if not chunks or not query.strip():
        return []
    key = model_key()
    documents = _document_vectors(key, tuple(chunk.text for chunk in chunks))
    query_vector = _encode(_model(key), (query,))[0]
    # Unit-normalized dot product is cosine. Keep signed scores and only clamp
    # floating point roundoff at the mathematical boundaries.
    return [max(-1.0, min(1.0, fsum(a * b for a, b in zip(query_vector, doc, strict=True))))
            for doc in documents]


def clear_cache() -> None:
    """Release the process-local index/model, e.g. between controlled tests."""
    _document_vectors.cache_clear()
    _model.cache_clear()
