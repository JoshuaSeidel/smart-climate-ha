"""Config flow for Smart Climate integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import (
    area_registry as ar,
)
from homeassistant.helpers import (
    device_registry as dr,
)
from homeassistant.helpers import (
    entity_registry as er,
)
from homeassistant.helpers import (
    selector,
)

from .const import (
    AI_PROVIDER_NONE,
    AI_PROVIDERS,
    CONF_AI_ANALYSIS_TIME,
    CONF_AI_API_KEY,
    CONF_AI_AUTO_APPLY,
    CONF_AI_BASE_URL,
    CONF_AI_MODEL,
    CONF_AI_PROVIDER,
    CONF_AUXILIARY_ENTITIES,
    CONF_CLIMATE_ENTITY,
    CONF_DOOR_WINDOW_SENSORS,
    CONF_ENABLE_FOLLOW_ME,
    CONF_ENABLE_ZONE_BALANCING,
    CONF_HUMIDITY_SENSORS,
    CONF_INTEGRATION_NAME,
    CONF_OPERATION_MODE,
    CONF_OUTDOOR_TEMP_SENSOR,
    CONF_PRESENCE_SENSORS,
    CONF_ROOM_NAME,
    CONF_ROOM_PRIORITY,
    CONF_ROOM_SLUG,
    CONF_ROOMS,
    CONF_SCHEDULE_DAYS,
    CONF_SCHEDULE_ENABLED,
    CONF_SCHEDULE_END_TIME,
    CONF_SCHEDULE_HVAC_MODE,
    CONF_SCHEDULE_NAME,
    CONF_SCHEDULE_PRIORITY,
    CONF_SCHEDULE_ROOMS,
    CONF_SCHEDULE_SLUG,
    CONF_SCHEDULE_START_TIME,
    CONF_SCHEDULE_TARGET_TEMP,
    CONF_SCHEDULE_USE_AUXILIARY,
    CONF_SCHEDULES,
    CONF_TARGET_TEMP_OFFSET,
    CONF_TEMP_SENSORS,
    CONF_TEMP_UNIT,
    CONF_UPDATE_INTERVAL,
    CONF_VENT_ENTITIES,
    CONF_WEATHER_ENTITY,
    DEFAULT_AI_ANALYSIS_TIME,
    DEFAULT_AI_AUTO_APPLY,
    DEFAULT_ENABLE_FOLLOW_ME,
    DEFAULT_ENABLE_ZONE_BALANCING,
    DEFAULT_NAME,
    DEFAULT_OPERATION_MODE,
    DEFAULT_ROOM_PRIORITY,
    DEFAULT_TARGET_TEMP_OFFSET,
    DEFAULT_TEMP_UNIT,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
)
from .models import slugify

_LOGGER = logging.getLogger(__name__)

# Device classes used for auto-detection
_PRESENCE_DEVICE_CLASSES = {"motion", "occupancy", "presence"}
_DOOR_WINDOW_DEVICE_CLASSES = {"door", "window", "opening", "garage_door"}


# ── Module-level helpers for area auto-detection ──────────────────────


def _get_device_class(entity: Any) -> str | None:
    """Get device class from an entity registry entry."""
    return getattr(entity, "device_class", None) or getattr(
        entity, "original_device_class", None
    )


def _get_entities_for_area(
    area_id: str, entity_reg: er.EntityRegistry, device_reg: dr.DeviceRegistry
) -> list:
    """Get all entities belonging to an area (directly or via device)."""
    entities = []
    for entity in entity_reg.entities.values():
        entity_area = entity.area_id
        if not entity_area and entity.device_id:
            device = device_reg.async_get(entity.device_id)
            if device:
                entity_area = device.area_id
        if entity_area == area_id:
            entities.append(entity)
    return entities


def _auto_detect_rooms_into(
    hass: Any, area_ids: list[str], rooms: list[dict[str, Any]]
) -> None:
    """Auto-detect room entities from selected HA areas and append to rooms list.

    Shared by both config flow and options flow.
    """
    area_reg = ar.async_get(hass)
    entity_reg = er.async_get(hass)
    device_reg = dr.async_get(hass)

    # Collect all climate entities for fallback assignment
    all_climate_entities = [
        entry.entity_id
        for entry in entity_reg.entities.values()
        if entry.domain == "climate" and not entry.disabled_by
    ]

    for area_id in area_ids:
        area = area_reg.async_get_area(area_id)
        if not area:
            continue

        # Find all entities assigned to this area
        area_entities = _get_entities_for_area(area_id, entity_reg, device_reg)

        # Categorize by domain and device class
        climate = [
            e for e in area_entities
            if e.domain == "climate" and not e.disabled_by
        ]
        temp = [
            e for e in area_entities
            if e.domain == "sensor"
            and _get_device_class(e) == "temperature"
            and not e.disabled_by
        ]
        humidity = [
            e for e in area_entities
            if e.domain == "sensor"
            and _get_device_class(e) == "humidity"
            and not e.disabled_by
        ]
        presence = [
            e for e in area_entities
            if e.domain == "binary_sensor"
            and _get_device_class(e) in _PRESENCE_DEVICE_CLASSES
            and not e.disabled_by
        ]
        door_window = [
            e for e in area_entities
            if e.domain == "binary_sensor"
            and _get_device_class(e) in _DOOR_WINDOW_DEVICE_CLASSES
            and not e.disabled_by
        ]
        vents = [
            e for e in area_entities
            if e.domain in ("cover", "number") and not e.disabled_by
        ]

        # Determine climate entity: prefer one in this area, fallback to system-wide
        climate_entity = ""
        if climate:
            climate_entity = climate[0].entity_id
        elif all_climate_entities:
            climate_entity = all_climate_entities[0]

        if not climate_entity:
            # No climate entity available anywhere, skip this room
            continue

        # Check for duplicate slug
        room_slug = slugify(area.name)
        existing_slugs = {r[CONF_ROOM_SLUG] for r in rooms}
        if room_slug in existing_slugs:
            continue

        room_data = {
            CONF_ROOM_NAME: area.name,
            CONF_ROOM_SLUG: room_slug,
            CONF_CLIMATE_ENTITY: climate_entity,
            CONF_TEMP_SENSORS: [e.entity_id for e in temp],
            CONF_HUMIDITY_SENSORS: [e.entity_id for e in humidity],
            CONF_PRESENCE_SENSORS: [e.entity_id for e in presence],
            CONF_DOOR_WINDOW_SENSORS: [e.entity_id for e in door_window],
            CONF_VENT_ENTITIES: [e.entity_id for e in vents],
            CONF_AUXILIARY_ENTITIES: [],
            CONF_ROOM_PRIORITY: DEFAULT_ROOM_PRIORITY,
            CONF_TARGET_TEMP_OFFSET: DEFAULT_TARGET_TEMP_OFFSET,
        }
        rooms.append(room_data)


class SmartClimateConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Smart Climate."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._data: dict[str, Any] = {}
        self._rooms: list[dict[str, Any]] = []
        self._schedules: list[dict[str, Any]] = []

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> SmartClimateOptionsFlow:
        """Get the options flow."""
        return SmartClimateOptionsFlow(config_entry)

    # ── Step 1: General Settings ──────────────────────────────────────

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 1: General settings."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_weather()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_INTEGRATION_NAME, default=DEFAULT_NAME
                    ): str,
                    vol.Required(
                        CONF_TEMP_UNIT, default=DEFAULT_TEMP_UNIT
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[
                                selector.SelectOptionDict(value="F", label="Fahrenheit"),
                                selector.SelectOptionDict(value="C", label="Celsius"),
                            ],
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Required(
                        CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=15, max=300, step=15, unit_of_measurement="seconds"
                        )
                    ),
                    vol.Required(
                        CONF_ENABLE_FOLLOW_ME, default=DEFAULT_ENABLE_FOLLOW_ME
                    ): bool,
                    vol.Required(
                        CONF_ENABLE_ZONE_BALANCING,
                        default=DEFAULT_ENABLE_ZONE_BALANCING,
                    ): bool,
                    vol.Required(
                        CONF_OPERATION_MODE, default=DEFAULT_OPERATION_MODE
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[
                                selector.SelectOptionDict(
                                    value="training",
                                    label="Training (observe only, collect data)",
                                ),
                                selector.SelectOptionDict(
                                    value="active",
                                    label="Active (full climate control)",
                                ),
                                selector.SelectOptionDict(
                                    value="disabled",
                                    label="Disabled (paused)",
                                ),
                            ],
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
            errors=errors,
        )

    # ── Step 2: Outdoor Weather ───────────────────────────────────────

    async def async_step_weather(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 2: Outdoor weather source."""
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_area_select()

        return self.async_show_form(
            step_id="weather",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_WEATHER_ENTITY): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="weather")
                    ),
                    vol.Optional(CONF_OUTDOOR_TEMP_SENSOR): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="sensor", device_class="temperature")
                    ),
                }
            ),
        )

    # ── Step 3: Area Auto-Detection ───────────────────────────────────

    async def async_step_area_select(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 3: Select HA areas to auto-detect rooms."""
        if user_input is not None:
            selected_areas = user_input.get("areas", [])
            if selected_areas:
                self._auto_detect_rooms(selected_areas)
            return await self.async_step_room_menu()

        # Try to get areas from HA
        try:
            area_reg = ar.async_get(self.hass)
            areas = list(area_reg.async_list_areas())
        except Exception:
            areas = []

        if not areas:
            # No areas defined, go straight to manual room setup
            return await self.async_step_room_menu()

        return self.async_show_form(
            step_id="area_select",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        "areas",
                        default=[a.id for a in areas],
                    ): selector.AreaSelector(
                        selector.AreaSelectorConfig(multiple=True)
                    ),
                }
            ),
        )

    def _auto_detect_rooms(self, area_ids: list[str]) -> None:
        """Auto-detect room entities from selected HA areas."""
        _auto_detect_rooms_into(self.hass, area_ids, self._rooms)

    # ── Step 4: Room Menu ─────────────────────────────────────────────

    async def async_step_room_menu(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 4: Room menu - add/remove rooms or finish."""
        if user_input is not None:
            action = user_input.get("action")
            if action == "add_room":
                return await self.async_step_add_room()
            if action == "remove_room":
                return await self.async_step_remove_room()
            if action == "finish_rooms":
                if not self._rooms:
                    return self.async_show_form(
                        step_id="room_menu",
                        data_schema=self._get_room_menu_schema(),
                        errors={"base": "min_one_room"},
                    )
                return await self.async_step_schedule_menu()

        room_count = len(self._rooms)
        room_names = (
            ", ".join(r[CONF_ROOM_NAME] for r in self._rooms)
            if self._rooms
            else "None"
        )
        description_placeholders = {
            "room_count": str(room_count),
            "room_names": room_names,
        }

        return self.async_show_form(
            step_id="room_menu",
            data_schema=self._get_room_menu_schema(),
            description_placeholders=description_placeholders,
        )

    def _get_room_menu_schema(self) -> vol.Schema:
        """Build the room menu schema with dynamic options."""
        options = [
            selector.SelectOptionDict(value="add_room", label="Add a Room"),
        ]
        if self._rooms:
            options.append(
                selector.SelectOptionDict(
                    value="remove_room", label="Remove a Room"
                )
            )
        options.append(
            selector.SelectOptionDict(
                value="finish_rooms", label="Finish Room Setup"
            )
        )
        return vol.Schema(
            {
                vol.Required("action"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=options,
                        mode=selector.SelectSelectorMode.LIST,
                    )
                )
            }
        )

    # ── Step 5: Add Room ──────────────────────────────────────────────

    async def async_step_add_room(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Add a room manually."""
        if user_input is not None:
            room_data = {
                CONF_ROOM_NAME: user_input[CONF_ROOM_NAME],
                CONF_ROOM_SLUG: slugify(user_input[CONF_ROOM_NAME]),
                CONF_CLIMATE_ENTITY: user_input[CONF_CLIMATE_ENTITY],
                CONF_TEMP_SENSORS: user_input.get(CONF_TEMP_SENSORS, []),
                CONF_HUMIDITY_SENSORS: user_input.get(CONF_HUMIDITY_SENSORS, []),
                CONF_PRESENCE_SENSORS: user_input.get(CONF_PRESENCE_SENSORS, []),
                CONF_DOOR_WINDOW_SENSORS: user_input.get(
                    CONF_DOOR_WINDOW_SENSORS, []
                ),
                CONF_VENT_ENTITIES: user_input.get(CONF_VENT_ENTITIES, []),
                CONF_AUXILIARY_ENTITIES: user_input.get(
                    CONF_AUXILIARY_ENTITIES, []
                ),
                CONF_ROOM_PRIORITY: user_input.get(
                    CONF_ROOM_PRIORITY, DEFAULT_ROOM_PRIORITY
                ),
                CONF_TARGET_TEMP_OFFSET: user_input.get(
                    CONF_TARGET_TEMP_OFFSET, DEFAULT_TARGET_TEMP_OFFSET
                ),
            }
            self._rooms.append(room_data)
            return await self.async_step_room_menu()

        return self.async_show_form(
            step_id="add_room",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ROOM_NAME): str,
                    vol.Required(CONF_CLIMATE_ENTITY): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="climate")
                    ),
                    vol.Optional(CONF_TEMP_SENSORS): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain="sensor",
                            device_class="temperature",
                            multiple=True,
                        )
                    ),
                    vol.Optional(CONF_HUMIDITY_SENSORS): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain="sensor",
                            device_class="humidity",
                            multiple=True,
                        )
                    ),
                    vol.Optional(CONF_PRESENCE_SENSORS): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain="binary_sensor",
                            multiple=True,
                        )
                    ),
                    vol.Optional(
                        CONF_DOOR_WINDOW_SENSORS
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain="binary_sensor",
                            multiple=True,
                        )
                    ),
                    vol.Optional(CONF_VENT_ENTITIES): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain=["cover", "switch", "number"],
                            multiple=True,
                        )
                    ),
                    vol.Optional(
                        CONF_AUXILIARY_ENTITIES
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain=["climate", "switch", "fan"],
                            multiple=True,
                        )
                    ),
                    vol.Optional(
                        CONF_ROOM_PRIORITY, default=DEFAULT_ROOM_PRIORITY
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1, max=10, step=1, mode=selector.NumberSelectorMode.SLIDER
                        )
                    ),
                    vol.Optional(
                        CONF_TARGET_TEMP_OFFSET, default=DEFAULT_TARGET_TEMP_OFFSET
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=-10.0,
                            max=10.0,
                            step=0.5,
                            unit_of_measurement="°",
                        )
                    ),
                }
            ),
        )

    # ── Step 6: Remove Room ───────────────────────────────────────────

    async def async_step_remove_room(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Remove a room from the list."""
        if user_input is not None:
            room_slug = user_input.get("room_to_remove")
            if room_slug:
                self._rooms = [
                    r for r in self._rooms if r[CONF_ROOM_SLUG] != room_slug
                ]
            return await self.async_step_room_menu()

        room_options = [
            selector.SelectOptionDict(
                value=r[CONF_ROOM_SLUG], label=r[CONF_ROOM_NAME]
            )
            for r in self._rooms
        ]

        return self.async_show_form(
            step_id="remove_room",
            data_schema=vol.Schema(
                {
                    vol.Required("room_to_remove"): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=room_options,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
        )

    # ── Step 7: Schedule Menu ─────────────────────────────────────────

    async def async_step_schedule_menu(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Schedule menu."""
        if user_input is not None:
            action = user_input.get("action")
            if action == "add_schedule":
                return await self.async_step_add_schedule()
            if action in ("finish_schedules", "skip_schedules"):
                return await self.async_step_ai_provider()

        schedule_count = len(self._schedules)
        description_placeholders = {"schedule_count": str(schedule_count)}

        return self.async_show_form(
            step_id="schedule_menu",
            data_schema=vol.Schema(
                {
                    vol.Required("action"): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[
                                selector.SelectOptionDict(
                                    value="add_schedule",
                                    label="Add a Schedule",
                                ),
                                selector.SelectOptionDict(
                                    value="finish_schedules",
                                    label="Finish Schedule Setup",
                                ),
                                selector.SelectOptionDict(
                                    value="skip_schedules",
                                    label="Skip Schedules",
                                ),
                            ],
                            mode=selector.SelectSelectorMode.LIST,
                        )
                    )
                }
            ),
            description_placeholders=description_placeholders,
        )

    # ── Step 8: Add Schedule ──────────────────────────────────────────

    async def async_step_add_schedule(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Add a schedule."""
        if user_input is not None:
            room_options = user_input.get(CONF_SCHEDULE_ROOMS, ["__all__"])
            schedule_data = {
                CONF_SCHEDULE_NAME: user_input[CONF_SCHEDULE_NAME],
                CONF_SCHEDULE_SLUG: slugify(user_input[CONF_SCHEDULE_NAME]),
                CONF_SCHEDULE_ROOMS: room_options,
                CONF_SCHEDULE_DAYS: user_input.get(
                    CONF_SCHEDULE_DAYS, list(range(7))
                ),
                CONF_SCHEDULE_START_TIME: user_input[CONF_SCHEDULE_START_TIME],
                CONF_SCHEDULE_END_TIME: user_input[CONF_SCHEDULE_END_TIME],
                CONF_SCHEDULE_TARGET_TEMP: user_input[CONF_SCHEDULE_TARGET_TEMP],
                CONF_SCHEDULE_HVAC_MODE: user_input.get(CONF_SCHEDULE_HVAC_MODE),
                CONF_SCHEDULE_USE_AUXILIARY: user_input.get(
                    CONF_SCHEDULE_USE_AUXILIARY, False
                ),
                CONF_SCHEDULE_PRIORITY: user_input.get(
                    CONF_SCHEDULE_PRIORITY, 5
                ),
                CONF_SCHEDULE_ENABLED: True,
            }
            self._schedules.append(schedule_data)
            return await self.async_step_schedule_menu()

        room_options = [
            selector.SelectOptionDict(value="__all__", label="All Rooms")
        ] + [
            selector.SelectOptionDict(
                value=r[CONF_ROOM_SLUG], label=r[CONF_ROOM_NAME]
            )
            for r in self._rooms
        ]

        day_options = [
            selector.SelectOptionDict(value="0", label="Monday"),
            selector.SelectOptionDict(value="1", label="Tuesday"),
            selector.SelectOptionDict(value="2", label="Wednesday"),
            selector.SelectOptionDict(value="3", label="Thursday"),
            selector.SelectOptionDict(value="4", label="Friday"),
            selector.SelectOptionDict(value="5", label="Saturday"),
            selector.SelectOptionDict(value="6", label="Sunday"),
        ]

        return self.async_show_form(
            step_id="add_schedule",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_SCHEDULE_NAME): str,
                    vol.Optional(
                        CONF_SCHEDULE_ROOMS, default=["__all__"]
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=room_options,
                            multiple=True,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Optional(
                        CONF_SCHEDULE_DAYS, default=["0", "1", "2", "3", "4", "5", "6"]
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=day_options,
                            multiple=True,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Required(CONF_SCHEDULE_START_TIME): selector.TimeSelector(),
                    vol.Required(CONF_SCHEDULE_END_TIME): selector.TimeSelector(),
                    vol.Required(CONF_SCHEDULE_TARGET_TEMP): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=50.0,
                            max=90.0,
                            step=0.5,
                            unit_of_measurement="°",
                        )
                    ),
                    vol.Optional(CONF_SCHEDULE_HVAC_MODE): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[
                                selector.SelectOptionDict(value="heat", label="Heat"),
                                selector.SelectOptionDict(value="cool", label="Cool"),
                                selector.SelectOptionDict(value="auto", label="Auto"),
                                selector.SelectOptionDict(value="off", label="Off"),
                            ],
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Optional(
                        CONF_SCHEDULE_USE_AUXILIARY, default=False
                    ): bool,
                    vol.Optional(
                        CONF_SCHEDULE_PRIORITY, default=5
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1, max=10, step=1, mode=selector.NumberSelectorMode.SLIDER
                        )
                    ),
                }
            ),
        )

    # ── Step 9: AI Provider ───────────────────────────────────────────

    async def async_step_ai_provider(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """AI Provider configuration."""
        errors: dict[str, str] = {}

        if user_input is not None:
            provider = user_input.get(CONF_AI_PROVIDER, AI_PROVIDER_NONE)
            self._data[CONF_AI_PROVIDER] = provider
            self._data[CONF_AI_API_KEY] = user_input.get(CONF_AI_API_KEY, "")
            self._data[CONF_AI_MODEL] = user_input.get(CONF_AI_MODEL, "")
            self._data[CONF_AI_BASE_URL] = user_input.get(CONF_AI_BASE_URL, "")
            self._data[CONF_AI_ANALYSIS_TIME] = user_input.get(
                CONF_AI_ANALYSIS_TIME, DEFAULT_AI_ANALYSIS_TIME
            )
            self._data[CONF_AI_AUTO_APPLY] = user_input.get(
                CONF_AI_AUTO_APPLY, DEFAULT_AI_AUTO_APPLY
            )

            # Test connection if provider is not none
            if provider != AI_PROVIDER_NONE:
                try:
                    from .ai.provider import create_ai_provider

                    ai_provider = create_ai_provider(
                        provider,
                        {
                            "api_key": self._data.get(CONF_AI_API_KEY, ""),
                            "model": self._data.get(CONF_AI_MODEL, ""),
                            "base_url": self._data.get(CONF_AI_BASE_URL, ""),
                        },
                    )
                    if not await ai_provider.test_connection():
                        errors["base"] = "ai_connection_failed"
                except Exception:
                    _LOGGER.exception("AI provider connection test failed")
                    errors["base"] = "ai_connection_failed"

            if not errors:
                self._data[CONF_ROOMS] = self._rooms
                self._data[CONF_SCHEDULES] = self._schedules
                return self.async_create_entry(
                    title=self._data.get(CONF_INTEGRATION_NAME, DEFAULT_NAME),
                    data=self._data,
                )

        return self.async_show_form(
            step_id="ai_provider",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_AI_PROVIDER, default=AI_PROVIDER_NONE
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[
                                selector.SelectOptionDict(
                                    value=p, label=p.title() if p != "none" else "None (Disable AI)"
                                )
                                for p in AI_PROVIDERS
                            ],
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Optional(CONF_AI_API_KEY): str,
                    vol.Optional(CONF_AI_MODEL): str,
                    vol.Optional(CONF_AI_BASE_URL): str,
                    vol.Optional(
                        CONF_AI_ANALYSIS_TIME, default=DEFAULT_AI_ANALYSIS_TIME
                    ): selector.TimeSelector(),
                    vol.Optional(
                        CONF_AI_AUTO_APPLY, default=DEFAULT_AI_AUTO_APPLY
                    ): bool,
                }
            ),
            errors=errors,
        )


