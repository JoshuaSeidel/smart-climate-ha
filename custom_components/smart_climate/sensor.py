"""Sensor platform for the Smart Climate integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTemperature, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_TEMP_UNIT,
    DOMAIN,
    ENTITY_PREFIX,
    SUGGESTION_PENDING,
)
from .entity import SmartClimateEntity

_LOGGER = logging.getLogger(__name__)

# Comfort score labels
COMFORT_LABELS = {
    90: "Excellent",
    70: "Good",
    50: "Fair",
    30: "Poor",
    0: "Bad",
}


def _comfort_label(score: float) -> str:
    """Return a human-readable comfort label for a numeric score."""
    for threshold, label in sorted(COMFORT_LABELS.items(), reverse=True):
        if score >= threshold:
            return label
    return "Bad"


# ---------------------------------------------------------------------------
# Platform setup
# ---------------------------------------------------------------------------


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Smart Climate sensor entities from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = []

    # Determine temperature unit from config
    temp_unit_cfg = entry.data.get(CONF_TEMP_UNIT, "F")
    native_temp_unit = (
        UnitOfTemperature.FAHRENHEIT
        if temp_unit_cfg == "F"
        else UnitOfTemperature.CELSIUS
    )

    # --- Per-room sensors --------------------------------------------------
    rooms = coordinator.data.get("rooms", {})
    for room_slug in rooms:
        entities.extend(
            [
                SmartClimateComfortSensor(coordinator, room_slug),
                SmartClimateEfficiencySensor(coordinator, room_slug),
                SmartClimateTemperatureSensor(
                    coordinator, room_slug, native_temp_unit
                ),
                SmartClimateHumiditySensor(coordinator, room_slug),
                SmartClimateRuntimeSensor(coordinator, room_slug),
                SmartClimateCyclesSensor(coordinator, room_slug),
                SmartClimateActiveScheduleSensor(coordinator, room_slug),
            ]
        )

    # --- Whole-house sensors -----------------------------------------------
    entities.extend(
        [
            SmartClimateHouseComfortSensor(coordinator),
            SmartClimateHouseEfficiencySensor(coordinator),
            SmartClimateHouseRuntimeSensor(coordinator),
            SmartClimateHDDSensor(coordinator),
            SmartClimateCDDSensor(coordinator),
            SmartClimateLastAnalysisSensor(coordinator),
            SmartClimateSuggestionCountSensor(coordinator),
            SmartClimateDailySummarySensor(coordinator),
            SmartClimateActiveHouseScheduleSensor(coordinator),
        ]
    )

    async_add_entities(entities)


# ===========================================================================
# Per-Room Sensor Classes
# ===========================================================================


class SmartClimateComfortSensor(SmartClimateEntity, SensorEntity):
    """Comfort score for a room (0-100%)."""

    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:emoticon-happy-outline"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, room_slug: str) -> None:
        """Initialize the comfort sensor."""
        super().__init__(
            coordinator,
            entity_key="comfort_score",
            name="Comfort Score",
            room_slug=room_slug,
        )

    @property
    def entity_id(self) -> str:
        """Return the entity_id."""
        return f"sensor.{ENTITY_PREFIX}_{self._room_slug}_comfort_score"

    @entity_id.setter
    def entity_id(self, value: str) -> None:
        """Allow HA to set entity_id."""
        self._attr_entity_id = value

    @property
    def native_value(self) -> float | None:
        """Return the comfort score."""
        room_state = self.coordinator.data.get("rooms", {}).get(self._room_slug)
        if room_state is None:
            return None
        return round(room_state.comfort_score, 1)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        room_state = self.coordinator.data.get("rooms", {}).get(self._room_slug)
        if room_state is None:
            return {}
        return {
            "comfort_label": _comfort_label(room_state.comfort_score),
            "occupied": room_state.occupied,
            "window_open": room_state.window_open,
        }


class SmartClimateEfficiencySensor(SmartClimateEntity, SensorEntity):
    """Efficiency score for a room (0-100%)."""

    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:lightning-bolt"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, room_slug: str) -> None:
        """Initialize the efficiency sensor."""
        super().__init__(
            coordinator,
            entity_key="efficiency_score",
            name="Efficiency Score",
            room_slug=room_slug,
        )

    @property
    def entity_id(self) -> str:
        """Return the entity_id."""
        return f"sensor.{ENTITY_PREFIX}_{self._room_slug}_efficiency_score"

    @entity_id.setter
    def entity_id(self, value: str) -> None:
        """Allow HA to set entity_id."""
        self._attr_entity_id = value

    @property
    def native_value(self) -> float | None:
        """Return the efficiency score."""
        room_state = self.coordinator.data.get("rooms", {}).get(self._room_slug)
        if room_state is None:
            return None
        return round(room_state.efficiency_score, 1)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        room_state = self.coordinator.data.get("rooms", {}).get(self._room_slug)
        if room_state is None:
            return {}
        return {
            "hvac_action": room_state.hvac_action.value if room_state.hvac_action else None,
            "hvac_runtime_today": round(room_state.hvac_runtime_today, 1),
            "hvac_cycles_today": room_state.hvac_cycles_today,
        }


class SmartClimateTemperatureSensor(SmartClimateEntity, SensorEntity):
    """Aggregated temperature for a room."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self, coordinator, room_slug: str, temp_unit: str
    ) -> None:
        """Initialize the temperature sensor."""
        super().__init__(
            coordinator,
            entity_key="temperature",
            name="Temperature",
            room_slug=room_slug,
        )
        self._attr_native_unit_of_measurement = temp_unit

    @property
    def entity_id(self) -> str:
        """Return the entity_id."""
        return f"sensor.{ENTITY_PREFIX}_{self._room_slug}_temperature"

    @entity_id.setter
    def entity_id(self, value: str) -> None:
        """Allow HA to set entity_id."""
        self._attr_entity_id = value

    @property
    def native_value(self) -> float | None:
        """Return the room temperature."""
        room_state = self.coordinator.data.get("rooms", {}).get(self._room_slug)
        if room_state is None:
            return None
        return room_state.temperature

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        room_state = self.coordinator.data.get("rooms", {}).get(self._room_slug)
        if room_state is None:
            return {}
        return {
            "temp_trend": room_state.temp_trend,
            "current_target": room_state.current_target,
            "smart_target": room_state.smart_target,
        }


