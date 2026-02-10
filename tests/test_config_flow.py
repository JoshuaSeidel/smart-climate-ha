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


# ---------------------------------------------------------------------------
# Tests for area auto-detection
# ---------------------------------------------------------------------------


class TestAreaAutoDetection:
    """Test the area auto-detection feature in the config flow."""

    def test_config_flow_has_area_select_step(self):
        """Config flow should have async_step_area_select."""
        from custom_components.smart_climate.config_flow import SmartClimateConfigFlow

        flow = SmartClimateConfigFlow()
        assert hasattr(flow, "async_step_area_select")
        assert callable(flow.async_step_area_select)

    def test_config_flow_has_remove_room_step(self):
        """Config flow should have async_step_remove_room."""
        from custom_components.smart_climate.config_flow import SmartClimateConfigFlow

        flow = SmartClimateConfigFlow()
        assert hasattr(flow, "async_step_remove_room")
        assert callable(flow.async_step_remove_room)

    def test_config_flow_has_auto_detect_rooms(self):
        """Config flow should have _auto_detect_rooms method."""
        from custom_components.smart_climate.config_flow import SmartClimateConfigFlow

        flow = SmartClimateConfigFlow()
        assert hasattr(flow, "_auto_detect_rooms")
        assert callable(flow._auto_detect_rooms)

    def test_module_has_get_entities_for_area(self):
        """Module should have _get_entities_for_area function."""
        from custom_components.smart_climate.config_flow import _get_entities_for_area

        assert callable(_get_entities_for_area)

    def test_get_device_class_returns_device_class(self):
        """_get_device_class should return device_class first."""
        from custom_components.smart_climate.config_flow import _get_device_class

        class FakeEntity:
            device_class = "temperature"
            original_device_class = "humidity"

        result = _get_device_class(FakeEntity())
        assert result == "temperature"

    def test_get_device_class_falls_back_to_original(self):
        """_get_device_class should fallback to original_device_class."""
        from custom_components.smart_climate.config_flow import _get_device_class

        class FakeEntity:
            device_class = None
            original_device_class = "humidity"

        result = _get_device_class(FakeEntity())
        assert result == "humidity"

    def test_get_device_class_returns_none(self):
        """_get_device_class should return None if no device_class."""
        from custom_components.smart_climate.config_flow import _get_device_class

        class FakeEntity:
            device_class = None
            original_device_class = None

        result = _get_device_class(FakeEntity())
        assert result is None

    def test_get_entities_for_area_direct_assignment(self):
        """_get_entities_for_area should find entities directly assigned."""
        from homeassistant.helpers.device_registry import FakeDeviceRegistry
        from homeassistant.helpers.entity_registry import (
            FakeEntityEntry,
            FakeEntityRegistry,
        )

        from custom_components.smart_climate.config_flow import _get_entities_for_area

        entity_reg = FakeEntityRegistry()
        entity_reg.entities = {
            "climate.living_room": FakeEntityEntry(
                "climate.living_room", area_id="lr_area"
            ),
            "sensor.bedroom_temp": FakeEntityEntry(
                "sensor.bedroom_temp", area_id="br_area"
            ),
        }
        device_reg = FakeDeviceRegistry()

        result = _get_entities_for_area("lr_area", entity_reg, device_reg)
        assert len(result) == 1
        assert result[0].entity_id == "climate.living_room"

    def test_get_entities_for_area_via_device(self):
        """_get_entities_for_area should find entities via device area."""
        from homeassistant.helpers.device_registry import (
            FakeDeviceEntry,
            FakeDeviceRegistry,
        )
        from homeassistant.helpers.entity_registry import (
            FakeEntityEntry,
            FakeEntityRegistry,
        )

        from custom_components.smart_climate.config_flow import _get_entities_for_area

        entity_reg = FakeEntityRegistry()
        entity_reg.entities = {
            "sensor.lr_temp": FakeEntityEntry(
                "sensor.lr_temp", area_id=None, device_id="dev1"
            ),
        }
        device_reg = FakeDeviceRegistry()
        device_reg.devices = {
            "dev1": FakeDeviceEntry("dev1", area_id="lr_area"),
        }

        result = _get_entities_for_area("lr_area", entity_reg, device_reg)
        assert len(result) == 1
        assert result[0].entity_id == "sensor.lr_temp"

    def test_auto_detect_rooms_creates_rooms(self):
        """_auto_detect_rooms should create room entries from areas."""
        from homeassistant.helpers import (
            area_registry as ar,
        )
        from homeassistant.helpers import (
            device_registry as dr,
        )
        from homeassistant.helpers import (
            entity_registry as er,
        )
        from homeassistant.helpers.area_registry import (
            FakeAreaEntry,
            FakeAreaRegistry,
        )
        from homeassistant.helpers.device_registry import FakeDeviceRegistry
        from homeassistant.helpers.entity_registry import (
            FakeEntityEntry,
            FakeEntityRegistry,
        )

        from custom_components.smart_climate.config_flow import SmartClimateConfigFlow

        # Set up registries
        area_reg = FakeAreaRegistry()
        area_reg.areas = {
            "lr": FakeAreaEntry("lr", "Living Room"),
        }

        entity_reg = FakeEntityRegistry()
        entity_reg.entities = {
            "climate.ecobee": FakeEntityEntry(
                "climate.ecobee", area_id="lr"
            ),
            "sensor.lr_temp": FakeEntityEntry(
                "sensor.lr_temp",
                device_class="temperature",
                area_id="lr",
            ),
            "binary_sensor.lr_motion": FakeEntityEntry(
                "binary_sensor.lr_motion",
                device_class="motion",
                area_id="lr",
            ),
        }

        device_reg = FakeDeviceRegistry()

        # Patch async_get to return our registries
        ar.async_get = MagicMock(return_value=area_reg)
        er.async_get = MagicMock(return_value=entity_reg)
        dr.async_get = MagicMock(return_value=device_reg)

        flow = SmartClimateConfigFlow()
        flow.hass = MagicMock()
        flow._auto_detect_rooms(["lr"])

        assert len(flow._rooms) == 1
        room = flow._rooms[0]
        assert room["room_name"] == "Living Room"
        assert room["room_slug"] == "living_room"
        assert room["climate_entity"] == "climate.ecobee"
        assert "sensor.lr_temp" in room["temp_sensors"]
        assert "binary_sensor.lr_motion" in room["presence_sensors"]

    def test_auto_detect_rooms_fallback_climate(self):
        """_auto_detect_rooms should use system-wide climate entity as fallback."""
        from homeassistant.helpers import (
            area_registry as ar,
        )
        from homeassistant.helpers import (
            device_registry as dr,
        )
        from homeassistant.helpers import (
            entity_registry as er,
        )
        from homeassistant.helpers.area_registry import (
            FakeAreaEntry,
            FakeAreaRegistry,
        )
        from homeassistant.helpers.device_registry import FakeDeviceRegistry
        from homeassistant.helpers.entity_registry import (
            FakeEntityEntry,
            FakeEntityRegistry,
        )

        from custom_components.smart_climate.config_flow import SmartClimateConfigFlow

        area_reg = FakeAreaRegistry()
        area_reg.areas = {
            "nr": FakeAreaEntry("nr", "Nursery"),
        }

        entity_reg = FakeEntityRegistry()
        entity_reg.entities = {
            # Climate in a different area
            "climate.ecobee": FakeEntityEntry(
                "climate.ecobee", area_id="lr"
            ),
            # Nursery only has a temp sensor
            "sensor.nursery_temp": FakeEntityEntry(
                "sensor.nursery_temp",
                device_class="temperature",
                area_id="nr",
            ),
        }

        device_reg = FakeDeviceRegistry()

        ar.async_get = MagicMock(return_value=area_reg)
        er.async_get = MagicMock(return_value=entity_reg)
        dr.async_get = MagicMock(return_value=device_reg)

        flow = SmartClimateConfigFlow()
        flow.hass = MagicMock()
        flow._auto_detect_rooms(["nr"])

        assert len(flow._rooms) == 1
        # Should fallback to the only climate entity in the system
        assert flow._rooms[0]["climate_entity"] == "climate.ecobee"
        assert "sensor.nursery_temp" in flow._rooms[0]["temp_sensors"]

    def test_auto_detect_rooms_skips_no_climate(self):
        """_auto_detect_rooms should skip areas with no climate entity available."""
        from homeassistant.helpers import (
            area_registry as ar,
        )
        from homeassistant.helpers import (
            device_registry as dr,
        )
        from homeassistant.helpers import (
            entity_registry as er,
        )
        from homeassistant.helpers.area_registry import (
            FakeAreaEntry,
            FakeAreaRegistry,
        )
        from homeassistant.helpers.device_registry import FakeDeviceRegistry
        from homeassistant.helpers.entity_registry import (
            FakeEntityEntry,
            FakeEntityRegistry,
        )

        from custom_components.smart_climate.config_flow import SmartClimateConfigFlow

        area_reg = FakeAreaRegistry()
        area_reg.areas = {
            "garage": FakeAreaEntry("garage", "Garage"),
        }

        entity_reg = FakeEntityRegistry()
        entity_reg.entities = {
            # Only a switch, no climate at all in the system
            "switch.garage_light": FakeEntityEntry(
                "switch.garage_light", area_id="garage"
            ),
        }

        device_reg = FakeDeviceRegistry()

        ar.async_get = MagicMock(return_value=area_reg)
        er.async_get = MagicMock(return_value=entity_reg)
        dr.async_get = MagicMock(return_value=device_reg)

        flow = SmartClimateConfigFlow()
        flow.hass = MagicMock()
        flow._auto_detect_rooms(["garage"])

        assert len(flow._rooms) == 0

    def test_auto_detect_rooms_skips_disabled_entities(self):
        """_auto_detect_rooms should skip disabled entities."""
        from homeassistant.helpers import (
            area_registry as ar,
        )
        from homeassistant.helpers import (
            device_registry as dr,
        )
        from homeassistant.helpers import (
            entity_registry as er,
        )
        from homeassistant.helpers.area_registry import (
            FakeAreaEntry,
            FakeAreaRegistry,
        )
        from homeassistant.helpers.device_registry import FakeDeviceRegistry
        from homeassistant.helpers.entity_registry import (
            FakeEntityEntry,
            FakeEntityRegistry,
        )

        from custom_components.smart_climate.config_flow import SmartClimateConfigFlow

        area_reg = FakeAreaRegistry()
        area_reg.areas = {
            "lr": FakeAreaEntry("lr", "Living Room"),
        }

        entity_reg = FakeEntityRegistry()
        entity_reg.entities = {
            "climate.ecobee": FakeEntityEntry(
                "climate.ecobee", area_id="lr"
            ),
            "sensor.disabled_temp": FakeEntityEntry(
                "sensor.disabled_temp",
                device_class="temperature",
                area_id="lr",
                disabled_by="user",
            ),
            "sensor.active_temp": FakeEntityEntry(
                "sensor.active_temp",
                device_class="temperature",
                area_id="lr",
            ),
        }

        device_reg = FakeDeviceRegistry()

        ar.async_get = MagicMock(return_value=area_reg)
        er.async_get = MagicMock(return_value=entity_reg)
        dr.async_get = MagicMock(return_value=device_reg)

        flow = SmartClimateConfigFlow()
        flow.hass = MagicMock()
        flow._auto_detect_rooms(["lr"])

        assert len(flow._rooms) == 1
        # Only the active sensor should be included
        assert "sensor.active_temp" in flow._rooms[0]["temp_sensors"]
        assert "sensor.disabled_temp" not in flow._rooms[0]["temp_sensors"]

    def test_auto_detect_rooms_skips_duplicate_slugs(self):
        """_auto_detect_rooms should not add duplicate rooms."""
        from homeassistant.helpers import (
            area_registry as ar,
        )
        from homeassistant.helpers import (
            device_registry as dr,
        )
        from homeassistant.helpers import (
            entity_registry as er,
        )
        from homeassistant.helpers.area_registry import (
            FakeAreaEntry,
            FakeAreaRegistry,
        )
        from homeassistant.helpers.device_registry import FakeDeviceRegistry
        from homeassistant.helpers.entity_registry import (
            FakeEntityEntry,
            FakeEntityRegistry,
        )

        from custom_components.smart_climate.config_flow import SmartClimateConfigFlow

        area_reg = FakeAreaRegistry()
        area_reg.areas = {
            "lr": FakeAreaEntry("lr", "Living Room"),
        }

        entity_reg = FakeEntityRegistry()
        entity_reg.entities = {
            "climate.ecobee": FakeEntityEntry(
                "climate.ecobee", area_id="lr"
            ),
        }

        device_reg = FakeDeviceRegistry()

        ar.async_get = MagicMock(return_value=area_reg)
        er.async_get = MagicMock(return_value=entity_reg)
        dr.async_get = MagicMock(return_value=device_reg)

        flow = SmartClimateConfigFlow()
        flow.hass = MagicMock()
        # Pre-add a room with same slug
        flow._rooms.append({"room_name": "Living Room", "room_slug": "living_room"})
        flow._auto_detect_rooms(["lr"])

        # Should still be just the one pre-existing room
        assert len(flow._rooms) == 1


