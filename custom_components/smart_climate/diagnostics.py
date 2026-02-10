"""Diagnostics support for Smart Climate."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_AI_API_KEY, DOMAIN

REDACT_KEYS = {CONF_AI_API_KEY, "api_key"}


def _redact_data(data: dict) -> dict:
    """Redact sensitive data from diagnostics."""
    redacted = {}
    for key, value in data.items():
        if key in REDACT_KEYS:
            redacted[key] = "**REDACTED**"
        elif isinstance(value, dict):
            redacted[key] = _redact_data(value)
        elif isinstance(value, list):
            redacted[key] = [
                _redact_data(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            redacted[key] = value
    return redacted


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    data = coordinator.data

    rooms_diag = {}
    for slug, room_state in data.get("rooms", {}).items():
        rooms_diag[slug] = {
            "name": room_state.config.name,
            "climate_entity": room_state.config.climate_entity,
            "temp_sensors": room_state.config.temp_sensors,
            "humidity_sensors": room_state.config.humidity_sensors,
            "presence_sensors": room_state.config.presence_sensors,
            "door_window_sensors": room_state.config.door_window_sensors,
            "vent_entities": room_state.config.vent_entities,
            "auxiliary_entities": room_state.config.auxiliary_entities,
            "priority": room_state.config.priority,
            "temperature": room_state.temperature,
            "humidity": room_state.humidity,
            "occupied": room_state.occupied,
            "window_open": room_state.window_open,
            "comfort_score": room_state.comfort_score,
            "efficiency_score": room_state.efficiency_score,
            "hvac_action": room_state.hvac_action.value,
            "hvac_runtime_today": room_state.hvac_runtime_today,
            "hvac_cycles_today": room_state.hvac_cycles_today,
            "current_target": room_state.current_target,
            "smart_target": room_state.smart_target,
            "follow_me_active": room_state.follow_me_active,
            "active_schedule": room_state.active_schedule,
            "auxiliary_active": room_state.auxiliary_active,
            "temp_trend": room_state.temp_trend,
        }

    house = data.get("house")
    house_diag = {}
    if house:
        house_diag = {
            "comfort_score": house.comfort_score,
            "efficiency_score": house.efficiency_score,
            "total_hvac_runtime": house.total_hvac_runtime,
            "heating_degree_days": house.heating_degree_days,
            "cooling_degree_days": house.cooling_degree_days,
            "follow_me_target": house.follow_me_target,
            "active_schedule": house.active_schedule,
            "outdoor_temperature": house.outdoor_temperature,
            "last_analysis_time": (
                house.last_analysis_time.isoformat()
                if house.last_analysis_time
                else None
            ),
            "suggestion_count": len(house.suggestions),
        }

    return {
        "config_entry": _redact_data(dict(entry.data)),
        "rooms": rooms_diag,
        "house": house_diag,
        "coordinator_last_update": (
            coordinator.last_update_success_time.isoformat()
            if coordinator.last_update_success_time
            else None
        ),
    }
