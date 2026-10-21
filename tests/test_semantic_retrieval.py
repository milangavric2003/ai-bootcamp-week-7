"""Semantic contracts use controlled encoders; no model import or download."""

import builtins
import json
import math
import sys
from types import SimpleNamespace

import pytest

from src import config, generation, rag, retrieval, semantic_retrieval as semantic
from src.chunking import Chunk
from src.gemma_client import ProviderResponse
from src.retrieval_errors import RetrievalError


def chunk(identifier, text, status="current"):
    return Chunk(identifier, identifier.split("-")[0], "Guide", "2026", status, text)


class FakeEncoder:
    def __init__(self, vectors):
        self.vectors = vectors
        self.calls = []

    def encode(self, texts, **kwargs):
        self.calls.append((tuple(texts), kwargs))
        return [self.vectors[text] for text in texts]


@pytest.fixture(autouse=True)
def isolated_semantic_cache():
    semantic.clear_caches()
    yield
    semantic.clear_caches()


@pytest.fixture
def encoder(monkeypatch):
    fake = FakeEncoder({"question": (2, 0), "answer": (4, 0),
                        "related": (1, 1), "opposite": (-3, 0)})
    monkeypatch.setattr(semantic, "_create_encoder", lambda identity: fake)
    return fake


def test_cosine_uses_original_text_and_normalized_vectors(encoder, monkeypatch):
    monkeypatch.setattr(config, "STOPWORDS_ENABLED", True)
    scores = semantic.semantic_scores("question", [chunk("a", "answer"), chunk("b", "related"), chunk("c", "opposite")])
    assert scores == pytest.approx([1, 1 / math.sqrt(2), -1])
    assert encoder.calls[0][0] == ("answer", "related", "opposite")
    assert encoder.calls[1][0] == ("question",)
    assert all(call[1]["normalize_embeddings"] is True for call in encoder.calls)


def test_stopword_setting_does_not_rewrite_semantic_input(monkeypatch):
    fake = FakeEncoder({"What is the policy?": (1, 0), "The policy is current.": (1, 0)})
    monkeypatch.setattr(semantic, "_create_encoder", lambda identity: fake)
    evidence = [chunk("a", "The policy is current.")]
    for enabled in (False, True):
        monkeypatch.setattr(config, "STOPWORDS_ENABLED", enabled)
        assert semantic.semantic_scores("What is the policy?", evidence) == [1]
    assert fake.calls[0][0] == ("The policy is current.",)
    assert [call[0] for call in fake.calls[1:]] == [("What is the policy?",)] * 2


def test_unchanged_corpus_is_encoded_once_and_new_text_invalidates(encoder):
    semantic.semantic_scores("question", [chunk("a", "answer")])
    semantic.semantic_scores("related", [chunk("new-id", "answer")])
    semantic.semantic_scores("question", [chunk("a", "related")])
    corpus_calls = [texts for texts, _ in encoder.calls if texts in [("answer",), ("related",)]]
    assert corpus_calls.count(("answer",)) == 1
    # related is both a question in the second call and a changed corpus in the third.
    assert corpus_calls.count(("related",)) == 2


def test_model_identity_change_reloads_encoder_and_corpus(monkeypatch):
    loaded = []
    def create(identity):
        loaded.append(identity)
        return FakeEncoder({"question": (1, 0), "answer": (1, 0)})
    monkeypatch.setattr(semantic, "_create_encoder", create)
    evidence = [chunk("a", "answer")]
    semantic.semantic_scores("question", evidence)
    monkeypatch.setattr(config, "EMBEDDING_REVISION", "a" * 40)
    semantic.semantic_scores("question", evidence)
    assert len(loaded) == 2
    assert loaded[0] != loaded[1]


def test_semantic_ranking_filters_before_encoding_and_keeps_original_chunks(encoder, monkeypatch):
    monkeypatch.setattr(config, "RETRIEVAL_BACKEND", "embeddings")
    monkeypatch.setattr(config, "CURRENT_ONLY", True)
    first, tied = chunk("a", "answer"), chunk("b", "answer")
    old = chunk("old", "not in encoder", "superseded")
    result = retrieval.retrieve_top_k("question", [tied, old, first, chunk("c", "opposite")], k=2)
    assert [r.chunk.chunk_id for r in result] == ["a", "b"]
    assert result[0].chunk is first and result[1].chunk is tied
    assert result[0].score == 1
    assert "not in encoder" not in encoder.calls[0][0]


