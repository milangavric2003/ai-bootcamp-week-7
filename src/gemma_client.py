"""Bounded Google generation attempts: Gemma first, then explicit Gemini fallback."""

from copy import deepcopy
from dataclasses import dataclass, field
from http.client import HTTPException
import json
import math
import os
import re
import ssl
from time import perf_counter, sleep
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from . import config
from .generation_errors import ConfigurationError, GenerationError, InvalidResponseError, ProviderError


@dataclass(frozen=True)
class ProviderResponse:
    text: str
    usage: dict
    model: str | None = None
    attempts: list[dict] = field(default_factory=list)


class _RetryableProviderError(ProviderError):
    """Internal marker for a sanitized transient failure, never a model refusal."""


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
        fallback = config.GEMMA_FALLBACK_MODEL
        if not isinstance(fallback, str) or (fallback and not re.fullmatch(r"gemini-[A-Za-z0-9][A-Za-z0-9._-]*", fallback)):
            raise ConfigurationError("GEMMA_FALLBACK_MODEL must be a Gemini model ID or empty to disable fallback.")
        for name, count in [("GEMMA_PRIMARY_ATTEMPTS", config.GEMMA_PRIMARY_ATTEMPTS),
                            ("GEMMA_FALLBACK_ATTEMPTS", config.GEMMA_FALLBACK_ATTEMPTS)]:
            if type(count) is not int or not 1 <= count <= 2:
                raise ConfigurationError(f"{name} must be an integer between 1 and 2.")
        backoff = config.GEMMA_RETRY_BACKOFF_SECONDS
        if type(backoff) not in (int, float) or not math.isfinite(backoff) or not 0 <= backoff <= 1:
            raise ConfigurationError("GEMMA_RETRY_BACKOFF_SECONDS must be finite and between 0 and 1.")
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
        # Google issues both standard keys and newer dotted authorization keys.
        # Treat the credential as opaque while excluding unsafe header characters.
        if not key or not re.fullmatch(r"[!-~]+", key):
            raise ConfigurationError("Set a valid GEMINI_API_KEY locally before selecting Gemma.")

    def generate(self, payload: dict) -> ProviderResponse:
        self.validate()
        models = [config.GEMMA_MODEL] * config.GEMMA_PRIMARY_ATTEMPTS
        if config.GEMMA_FALLBACK_MODEL:
            models += [config.GEMMA_FALLBACK_MODEL] * config.GEMMA_FALLBACK_ATTEMPTS
        # Validate/encode all inputs before any request; never truncate evidence.
        encoded = {model: self._encode(payload, model) for model in dict.fromkeys(models)}
        attempts = []
        for index, model in enumerate(models):
            started = perf_counter()
            try:
                response = self._generate_once(encoded[model], model)
            except GenerationError as error:
                retryable = isinstance(error, _RetryableProviderError)
                attempts.append({"model": model, "attempt": index + 1,
                                 "status": "retryable_error" if retryable else "error",
                                 "elapsed_ms": round((perf_counter() - started) * 1000, 3),
                                 "error": str(error)})
                if not retryable:
                    error.model, error.attempts = model, attempts
                    raise error from None
                if index == len(models) - 1:
                    raise ProviderError(
                        f"Google generation failed after {len(attempts)} attempts. {error}",
                        model=model, attempts=attempts,
                    ) from None
                sleep(min(config.GEMMA_RETRY_BACKOFF_SECONDS * (2 ** index), 1.0))
                continue
            attempts.append({"model": model, "attempt": index + 1, "status": "success",
                             "elapsed_ms": round((perf_counter() - started) * 1000, 3)})
            return ProviderResponse(response.text, response.usage, model, attempts)
        raise AssertionError("Validated attempt schedule must not be empty.")

    @staticmethod
    def _encode(payload: dict, model: str) -> bytes:
        request_payload = deepcopy(payload)
        if model.startswith("gemini-") and isinstance(request_payload.get("generationConfig"), dict):
            # Use Gemini's single-candidate default; keep the same evidence/prompt.
            request_payload["generationConfig"].pop("candidateCount", None)
        try:
            data = json.dumps(request_payload, ensure_ascii=False, allow_nan=False).encode("utf-8")
        except (ValueError, TypeError, UnicodeError):
            raise ConfigurationError("Gemma input could not be serialized.") from None
        if len(data) > config.GEMMA_MAX_INPUT_BYTES:
            raise ConfigurationError("Gemma input exceeds the configured byte budget; no chunks were dropped.")
        return data

    def _generate_once(self, data: bytes, model: str) -> ProviderResponse:
        request = Request(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
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
            hint = hints.get(code, "request failed")
            error_type = _RetryableProviderError if code in (408, 429, 500, 502, 503, 504) else ProviderError
            raise error_type(f"Google HTTP {code}: {hint}.") from None
        except ssl.SSLCertVerificationError:
            raise ProviderError("Google TLS certificate verification failed; check local certificates.") from None
        except URLError as error:
            if isinstance(error.reason, ssl.SSLCertVerificationError):
                raise ProviderError("Google TLS certificate verification failed; check local certificates.") from None
            raise _RetryableProviderError("Google network request failed or timed out.") from None
        except (OSError, HTTPException):
            # Provider errors can include URLs, headers or request data. Never echo them.
            raise _RetryableProviderError("Google network request failed or timed out.") from None
        if len(raw) > 2 * 1024 * 1024:
            raise InvalidResponseError("Google response exceeded the transport size limit.")
        try:
            value = json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeError, RecursionError):
            raise InvalidResponseError("Google returned invalid provider JSON.") from None
        return self._extract(value)

    @staticmethod
    def _extract(value) -> ProviderResponse:
        if not isinstance(value, dict):
            raise InvalidResponseError("Google response must be an object.")
        feedback = value.get("promptFeedback", {})
        if not isinstance(feedback, dict) or feedback.get("blockReason"):
            raise InvalidResponseError("Google blocked the prompt or returned invalid feedback.")
        candidates = value.get("candidates")
        if not isinstance(candidates, list) or len(candidates) != 1:
            raise InvalidResponseError("Google must return one complete candidate.")
        candidate = candidates[0]
        if not isinstance(candidate, dict) or candidate.get("finishReason") != "STOP":
            raise InvalidResponseError("Google output was blocked, truncated or incomplete.")
        content = candidate.get("content", {})
        parts = content.get("parts") if isinstance(content, dict) else None
        if not isinstance(parts, list) or not parts:
            raise InvalidResponseError("Google returned no text parts.")
        text = []
        for part in parts:
            if not isinstance(part, dict):
                raise InvalidResponseError("Google returned an invalid text part.")
            if part.get("thought") is True:
                continue
            if not isinstance(part.get("text"), str) or "functionCall" in part:
                raise InvalidResponseError("Google returned a non-text answer part.")
            text.append(part["text"])
        combined = "".join(text)
        if not combined.strip():
            raise InvalidResponseError("Google returned an empty answer.")
        supplied_usage = value.get("usageMetadata", {})
        fields = ("promptTokenCount", "candidatesTokenCount", "totalTokenCount",
                  "cachedContentTokenCount", "thoughtsTokenCount")
        usage = {k: v for k, v in supplied_usage.items()
                 if k in fields and type(v) is int and v >= 0} if isinstance(supplied_usage, dict) else {}
        return ProviderResponse(combined, usage)