class SmartClimateHumiditySensor(SmartClimateEntity, SensorEntity):
    """Aggregated humidity for a room."""

    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, room_slug: str) -> None:
        """Initialize the humidity sensor."""
        super().__init__(
            coordinator,
            entity_key="humidity",
            name="Humidity",
            room_slug=room_slug,
        )

    @property
    def entity_id(self) -> str:
        """Return the entity_id."""
        return f"sensor.{ENTITY_PREFIX}_{self._room_slug}_humidity"

    @entity_id.setter
    def entity_id(self, value: str) -> None:
        """Allow HA to set entity_id."""
        self._attr_entity_id = value

    @property
    def native_value(self) -> float | None:
        """Return the room humidity."""
        room_state = self.coordinator.data.get("rooms", {}).get(self._room_slug)
        if room_state is None:
            return None
        return room_state.humidity


class SmartClimateRuntimeSensor(SmartClimateEntity, SensorEntity):
    """HVAC runtime today for a room (minutes)."""

    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_icon = "mdi:clock-outline"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    def __init__(self, coordinator, room_slug: str) -> None:
        """Initialize the runtime sensor."""
        super().__init__(
            coordinator,
            entity_key="hvac_runtime",
            name="HVAC Runtime",
            room_slug=room_slug,
        )

    @property
    def entity_id(self) -> str:
        """Return the entity_id."""
        return f"sensor.{ENTITY_PREFIX}_{self._room_slug}_hvac_runtime"

    @entity_id.setter
    def entity_id(self, value: str) -> None:
        """Allow HA to set entity_id."""
        self._attr_entity_id = value

    @property
    def native_value(self) -> float | None:
        """Return HVAC runtime in minutes."""
        room_state = self.coordinator.data.get("rooms", {}).get(self._room_slug)
        if room_state is None:
            return None
        return round(room_state.hvac_runtime_today, 1)


class SmartClimateCyclesSensor(SmartClimateEntity, SensorEntity):
    """HVAC cycle count today for a room."""

    _attr_icon = "mdi:refresh"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    def __init__(self, coordinator, room_slug: str) -> None:
        """Initialize the cycles sensor."""
        super().__init__(
            coordinator,
            entity_key="hvac_cycles",
            name="HVAC Cycles",
            room_slug=room_slug,
        )

    @property
    def entity_id(self) -> str:
        """Return the entity_id."""
        return f"sensor.{ENTITY_PREFIX}_{self._room_slug}_hvac_cycles"

    @entity_id.setter
    def entity_id(self, value: str) -> None:
        """Allow HA to set entity_id."""
        self._attr_entity_id = value

    @property
    def native_value(self) -> int | None:
        """Return HVAC cycle count."""
        room_state = self.coordinator.data.get("rooms", {}).get(self._room_slug)
        if room_state is None:
            return None
        return room_state.hvac_cycles_today


