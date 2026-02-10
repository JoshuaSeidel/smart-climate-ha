"""Smart Climate - AI-Powered Home Assistant Integration."""

from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import SmartClimateCoordinator
from .services import async_setup_services, async_unload_services

_LOGGER = logging.getLogger(__name__)

CARD_URL = f"/{DOMAIN}/smart-climate-card.js"
CARD_DIR = Path(__file__).parent / "www"

PLATFORMS_LIST: list[Platform] = [
    Platform.CLIMATE,
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.SELECT,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Smart Climate from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    coordinator = SmartClimateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS_LIST)
    await async_setup_services(hass, coordinator)

    # Register the Lovelace card as a static resource
    await _async_register_card(hass)

    # Schedule daily AI analysis
    coordinator.schedule_daily_analysis()

    entry.async_on_unload(entry.add_update_listener(async_update_options))

    _LOGGER.info("Smart Climate integration setup complete for %s", entry.title)
    return True


async def _async_register_card(hass: HomeAssistant) -> None:
    """Register the custom Lovelace card JS file."""
    card_file = CARD_DIR / "smart-climate-card.js"
    if not card_file.is_file():
        _LOGGER.debug("Lovelace card JS not found at %s, skipping registration", card_file)
        return

    # Serve the card JS file — use the modern async API (HA 2025.12+)
    try:
        from homeassistant.components.http import StaticPathConfig

        await hass.http.async_register_static_paths(
            [StaticPathConfig(url_path=CARD_URL, path=str(card_file), cache_headers=False)]
        )
    except (ImportError, AttributeError):
        # Fallback for older HA versions
        hass.http.register_static_path(CARD_URL, str(card_file), cache_headers=False)

    # Auto-register as a Lovelace resource so users don't have to
    _register_lovelace_resource(hass)


def _register_lovelace_resource(hass: HomeAssistant) -> None:
    """Add the card to Lovelace resources if not already present."""
    # This works with both storage and YAML Lovelace modes
    try:
        from homeassistant.components.lovelace import _resource_to_dict  # noqa: F401
        from homeassistant.components.lovelace.resources import (
            ResourceStorageCollection,
        )
    except ImportError:
        _LOGGER.debug("Could not import Lovelace resource helpers, skipping auto-register")
        return

    try:
        resources = hass.data.get("lovelace_resources")
        if resources is None:
            return

        if isinstance(resources, ResourceStorageCollection):
            # Check if already registered
            for item in resources.async_items():
                if CARD_URL in item.get("url", ""):
                    return

            # Register as a module resource
            hass.async_create_task(
                resources.async_create_item({"res_type": "module", "url": CARD_URL})
            )
            _LOGGER.info("Registered Smart Climate card as Lovelace resource")
    except Exception:
        _LOGGER.debug("Could not auto-register Lovelace resource", exc_info=True)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    coordinator: SmartClimateCoordinator = hass.data[DOMAIN][entry.entry_id]
    coordinator.cancel_scheduled_tasks()

    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, PLATFORMS_LIST
    )

    if unload_ok:
        await async_unload_services(hass)
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)
