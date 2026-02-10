"""Tests for service definitions, model helpers, scheduling, presence, vents, and auxiliary."""
from datetime import datetime, time, timedelta

from custom_components.smart_climate.const import (
    DEFAULT_AWAY_TEMP_OFFSET,
)
from custom_components.smart_climate.helpers.auxiliary import (
    FAN_SPEED_PER_DEGREE,
    calculate_fan_speed,
    should_disengage_auxiliary,
    should_engage_auxiliary,
)
from custom_components.smart_climate.helpers.presence import (
    calculate_follow_me_targets,
    determine_follow_me_target,
)
from custom_components.smart_climate.helpers.scheduling import (
    get_all_active_schedules,
    get_house_active_schedule,
    get_todays_schedules,
    get_winning_schedule,
    is_schedule_active_now,
    parse_time,
)
from custom_components.smart_climate.helpers.vents import (
    MIN_VENT_POSITION,
    calculate_vent_positions,
)
from custom_components.smart_climate.models import (
    AuxiliaryDeviceState,
    AuxiliaryDeviceType,
    HVACAction,
    RoomConfig,
    RoomState,
    Schedule,
    Suggestion,
    slugify,
)

# ---------------------------------------------------------------------------
# slugify function
# ---------------------------------------------------------------------------


class TestSlugify:
    """Tests for the slugify utility function."""

    def test_simple_name(self):
        """Simple name should be lowercased and spaces replaced."""
        assert slugify("Living Room") == "living_room"

    def test_strips_whitespace(self):
        """Leading/trailing whitespace should be stripped."""
        assert slugify("  Kitchen  ") == "kitchen"

    def test_special_characters_removed(self):
        """Special characters should be removed."""
        assert slugify("Baby's Room!") == "babys_room"

    def test_multiple_spaces(self):
        """Multiple spaces should be collapsed to one underscore."""
        assert slugify("Living   Room") == "living_room"

    def test_hyphens_converted(self):
        """Hyphens should be converted to underscores."""
        assert slugify("master-bedroom") == "master_bedroom"

    def test_already_slugified(self):
        """Already slugified string should remain unchanged."""
        assert slugify("living_room") == "living_room"

    def test_empty_string(self):
        """Empty string should return empty string."""
        assert slugify("") == ""

    def test_numbers_preserved(self):
        """Numbers should be preserved."""
        assert slugify("Room 2") == "room_2"


# ---------------------------------------------------------------------------
# RoomConfig from_dict / to_dict roundtrip
# ---------------------------------------------------------------------------


class TestRoomConfigSerialization:
    """Tests for RoomConfig serialization."""

    def test_from_dict_basic(self):
        """RoomConfig.from_dict should parse all fields."""
        data = {
            "room_name": "Kitchen",
            "room_slug": "kitchen",
            "climate_entity": "climate.kitchen",
            "temp_sensors": ["sensor.kitchen_temp"],
            "humidity_sensors": ["sensor.kitchen_humidity"],
            "presence_sensors": ["binary_sensor.kitchen_motion"],
            "door_window_sensors": ["binary_sensor.kitchen_door"],
            "vent_entities": ["cover.kitchen_vent"],
            "auxiliary_entities": ["switch.kitchen_heater"],
            "room_priority": 6,
            "target_temp_offset": 1.5,
        }
        config = RoomConfig.from_dict(data)

        assert config.name == "Kitchen"
        assert config.slug == "kitchen"
        assert config.climate_entity == "climate.kitchen"
        assert config.temp_sensors == ["sensor.kitchen_temp"]
        assert config.humidity_sensors == ["sensor.kitchen_humidity"]
        assert config.presence_sensors == ["binary_sensor.kitchen_motion"]
        assert config.door_window_sensors == ["binary_sensor.kitchen_door"]
        assert config.vent_entities == ["cover.kitchen_vent"]
        assert config.auxiliary_entities == ["switch.kitchen_heater"]
        assert config.priority == 6
        assert config.target_temp_offset == 1.5

    def test_from_dict_minimal(self):
        """RoomConfig.from_dict should work with only required fields."""
        data = {
            "room_name": "Test",
            "climate_entity": "climate.test",
        }
        config = RoomConfig.from_dict(data)
        assert config.name == "Test"
        assert config.slug == "test"
        assert config.temp_sensors == []
        assert config.priority == 5  # default

    def test_to_dict(self, sample_room_config):
        """RoomConfig.to_dict should serialize all fields."""
        data = sample_room_config.to_dict()
        assert data["room_name"] == "Living Room"
        assert data["room_slug"] == "living_room"
        assert data["climate_entity"] == "climate.living_room"
        assert data["temp_sensors"] == ["sensor.lr_temp"]
        assert data["room_priority"] == 7

    def test_roundtrip(self, sample_room_config):
        """from_dict(to_dict(config)) should produce equivalent config."""
        data = sample_room_config.to_dict()
        restored = RoomConfig.from_dict(data)
        assert restored.name == sample_room_config.name
        assert restored.slug == sample_room_config.slug
        assert restored.climate_entity == sample_room_config.climate_entity
        assert restored.temp_sensors == sample_room_config.temp_sensors
        assert restored.priority == sample_room_config.priority
        assert restored.target_temp_offset == sample_room_config.target_temp_offset

    def test_from_dict_auto_generates_slug(self):
        """from_dict should auto-generate slug from name if not provided."""
        data = {
            "room_name": "Master Bedroom",
            "climate_entity": "climate.master",
        }
        config = RoomConfig.from_dict(data)
        assert config.slug == "master_bedroom"


