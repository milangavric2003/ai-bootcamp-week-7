"""Verify saved retry evidence from the repository root; makes no API requests."""

import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess

from dotenv import dotenv_values


ROOT = Path(__file__).resolve().parents[4]
EVIDENCE = Path(__file__).resolve().parent


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    before = read_json(EVIDENCE / "before.json")
    after = read_json(EVIDENCE / "after.json")
    assert before["eval_set_sha256"] == after["eval_set_sha256"]
    assert before["summary"] == after["summary"]
    assert before["results"] == after["results"]
    assert all(after["config"][k] == v for k, v in before["config"].items())
    added = {k: v for k, v in after["config"].items() if k not in before["config"]}
    assert added == {"GEMMA_FALLBACK_MODEL": "gemini-3.5-flash-lite",
                     "GEMMA_PRIMARY_ATTEMPTS": 2, "GEMMA_FALLBACK_ATTEMPTS": 2,
                     "GEMMA_RETRY_BACKOFF_SECONDS": 0.25}
    assert after["config"]["GEMMA_TIMEOUT_SECONDS"] == 30
    assert after["config"]["STOPWORDS_ENABLED"] is False

    allowed = {".env.example", "src/config.py", "src/gemma_client.py",
               "src/generation.py", "src/generation_errors.py", "src/rag.py",
               "src/cli.py", "tests/conftest.py", "tests/test_gemma_client.py",
               "tests/test_generation.py"}
    hashes = read_json(EVIDENCE / "before-manifest.json")["sha256"]
    protected = {name: digest for name, digest in hashes.items() if name not in allowed}
    for name, digest in protected.items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name

    primary = read_json(EVIDENCE / "parental-cli.jsonl")
    fallback = read_json(EVIDENCE / "fallback-probe.jsonl")
    gemma, gemini = "gemma-4-26b-a4b-it", "gemini-3.5-flash-lite"
    assert primary["model"] == gemma and primary["fallback_used"] is False
    assert [a["status"] for a in primary["attempts"]] == ["success"]
    assert fallback["model"] == gemini and fallback["fallback_used"] is True
    assert [a["model"] for a in fallback["attempts"]] == [gemma, gemma, gemini]
    assert [a["status"] for a in fallback["attempts"]] == ["retryable_error", "retryable_error", "success"]
    for trace in (primary, fallback):
        assert trace["status"] == "complete" and trace["refused"] is True
        assert trace["citations"] == []
    assert primary["retrieved"] == fallback["retrieved"]

    # Tee-Object under Windows PowerShell writes UTF-16; keep new logs readable
    # in Git without altering the protected historical live evidence.
    for path in EVIDENCE.glob("*.txt"):
        raw = path.read_bytes()
        if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
            path.write_text(raw.decode("utf-16"), encoding="utf-8", newline="\n")

    python_files = list((ROOT / "src").glob("*.py")) + list((ROOT / "tests").glob("*.py"))
    for path in python_files:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        definitions = Counter(n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)))
        assert all(count == 1 for count in definitions.values()), path.name

    names = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=ROOT
    ).decode().split("\0")
    key = dotenv_values(ROOT / ".env", interpolate=False).get("GEMINI_API_KEY")
    assert key, "Local credential missing; never print it."
    scanned = 0
    for name in names:
        if not name or name.startswith("week06/"):
            continue
        path = ROOT / name
        if not path.is_file():
            continue
        raw = path.read_bytes()
        assert all(key.encode(encoding) not in raw for encoding in ("utf-8", "utf-16-le", "utf-16-be")), name
        scanned += 1

    result = {"protected_files_unchanged": len(protected),
              "eval_rows_identical": len(after["results"]),
              "summary_identical": True, "original_config_identical": True,
              "timeout_seconds": 30, "stopwords_enabled": False,
              "new_retry_settings": added, "live_primary_attempts": 1,
              "live_fallback_attempts": 3, "injected_primary_failures": 2,
              "python_files_parsed": len(python_files),
              "credential_scan_files": scanned, "credential_matches": 0}
    (EVIDENCE / "verification.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
