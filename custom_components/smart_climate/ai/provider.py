"""Abstract AI provider base class and factory."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod

_LOGGER = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class AIProviderError(Exception):
    """Base exception for AI provider errors."""


class AIConnectionError(AIProviderError):
    """Raised when the provider cannot be reached."""


class AIResponseError(AIProviderError):
    """Raised when the provider returns an unexpected response."""


# ---------------------------------------------------------------------------
# Abstract base
# ---------------------------------------------------------------------------


class AIProviderBase(ABC):
    """Base class that every AI provider must implement."""

    def __init__(self, config: dict) -> None:
        self._config = config

    @abstractmethod
    async def analyze(self, system_prompt: str, user_prompt: str) -> str:
        """Send prompts to the AI and return the raw response text."""

    @abstractmethod
    async def test_connection(self) -> bool:
        """Return True if the provider is reachable and credentials are valid."""


# ---------------------------------------------------------------------------
# No-op provider (used when AI is disabled)
# ---------------------------------------------------------------------------


class NoOpProvider(AIProviderBase):
    """Provider that does nothing -- returned when AI is disabled."""

    async def analyze(self, system_prompt: str, user_prompt: str) -> str:
        """Return an empty JSON object."""
        return "{}"

    async def test_connection(self) -> bool:
        """Always succeeds."""
        return True


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------


def create_ai_provider(provider_type: str, config: dict) -> AIProviderBase:
    """Create and return the appropriate AI provider instance.

    Args:
        provider_type: One of the AI_PROVIDER_* constants (e.g. "openai").
        config: Dict with keys ``api_key``, ``model``, and ``base_url``.

    Returns:
        An instance of the matching AIProviderBase subclass.
    """
    from ..const import (
        AI_PROVIDER_ANTHROPIC,
        AI_PROVIDER_GEMINI,
        AI_PROVIDER_GROK,
        AI_PROVIDER_OLLAMA,
        AI_PROVIDER_OPENAI,
    )

    if provider_type == AI_PROVIDER_OPENAI:
        from .openai_provider import OpenAIProvider

        return OpenAIProvider(config)

    if provider_type == AI_PROVIDER_ANTHROPIC:
        from .anthropic_provider import AnthropicProvider

        return AnthropicProvider(config)

    if provider_type == AI_PROVIDER_OLLAMA:
        from .ollama_provider import OllamaProvider

        return OllamaProvider(config)

    if provider_type == AI_PROVIDER_GEMINI:
        from .gemini_provider import GeminiProvider

        return GeminiProvider(config)

    if provider_type == AI_PROVIDER_GROK:
        from .grok_provider import GrokProvider

        return GrokProvider(config)

    _LOGGER.warning(
        "Unknown AI provider type '%s'; falling back to NoOpProvider",
        provider_type,
    )
    return NoOpProvider(config)