# ---------------------------------------------------------------------------
# Schedule from_dict / to_dict roundtrip
# ---------------------------------------------------------------------------


class TestScheduleSerialization:
    """Tests for Schedule serialization."""

    def test_from_dict(self):
        """Schedule.from_dict should parse all fields."""
        data = {
            "schedule_name": "Morning Warmup",
            "schedule_slug": "morning_warmup",
            "schedule_rooms": ["living_room", "kitchen"],
            "schedule_days": [0, 1, 2, 3, 4],
            "schedule_start_time": "06:00",
            "schedule_end_time": "08:00",
            "schedule_target_temp": 72.0,
            "schedule_hvac_mode": "heat",
            "schedule_use_auxiliary": True,
            "schedule_priority": 7,
            "schedule_enabled": True,
        }
        schedule = Schedule.from_dict(data)
        assert schedule.name == "Morning Warmup"
        assert schedule.slug == "morning_warmup"
        assert schedule.rooms == ["living_room", "kitchen"]
        assert schedule.days == [0, 1, 2, 3, 4]
        assert schedule.start_time == "06:00"
        assert schedule.end_time == "08:00"
        assert schedule.target_temperature == 72.0
        assert schedule.hvac_mode == "heat"
        assert schedule.use_auxiliary is True
        assert schedule.priority == 7
        assert schedule.enabled is True

    def test_to_dict(self, sample_schedule):
        """Schedule.to_dict should serialize all fields."""
        data = sample_schedule.to_dict()
        assert data["schedule_name"] == "Baby Nap"
        assert data["schedule_slug"] == "baby_nap"
        assert data["schedule_rooms"] == ["nursery"]
        assert data["schedule_start_time"] == "13:00"
        assert data["schedule_target_temp"] == 70.0

    def test_roundtrip(self, sample_schedule):
        """from_dict(to_dict(schedule)) should produce equivalent schedule."""
        data = sample_schedule.to_dict()
        restored = Schedule.from_dict(data)
        assert restored.name == sample_schedule.name
        assert restored.slug == sample_schedule.slug
        assert restored.rooms == sample_schedule.rooms
        assert restored.days == sample_schedule.days
        assert restored.start_time == sample_schedule.start_time
        assert restored.end_time == sample_schedule.end_time
        assert restored.target_temperature == sample_schedule.target_temperature

    def test_from_dict_defaults(self):
        """from_dict with minimal fields should use sensible defaults."""
        data = {
            "schedule_name": "Test",
            "schedule_start_time": "09:00",
            "schedule_end_time": "17:00",
            "schedule_target_temp": 72.0,
        }
        schedule = Schedule.from_dict(data)
        assert schedule.rooms == ["__all__"]
        assert schedule.days == list(range(7))
        assert schedule.priority == 5
        assert schedule.enabled is True
        assert schedule.use_auxiliary is False


# ---------------------------------------------------------------------------
# Suggestion to_dict and is_expired
# ---------------------------------------------------------------------------