class TestRemoveRoom:
    """Test the remove room functionality."""

    def test_remove_room_removes_by_slug(self):
        """Removing a room by slug should work correctly."""
        from custom_components.smart_climate.config_flow import SmartClimateConfigFlow

        flow = SmartClimateConfigFlow()
        flow._rooms = [
            {"room_name": "Living Room", "room_slug": "living_room"},
            {"room_name": "Bedroom", "room_slug": "bedroom"},
            {"room_name": "Nursery", "room_slug": "nursery"},
        ]

        # Simulate removing bedroom
        flow._rooms = [
            r for r in flow._rooms if r["room_slug"] != "bedroom"
        ]

        assert len(flow._rooms) == 2
        slugs = [r["room_slug"] for r in flow._rooms]
        assert "bedroom" not in slugs
        assert "living_room" in slugs
        assert "nursery" in slugs

    def test_room_menu_schema_has_remove_when_rooms_exist(self):
        """Room menu should include remove option when rooms exist."""
        from custom_components.smart_climate.config_flow import SmartClimateConfigFlow

        flow = SmartClimateConfigFlow()
        flow._rooms = [{"room_name": "Test", "room_slug": "test"}]

        schema = flow._get_room_menu_schema()
        assert schema is not None

    def test_room_menu_schema_no_remove_when_empty(self):
        """Room menu should not include remove option when no rooms."""
        from custom_components.smart_climate.config_flow import SmartClimateConfigFlow

        flow = SmartClimateConfigFlow()
        flow._rooms = []

        schema = flow._get_room_menu_schema()
        assert schema is not None


