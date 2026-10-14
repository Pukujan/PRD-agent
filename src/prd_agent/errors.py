"""The failure vocabulary of the pipeline. Every stage failure is one of these."""

from __future__ import annotations


class StageError(Exception):
    """A stage could not complete. The run stops and reports this message."""


class SchemaError(StageError):
    """A stage document does not match its contract."""


class ModelOutputError(StageError):
    """The model returned something the stage cannot parse."""


class LLMUnavailable(StageError):
    """No model provider is configured, so the run cannot make a model call."""


class StoryGateError(StageError):
    """A draft still trips a banned pattern after the allowed rewrites."""