class TestSuggestionModel:
    """Tests for the Suggestion model."""

    def test_to_dict_all_fields(self, sample_suggestion):
        """to_dict should include all expected keys."""
        data = sample_suggestion.to_dict()
        expected_keys = {
            "id", "title", "description", "reasoning", "room",
            "action_type", "action_data", "confidence", "priority",
            "status", "created_at", "expires_at", "applied_at",
            "rejected_reason",
        }
        assert set(data.keys()) == expected_keys

    def test_is_expired_future(self):
        """Suggestion with future expiry should not be expired."""
        s = Suggestion(expires_at=datetime.now() + timedelta(hours=24))
        assert s.is_expired() is False

    def test_is_expired_past(self):
        """Suggestion with past expiry should be expired."""
        s = Suggestion(expires_at=datetime.now() - timedelta(seconds=1))
        assert s.is_expired() is True

    def test_is_expired_far_past(self):
        """Suggestion expired days ago should be expired."""
        s = Suggestion(expires_at=datetime.now() - timedelta(days=7))
        assert s.is_expired() is True


# ---------------------------------------------------------------------------
# Scheduling: is_schedule_active_now
# ---------------------------------------------------------------------------


class TestScheduleActive:
    """Tests for is_schedule_active_now."""

    def test_active_during_window(self, sample_schedule):
        """Schedule should be active during its time window on correct day."""
        # Monday at 14:00 (within 13:00-15:00)
        now = datetime(2024, 1, 1, 14, 0)  # Monday
        assert is_schedule_active_now(sample_schedule, now) is True

    def test_inactive_outside_window(self, sample_schedule):
        """Schedule should be inactive outside its time window."""
        # Monday at 16:00 (after 15:00)
        now = datetime(2024, 1, 1, 16, 0)  # Monday
        assert is_schedule_active_now(sample_schedule, now) is False

    def test_inactive_wrong_day(self, sample_schedule):
        """Schedule should be inactive on days not in its day list."""
        # Saturday at 14:00 (sample_schedule is Mon-Fri only)
        now = datetime(2024, 1, 6, 14, 0)  # Saturday
        assert is_schedule_active_now(sample_schedule, now) is False

    def test_inactive_when_disabled(self, sample_schedule):
        """Disabled schedule should never be active."""
        sample_schedule.enabled = False
        now = datetime(2024, 1, 1, 14, 0)  # Monday at 14:00
        assert is_schedule_active_now(sample_schedule, now) is False

    def test_overnight_schedule(self, sample_schedule_night):
        """Overnight schedule (22:00-06:00) should be active at 23:00."""
        # Monday at 23:00
        now = datetime(2024, 1, 1, 23, 0)  # Monday
        assert is_schedule_active_now(sample_schedule_night, now) is True

    def test_overnight_schedule_early_morning(self, sample_schedule_night):
        """Overnight schedule should be active at 02:00."""
        now = datetime(2024, 1, 1, 2, 0)  # Monday
        assert is_schedule_active_now(sample_schedule_night, now) is True

    def test_overnight_schedule_inactive_midday(self, sample_schedule_night):
        """Overnight schedule should be inactive at 12:00."""
        now = datetime(2024, 1, 1, 12, 0)  # Monday
        assert is_schedule_active_now(sample_schedule_night, now) is False

    def test_at_start_time_boundary(self, sample_schedule):
        """Schedule should be active at exactly start_time."""
        now = datetime(2024, 1, 1, 13, 0)  # Monday at 13:00
        assert is_schedule_active_now(sample_schedule, now) is True

    def test_at_end_time_boundary(self, sample_schedule):
        """Schedule should be active at exactly end_time."""
        now = datetime(2024, 1, 1, 15, 0)  # Monday at 15:00
        assert is_schedule_active_now(sample_schedule, now) is True


# ---------------------------------------------------------------------------
# Scheduling: get_winning_schedule
# ---------------------------------------------------------------------------


