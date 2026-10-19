from dataclasses import dataclass
import re

from . import config
from .chunking import Chunk


TOKEN_RE = re.compile(r"[a-zA-Z0-9]+")
# Frozen M2 vocabulary; see specs/004-stopword-filter/plan.md.
STOPWORDS = frozenset({
    "a", "an", "and", "are", "as", "at", "be", "been", "but", "by",
    "can", "do", "does", "for", "from", "had", "has", "have", "how", "i",
    "in", "is", "it", "of", "on", "or", "that", "the", "their", "there",
    "these", "they", "this", "to", "was", "were", "what", "when", "where", "with",
})


def tokenize(text: str) -> list[str]:
    tokens = [token.lower() for token in TOKEN_RE.findall(text)]
    if config.STOPWORDS_ENABLED:
        return [token for token in tokens if token not in STOPWORDS]
    return tokens


@dataclass(frozen=True)
class RetrievalResult:
    chunk: Chunk
    score: float


def lexical_score(query: str, chunk_text: str) -> float:
    q_tokens = tokenize(query)
    c_tokens = tokenize(chunk_text)
    if not q_tokens or not c_tokens:
        return 0.0

    q_set = set(q_tokens)
    overlap = sum(1 for token in c_tokens if token in q_set)
    return overlap / len(c_tokens)


def searchable_chunks(chunks: list[Chunk]) -> list[Chunk]:
    if config.CURRENT_ONLY:
        return [chunk for chunk in chunks if chunk.status != "superseded"]
    return chunks


def retrieve_top_k(query: str, chunks: list[Chunk], k: int | None = None) -> list[RetrievalResult]:
    k = config.TOP_K if k is None else k
    if k <= 0:
        raise ValueError("k must be > 0")

    if config.RETRIEVAL_BACKEND not in {"lexical", "embeddings"}:
        raise ValueError(f"Unknown RETRIEVAL_BACKEND: {config.RETRIEVAL_BACKEND}")
    eligible = searchable_chunks(chunks)
    if not eligible or not query.strip():
        return []
    if config.RETRIEVAL_BACKEND == "embeddings":
        from .embeddings import score_chunks
        scores = score_chunks(query, eligible)
    else:
        scores = [lexical_score(query, chunk.text) for chunk in eligible]
    scored = [RetrievalResult(chunk=chunk, score=score)
              for chunk, score in zip(eligible, scores, strict=True)]
    filtered = [item for item in scored if item.score >= config.RETRIEVAL_MIN_SCORE]
    filtered.sort(key=lambda item: (-item.score, item.chunk.chunk_id))
    return filtered[:k]
