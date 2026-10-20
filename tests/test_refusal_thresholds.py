import pytest

from src import config, rag
from src.chunking import Chunk
from src.retrieval import RetrievalResult


@pytest.mark.parametrize("backend,threshold", [("lexical", 0.10), ("embeddings", 0.50)])
@pytest.mark.parametrize("score", [0.0999, 0.10, 0.1001, 0.4999, 0.50, 0.5001])
def test_backend_threshold_boundaries(monkeypatch, backend, threshold, score):
    monkeypatch.setattr(config, "RETRIEVAL_BACKEND", backend)
    monkeypatch.setattr(config, "REFUSAL_THRESHOLD", 0.10)
    monkeypatch.setattr(config, "EMBEDDING_REFUSAL_THRESHOLD", 0.50, raising=False)
    chunk = Chunk("proof", "doc", "Title", "2026", "current", "Evidence text.")
    monkeypatch.setattr(rag, "retrieve_top_k", lambda *args: [RetrievalResult(chunk, score)])
    result = rag.build_grounded_answer("Question", [chunk])
    assert result.refused is (score < threshold)
    assert result.citations == ([] if score < threshold else ["proof"])
    assert result.retrieved[0].score == score


@pytest.mark.parametrize("backend", ["lexical", "embeddings"])
def test_missing_results_refused_for_each_backend(monkeypatch, backend):
    monkeypatch.setattr(config, "RETRIEVAL_BACKEND", backend)
    monkeypatch.setattr(rag, "retrieve_top_k", lambda *args: [])
    result = rag.build_grounded_answer("Question", [])
    assert result.refused and result.citations == []


@pytest.mark.parametrize("backend,inactive", [("lexical", "EMBEDDING_REFUSAL_THRESHOLD"),
                                              ("embeddings", "REFUSAL_THRESHOLD")])
def test_changing_other_backend_threshold_has_no_effect(monkeypatch, backend, inactive):
    monkeypatch.setattr(config, "RETRIEVAL_BACKEND", backend)
    monkeypatch.setattr(config, "REFUSAL_THRESHOLD", 0.10)
    monkeypatch.setattr(config, "EMBEDDING_REFUSAL_THRESHOLD", 0.50, raising=False)
    chunk = Chunk("proof", "doc", "Title", "2026", "current", "Evidence text.")
    monkeypatch.setattr(rag, "retrieve_top_k", lambda *args: [RetrievalResult(chunk, 0.6)])
    assert not rag.build_grounded_answer("Question", [chunk]).refused
    monkeypatch.setattr(config, inactive, 0.99)
    assert not rag.build_grounded_answer("Question", [chunk]).refused
