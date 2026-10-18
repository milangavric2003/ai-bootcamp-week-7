import pytest

from src import config
from src.chunking import build_chunks, split_text, split_text_by_sentences, split_text_with_overlap
from src.corpus import load_corpus


def test_split_text_with_overlap_returns_multiple_chunks() -> None:
    text = "abcdefghijklmnopqrstuvwxyz" * 4
    chunks = split_text_with_overlap(text, chunk_size=30, overlap=10)
    assert len(chunks) >= 3


def test_split_text_with_overlap_rejects_invalid_overlap() -> None:
    with pytest.raises(ValueError):
        split_text_with_overlap("abc", chunk_size=10, overlap=10)


def test_build_chunks_uses_stable_ids_and_keeps_metadata() -> None:
    chunks = build_chunks(load_corpus())
    ids = [chunk.chunk_id for chunk in chunks]
    assert len(ids) == len(set(ids))
    first = chunks[0]
    assert first.chunk_id == f"{first.doc_id}-chunk-0"
    assert first.version and first.status in {"current", "superseded"}


@pytest.mark.parametrize(
    ("text", "size", "expected"),
    [
        ("", 10, []),
        (" \n\t ", 10, []),
        (" One.\n Two!\t Three?  Tail ", 11, ["One. Two!", "Three? Tail"]),
        ("One. Two.", 9, ["One. Two."]),
        ("One. Two.", 8, ["One.", "Two."]),
        ("No final punctuation", 30, ["No final punctuation"]),
        ("No final punctuation", 5, ["No final punctuation"]),
        ("Hi. A much longer sentence. End.", 8, ["Hi.", "A much longer sentence.", "End."]),
        ("123456789. End.", 10, ["123456789.", "End."]),
        ("One.Two!Three?", 4, ["One.Two!Three?"]),
    ],
)
def test_sentence_chunking_contract(text: str, size: int, expected: list[str]) -> None:
    chunks = split_text_by_sentences(text, chunk_size=size)
    assert chunks == expected
    assert " ".join(chunks) == " ".join(text.split())


@pytest.mark.parametrize("size", [0, -1])
@pytest.mark.parametrize("text", ["", "Some text."])
def test_sentence_chunking_rejects_nonpositive_size(text: str, size: int) -> None:
    with pytest.raises(ValueError, match="chunk_size must be > 0"):
        split_text_by_sentences(text, chunk_size=size)


def test_sentence_strategy_dispatch_and_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(config, "CHUNK_STRATEGY", "sentences")
    monkeypatch.setattr(config, "CHUNK_SIZE", 10)
    documents = load_corpus()
    chunks = build_chunks(documents)
    assert chunks == build_chunks(documents)
    for document in documents:
        parts = [chunk for chunk in chunks if chunk.doc_id == document.doc_id]
        assert [chunk.text for chunk in parts] == split_text(document.text)
        assert " ".join(chunk.text for chunk in parts) == " ".join(document.text.split())
        for index, chunk in enumerate(parts):
            assert chunk.chunk_id == f"{document.doc_id}-chunk-{index}"
            assert (chunk.title, chunk.version, chunk.status) == (
                document.title, document.version, document.status
            )


def test_equipment_deadline_sentence_stays_whole(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(config, "CHUNK_STRATEGY", "sentences")
    monkeypatch.setattr(config, "CHUNK_SIZE", 140)
    equipment = load_corpus()[0]
    deadline_sentence = equipment.text.split(". ")[1] + "."
    assert len(deadline_sentence) > config.CHUNK_SIZE
    assert deadline_sentence in [chunk.text for chunk in build_chunks([equipment])]


def test_chars_strategy_keeps_existing_overlap(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(config, "CHUNK_STRATEGY", "chars")
    monkeypatch.setattr(config, "CHUNK_SIZE", 6)
    monkeypatch.setattr(config, "CHUNK_OVERLAP", 2)
    assert split_text("abcdefghijkl") == ["abcdef", "efghij", "ijkl"]
