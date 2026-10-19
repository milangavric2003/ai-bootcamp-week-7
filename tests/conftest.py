"""Unit tests stay offline even when a developer's .env enables Gemma."""

import pytest

from src import config, gemma_client


@pytest.fixture(autouse=True)
def offline_generation_defaults(monkeypatch):
    monkeypatch.setattr(config, "ANSWER_BACKEND", "extractive")
    monkeypatch.setattr(config, "GEMMA_MODEL", "gemma-4-26b-a4b-it")
    monkeypatch.setattr(config, "GEMMA_TIMEOUT_SECONDS", 30.0)
    monkeypatch.setattr(config, "GEMMA_TEMPERATURE", 0.0)
    monkeypatch.setattr(config, "GEMMA_MAX_OUTPUT_TOKENS", 1024)
    monkeypatch.setattr(config, "GEMMA_THINKING_LEVEL", "minimal")
    monkeypatch.delenv("GEMMA_TRACE_PATH", raising=False)

    def unexpected_request(*args, **kwargs):
        pytest.fail("Unit tests must mock every Google request.")

    monkeypatch.setattr(gemma_client, "_open", unexpected_request)
