"""HA recorder/statistics query helpers for Smart Climate."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


async def async_get_sensor_history(
    hass: HomeAssistant,
    entity_id: str,
    hours: int = 24,
) -> list[tuple[datetime, float]]:
    """Get historical state values for a sensor entity.

    Returns list of (timestamp, value) tuples.
    """
    from homeassistant.components.recorder import get_instance
    from homeassistant.components.recorder.history import get_significant_states

    try:
        start_time = datetime.now() - timedelta(hours=hours)
        instance = get_instance(hass)

        states = await instance.async_add_executor_job(
            get_significant_states,
            hass,
            start_time,
            None,
            [entity_id],
        )

        result: list[tuple[datetime, float]] = []
        for state in states.get(entity_id, []):
            try:
                value = float(state.state)
                result.append((state.last_updated, value))
            except (ValueError, TypeError):
                continue

        return result
    except Exception:
        _LOGGER.debug("Could not fetch history for %s", entity_id, exc_info=True)
        return []


async def async_get_runtime_stats(
    hass: HomeAssistant,
    climate_entity: str,
    hours: int = 24,
) -> dict:
    """Get HVAC runtime statistics from state history.

    Returns dict with runtime_minutes, cycles, states breakdown.
    """
    from homeassistant.components.recorder import get_instance
    from homeassistant.components.recorder.history import get_significant_states

    try:
        start_time = datetime.now() - timedelta(hours=hours)
        instance = get_instance(hass)

        states = await instance.async_add_executor_job(
            get_significant_states,
            hass,
            start_time,
            None,
            [climate_entity],
        )

        runtime_minutes = 0.0
        cycles = 0
        last_state = None
        last_time = None
        active_states = {"heating", "cooling"}

        for state in states.get(climate_entity, []):
            hvac_action = state.attributes.get("hvac_action", "idle")
            current_time = state.last_updated

            if last_state in active_states and last_time:
                duration = (current_time - last_time).total_seconds() / 60
                runtime_minutes += duration

            if hvac_action in active_states and last_state not in active_states:
                cycles += 1

            last_state = hvac_action
            last_time = current_time

        # Account for current state if still active
        if last_state in active_states and last_time:
            duration = (datetime.now() - last_time.replace(tzinfo=None)).total_seconds() / 60
            runtime_minutes += max(0, duration)

        return {
            "runtime_minutes": round(runtime_minutes, 1),
            "cycles": cycles,
        }
    except Exception:
        _LOGGER.debug(
            "Could not fetch runtime stats for %s", climate_entity, exc_info=True
        )
        return {"runtime_minutes": 0.0, "cycles": 0}
