import pytest

from src import config
from src.chunking import Chunk, build_chunks
from src.corpus import load_corpus
from src.rag import REFUSAL_MESSAGE, build_grounded_answer


def test_supported_question_returns_citations() -> None:
    result = build_grounded_answer("How often do passwords need to be changed?", build_chunks(load_corpus()))
    assert result.refused is False
    assert result.citations


def test_question_without_matching_words_is_refused() -> None:
    result = build_grounded_answer("Zebra xylophone quantum?", build_chunks(load_corpus()))
    assert result.refused is True
    assert result.citations == []
    assert result.answer == REFUSAL_MESSAGE


@pytest.mark.parametrize("current_only", [False, True])
def test_remote_policy_citations_follow_current_filter(monkeypatch, current_only) -> None:
    monkeypatch.setattr(config, "CURRENT_ONLY", current_only)
    chunks = build_chunks(load_corpus())
    chunks_by_id = {chunk.chunk_id: chunk for chunk in chunks}

    result = build_grounded_answer("How many days per week can I work remotely?", chunks)

    assert result.refused is False
    assert "3 days per week" in result.answer
    assert result.citations
    assert all(chunk_id in chunks_by_id for chunk_id in result.citations)
    has_superseded_citation = any(
        chunks_by_id[chunk_id].status == "superseded" for chunk_id in result.citations
    )
    assert has_superseded_citation is (not current_only)
    if current_only:
        assert all(item.chunk.status != "superseded" for item in result.retrieved)
        assert "2 days per week" not in result.answer


def test_only_superseded_evidence_is_refused_when_filtered(monkeypatch) -> None:
    monkeypatch.setattr(config, "CURRENT_ONLY", True)
    chunks = [Chunk(chunk_id="old", doc_id="policy", title="Policy", version="2024",
                    status="superseded", text="Remote work permits two days weekly.")]

    result = build_grounded_answer("remote work", chunks)

    assert result.refused is True
    assert result.retrieved == []
    assert result.citations == []
    assert result.answer == REFUSAL_MESSAGE


def test_all_stopword_question_is_refused_without_citations(monkeypatch) -> None:
    monkeypatch.setattr(config, "STOPWORDS_ENABLED", True)

    result = build_grounded_answer("What is it?", build_chunks(load_corpus()))

    assert result.refused is True
    assert result.retrieved == []
    assert result.citations == []
    assert result.answer == REFUSAL_MESSAGE
