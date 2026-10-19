"""One nonstreaming Google generateContent request; no retry or fallback."""

from dataclasses import dataclass
from http.client import HTTPException
import json
import math
import os
import re
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from . import config
from .generation_errors import ConfigurationError, InvalidResponseError, ProviderError


@dataclass(frozen=True)
class ProviderResponse:
    text: str
    usage: dict


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Do not forward the private authentication header to any redirect target.
        return None


def _open(request: Request, timeout: float):
    return build_opener(_NoRedirect()).open(request, timeout=timeout)


class GemmaClient:
    def validate(self) -> None:
        model = config.GEMMA_MODEL
        if not isinstance(model, str) or not re.fullmatch(r"gemma-[A-Za-z0-9][A-Za-z0-9._-]*", model):
            raise ConfigurationError("GEMMA_MODEL must be a Gemma model ID, not a URL.")
        for name, value in [("GEMMA_TIMEOUT_SECONDS", config.GEMMA_TIMEOUT_SECONDS),
                            ("GEMMA_TEMPERATURE", config.GEMMA_TEMPERATURE)]:
            if type(value) not in (int, float) or not math.isfinite(value):
                raise ConfigurationError(f"{name} must be finite.")
        if config.GEMMA_TIMEOUT_SECONDS <= 0:
            raise ConfigurationError("GEMMA_TIMEOUT_SECONDS must be positive.")
        if not 0 <= config.GEMMA_TEMPERATURE <= 2:
            raise ConfigurationError("GEMMA_TEMPERATURE must be between 0 and 2.")
        if type(config.GEMMA_MAX_OUTPUT_TOKENS) is not int or not 1 <= config.GEMMA_MAX_OUTPUT_TOKENS <= 8192:
            raise ConfigurationError("GEMMA_MAX_OUTPUT_TOKENS must be an integer between 1 and 8192.")
        if config.GEMMA_THINKING_LEVEL not in ("minimal", "high"):
            raise ConfigurationError("GEMMA_THINKING_LEVEL must be minimal or high.")
        key = os.environ.get("GEMINI_API_KEY", "")
        if not key or not re.fullmatch(r"[A-Za-z0-9_-]+", key):
            raise ConfigurationError("Set a valid GEMINI_API_KEY locally before selecting Gemma.")

    def generate(self, payload: dict) -> ProviderResponse:
        self.validate()
        try:
            data = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode("utf-8")
        except (ValueError, TypeError, UnicodeError):
            raise ConfigurationError("Gemma input could not be serialized.") from None
        if len(data) > config.GEMMA_MAX_INPUT_BYTES:
            raise ConfigurationError("Gemma input exceeds the configured byte budget; no chunks were dropped.")
        request = Request(
            f"https://generativelanguage.googleapis.com/v1beta/models/{config.GEMMA_MODEL}:generateContent",
            data=data, method="POST",
            headers={"Content-Type": "application/json", "x-goog-api-key": os.environ["GEMINI_API_KEY"]},
        )
        try:
            with _open(request, timeout=config.GEMMA_TIMEOUT_SECONDS) as response:
                raw = response.read(2 * 1024 * 1024 + 1)
        except HTTPError as error:
            code = error.code
            error.close()
            hints = {401: "check the API key", 403: "check key permissions and model access",
                     404: "check model availability", 429: "quota or rate limit exhausted"}
            hint = hints.get(code, "request failed; no automatic retry")
            raise ProviderError(f"Gemma HTTP {code}: {hint}.") from None
        except (URLError, OSError, HTTPException):
            # Provider errors can include URLs, headers or request data. Never echo them.
            raise ProviderError("Gemma network request failed or timed out; no automatic retry.") from None
        if len(raw) > 2 * 1024 * 1024:
            raise InvalidResponseError("Gemma response exceeded the transport size limit.")
        try:
            value = json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeError, RecursionError):
            raise InvalidResponseError("Gemma returned invalid provider JSON.") from None
        return self._extract(value)

    @staticmethod
    def _extract(value) -> ProviderResponse:
        if not isinstance(value, dict):
            raise InvalidResponseError("Gemma response must be an object.")
        feedback = value.get("promptFeedback", {})
        if not isinstance(feedback, dict) or feedback.get("blockReason"):
            raise InvalidResponseError("Gemma blocked the prompt or returned invalid feedback.")
        candidates = value.get("candidates")
        if not isinstance(candidates, list) or len(candidates) != 1:
            raise InvalidResponseError("Gemma must return one complete candidate.")
        candidate = candidates[0]
        if not isinstance(candidate, dict) or candidate.get("finishReason") != "STOP":
            raise InvalidResponseError("Gemma output was blocked, truncated or incomplete.")
        content = candidate.get("content", {})
        parts = content.get("parts") if isinstance(content, dict) else None
        if not isinstance(parts, list) or not parts:
            raise InvalidResponseError("Gemma returned no text parts.")
        text = []
        for part in parts:
            if not isinstance(part, dict):
                raise InvalidResponseError("Gemma returned an invalid text part.")
            if part.get("thought") is True:
                continue
            if not isinstance(part.get("text"), str) or "functionCall" in part:
                raise InvalidResponseError("Gemma returned a non-text answer part.")
            text.append(part["text"])
        combined = "".join(text)
        if not combined.strip():
            raise InvalidResponseError("Gemma returned an empty answer.")
        supplied_usage = value.get("usageMetadata", {})
        fields = ("promptTokenCount", "candidatesTokenCount", "totalTokenCount",
                  "cachedContentTokenCount", "thoughtsTokenCount")
        usage = {k: v for k, v in supplied_usage.items()
                 if k in fields and type(v) is int and v >= 0} if isinstance(supplied_usage, dict) else {}
        return ProviderResponse(combined, usage)
