"""Operational errors are deliberately distinct from evidence refusals."""


class GenerationError(RuntimeError):
    """Generation could not complete; no quality result should be recorded."""

    def __init__(self, message: str, *, model: str | None = None, attempts: list[dict] | None = None):
        super().__init__(message)
        self.model = model
        self.attempts = list(attempts or [])


class ConfigurationError(GenerationError):
    """Missing or invalid local settings."""


class ProviderError(GenerationError):
    """Sanitized transport/provider failure."""


class InvalidResponseError(GenerationError):
    """The provider output does not satisfy the answer contract."""


class TraceError(GenerationError):
    """Requested evidence could not be saved safely."""
