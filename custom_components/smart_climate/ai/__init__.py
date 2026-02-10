"""AI analysis pipeline for Smart Climate."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from ..coordinator import SmartClimateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_run_analysis(hass: HomeAssistant, coordinator: SmartClimateCoordinator) -> None:
    """Run the full AI analysis pipeline.

    Steps:
        1. Determine the configured AI provider.
        2. Build system and user prompts from current coordinator data.
        3. Send prompts to the AI provider and receive a response.
        4. Parse the AI response into structured suggestions.
        5. Store suggestions and summary in the coordinator's house state.
    """
    from ..const import (
        AI_PROVIDER_NONE,
        CONF_AI_API_KEY,
        CONF_AI_BASE_URL,
        CONF_AI_MODEL,
        CONF_AI_PROVIDER,
    )
    from .analysis import parse_ai_response
    from .prompts import build_system_prompt, build_user_prompt
    from .provider import create_ai_provider
    from .suggestions import store_suggestions

    config = coordinator.config_entry.data
    provider_type = config.get(CONF_AI_PROVIDER, AI_PROVIDER_NONE)

    if provider_type == AI_PROVIDER_NONE:
        _LOGGER.debug("AI provider is 'none'; skipping analysis pipeline")
        return

    _LOGGER.info("Starting AI analysis pipeline with provider '%s'", provider_type)

    provider = create_ai_provider(
        provider_type,
        {
            "api_key": config.get(CONF_AI_API_KEY, ""),
            "model": config.get(CONF_AI_MODEL, ""),
            "base_url": config.get(CONF_AI_BASE_URL, ""),
        },
    )

    system_prompt = build_system_prompt()
    user_prompt = build_user_prompt(coordinator.data)

    try:
        response = await provider.analyze(system_prompt, user_prompt)
    except Exception:
        _LOGGER.exception("AI provider failed to generate a response")
        raise

    suggestions, summary = parse_ai_response(response)

    _LOGGER.info(
        "AI analysis complete: %d suggestions generated", len(suggestions)
    )

    await store_suggestions(coordinator, suggestions, summary)
