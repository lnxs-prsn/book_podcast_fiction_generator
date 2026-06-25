"""novel_pipeline — pedagogical-novel writing pipeline.

Public API:
- main (CLI entry)
- run_session
- load_config
- All custom exceptions
"""

from .cli import main
from .config import load_config
from .exceptions import (
    APIRateLimitError,
    APIResponseError,
    ChapterValidationError,
    ConfigError,
    ContextOverflowError,
    CostLimitError,
    DocumentLoadError,
    LivingDocValidationError,
    PipelineError,
    PromotionCollisionError,
    RejectionLimitReachedError,
    ResumeStateError,
)
from .session import run_session

__all__ = [
    "main",
    "run_session",
    "load_config",
    "PipelineError",
    "DocumentLoadError",
    "ConfigError",
    "APIResponseError",
    "APIRateLimitError",
    "ChapterValidationError",
    "LivingDocValidationError",
    "ContextOverflowError",
    "CostLimitError",
    "ResumeStateError",
    "PromotionCollisionError",
    "RejectionLimitReachedError",
]

__version__ = "0.3.0"
