import json
from pathlib import Path

import pytest

from src import config, generation, rag
from src.chunking import Chunk
from src.gemma_client import ProviderResponse
from src.generation_errors import GenerationError, InvalidResponseError, ProviderError
from src.retrieval import RetrievalResult


@pytest.fixture
def evidence():
    return [
        RetrievalResult(Chunk("guide-chunk-0", "guide", "Guide", "2026", "current",
                              "Equipment is replaced within 8 days."), 0.8),
        RetrievalResult(Chunk("leave-chunk-0", "leave", "Leave", "2026", "current",
                              "Annual leave is 20 days."), 0.4),
    ]


@pytest.fixture(autouse=True)
def settings(monkeypatch):
    monkeypatch.setattr(config, "ANSWER_BACKEND", "extractive")
    monkeypatch.delenv("GEMMA_TRACE_PATH", raising=False)


def decision(**overrides):
    value = {"answer": "Within 8 days. [guide-chunk-0]", "citations": ["guide-chunk-0"], "refused": False}
    value.update(overrides)
    return json.dumps(value)


def test_prompt_sends_all_text_metadata_in_retrieval_order(evidence):
    payload = generation.build_request("When is equipment replaced?", evidence)
    data = json.loads(payload["contents"][0]["parts"][0]["text"])
    assert data["question"] == "When is equipment replaced?"
    assert [c["chunk_id"] for c in data["evidence"]] == [r.chunk.chunk_id for r in evidence]
    assert data["evidence"][1] == {"chunk_id": "leave-chunk-0", "doc_id": "leave", "title": "Leave",
                                    "version": "2026", "status": "current", "text": "Annual leave is 20 days."}
    assert payload["generationConfig"]["thinkingConfig"] == {"thinkingLevel": "minimal"}
    assert "tools" not in payload
    assert "responseMimeType" not in payload["generationConfig"]


def test_valid_decision_deduplicates_citations(evidence):
    result = generation.parse_decision(decision(citations=["guide-chunk-0", "guide-chunk-0"]), evidence)
    assert result.citations == ["guide-chunk-0"]
    assert result.refused is False


@pytest.mark.parametrize("bad", [
    "not JSON", "```json\n{}\n```", "null", "[]", "{}",
    decision(answer=""), decision(answer=42), decision(refused="false"), decision(refused=0),
    decision(citations=[]), decision(citations="guide-chunk-0"), decision(citations=[42]),
    decision(citations=["invented"]), decision(answer="Claim [invented]."),
    decision(answer="Claim [leave-chunk-0]."), decision(unexpected=True),
    decision(refused=True), decision(answer="", refused=True),
    '{"answer":"a","answer":"b","citations":["guide-chunk-0"],"refused":false}',
])
def test_invalid_decisions_raise_instead_of_becoming_refusals(evidence, bad):
    with pytest.raises(InvalidResponseError):
        generation.parse_decision(bad, evidence)


def test_integration_keeps_retrieval_and_selects_only_support(monkeypatch, evidence):
    monkeypatch.setattr(config, "ANSWER_BACKEND", "gemma")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(rag, "retrieve_top_k", lambda *_: evidence)
    monkeypatch.setattr(generation.GemmaClient, "generate", lambda *a: ProviderResponse(decision(), {"totalTokenCount": 8}))
    result = rag.build_grounded_answer("equipment", [])
    assert result.retrieved is evidence
    assert result.citations == ["guide-chunk-0"]
    assert "Within 8 days" in result.answer


def test_valid_model_refusal_maps_to_existing_refusal(monkeypatch, evidence):
    monkeypatch.setattr(config, "ANSWER_BACKEND", "gemma")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(rag, "retrieve_top_k", lambda *_: evidence)
    monkeypatch.setattr(generation.GemmaClient, "generate", lambda *a: ProviderResponse(
        decision(answer="", citations=[], refused=True), {}))
    result = rag.build_grounded_answer("unsupported policy", [])
    assert result.answer == rag.REFUSAL_MESSAGE
    assert result.refused is True and result.citations == []
    assert result.retrieved is evidence


