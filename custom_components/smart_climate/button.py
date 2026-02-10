"""Button platform for the Smart Climate integration."""

from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, ENTITY_PREFIX
from .entity import SmartClimateEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Smart Climate button entities from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SmartClimateTriggerAnalysisButton(coordinator)])


class SmartClimateTriggerAnalysisButton(SmartClimateEntity, ButtonEntity):
    """Button to trigger an AI analysis on demand."""

    _attr_icon = "mdi:brain"

    def __init__(self, coordinator) -> None:
        """Initialize the trigger analysis button."""
        super().__init__(
            coordinator,
            entity_key="trigger_analysis",
            name="Trigger AI Analysis",
        )

    @property
    def entity_id(self) -> str:
        """Return the entity_id."""
        return f"button.{ENTITY_PREFIX}_trigger_analysis"

    @entity_id.setter
    def entity_id(self, value: str) -> None:
        """Allow HA to set entity_id."""
        self._attr_entity_id = value

    async def async_press(self) -> None:
        """Handle the button press."""
        _LOGGER.info("AI analysis triggered via button press")
        await self.coordinator.async_trigger_analysis()
