"""Grounded decisions and same-run evidence, independent of retrieval backend."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re

from . import config
from .gemma_client import GemmaClient
from .generation_errors import ConfigurationError, GenerationError, InvalidResponseError, TraceError
from .generation_prompt import SYSTEM_PROMPT
from .retrieval import RetrievalResult


@dataclass(frozen=True)
class GenerationDecision:
    answer: str
    citations: list[str]
    refused: bool
    usage: dict | None = None
    model: str | None = None
    attempts: list[dict] = field(default_factory=list)


def validate_backend() -> None:
    if config.ANSWER_BACKEND not in ("extractive", "gemma"):
        raise ConfigurationError("ANSWER_BACKEND must be extractive or gemma.")
    if config.ANSWER_BACKEND == "gemma":
        GemmaClient().validate()


def build_request(question: str, results: list[RetrievalResult]) -> dict:
    evidence = [{"chunk_id": r.chunk.chunk_id, "doc_id": r.chunk.doc_id,
                 "title": r.chunk.title, "version": r.chunk.version,
                 "status": r.chunk.status, "text": r.chunk.text} for r in results]
    return {
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": json.dumps(
            {"question": question, "evidence": evidence}, ensure_ascii=False)}]}],
        "generationConfig": {"temperature": config.GEMMA_TEMPERATURE, "candidateCount": 1,
                             "maxOutputTokens": config.GEMMA_MAX_OUTPUT_TOKENS,
                             "thinkingConfig": {"thinkingLevel": config.GEMMA_THINKING_LEVEL}},
    }


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InvalidResponseError("Gemma decision contains duplicate fields.")
        result[key] = value
    return result


def _invalid_constant(_):
    raise InvalidResponseError("Gemma decision contains a non-JSON number.")


def _normalize_inline_citations(answer: str, citations: list[str]) -> str:
    groups = re.compile(r"\[([^\[\]]*)\]")
    # Leftover brackets expose nesting or an unbalanced marker that a regex
    # matching only complete groups would otherwise silently skip.
    unbracketed = groups.sub("", answer)
    if "[" in unbracketed or "]" in unbracketed:
        raise InvalidResponseError("Gemma inline citations must be balanced, non-nested source groups.")
    selected = set(citations)

    def normalize(match):
        members = list(dict.fromkeys(member.strip() for member in match.group(1).split(",")))
        if any(not member or member not in selected for member in members):
            raise InvalidResponseError("Gemma inline citations must match the selected source IDs.")
        return " ".join(f"[{member}]" for member in members)

    return groups.sub(normalize, answer)


def parse_decision(text: str, results: list[RetrievalResult]) -> GenerationDecision:
    try:
        value = json.loads(text, object_pairs_hook=_unique_object, parse_constant=_invalid_constant)
    except (ValueError, TypeError, RecursionError):
        raise InvalidResponseError("Gemma decision must be strict JSON without Markdown fences.") from None
    if not isinstance(value, dict) or set(value) != {"answer", "citations", "refused"}:
        raise InvalidResponseError("Gemma decision must contain exactly answer, citations and refused.")
    answer, citations, refused = value["answer"], value["citations"], value["refused"]
    if not isinstance(answer, str) or type(refused) is not bool:
        raise InvalidResponseError("Gemma answer must be a string and refused must be a boolean.")
    if not isinstance(citations, list) or any(not isinstance(c, str) for c in citations):
        raise InvalidResponseError("Gemma citations must be an array of chunk ID strings.")
    allowed = {r.chunk.chunk_id for r in results}
    if any(c not in allowed for c in citations):
        raise InvalidResponseError("Gemma cited a chunk that was not supplied.")
    citations = list(dict.fromkeys(citations))
    if refused:
        if answer != "" or citations:
            raise InvalidResponseError("Gemma refusal must have empty answer and citations.")
    elif not answer.strip() or not citations:
        raise InvalidResponseError("Gemma answer must have nonempty text and supporting citations.")
    answer = _normalize_inline_citations(answer, citations)
    return GenerationDecision(answer, citations, refused)


def generate_answer(question: str, results: list[RetrievalResult]) -> GenerationDecision:
    response = GemmaClient().generate(build_request(question, results))
    model = response.model or config.GEMMA_MODEL
    try:
        decision = parse_decision(response.text, results)
    except GenerationError as error:
        error.model, error.attempts = model, response.attempts
        raise error from None
    return GenerationDecision(decision.answer, decision.citations, decision.refused,
                              response.usage, model, response.attempts)


_trace_paths: set[Path] = set()


def record_trace(question, results, result, status, elapsed_ms, usage=None, error=None) -> None:
    destination = os.environ.get("GEMMA_TRACE_PATH", "")
    if not destination:
        return
    path = Path(destination).resolve()
    if path.suffix.lower() != ".jsonl":
        raise TraceError("GEMMA_TRACE_PATH must name a fresh .jsonl evidence file.")
    model = result.model if result else error.model if error else None
    attempts = result.attempts if result else error.attempts if error else []
    record = {
        "created_at": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
        "question": question, "backend": config.ANSWER_BACKEND,
        "provider": config.GEMMA_PROVIDER if config.ANSWER_BACKEND == "gemma" else None,
        "requested_model": config.GEMMA_MODEL if config.ANSWER_BACKEND == "gemma" else None,
        "model": model, "attempts": attempts,
        "fallback_used": any(attempt["model"] != config.GEMMA_MODEL for attempt in attempts),
        "prompt_sha256": config.GEMMA_PROMPT_SHA256 if config.ANSWER_BACKEND == "gemma" else None,
        "status": status, "elapsed_ms": round(elapsed_ms, 3), "usage": usage or {},
        "retrieved": [{"chunk_id": r.chunk.chunk_id, "score": r.score} for r in results],
        "answer": result.answer if result else None,
        "citations": result.citations if result else [],
        "refused": result.refused if result else None,
        "error_type": type(error).__name__ if error else None,
        "error": str(error) if error else None,
    }
    # Also redact accidental occurrences in question/answer text supplied by users.
    key = os.environ.get("GEMINI_API_KEY", "")
    def redact(value):
        if isinstance(value, str):
            return value.replace(key, "[REDACTED]") if key else value
        if isinstance(value, list):
            return [redact(v) for v in value]
        if isinstance(value, dict):
            return {k: redact(v) for k, v in value.items()}
        return value
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        # First use is exclusive creation; never mix a previous process's evidence.
        with path.open("a" if path in _trace_paths else "x", encoding="utf-8") as stream:
            stream.write(json.dumps(redact(record), ensure_ascii=False, allow_nan=False) + "\n")
        _trace_paths.add(path)
    except (OSError, ValueError):
        raise TraceError("Cannot write Gemma evidence; choose a new writable .jsonl file.") from None
