"""Service handlers for Smart Climate."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN,
    SERVICE_ACTIVATE_SCHEDULE,
    SERVICE_ADD_SCHEDULE,
    SERVICE_APPROVE_ALL,
    SERVICE_APPROVE_SUGGESTION,
    SERVICE_DEACTIVATE_SCHEDULE,
    SERVICE_FORCE_FOLLOW_ME,
    SERVICE_REJECT_ALL,
    SERVICE_REJECT_SUGGESTION,
    SERVICE_REMOVE_SCHEDULE,
    SERVICE_RESET_STATISTICS,
    SERVICE_SET_AUXILIARY_MODE,
    SERVICE_SET_ROOM_PRIORITY,
    SERVICE_TRIGGER_ANALYSIS,
    SUGGESTION_PENDING,
)
from .models import Schedule, slugify

if TYPE_CHECKING:
    from .coordinator import SmartClimateCoordinator

_LOGGER = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Voluptuous schemas for service calls
# ---------------------------------------------------------------------------

SCHEMA_TRIGGER_ANALYSIS = vol.Schema(
    {
        vol.Optional("scope", default="all"): vol.In(["all", "room"]),
        vol.Optional("room"): cv.string,
    }
)

SCHEMA_APPROVE_SUGGESTION = vol.Schema(
    {
        vol.Required("suggestion_id"): cv.string,
    }
)

SCHEMA_REJECT_SUGGESTION = vol.Schema(
    {
        vol.Required("suggestion_id"): cv.string,
        vol.Optional("reason"): cv.string,
    }
)

SCHEMA_SET_ROOM_PRIORITY = vol.Schema(
    {
        vol.Required("room"): cv.string,
        vol.Required("priority"): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=10)
        ),
    }
)

SCHEMA_FORCE_FOLLOW_ME = vol.Schema(
    {
        vol.Required("room"): cv.string,
    }
)

SCHEMA_ADD_SCHEDULE = vol.Schema(
    {
        vol.Required("name"): cv.string,
        vol.Required("rooms"): cv.string,
        vol.Required("days"): cv.string,
        vol.Required("start_time"): cv.string,
        vol.Required("end_time"): cv.string,
        vol.Required("target_temp"): vol.Coerce(float),
        vol.Optional("hvac_mode"): vol.In(["heat", "cool", "auto", "off"]),
        vol.Optional("use_auxiliary", default=False): cv.boolean,
        vol.Optional("priority", default=5): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=10)
        ),
    }
)

SCHEMA_REMOVE_SCHEDULE = vol.Schema(
    {
        vol.Required("name"): cv.string,
    }
)

SCHEMA_ACTIVATE_SCHEDULE = vol.Schema(
    {
        vol.Required("name"): cv.string,
    }
)

SCHEMA_DEACTIVATE_SCHEDULE = vol.Schema(
    {
        vol.Required("name"): cv.string,
    }
)

SCHEMA_SET_AUXILIARY_MODE = vol.Schema(
    {
        vol.Required("room"): cv.string,
        vol.Required("enabled"): cv.boolean,
    }
)


# ---------------------------------------------------------------------------
# Coordinator lookup helper
# ---------------------------------------------------------------------------


def _get_coordinator(hass: HomeAssistant) -> SmartClimateCoordinator | None:
    """Return the first SmartClimateCoordinator from hass.data."""
    domain_data = hass.data.get(DOMAIN)
    if not domain_data:
        return None
    for coordinator in domain_data.values():
        return coordinator  # type: ignore[return-value]
    return None


# ---------------------------------------------------------------------------
# Service handler functions
# ---------------------------------------------------------------------------


async def _handle_trigger_analysis(call: ServiceCall) -> None:
    """Handle the trigger_analysis service call."""
    coordinator = _get_coordinator(call.hass)
    if coordinator is None:
        _LOGGER.error("No Smart Climate coordinator found")
        return

    scope = call.data.get("scope", "all")
    room = call.data.get("room")

    _LOGGER.info("Service trigger_analysis called (scope=%s, room=%s)", scope, room)
    await coordinator.async_trigger_analysis()


async def _handle_approve_suggestion(call: ServiceCall) -> None:
    """Handle the approve_suggestion service call."""
    from .ai.suggestions import approve_suggestion

    coordinator = _get_coordinator(call.hass)
    if coordinator is None:
        _LOGGER.error("No Smart Climate coordinator found")
        return

    suggestion_id = call.data.get("suggestion_id")
    _LOGGER.info("Service approve_suggestion called (id=%s)", suggestion_id)
    await approve_suggestion(coordinator, suggestion_id)


async def _handle_reject_suggestion(call: ServiceCall) -> None:
    """Handle the reject_suggestion service call."""
    from .ai.suggestions import reject_suggestion

    coordinator = _get_coordinator(call.hass)
    if coordinator is None:
        _LOGGER.error("No Smart Climate coordinator found")
        return

    suggestion_id = call.data.get("suggestion_id")
    reason = call.data.get("reason", "")
    _LOGGER.info("Service reject_suggestion called (id=%s, reason=%s)", suggestion_id, reason)
    await reject_suggestion(coordinator, suggestion_id, reason)


async def _handle_approve_all_suggestions(call: ServiceCall) -> None:
    """Handle the approve_all_suggestions service call."""
    from .ai.suggestions import approve_suggestion

    coordinator = _get_coordinator(call.hass)
    if coordinator is None:
        _LOGGER.error("No Smart Climate coordinator found")
        return

    if not coordinator.data:
        _LOGGER.warning("No coordinator data available")
        return

    house = coordinator.data.get("house")
    if house is None:
        _LOGGER.warning("No house state available")
        return

    pending = [s for s in house.suggestions if s.status == SUGGESTION_PENDING]
    _LOGGER.info("Service approve_all_suggestions called (%d pending)", len(pending))

    for suggestion in pending:
        await approve_suggestion(coordinator, suggestion.id)


async def _handle_reject_all_suggestions(call: ServiceCall) -> None:
    """Handle the reject_all_suggestions service call."""
    from .ai.suggestions import reject_suggestion

    coordinator = _get_coordinator(call.hass)
    if coordinator is None:
        _LOGGER.error("No Smart Climate coordinator found")
        return

    if not coordinator.data:
        _LOGGER.warning("No coordinator data available")
        return

    house = coordinator.data.get("house")
    if house is None:
        _LOGGER.warning("No house state available")
        return

    pending = [s for s in house.suggestions if s.status == SUGGESTION_PENDING]
    _LOGGER.info("Service reject_all_suggestions called (%d pending)", len(pending))

    for suggestion in pending:
        await reject_suggestion(coordinator, suggestion.id, "Bulk rejected by user")


async def _handle_set_room_priority(call: ServiceCall) -> None:
    """Handle the set_room_priority service call."""
    coordinator = _get_coordinator(call.hass)
    if coordinator is None:
        _LOGGER.error("No Smart Climate coordinator found")
        return

    room_slug = call.data.get("room")
    priority = call.data.get("priority")

    room_config = coordinator.room_configs.get(room_slug)
    if room_config is None:
        _LOGGER.error("Room '%s' not found in configuration", room_slug)
        return

    room_config.priority = priority
    _LOGGER.info("Set room '%s' priority to %d", room_slug, priority)
    await coordinator.async_request_refresh()


async def _handle_force_follow_me(call: ServiceCall) -> None:
    """Handle the force_follow_me service call."""
    coordinator = _get_coordinator(call.hass)
    if coordinator is None:
        _LOGGER.error("No Smart Climate coordinator found")
        return

    room_slug = call.data.get("room")

    if room_slug not in coordinator.room_configs:
        _LOGGER.error("Room '%s' not found in configuration", room_slug)
        return

    coordinator.forced_follow_me_target = room_slug
    _LOGGER.info("Forced follow-me target set to room '%s'", room_slug)
    await coordinator.async_request_refresh()


async def _handle_reset_statistics(call: ServiceCall) -> None:
    """Handle the reset_statistics service call."""
    coordinator = _get_coordinator(call.hass)
    if coordinator is None:
        _LOGGER.error("No Smart Climate coordinator found")
        return

    if not coordinator.data:
        _LOGGER.warning("No coordinator data available")
        return

    rooms = coordinator.data.get("rooms", {})
    for slug, room_state in rooms.items():
        room_state.hvac_runtime_today = 0.0
        room_state.hvac_cycles_today = 0
        room_state.auxiliary_runtime_minutes = 0.0
        _LOGGER.debug("Reset statistics for room '%s'", slug)

    house = coordinator.data.get("house")
    if house is not None:
        house.total_hvac_runtime = 0.0

    _LOGGER.info("Service reset_statistics: all room and house counters zeroed")
    await coordinator.async_request_refresh()


async def _handle_add_schedule(call: ServiceCall) -> None:
    """Handle the add_schedule service call."""
    coordinator = _get_coordinator(call.hass)
    if coordinator is None:
        _LOGGER.error("No Smart Climate coordinator found")
        return

    name = call.data.get("name")
    rooms_raw = call.data.get("rooms", "__all__")
    days_raw = call.data.get("days", "0,1,2,3,4,5,6")
    start_time = call.data.get("start_time")
    end_time = call.data.get("end_time")
    target_temp = call.data.get("target_temp")
    hvac_mode = call.data.get("hvac_mode")
    use_auxiliary = call.data.get("use_auxiliary", False)
    priority = call.data.get("priority", 5)

    # Parse rooms: comma-separated slugs or "__all__"
    if rooms_raw == "__all__":
        rooms = ["__all__"]
    else:
        rooms = [r.strip() for r in rooms_raw.split(",") if r.strip()]

    # Parse days: comma-separated integers
    try:
        days = [int(d.strip()) for d in days_raw.split(",") if d.strip()]
    except ValueError:
        _LOGGER.error("Invalid days format: '%s'. Use comma-separated 0-6.", days_raw)
        return

    schedule = Schedule(
        name=name,
        slug=slugify(name),
        rooms=rooms,
        days=days,
        start_time=start_time,
        end_time=end_time,
        target_temperature=target_temp,
        hvac_mode=hvac_mode,
        use_auxiliary=use_auxiliary,
        priority=priority,
        enabled=True,
    )

    # Check for duplicate name
    for existing in coordinator.schedules:
        if existing.slug == schedule.slug:
            _LOGGER.warning(
                "Schedule '%s' already exists; replacing it", name
            )
            coordinator.schedules.remove(existing)
            break

    coordinator.schedules.append(schedule)
    _LOGGER.info("Added schedule '%s' (slug=%s)", name, schedule.slug)
    await coordinator.async_request_refresh()


async def _handle_remove_schedule(call: ServiceCall) -> None:
    """Handle the remove_schedule service call."""
    coordinator = _get_coordinator(call.hass)
    if coordinator is None:
        _LOGGER.error("No Smart Climate coordinator found")
        return

    name = call.data.get("name")
    target_slug = slugify(name)

    for schedule in coordinator.schedules:
        if schedule.slug == target_slug:
            coordinator.schedules.remove(schedule)
            _LOGGER.info("Removed schedule '%s'", name)
            await coordinator.async_request_refresh()
            return

    _LOGGER.warning("Schedule '%s' not found", name)


async def _handle_activate_schedule(call: ServiceCall) -> None:
    """Handle the activate_schedule service call (manual override)."""
    coordinator = _get_coordinator(call.hass)
    if coordinator is None:
        _LOGGER.error("No Smart Climate coordinator found")
        return

    name = call.data.get("name")
    target_slug = slugify(name)

    for schedule in coordinator.schedules:
        if schedule.slug == target_slug:
            schedule.enabled = True
            # Mark as a manual override so the schedule engine picks it up
            # regardless of its time window
            schedule._manual_override = True  # type: ignore[attr-defined]
            _LOGGER.info("Manually activated schedule '%s'", name)
            await coordinator.async_request_refresh()
            return

    _LOGGER.warning("Schedule '%s' not found", name)


async def _handle_deactivate_schedule(call: ServiceCall) -> None:
    """Handle the deactivate_schedule service call."""
    coordinator = _get_coordinator(call.hass)
    if coordinator is None:
        _LOGGER.error("No Smart Climate coordinator found")
        return

    name = call.data.get("name")
    target_slug = slugify(name)

    for schedule in coordinator.schedules:
        if schedule.slug == target_slug:
            # Clear manual override; the schedule returns to time-based activation
            if hasattr(schedule, "_manual_override"):
                del schedule._manual_override  # type: ignore[attr-defined]
            schedule.enabled = False
            _LOGGER.info("Deactivated schedule '%s'", name)
            await coordinator.async_request_refresh()
            return

    _LOGGER.warning("Schedule '%s' not found", name)


async def _handle_set_auxiliary_mode(call: ServiceCall) -> None:
    """Handle the set_auxiliary_mode service call."""
    coordinator = _get_coordinator(call.hass)
    if coordinator is None:
        _LOGGER.error("No Smart Climate coordinator found")
        return

    room_slug = call.data.get("room")
    enabled = call.data.get("enabled")

    if room_slug not in coordinator.room_configs:
        _LOGGER.error("Room '%s' not found in configuration", room_slug)
        return

    if not coordinator.data:
        _LOGGER.warning("No coordinator data available")
        return

    rooms = coordinator.data.get("rooms", {})
    room_state = rooms.get(room_slug)
    if room_state is None:
        _LOGGER.warning("Room state for '%s' not available", room_slug)
        return

    room_state.auxiliary_active = enabled
    if not enabled:
        # Turn off any active auxiliary devices for this room
        room_state.auxiliary_devices_on.clear()
        room_state.auxiliary_reason = ""

    _LOGGER.info(
        "Set auxiliary mode for room '%s' to %s",
        room_slug,
        "enabled" if enabled else "disabled",
    )
    await coordinator.async_request_refresh()


# ---------------------------------------------------------------------------
# Registration / unregistration
# ---------------------------------------------------------------------------


async def async_setup_services(
    hass: HomeAssistant, coordinator: SmartClimateCoordinator
) -> None:
    """Register all Smart Climate services with Home Assistant."""

    hass.services.async_register(
        DOMAIN,
        SERVICE_TRIGGER_ANALYSIS,
        _handle_trigger_analysis,
        schema=SCHEMA_TRIGGER_ANALYSIS,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_APPROVE_SUGGESTION,
        _handle_approve_suggestion,
        schema=SCHEMA_APPROVE_SUGGESTION,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_REJECT_SUGGESTION,
        _handle_reject_suggestion,
        schema=SCHEMA_REJECT_SUGGESTION,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_APPROVE_ALL,
        _handle_approve_all_suggestions,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_REJECT_ALL,
        _handle_reject_all_suggestions,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_ROOM_PRIORITY,
        _handle_set_room_priority,
        schema=SCHEMA_SET_ROOM_PRIORITY,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_FORCE_FOLLOW_ME,
        _handle_force_follow_me,
        schema=SCHEMA_FORCE_FOLLOW_ME,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_RESET_STATISTICS,
        _handle_reset_statistics,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_ADD_SCHEDULE,
        _handle_add_schedule,
        schema=SCHEMA_ADD_SCHEDULE,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_REMOVE_SCHEDULE,
        _handle_remove_schedule,
        schema=SCHEMA_REMOVE_SCHEDULE,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_ACTIVATE_SCHEDULE,
        _handle_activate_schedule,
        schema=SCHEMA_ACTIVATE_SCHEDULE,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_DEACTIVATE_SCHEDULE,
        _handle_deactivate_schedule,
        schema=SCHEMA_DEACTIVATE_SCHEDULE,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_AUXILIARY_MODE,
        _handle_set_auxiliary_mode,
        schema=SCHEMA_SET_AUXILIARY_MODE,
    )

    _LOGGER.debug("Registered %d Smart Climate services", 13)


async def async_unload_services(hass: HomeAssistant) -> None:
    """Unregister all Smart Climate services."""
    # Only unregister if no other config entries remain
    if hass.data.get(DOMAIN):
        return

    for service_name in (
        SERVICE_TRIGGER_ANALYSIS,
        SERVICE_APPROVE_SUGGESTION,
        SERVICE_REJECT_SUGGESTION,
        SERVICE_APPROVE_ALL,
        SERVICE_REJECT_ALL,
        SERVICE_SET_ROOM_PRIORITY,
        SERVICE_FORCE_FOLLOW_ME,
        SERVICE_RESET_STATISTICS,
        SERVICE_ADD_SCHEDULE,
        SERVICE_REMOVE_SCHEDULE,
        SERVICE_ACTIVATE_SCHEDULE,
        SERVICE_DEACTIVATE_SCHEDULE,
        SERVICE_SET_AUXILIARY_MODE,
    ):
        hass.services.async_remove(DOMAIN, service_name)

    _LOGGER.debug("Unregistered all Smart Climate services")
