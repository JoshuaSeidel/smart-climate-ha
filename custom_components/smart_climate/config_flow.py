"""Config flow for Smart Climate integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

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
    DEFAULT_ROOM_PRIORITY,
    DEFAULT_TARGET_TEMP_OFFSET,
    DEFAULT_TEMP_UNIT,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
)
from .models import slugify

_LOGGER = logging.getLogger(__name__)


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
                }
            ),
            errors=errors,
        )

    async def async_step_weather(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 2: Outdoor weather source."""
        if user_input is not None:
            self._data.update(user_input)
            return await self.async_step_room_menu()

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

    async def async_step_room_menu(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 3: Room menu - add rooms or finish."""
        if user_input is not None:
            if user_input.get("action") == "add_room":
                return await self.async_step_add_room()
            if user_input.get("action") == "finish_rooms":
                if not self._rooms:
                    return self.async_show_form(
                        step_id="room_menu",
                        data_schema=vol.Schema(
                            {
                                vol.Required("action"): selector.SelectSelector(
                                    selector.SelectSelectorConfig(
                                        options=[
                                            selector.SelectOptionDict(
                                                value="add_room",
                                                label="Add a Room",
                                            ),
                                            selector.SelectOptionDict(
                                                value="finish_rooms",
                                                label="Finish Room Setup",
                                            ),
                                        ],
                                        mode=selector.SelectSelectorMode.LIST,
                                    )
                                )
                            }
                        ),
                        errors={"base": "min_one_room"},
                    )
                return await self.async_step_schedule_menu()

        room_count = len(self._rooms)
        description_placeholders = {"room_count": str(room_count)}

        return self.async_show_form(
            step_id="room_menu",
            data_schema=vol.Schema(
                {
                    vol.Required("action"): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[
                                selector.SelectOptionDict(
                                    value="add_room", label="Add a Room"
                                ),
                                selector.SelectOptionDict(
                                    value="finish_rooms",
                                    label="Finish Room Setup",
                                ),
                            ],
                            mode=selector.SelectSelectorMode.LIST,
                        )
                    )
                }
            ),
            description_placeholders=description_placeholders,
        )

    async def async_step_add_room(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 4: Add a room."""
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
                            device_class="motion",
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

    async def async_step_schedule_menu(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 5: Schedule menu."""
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

    async def async_step_ai_provider(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Step 6: AI Provider configuration."""
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
    """Handle options flow for Smart Climate."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data = self._config_entry.data

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_UPDATE_INTERVAL,
                        default=data.get(
                            CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=15, max=300, step=15, unit_of_measurement="seconds"
                        )
                    ),
                    vol.Required(
                        CONF_ENABLE_FOLLOW_ME,
                        default=data.get(
                            CONF_ENABLE_FOLLOW_ME, DEFAULT_ENABLE_FOLLOW_ME
                        ),
                    ): bool,
                    vol.Required(
                        CONF_ENABLE_ZONE_BALANCING,
                        default=data.get(
                            CONF_ENABLE_ZONE_BALANCING,
                            DEFAULT_ENABLE_ZONE_BALANCING,
                        ),
                    ): bool,
                    vol.Optional(
                        CONF_AI_PROVIDER,
                        default=data.get(CONF_AI_PROVIDER, AI_PROVIDER_NONE),
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
                        default=data.get(CONF_AI_API_KEY, ""),
                    ): str,
                    vol.Optional(
                        CONF_AI_MODEL,
                        default=data.get(CONF_AI_MODEL, ""),
                    ): str,
                    vol.Optional(
                        CONF_AI_BASE_URL,
                        default=data.get(CONF_AI_BASE_URL, ""),
                    ): str,
                    vol.Optional(
                        CONF_AI_AUTO_APPLY,
                        default=data.get(
                            CONF_AI_AUTO_APPLY, DEFAULT_AI_AUTO_APPLY
                        ),
                    ): bool,
                }
            ),
        )