class SmartClimateActiveScheduleSensor(SmartClimateEntity, SensorEntity):
    """Active schedule for a room."""

    _attr_icon = "mdi:calendar-clock"

    def __init__(self, coordinator, room_slug: str) -> None:
        """Initialize the active schedule sensor."""
        super().__init__(
            coordinator,
            entity_key="active_schedule",
            name="Active Schedule",
            room_slug=room_slug,
        )

    @property
    def entity_id(self) -> str:
        """Return the entity_id."""
        return f"sensor.{ENTITY_PREFIX}_{self._room_slug}_active_schedule"

    @entity_id.setter
    def entity_id(self, value: str) -> None:
        """Allow HA to set entity_id."""
        self._attr_entity_id = value

    @property
    def native_value(self) -> str:
        """Return the active schedule name or 'none'."""
        room_state = self.coordinator.data.get("rooms", {}).get(self._room_slug)
        if room_state is None:
            return "none"
        return room_state.active_schedule or "none"


# ===========================================================================
# Whole-House Sensor Classes
# ===========================================================================


class SmartClimateHouseComfortSensor(SmartClimateEntity, SensorEntity):
    """Whole-house average comfort score."""

    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:emoticon-happy-outline"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator) -> None:
        """Initialize the house comfort sensor."""
        super().__init__(
            coordinator,
            entity_key="house_comfort",
            name="House Comfort",
        )

    @property
    def entity_id(self) -> str:
        """Return the entity_id."""
        return f"sensor.{ENTITY_PREFIX}_house_comfort"

    @entity_id.setter
    def entity_id(self, value: str) -> None:
        """Allow HA to set entity_id."""
        self._attr_entity_id = value

    @property
    def native_value(self) -> float | None:
        """Return the house comfort score."""
        house_state = self.coordinator.data.get("house")
        if house_state is None:
            return None
        return round(house_state.comfort_score, 1)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        house_state = self.coordinator.data.get("house")
        if house_state is None:
            return {}
        return {
            "comfort_label": _comfort_label(house_state.comfort_score),
        }


class SmartClimateHouseEfficiencySensor(SmartClimateEntity, SensorEntity):
    """Whole-house average efficiency score."""

    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_icon = "mdi:lightning-bolt"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator) -> None:
        """Initialize the house efficiency sensor."""
        super().__init__(
            coordinator,
            entity_key="house_efficiency",
            name="House Efficiency",
        )

    @property
    def entity_id(self) -> str:
        """Return the entity_id."""
        return f"sensor.{ENTITY_PREFIX}_house_efficiency"

    @entity_id.setter
    def entity_id(self, value: str) -> None:
        """Allow HA to set entity_id."""
        self._attr_entity_id = value

    @property
    def native_value(self) -> float | None:
        """Return the house efficiency score."""
        house_state = self.coordinator.data.get("house")
        if house_state is None:
            return None
        return round(house_state.efficiency_score, 1)


class SmartClimateHouseRuntimeSensor(SmartClimateEntity, SensorEntity):
    """Total HVAC runtime across all rooms today (minutes)."""

    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_icon = "mdi:clock-outline"
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    def __init__(self, coordinator) -> None:
        """Initialize the house runtime sensor."""
        super().__init__(
            coordinator,
            entity_key="house_hvac_runtime",
            name="House HVAC Runtime",
        )

    @property
    def entity_id(self) -> str:
        """Return the entity_id."""
        return f"sensor.{ENTITY_PREFIX}_house_hvac_runtime"

    @entity_id.setter
    def entity_id(self, value: str) -> None:
        """Allow HA to set entity_id."""
        self._attr_entity_id = value

    @property
    def native_value(self) -> float | None:
        """Return total HVAC runtime in minutes."""
        house_state = self.coordinator.data.get("house")
        if house_state is None:
            return None
        return round(house_state.total_hvac_runtime, 1)


class SmartClimateHDDSensor(SmartClimateEntity, SensorEntity):
    """Heating degree days."""

    _attr_icon = "mdi:thermometer-chevron-up"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator) -> None:
        """Initialize the HDD sensor."""
        super().__init__(
            coordinator,
            entity_key="heating_degree_days",
            name="Heating Degree Days",
        )

    @property
    def entity_id(self) -> str:
        """Return the entity_id."""
        return f"sensor.{ENTITY_PREFIX}_heating_degree_days"

    @entity_id.setter
    def entity_id(self, value: str) -> None:
        """Allow HA to set entity_id."""
        self._attr_entity_id = value

    @property
    def native_value(self) -> float | None:
        """Return heating degree days."""
        house_state = self.coordinator.data.get("house")
        if house_state is None:
            return None
        return round(house_state.heating_degree_days, 2)


