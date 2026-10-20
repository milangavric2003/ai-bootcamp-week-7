"""Hybrid behavior contracts use controlled cosine scores, with no model downloads."""

import pytest

import sys

from src import cli, config, embeddings, rag
from src.chunking import Chunk, build_chunks
from src.corpus import load_corpus
from src.retrieval import RetrievalResult, retrieve_top_k


def chunk(chunk_id, text, status="current"):
    return Chunk(chunk_id, "doc", "Title", "2026", status, text)


@pytest.fixture
def hybrid_scores(monkeypatch):
    monkeypatch.setattr(config, "RETRIEVAL_BACKEND", "hybrid")
    monkeypatch.setattr(config, "CURRENT_ONLY", True)
    monkeypatch.setattr(config, "STOPWORDS_ENABLED", False)
    monkeypatch.setattr(config, "TOP_K", 2)
    monkeypatch.setattr(config, "RETRIEVAL_MIN_SCORE", 0.01)
    monkeypatch.setattr(config, "HYBRID_RRF_CONSTANT", 60, raising=False)

    def set_scores(scores):
        monkeypatch.setattr(embeddings, "score_chunks", lambda query, chunks: [
            scores.get(c.chunk_id, 0.0) for c in chunks
        ])

    return set_scores


def test_e09_selected_evidence_contains_location_and_deadline(hybrid_scores):
    hybrid_scores({"hb-01-chunk-1": 0.6766, "hb-01-chunk-0": 0.6628,
                   "hb-01-chunk-2": 0.6434})
    results = retrieve_top_k(
        "Where do I request a replacement laptop and how long does it take?",
        build_chunks(load_corpus()),
    )
    assert [r.chunk.chunk_id for r in results] == ["hb-01-chunk-1", "hb-01-chunk-2"]
    text = " ".join(r.chunk.text for r in results)
    assert all(fact in text for fact in ["IT portal", "Hardware", "5 business days"])


def test_e05_preserves_semantic_deadline_despite_misleading_word_overlap(hybrid_scores):
    hybrid_scores({"hb-01-chunk-1": 0.6322, "hb-01-chunk-0": 0.4767,
                   "hb-01-chunk-2": 0.4357, "hb-06-chunk-0": 0.42})
    results = retrieve_top_k("How long until I get a new notebook computer?",
                             build_chunks(load_corpus()))
    assert results[0].chunk.chunk_id == "hb-01-chunk-1"
    assert "5 business days" in results[0].chunk.text


@pytest.mark.parametrize("k", [1, 2, 10])
def test_semantic_anchor_survives_higher_rrf_candidate_without_duplication(hybrid_scores, k):
    hybrid_scores({"anchor": 0.9, "other": 0.8})
    results = retrieve_top_k("request", [chunk("anchor", "deadline"),
                                         chunk("other", "request")], k=k)
    ids = [r.chunk.chunk_id for r in results]
    assert ids == ["anchor", "other"][:k]
    assert results[0].score == pytest.approx(1 / 61)
    if k > 1:
        assert results[1].score > results[0].score


def test_component_only_membership_keeps_raw_semantic_confidence(hybrid_scores):
    hybrid_scores({"z-anchor": 0.8, "a-request": 0.005})
    results = retrieve_top_k("request", [chunk("z-anchor", "deadline"),
                                         chunk("a-request", "request")])
    assert [r.chunk.chunk_id for r in results] == ["z-anchor", "a-request"]
    assert [r.score for r in results] == pytest.approx([1 / 61, 1 / 61])
    assert [r.semantic_score for r in results] == [0.8, 0.005]


def test_raw_minimum_is_not_reapplied_to_fused_score(hybrid_scores, monkeypatch):
    hybrid_scores({"proof": 0.8})
    monkeypatch.setattr(config, "RETRIEVAL_MIN_SCORE", 0.5)
    results = retrieve_top_k("request", [chunk("proof", "request")])
    assert len(results) == 1
    assert results[0].score == pytest.approx(2 / 61)


def test_without_word_matches_semantic_order_is_preserved(hybrid_scores):
    hybrid_scores({"a": 0.6, "b": 0.8})
    results = retrieve_top_k("notebook", [chunk("a", "laptop"), chunk("b", "computer")])
    assert [r.chunk.chunk_id for r in results] == ["b", "a"]


def test_component_and_fused_ties_use_chunk_id(hybrid_scores):
    hybrid_scores({"a": 0.7, "z": 0.7})
    chunks = [chunk("z", "request"), chunk("a", "request")]
    assert [r.chunk.chunk_id for r in retrieve_top_k("request", chunks)] == ["a", "z"]
    assert [r.chunk.chunk_id for r in retrieve_top_k("request", chunks[::-1])] == ["a", "z"]


def test_superseded_sources_are_filtered_before_semantic_scoring(hybrid_scores, monkeypatch):
    seen = []

    def score(query, chunks):
        seen.extend(c.chunk_id for c in chunks)
        return [0.8] * len(chunks)

    monkeypatch.setattr(embeddings, "score_chunks", score)
    results = retrieve_top_k("request", [chunk("old", "request", "superseded"),
                                         chunk("current", "request")])
    assert seen == ["current"]
    assert [r.chunk.chunk_id for r in results] == ["current"]