class TestGetWinningSchedule:
    """Tests for get_winning_schedule with overlapping schedules."""

    def test_no_active_returns_none(self, sample_schedule):
        """Should return None when no schedules are active."""
        now = datetime(2024, 1, 1, 16, 0)  # Outside window
        result = get_winning_schedule([sample_schedule], "nursery", now)
        assert result is None

    def test_single_active_schedule(self, sample_schedule):
        """Should return the only active schedule."""
        now = datetime(2024, 1, 1, 14, 0)  # Within window
        result = get_winning_schedule([sample_schedule], "nursery", now)
        assert result is not None
        assert result.name == "Baby Nap"

    def test_room_not_in_schedule(self, sample_schedule):
        """Should return None if room is not covered by active schedule."""
        now = datetime(2024, 1, 1, 14, 0)
        result = get_winning_schedule([sample_schedule], "living_room", now)
        assert result is None

    def test_all_rooms_schedule_matches_any_room(self, sample_schedule_night):
        """__all__ rooms schedule should match any room slug."""
        now = datetime(2024, 1, 1, 23, 0)
        result = get_winning_schedule(
            [sample_schedule_night], "living_room", now
        )
        assert result is not None
        assert result.name == "Night Mode"

    def test_highest_priority_wins(self, sample_schedule, sample_schedule_night):
        """When multiple schedules apply, highest priority should win."""
        # Both active, nursery matched by both (nap=priority 8, night=priority 5)
        # Make night schedule also apply to nursery
        sample_schedule_night.rooms = ["__all__"]
        now = datetime(2024, 1, 1, 23, 0)

        # Only night mode is active at 23:00 (nap is 13-15)
        result = get_winning_schedule(
            [sample_schedule, sample_schedule_night], "nursery", now
        )
        assert result is not None
        assert result.name == "Night Mode"

    def test_overlapping_schedules_priority_resolution(self):
        """When two schedules overlap, higher priority wins."""
        s1 = Schedule(
            name="Low Priority",
            slug="low",
            rooms=["__all__"],
            days=list(range(7)),
            start_time="08:00",
            end_time="20:00",
            target_temperature=72.0,
            priority=3,
            enabled=True,
        )
        s2 = Schedule(
            name="High Priority",
            slug="high",
            rooms=["living_room"],
            days=list(range(7)),
            start_time="08:00",
            end_time="20:00",
            target_temperature=68.0,
            priority=8,
            enabled=True,
        )
        now = datetime(2024, 1, 1, 12, 0)  # Monday noon
        result = get_winning_schedule([s1, s2], "living_room", now)
        assert result.name == "High Priority"

    def test_get_all_active_schedules_multiple_rooms(self):
        """get_all_active_schedules should return per-room winners."""
        s1 = Schedule(
            name="All Rooms",
            slug="all",
            rooms=["__all__"],
            days=list(range(7)),
            start_time="08:00",
            end_time="20:00",
            target_temperature=72.0,
            priority=3,
            enabled=True,
        )
        now = datetime(2024, 1, 1, 12, 0)
        result = get_all_active_schedules(
            [s1], ["living_room", "nursery"], now
        )
        assert result["living_room"] is not None
        assert result["nursery"] is not None
        assert result["living_room"].name == "All Rooms"


# ---------------------------------------------------------------------------
# Scheduling: get_house_active_schedule
# ---------------------------------------------------------------------------


class TestHouseActiveSchedule:
    """Tests for get_house_active_schedule."""

    def test_returns_none_when_no_house_schedule(self, sample_schedule):
        """Should return None when no __all__ schedule is active."""
        now = datetime(2024, 1, 1, 14, 0)
        result = get_house_active_schedule([sample_schedule], now)
        # sample_schedule is for nursery only, not __all__
        assert result is None

    def test_returns_name_of_house_schedule(self, sample_schedule_night):
        """Should return the name of active __all__ schedule."""
        now = datetime(2024, 1, 1, 23, 0)
        result = get_house_active_schedule([sample_schedule_night], now)
        assert result == "Night Mode"


# ---------------------------------------------------------------------------
# Scheduling: get_todays_schedules
# ---------------------------------------------------------------------------


class TestGetTodaysSchedules:
    """Tests for get_todays_schedules."""

    def test_returns_schedules_for_today(self, sample_schedule):
        """Should return schedules that run on today's day of week."""
        now = datetime(2024, 1, 1, 10, 0)  # Monday
        result = get_todays_schedules([sample_schedule], now)
        assert len(result) == 1

    def test_excludes_disabled(self, sample_schedule):
        """Should exclude disabled schedules."""
        sample_schedule.enabled = False
        now = datetime(2024, 1, 1, 10, 0)  # Monday
        result = get_todays_schedules([sample_schedule], now)
        assert len(result) == 0

    def test_excludes_other_days(self, sample_schedule):
        """Should exclude schedules not running today."""
        now = datetime(2024, 1, 6, 10, 0)  # Saturday
        result = get_todays_schedules([sample_schedule], now)
        assert len(result) == 0


