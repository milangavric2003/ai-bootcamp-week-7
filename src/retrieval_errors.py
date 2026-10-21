"""Operational retrieval failures are distinct from evidence-based refusals."""


class RetrievalError(RuntimeError):
    """The selected retrieval backend could not produce valid evidence scores."""
