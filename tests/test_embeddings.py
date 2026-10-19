"""Offline contracts: controlled vectors, no downloads or optional packages."""

import builtins
import math
import sys
from types import SimpleNamespace
from dataclasses import replace

import pytest

from src import config, embeddings
from src.chunking import Chunk
from src.rag import build_grounded_answer
from src.retrieval import retrieve_top_k


def chunk(chunk_id, text, status="current"):
    return Chunk(chunk_id, "d", "Title", "2026", status, text)


class Encoder:
    def __init__(self):
        self.calls = []
        self.vectors = {
            "notebook": [1.0, 0.0],
            "laptop deadline": [1.0, 0.0],
            "irrelevant": [0.0, 1.0],
            "opposite": [-1.0, 0.0],
            "partial": [0.5, math.sqrt(0.75)],
        }

    def encode(self, texts, **kwargs):
        assert kwargs == {"normalize_embeddings": True, "show_progress_bar": False}
        self.calls.append(tuple(texts))
        return [self.vectors[t] for t in texts]


@pytest.fixture
def encoder(monkeypatch):
    embeddings.clear_cache()
    fake = Encoder()
    monkeypatch.setattr(config, "RETRIEVAL_BACKEND", "embeddings", raising=False)
    monkeypatch.setattr(config, "CURRENT_ONLY", True)
    monkeypatch.setattr(config, "RETRIEVAL_MIN_SCORE", 0.01)
    monkeypatch.setattr(embeddings, "load_model", lambda *args, **kwargs: fake)
    yield fake
    embeddings.clear_cache()


def test_semantic_match_without_shared_words_and_current_filter(encoder):
    old = chunk("old", "laptop deadline", "superseded")
    current = chunk("new", "laptop deadline")
    results = retrieve_top_k("notebook", [old, chunk("noise", "irrelevant"), current])
    assert [(r.chunk, r.score) for r in results] == [(current, 1.0)]
    assert encoder.calls[0] == ("irrelevant", "laptop deadline")


def test_cosine_sign_minimum_ties_and_top_k(encoder, monkeypatch):
    monkeypatch.setattr(config, "RETRIEVAL_MIN_SCORE", 0.5)
    chunks = [chunk("z", "laptop deadline"), chunk("a", "laptop deadline"),
              chunk("partial", "partial"), chunk("negative", "opposite")]
    assert [r.chunk.chunk_id for r in retrieve_top_k("notebook", chunks, k=3)] == ["a", "z", "partial"]
    assert len(retrieve_top_k("notebook", chunks, k=1)) == 1


def test_index_reuse_and_content_or_model_revision_invalidation(encoder, monkeypatch):
    chunks = [chunk("a", "laptop deadline")]
    retrieve_top_k("notebook", chunks)
    retrieve_top_k("notebook", [replace(chunks[0], chunk_id="renamed")])
    assert encoder.calls.count(("laptop deadline",)) == 1
    retrieve_top_k("notebook", [replace(chunks[0], text="irrelevant")])
    assert ("irrelevant",) in encoder.calls
    monkeypatch.setattr(config, "EMBEDDING_REVISION", "another-revision")
    retrieve_top_k("notebook", chunks)
    assert encoder.calls.count(("laptop deadline",)) == 2


def test_filter_change_rebuilds_eligible_index(encoder, monkeypatch):
    chunks = [chunk("old", "laptop deadline", "superseded"), chunk("new", "partial")]
    retrieve_top_k("notebook", chunks)
    monkeypatch.setattr(config, "CURRENT_ONLY", False)
    retrieve_top_k("notebook", chunks)
    assert encoder.calls[0] == ("partial",)
    assert ("laptop deadline", "partial") in encoder.calls


@pytest.mark.parametrize("query,chunks", [("notebook", []), (" ", [chunk("a", "partial")]),
                                         ("notebook", [chunk("old", "partial", "superseded")])])
def test_empty_inputs_do_not_load_model(encoder, query, chunks):
    assert retrieve_top_k(query, chunks) == []
    assert encoder.calls == []


