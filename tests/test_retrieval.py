import pytest

from src import config
from src.chunking import Chunk
from src.retrieval import lexical_score, retrieve_top_k, searchable_chunks, tokenize


def make_chunk(chunk_id: str, text: str, status: str = "current") -> Chunk:
    return Chunk(chunk_id=chunk_id, doc_id="d", title="T", version="2026", status=status, text=text)


def test_retrieve_top_k_orders_by_score_desc() -> None:
    chunks = [
        make_chunk("a", "rag retrieval citations evidence"),
        make_chunk("b", "weather forecast rain tomorrow"),
    ]
    results = retrieve_top_k("rag citations", chunks, k=2)
    assert results
    assert results[0].chunk.chunk_id == "a"


def test_retrieve_top_k_returns_empty_for_unrelated_query() -> None:
    chunks = [make_chunk("a", "vector database retrieval")]
    assert retrieve_top_k("basketball playoffs", chunks, k=2) == []


def test_ties_are_broken_by_chunk_id() -> None:
    chunks = [make_chunk("b", "leave policy"), make_chunk("a", "leave policy")]
    results = retrieve_top_k("leave", chunks, k=2)
    assert [r.chunk.chunk_id for r in results] == ["a", "b"]


def test_current_filter_preserves_eligible_order_and_input(monkeypatch) -> None:
    monkeypatch.setattr(config, "CURRENT_ONLY", True)
    chunks = [
        make_chunk("z", "current rule"),
        make_chunk("old", "old rule", status="superseded"),
        make_chunk("a", "another rule", status="draft"),
    ]
    original = chunks.copy()

    eligible = searchable_chunks(chunks)

    assert eligible == [chunks[0], chunks[2]]
    assert chunks == original


def test_superseded_best_match_cannot_displace_current_evidence(monkeypatch) -> None:
    monkeypatch.setattr(config, "CURRENT_ONLY", True)
    chunks = [
        make_chunk("old", "remote work", status="superseded"),
        make_chunk("new", "remote work allows three days weekly"),
    ]

    results = retrieve_top_k("remote work", chunks, k=1)

    assert [item.chunk.chunk_id for item in results] == ["new"]
    assert results[0].score == pytest.approx(2 / 6)


def test_disabled_filter_keeps_superseded_best_match(monkeypatch) -> None:
    monkeypatch.setattr(config, "CURRENT_ONLY", False)
    chunks = [
        make_chunk("new", "remote work allows three days weekly"),
        make_chunk("old", "remote work", status="superseded"),
    ]

    assert searchable_chunks(chunks) == chunks
    results = retrieve_top_k("remote work", chunks, k=1)
    assert [item.chunk.chunk_id for item in results] == ["old"]
    assert results[0].score == 1.0


@pytest.mark.parametrize("statuses", [[], ["superseded"]])
def test_no_eligible_chunks_returns_empty_results(monkeypatch, statuses) -> None:
    monkeypatch.setattr(config, "CURRENT_ONLY", True)
    chunks = [make_chunk(str(i), "remote work", status) for i, status in enumerate(statuses)]

    assert searchable_chunks(chunks) == []
    assert retrieve_top_k("remote work", chunks, k=2) == []


def test_disabled_stopwords_preserve_original_token_stream(monkeypatch) -> None:
    monkeypatch.setattr(config, "STOPWORDS_ENABLED", False)

    assert tokenize("The IT policy is in HR portal, 2026.") == [
        "the", "it", "policy", "is", "in", "hr", "portal", "2026",
    ]


def test_enabled_stopwords_preserve_content_order_repetition_and_qualifiers(monkeypatch) -> None:
    monkeypatch.setattr(config, "STOPWORDS_ENABLED", True)

    assert tokenize("THE Policy policy is NOT valid until 31 March; no, never without a badge.") == [
        "policy", "policy", "not", "valid", "until", "31", "march", "no", "never", "without", "badge",
    ]


def test_stopwords_score_uses_filtered_content_on_both_sides(monkeypatch) -> None:
    monkeypatch.setattr(config, "STOPWORDS_ENABLED", True)

    assert lexical_score("What is the equipment policy?", "The equipment policy is clear.") == pytest.approx(2 / 3)


@pytest.mark.parametrize("query,text", [
    ("", "equipment"),
    ("the and", "equipment"),
    ("equipment", "the and"),
    ("???", "equipment"),
    ("equipment", "..."),
])
def test_empty_filtered_inputs_score_zero_and_retrieve_nothing(monkeypatch, query, text) -> None:
    monkeypatch.setattr(config, "STOPWORDS_ENABLED", True)

    assert lexical_score(query, text) == 0.0
    assert retrieve_top_k(query, [make_chunk("a", text)]) == []


def test_stopword_only_overlap_cannot_retrieve_unrelated_content(monkeypatch) -> None:
    chunks = [make_chunk("a", "The weather is cold.")]
    monkeypatch.setattr(config, "STOPWORDS_ENABLED", False)
    assert retrieve_top_k("What is the equipment?", chunks)

    monkeypatch.setattr(config, "STOPWORDS_ENABLED", True)
    assert retrieve_top_k("What is the equipment?", chunks) == []