class SmartClimateOptionsFlow(OptionsFlow):
    """Handle options flow for Smart Climate.

    Multi-step menu:
      init (menu) → General Settings / Manage Rooms / AI Settings / Save
    """

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry
        # Working copies so we can edit before saving
        self._data: dict[str, Any] = dict(config_entry.data)
        self._rooms: list[dict[str, Any]] = list(
            config_entry.data.get(CONF_ROOMS, [])
        )
        self._editing_room_index: int | None = None

    # ── Options Menu ──────────────────────────────────────────────────

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Options main menu."""
        if user_input is not None:
            action = user_input.get("action")
            if action == "general_settings":
                return await self.async_step_general_settings()
            if action == "manage_rooms":
                return await self.async_step_manage_rooms()
            if action == "ai_settings":
                return await self.async_step_ai_settings()
            if action == "save":
                return await self._save_and_exit()

        room_count = len(self._rooms)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required("action"): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[
                                selector.SelectOptionDict(
                                    value="general_settings",
                                    label="General Settings",
                                ),
                                selector.SelectOptionDict(
                                    value="manage_rooms",
                                    label=f"Manage Rooms ({room_count} configured)",
                                ),
                                selector.SelectOptionDict(
                                    value="ai_settings",
                                    label="AI Settings",
                                ),
                                selector.SelectOptionDict(
                                    value="save",
                                    label="Save & Close",
                                ),
                            ],
                            mode=selector.SelectSelectorMode.LIST,
                        )
                    )
                }
            ),
        )

    # ── General Settings ──────────────────────────────────────────────

    async def async_step_general_settings(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Edit general settings."""
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_init()

        return self.async_show_form(
            step_id="general_settings",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_UPDATE_INTERVAL,
                        default=self._data.get(
                            CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=15, max=300, step=15, unit_of_measurement="seconds"
                        )
                    ),
                    vol.Required(
                        CONF_ENABLE_FOLLOW_ME,
                        default=self._data.get(
                            CONF_ENABLE_FOLLOW_ME, DEFAULT_ENABLE_FOLLOW_ME
                        ),
                    ): bool,
                    vol.Required(
                        CONF_ENABLE_ZONE_BALANCING,
                        default=self._data.get(
                            CONF_ENABLE_ZONE_BALANCING,
                            DEFAULT_ENABLE_ZONE_BALANCING,
                        ),
                    ): bool,
                    vol.Required(
                        CONF_OPERATION_MODE,
                        default=self._data.get(
                            CONF_OPERATION_MODE, DEFAULT_OPERATION_MODE
                        ),
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[
                                selector.SelectOptionDict(
                                    value="training",
                                    label="Training (observe only)",
                                ),
                                selector.SelectOptionDict(
                                    value="active",
                                    label="Active (full control)",
                                ),
                                selector.SelectOptionDict(
                                    value="disabled",
                                    label="Disabled (paused)",
                                ),
                            ],
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
        )

    # ── Manage Rooms ──────────────────────────────────────────────────

    async def async_step_manage_rooms(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Room management menu."""
        if user_input is not None:
            action = user_input.get("action")
            if action == "auto_detect":
                return await self.async_step_options_area_select()
            if action == "add_room":
                return await self.async_step_options_add_room()
            if action == "edit_room":
                return await self.async_step_options_select_room()
            if action == "remove_room":
                return await self.async_step_options_remove_room()
            if action == "done_rooms":
                return await self.async_step_init()

        room_count = len(self._rooms)
        room_names = (
            ", ".join(r[CONF_ROOM_NAME] for r in self._rooms)
            if self._rooms
            else "None"
        )

        options = [
            selector.SelectOptionDict(
                value="auto_detect",
                label="Auto-Detect from Areas",
            ),
            selector.SelectOptionDict(
                value="add_room",
                label="Add a Room Manually",
            ),
        ]
        if self._rooms:
            options.append(
                selector.SelectOptionDict(
                    value="edit_room", label="Edit a Room"
                )
            )
            options.append(
                selector.SelectOptionDict(
                    value="remove_room", label="Remove a Room"
                )
            )
        options.append(
            selector.SelectOptionDict(value="done_rooms", label="Done"),
        )

        return self.async_show_form(
            step_id="manage_rooms",
            data_schema=vol.Schema(
                {
                    vol.Required("action"): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=options,
                            mode=selector.SelectSelectorMode.LIST,
                        )
                    )
                }
            ),
            description_placeholders={
                "room_count": str(room_count),
                "room_names": room_names,
            },
        )

    async def async_step_options_area_select(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Auto-detect rooms from HA areas (options flow)."""
        if user_input is not None:
            selected_areas = user_input.get("areas", [])
            if selected_areas:
                _auto_detect_rooms_into(
                    self.hass, selected_areas, self._rooms
                )
            return await self.async_step_manage_rooms()

        try:
            area_reg = ar.async_get(self.hass)
            areas = list(area_reg.async_list_areas())
        except Exception:
            areas = []

        if not areas:
            return await self.async_step_manage_rooms()

        return self.async_show_form(
            step_id="options_area_select",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        "areas",
                        default=[a.id for a in areas],
                    ): selector.AreaSelector(
                        selector.AreaSelectorConfig(multiple=True)
                    ),
                }
            ),
        )

    async def async_step_options_add_room(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Add a room manually (options flow)."""
        if user_input is not None:
            room_data = {
                CONF_ROOM_NAME: user_input[CONF_ROOM_NAME],
                CONF_ROOM_SLUG: slugify(user_input[CONF_ROOM_NAME]),
                CONF_CLIMATE_ENTITY: user_input[CONF_CLIMATE_ENTITY],
                CONF_TEMP_SENSORS: user_input.get(CONF_TEMP_SENSORS, []),
                CONF_HUMIDITY_SENSORS: user_input.get(CONF_HUMIDITY_SENSORS, []),
                CONF_PRESENCE_SENSORS: user_input.get(CONF_PRESENCE_SENSORS, []),
                CONF_DOOR_WINDOW_SENSORS: user_input.get(
                    CONF_DOOR_WINDOW_SENSORS, []
                ),
                CONF_VENT_ENTITIES: user_input.get(CONF_VENT_ENTITIES, []),
                CONF_AUXILIARY_ENTITIES: user_input.get(
                    CONF_AUXILIARY_ENTITIES, []
                ),
                CONF_ROOM_PRIORITY: user_input.get(
                    CONF_ROOM_PRIORITY, DEFAULT_ROOM_PRIORITY
                ),
                CONF_TARGET_TEMP_OFFSET: user_input.get(
                    CONF_TARGET_TEMP_OFFSET, DEFAULT_TARGET_TEMP_OFFSET
                ),
            }
            self._rooms.append(room_data)
            return await self.async_step_manage_rooms()

        return self.async_show_form(
            step_id="options_add_room",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ROOM_NAME): str,
                    vol.Required(CONF_CLIMATE_ENTITY): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="climate")
                    ),
                    vol.Optional(CONF_TEMP_SENSORS): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain="sensor",
                            device_class="temperature",
                            multiple=True,
                        )
                    ),
                    vol.Optional(CONF_HUMIDITY_SENSORS): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain="sensor",
                            device_class="humidity",
                            multiple=True,
                        )
                    ),
                    vol.Optional(CONF_PRESENCE_SENSORS): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain="binary_sensor",
                            multiple=True,
                        )
                    ),
                    vol.Optional(
                        CONF_DOOR_WINDOW_SENSORS
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain="binary_sensor",
                            multiple=True,
                        )
                    ),
                    vol.Optional(CONF_VENT_ENTITIES): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain=["cover", "switch", "number"],
                            multiple=True,
                        )
                    ),
                    vol.Optional(
                        CONF_AUXILIARY_ENTITIES
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain=["climate", "switch", "fan"],
                            multiple=True,
                        )
                    ),
                    vol.Optional(
                        CONF_ROOM_PRIORITY, default=DEFAULT_ROOM_PRIORITY
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1, max=10, step=1,
                            mode=selector.NumberSelectorMode.SLIDER,
                        )
                    ),
                    vol.Optional(
                        CONF_TARGET_TEMP_OFFSET, default=DEFAULT_TARGET_TEMP_OFFSET
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=-10.0, max=10.0, step=0.5,
                            unit_of_measurement="°",
                        )
                    ),
                }
            ),
        )

    async def async_step_options_select_room(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Select a room to edit (options flow)."""
        if user_input is not None:
            room_slug = user_input.get("room_to_edit")
            for idx, room in enumerate(self._rooms):
                if room.get(CONF_ROOM_SLUG) == room_slug:
                    self._editing_room_index = idx
                    return await self.async_step_options_edit_room()
            return await self.async_step_manage_rooms()

        room_options = [
            selector.SelectOptionDict(
                value=r[CONF_ROOM_SLUG], label=r[CONF_ROOM_NAME]
            )
            for r in self._rooms
        ]

        return self.async_show_form(
            step_id="options_select_room",
            data_schema=vol.Schema(
                {
                    vol.Required("room_to_edit"): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=room_options,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
        )

    async def async_step_options_edit_room(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Edit an existing room's configuration (options flow)."""
        idx = self._editing_room_index
        if idx is None or idx >= len(self._rooms):
            return await self.async_step_manage_rooms()

        room = self._rooms[idx]

        if user_input is not None:
            # Update the room in-place, preserve slug
            room[CONF_ROOM_NAME] = user_input[CONF_ROOM_NAME]
            room[CONF_CLIMATE_ENTITY] = user_input[CONF_CLIMATE_ENTITY]
            room[CONF_TEMP_SENSORS] = user_input.get(CONF_TEMP_SENSORS, [])
            room[CONF_HUMIDITY_SENSORS] = user_input.get(CONF_HUMIDITY_SENSORS, [])
            room[CONF_PRESENCE_SENSORS] = user_input.get(CONF_PRESENCE_SENSORS, [])
            room[CONF_DOOR_WINDOW_SENSORS] = user_input.get(
                CONF_DOOR_WINDOW_SENSORS, []
            )
            room[CONF_VENT_ENTITIES] = user_input.get(CONF_VENT_ENTITIES, [])
            room[CONF_AUXILIARY_ENTITIES] = user_input.get(
                CONF_AUXILIARY_ENTITIES, []
            )
            room[CONF_ROOM_PRIORITY] = user_input.get(
                CONF_ROOM_PRIORITY, DEFAULT_ROOM_PRIORITY
            )
            room[CONF_TARGET_TEMP_OFFSET] = user_input.get(
                CONF_TARGET_TEMP_OFFSET, DEFAULT_TARGET_TEMP_OFFSET
            )
            self._editing_room_index = None
            return await self.async_step_manage_rooms()

        return self.async_show_form(
            step_id="options_edit_room",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_ROOM_NAME, default=room.get(CONF_ROOM_NAME, "")
                    ): str,
                    vol.Required(
                        CONF_CLIMATE_ENTITY,
                        default=room.get(CONF_CLIMATE_ENTITY, ""),
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(domain="climate")
                    ),
                    vol.Optional(
                        CONF_TEMP_SENSORS,
                        default=room.get(CONF_TEMP_SENSORS, []),
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain="sensor",
                            device_class="temperature",
                            multiple=True,
                        )
                    ),
                    vol.Optional(
                        CONF_HUMIDITY_SENSORS,
                        default=room.get(CONF_HUMIDITY_SENSORS, []),
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain="sensor",
                            device_class="humidity",
                            multiple=True,
                        )
                    ),
                    vol.Optional(
                        CONF_PRESENCE_SENSORS,
                        default=room.get(CONF_PRESENCE_SENSORS, []),
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain="binary_sensor",
                            multiple=True,
                        )
                    ),
                    vol.Optional(
                        CONF_DOOR_WINDOW_SENSORS,
                        default=room.get(CONF_DOOR_WINDOW_SENSORS, []),
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain="binary_sensor",
                            multiple=True,
                        )
                    ),
                    vol.Optional(
                        CONF_VENT_ENTITIES,
                        default=room.get(CONF_VENT_ENTITIES, []),
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain=["cover", "switch", "number"],
                            multiple=True,
                        )
                    ),
                    vol.Optional(
                        CONF_AUXILIARY_ENTITIES,
                        default=room.get(CONF_AUXILIARY_ENTITIES, []),
                    ): selector.EntitySelector(
                        selector.EntitySelectorConfig(
                            domain=["climate", "switch", "fan"],
                            multiple=True,
                        )
                    ),
                    vol.Optional(
                        CONF_ROOM_PRIORITY,
                        default=room.get(CONF_ROOM_PRIORITY, DEFAULT_ROOM_PRIORITY),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=1, max=10, step=1,
                            mode=selector.NumberSelectorMode.SLIDER,
                        )
                    ),
                    vol.Optional(
                        CONF_TARGET_TEMP_OFFSET,
                        default=room.get(
                            CONF_TARGET_TEMP_OFFSET, DEFAULT_TARGET_TEMP_OFFSET
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=-10.0, max=10.0, step=0.5,
                            unit_of_measurement="°",
                        )
                    ),
                }
            ),
            description_placeholders={
                "room_name": room.get(CONF_ROOM_NAME, ""),
            },
        )

    async def async_step_options_remove_room(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Remove a room (options flow)."""
        if user_input is not None:
            room_slug = user_input.get("room_to_remove")
            if room_slug:
                self._rooms = [
                    r for r in self._rooms if r[CONF_ROOM_SLUG] != room_slug
                ]
            return await self.async_step_manage_rooms()

        room_options = [
            selector.SelectOptionDict(
                value=r[CONF_ROOM_SLUG], label=r[CONF_ROOM_NAME]
            )
            for r in self._rooms
        ]

        return self.async_show_form(
            step_id="options_remove_room",
            data_schema=vol.Schema(
                {
                    vol.Required("room_to_remove"): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=room_options,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
        )

    # ── AI Settings ───────────────────────────────────────────────────

    async def async_step_ai_settings(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Edit AI provider settings."""
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_init()

        return self.async_show_form(
            step_id="ai_settings",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_AI_PROVIDER,
                        default=self._data.get(CONF_AI_PROVIDER, AI_PROVIDER_NONE),
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[
                                selector.SelectOptionDict(
                                    value=p,
                                    label=p.title()
                                    if p != "none"
                                    else "None (Disable AI)",
                                )
                                for p in AI_PROVIDERS
                            ],
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                    vol.Optional(
                        CONF_AI_API_KEY,
                        default=self._data.get(CONF_AI_API_KEY, ""),
                    ): str,
                    vol.Optional(
                        CONF_AI_MODEL,
                        default=self._data.get(CONF_AI_MODEL, ""),
                    ): str,
                    vol.Optional(
                        CONF_AI_BASE_URL,
                        default=self._data.get(CONF_AI_BASE_URL, ""),
                    ): str,
                    vol.Optional(
                        CONF_AI_AUTO_APPLY,
                        default=self._data.get(
                            CONF_AI_AUTO_APPLY, DEFAULT_AI_AUTO_APPLY
                        ),
                    ): bool,
                }
            ),
        )

    # ── Save & Exit ───────────────────────────────────────────────────

    async def _save_and_exit(self) -> FlowResult:
        """Persist all changes and close the options flow."""
        # Update rooms in config entry data
        self._data[CONF_ROOMS] = self._rooms
        self.hass.config_entries.async_update_entry(
            self._config_entry, data=self._data
        )
        return self.async_create_entry(title="", data={})
