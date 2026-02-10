"""Base entity for Smart Climate integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ENTITY_PREFIX

if TYPE_CHECKING:
    from .coordinator import SmartClimateCoordinator


class SmartClimateEntity(CoordinatorEntity["SmartClimateCoordinator"], Entity):
    """Base entity for Smart Climate."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SmartClimateCoordinator,
        entity_key: str,
        name: str,
        room_slug: str | None = None,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._room_slug = room_slug
        self._entity_key = entity_key

        if room_slug:
            self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{room_slug}_{entity_key}"
            self._attr_name = f"{room_slug} {name}"
        else:
            self._attr_unique_id = (
                f"{coordinator.config_entry.entry_id}_{entity_key}"
            )
            self._attr_name = name

    @property
    def device_info(self):
        """Return device info."""
        if self._room_slug:
            room_state = self.coordinator.data.get("rooms", {}).get(self._room_slug)
            room_name = (
                room_state.config.name if room_state else self._room_slug
            )
            return {
                "identifiers": {
                    (DOMAIN, f"{self.coordinator.config_entry.entry_id}_{self._room_slug}")
                },
                "name": f"Smart Climate - {room_name}",
                "manufacturer": "Smart Climate",
                "model": "Room Zone",
                "via_device": (DOMAIN, self.coordinator.config_entry.entry_id),
            }
        return {
            "identifiers": {(DOMAIN, self.coordinator.config_entry.entry_id)},
            "name": "Smart Climate",
            "manufacturer": "Smart Climate",
            "model": "House Controller",
        }

    @property
    def entity_id_suffix(self) -> str:
        """Return entity ID suffix."""
        if self._room_slug:
            return f"{ENTITY_PREFIX}_{self._room_slug}_{self._entity_key}"
        return f"{ENTITY_PREFIX}_{self._entity_key}"
