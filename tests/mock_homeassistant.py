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
        "BUTTON": "button",
        "CLIMATE": "climate",
        "SENSOR": "sensor",
        "BINARY_SENSOR": "binary_sensor",
        "SELECT": "select",
    })()
    ha_const.UnitOfTemperature = type("UnitOfTemperature", (), {
        "FAHRENHEIT": "°F",
        "CELSIUS": "°C",
    })()
    ha_const.UnitOfTime = type("UnitOfTime", (), {
        "MINUTES": "min",
        "SECONDS": "s",
        "HOURS": "h",
    })()
    ha_const.PERCENTAGE = "%"
    ha_const.ATTR_TEMPERATURE = "temperature"

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
    # Use MagicMock() instances so attribute access (e.g. .LIST) auto-generates
    for name in [
        "SelectSelector", "SelectSelectorConfig", "SelectOptionDict",
        "SelectSelectorMode", "NumberSelector", "NumberSelectorConfig",
        "NumberSelectorMode", "EntitySelector", "EntitySelectorConfig",
        "TimeSelector", "AreaSelector", "AreaSelectorConfig",
    ]:
        setattr(ha_selector, name, MagicMock())

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
    class FakeCoordinatorEntityMeta(type):
        """Allow CoordinatorEntity[X] subscription on Python 3.9."""
        def __getitem__(cls, item):
            return cls

    class FakeCoordinatorEntity(metaclass=FakeCoordinatorEntityMeta):
        def __init__(self, coordinator):
            self.coordinator = coordinator

    ha_coordinator.CoordinatorEntity = FakeCoordinatorEntity

    # homeassistant.helpers.event
    ha_event = _create_module("homeassistant.helpers.event")
    ha_event.async_track_time_change = MagicMock(return_value=lambda: None)

    # homeassistant.helpers.area_registry
    ha_area_reg = _create_module("homeassistant.helpers.area_registry")

    class FakeAreaEntry:
        """Minimal AreaEntry stub."""
        def __init__(self, area_id, name):
            self.id = area_id
            self.name = name

    class FakeAreaRegistry:
        """Minimal AreaRegistry stub."""
        def __init__(self):
            self.areas = {}

        def async_list_areas(self):
            return list(self.areas.values())

        def async_get_area(self, area_id):
            return self.areas.get(area_id)

    ha_area_reg.AreaEntry = FakeAreaEntry
    ha_area_reg.FakeAreaEntry = FakeAreaEntry
    ha_area_reg.AreaRegistry = FakeAreaRegistry
    ha_area_reg.FakeAreaRegistry = FakeAreaRegistry
    ha_area_reg.async_get = MagicMock(return_value=FakeAreaRegistry())

    # homeassistant.helpers.entity_registry
    ha_entity_reg = _create_module("homeassistant.helpers.entity_registry")

    class FakeEntityEntry:
        """Minimal entity registry entry stub."""
        def __init__(
            self,
            entity_id,
            domain=None,
            device_class=None,
            original_device_class=None,
            area_id=None,
            device_id=None,
            disabled_by=None,
        ):
            self.entity_id = entity_id
            self.domain = domain or entity_id.split(".")[0]
            self.device_class = device_class
            self.original_device_class = original_device_class
            self.area_id = area_id
            self.device_id = device_id
            self.disabled_by = disabled_by

    class FakeEntityRegistry:
        """Minimal EntityRegistry stub."""
        def __init__(self):
            self.entities = {}

    ha_entity_reg.RegistryEntry = FakeEntityEntry
    ha_entity_reg.FakeEntityEntry = FakeEntityEntry
    ha_entity_reg.EntityRegistry = FakeEntityRegistry
    ha_entity_reg.FakeEntityRegistry = FakeEntityRegistry
    ha_entity_reg.async_get = MagicMock(return_value=FakeEntityRegistry())

    # homeassistant.helpers.device_registry
    ha_device_reg = _create_module("homeassistant.helpers.device_registry")

    class FakeDeviceEntry:
        """Minimal device registry entry stub."""
        def __init__(self, device_id, area_id=None):
            self.id = device_id
            self.area_id = area_id

    class FakeDeviceRegistry:
        """Minimal DeviceRegistry stub."""
        def __init__(self):
            self.devices = {}

        def async_get(self, device_id):
            return self.devices.get(device_id)

    ha_device_reg.DeviceEntry = FakeDeviceEntry
    ha_device_reg.FakeDeviceEntry = FakeDeviceEntry
    ha_device_reg.DeviceRegistry = FakeDeviceRegistry
    ha_device_reg.FakeDeviceRegistry = FakeDeviceRegistry
    ha_device_reg.async_get = MagicMock(return_value=FakeDeviceRegistry())

    # homeassistant.components
    _create_module("homeassistant.components")

    # homeassistant.components.http
    ha_http = _create_module("homeassistant.components.http")
    ha_http.StaticPathConfig = MagicMock

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

    # homeassistant.components.select
    ha_select = _create_module("homeassistant.components.select")
    ha_select.SelectEntity = type("SelectEntity", (), {})

    # homeassistant.components.button
    ha_button = _create_module("homeassistant.components.button")
    ha_button.ButtonEntity = type("ButtonEntity", (), {
        "async_press": lambda self: None,
    })

    # homeassistant.components.persistent_notification
    ha_pn = _create_module("homeassistant.components.persistent_notification")
    ha_pn.async_create = MagicMock()

    # homeassistant.helpers.entity_platform
    ha_entity_platform = _create_module("homeassistant.helpers.entity_platform")
    ha_entity_platform.AddEntitiesCallback = MagicMock

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
