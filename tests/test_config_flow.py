"""Tests for the Smart Climate config flow."""
from unittest.mock import MagicMock

from custom_components.smart_climate.const import (
    CONF_ENABLE_FOLLOW_ME,
    CONF_ENABLE_ZONE_BALANCING,
    CONF_INTEGRATION_NAME,
    CONF_ROOMS,
    CONF_SCHEDULES,
    CONF_TEMP_UNIT,
    CONF_UPDATE_INTERVAL,
)

# ---------------------------------------------------------------------------
# Tests for flow class structure and existence
# ---------------------------------------------------------------------------


class TestConfigFlowExists:
    """Verify that the config flow classes exist and have correct structure."""

    def test_config_flow_class_exists(self):
        """SmartClimateConfigFlow should be importable."""
        from custom_components.smart_climate.config_flow import SmartClimateConfigFlow

        flow = SmartClimateConfigFlow()
        assert flow is not None

    def test_config_flow_has_user_step(self):
        """Config flow should have async_step_user."""
        from custom_components.smart_climate.config_flow import SmartClimateConfigFlow

        flow = SmartClimateConfigFlow()
        assert hasattr(flow, "async_step_user")
        assert callable(flow.async_step_user)

    def test_config_flow_has_weather_step(self):
        """Config flow should have async_step_weather."""
        from custom_components.smart_climate.config_flow import SmartClimateConfigFlow

        flow = SmartClimateConfigFlow()
        assert hasattr(flow, "async_step_weather")
        assert callable(flow.async_step_weather)

    def test_config_flow_has_room_menu_step(self):
        """Config flow should have async_step_room_menu."""
        from custom_components.smart_climate.config_flow import SmartClimateConfigFlow

        flow = SmartClimateConfigFlow()
        assert hasattr(flow, "async_step_room_menu")
        assert callable(flow.async_step_room_menu)

    def test_config_flow_has_add_room_step(self):
        """Config flow should have async_step_add_room."""
        from custom_components.smart_climate.config_flow import SmartClimateConfigFlow

        flow = SmartClimateConfigFlow()
        assert hasattr(flow, "async_step_add_room")
        assert callable(flow.async_step_add_room)

    def test_config_flow_has_schedule_menu_step(self):
        """Config flow should have async_step_schedule_menu."""
        from custom_components.smart_climate.config_flow import SmartClimateConfigFlow

        flow = SmartClimateConfigFlow()
        assert hasattr(flow, "async_step_schedule_menu")
        assert callable(flow.async_step_schedule_menu)

    def test_config_flow_has_add_schedule_step(self):
        """Config flow should have async_step_add_schedule."""
        from custom_components.smart_climate.config_flow import SmartClimateConfigFlow

        flow = SmartClimateConfigFlow()
        assert hasattr(flow, "async_step_add_schedule")
        assert callable(flow.async_step_add_schedule)

    def test_config_flow_has_ai_provider_step(self):
        """Config flow should have async_step_ai_provider."""
        from custom_components.smart_climate.config_flow import SmartClimateConfigFlow

        flow = SmartClimateConfigFlow()
        assert hasattr(flow, "async_step_ai_provider")
        assert callable(flow.async_step_ai_provider)

    def test_config_flow_domain(self):
        """Config flow should be registered for the smart_climate domain."""
        from custom_components.smart_climate.config_flow import SmartClimateConfigFlow

        assert SmartClimateConfigFlow.VERSION == 1

    def test_config_flow_init_state(self):
        """Config flow should initialize with empty data/rooms/schedules."""
        from custom_components.smart_climate.config_flow import SmartClimateConfigFlow

        flow = SmartClimateConfigFlow()
        assert flow._data == {}
        assert flow._rooms == []
        assert flow._schedules == []


class TestOptionsFlowExists:
    """Verify that the options flow class exists and has correct structure."""

    def test_options_flow_class_exists(self):
        """SmartClimateOptionsFlow should be importable."""
        from custom_components.smart_climate.config_flow import SmartClimateOptionsFlow

        assert SmartClimateOptionsFlow is not None

    def test_options_flow_has_init_step(self):
        """Options flow should have async_step_init."""
        from custom_components.smart_climate.config_flow import SmartClimateOptionsFlow

        mock_entry = MagicMock()
        mock_entry.data = {
            CONF_UPDATE_INTERVAL: 60,
            CONF_ENABLE_FOLLOW_ME: True,
            CONF_ENABLE_ZONE_BALANCING: True,
        }
        flow = SmartClimateOptionsFlow(mock_entry)
        assert hasattr(flow, "async_step_init")
        assert callable(flow.async_step_init)

    def test_options_flow_stores_config_entry(self):
        """Options flow should store the config entry reference."""
        from custom_components.smart_climate.config_flow import SmartClimateOptionsFlow

        mock_entry = MagicMock()
        mock_entry.data = {}
        flow = SmartClimateOptionsFlow(mock_entry)
        assert flow._config_entry is mock_entry


# ---------------------------------------------------------------------------
# Tests for config flow internal data management
# ---------------------------------------------------------------------------


class TestConfigFlowDataManagement:
    """Test internal data management of the config flow."""

    def test_rooms_accumulate(self):
        """Adding rooms should append to internal list."""
        from custom_components.smart_climate.config_flow import SmartClimateConfigFlow

        flow = SmartClimateConfigFlow()
        flow._rooms.append({"room_name": "Living Room"})
        flow._rooms.append({"room_name": "Bedroom"})
        assert len(flow._rooms) == 2
        assert flow._rooms[0]["room_name"] == "Living Room"
        assert flow._rooms[1]["room_name"] == "Bedroom"

    def test_schedules_accumulate(self):
        """Adding schedules should append to internal list."""
        from custom_components.smart_climate.config_flow import SmartClimateConfigFlow

        flow = SmartClimateConfigFlow()
        flow._schedules.append({"schedule_name": "Night Mode"})
        assert len(flow._schedules) == 1

    def test_data_updates_merge(self):
        """Data updates should merge into the internal data dict."""
        from custom_components.smart_climate.config_flow import SmartClimateConfigFlow

        flow = SmartClimateConfigFlow()
        flow._data.update({CONF_INTEGRATION_NAME: "My Climate"})
        flow._data.update({CONF_TEMP_UNIT: "C"})
        assert flow._data[CONF_INTEGRATION_NAME] == "My Climate"
        assert flow._data[CONF_TEMP_UNIT] == "C"

    def test_flow_supports_options_flow(self):
        """Config flow should have async_get_options_flow static method."""
        from custom_components.smart_climate.config_flow import SmartClimateConfigFlow

        assert hasattr(SmartClimateConfigFlow, "async_get_options_flow")

    def test_final_data_includes_rooms_and_schedules(self):
        """Final config data should include rooms and schedules lists."""
        from custom_components.smart_climate.config_flow import SmartClimateConfigFlow

        flow = SmartClimateConfigFlow()
        room = {
            "room_name": "Test Room",
            "room_slug": "test_room",
            "climate_entity": "climate.test",
        }
        flow._rooms.append(room)
        flow._data[CONF_ROOMS] = flow._rooms
        flow._data[CONF_SCHEDULES] = flow._schedules

        assert len(flow._data[CONF_ROOMS]) == 1
        assert len(flow._data[CONF_SCHEDULES]) == 0
        assert flow._data[CONF_ROOMS][0]["room_name"] == "Test Room"
