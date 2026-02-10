"""Climate platform for the Smart Climate integration.

Creates virtual zone climate entities that proxy real climate entities.
One per room. Entity: climate.sc_{room_slug}
"""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ENTITY_PREFIX
from .entity import SmartClimateEntity

_LOGGER = logging.getLogger(__name__)

# Mapping from HA state strings to HVACMode enum values
_HVAC_MODE_MAP: dict[str, HVACMode] = {m.value: m for m in HVACMode}

# Mapping from HA hvac_action strings to HVACAction enum values
_HVAC_ACTION_MAP: dict[str, HVACAction] = {a.value: a for a in HVACAction}


# ---------------------------------------------------------------------------
# Platform setup
# ---------------------------------------------------------------------------


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Smart Climate virtual climate entities from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for room_slug in coordinator.data["rooms"]:
        room_state = coordinator.data["rooms"][room_slug]
        entities.append(
            SmartClimateVirtualClimate(
                coordinator, room_slug, room_state.config.name
            )
        )
    async_add_entities(entities)


# ---------------------------------------------------------------------------
# Virtual Climate Entity
# ---------------------------------------------------------------------------


class SmartClimateVirtualClimate(SmartClimateEntity, ClimateEntity):
    """Virtual zone climate entity that proxies a real climate entity.

    Reads current state from the underlying real climate entity and adds a
    Smart Climate control layer (smart targets, follow-me override, user
    override tracking).
    """

    _attr_has_entity_name = True
    _enable_turn_on_off_backwards_compat = False

    def __init__(
        self,
        coordinator,
        room_slug: str,
        room_name: str,
    ) -> None:
        """Initialize the virtual climate entity."""
        super().__init__(
            coordinator,
            entity_key="climate",
            name=room_name,
            room_slug=room_slug,
        )
        room_config = coordinator.data["rooms"][room_slug].config
        self._underlying_entity: str = room_config.climate_entity

    # ------------------------------------------------------------------
    # Entity ID override
    # ------------------------------------------------------------------

    @property
    def entity_id(self) -> str:
        """Return the entity_id."""
        return f"climate.{ENTITY_PREFIX}_{self._room_slug}"

    @entity_id.setter
    def entity_id(self, value: str) -> None:
        """Allow HA to set entity_id."""
        self._attr_entity_id = value

    # ------------------------------------------------------------------
    # Helpers to read real entity state
    # ------------------------------------------------------------------

    def _get_real_state(self):
        """Return the State object for the underlying real climate entity."""
        return self.hass.states.get(self._underlying_entity)

    def _get_real_attr(self, key: str, default=None):
        """Return an attribute from the underlying real climate entity."""
        real_state = self._get_real_state()
        if real_state is None:
            return default
        return real_state.attributes.get(key, default)

    def _get_room_state(self):
        """Return the RoomState from coordinator data for this room."""
        return self.coordinator.data.get("rooms", {}).get(self._room_slug)

    # ------------------------------------------------------------------
    # Climate entity properties - mirrored from real entity
    # ------------------------------------------------------------------

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return current HVAC mode from the real entity."""
        real_state = self._get_real_state()
        if real_state is None:
            return None
        return _HVAC_MODE_MAP.get(real_state.state)

    @property
    def hvac_modes(self) -> list[HVACMode]:
        """Return the list of available HVAC modes from the real entity."""
        raw_modes = self._get_real_attr("hvac_modes", [])
        modes = []
        for mode in raw_modes:
            mapped = _HVAC_MODE_MAP.get(mode)
            if mapped is not None:
                modes.append(mapped)
        return modes or [HVACMode.OFF]

    @property
    def hvac_action(self) -> HVACAction | None:
        """Return current HVAC action from the real entity."""
        raw_action = self._get_real_attr("hvac_action")
        if raw_action is None:
            return None
        return _HVAC_ACTION_MAP.get(raw_action)

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature from the real entity."""
        value = self._get_real_attr("current_temperature")
        if value is not None:
            try:
                return float(value)
            except (ValueError, TypeError):
                return None
        return None

    @property
    def target_temperature(self) -> float | None:
        """Return the target temperature from the real entity."""
        value = self._get_real_attr("temperature")
        if value is not None:
            try:
                return float(value)
            except (ValueError, TypeError):
                return None
        return None

    @property
    def target_temperature_high(self) -> float | None:
        """Return the upper bound target temperature from the real entity."""
        value = self._get_real_attr("target_temp_high")
        if value is not None:
            try:
                return float(value)
            except (ValueError, TypeError):
                return None
        return None

    @property
    def target_temperature_low(self) -> float | None:
        """Return the lower bound target temperature from the real entity."""
        value = self._get_real_attr("target_temp_low")
        if value is not None:
            try:
                return float(value)
            except (ValueError, TypeError):
                return None
        return None

    @property
    def target_temperature_step(self) -> float | None:
        """Return the temperature step from the real entity."""
        value = self._get_real_attr("target_temp_step")
        if value is not None:
            try:
                return float(value)
            except (ValueError, TypeError):
                return None
        return None

    @property
    def min_temp(self) -> float:
        """Return the minimum temperature from the real entity."""
        value = self._get_real_attr("min_temp")
        if value is not None:
            try:
                return float(value)
            except (ValueError, TypeError):
                pass
        return super().min_temp

    @property
    def max_temp(self) -> float:
        """Return the maximum temperature from the real entity."""
        value = self._get_real_attr("max_temp")
        if value is not None:
            try:
                return float(value)
            except (ValueError, TypeError):
                pass
        return super().max_temp

    @property
    def temperature_unit(self) -> str:
        """Return the temperature unit from the real entity."""
        unit = self._get_real_attr("unit_of_measurement")
        if unit is not None:
            return unit
        return UnitOfTemperature.FAHRENHEIT

    @property
    def fan_mode(self) -> str | None:
        """Return the current fan mode from the real entity."""
        return self._get_real_attr("fan_mode")

    @property
    def fan_modes(self) -> list[str] | None:
        """Return the list of available fan modes from the real entity."""
        return self._get_real_attr("fan_modes")

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode from the real entity."""
        return self._get_real_attr("preset_mode")

    @property
    def preset_modes(self) -> list[str] | None:
        """Return the list of available preset modes from the real entity."""
        return self._get_real_attr("preset_modes")

    @property
    def swing_mode(self) -> str | None:
        """Return the current swing mode from the real entity."""
        return self._get_real_attr("swing_mode")

    @property
    def swing_modes(self) -> list[str] | None:
        """Return the list of available swing modes from the real entity."""
        return self._get_real_attr("swing_modes")

    @property
    def supported_features(self) -> ClimateEntityFeature:
        """Return supported features from the real entity."""
        raw = self._get_real_attr("supported_features", 0)
        try:
            return ClimateEntityFeature(int(raw))
        except (ValueError, TypeError):
            return ClimateEntityFeature(0)

    # ------------------------------------------------------------------
    # Extra state attributes (Smart Climate layer)
    # ------------------------------------------------------------------

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return Smart Climate extra attributes."""
        room_state = self._get_room_state()
        attrs: dict[str, Any] = {
            "underlying_entity": self._underlying_entity,
        }
        if room_state is not None:
            attrs["smart_target"] = room_state.smart_target
            attrs["user_override_active"] = room_state.user_override_active
            attrs["follow_me_active"] = room_state.follow_me_active
            attrs["last_adjustment_reason"] = room_state.last_adjustment_reason
        else:
            attrs["smart_target"] = None
            attrs["user_override_active"] = False
            attrs["follow_me_active"] = False
            attrs["last_adjustment_reason"] = ""
        return attrs

    # ------------------------------------------------------------------
    # Service call forwarding
    # ------------------------------------------------------------------

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set temperature -- mark user override, then forward to real entity."""
        room_state = self._get_room_state()
        if room_state is not None:
            room_state.user_override_active = True
            _LOGGER.debug(
                "User override activated for room '%s' via set_temperature",
                self._room_slug,
            )

        # Build service data targeting the real entity
        service_data: dict[str, Any] = {"entity_id": self._underlying_entity}
        if ATTR_TEMPERATURE in kwargs:
            service_data[ATTR_TEMPERATURE] = kwargs[ATTR_TEMPERATURE]
        if "target_temp_high" in kwargs:
            service_data["target_temp_high"] = kwargs["target_temp_high"]
        if "target_temp_low" in kwargs:
            service_data["target_temp_low"] = kwargs["target_temp_low"]
        if "hvac_mode" in kwargs:
            service_data["hvac_mode"] = kwargs["hvac_mode"]

        await self.hass.services.async_call(
            "climate", "set_temperature", service_data, blocking=True
        )

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set HVAC mode -- forward to real entity."""
        service_data = {
            "entity_id": self._underlying_entity,
            "hvac_mode": hvac_mode.value if isinstance(hvac_mode, HVACMode) else hvac_mode,
        }
        await self.hass.services.async_call(
            "climate", "set_hvac_mode", service_data, blocking=True
        )

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set fan mode -- forward to real entity."""
        service_data = {
            "entity_id": self._underlying_entity,
            "fan_mode": fan_mode,
        }
        await self.hass.services.async_call(
            "climate", "set_fan_mode", service_data, blocking=True
        )

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set preset mode -- forward to real entity."""
        service_data = {
            "entity_id": self._underlying_entity,
            "preset_mode": preset_mode,
        }
        await self.hass.services.async_call(
            "climate", "set_preset_mode", service_data, blocking=True
        )

    async def async_set_swing_mode(self, swing_mode: str) -> None:
        """Set swing mode -- forward to real entity."""
        service_data = {
            "entity_id": self._underlying_entity,
            "swing_mode": swing_mode,
        }
        await self.hass.services.async_call(
            "climate", "set_swing_mode", service_data, blocking=True
        )

    async def async_turn_on(self) -> None:
        """Turn on -- forward to real entity."""
        await self.hass.services.async_call(
            "climate",
            "turn_on",
            {"entity_id": self._underlying_entity},
            blocking=True,
        )

    async def async_turn_off(self) -> None:
        """Turn off -- forward to real entity."""
        await self.hass.services.async_call(
            "climate",
            "turn_off",
            {"entity_id": self._underlying_entity},
            blocking=True,
        )
