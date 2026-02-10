"""Constants for the Smart Climate integration."""

from __future__ import annotations

DOMAIN = "smart_climate"
PLATFORMS = ["climate", "sensor", "binary_sensor"]

# Config keys - General
CONF_INTEGRATION_NAME = "integration_name"
CONF_TEMP_UNIT = "temp_unit"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_ENABLE_FOLLOW_ME = "enable_follow_me"
CONF_ENABLE_ZONE_BALANCING = "enable_zone_balancing"

# Config keys - Weather
CONF_WEATHER_ENTITY = "weather_entity"
CONF_OUTDOOR_TEMP_SENSOR = "outdoor_temp_sensor"

# Config keys - Rooms
CONF_ROOMS = "rooms"
CONF_ROOM_NAME = "room_name"
CONF_ROOM_SLUG = "room_slug"
CONF_CLIMATE_ENTITY = "climate_entity"
CONF_TEMP_SENSORS = "temp_sensors"
CONF_HUMIDITY_SENSORS = "humidity_sensors"
CONF_PRESENCE_SENSORS = "presence_sensors"
CONF_DOOR_WINDOW_SENSORS = "door_window_sensors"
CONF_VENT_ENTITIES = "vent_entities"
CONF_AUXILIARY_ENTITIES = "auxiliary_entities"
CONF_ROOM_PRIORITY = "room_priority"
CONF_TARGET_TEMP_OFFSET = "target_temp_offset"

# Config keys - Schedules
CONF_SCHEDULES = "schedules"
CONF_SCHEDULE_NAME = "schedule_name"
CONF_SCHEDULE_SLUG = "schedule_slug"
CONF_SCHEDULE_ROOMS = "schedule_rooms"
CONF_SCHEDULE_DAYS = "schedule_days"
CONF_SCHEDULE_START_TIME = "schedule_start_time"
CONF_SCHEDULE_END_TIME = "schedule_end_time"
CONF_SCHEDULE_TARGET_TEMP = "schedule_target_temp"
CONF_SCHEDULE_HVAC_MODE = "schedule_hvac_mode"
CONF_SCHEDULE_USE_AUXILIARY = "schedule_use_auxiliary"
CONF_SCHEDULE_PRIORITY = "schedule_priority"
CONF_SCHEDULE_ENABLED = "schedule_enabled"
CONF_SCHEDULE_ALL_ROOMS = "__all__"

# Config keys - AI
CONF_AI_PROVIDER = "ai_provider"
CONF_AI_API_KEY = "ai_api_key"
CONF_AI_MODEL = "ai_model"
CONF_AI_BASE_URL = "ai_base_url"
CONF_AI_ANALYSIS_TIME = "ai_analysis_time"
CONF_AI_AUTO_APPLY = "ai_auto_apply"

# Config keys - Advanced/Options
CONF_COMFORT_TEMP_WEIGHT = "comfort_temp_weight"
CONF_COMFORT_HUMIDITY_WEIGHT = "comfort_humidity_weight"
CONF_EFFICIENCY_THRESHOLD = "efficiency_threshold"
CONF_FOLLOW_ME_COOLDOWN = "follow_me_cooldown"
CONF_AWAY_TEMP_OFFSET = "away_temp_offset"
CONF_WINDOW_OPEN_BEHAVIOR = "window_open_behavior"
CONF_AUXILIARY_THRESHOLD = "auxiliary_threshold"
CONF_AUXILIARY_DELAY_MINUTES = "auxiliary_delay_minutes"
CONF_AUXILIARY_MAX_RUNTIME = "auxiliary_max_runtime"

# Defaults
DEFAULT_NAME = "Smart Climate"
DEFAULT_TEMP_UNIT = "F"
DEFAULT_UPDATE_INTERVAL = 60
DEFAULT_ENABLE_FOLLOW_ME = True
DEFAULT_ENABLE_ZONE_BALANCING = True
DEFAULT_ROOM_PRIORITY = 5
DEFAULT_TARGET_TEMP_OFFSET = 0.0
DEFAULT_AI_ANALYSIS_TIME = "06:00"
DEFAULT_AI_AUTO_APPLY = False
DEFAULT_COMFORT_TEMP_WEIGHT = 0.7
DEFAULT_COMFORT_HUMIDITY_WEIGHT = 0.3
DEFAULT_EFFICIENCY_THRESHOLD = 70
DEFAULT_FOLLOW_ME_COOLDOWN = 10
DEFAULT_AWAY_TEMP_OFFSET = 4.0
DEFAULT_WINDOW_OPEN_BEHAVIOR = "eco"
DEFAULT_AUXILIARY_THRESHOLD = 2.0
DEFAULT_AUXILIARY_DELAY_MINUTES = 15
DEFAULT_AUXILIARY_MAX_RUNTIME = 120