def test_model_loaded_once_and_only_from_local_cache(monkeypatch):
    embeddings.clear_cache()
    calls = []
    fake = Encoder()

    def load(*args, **kwargs):
        calls.append((args, kwargs))
        return fake

    monkeypatch.setattr(embeddings, "load_model", load)
    monkeypatch.setattr(config, "RETRIEVAL_BACKEND", "embeddings", raising=False)
    retrieve_top_k("notebook", [chunk("a", "partial")])
    retrieve_top_k("notebook", [chunk("b", "laptop deadline")])
    assert len(calls) == 1
    assert calls[0][1] == {"local_files_only": True}
    embeddings.clear_cache()


def test_lexical_backend_never_imports_optional_dependencies(monkeypatch):
    monkeypatch.setattr(config, "RETRIEVAL_BACKEND", "lexical", raising=False)
    original = builtins.__import__

    def guarded(name, *args, **kwargs):
        if name.startswith(("sentence_transformers", "torch", "numpy")):
            raise AssertionError("Lexical retrieval imported optional dependencies")
        return original(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded)
    assert retrieve_top_k("laptop", [chunk("a", "laptop deadline")])[0].score == 0.5


def test_model_failure_is_actionable_and_does_not_fallback(encoder, monkeypatch):
    def unavailable(*args, **kwargs):
        raise OSError("missing cached model")

    monkeypatch.setattr(embeddings, "load_model", unavailable)
    with pytest.raises(RuntimeError, match="prepare_embeddings"):
        retrieve_top_k("notebook", [chunk("a", "laptop deadline")])


def test_unknown_backend_and_invalid_k_are_rejected(monkeypatch):
    monkeypatch.setattr(config, "RETRIEVAL_BACKEND", "typo", raising=False)
    with pytest.raises(ValueError, match="RETRIEVAL_BACKEND"):
        retrieve_top_k("q", [])
    with pytest.raises(ValueError, match="k must be"):
        retrieve_top_k("q", [], k=0)


def test_embedding_results_flow_to_existing_answer_and_refusal(encoder, monkeypatch):
    supported = build_grounded_answer("notebook", [chunk("a", "laptop deadline")])
    assert not supported.refused
    assert supported.citations == ["a"]
    assert "laptop deadline" in supported.answer
    monkeypatch.setattr(config, "EMBEDDING_REFUSAL_THRESHOLD", 0.6)
    refused = build_grounded_answer("notebook", [chunk("b", "partial")])
    assert refused.refused
    assert refused.citations == []


def test_model_identity_and_backend_are_recorded_in_snapshot(monkeypatch):
    monkeypatch.setattr(config, "RETRIEVAL_BACKEND", "embeddings", raising=False)
    snapshot = config.snapshot()
    assert snapshot["RETRIEVAL_BACKEND"] == "embeddings"
    for key in ["EMBEDDING_MODEL", "EMBEDDING_REVISION", "EMBEDDING_DEVICE", "EMBEDDING_CACHE_DIR"]:
        assert snapshot[key]


def test_model_constructor_pins_revision_and_offline_mode(monkeypatch):
    calls = []

    def constructor(model_id, **kwargs):
        calls.append((model_id, kwargs))
        return object()

    monkeypatch.setitem(sys.modules, "sentence_transformers",
                        SimpleNamespace(SentenceTransformer=constructor))
    embeddings.load_model("model", "revision", "cpu", "cache", local_files_only=True)
    assert calls == [("model", {"revision": "revision", "device": "cpu",
                               "cache_folder": "cache", "local_files_only": True,
                               "trust_remote_code": False})]


def test_missing_optional_dependency_has_install_instructions(monkeypatch):
    monkeypatch.setitem(sys.modules, "sentence_transformers", None)
    with pytest.raises(RuntimeError, match="requirements-embeddings.txt"):
        embeddings.load_model("model", "revision", "cpu", "cache", local_files_only=True)


def test_negative_cosine_is_not_mapped_to_positive_evidence(encoder, monkeypatch):
    monkeypatch.setattr(config, "RETRIEVAL_MIN_SCORE", -1.0)
    results = retrieve_top_k("notebook", [chunk("a", "opposite")])
    assert results[0].score == -1.0


def test_cli_backend_argument_overrides_environment_default(monkeypatch):
    from src.cli import parse_args

    monkeypatch.setattr(config, "RETRIEVAL_BACKEND", "lexical")
    monkeypatch.setattr(sys, "argv", ["cli", "--question", "notebook",
                                     "--retrieval-backend", "embeddings"])
    assert parse_args().retrieval_backend == "embeddings"
