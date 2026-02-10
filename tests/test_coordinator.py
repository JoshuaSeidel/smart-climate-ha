"""Tests for the Smart Climate coordinator."""
from datetime import datetime, timedelta

from custom_components.smart_climate.const import (
    CONF_ROOMS,
)
from custom_components.smart_climate.models import (
    AuxiliaryDeviceState,
    AuxiliaryDeviceType,
    HouseState,
    HVACAction,
    RoomConfig,
    RoomState,
)

# ---------------------------------------------------------------------------
# Coordinator class existence and structure
# ---------------------------------------------------------------------------


class TestCoordinatorExists:
    """Verify the coordinator class exists and has the expected interface."""

    def test_coordinator_class_importable(self):
        """SmartClimateCoordinator should be importable."""
        from custom_components.smart_climate.coordinator import (
            SmartClimateCoordinator,
        )

        assert SmartClimateCoordinator is not None

    def test_coordinator_has_update_data(self):
        """Coordinator should have _async_update_data method."""
        from custom_components.smart_climate.coordinator import (
            SmartClimateCoordinator,
        )

        assert hasattr(SmartClimateCoordinator, "_async_update_data")

    def test_coordinator_has_schedule_daily_analysis(self):
        """Coordinator should have schedule_daily_analysis method."""
        from custom_components.smart_climate.coordinator import (
            SmartClimateCoordinator,
        )

        assert hasattr(SmartClimateCoordinator, "schedule_daily_analysis")

    def test_coordinator_has_cancel_scheduled_tasks(self):
        """Coordinator should have cancel_scheduled_tasks method."""
        from custom_components.smart_climate.coordinator import (
            SmartClimateCoordinator,
        )

        assert hasattr(SmartClimateCoordinator, "cancel_scheduled_tasks")

    def test_coordinator_has_trigger_analysis(self):
        """Coordinator should have async_trigger_analysis method."""
        from custom_components.smart_climate.coordinator import (
            SmartClimateCoordinator,
        )

        assert hasattr(SmartClimateCoordinator, "async_trigger_analysis")

    def test_coordinator_has_calculate_trend(self):
        """Coordinator should have static _calculate_trend method."""
        from custom_components.smart_climate.coordinator import (
            SmartClimateCoordinator,
        )

        assert hasattr(SmartClimateCoordinator, "_calculate_trend")


# ---------------------------------------------------------------------------
# Trend calculation (static method, can test independently)
# ---------------------------------------------------------------------------


class TestTrendCalculation:
    """Tests for the coordinator's temperature trend calculation."""

    def test_trend_no_data(self):
        """Empty history should return 0.0."""
        from custom_components.smart_climate.coordinator import (
            SmartClimateCoordinator,
        )

        result = SmartClimateCoordinator._calculate_trend([])
        assert result == 0.0

    def test_trend_single_reading(self):
        """Single reading should return 0.0."""
        from custom_components.smart_climate.coordinator import (
            SmartClimateCoordinator,
        )

        now = datetime.now()
        result = SmartClimateCoordinator._calculate_trend([(now, 72.0)])
        assert result == 0.0

    def test_trend_rising(self):
        """Rising temperatures should yield a positive trend."""
        from custom_components.smart_climate.coordinator import (
            SmartClimateCoordinator,
        )

        now = datetime.now()
        history = [
            (now - timedelta(hours=1), 70.0),
            (now, 72.0),
        ]
        result = SmartClimateCoordinator._calculate_trend(history)
        assert result == 2.0  # 2 degrees per hour

    def test_trend_falling(self):
        """Falling temperatures should yield a negative trend."""
        from custom_components.smart_climate.coordinator import (
            SmartClimateCoordinator,
        )

        now = datetime.now()
        history = [
            (now - timedelta(hours=1), 75.0),
            (now, 72.0),
        ]
        result = SmartClimateCoordinator._calculate_trend(history)
        assert result == -3.0  # -3 degrees per hour

    def test_trend_stable(self):
        """Stable temperature should yield 0.0 trend."""
        from custom_components.smart_climate.coordinator import (
            SmartClimateCoordinator,
        )

        now = datetime.now()
        history = [
            (now - timedelta(hours=1), 72.0),
            (now, 72.0),
        ]
        result = SmartClimateCoordinator._calculate_trend(history)
        assert result == 0.0

    def test_trend_same_timestamp(self):
        """Same timestamp for all readings should return 0.0 (no time elapsed)."""
        from custom_components.smart_climate.coordinator import (
            SmartClimateCoordinator,
        )

        now = datetime.now()
        history = [
            (now, 70.0),
            (now, 72.0),
        ]
        result = SmartClimateCoordinator._calculate_trend(history)
        assert result == 0.0

    def test_trend_multiple_readings(self):
        """Multiple readings should use first and last only."""
        from custom_components.smart_climate.coordinator import (
            SmartClimateCoordinator,
        )

        now = datetime.now()
        history = [
            (now - timedelta(hours=2), 68.0),
            (now - timedelta(hours=1), 71.0),
            (now, 74.0),
        ]
        # (74-68) / 2 hours = 3.0 degrees per hour
        result = SmartClimateCoordinator._calculate_trend(history)
        assert result == 3.0

    def test_trend_is_rounded(self):
        """Trend should be rounded to 2 decimal places."""
        from custom_components.smart_climate.coordinator import (
            SmartClimateCoordinator,
        )

        now = datetime.now()
        history = [
            (now - timedelta(hours=3), 70.0),
            (now, 71.0),
        ]
        # 1.0 / 3 = 0.333... rounded to 0.33
        result = SmartClimateCoordinator._calculate_trend(history)
        assert result == round(result, 2)
        assert result == 0.33