# ---------------------------------------------------------------------------
# parse_time
# ---------------------------------------------------------------------------


class TestParseTime:
    """Tests for the parse_time helper."""

    def test_basic_time(self):
        """Should parse HH:MM format."""
        result = parse_time("13:30")
        assert result == time(13, 30)

    def test_midnight(self):
        """Should parse midnight."""
        result = parse_time("00:00")
        assert result == time(0, 0)

    def test_end_of_day(self):
        """Should parse 23:59."""
        result = parse_time("23:59")
        assert result == time(23, 59)


# ---------------------------------------------------------------------------
# Presence: determine_follow_me_target
# ---------------------------------------------------------------------------


class TestDetermineFollowMeTarget:
    """Tests for the follow-me target determination."""

    def test_no_occupied_rooms(self, sample_room_state, sample_room_state_2):
        """Should return None when no rooms are occupied."""
        sample_room_state.occupied = False
        sample_room_state_2.occupied = False
        rooms = {
            "living_room": sample_room_state,
            "nursery": sample_room_state_2,
        }
        result = determine_follow_me_target(rooms)
        assert result is None

    def test_single_occupied_room(self, sample_room_state, sample_room_state_2):
        """Should return the only occupied room."""
        sample_room_state.occupied = True
        sample_room_state_2.occupied = False
        rooms = {
            "living_room": sample_room_state,
            "nursery": sample_room_state_2,
        }
        result = determine_follow_me_target(rooms)
        assert result == "living_room"

    def test_most_recent_presence_wins(self, sample_room_state, sample_room_state_2):
        """Most recently occupied room should win."""
        now = datetime.now()
        sample_room_state.occupied = True
        sample_room_state.last_presence_time = now - timedelta(minutes=5)
        sample_room_state_2.occupied = True
        sample_room_state_2.last_presence_time = now
        rooms = {
            "living_room": sample_room_state,
            "nursery": sample_room_state_2,
        }
        result = determine_follow_me_target(rooms)
        assert result == "nursery"

    def test_cooldown_prevents_thrashing(
        self, sample_room_state, sample_room_state_2
    ):
        """Cooldown should prevent rapid switching between rooms."""
        now = datetime.now()
        # Current target is living_room, last presence was 2 min ago (< 10 min cooldown)
        sample_room_state.occupied = True
        sample_room_state.last_presence_time = now - timedelta(minutes=2)

        # Nursery has more recent presence
        sample_room_state_2.occupied = True
        sample_room_state_2.last_presence_time = now

        rooms = {
            "living_room": sample_room_state,
            "nursery": sample_room_state_2,
        }
        # Current target is living_room, cooldown active
        result = determine_follow_me_target(
            rooms, current_target="living_room", cooldown_minutes=10
        )
        assert result == "living_room"

    def test_no_presence_sensors_excluded(self):
        """Rooms without presence sensors should be excluded."""
        config_no_sensors = RoomConfig(
            name="Garage",
            slug="garage",
            climate_entity="climate.garage",
            presence_sensors=[],
        )
        room = RoomState(
            config=config_no_sensors,
            occupied=True,
            last_presence_time=datetime.now(),
        )
        rooms = {"garage": room}
        result = determine_follow_me_target(rooms)
        assert result is None


# ---------------------------------------------------------------------------
# Presence: calculate_follow_me_targets
# ---------------------------------------------------------------------------