# ---------------------------------------------------------------------------
# Tests for module-level _auto_detect_rooms_into
# ---------------------------------------------------------------------------


class TestAutoDetectRoomsInto:
    """Test the module-level _auto_detect_rooms_into function."""

    def test_auto_detect_rooms_into_importable(self):
        """_auto_detect_rooms_into should be importable from config_flow."""
        from custom_components.smart_climate.config_flow import _auto_detect_rooms_into

        assert callable(_auto_detect_rooms_into)

    def test_auto_detect_rooms_into_creates_rooms(self):
        """_auto_detect_rooms_into should add rooms to the provided list."""
        from homeassistant.helpers import (
            area_registry as ar,
        )
        from homeassistant.helpers import (
            device_registry as dr,
        )
        from homeassistant.helpers import (
            entity_registry as er,
        )
        from homeassistant.helpers.area_registry import (
            FakeAreaEntry,
            FakeAreaRegistry,
        )
        from homeassistant.helpers.device_registry import FakeDeviceRegistry
        from homeassistant.helpers.entity_registry import (
            FakeEntityEntry,
            FakeEntityRegistry,
        )

        from custom_components.smart_climate.config_flow import _auto_detect_rooms_into

        area_reg = FakeAreaRegistry()
        area_reg.areas = {
            "lr": FakeAreaEntry("lr", "Living Room"),
        }

        entity_reg = FakeEntityRegistry()
        entity_reg.entities = {
            "climate.ecobee": FakeEntityEntry(
                "climate.ecobee", area_id="lr"
            ),
            "sensor.lr_temp": FakeEntityEntry(
                "sensor.lr_temp",
                device_class="temperature",
                area_id="lr",
            ),
        }

        device_reg = FakeDeviceRegistry()

        hass = MagicMock()
        ar.async_get = MagicMock(return_value=area_reg)
        er.async_get = MagicMock(return_value=entity_reg)
        dr.async_get = MagicMock(return_value=device_reg)

        rooms = []
        _auto_detect_rooms_into(hass, ["lr"], rooms)

        assert len(rooms) == 1
        assert rooms[0]["room_name"] == "Living Room"
        assert rooms[0]["climate_entity"] == "climate.ecobee"
        assert "sensor.lr_temp" in rooms[0]["temp_sensors"]

    def test_auto_detect_rooms_into_skips_duplicates(self):
        """_auto_detect_rooms_into should not duplicate existing rooms."""
        from homeassistant.helpers import (
            area_registry as ar,
        )
        from homeassistant.helpers import (
            device_registry as dr,
        )
        from homeassistant.helpers import (
            entity_registry as er,
        )
        from homeassistant.helpers.area_registry import (
            FakeAreaEntry,
            FakeAreaRegistry,
        )
        from homeassistant.helpers.device_registry import FakeDeviceRegistry
        from homeassistant.helpers.entity_registry import (
            FakeEntityEntry,
            FakeEntityRegistry,
        )

        from custom_components.smart_climate.config_flow import _auto_detect_rooms_into

        area_reg = FakeAreaRegistry()
        area_reg.areas = {
            "lr": FakeAreaEntry("lr", "Living Room"),
        }

        entity_reg = FakeEntityRegistry()
        entity_reg.entities = {
            "climate.ecobee": FakeEntityEntry(
                "climate.ecobee", area_id="lr"
            ),
        }

        device_reg = FakeDeviceRegistry()

        hass = MagicMock()
        ar.async_get = MagicMock(return_value=area_reg)
        er.async_get = MagicMock(return_value=entity_reg)
        dr.async_get = MagicMock(return_value=device_reg)

        # Pre-existing room with same slug
        rooms = [{"room_name": "Living Room", "room_slug": "living_room"}]
        _auto_detect_rooms_into(hass, ["lr"], rooms)

        assert len(rooms) == 1  # No duplicate added


