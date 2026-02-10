"""Select entity for Smart Climate operation mode."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    DOMAIN,
    ENTITY_PREFIX,
    OPERATION_MODE_ACTIVE,
    OPERATION_MODE_DISABLED,
    OPERATION_MODE_TRAINING,
    OPERATION_MODES,
)
from .coordinator import SmartClimateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Smart Climate select entities."""
    coordinator: SmartClimateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SmartClimateOperationModeSelect(coordinator)])


_MODE_LABELS = {
    OPERATION_MODE_TRAINING: "Training",
    OPERATION_MODE_ACTIVE: "Active",
    OPERATION_MODE_DISABLED: "Disabled",
}


class SmartClimateOperationModeSelect(SelectEntity):
    """Select entity to control the Smart Climate operation mode."""

    _attr_has_entity_name = True
    _attr_translation_key = "operation_mode"

    def __init__(self, coordinator: SmartClimateCoordinator) -> None:
        """Initialize the select entity."""
        self.coordinator = coordinator
        self._attr_unique_id = f"{DOMAIN}_{ENTITY_PREFIX}_operation_mode"
        self._attr_options = list(OPERATION_MODES)
        self._attr_current_option = coordinator.operation_mode
        self._attr_icon = "mdi:tune"
        self._attr_name = f"{ENTITY_PREFIX.upper()} Operation Mode"

    @property
    def current_option(self) -> str:
        """Return the current operation mode."""
        return self.coordinator.operation_mode

    async def async_select_option(self, option: str) -> None:
        """Change the operation mode."""
        if option not in OPERATION_MODES:
            return
        self.coordinator.operation_mode = option
        self.async_write_ha_state()
