"""Mock homeassistant module for testing without HA installed.

This module creates minimal stubs for all homeassistant imports used
by the smart_climate integration, allowing unit tests to run without
a full homeassistant installation.
"""

import sys
from types import ModuleType
from unittest.mock import MagicMock


def _create_module(name: str) -> ModuleType:
    """Create a mock module and register in sys.modules."""
    mod = ModuleType(name)
    sys.modules[name] = mod
    return mod


def setup_mock_homeassistant():
    """Install mock homeassistant modules into sys.modules."""
    # Skip if real homeassistant is available
    if "homeassistant" in sys.modules and not isinstance(
        sys.modules["homeassistant"], ModuleType
    ):
        return

    # Root module
    _create_module("homeassistant")

    # homeassistant.const
    ha_const = _create_module("homeassistant.const")
    ha_const.Platform = type("Platform", (), {
        "CLIMATE": "climate",
        "SENSOR": "sensor",
        "BINARY_SENSOR": "binary_sensor",
    })()
    ha_const.UnitOfTemperature = type("UnitOfTemperature", (), {
        "FAHRENHEIT": "°F",
        "CELSIUS": "°C",
    })()

    # homeassistant.core
    ha_core = _create_module("homeassistant.core")
    ha_core.HomeAssistant = MagicMock
    ha_core.ServiceCall = MagicMock
    ha_core.callback = lambda f: f
    ha_core.CALLBACK_TYPE = MagicMock

    # homeassistant.config_entries
    ha_config_entries = _create_module("homeassistant.config_entries")
    ha_config_entries.ConfigEntry = MagicMock

    class ConfigFlowMeta(type):
        """Allow ConfigFlow(domain=...) keyword in class definition."""
        def __new__(mcs, name, bases, namespace, domain=None, **kwargs):
            cls = super().__new__(mcs, name, bases, namespace)
            if domain is not None:
                cls.DOMAIN = domain
            return cls

    class FakeConfigFlow(metaclass=ConfigFlowMeta):
        VERSION = 1
        def async_show_form(self, **kw):
            return kw
        def async_create_entry(self, **kw):
            return kw

    ha_config_entries.ConfigFlow = FakeConfigFlow

    class FakeOptionsFlow:
        def async_show_form(self, **kw):
            return kw
        def async_create_entry(self, **kw):
            return kw

    ha_config_entries.OptionsFlow = FakeOptionsFlow

    # homeassistant.data_entry_flow
    ha_flow = _create_module("homeassistant.data_entry_flow")
    ha_flow.FlowResult = dict

    # homeassistant.helpers
    _create_module("homeassistant.helpers")

    # homeassistant.helpers.selector
    ha_selector = _create_module("homeassistant.helpers.selector")
    # Mock all selector classes used in config_flow
    for name in [
        "SelectSelector", "SelectSelectorConfig", "SelectOptionDict",
        "SelectSelectorMode", "NumberSelector", "NumberSelectorConfig",
        "NumberSelectorMode", "EntitySelector", "EntitySelectorConfig",
        "TimeSelector",
    ]:
        setattr(ha_selector, name, MagicMock)

    # homeassistant.helpers.config_validation
    ha_cv = _create_module("homeassistant.helpers.config_validation")
    ha_cv.string = str
    ha_cv.boolean = bool
    ha_cv.positive_int = int
    ha_cv.positive_float = float

    # homeassistant.helpers.entity
    ha_entity = _create_module("homeassistant.helpers.entity")
    ha_entity.Entity = type("Entity", (), {})

    # homeassistant.helpers.update_coordinator
    ha_coordinator = _create_module("homeassistant.helpers.update_coordinator")

    class FakeCoordinatorMeta(type):
        """Allow DataUpdateCoordinator[X] subscription."""
        def __getitem__(cls, item):
            return cls

    class FakeCoordinator(metaclass=FakeCoordinatorMeta):
        def __init__(self, hass=None, *args, **kwargs):
            self.hass = hass
            self.data = {}
            self.config_entry = MagicMock()
            self.last_update_success_time = None
            self.logger = MagicMock()

        async def async_config_entry_first_refresh(self):
            pass

        def async_set_updated_data(self, data):
            self.data = data

    ha_coordinator.DataUpdateCoordinator = FakeCoordinator
    ha_coordinator.CoordinatorEntity = type("CoordinatorEntity", (), {
        "__init__": lambda self, coordinator: setattr(self, "coordinator", coordinator),
    })

    # homeassistant.helpers.event
    ha_event = _create_module("homeassistant.helpers.event")
    ha_event.async_track_time_change = MagicMock(return_value=lambda: None)

    # homeassistant.components
    _create_module("homeassistant.components")

    # homeassistant.components.sensor
    ha_sensor = _create_module("homeassistant.components.sensor")
    ha_sensor.SensorEntity = type("SensorEntity", (), {})
    ha_sensor.SensorDeviceClass = type("SensorDeviceClass", (), {
        "TEMPERATURE": "temperature",
        "HUMIDITY": "humidity",
        "TIMESTAMP": "timestamp",
    })()
    ha_sensor.SensorStateClass = type("SensorStateClass", (), {
        "MEASUREMENT": "measurement",
        "TOTAL_INCREASING": "total_increasing",
    })()

    # homeassistant.components.binary_sensor
    ha_bsensor = _create_module("homeassistant.components.binary_sensor")
    ha_bsensor.BinarySensorEntity = type("BinarySensorEntity", (), {})
    ha_bsensor.BinarySensorDeviceClass = type("BinarySensorDeviceClass", (), {
        "OCCUPANCY": "occupancy",
        "WINDOW": "window",
    })()

    # homeassistant.components.climate
    ha_climate = _create_module("homeassistant.components.climate")
    ha_climate.ClimateEntity = type("ClimateEntity", (), {})
    ha_climate.ClimateEntityFeature = type("ClimateEntityFeature", (), {
        "TARGET_TEMPERATURE": 1,
        "FAN_MODE": 8,
        "PRESET_MODE": 16,
        "SWING_MODE": 32,
    })()
    ha_climate.HVACMode = type("HVACMode", (), {
        "OFF": "off",
        "HEAT": "heat",
        "COOL": "cool",
        "AUTO": "auto",
        "HEAT_COOL": "heat_cool",
        "DRY": "dry",
        "FAN_ONLY": "fan_only",
    })()
    ha_climate.HVACAction = type("HVACAction", (), {
        "HEATING": "heating",
        "COOLING": "cooling",
        "IDLE": "idle",
        "OFF": "off",
        "DRYING": "drying",
        "FAN": "fan",
    })()

    # homeassistant.components.recorder
    _create_module("homeassistant.components.recorder")
    _create_module("homeassistant.components.recorder.history")

    # voluptuous (not part of HA but needed)
    try:
        import voluptuous  # noqa: F401
    except ImportError:
        vol = _create_module("voluptuous")
        vol.Schema = MagicMock
        vol.Required = lambda *a, **kw: MagicMock()
        vol.Optional = lambda *a, **kw: MagicMock()
        vol.All = MagicMock
        vol.Coerce = MagicMock
        vol.In = MagicMock
        vol.ALLOW_EXTRA = MagicMock


# Auto-setup when imported
setup_mock_homeassistant()
