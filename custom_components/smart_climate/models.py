"""Data models for the Smart Climate integration."""

from __future__ import annotations

import re
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from enum import Enum

    class StrEnum(str, Enum):
        """Backport of StrEnum for Python < 3.11."""

from .const import (
    DEFAULT_AUXILIARY_DELAY_MINUTES,
    DEFAULT_AUXILIARY_MAX_RUNTIME,
    DEFAULT_AUXILIARY_THRESHOLD,
    DEFAULT_ROOM_PRIORITY,
    DEFAULT_TARGET_TEMP_OFFSET,
    SUGGESTION_PENDING,
)


def slugify(name: str) -> str:
    """Convert a name to a slug."""
    slug = name.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s-]+", "_", slug)
    return slug


class HVACAction(StrEnum):
    """HVAC action states."""

    HEATING = "heating"
    COOLING = "cooling"
    IDLE = "idle"
    OFF = "off"
    DRYING = "drying"
    FAN = "fan"


class SuggestionPriority(StrEnum):
    """Suggestion priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuxiliaryDeviceType(StrEnum):
    """Types of auxiliary devices by HA domain."""

    CLIMATE = "climate"
    SWITCH = "switch"
    FAN = "fan"
    NUMBER = "number"


@dataclass
class RoomConfig:
    """Configuration for a room."""

    name: str
    slug: str
    climate_entity: str
    temp_sensors: list[str] = field(default_factory=list)
    humidity_sensors: list[str] = field(default_factory=list)
    presence_sensors: list[str] = field(default_factory=list)
    door_window_sensors: list[str] = field(default_factory=list)
    vent_entities: list[str] = field(default_factory=list)
    auxiliary_entities: list[str] = field(default_factory=list)
    priority: int = DEFAULT_ROOM_PRIORITY
    target_temp_offset: float = DEFAULT_TARGET_TEMP_OFFSET

    @classmethod
    def from_dict(cls, data: dict) -> RoomConfig:
        """Create from config dict."""
        return cls(
            name=data["room_name"],
            slug=data.get("room_slug", slugify(data["room_name"])),
            climate_entity=data["climate_entity"],
            temp_sensors=data.get("temp_sensors", []),
            humidity_sensors=data.get("humidity_sensors", []),
            presence_sensors=data.get("presence_sensors", []),
            door_window_sensors=data.get("door_window_sensors", []),
            vent_entities=data.get("vent_entities", []),
            auxiliary_entities=data.get("auxiliary_entities", []),
            priority=data.get("room_priority", DEFAULT_ROOM_PRIORITY),
            target_temp_offset=data.get(
                "target_temp_offset", DEFAULT_TARGET_TEMP_OFFSET
            ),
        )

    def to_dict(self) -> dict:
        """Serialize to config dict."""
        return {
            "room_name": self.name,
            "room_slug": self.slug,
            "climate_entity": self.climate_entity,
            "temp_sensors": self.temp_sensors,
            "humidity_sensors": self.humidity_sensors,
            "presence_sensors": self.presence_sensors,
            "door_window_sensors": self.door_window_sensors,
            "vent_entities": self.vent_entities,
            "auxiliary_entities": self.auxiliary_entities,
            "room_priority": self.priority,
            "target_temp_offset": self.target_temp_offset,
        }


@dataclass
class Schedule:
    """A named, recurring temperature schedule."""

    name: str
    slug: str
    rooms: list[str]  # room slugs, or ["__all__"]
    days: list[int]  # 0=Mon through 6=Sun
    start_time: str  # "HH:MM"
    end_time: str  # "HH:MM"
    target_temperature: float
    hvac_mode: str | None = None
    use_auxiliary: bool = False
    priority: int = 5
    enabled: bool = True

    @classmethod
    def from_dict(cls, data: dict) -> Schedule:
        """Create from config dict."""
        return cls(
            name=data["schedule_name"],
            slug=data.get("schedule_slug", slugify(data["schedule_name"])),
            rooms=data.get("schedule_rooms", ["__all__"]),
            days=data.get("schedule_days", list(range(7))),
            start_time=data["schedule_start_time"],
            end_time=data["schedule_end_time"],
            target_temperature=data["schedule_target_temp"],
            hvac_mode=data.get("schedule_hvac_mode"),
            use_auxiliary=data.get("schedule_use_auxiliary", False),
            priority=data.get("schedule_priority", 5),
            enabled=data.get("schedule_enabled", True),
        )

    def to_dict(self) -> dict:
        """Serialize to config dict."""
        return {
            "schedule_name": self.name,
            "schedule_slug": self.slug,
            "schedule_rooms": self.rooms,
            "schedule_days": self.days,
            "schedule_start_time": self.start_time,
            "schedule_end_time": self.end_time,
            "schedule_target_temp": self.target_temperature,
            "schedule_hvac_mode": self.hvac_mode,
            "schedule_use_auxiliary": self.use_auxiliary,
            "schedule_priority": self.priority,
            "schedule_enabled": self.enabled,
        }


@dataclass
class RoomState:
    """Live state for a room, updated by the coordinator."""

    config: RoomConfig
    temperature: float | None = None
    humidity: float | None = None
    occupied: bool = False
    window_open: bool = False
    comfort_score: float = 0.0
    efficiency_score: float = 0.0
    hvac_action: HVACAction = HVACAction.IDLE
    hvac_runtime_today: float = 0.0  # minutes
    hvac_cycles_today: int = 0
    current_target: float | None = None
    smart_target: float | None = None
    user_override_active: bool = False
    follow_me_active: bool = False
    last_adjustment_reason: str = ""
    active_schedule: str | None = None
    auxiliary_active: bool = False
    auxiliary_devices_on: list[str] = field(default_factory=list)
    auxiliary_reason: str = ""
    auxiliary_runtime_minutes: float = 0.0
    temp_trend: float = 0.0  # degrees per hour
    last_presence_time: datetime | None = None
    last_hvac_state: str | None = None
    hvac_state_change_time: datetime | None = None
    temp_history: list[tuple[datetime, float]] = field(default_factory=list)


@dataclass
class Suggestion:
    """An AI-generated suggestion."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    reasoning: str = ""
    room: str | None = None  # room slug, or None for house-wide
    action_type: str = ""  # set_temperature, set_mode, vent_adjustment, schedule_change, etc.
    action_data: dict = field(default_factory=dict)
    confidence: float = 0.0
    priority: SuggestionPriority = SuggestionPriority.MEDIUM
    status: str = SUGGESTION_PENDING
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime = field(
        default_factory=lambda: datetime.now() + timedelta(hours=24)
    )
    applied_at: datetime | None = None
    rejected_reason: str | None = None

    def is_expired(self) -> bool:
        """Check if the suggestion has expired."""
        return datetime.now() > self.expires_at

    def to_dict(self) -> dict:
        """Serialize for API/events."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "reasoning": self.reasoning,
            "room": self.room,
            "action_type": self.action_type,
            "action_data": self.action_data,
            "confidence": self.confidence,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
            "rejected_reason": self.rejected_reason,
        }


@dataclass
class HouseState:
    """Whole-house aggregated state."""

    comfort_score: float = 0.0
    efficiency_score: float = 0.0
    total_hvac_runtime: float = 0.0
    heating_degree_days: float = 0.0
    cooling_degree_days: float = 0.0
    follow_me_target: str | None = None
    active_schedule: str | None = None
    outdoor_temperature: float | None = None
    outdoor_humidity: float | None = None
    last_analysis_time: datetime | None = None
    ai_daily_summary: str = ""
    suggestions: list[Suggestion] = field(default_factory=list)


@dataclass
class AuxiliaryDeviceState:
    """Tracking state for an auxiliary device."""

    entity_id: str
    device_type: AuxiliaryDeviceType
    is_on: bool = False
    started_at: datetime | None = None
    runtime_minutes: float = 0.0
    max_runtime: int = DEFAULT_AUXILIARY_MAX_RUNTIME
    threshold: float = DEFAULT_AUXILIARY_THRESHOLD
    delay_minutes: int = DEFAULT_AUXILIARY_DELAY_MINUTES
