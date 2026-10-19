"""All tunable parameters of the RAG pipeline.

The eval runner records every value in this module in its JSON output.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

from .generation_errors import ConfigurationError
from .generation_prompt import SYSTEM_PROMPT_SHA256 as GEMMA_PROMPT_SHA256


# Never bind the API key here: snapshot() records all uppercase module values.
load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False, interpolate=False)


def _number(name: str, default: str, convert):
    try:
        return convert(os.environ.get(name, default))
    except (ValueError, TypeError):
        raise ConfigurationError(f"{name} must be a valid number.") from None


# Chunking
CHUNK_STRATEGY = "sentences"  # "chars" or "sentences"
CHUNK_SIZE = 140
CHUNK_OVERLAP = 30

# Retrieval
TOP_K = 2
RETRIEVAL_MIN_SCORE = 0.01
STOPWORDS_ENABLED = False  # M2 implemented; disabled after the measured E09 regression.
CURRENT_ONLY = True

# Answering
REFUSAL_THRESHOLD = 0.10
CITATION_MIN_SCORE = None  # None or a float score
ANSWER_BACKEND = os.environ.get("ANSWER_BACKEND", "extractive")
GEMMA_PROVIDER = "google"
GEMMA_MODEL = os.environ.get("GEMMA_MODEL", "gemma-4-26b-a4b-it")
GEMMA_TEMPERATURE = _number("GEMMA_TEMPERATURE", "0", float)
GEMMA_MAX_OUTPUT_TOKENS = _number("GEMMA_MAX_OUTPUT_TOKENS", "1024", int)
GEMMA_THINKING_LEVEL = os.environ.get("GEMMA_THINKING_LEVEL", "minimal")
GEMMA_TIMEOUT_SECONDS = _number("GEMMA_TIMEOUT_SECONDS", "30", float)
# Conservative application input budget in UTF-8 bytes, not a model token claim.
GEMMA_MAX_INPUT_BYTES = 65536


def snapshot() -> dict:
    """Return the current configuration as a plain dict."""
    return {
        name: value
        for name, value in globals().items()
        if name.isupper()
    }