class TestCalculateFollowMeTargets:
    """Tests for follow-me temperature target calculation."""

    def test_primary_room_gets_target_plus_offset(
        self, sample_room_state
    ):
        """Primary room should get current_target + offset."""
        sample_room_state.current_target = 72.0
        sample_room_state.config.target_temp_offset = 0.0
        rooms = {"living_room": sample_room_state}
        targets = calculate_follow_me_targets(rooms, "living_room")
        assert targets["living_room"] == 72.0

    def test_primary_room_with_offset(self, sample_room_state):
        """Primary room with offset should adjust target."""
        sample_room_state.current_target = 72.0
        sample_room_state.config.target_temp_offset = 1.5
        rooms = {"living_room": sample_room_state}
        targets = calculate_follow_me_targets(rooms, "living_room")
        assert targets["living_room"] == 73.5

    def test_unoccupied_heating_lowers_target(self, sample_room_state_2):
        """Unoccupied room in heating mode should lower target."""
        sample_room_state_2.occupied = False
        sample_room_state_2.current_target = 70.0
        sample_room_state_2.hvac_action = HVACAction.HEATING
        rooms = {"nursery": sample_room_state_2}
        targets = calculate_follow_me_targets(rooms, None)
        assert targets["nursery"] == 70.0 - DEFAULT_AWAY_TEMP_OFFSET

    def test_unoccupied_cooling_raises_target(self, sample_room_state_2):
        """Unoccupied room in cooling mode should raise target."""
        sample_room_state_2.occupied = False
        sample_room_state_2.current_target = 70.0
        sample_room_state_2.hvac_action = HVACAction.COOLING
        rooms = {"nursery": sample_room_state_2}
        targets = calculate_follow_me_targets(rooms, None)
        assert targets["nursery"] == 70.0 + DEFAULT_AWAY_TEMP_OFFSET

    def test_none_target_returns_none(self, sample_room_state):
        """Room with None current_target should get None."""
        sample_room_state.current_target = None
        rooms = {"living_room": sample_room_state}
        targets = calculate_follow_me_targets(rooms, "living_room")
        assert targets["living_room"] is None

    def test_custom_away_offset(self, sample_room_state_2):
        """Custom away offset should be applied."""
        sample_room_state_2.occupied = False
        sample_room_state_2.current_target = 70.0
        sample_room_state_2.hvac_action = HVACAction.HEATING
        rooms = {"nursery": sample_room_state_2}
        targets = calculate_follow_me_targets(
            rooms, None, away_temp_offset=6.0
        )
        assert targets["nursery"] == 64.0


# ---------------------------------------------------------------------------
# Vents: calculate_vent_positions
# ---------------------------------------------------------------------------


class TestCalculateVentPositions:
    """Tests for smart vent position calculations."""

    def test_no_vents_returns_empty(self, sample_room_state_2):
        """Room without vent entities should be excluded."""
        rooms = {"nursery": sample_room_state_2}
        positions = calculate_vent_positions(rooms)
        assert "nursery" not in positions

    def test_window_open_closes_vents(self, sample_room_state, sample_room_state_2):
        """Open window should close vents (safety may bump to 40 with few rooms)."""
        sample_room_state.window_open = True
        sample_room_state.temperature = 72.0
        sample_room_state.current_target = 72.0
        # Add a second room with vents open to avoid safety ratio trigger
        sample_room_state_2.config.vent_entities = ["cover.nursery_vent"]
        sample_room_state_2.temperature = 70.0
        sample_room_state_2.current_target = 70.0
        sample_room_state_2.occupied = True
        rooms = {"living_room": sample_room_state, "nursery": sample_room_state_2}
        positions = calculate_vent_positions(rooms)
        assert "living_room" in positions
        for _eid, pos in positions["living_room"]:
            assert pos == MIN_VENT_POSITION

    def test_unoccupied_at_target_reduces_airflow(self, sample_room_state, sample_room_state_2):
        """Unoccupied room at target should reduce airflow."""
        sample_room_state.occupied = False
        sample_room_state.temperature = 72.0
        sample_room_state.current_target = 72.0
        sample_room_state.hvac_action = HVACAction.COOLING
        # Add a second occupied room with vents to avoid safety ratio trigger
        sample_room_state_2.config.vent_entities = ["cover.nursery_vent"]
        sample_room_state_2.temperature = 68.0
        sample_room_state_2.current_target = 70.0
        sample_room_state_2.occupied = True
        rooms = {"living_room": sample_room_state, "nursery": sample_room_state_2}
        positions = calculate_vent_positions(rooms)
        assert "living_room" in positions
        for _eid, pos in positions["living_room"]:
            assert pos <= 30

    def test_far_from_target_fully_open(self, sample_room_state):
        """Room far from target should have fully open vents."""
        sample_room_state.temperature = 68.0
        sample_room_state.current_target = 72.0
        sample_room_state.hvac_action = HVACAction.HEATING
        rooms = {"living_room": sample_room_state}
        positions = calculate_vent_positions(rooms)
        assert "living_room" in positions
        for _eid, pos in positions["living_room"]:
            assert pos == 100

    def test_near_target_moderate_position(self, sample_room_state):
        """Room near target should have moderate vent position."""
        sample_room_state.temperature = 71.8
        sample_room_state.current_target = 72.0
        sample_room_state.hvac_action = HVACAction.HEATING
        rooms = {"living_room": sample_room_state}
        positions = calculate_vent_positions(rooms)
        assert "living_room" in positions
        for _eid, pos in positions["living_room"]:
            # Small need (0.2) -> moderate position
            assert 50 <= pos <= 100

    def test_none_target_neutral_need(self, sample_room_state):
        """Room with None target should have 0 need."""
        sample_room_state.current_target = None
        rooms = {"living_room": sample_room_state}
        positions = calculate_vent_positions(rooms)
        # With need=0, falls into "near target" moderate
        assert "living_room" in positions