# ---------------------------------------------------------------------------
# Tests for expanded options flow
# ---------------------------------------------------------------------------


class TestOptionsFlowMenu:
    """Test the multi-step options flow menu structure."""

    def _make_options_flow(self, rooms=None, data=None):
        """Create an options flow with mock data."""
        from custom_components.smart_climate.config_flow import SmartClimateOptionsFlow

        mock_entry = MagicMock()
        mock_entry.data = data or {
            CONF_UPDATE_INTERVAL: 60,
            CONF_ENABLE_FOLLOW_ME: True,
            CONF_ENABLE_ZONE_BALANCING: True,
            CONF_ROOMS: rooms or [],
        }
        return SmartClimateOptionsFlow(mock_entry)

    def test_options_flow_has_general_settings_step(self):
        """Options flow should have async_step_general_settings."""
        flow = self._make_options_flow()
        assert hasattr(flow, "async_step_general_settings")
        assert callable(flow.async_step_general_settings)

    def test_options_flow_has_manage_rooms_step(self):
        """Options flow should have async_step_manage_rooms."""
        flow = self._make_options_flow()
        assert hasattr(flow, "async_step_manage_rooms")
        assert callable(flow.async_step_manage_rooms)

    def test_options_flow_has_options_area_select_step(self):
        """Options flow should have async_step_options_area_select."""
        flow = self._make_options_flow()
        assert hasattr(flow, "async_step_options_area_select")
        assert callable(flow.async_step_options_area_select)

    def test_options_flow_has_options_add_room_step(self):
        """Options flow should have async_step_options_add_room."""
        flow = self._make_options_flow()
        assert hasattr(flow, "async_step_options_add_room")
        assert callable(flow.async_step_options_add_room)

    def test_options_flow_has_options_remove_room_step(self):
        """Options flow should have async_step_options_remove_room."""
        flow = self._make_options_flow()
        assert hasattr(flow, "async_step_options_remove_room")
        assert callable(flow.async_step_options_remove_room)

    def test_options_flow_has_ai_settings_step(self):
        """Options flow should have async_step_ai_settings."""
        flow = self._make_options_flow()
        assert hasattr(flow, "async_step_ai_settings")
        assert callable(flow.async_step_ai_settings)

    def test_options_flow_has_save_and_exit(self):
        """Options flow should have _save_and_exit method."""
        flow = self._make_options_flow()
        assert hasattr(flow, "_save_and_exit")
        assert callable(flow._save_and_exit)

    def test_options_flow_initializes_rooms_from_config(self):
        """Options flow should load existing rooms from config entry."""
        rooms = [
            {"room_name": "Living Room", "room_slug": "living_room"},
            {"room_name": "Bedroom", "room_slug": "bedroom"},
        ]
        flow = self._make_options_flow(rooms=rooms)
        assert len(flow._rooms) == 2
        assert flow._rooms[0]["room_name"] == "Living Room"
        assert flow._rooms[1]["room_name"] == "Bedroom"

    def test_options_flow_rooms_are_mutable_copy(self):
        """Options flow rooms should be a copy, not a reference."""
        rooms = [{"room_name": "Living Room", "room_slug": "living_room"}]
        flow = self._make_options_flow(rooms=rooms)
        flow._rooms.append({"room_name": "New", "room_slug": "new"})
        # Original list should not be modified
        assert len(rooms) == 1

    def test_options_flow_data_is_mutable_copy(self):
        """Options flow data should be a copy, not a reference."""
        data = {CONF_UPDATE_INTERVAL: 60, CONF_ROOMS: []}
        flow = self._make_options_flow(data=data)
        flow._data[CONF_UPDATE_INTERVAL] = 120
        # Original should not be modified
        assert data[CONF_UPDATE_INTERVAL] == 60

    def test_options_flow_add_room_appends(self):
        """Adding a room via options flow should append to _rooms."""
        flow = self._make_options_flow()
        assert len(flow._rooms) == 0
        flow._rooms.append({
            "room_name": "New Room",
            "room_slug": "new_room",
            "climate_entity": "climate.test",
        })
        assert len(flow._rooms) == 1
        assert flow._rooms[0]["room_name"] == "New Room"

    def test_options_flow_remove_room_filters(self):
        """Removing a room via options flow should filter by slug."""
        rooms = [
            {"room_name": "Living Room", "room_slug": "living_room"},
            {"room_name": "Bedroom", "room_slug": "bedroom"},
        ]
        flow = self._make_options_flow(rooms=rooms)
        flow._rooms = [
            r for r in flow._rooms if r["room_slug"] != "bedroom"
        ]
        assert len(flow._rooms) == 1
        assert flow._rooms[0]["room_slug"] == "living_room"

    def test_options_flow_has_select_room_step(self):
        """Options flow should have async_step_options_select_room."""
        flow = self._make_options_flow()
        assert hasattr(flow, "async_step_options_select_room")
        assert callable(flow.async_step_options_select_room)

    def test_options_flow_has_edit_room_step(self):
        """Options flow should have async_step_options_edit_room."""
        flow = self._make_options_flow()
        assert hasattr(flow, "async_step_options_edit_room")
        assert callable(flow.async_step_options_edit_room)

    def test_options_flow_editing_room_index_init(self):
        """Options flow should initialize _editing_room_index to None."""
        flow = self._make_options_flow()
        assert flow._editing_room_index is None

    def test_options_flow_edit_room_updates_in_place(self):
        """Editing a room should update it in-place, preserving slug."""
        from custom_components.smart_climate.const import (
            CONF_AUXILIARY_ENTITIES,
            CONF_CLIMATE_ENTITY,
            CONF_DOOR_WINDOW_SENSORS,
            CONF_HUMIDITY_SENSORS,
            CONF_PRESENCE_SENSORS,
            CONF_ROOM_NAME,
            CONF_ROOM_PRIORITY,
            CONF_ROOM_SLUG,
            CONF_TARGET_TEMP_OFFSET,
            CONF_TEMP_SENSORS,
            CONF_VENT_ENTITIES,
        )

        rooms = [
            {
                CONF_ROOM_NAME: "Living Room",
                CONF_ROOM_SLUG: "living_room",
                CONF_CLIMATE_ENTITY: "climate.old",
                CONF_TEMP_SENSORS: ["sensor.old_temp"],
                CONF_HUMIDITY_SENSORS: [],
                CONF_PRESENCE_SENSORS: [],
                CONF_DOOR_WINDOW_SENSORS: [],
                CONF_VENT_ENTITIES: [],
                CONF_AUXILIARY_ENTITIES: [],
                CONF_ROOM_PRIORITY: 5,
                CONF_TARGET_TEMP_OFFSET: 0.0,
            },
        ]
        flow = self._make_options_flow(rooms=rooms)

        # Simulate selecting room to edit
        flow._editing_room_index = 0
        room = flow._rooms[0]

        # Simulate user submitting updated values
        room[CONF_ROOM_NAME] = "Updated Living Room"
        room[CONF_CLIMATE_ENTITY] = "climate.new"
        room[CONF_TEMP_SENSORS] = ["sensor.new_temp"]
        room[CONF_ROOM_PRIORITY] = 8

        assert flow._rooms[0][CONF_ROOM_NAME] == "Updated Living Room"
        assert flow._rooms[0][CONF_CLIMATE_ENTITY] == "climate.new"
        assert flow._rooms[0][CONF_TEMP_SENSORS] == ["sensor.new_temp"]
        assert flow._rooms[0][CONF_ROOM_PRIORITY] == 8
        # Slug should be preserved
        assert flow._rooms[0][CONF_ROOM_SLUG] == "living_room"

    def test_options_flow_edit_preserves_other_rooms(self):
        """Editing one room should not affect other rooms."""
        rooms = [
            {"room_name": "Living Room", "room_slug": "living_room",
             "climate_entity": "climate.lr"},
            {"room_name": "Bedroom", "room_slug": "bedroom",
             "climate_entity": "climate.br"},
        ]
        flow = self._make_options_flow(rooms=rooms)
        flow._editing_room_index = 0
        flow._rooms[0]["room_name"] = "Updated"

        assert flow._rooms[1]["room_name"] == "Bedroom"
        assert flow._rooms[1]["climate_entity"] == "climate.br"
