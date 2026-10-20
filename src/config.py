"""All tunable parameters of the RAG pipeline.

The eval runner records every value in this module in its JSON output.
"""

import os

# Chunking
CHUNK_STRATEGY = "sentences"  # "chars" or "sentences"
CHUNK_SIZE = 140
CHUNK_OVERLAP = 30

# Retrieval
RETRIEVAL_BACKEND = os.environ.get("RAG_RETRIEVAL_BACKEND", "lexical")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_REVISION = "1110a243fdf4706b3f48f1d95db1a4f5529b4d41"
EMBEDDING_DEVICE = "cpu"
EMBEDDING_CACHE_DIR = ".cache/embeddings"
TOP_K = 2
RETRIEVAL_MIN_SCORE = 0.01
STOPWORDS_ENABLED = False  # M2 implemented; disabled after the measured E09 regression.
CURRENT_ONLY = True

# Answering
REFUSAL_THRESHOLD = 0.10  # Lexical score; preserve the M3 calibration.
EMBEDDING_REFUSAL_THRESHOLD = 0.51  # Eval-informed follow-up; see docs/threshold-051-report.md.
CITATION_MIN_SCORE = None  # None or a float score


def snapshot() -> dict:
    """Return the current configuration as a plain dict."""
    return {
        name: value
        for name, value in globals().items()
        if name.isupper()
    }
