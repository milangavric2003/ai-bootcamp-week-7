import io
import json
import math
from urllib.error import HTTPError, URLError

import pytest

from src import config
from src import gemma_client
from src.gemma_client import GemmaClient
from src.generation_errors import ConfigurationError, InvalidResponseError, ProviderError


@pytest.fixture(autouse=True)
def settings(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key-never-log")
    monkeypatch.setattr(config, "ANSWER_BACKEND", "gemma")


def response(text='{"answer":"ok","citations":["c1"],"refused":false}'):
    return {"candidates": [{"finishReason": "STOP", "content": {
        "parts": [{"text": text}]}}], "usageMetadata": {"totalTokenCount": 20}}


def serve(monkeypatch, value):
    raw = json.dumps(value).encode()
    monkeypatch.setattr(gemma_client, "_open", lambda *a, **k: io.BytesIO(raw))


def test_request_uses_private_header_and_exact_google_endpoint(monkeypatch):
    captured = []
    def opened(request, timeout):
        captured.append((request, timeout))
        return io.BytesIO(json.dumps(response()).encode())
    monkeypatch.setattr(gemma_client, "_open", opened)
    payload = {"contents": [{"parts": [{"text": "all evidence"}]}]}
    result = GemmaClient().generate(payload)
    request, timeout = captured[0]
    assert len(captured) == 1
    assert request.full_url == "https://generativelanguage.googleapis.com/v1beta/models/gemma-4-26b-a4b-it:generateContent"
    assert request.get_header("X-goog-api-key") == "test-key-never-log"
    assert "test-key" not in request.full_url
    assert json.loads(request.data) == payload
    assert timeout == 30
    assert result.usage == {"totalTokenCount": 20}


@pytest.mark.parametrize("key", ["AIza-synthetic_opaque-key", "AQ.synthetic_opaque.auth-key"])
def test_standard_and_authorization_keys_are_opaque_header_values(monkeypatch, key):
    monkeypatch.setenv("GEMINI_API_KEY", key)
    captured = []
    def opened(request, timeout):
        captured.append(request.get_header("X-goog-api-key"))
        return io.BytesIO(json.dumps(response()).encode())
    monkeypatch.setattr(gemma_client, "_open", opened)
    GemmaClient().generate({})
    assert captured == [key]


@pytest.mark.parametrize("key", ["", "key with spaces", "key\r\nInjected: value", "key\x01", "key\u00e9"])
def test_invalid_header_characters_are_rejected_before_network(monkeypatch, key):
    monkeypatch.setenv("GEMINI_API_KEY", key)
    monkeypatch.setattr(gemma_client, "_open", lambda *a, **k: pytest.fail("network"))
    with pytest.raises(ConfigurationError):
        GemmaClient().generate({})


@pytest.mark.parametrize("code", [301, 400, 401, 403, 404, 429, 500, 503])
def test_http_errors_are_sanitized_without_retries(monkeypatch, code):
    calls = []
    def fail(*a, **k):
        calls.append(1)
        raise HTTPError("https://example.invalid/?key=test-key-never-log", code,
                        "test-key-never-log", {}, io.BytesIO(b"private provider body"))
    monkeypatch.setattr(gemma_client, "_open", fail)
    with pytest.raises(ProviderError) as error:
        GemmaClient().generate({})
    assert str(code) in str(error.value)
    assert "test-key-never-log" not in str(error.value)
    assert "private provider body" not in str(error.value)
    assert error.value.__suppress_context__
    assert len(calls) == 1


@pytest.mark.parametrize("failure", [TimeoutError("test-key-never-log"),
                                     URLError("test-key-never-log"), OSError("test-key-never-log")])
def test_transport_errors_are_sanitized(monkeypatch, failure):
    def fail(*a, **k):
        raise failure
    monkeypatch.setattr(gemma_client, "_open", fail)
    with pytest.raises(ProviderError) as error:
        GemmaClient().generate({})
    assert "test-key-never-log" not in str(error.value)


@pytest.mark.parametrize("bad", [
    {}, [], {"candidates": []}, {"candidates": "bad"},
    {"promptFeedback": {"blockReason": "SAFETY"}},
    {"candidates": [{"finishReason": "MAX_TOKENS", "content": {"parts": [{"text": "{}"}]}}]},
    {"candidates": [{"finishReason": "STOP", "content": {"parts": [{"functionCall": {}}]}}]},
    {"candidates": [{"finishReason": "STOP", "content": {"parts": [{"thought": True, "text": "private"}]}}]},
    {"candidates": [{"finishReason": "STOP", "content": {"parts": "bad"}}]},
    {"candidates": [{"finishReason": "STOP", "content": {"parts": [{"text": ""}]}}]},
])
def test_incomplete_or_blocked_response_is_not_a_refusal(monkeypatch, bad):
    serve(monkeypatch, bad)
    with pytest.raises(InvalidResponseError):
        GemmaClient().generate({})


def test_text_parts_join_in_order_and_thinking_is_excluded(monkeypatch):
    value = response()
    value["candidates"][0]["content"]["parts"] = [
        {"thought": True, "text": "reasoning"}, {"text": "first"}, {"text": "second"}]
    value["usageMetadata"]["unexpected"] = "test-key-never-log"
    serve(monkeypatch, value)
    result = GemmaClient().generate({})
    assert result.text == "firstsecond"
    assert result.usage == {"totalTokenCount": 20}


@pytest.mark.parametrize("raw", [b"not JSON", b"\xff", b'"string"'])
def test_invalid_provider_json(monkeypatch, raw):
    monkeypatch.setattr(gemma_client, "_open", lambda *a, **k: io.BytesIO(raw))
    with pytest.raises(InvalidResponseError):
        GemmaClient().generate({})


@pytest.mark.parametrize("name,value", [
    ("GEMMA_TIMEOUT_SECONDS", 0), ("GEMMA_TIMEOUT_SECONDS", math.inf),
    ("GEMMA_TEMPERATURE", math.nan), ("GEMMA_TEMPERATURE", -1),
    ("GEMMA_MAX_OUTPUT_TOKENS", True), ("GEMMA_MAX_OUTPUT_TOKENS", 0),
    ("GEMMA_MODEL", "../secret?key=test-key-never-log"),
    ("GEMMA_THINKING_LEVEL", "unknown"),
])
def test_invalid_settings_fail_before_network(monkeypatch, name, value):
    monkeypatch.setattr(config, name, value)
    monkeypatch.setattr(gemma_client, "_open", lambda *a, **k: pytest.fail("network"))
    with pytest.raises(ConfigurationError) as error:
        GemmaClient().generate({})
    assert "test-key-never-log" not in str(error.value)


def test_oversized_input_is_rejected_without_truncation(monkeypatch):
    monkeypatch.setattr(gemma_client, "_open", lambda *a, **k: pytest.fail("network"))
    with pytest.raises(ConfigurationError, match="input"):
        GemmaClient().generate({"contents": "x" * 70000})


def test_oversized_response_is_rejected(monkeypatch):
    monkeypatch.setattr(gemma_client, "_open", lambda *a, **k: io.BytesIO(b"x" * (2 * 1024 * 1024 + 1)))
    with pytest.raises(InvalidResponseError, match="size limit"):
        GemmaClient().generate({})


def test_redirect_handler_refuses_to_forward_credentials():
    handler = gemma_client._NoRedirect()
    assert handler.redirect_request(None, None, 302, "redirect", {}, "https://elsewhere.invalid") is None
