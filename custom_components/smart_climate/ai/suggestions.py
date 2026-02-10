"""Suggestion lifecycle management for Smart Climate AI pipeline."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any

from ..const import (
    AUTO_APPLY_CONFIDENCE_THRESHOLD,
    CONF_AI_AUTO_APPLY,
    DEFAULT_AI_AUTO_APPLY,
    DOMAIN,
    EVENT_NEW_SUGGESTIONS,
    EVENT_SUGGESTION_APPLIED,
    EVENT_SUGGESTION_REJECTED,
    SUGGESTION_APPLIED,
    SUGGESTION_EXPIRED,
    SUGGESTION_PENDING,
    SUGGESTION_REJECTED,
)
from ..models import HouseState, Suggestion

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from ..coordinator import SmartClimateCoordinator

_LOGGER = logging.getLogger(__name__)

# Service calls that are considered safe for automatic execution.
SAFE_SERVICE_MAP: dict[str, tuple[str, str]] = {
    "set_temperature": ("climate", "set_temperature"),
    "set_mode": ("climate", "set_hvac_mode"),
}


# ---------------------------------------------------------------------------
# Store suggestions
# ---------------------------------------------------------------------------


async def store_suggestions(
    coordinator: SmartClimateCoordinator,
    suggestions: list[Suggestion],
    summary: str,
) -> None:
    """Store new suggestions in the house state and fire events.

    If auto-apply is enabled in the config, high-confidence suggestions
    will be executed automatically.

    Args:
        coordinator: The active SmartClimateCoordinator instance.
        suggestions: List of parsed Suggestion objects from the AI.
        summary: The AI-generated daily summary text.
    """
    hass = coordinator.hass
    house: HouseState = coordinator.data.get("house") if coordinator.data else None  # type: ignore[assignment]

    if house is None:
        _LOGGER.warning("No house state available; cannot store suggestions")
        return

    # Expire any old suggestions first
    expire_old_suggestions(house)

    # Store new suggestions and summary
    house.suggestions.extend(suggestions)
    house.ai_daily_summary = summary
    house.last_analysis_time = datetime.now()

    # Fire event so the frontend / automations can react
    hass.bus.async_fire(
        EVENT_NEW_SUGGESTIONS,
        {
            "count": len(suggestions),
            "summary": summary,
            "suggestion_ids": [s.id for s in suggestions],
        },
    )

    _LOGGER.info(
        "Stored %d new AI suggestions; daily summary updated",
        len(suggestions),
    )

    # Auto-apply if configured
    auto_apply = coordinator.config_entry.data.get(
        CONF_AI_AUTO_APPLY, DEFAULT_AI_AUTO_APPLY
    )
    if auto_apply:
        await _auto_apply_suggestions(hass, coordinator, suggestions)

    # Request a coordinator refresh so entities pick up new data
    await coordinator.async_request_refresh()


# ---------------------------------------------------------------------------
# Approve / reject / execute
# ---------------------------------------------------------------------------


async def approve_suggestion(
    coordinator: SmartClimateCoordinator, suggestion_id: str
) -> bool:
    """Approve and execute a pending suggestion.

    Args:
        coordinator: The active SmartClimateCoordinator instance.
        suggestion_id: UUID of the suggestion to approve.

    Returns:
        True if the suggestion was found, approved, and executed.
    """
    suggestion = _find_suggestion(coordinator, suggestion_id)
    if suggestion is None:
        _LOGGER.warning("Suggestion '%s' not found", suggestion_id)
        return False

    if suggestion.status != SUGGESTION_PENDING:
        _LOGGER.warning(
            "Suggestion '%s' is not pending (status=%s)",
            suggestion_id,
            suggestion.status,
        )
        return False

    if suggestion.is_expired():
        suggestion.status = SUGGESTION_EXPIRED
        _LOGGER.info("Suggestion '%s' has expired", suggestion_id)
        return False

    # Execute the action
    success = await execute_suggestion(coordinator.hass, suggestion)

    if success:
        suggestion.status = SUGGESTION_APPLIED
        suggestion.applied_at = datetime.now()

        coordinator.hass.bus.async_fire(
            EVENT_SUGGESTION_APPLIED,
            {
                "suggestion_id": suggestion.id,
                "title": suggestion.title,
                "action_type": suggestion.action_type,
                "room": suggestion.room,
            },
        )
        _LOGGER.info("Suggestion '%s' approved and applied", suggestion_id)
    else:
        _LOGGER.warning("Suggestion '%s' approved but execution failed", suggestion_id)

    return success


async def reject_suggestion(
    coordinator: SmartClimateCoordinator,
    suggestion_id: str,
    reason: str = "",
) -> bool:
    """Reject a pending suggestion.

    Args:
        coordinator: The active SmartClimateCoordinator instance.
        suggestion_id: UUID of the suggestion to reject.
        reason: Optional reason for rejection.

    Returns:
        True if the suggestion was found and rejected.
    """
    suggestion = _find_suggestion(coordinator, suggestion_id)
    if suggestion is None:
        _LOGGER.warning("Suggestion '%s' not found", suggestion_id)
        return False

    if suggestion.status != SUGGESTION_PENDING:
        _LOGGER.warning(
            "Suggestion '%s' is not pending (status=%s)",
            suggestion_id,
            suggestion.status,
        )
        return False

    suggestion.status = SUGGESTION_REJECTED
    suggestion.rejected_reason = reason or "Rejected by user"

    coordinator.hass.bus.async_fire(
        EVENT_SUGGESTION_REJECTED,
        {
            "suggestion_id": suggestion.id,
            "title": suggestion.title,
            "reason": suggestion.rejected_reason,
        },
    )

    _LOGGER.info("Suggestion '%s' rejected: %s", suggestion_id, suggestion.rejected_reason)
    return True


async def execute_suggestion(
    hass: HomeAssistant, suggestion: Suggestion
) -> bool:
    """Convert a suggestion's action_data into Home Assistant service calls.

    Only allows safe service calls (climate.set_temperature,
    climate.set_hvac_mode, etc.).

    Args:
        hass: The Home Assistant instance.
        suggestion: The Suggestion to execute.

    Returns:
        True if the service call was dispatched successfully.
    """
    action_type = suggestion.action_type
    action_data = suggestion.action_data
    room_slug = suggestion.room

    if action_type == "set_temperature":
        return await _execute_set_temperature(hass, room_slug, action_data)

    if action_type == "set_mode":
        return await _execute_set_mode(hass, room_slug, action_data)

    if action_type == "vent_adjustment":
        return await _execute_vent_adjustment(hass, room_slug, action_data)

    if action_type in ("schedule_change", "general"):
        # These are informational and don't map to a direct service call.
        # They are considered "executed" once the user acknowledges them.
        _LOGGER.info(
            "Suggestion '%s' is informational (action_type=%s); no service call needed",
            suggestion.id,
            action_type,
        )
        return True

    _LOGGER.warning(
        "Unknown action_type '%s' for suggestion '%s'",
        action_type,
        suggestion.id,
    )
    return False


# ---------------------------------------------------------------------------
# Expiration
# ---------------------------------------------------------------------------


def expire_old_suggestions(house_state: HouseState) -> None:
    """Mark expired suggestions in the house state.

    Any suggestion that is still pending and past its ``expires_at``
    timestamp will be moved to the ``expired`` status.
    """
    now = datetime.now()
    expired_count = 0

    for suggestion in house_state.suggestions:
        if suggestion.status == SUGGESTION_PENDING and now > suggestion.expires_at:
            suggestion.status = SUGGESTION_EXPIRED
            expired_count += 1

    if expired_count:
        _LOGGER.debug("Expired %d old suggestions", expired_count)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _find_suggestion(
    coordinator: SmartClimateCoordinator, suggestion_id: str
) -> Suggestion | None:
    """Look up a suggestion by ID from the coordinator's house state."""
    if not coordinator.data:
        return None

    house: HouseState | None = coordinator.data.get("house")  # type: ignore[assignment]
    if house is None:
        return None

    for suggestion in house.suggestions:
        if suggestion.id == suggestion_id:
            return suggestion

    return None


