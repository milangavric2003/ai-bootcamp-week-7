import copy
import io
import json
import ssl
from urllib.error import HTTPError, URLError

import pytest

from src import config, gemma_client
from src.gemma_client import GemmaClient
from src.generation_errors import ConfigurationError, InvalidResponseError, ProviderError


PRIMARY = "gemma-4-26b-a4b-it"
FALLBACK = "gemini-3.5-flash-lite"


@pytest.fixture(autouse=True)
def retry_settings(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "private-test-key")
    monkeypatch.setattr(config, "GEMMA_FALLBACK_MODEL", FALLBACK, raising=False)
    monkeypatch.setattr(config, "GEMMA_PRIMARY_ATTEMPTS", 2, raising=False)
    monkeypatch.setattr(config, "GEMMA_FALLBACK_ATTEMPTS", 2, raising=False)
    monkeypatch.setattr(config, "GEMMA_RETRY_BACKOFF_SECONDS", 0.25, raising=False)


def good_response():
    return {"candidates": [{"finishReason": "STOP", "content": {"parts": [{
        "text": '{"answer":"Supported.","citations":["source"],"refused":false}'
    }]}}], "usageMetadata": {"totalTokenCount": 12}}


def sequence(monkeypatch, outcomes):
    calls, delays = [], []
    outcomes = iter(outcomes)
    def opened(request, timeout):
        model = request.full_url.split("/models/")[1].split(":")[0]
        calls.append({"model": model, "timeout": timeout, "payload": json.loads(request.data)})
        outcome = next(outcomes)
        if isinstance(outcome, Exception):
            raise outcome
        return io.BytesIO(json.dumps(outcome).encode())
    monkeypatch.setattr(gemma_client, "_open", opened)
    monkeypatch.setattr(gemma_client, "sleep", delays.append, raising=False)
    return calls, delays


@pytest.mark.parametrize("successful_attempt", [1, 2, 3, 4])
def test_success_stops_at_the_right_attempt_with_unchanged_timeout(monkeypatch, successful_attempt):
    outcomes = [TimeoutError("private-test-key")] * (successful_attempt - 1) + [good_response()]
    calls, delays = sequence(monkeypatch, outcomes)
    result = GemmaClient().generate({"contents": []})
    expected = [PRIMARY, PRIMARY, FALLBACK, FALLBACK][:successful_attempt]
    assert [call["model"] for call in calls] == expected
    assert all(call["timeout"] == 30 for call in calls)
    assert result.model == expected[-1]
    assert [attempt["model"] for attempt in result.attempts] == expected
    assert [attempt["attempt"] for attempt in result.attempts] == list(range(1, successful_attempt + 1))
    assert result.attempts[-1]["status"] == "success"
    assert delays == [0.25, 0.5, 1.0][:successful_attempt - 1]


def test_four_network_failures_exhaust_both_models_without_leaking_errors(monkeypatch):
    calls, delays = sequence(monkeypatch, [URLError("private-test-key")] * 4)
    with pytest.raises(ProviderError, match="4 attempts") as error:
        GemmaClient().generate({})
    assert [call["model"] for call in calls] == [PRIMARY, PRIMARY, FALLBACK, FALLBACK]
    assert len(error.value.attempts) == 4
    assert error.value.model == FALLBACK
    assert "private-test-key" not in str(error.value)
    assert "private-test-key" not in json.dumps(error.value.attempts)
    assert delays == [0.25, 0.5, 1.0]


@pytest.mark.parametrize("code", [408, 429, 500, 502, 503, 504])
def test_transient_http_failure_can_recover_on_same_model(monkeypatch, code):
    failure = HTTPError("https://example.invalid/?key=private-test-key", code,
                        "private-test-key", {}, io.BytesIO(b"private body"))
    calls, _ = sequence(monkeypatch, [failure, good_response()])
    result = GemmaClient().generate({})
    assert [c["model"] for c in calls] == [PRIMARY, PRIMARY]
    assert result.model == PRIMARY
    assert str(code) in result.attempts[0]["error"]