# ---------------------------------------------------------------------------
# Auxiliary: should_engage_auxiliary
# ---------------------------------------------------------------------------


class TestShouldEngageAuxiliary:
    """Tests for auxiliary device engagement logic."""

    def test_engage_when_all_conditions_met(self, sample_room_state):
        """Should engage when deviation exceeds threshold and HVAC is running."""
        sample_room_state.temperature = 76.0  # 4 degrees above target
        sample_room_state.hvac_action = HVACAction.COOLING
        sample_room_state.hvac_state_change_time = (
            datetime.now() - timedelta(minutes=20)
        )
        sample_room_state.temp_trend = 0.3  # Still warming (HVAC failing)

        result = should_engage_auxiliary(
            sample_room_state, target_temp=72.0, threshold=2.0, delay_minutes=15
        )
        assert result is True

    def test_no_engage_below_threshold(self, sample_room_state):
        """Should not engage when temp deviation is within threshold."""
        sample_room_state.temperature = 72.5
        sample_room_state.hvac_action = HVACAction.COOLING
        sample_room_state.hvac_state_change_time = (
            datetime.now() - timedelta(minutes=20)
        )
        result = should_engage_auxiliary(
            sample_room_state, target_temp=72.0, threshold=2.0
        )
        assert result is False

    def test_no_engage_hvac_idle(self, sample_room_state):
        """Should not engage when HVAC is idle."""
        sample_room_state.temperature = 76.0
        sample_room_state.hvac_action = HVACAction.IDLE
        sample_room_state.hvac_state_change_time = (
            datetime.now() - timedelta(minutes=20)
        )
        result = should_engage_auxiliary(
            sample_room_state, target_temp=72.0
        )
        assert result is False

    def test_no_engage_within_delay(self, sample_room_state):
        """Should not engage when HVAC hasn't been running long enough."""
        sample_room_state.temperature = 76.0
        sample_room_state.hvac_action = HVACAction.COOLING
        sample_room_state.hvac_state_change_time = (
            datetime.now() - timedelta(minutes=5)
        )
        sample_room_state.temp_trend = 0.3
        result = should_engage_auxiliary(
            sample_room_state, target_temp=72.0, delay_minutes=15
        )
        assert result is False

    def test_no_engage_hvac_keeping_up_cooling(self, sample_room_state):
        """Should not engage when HVAC is cooling effectively (temp dropping)."""
        sample_room_state.temperature = 76.0
        sample_room_state.hvac_action = HVACAction.COOLING
        sample_room_state.hvac_state_change_time = (
            datetime.now() - timedelta(minutes=20)
        )
        sample_room_state.temp_trend = -0.8  # Temperature is dropping -> HVAC working
        result = should_engage_auxiliary(
            sample_room_state, target_temp=72.0
        )
        assert result is False

    def test_no_engage_hvac_keeping_up_heating(self, sample_room_state):
        """Should not engage when HVAC is heating effectively (temp rising)."""
        sample_room_state.temperature = 66.0
        sample_room_state.hvac_action = HVACAction.HEATING
        sample_room_state.hvac_state_change_time = (
            datetime.now() - timedelta(minutes=20)
        )
        sample_room_state.temp_trend = 0.8  # Temperature is rising -> HVAC working
        result = should_engage_auxiliary(
            sample_room_state, target_temp=72.0
        )
        assert result is False

    def test_no_engage_none_temperature(self, sample_room_state):
        """Should not engage when temperature is None."""
        sample_room_state.temperature = None
        result = should_engage_auxiliary(
            sample_room_state, target_temp=72.0
        )
        assert result is False

    def test_no_engage_no_state_change_time(self, sample_room_state):
        """Should not engage when hvac_state_change_time is None."""
        sample_room_state.temperature = 76.0
        sample_room_state.hvac_action = HVACAction.COOLING
        sample_room_state.hvac_state_change_time = None
        result = should_engage_auxiliary(
            sample_room_state, target_temp=72.0
        )
        assert result is False