async def _auto_apply_suggestions(
    hass: HomeAssistant,
    coordinator: SmartClimateCoordinator,
    suggestions: list[Suggestion],
) -> None:
    """Auto-apply suggestions that meet the confidence threshold."""
    for suggestion in suggestions:
        if (
            suggestion.status == SUGGESTION_PENDING
            and suggestion.confidence >= AUTO_APPLY_CONFIDENCE_THRESHOLD
            and suggestion.action_type in SAFE_SERVICE_MAP
        ):
            _LOGGER.info(
                "Auto-applying suggestion '%s' (confidence=%.2f)",
                suggestion.title,
                suggestion.confidence,
            )
            await approve_suggestion(coordinator, suggestion.id)


def _get_climate_entity_for_room(
    hass: HomeAssistant, room_slug: str | None
) -> str | None:
    """Resolve a room slug to its climate entity ID.

    Searches the coordinator data stored in hass.data for the matching
    room configuration.
    """
    if room_slug is None:
        return None

    domain_data = hass.data.get(DOMAIN)
    if not domain_data:
        return None

    # Iterate over all config entries for this domain
    for entry_data in domain_data.values():
        if not hasattr(entry_data, "data") or not entry_data.data:
            continue
        rooms = entry_data.data.get("rooms", {})
        for slug, room_state in rooms.items():
            if slug == room_slug:
                config = getattr(room_state, "config", None)
                if config is not None:
                    return getattr(config, "climate_entity", None)

    return None


