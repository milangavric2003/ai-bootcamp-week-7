"""Operational errors are deliberately distinct from evidence refusals."""


class GenerationError(RuntimeError):
    """Generation could not complete; no quality result should be recorded."""


class ConfigurationError(GenerationError):
    """Missing or invalid local settings."""


class ProviderError(GenerationError):
    """Sanitized transport/provider failure."""


class InvalidResponseError(GenerationError):
    """The provider output does not satisfy the answer contract."""


class TraceError(GenerationError):
    """Requested evidence could not be saved safely."""