@pytest.mark.parametrize("code", [301, 400, 401, 403, 404, 422])
def test_permanent_http_error_does_not_retry_or_fallback(monkeypatch, code):
    failure = HTTPError("https://example.invalid/?key=private-test-key", code,
                        "private-test-key", {}, io.BytesIO(b"private body"))
    calls, delays = sequence(monkeypatch, [failure])
    with pytest.raises(ProviderError) as error:
        GemmaClient().generate({})
    assert len(calls) == 1 and delays == []
    assert error.value.model == PRIMARY
    assert len(error.value.attempts) == 1
    assert "private-test-key" not in str(error.value)


def test_fallback_authentication_failure_stops_without_second_fallback(monkeypatch):
    failure = HTTPError("https://example.invalid/", 403, "forbidden", {}, io.BytesIO())
    calls, delays = sequence(monkeypatch, [TimeoutError(), TimeoutError(), failure])
    with pytest.raises(ProviderError) as error:
        GemmaClient().generate({})
    assert [c["model"] for c in calls] == [PRIMARY, PRIMARY, FALLBACK]
    assert error.value.model == FALLBACK and len(error.value.attempts) == 3
    assert delays == [0.25, 0.5]


@pytest.mark.parametrize("wrapped", [False, True])
def test_certificate_failure_is_clear_and_not_retried(monkeypatch, wrapped):
    certificate_error = ssl.SSLCertVerificationError("private-test-key")
    failure = URLError(certificate_error) if wrapped else certificate_error
    calls, delays = sequence(monkeypatch, [failure])
    with pytest.raises(ProviderError, match="certificate") as error:
        GemmaClient().generate({})
    assert len(calls) == 1 and delays == []
    assert "private-test-key" not in str(error.value)


def test_invalid_output_is_not_retried(monkeypatch):
    calls, delays = sequence(monkeypatch, [{"candidates": []}])
    with pytest.raises(InvalidResponseError) as error:
        GemmaClient().generate({})
    assert len(calls) == 1 and delays == []
    assert error.value.model == PRIMARY and len(error.value.attempts) == 1


def test_fallback_preserves_context_prompt_and_caller_payload(monkeypatch):
    payload = {"contents": [{"parts": [{"text": "all chunks and the original question"}]}],
               "systemInstruction": {"parts": [{"text": "fixed policy"}]},
               "generationConfig": {"candidateCount": 1, "temperature": 0,
                                    "thinkingConfig": {"thinkingLevel": "minimal"}}}
    original = copy.deepcopy(payload)
    calls, _ = sequence(monkeypatch, [TimeoutError(), TimeoutError(), good_response()])
    GemmaClient().generate(payload)
    assert payload == original
    assert calls[0]["payload"] == calls[1]["payload"] == original
    expected = copy.deepcopy(original)
    expected["generationConfig"].pop("candidateCount")
    assert calls[2]["payload"] == expected


def test_empty_fallback_model_disables_fallback(monkeypatch):
    monkeypatch.setattr(config, "GEMMA_FALLBACK_MODEL", "")
    calls, _ = sequence(monkeypatch, [TimeoutError(), TimeoutError()])
    with pytest.raises(ProviderError, match="2 attempts"):
        GemmaClient().generate({})
    assert [c["model"] for c in calls] == [PRIMARY, PRIMARY]


def test_invalid_fallback_model_fails_before_primary_request(monkeypatch):
    monkeypatch.setattr(config, "GEMMA_FALLBACK_MODEL", "https://invalid/?key=private-test-key")
    monkeypatch.setattr(gemma_client, "_open", lambda *a, **k: pytest.fail("network"))
    with pytest.raises(ConfigurationError) as error:
        GemmaClient().generate({})
    assert "private-test-key" not in str(error.value)