class SmartClimateCDDSensor(SmartClimateEntity, SensorEntity):
    """Cooling degree days."""

    _attr_icon = "mdi:thermometer-chevron-down"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator) -> None:
        """Initialize the CDD sensor."""
        super().__init__(
            coordinator,
            entity_key="cooling_degree_days",
            name="Cooling Degree Days",
        )

    @property
    def entity_id(self) -> str:
        """Return the entity_id."""
        return f"sensor.{ENTITY_PREFIX}_cooling_degree_days"

    @entity_id.setter
    def entity_id(self, value: str) -> None:
        """Allow HA to set entity_id."""
        self._attr_entity_id = value

    @property
    def native_value(self) -> float | None:
        """Return cooling degree days."""
        house_state = self.coordinator.data.get("house")
        if house_state is None:
            return None
        return round(house_state.cooling_degree_days, 2)


class SmartClimateLastAnalysisSensor(SmartClimateEntity, SensorEntity):
    """Timestamp of the last AI analysis run."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, coordinator) -> None:
        """Initialize the last analysis sensor."""
        super().__init__(
            coordinator,
            entity_key="ai_last_analysis",
            name="AI Last Analysis",
        )

    @property
    def entity_id(self) -> str:
        """Return the entity_id."""
        return f"sensor.{ENTITY_PREFIX}_ai_last_analysis"

    @entity_id.setter
    def entity_id(self, value: str) -> None:
        """Allow HA to set entity_id."""
        self._attr_entity_id = value

    @property
    def native_value(self):
        """Return the last analysis timestamp."""
        house_state = self.coordinator.data.get("house")
        if house_state is None:
            return None
        return house_state.last_analysis_time


class SmartClimateSuggestionCountSensor(SmartClimateEntity, SensorEntity):
    """Count of pending AI suggestions."""

    _attr_icon = "mdi:lightbulb-on-outline"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator) -> None:
        """Initialize the suggestion count sensor."""
        super().__init__(
            coordinator,
            entity_key="ai_suggestion_count",
            name="AI Suggestion Count",
        )

    @property
    def entity_id(self) -> str:
        """Return the entity_id."""
        return f"sensor.{ENTITY_PREFIX}_ai_suggestion_count"

    @entity_id.setter
    def entity_id(self, value: str) -> None:
        """Allow HA to set entity_id."""
        self._attr_entity_id = value

    @property
    def native_value(self) -> int:
        """Return the number of pending suggestions."""
        house_state = self.coordinator.data.get("house")
        if house_state is None:
            return 0
        return sum(
            1
            for s in house_state.suggestions
            if s.status == SUGGESTION_PENDING
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        house_state = self.coordinator.data.get("house")
        if house_state is None:
            return {}
        pending = [
            s for s in house_state.suggestions if s.status == SUGGESTION_PENDING
        ]
        return {
            "total_suggestions": len(house_state.suggestions),
            "pending_titles": [s.title for s in pending],
        }


class SmartClimateDailySummarySensor(SmartClimateEntity, SensorEntity):
    """AI-generated daily summary text."""

    _attr_icon = "mdi:text-box-outline"

    def __init__(self, coordinator) -> None:
        """Initialize the daily summary sensor."""
        super().__init__(
            coordinator,
            entity_key="ai_daily_summary",
            name="AI Daily Summary",
        )

    @property
    def entity_id(self) -> str:
        """Return the entity_id."""
        return f"sensor.{ENTITY_PREFIX}_ai_daily_summary"

    @entity_id.setter
    def entity_id(self, value: str) -> None:
        """Allow HA to set entity_id."""
        self._attr_entity_id = value

    @property
    def native_value(self) -> str | None:
        """Return the daily summary text."""
        house_state = self.coordinator.data.get("house")
        if house_state is None:
            return None
        return house_state.ai_daily_summary or None


class SmartClimateActiveHouseScheduleSensor(SmartClimateEntity, SensorEntity):
    """Currently active house-wide schedule."""

    _attr_icon = "mdi:calendar-clock"

    def __init__(self, coordinator) -> None:
        """Initialize the active house schedule sensor."""
        super().__init__(
            coordinator,
            entity_key="active_schedule",
            name="Active Schedule",
        )

    @property
    def entity_id(self) -> str:
        """Return the entity_id."""
        return f"sensor.{ENTITY_PREFIX}_active_schedule"

    @entity_id.setter
    def entity_id(self, value: str) -> None:
        """Allow HA to set entity_id."""
        self._attr_entity_id = value

    @property
    def native_value(self) -> str:
        """Return the active house schedule name or 'none'."""
        house_state = self.coordinator.data.get("house")
        if house_state is None:
            return "none"
        return house_state.active_schedule or "none"