@pytest.mark.parametrize("query,chunks", [
    ("request", []),
    (" ", [chunk("a", "request")]),
    ("request", [chunk("old", "request", "superseded")]),
])
def test_empty_hybrid_inputs_do_not_score(hybrid_scores, monkeypatch, query, chunks):
    def forbidden(*args):
        raise AssertionError("Empty input loaded the model")

    monkeypatch.setattr(embeddings, "score_chunks", forbidden)
    assert retrieve_top_k(query, chunks) == []


def test_hybrid_model_errors_do_not_silently_fallback(hybrid_scores, monkeypatch):
    def unavailable(*args):
        raise RuntimeError("Run python -m src.prepare_embeddings first")

    monkeypatch.setattr(embeddings, "score_chunks", unavailable)
    with pytest.raises(RuntimeError, match="prepare_embeddings"):
        retrieve_top_k("request", [chunk("a", "request")])


@pytest.mark.parametrize("constant", [0, -1])
def test_nonpositive_rrf_constant_is_rejected(hybrid_scores, monkeypatch, constant):
    hybrid_scores({"a": 0.8})
    monkeypatch.setattr(config, "HYBRID_RRF_CONSTANT", constant)
    with pytest.raises(ValueError, match="HYBRID_RRF_CONSTANT"):
        retrieve_top_k("request", [chunk("a", "request")])


@pytest.mark.parametrize("cosine", [0.5099, 0.51, 0.5101])
def test_hybrid_refusal_uses_semantic_threshold_not_fused_rank(hybrid_scores, monkeypatch, cosine):
    hybrid_scores({"proof": cosine})
    monkeypatch.setattr(config, "EMBEDDING_REFUSAL_THRESHOLD", 0.51)
    monkeypatch.setattr(config, "REFUSAL_THRESHOLD", 0.99)
    result = rag.build_grounded_answer("request", [chunk("proof", "request")])
    assert result.refused is (cosine < 0.51)
    assert result.citations == ([] if cosine < 0.51 else ["proof"])
    assert result.retrieved[0].score < 0.1


def test_e09_actual_answer_contains_both_required_facts(hybrid_scores):
    hybrid_scores({"hb-01-chunk-1": 0.6766, "hb-01-chunk-0": 0.6628,
                   "hb-01-chunk-2": 0.6434})
    result = rag.build_grounded_answer(
        "Where do I request a replacement laptop and how long does it take?",
        build_chunks(load_corpus()),
    )
    assert not result.refused
    assert result.citations == ["hb-01-chunk-1", "hb-01-chunk-2"]
    assert all(fact in result.answer for fact in ["IT portal", "Hardware", "5 business days"])


def test_confidence_can_come_from_any_selected_chunk(hybrid_scores, monkeypatch):
    weak, strong = chunk("weak", "Weak evidence."), chunk("strong", "Strong evidence.")
    selected = [RetrievalResult(weak, 0.03, 0.2), RetrievalResult(strong, 0.02, 0.8)]
    monkeypatch.setattr(rag, "retrieve_top_k", lambda *args: selected)
    result = rag.build_grounded_answer("question", [weak, strong])
    assert not result.refused
    assert result.citations == ["weak", "strong"]


def test_missing_semantic_confidence_fails_closed(hybrid_scores, monkeypatch):
    evidence = chunk("proof", "Evidence.")
    monkeypatch.setattr(rag, "retrieve_top_k", lambda *args: [RetrievalResult(evidence, 1.0)])
    result = rag.build_grounded_answer("question", [evidence])
    assert result.refused
    assert result.citations == []


def test_lexical_only_union_is_returned_but_does_not_authorize_answer(hybrid_scores):
    hybrid_scores({"weak": -0.2})
    result = rag.build_grounded_answer("request", [chunk("weak", "request")])
    assert [r.chunk.chunk_id for r in result.retrieved] == ["weak"]
    assert result.retrieved[0].semantic_score == -0.2
    assert result.refused and result.citations == []


def test_empty_hybrid_answer_is_refused(hybrid_scores):
    hybrid_scores({})
    result = rag.build_grounded_answer("request", [])
    assert result.refused and result.citations == [] and result.retrieved == []


def test_cli_accepts_explicit_hybrid_override(monkeypatch):
    monkeypatch.setattr(config, "RETRIEVAL_BACKEND", "lexical")
    monkeypatch.setattr(sys, "argv", ["cli", "--question", "request",
                                     "--retrieval-backend", "hybrid"])
    assert cli.parse_args().retrieval_backend == "hybrid"


def test_cli_labels_fused_and_semantic_scores(hybrid_scores, monkeypatch, capsys):
    hybrid_scores({"hb-01-chunk-1": 0.8})
    monkeypatch.setattr(sys, "argv", ["cli", "--question", "replacement laptop",
                                     "--retrieval-backend", "hybrid", "--show-retrieved"])
    cli.main()
    output = capsys.readouterr().out
    assert "RRF=" in output and "cosine=0.8000" in output
    assert "Refused: False" in output


def test_hybrid_configuration_is_recorded(hybrid_scores):
    snapshot = config.snapshot()
    assert snapshot["RETRIEVAL_BACKEND"] == "hybrid"
    assert snapshot["HYBRID_RRF_CONSTANT"] == 60