async def _execute_set_temperature(
    hass: HomeAssistant, room_slug: str | None, action_data: dict
) -> bool:
    """Execute a set_temperature action via climate.set_temperature."""
    temperature = action_data.get("temperature")
    if temperature is None:
        _LOGGER.warning("set_temperature action missing 'temperature' field")
        return False

    entity_id = _get_climate_entity_for_room(hass, room_slug)
    if entity_id is None:
        _LOGGER.warning(
            "Cannot resolve climate entity for room '%s'", room_slug
        )
        return False

    service_data: dict[str, Any] = {
        "entity_id": entity_id,
        "temperature": temperature,
    }

    try:
        await hass.services.async_call(
            "climate", "set_temperature", service_data, blocking=True
        )
        _LOGGER.info(
            "Set temperature to %s on %s (room=%s)",
            temperature,
            entity_id,
            room_slug,
        )
        return True
    except Exception:
        _LOGGER.exception(
            "Failed to call climate.set_temperature for %s", entity_id
        )
        return False


async def _execute_set_mode(
    hass: HomeAssistant, room_slug: str | None, action_data: dict
) -> bool:
    """Execute a set_mode action via climate.set_hvac_mode."""
    mode = action_data.get("mode")
    if not mode:
        _LOGGER.warning("set_mode action missing 'mode' field")
        return False

    entity_id = _get_climate_entity_for_room(hass, room_slug)
    if entity_id is None:
        _LOGGER.warning(
            "Cannot resolve climate entity for room '%s'", room_slug
        )
        return False

    service_data: dict[str, Any] = {
        "entity_id": entity_id,
        "hvac_mode": mode,
    }

    try:
        await hass.services.async_call(
            "climate", "set_hvac_mode", service_data, blocking=True
        )
        _LOGGER.info(
            "Set HVAC mode to '%s' on %s (room=%s)",
            mode,
            entity_id,
            room_slug,
        )
        return True
    except Exception:
        _LOGGER.exception(
            "Failed to call climate.set_hvac_mode for %s", entity_id
        )
        return False


async def _execute_vent_adjustment(
    hass: HomeAssistant, room_slug: str | None, action_data: dict
) -> bool:
    """Execute a vent_adjustment action.

    Attempts to set a cover position (most smart vents expose themselves as
    cover entities) or a number entity.
    """
    position = action_data.get("vent_position")
    if position is None:
        _LOGGER.warning("vent_adjustment action missing 'vent_position' field")
        return False

    if room_slug is None:
        _LOGGER.warning("vent_adjustment requires a room slug")
        return False

    # Find vent entities from the coordinator data
    domain_data = hass.data.get(DOMAIN)
    if not domain_data:
        return False

    vent_entities: list[str] = []
    for entry_data in domain_data.values():
        if not hasattr(entry_data, "data") or not entry_data.data:
            continue
        rooms = entry_data.data.get("rooms", {})
        for slug, room_state in rooms.items():
            if slug == room_slug:
                config = getattr(room_state, "config", None)
                if config is not None:
                    vent_entities = getattr(config, "vent_entities", [])
                break

    if not vent_entities:
        _LOGGER.info(
            "No vent entities configured for room '%s'; vent_adjustment is informational",
            room_slug,
        )
        return True

    success = True
    for entity_id in vent_entities:
        try:
            domain = entity_id.split(".")[0]
            if domain == "cover":
                await hass.services.async_call(
                    "cover",
                    "set_cover_position",
                    {"entity_id": entity_id, "position": position},
                    blocking=True,
                )
            elif domain == "number":
                await hass.services.async_call(
                    "number",
                    "set_value",
                    {"entity_id": entity_id, "value": position},
                    blocking=True,
                )
            else:
                _LOGGER.debug(
                    "Unsupported vent entity domain '%s' for %s",
                    domain,
                    entity_id,
                )
                continue

            _LOGGER.info(
                "Set vent position to %d on %s (room=%s)",
                position,
                entity_id,
                room_slug,
            )
        except Exception:
            _LOGGER.exception(
                "Failed to set vent position on %s", entity_id
            )
            success = False

    return success