def test_metadata_changes_cannot_return_stale_citation_objects(encoder, monkeypatch):
    monkeypatch.setattr(config, "RETRIEVAL_BACKEND", "embeddings")
    original = chunk("old-id", "answer")
    retrieval.retrieve_top_k("question", [original])
    replacement = Chunk("fresh-id", "fresh-doc", "Updated", "2027", "draft", "answer")
    result = retrieval.retrieve_top_k("question", [replacement])
    assert result[0].chunk is replacement
    assert result[0].chunk.doc_id == "fresh-doc"


def test_chunk_reordering_does_not_mix_vectors(encoder, monkeypatch):
    monkeypatch.setattr(config, "RETRIEVAL_BACKEND", "embeddings")
    a, b = chunk("a", "answer"), chunk("b", "related")
    first = retrieval.retrieve_top_k("question", [a, b])
    second = retrieval.retrieve_top_k("question", [b, a])
    assert first == second


def test_semantic_minimum_and_explicit_k_apply(encoder, monkeypatch):
    monkeypatch.setattr(config, "RETRIEVAL_BACKEND", "embeddings")
    monkeypatch.setattr(config, "RETRIEVAL_MIN_SCORE", 0.8)
    assert [r.chunk.chunk_id for r in retrieval.retrieve_top_k("question", [chunk("b", "related"), chunk("a", "answer")], k=3)] == ["a"]
    monkeypatch.setattr(config, "RETRIEVAL_MIN_SCORE", -1.0)
    assert len(retrieval.retrieve_top_k("question", [chunk("a", "answer"), chunk("b", "opposite")], k=1)) == 1


@pytest.mark.parametrize("query,chunks", [("", [chunk("a", "answer")]), (" \t", [chunk("a", "answer")]),
    ("???", [chunk("a", "answer")]), ("question", []), ("question", [chunk("a", "answer", "superseded")])])
def test_empty_inputs_do_not_load_a_model(monkeypatch, query, chunks):
    monkeypatch.setattr(config, "RETRIEVAL_BACKEND", "embeddings")
    monkeypatch.setattr(semantic, "_create_encoder", lambda *_: pytest.fail("must not load"))
    assert retrieval.retrieve_top_k(query, chunks) == []


@pytest.mark.parametrize("k", [0, -1])
def test_invalid_k_is_rejected_before_model_load(monkeypatch, k):
    monkeypatch.setattr(config, "RETRIEVAL_BACKEND", "embeddings")
    with pytest.raises(ValueError, match="k must be > 0"):
        retrieval.retrieve_top_k("question", [], k=k)


def test_unknown_backend_does_not_silently_use_lexical(monkeypatch):
    monkeypatch.setattr(config, "RETRIEVAL_BACKEND", "typo")
    with pytest.raises(RetrievalError, match="backend"):
        retrieval.retrieve_top_k("question", [])


def test_lexical_mode_never_loads_encoder(monkeypatch):
    monkeypatch.setattr(config, "RETRIEVAL_BACKEND", "lexical")
    monkeypatch.setattr(semantic, "_create_encoder", lambda *_: pytest.fail("must not load"))
    assert retrieval.retrieve_top_k("policy", [chunk("a", "policy guidance")])[0].score == 0.5


@pytest.mark.parametrize("vectors", [
    {"answer": (0, 0), "question": (1, 0)},
    {"answer": (float("nan"), 0), "question": (1, 0)},
    {"answer": (float("inf"), 0), "question": (1, 0)},
    {"answer": (), "question": (1, 0)},
    {"answer": (1, 0), "question": (1, 0, 0)},
    {"answer": (1, 0), "question": (0, 0)},
    {"answer": ("invalid", 0), "question": (1, 0)},
])
def test_invalid_vectors_fail_explicitly(monkeypatch, vectors):
    monkeypatch.setattr(semantic, "_create_encoder", lambda identity: FakeEncoder(vectors))
    with pytest.raises(RetrievalError, match="vector"):
        semantic.semantic_scores("question", [chunk("a", "answer")])


def test_wrong_vector_count_and_ragged_corpus_are_errors(monkeypatch):
    fake = FakeEncoder({"a": (1, 0), "b": (1, 0, 0), "question": (1, 0)})
    monkeypatch.setattr(semantic, "_create_encoder", lambda identity: fake)
    with pytest.raises(RetrievalError, match="vector"):
        semantic.semantic_scores("question", [chunk("a", "a"), chunk("b", "b")])
    semantic.clear_caches()
    fake.encode = lambda *args, **kwargs: []
    with pytest.raises(RetrievalError, match="vector"):
        semantic.semantic_scores("question", [chunk("a", "a")])