# AI Provider types
AI_PROVIDER_NONE = "none"
AI_PROVIDER_OPENAI = "openai"
AI_PROVIDER_ANTHROPIC = "anthropic"
AI_PROVIDER_OLLAMA = "ollama"
AI_PROVIDER_GEMINI = "gemini"
AI_PROVIDER_GROK = "grok"

AI_PROVIDERS = [
    AI_PROVIDER_NONE,
    AI_PROVIDER_OPENAI,
    AI_PROVIDER_ANTHROPIC,
    AI_PROVIDER_OLLAMA,
    AI_PROVIDER_GEMINI,
    AI_PROVIDER_GROK,
]

# Comfort score thresholds
COMFORT_EXCELLENT = 90
COMFORT_GOOD = 70
COMFORT_FAIR = 50
COMFORT_POOR = 30

# Events
EVENT_ANALYSIS_COMPLETE = f"{DOMAIN}_analysis_complete"
EVENT_NEW_SUGGESTIONS = f"{DOMAIN}_new_suggestions"
EVENT_SUGGESTION_APPLIED = f"{DOMAIN}_suggestion_applied"
EVENT_SUGGESTION_REJECTED = f"{DOMAIN}_suggestion_rejected"
EVENT_COMFORT_ALERT = f"{DOMAIN}_comfort_alert"
EVENT_EFFICIENCY_ALERT = f"{DOMAIN}_efficiency_alert"
EVENT_FOLLOW_ME_CHANGED = f"{DOMAIN}_follow_me_changed"
EVENT_WINDOW_OPEN_ADJUSTED = f"{DOMAIN}_window_open_adjusted"
EVENT_SCHEDULE_ACTIVATED = f"{DOMAIN}_schedule_activated"
EVENT_SCHEDULE_DEACTIVATED = f"{DOMAIN}_schedule_deactivated"
EVENT_AUXILIARY_ACTIVATED = f"{DOMAIN}_auxiliary_activated"
EVENT_AUXILIARY_DEACTIVATED = f"{DOMAIN}_auxiliary_deactivated"

# Services
SERVICE_TRIGGER_ANALYSIS = "trigger_analysis"
SERVICE_APPROVE_SUGGESTION = "approve_suggestion"
SERVICE_REJECT_SUGGESTION = "reject_suggestion"
SERVICE_APPROVE_ALL = "approve_all_suggestions"
SERVICE_REJECT_ALL = "reject_all_suggestions"
SERVICE_ADD_ROOM = "add_room"
SERVICE_REMOVE_ROOM = "remove_room"
SERVICE_SET_ROOM_PRIORITY = "set_room_priority"
SERVICE_FORCE_FOLLOW_ME = "force_follow_me"
SERVICE_RESET_STATISTICS = "reset_statistics"
SERVICE_ADD_SCHEDULE = "add_schedule"
SERVICE_REMOVE_SCHEDULE = "remove_schedule"
SERVICE_ACTIVATE_SCHEDULE = "activate_schedule"
SERVICE_DEACTIVATE_SCHEDULE = "deactivate_schedule"
SERVICE_SET_AUXILIARY_MODE = "set_auxiliary_mode"

# Entity prefixes
ENTITY_PREFIX = "sc"

# Window open behaviors
WINDOW_BEHAVIOR_ECO = "eco"
WINDOW_BEHAVIOR_OFF = "off"
WINDOW_BEHAVIOR_REDUCE = "reduce"

# Suggestion statuses
SUGGESTION_PENDING = "pending"
SUGGESTION_APPROVED = "approved"
SUGGESTION_REJECTED = "rejected"
SUGGESTION_APPLIED = "applied"
SUGGESTION_EXPIRED = "expired"

# Suggestion expiry
SUGGESTION_EXPIRY_HOURS = 24

# Auto-apply confidence threshold
AUTO_APPLY_CONFIDENCE_THRESHOLD = 0.8
