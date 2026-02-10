"""Auxiliary device control for Smart Climate."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

from homeassistant.core import HomeAssistant

from ..const import (
    DEFAULT_AUXILIARY_DELAY_MINUTES,
    DEFAULT_AUXILIARY_THRESHOLD,
)
from ..models import AuxiliaryDeviceState, RoomState

_LOGGER = logging.getLogger(__name__)

# Hysteresis: disengage when within this many degrees of target
DISENGAGE_THRESHOLD = 1.0
# Fan speed: percentage per degree of deviation
FAN_SPEED_PER_DEGREE = 25


def should_engage_auxiliary(
    room: RoomState,
    target_temp: float,
    threshold: float = DEFAULT_AUXILIARY_THRESHOLD,
    delay_minutes: int = DEFAULT_AUXILIARY_DELAY_MINUTES,
) -> bool:
    """Determine if auxiliary devices should be engaged for a room.

    Conditions:
    1. Room is > threshold degrees from target
    2. HVAC has been running for > delay_minutes
    3. Temperature trend shows HVAC is losing or not gaining
    """
    if room.temperature is None:
        return False

    temp_deviation = abs(room.temperature - target_temp)

    # Condition 1: temperature deviation exceeds threshold
    if temp_deviation <= threshold:
        return False

    # Condition 2: HVAC has been running long enough
    if room.hvac_state_change_time is None:
        return False

    hvac_running_time = datetime.now() - room.hvac_state_change_time
    is_hvac_active = room.hvac_action.value in ("heating", "cooling")

    if not is_hvac_active:
        return False

    if hvac_running_time < timedelta(minutes=delay_minutes):
        return False

    # Condition 3: trend shows HVAC isn't keeping up
    # Positive trend = warming, negative = cooling
    if room.hvac_action.value == "heating" and room.temp_trend >= 0.5:
        # Heating and gaining temperature — HVAC is working, no auxiliary needed
        return False
    if room.hvac_action.value == "cooling" and room.temp_trend <= -0.5:
        # Cooling and temperature dropping — HVAC is working
        return False

    return True


def should_disengage_auxiliary(
    room: RoomState,
    target_temp: float,
    aux_state: AuxiliaryDeviceState,
) -> bool:
    """Determine if auxiliary devices should be disengaged.

    Disengage when:
    - Room is within DISENGAGE_THRESHOLD of target
    - Max runtime exceeded (safety)
    """
    if room.temperature is None:
        return True

    # Safety: max runtime exceeded
    if aux_state.is_on and aux_state.runtime_minutes >= aux_state.max_runtime:
        _LOGGER.warning(
            "Auxiliary device %s exceeded max runtime of %d minutes",
            aux_state.entity_id,
            aux_state.max_runtime,
        )
        return True

    # Within hysteresis band of target
    temp_deviation = abs(room.temperature - target_temp)
    if temp_deviation <= DISENGAGE_THRESHOLD:
        return True

    return False


def calculate_fan_speed(temp_deviation: float) -> int:
    """Calculate fan speed as percentage based on temperature deviation."""
    speed = int(abs(temp_deviation) * FAN_SPEED_PER_DEGREE)
    return max(0, min(100, speed))


async def async_engage_auxiliary(
    hass: HomeAssistant,
    entity_id: str,
    target_temp: float,
    temp_deviation: float,
) -> None:
    """Turn on / engage an auxiliary device."""
    domain = entity_id.split(".")[0]

    try:
        if domain == "switch":
            await hass.services.async_call(
                "switch", "turn_on", {"entity_id": entity_id}
            )
        elif domain == "climate":
            await hass.services.async_call(
                "climate",
                "set_temperature",
                {"entity_id": entity_id, "temperature": target_temp},
            )
            await hass.services.async_call(
                "climate", "turn_on", {"entity_id": entity_id}
            )
        elif domain == "fan":
            speed = calculate_fan_speed(temp_deviation)
            await hass.services.async_call(
                "fan", "turn_on", {"entity_id": entity_id, "percentage": speed}
            )
        _LOGGER.info("Engaged auxiliary device %s", entity_id)
    except Exception:
        _LOGGER.exception("Failed to engage auxiliary device %s", entity_id)


async def async_disengage_auxiliary(
    hass: HomeAssistant,
    entity_id: str,
) -> None:
    """Turn off / disengage an auxiliary device."""
    domain = entity_id.split(".")[0]

    try:
        if domain == "switch":
            await hass.services.async_call(
                "switch", "turn_off", {"entity_id": entity_id}
            )
        elif domain == "climate":
            await hass.services.async_call(
                "climate", "turn_off", {"entity_id": entity_id}
            )
        elif domain == "fan":
            await hass.services.async_call(
                "fan", "turn_off", {"entity_id": entity_id}
            )
        _LOGGER.info("Disengaged auxiliary device %s", entity_id)
    except Exception:
        _LOGGER.exception("Failed to disengage auxiliary device %s", entity_id)