def test_loader_is_local_pinned_cpu_and_remote_code_disabled(monkeypatch):
    captured = {}
    def factory(model, **kwargs):
        captured.update(model=model, **kwargs)
        return object()
    monkeypatch.setitem(sys.modules, "sentence_transformers", SimpleNamespace(SentenceTransformer=factory))
    semantic._create_encoder(semantic.model_identity())
    assert captured["revision"] == config.EMBEDDING_REVISION
    assert captured["local_files_only"] is True
    assert captured["trust_remote_code"] is False
    assert captured["device"] == "cpu"


def test_missing_dependency_and_cache_explain_setup(monkeypatch):
    original_import = builtins.__import__
    def missing(name, *args, **kwargs):
        if name == "sentence_transformers":
            raise ImportError("unavailable")
        return original_import(name, *args, **kwargs)
    with monkeypatch.context() as patch:
        patch.setattr(builtins, "__import__", missing)
        with pytest.raises(RetrievalError, match="requirements-embeddings.txt"):
            semantic._create_encoder(semantic.model_identity())
    def unavailable(*args, **kwargs):
        raise OSError("local files missing")
    monkeypatch.setitem(sys.modules, "sentence_transformers", SimpleNamespace(SentenceTransformer=unavailable))
    with pytest.raises(RetrievalError, match="prepare_embeddings"):
        semantic._create_encoder(semantic.model_identity())


def test_mutable_revision_is_not_accepted(monkeypatch):
    monkeypatch.setattr(config, "EMBEDDING_REVISION", "main")
    with pytest.raises(RetrievalError, match="revision"):
        semantic.model_identity()


def test_actual_semantic_results_reach_unchanged_gemma_request(monkeypatch):
    query, text = "Where is the notebook desk?", "The laptop desk is in Room Seven."
    fake = FakeEncoder({query: (1, 0), text: (1, 0)})
    monkeypatch.setattr(semantic, "_create_encoder", lambda identity: fake)
    monkeypatch.setattr(config, "RETRIEVAL_BACKEND", "embeddings")
    monkeypatch.setattr(config, "ANSWER_BACKEND", "gemma")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    source = chunk("desk-chunk-0", text)
    captured = {}
    def generate(self, payload):
        captured.update(json.loads(payload["contents"][0]["parts"][0]["text"]))
        return ProviderResponse(json.dumps({"answer": "Room Seven.", "citations": [source.chunk_id], "refused": False}), {})
    monkeypatch.setattr(generation.GemmaClient, "generate", generate)
    answer = rag.build_grounded_answer(query, [source])
    assert captured["question"] == query
    assert captured["evidence"][0]["text"] == text
    assert captured["evidence"][0]["chunk_id"] == source.chunk_id
    assert answer.citations == [source.chunk_id] and answer.refused is False


def test_low_cosine_still_uses_existing_local_refusal_gate(monkeypatch):
    monkeypatch.setattr(config, "RETRIEVAL_BACKEND", "embeddings")
    monkeypatch.setattr(config, "ANSWER_BACKEND", "gemma")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(semantic, "semantic_scores", lambda *args: [0.05])
    monkeypatch.setattr(generation.GemmaClient, "generate", lambda *args: pytest.fail("below refusal threshold"))
    assert rag.build_grounded_answer("question", [chunk("a", "answer")]).refused


def test_cli_backend_option_and_readable_setup_error(monkeypatch, capsys):
    from src import cli
    monkeypatch.setattr(sys, "argv", ["cli", "--retrieval-backend", "embeddings", "--question", "question"])
    def fail(*args):
        assert config.RETRIEVAL_BACKEND == "embeddings"
        raise RetrievalError("Run python -m src.prepare_embeddings")
    monkeypatch.setattr(cli, "build_grounded_answer", fail)
    with pytest.raises(SystemExit) as error:
        cli.main()
    assert error.value.code == 1
    assert "prepare_embeddings" in capsys.readouterr().err


def test_preparation_downloads_only_pinned_safe_model_files(monkeypatch, capsys):
    from src import prepare_embeddings
    captured = {}
    def snapshot(**kwargs):
        captured.update(kwargs)
        return "prepared-local-path"
    monkeypatch.setitem(sys.modules, "huggingface_hub", SimpleNamespace(snapshot_download=snapshot))
    assert prepare_embeddings.main() == 0
    assert captured["revision"] == config.EMBEDDING_REVISION
    assert "model.safetensors" in captured["allow_patterns"]
    assert not any(".bin" in item or "onnx" in item for item in captured["allow_patterns"])
    assert "Prepared" in capsys.readouterr().out