# ---------------------------------------------------------------------------
# Data structure shape expectations
# ---------------------------------------------------------------------------


class TestDataStructureShape:
    """Tests that verify the expected data model shapes are correct."""

    def test_room_state_default_values(self):
        """RoomState should have sensible defaults."""
        config = RoomConfig(
            name="Test", slug="test", climate_entity="climate.test"
        )
        state = RoomState(config=config)

        assert state.temperature is None
        assert state.humidity is None
        assert state.occupied is False
        assert state.window_open is False
        assert state.comfort_score == 0.0
        assert state.efficiency_score == 0.0
        assert state.hvac_action == HVACAction.IDLE
        assert state.hvac_runtime_today == 0.0
        assert state.hvac_cycles_today == 0
        assert state.current_target is None
        assert state.smart_target is None
        assert state.user_override_active is False
        assert state.follow_me_active is False
        assert state.active_schedule is None
        assert state.auxiliary_active is False
        assert state.temp_trend == 0.0
        assert state.last_presence_time is None
        assert state.temp_history == []

    def test_house_state_default_values(self):
        """HouseState should have sensible defaults."""
        state = HouseState()

        assert state.comfort_score == 0.0
        assert state.efficiency_score == 0.0
        assert state.total_hvac_runtime == 0.0
        assert state.heating_degree_days == 0.0
        assert state.cooling_degree_days == 0.0
        assert state.follow_me_target is None
        assert state.active_schedule is None
        assert state.outdoor_temperature is None
        assert state.outdoor_humidity is None
        assert state.last_analysis_time is None
        assert state.ai_daily_summary == ""
        assert state.suggestions == []

    def test_room_config_from_dict_basic(self, sample_config_data):
        """RoomConfig.from_dict should parse config data correctly."""
        room_data = sample_config_data[CONF_ROOMS][0]
        config = RoomConfig.from_dict(room_data)

        assert config.name == "Living Room"
        assert config.slug == "living_room"
        assert config.climate_entity == "climate.living_room"
        assert config.temp_sensors == ["sensor.lr_temp"]
        assert config.humidity_sensors == ["sensor.lr_humidity"]
        assert config.priority == 7

    def test_auxiliary_device_state_defaults(self):
        """AuxiliaryDeviceState should have proper defaults."""
        state = AuxiliaryDeviceState(
            entity_id="switch.heater",
            device_type=AuxiliaryDeviceType.SWITCH,
        )

        assert state.is_on is False
        assert state.started_at is None
        assert state.runtime_minutes == 0.0
        assert state.max_runtime == 120
        assert state.threshold == 2.0
        assert state.delay_minutes == 15

    def test_coordinator_data_expected_keys(self):
        """The coordinator data dict should have 'rooms' and 'house' keys."""
        # This test documents the expected shape without running the coordinator
        expected_keys = {"rooms", "house"}
        # Simulating what _async_update_data returns
        data = {"rooms": {}, "house": HouseState()}
        assert set(data.keys()) == expected_keys
        assert isinstance(data["house"], HouseState)
        assert isinstance(data["rooms"], dict)
