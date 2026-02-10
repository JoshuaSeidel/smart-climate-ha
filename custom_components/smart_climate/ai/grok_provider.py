"""xAI Grok AI provider (OpenAI-compatible) using direct aiohttp."""

from __future__ import annotations

import logging

from .openai_provider import OpenAIProvider

_LOGGER = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://api.x.ai"
DEFAULT_MODEL = "grok-3-mini"


class GrokProvider(OpenAIProvider):
    """AI provider that talks to the xAI Grok API.

    Grok uses an OpenAI-compatible API, so this subclass simply overrides
    the default base URL and model while inheriting all request logic.
    """

    def __init__(self, config: dict) -> None:
        # Apply Grok-specific defaults before passing to the parent
        grok_config = dict(config)
        if not grok_config.get("base_url"):
            grok_config["base_url"] = DEFAULT_BASE_URL
        if not grok_config.get("model"):
            grok_config["model"] = DEFAULT_MODEL
        super().__init__(grok_config)