# ---------------------------------------------------------------------------
# Auxiliary: should_disengage_auxiliary
# ---------------------------------------------------------------------------


class TestShouldDisengageAuxiliary:
    """Tests for auxiliary device disengagement logic."""

    def test_disengage_within_threshold(self, sample_room_state):
        """Should disengage when temp is within DISENGAGE_THRESHOLD of target."""
        sample_room_state.temperature = 72.5  # within 1.0 of 72.0
        aux_state = AuxiliaryDeviceState(
            entity_id="switch.heater",
            device_type=AuxiliaryDeviceType.SWITCH,
            is_on=True,
            runtime_minutes=10.0,
        )
        result = should_disengage_auxiliary(
            sample_room_state, target_temp=72.0, aux_state=aux_state
        )
        assert result is True

    def test_disengage_max_runtime_exceeded(self, sample_room_state):
        """Should disengage when max runtime is exceeded (safety)."""
        sample_room_state.temperature = 76.0  # Still far from target
        aux_state = AuxiliaryDeviceState(
            entity_id="switch.heater",
            device_type=AuxiliaryDeviceType.SWITCH,
            is_on=True,
            runtime_minutes=130.0,
            max_runtime=120,
        )
        result = should_disengage_auxiliary(
            sample_room_state, target_temp=72.0, aux_state=aux_state
        )
        assert result is True

    def test_no_disengage_still_needed(self, sample_room_state):
        """Should not disengage when temp is still far from target."""
        sample_room_state.temperature = 76.0  # > 1.0 from 72.0
        aux_state = AuxiliaryDeviceState(
            entity_id="switch.heater",
            device_type=AuxiliaryDeviceType.SWITCH,
            is_on=True,
            runtime_minutes=10.0,
        )
        result = should_disengage_auxiliary(
            sample_room_state, target_temp=72.0, aux_state=aux_state
        )
        assert result is False

    def test_disengage_none_temperature(self, sample_room_state):
        """Should disengage when temperature reading is None (safety)."""
        sample_room_state.temperature = None
        aux_state = AuxiliaryDeviceState(
            entity_id="switch.heater",
            device_type=AuxiliaryDeviceType.SWITCH,
            is_on=True,
            runtime_minutes=10.0,
        )
        result = should_disengage_auxiliary(
            sample_room_state, target_temp=72.0, aux_state=aux_state
        )
        assert result is True


# ---------------------------------------------------------------------------
# Auxiliary: calculate_fan_speed
# ---------------------------------------------------------------------------


class TestCalculateFanSpeed:
    """Tests for fan speed calculation."""

    def test_zero_deviation(self):
        """Zero deviation should give 0% fan speed."""
        assert calculate_fan_speed(0.0) == 0

    def test_one_degree_deviation(self):
        """1 degree deviation should give FAN_SPEED_PER_DEGREE%."""
        assert calculate_fan_speed(1.0) == FAN_SPEED_PER_DEGREE

    def test_two_degree_deviation(self):
        """2 degrees should give 2 * FAN_SPEED_PER_DEGREE%."""
        assert calculate_fan_speed(2.0) == 2 * FAN_SPEED_PER_DEGREE

    def test_large_deviation_capped_at_100(self):
        """Large deviation should cap at 100%."""
        assert calculate_fan_speed(10.0) == 100

    def test_negative_deviation_uses_absolute(self):
        """Negative deviation should be treated as absolute value."""
        assert calculate_fan_speed(-2.0) == 2 * FAN_SPEED_PER_DEGREE

    def test_small_deviation(self):
        """Small deviation should give proportional speed."""
        assert calculate_fan_speed(0.5) == int(0.5 * FAN_SPEED_PER_DEGREE)

    def test_never_below_zero(self):
        """Fan speed should never go below 0."""
        assert calculate_fan_speed(0.0) >= 0
        assert calculate_fan_speed(-0.1) >= 0

    def test_never_above_100(self):
        """Fan speed should never exceed 100."""
        assert calculate_fan_speed(100.0) == 100
