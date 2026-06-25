"""Custom exception hierarchy for the pipeline.

All pipeline-specific errors inherit from PipelineError so callers can catch
the whole family with one except clause when they want to.
"""


class PipelineError(Exception):
    """Base class for all pipeline-specific errors."""


class DocumentLoadError(PipelineError):
    """Raised when a template or living-doc file cannot be loaded."""


class ConfigError(PipelineError):
    """Raised when configuration is missing or invalid."""


class APIResponseError(PipelineError):
    """Raised when the OpenRouter response is malformed or unusable."""


class APIRateLimitError(APIResponseError):
    """Raised when the API returns 429 and retries are exhausted."""


class ChapterValidationError(PipelineError):
    """Raised when a generated chapter fails validation (too short,
    truncated by length, etc.)."""


class LivingDocValidationError(PipelineError):
    """Raised when an updated living doc fails structural validation."""

    def __init__(self, message: str, missing: list[str] | None = None, diff: str | None = None):
        super().__init__(message)
        self.missing = missing or []
        self.diff = diff or ""


class ContextOverflowError(PipelineError):
    """Raised when the prompt + safety margin would exceed the model context."""


class CostLimitError(PipelineError):
    """Raised when a session or lifetime cost limit would be exceeded."""


class ResumeStateError(PipelineError):
    """Raised when .pipeline_state.json is missing/malformed in a way that
    cannot be reconciled with the filesystem automatically."""


class PromotionCollisionError(PipelineError):
    """M1: Raised when promote_chapter would overwrite an existing canonical
    chapter. Indicates a state-drift bug that the human must resolve."""


class RejectionLimitReachedError(PipelineError):
    """M4: Raised when the rejection-retry loop exceeds the configured
    maximum number of iterations (`max_rejection_retries`)."""
