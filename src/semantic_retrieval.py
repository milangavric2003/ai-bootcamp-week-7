"""Optional local sentence representations for the existing small corpus.

No model is imported or downloaded merely by importing this module. Vectors are
cached by original text, never by citation metadata, and normal loading is offline.
"""

from dataclasses import dataclass
from functools import lru_cache
from math import fsum, hypot, isfinite
from pathlib import Path
import re

from . import config
from .chunking import Chunk
from .retrieval_errors import RetrievalError


@dataclass(frozen=True)
class ModelIdentity:
    name: str
    revision: str
    device: str
    cache: str


def model_identity() -> ModelIdentity:
    if not isinstance(config.EMBEDDING_REVISION, str) or not re.fullmatch(r"[a-fA-F0-9]{40}", config.EMBEDDING_REVISION):
        raise RetrievalError("The embedding revision must be a full immutable commit ID.")
    if not isinstance(config.EMBEDDING_MODEL, str) or not config.EMBEDDING_MODEL.strip():
        raise RetrievalError("Set a nonempty embedding model identifier.")
    if not isinstance(config.EMBEDDING_CACHE_DIR, str) or not config.EMBEDDING_CACHE_DIR.strip():
        raise RetrievalError("Set a nonempty local embedding cache directory.")
    cache = Path(config.EMBEDDING_CACHE_DIR).expanduser()
    if not cache.is_absolute():
        cache = Path(__file__).resolve().parents[1] / cache
    return ModelIdentity(config.EMBEDDING_MODEL, config.EMBEDDING_REVISION,
                         config.EMBEDDING_DEVICE, str(cache.resolve()))


def _create_encoder(identity: ModelIdentity):
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        raise RetrievalError(
            "Install optional model dependencies: python -m pip install -r requirements-embeddings.txt"
        ) from None
    try:
        return SentenceTransformer(identity.name, revision=identity.revision,
            device=identity.device, cache_folder=identity.cache,
            local_files_only=True, trust_remote_code=False)
    except (OSError, ValueError, RuntimeError):
        raise RetrievalError(
            "Cannot load the pinned local embedding model. Run python -m src.prepare_embeddings first."
        ) from None


@lru_cache(maxsize=1)
def _encoder(identity: ModelIdentity):
    return _create_encoder(identity)


def _encode(identity: ModelIdentity, texts: tuple[str, ...]) -> tuple[tuple[float, ...], ...]:
    try:
        encoded = _encoder(identity).encode(list(texts), normalize_embeddings=True,
            convert_to_numpy=True, show_progress_bar=False)
    except RetrievalError:
        raise
    except (ValueError, RuntimeError, OSError):
        raise RetrievalError("The local embedding model could not encode the supplied text.") from None
    try:
        vectors = tuple(tuple(float(value) for value in row) for row in encoded)
        if len(vectors) != len(texts):
            raise ValueError
        dimension = len(vectors[0]) if vectors else 0
        normalized = []
        for row in vectors:
            if not dimension or len(row) != dimension or not all(isfinite(value) for value in row):
                raise ValueError
            length = hypot(*row)
            if not isfinite(length) or length == 0:
                raise ValueError
            normalized.append(tuple(value / length for value in row))
        return tuple(normalized)
    except (TypeError, ValueError, OverflowError):
        raise RetrievalError("The embedding model returned invalid or mismatched vectors.") from None


@lru_cache(maxsize=2)
def _corpus_vectors(identity: ModelIdentity, texts: tuple[str, ...]):
    return _encode(identity, texts)


def semantic_scores(question: str, chunks: list[Chunk]) -> list[float]:
    """Cosine similarity in the same order as caller-provided eligible chunks."""
    if not chunks or not question.strip():
        return []
    identity = model_identity()
    documents = _corpus_vectors(identity, tuple(chunk.text for chunk in chunks))
    query = _encode(identity, (question,))[0]
    if any(len(document) != len(query) for document in documents):
        raise RetrievalError("Question and corpus embedding vector dimensions differ.")
    return [max(-1.0, min(1.0, fsum(a * b for a, b in zip(query, document, strict=True))))
            for document in documents]


def clear_caches() -> None:
    """Release the bounded process-local vectors/model, e.g. between experiments."""
    _corpus_vectors.cache_clear()
    _encoder.cache_clear()