@pytest.mark.parametrize("backend", ["extractive", "gemma"])
def test_score_gate_and_empty_results_never_call_provider(monkeypatch, backend, evidence):
    monkeypatch.setattr(config, "ANSWER_BACKEND", backend)
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(generation.GemmaClient, "generate", lambda *a: pytest.fail("provider"))
    for results in [[], [RetrievalResult(evidence[0].chunk, 0.01)]]:
        monkeypatch.setattr(rag, "retrieve_top_k", lambda *_, results=results: results)
        assert rag.build_grounded_answer("equipment", []).refused


def test_offline_backend_needs_no_key_or_network(monkeypatch, evidence):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setattr(generation.GemmaClient, "generate", lambda *a: pytest.fail("provider"))
    monkeypatch.setattr(rag, "retrieve_top_k", lambda *_: evidence)
    result = rag.build_grounded_answer("equipment", [])
    assert result.citations == [r.chunk.chunk_id for r in evidence]


def test_trace_records_answers_local_refusals_and_errors_without_secrets(monkeypatch, evidence, tmp_path):
    path = tmp_path / "answers.jsonl"
    monkeypatch.setenv("GEMMA_TRACE_PATH", str(path))
    monkeypatch.setenv("GEMINI_API_KEY", "private-key")
    monkeypatch.setattr(rag, "retrieve_top_k", lambda *_: evidence)
    rag.build_grounded_answer("private-key equipment", [])
    monkeypatch.setattr(rag, "retrieve_top_k", lambda *_: [])
    rag.build_grounded_answer("missing", [])
    monkeypatch.setattr(config, "ANSWER_BACKEND", "gemma")
    monkeypatch.setattr(rag, "retrieve_top_k", lambda *_: evidence)
    def fail(*a):
        raise ProviderError("network error")
    monkeypatch.setattr(generation.GemmaClient, "generate", fail)
    with pytest.raises(ProviderError):
        rag.build_grounded_answer("equipment", [])
    raw = path.read_text()
    assert "private-key" not in raw
    rows = [json.loads(line) for line in raw.splitlines()]
    assert [r["status"] for r in rows] == ["complete", "local_refusal", "error"]
    assert rows[1]["refused"] is True
    assert rows[2]["refused"] is None
    assert rows[2]["error_type"] == "ProviderError"


def test_provider_failure_stops_fixed_eval_without_writing_result(monkeypatch, tmp_path):
    from src import eval_runner
    monkeypatch.setattr(config, "ANSWER_BACKEND", "gemma")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    def fail(*a):
        raise ProviderError("quota exhausted")
    monkeypatch.setattr(generation.GemmaClient, "generate", fail)
    output = tmp_path / "must-not-exist.json"
    monkeypatch.setattr("sys.argv", ["eval_runner", "--out", str(output)])
    with pytest.raises(ProviderError):
        eval_runner.main()
    assert not output.exists()


def test_cli_prints_clear_operational_error(monkeypatch, capsys):
    from src import cli
    monkeypatch.setattr("sys.argv", ["cli", "--question", "equipment"])
    def fail(*a):
        raise ProviderError("HTTP 429: quota exhausted")
    monkeypatch.setattr(cli, "build_grounded_answer", fail)
    with pytest.raises(SystemExit) as error:
        cli.main()
    assert error.value.code == 1
    assert "HTTP 429" in capsys.readouterr().err


def test_existing_trace_file_is_not_silently_mixed(monkeypatch, tmp_path):
    path = tmp_path / "old.jsonl"
    path.write_text("previous evidence\n")
    monkeypatch.setenv("GEMMA_TRACE_PATH", str(path))
    with pytest.raises(GenerationError):
        rag.build_grounded_answer("missing", [])
    assert path.read_text() == "previous evidence\n"
