import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from src import config
from src.generation import validate_backend
from src.generation_errors import ConfigurationError


def test_key_and_trace_destination_are_not_in_snapshot(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "private-test-key")
    monkeypatch.setenv("GEMMA_TRACE_PATH", "private-location.jsonl")
    snapshot = json.dumps(config.snapshot())
    assert "private-test-key" not in snapshot
    assert "private-location" not in snapshot
    assert "GEMINI_API_KEY" not in snapshot
    assert config.STOPWORDS_ENABLED is False


def test_root_env_loading_preserves_process_precedence_and_does_not_expand_secrets(tmp_path):
    # Import the actual config file in a tiny isolated package beside a synthetic .env.
    package = tmp_path / "src"
    package.mkdir()
    (package / "__init__.py").write_text("")
    for name in ["config.py", "generation_prompt.py", "generation_errors.py"]:
        (package / name).write_bytes((Path("src") / name).read_bytes())
    (tmp_path / ".env").write_text(
        "ANSWER_BACKEND=gemma\nGEMINI_API_KEY=file-secret\nGEMMA_MODEL=${GEMINI_API_KEY}\n"
    )
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(("GEMMA_", "GEMINI_", "ANSWER_BACKEND", "PYTHON_DOTENV"))}
    env["ANSWER_BACKEND"] = "extractive"
    proc = subprocess.run(
        [sys.executable, "-c", "import json; from src.config import snapshot; print(json.dumps(snapshot()))"],
        cwd=tmp_path, env=env, capture_output=True, text=True, timeout=15,
    )
    assert proc.returncode == 0, proc.stderr
    snapshot = json.loads(proc.stdout)
    assert snapshot["ANSWER_BACKEND"] == "extractive"
    assert snapshot["GEMMA_MODEL"] == "${GEMINI_API_KEY}"
    assert "file-secret" not in proc.stdout


@pytest.mark.parametrize("backend", ["unknown", "", "Gemma"])
def test_unknown_backend_fails(monkeypatch, backend):
    monkeypatch.setattr(config, "ANSWER_BACKEND", backend)
    with pytest.raises(ConfigurationError):
        validate_backend()


def test_missing_key_fails_even_before_empty_retrieval(monkeypatch):
    from src import rag
    monkeypatch.setattr(config, "ANSWER_BACKEND", "gemma")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setattr(rag, "retrieve_top_k", lambda *_: pytest.fail("retrieval must not start"))
    with pytest.raises(ConfigurationError, match="GEMINI_API_KEY"):
        rag.build_grounded_answer("test", [])


def test_invalid_numeric_environment_does_not_echo_secret():
    env = os.environ.copy()
    env["GEMMA_TIMEOUT_SECONDS"] = "secret-must-not-be-echoed"
    proc = subprocess.run([sys.executable, "-c", "from src import config"],
                          env=env, capture_output=True, text=True, timeout=15)
    assert proc.returncode != 0
    assert "GEMMA_TIMEOUT_SECONDS must be a valid number" in proc.stderr
    assert "secret-must-not-be-echoed" not in proc.stderr
