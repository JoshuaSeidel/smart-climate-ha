"""Binary sensor platform for the Smart Climate integration."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    COMFORT_POOR,
    DOMAIN,
    ENTITY_PREFIX,
    SUGGESTION_PENDING,
)
from .entity import SmartClimateEntity

_LOGGER = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Platform setup
# ---------------------------------------------------------------------------


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Smart Climate binary sensor entities from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[BinarySensorEntity] = []

    # --- Per-room binary sensors -------------------------------------------
    rooms = coordinator.data.get("rooms", {})
    for room_slug in rooms:
        entities.extend(
            [
                SmartClimateOccupancySensor(coordinator, room_slug),
                SmartClimateWindowSensor(coordinator, room_slug),
                SmartClimateComfortAlertSensor(coordinator, room_slug),
                SmartClimateAuxiliaryActiveSensor(coordinator, room_slug),
            ]
        )

    # --- Whole-house binary sensors ----------------------------------------
    entities.extend(
        [
            SmartClimateSuggestionsPendingSensor(coordinator),
        ]
    )

    async_add_entities(entities)


# ===========================================================================
# Per-Room Binary Sensor Classes
# ===========================================================================


class SmartClimateOccupancySensor(SmartClimateEntity, BinarySensorEntity):
    """Occupancy state for a room."""

    _attr_device_class = BinarySensorDeviceClass.OCCUPANCY
    _attr_icon = "mdi:motion-sensor"

    def __init__(self, coordinator, room_slug: str) -> None:
        """Initialize the occupancy sensor."""
        super().__init__(
            coordinator,
            entity_key="occupied",
            name="Occupied",
            room_slug=room_slug,
        )

    @property
    def entity_id(self) -> str:
        """Return the entity_id."""
        return f"binary_sensor.{ENTITY_PREFIX}_{self._room_slug}_occupied"

    @entity_id.setter
    def entity_id(self, value: str) -> None:
        """Allow HA to set entity_id."""
        self._attr_entity_id = value

    @property
    def is_on(self) -> bool | None:
        """Return true if the room is occupied."""
        room_state = self.coordinator.data.get("rooms", {}).get(self._room_slug)
        if room_state is None:
            return None
        return room_state.occupied


class SmartClimateWindowSensor(SmartClimateEntity, BinarySensorEntity):
    """Window open state for a room."""

    _attr_device_class = BinarySensorDeviceClass.WINDOW
    _attr_icon = "mdi:window-open-variant"

    def __init__(self, coordinator, room_slug: str) -> None:
        """Initialize the window sensor."""
        super().__init__(
            coordinator,
            entity_key="window_open",
            name="Window Open",
            room_slug=room_slug,
        )

    @property
    def entity_id(self) -> str:
        """Return the entity_id."""
        return f"binary_sensor.{ENTITY_PREFIX}_{self._room_slug}_window_open"

    @entity_id.setter
    def entity_id(self, value: str) -> None:
        """Allow HA to set entity_id."""
        self._attr_entity_id = value

    @property
    def is_on(self) -> bool | None:
        """Return true if a window is open."""
        room_state = self.coordinator.data.get("rooms", {}).get(self._room_slug)
        if room_state is None:
            return None
        return room_state.window_open


class SmartClimateComfortAlertSensor(SmartClimateEntity, BinarySensorEntity):
    """Comfort alert for a room (on when comfort score is poor)."""

    _attr_icon = "mdi:alert-circle-outline"

    def __init__(self, coordinator, room_slug: str) -> None:
        """Initialize the comfort alert sensor."""
        super().__init__(
            coordinator,
            entity_key="comfort_alert",
            name="Comfort Alert",
            room_slug=room_slug,
        )

    @property
    def entity_id(self) -> str:
        """Return the entity_id."""
        return f"binary_sensor.{ENTITY_PREFIX}_{self._room_slug}_comfort_alert"

    @entity_id.setter
    def entity_id(self, value: str) -> None:
        """Allow HA to set entity_id."""
        self._attr_entity_id = value

    @property
    def is_on(self) -> bool | None:
        """Return true if comfort score is below the poor threshold."""
        room_state = self.coordinator.data.get("rooms", {}).get(self._room_slug)
        if room_state is None:
            return None
        return room_state.comfort_score < COMFORT_POOR


class SmartClimateAuxiliaryActiveSensor(SmartClimateEntity, BinarySensorEntity):
    """Auxiliary heating/cooling active state for a room."""

    _attr_icon = "mdi:radiator"

    def __init__(self, coordinator, room_slug: str) -> None:
        """Initialize the auxiliary active sensor."""
        super().__init__(
            coordinator,
            entity_key="auxiliary_active",
            name="Auxiliary Active",
            room_slug=room_slug,
        )

    @property
    def entity_id(self) -> str:
        """Return the entity_id."""
        return f"binary_sensor.{ENTITY_PREFIX}_{self._room_slug}_auxiliary_active"

    @entity_id.setter
    def entity_id(self, value: str) -> None:
        """Allow HA to set entity_id."""
        self._attr_entity_id = value

    @property
    def is_on(self) -> bool | None:
        """Return true if auxiliary devices are active."""
        room_state = self.coordinator.data.get("rooms", {}).get(self._room_slug)
        if room_state is None:
            return None
        return room_state.auxiliary_active

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes about auxiliary device state."""
        room_state = self.coordinator.data.get("rooms", {}).get(self._room_slug)
        if room_state is None:
            return {}

        attrs: dict[str, Any] = {
            "active_devices": room_state.auxiliary_devices_on,
            "reason": room_state.auxiliary_reason,
            "runtime_minutes": round(room_state.auxiliary_runtime_minutes, 1),
        }

        # Calculate auto-shutoff time if auxiliary is currently active
        if room_state.auxiliary_active and room_state.auxiliary_runtime_minutes > 0:
            # Estimate auto_shutoff_at from the configured max runtime
            from .const import DEFAULT_AUXILIARY_MAX_RUNTIME

            remaining = DEFAULT_AUXILIARY_MAX_RUNTIME - room_state.auxiliary_runtime_minutes
            if remaining > 0:
                attrs["auto_shutoff_at"] = (
                    datetime.now() + timedelta(minutes=remaining)
                ).isoformat()

        return attrs


# ===========================================================================
# Whole-House Binary Sensor Classes
# ===========================================================================


class SmartClimateSuggestionsPendingSensor(SmartClimateEntity, BinarySensorEntity):
    """Indicates whether there are pending AI suggestions."""

    _attr_icon = "mdi:lightbulb-on-outline"

    def __init__(self, coordinator) -> None:
        """Initialize the suggestions pending sensor."""
        super().__init__(
            coordinator,
            entity_key="suggestions_pending",
            name="Suggestions Pending",
        )

    @property
    def entity_id(self) -> str:
        """Return the entity_id."""
        return f"binary_sensor.{ENTITY_PREFIX}_suggestions_pending"

    @entity_id.setter
    def entity_id(self, value: str) -> None:
        """Allow HA to set entity_id."""
        self._attr_entity_id = value

    @property
    def is_on(self) -> bool:
        """Return true if there are pending suggestions."""
        house_state = self.coordinator.data.get("house")
        if house_state is None:
            return False
        return any(
            s.status == SUGGESTION_PENDING for s in house_state.suggestions
        )
