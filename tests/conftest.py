"""Fixtures for Smart Climate tests."""
# Must import mock_homeassistant first to stub HA modules
import tests.mock_homeassistant  # noqa: F401, I001, E402

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.smart_climate.const import (
    AI_PROVIDER_NONE,
    CONF_AI_ANALYSIS_TIME,
    CONF_AI_API_KEY,
    CONF_AI_AUTO_APPLY,
    CONF_AI_BASE_URL,
    CONF_AI_MODEL,
    CONF_AI_PROVIDER,
    CONF_ENABLE_FOLLOW_ME,
    CONF_ENABLE_ZONE_BALANCING,
    CONF_INTEGRATION_NAME,
    CONF_OUTDOOR_TEMP_SENSOR,
    CONF_ROOMS,
    CONF_SCHEDULES,
    CONF_TEMP_UNIT,
    CONF_UPDATE_INTERVAL,
    CONF_WEATHER_ENTITY,
    SUGGESTION_PENDING,
)
from custom_components.smart_climate.models import (
    HouseState,
    HVACAction,
    RoomConfig,
    RoomState,
    Schedule,
    Suggestion,
    SuggestionPriority,
)


@pytest.fixture
def sample_room_config():
    """Create a sample room config."""
    return RoomConfig(
        name="Living Room",
        slug="living_room",
        climate_entity="climate.living_room",
        temp_sensors=["sensor.lr_temp"],
        humidity_sensors=["sensor.lr_humidity"],
        presence_sensors=["binary_sensor.lr_motion"],
        door_window_sensors=["binary_sensor.lr_window"],
        vent_entities=["cover.lr_vent"],
        auxiliary_entities=["switch.lr_heater"],
        priority=7,
        target_temp_offset=0.0,
    )


@pytest.fixture
def sample_room_config_2():
    """Create a second sample room config."""
    return RoomConfig(
        name="Nursery",
        slug="nursery",
        climate_entity="climate.nursery",
        temp_sensors=["sensor.nursery_temp"],
        humidity_sensors=[],
        presence_sensors=["binary_sensor.nursery_motion"],
        door_window_sensors=[],
        vent_entities=[],
        auxiliary_entities=["switch.nursery_heater"],
        priority=9,
        target_temp_offset=0.0,
    )


@pytest.fixture
def sample_room_state(sample_room_config):
    """Create a sample room state."""
    return RoomState(
        config=sample_room_config,
        temperature=72.1,
        humidity=45.0,
        occupied=True,
        window_open=False,
        comfort_score=84.0,
        efficiency_score=68.0,
        hvac_action=HVACAction.COOLING,
        hvac_runtime_today=162.0,
        hvac_cycles_today=8,
        current_target=72.0,
        smart_target=72.0,
        follow_me_active=True,
        active_schedule=None,
        auxiliary_active=False,
        temp_trend=0.3,
        last_presence_time=datetime.now(),
    )


@pytest.fixture
def sample_room_state_2(sample_room_config_2):
    """Create a second room state (unoccupied nursery)."""
    return RoomState(
        config=sample_room_config_2,
        temperature=70.5,
        humidity=50.0,
        occupied=False,
        window_open=False,
        comfort_score=75.0,
        efficiency_score=80.0,
        hvac_action=HVACAction.IDLE,
        hvac_runtime_today=30.0,
        hvac_cycles_today=2,
        current_target=70.0,
        smart_target=66.0,
        follow_me_active=False,
        active_schedule="Baby Nap",
        auxiliary_active=False,
        temp_trend=-0.1,
        last_presence_time=datetime.now() - timedelta(hours=1),
    )


@pytest.fixture
def sample_house_state():
    """Create a sample house state."""
    return HouseState(
        comfort_score=79.5,
        efficiency_score=74.0,
        total_hvac_runtime=192.0,
        heating_degree_days=0.0,
        cooling_degree_days=7.5,
        follow_me_target="living_room",
        active_schedule=None,
        outdoor_temperature=82.0,
        outdoor_humidity=60.0,
    )


@pytest.fixture
def sample_schedule():
    """Create a sample schedule."""
    return Schedule(
        name="Baby Nap",
        slug="baby_nap",
        rooms=["nursery"],
        days=[0, 1, 2, 3, 4],  # Mon-Fri
        start_time="13:00",
        end_time="15:00",
        target_temperature=70.0,
        hvac_mode=None,
        use_auxiliary=True,
        priority=8,
        enabled=True,
    )


@pytest.fixture
def sample_schedule_night():
    """Create a night mode schedule."""
    return Schedule(
        name="Night Mode",
        slug="night_mode",
        rooms=["__all__"],
        days=[0, 1, 2, 3, 4, 5, 6],
        start_time="22:00",
        end_time="06:00",
        target_temperature=66.0,
        hvac_mode=None,
        use_auxiliary=False,
        priority=5,
        enabled=True,
    )


@pytest.fixture
def sample_suggestion():
    """Create a sample suggestion."""
    return Suggestion(
        id="test-uuid-1234",
        title="Lower nursery temperature",
        description="Lower nursery to 69F during naps",
        reasoning="Based on 2-week pattern analysis",
        room="nursery",
        action_type="set_temperature",
        action_data={"temperature": 69.0},
        confidence=0.85,
        priority=SuggestionPriority.HIGH,
        status=SUGGESTION_PENDING,
        created_at=datetime.now(),
        expires_at=datetime.now() + timedelta(hours=24),
    )


@pytest.fixture
def sample_config_data():
    """Create sample config entry data."""
    return {
        CONF_INTEGRATION_NAME: "Smart Climate",
        CONF_TEMP_UNIT: "F",
        CONF_UPDATE_INTERVAL: 60,
        CONF_ENABLE_FOLLOW_ME: True,
        CONF_ENABLE_ZONE_BALANCING: True,
        CONF_WEATHER_ENTITY: "weather.home",
        CONF_OUTDOOR_TEMP_SENSOR: None,
        CONF_AI_PROVIDER: AI_PROVIDER_NONE,
        CONF_AI_API_KEY: "",
        CONF_AI_MODEL: "",
        CONF_AI_BASE_URL: "",
        CONF_AI_ANALYSIS_TIME: "06:00",
        CONF_AI_AUTO_APPLY: False,
        CONF_ROOMS: [
            {
                "room_name": "Living Room",
                "room_slug": "living_room",
                "climate_entity": "climate.living_room",
                "temp_sensors": ["sensor.lr_temp"],
                "humidity_sensors": ["sensor.lr_humidity"],
                "presence_sensors": ["binary_sensor.lr_motion"],
                "door_window_sensors": ["binary_sensor.lr_window"],
                "vent_entities": [],
                "auxiliary_entities": [],
                "room_priority": 7,
                "target_temp_offset": 0.0,
            }
        ],
        CONF_SCHEDULES: [],
    }


@pytest.fixture
def mock_hass():
    """Create a mock Home Assistant instance."""
    hass = MagicMock()
    hass.states = MagicMock()
    hass.services = MagicMock()
    hass.services.async_call = AsyncMock()
    hass.bus = MagicMock()
    hass.bus.async_fire = MagicMock()
    hass.data = {}
    return hass
