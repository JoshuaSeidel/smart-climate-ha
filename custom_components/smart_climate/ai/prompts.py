"""Prompt templates for the Smart Climate AI analysis pipeline."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

_LOGGER = logging.getLogger(__name__)

# Maximum approximate token budget for the user prompt payload.
# We use a rough 4-characters-per-token heuristic to stay under ~4000 tokens.
MAX_USER_PROMPT_CHARS = 15000


def build_system_prompt() -> str:
    """Return the system prompt that defines the AI's role and output schema.

    The system prompt instructs the model to act as a home climate advisor,
    constrains it to only suggest safe HVAC actions, and defines the required
    JSON output format.
    """
    return """\
You are an expert home climate advisor integrated into a Home Assistant smart \
climate system. Your job is to analyze the current state of the home's HVAC \
system, room conditions, schedules, and weather, then provide actionable \
suggestions to improve comfort and energy efficiency.

## Important: HVAC Architecture

- Rooms are monitoring zones with their own temperature/humidity sensors.
- Multiple rooms often share the SAME climate entity (one HVAC system).
- The "HVAC target" shown per room comes from the shared climate entity — \
it is NOT a per-room thermostat. All rooms sharing a climate entity have the \
same target.
- The "Room sensor temperature" is the actual reading from that room's \
dedicated sensor (e.g. a remote sensor or thermostat used as a sensor).
- When you suggest `set_temperature`, it changes the climate entity's \
setpoint, which affects ALL rooms on that HVAC system.
- The "HVAC Systems" section shows which rooms share a climate entity. \
Do NOT suggest conflicting temperatures for rooms on the same HVAC system.
- Use `null` for the room field when a suggestion applies to the whole \
HVAC system rather than a specific zone.

## Constraints

- You may ONLY suggest the following safe action types:
  - **set_temperature**: Adjust an HVAC system's target temperature. This \
changes the climate entity setpoint for all rooms on that system.
  - **set_mode**: Change the HVAC mode (heat, cool, auto, off, fan_only).
  - **vent_adjustment**: Recommend opening or closing vents in specific rooms.
  - **schedule_change**: Suggest modifications to existing schedules.
  - **general**: Provide general advice that does not map to a specific action.

- NEVER suggest actions that could be unsafe or outside the HVAC domain.
- Keep temperatures within a reasonable range (55-85°F / 13-29°C).
- Consider energy efficiency alongside comfort.
- Factor in outdoor weather conditions and trends.
- Account for occupancy patterns when making suggestions.
- Prioritize rooms that are occupied or will be occupied soon.
- When rooms share an HVAC, suggest ONE temperature that best serves all \
zones — do not emit separate set_temperature suggestions per room.

## Data Limitations

- HVAC runtime and cycle counters are in-memory and reset to 0 when \
Home Assistant restarts. If runtime/cycles are missing or 0, do NOT \
conclude the HVAC is broken — the system may have recently restarted.
- Comfort and efficiency scores of 0 mean "not yet calculated", not \
"terrible". These are omitted when not yet available.
- Some room fields may be omitted if data is not yet available. This is \
normal and does NOT indicate a sensor problem.
- NEVER suggest investigating sensor availability or missing readings. \
The system already monitors sensor health separately.
- Focus your analysis EXCLUSIVELY on the data that IS present. Do NOT \
comment on or draw conclusions from missing fields.

## Output Format

You MUST respond with valid JSON matching this exact schema:

{
    "summary": "A concise daily summary of overall climate status and key recommendations (1-3 sentences).",
    "suggestions": [
        {
            "title": "Short actionable title",
            "description": "Detailed description of what to do and why",
            "reasoning": "Explanation of the data-driven reasoning behind this suggestion",
            "room": "room_slug or null for house-wide / shared HVAC suggestions",
            "action_type": "set_temperature|set_mode|vent_adjustment|schedule_change|general",
            "action_data": {
                "temperature": 72,
                "mode": "heat",
                "vent_position": 75
            },
            "confidence": 0.85,
            "priority": "low|medium|high|critical"
        }
    ]
}

- **confidence** must be a float between 0.0 and 1.0.
- **priority** must be one of: low, medium, high, critical.
- **action_data** fields depend on the action_type:
  - set_temperature: {"temperature": <number>}
  - set_mode: {"mode": "<hvac_mode>"}
  - vent_adjustment: {"vent_position": <0-100>}
  - schedule_change: {"description": "<what to change>"}
  - general: {"advice": "<text>"}
- Return an empty suggestions array if no improvements are needed.
- Return at most 10 suggestions, ordered by priority (highest first).\
"""


def build_user_prompt(coordinator_data: dict[str, Any]) -> str:
    """Build the user prompt from current coordinator data.

    Serializes room states, house state, schedules, and weather into a
    structured text payload for the LLM. If the payload would exceed the
    approximate token budget, room details are summarized.

    Args:
        coordinator_data: The dict returned by the coordinator's
            ``_async_update_data`` method, containing ``rooms`` and ``house``
            keys.

    Returns:
        A formatted string prompt ready to send to the AI provider.
    """
    if not coordinator_data:
        return _minimal_prompt()

    rooms_data = coordinator_data.get("rooms", {})
    house_state = coordinator_data.get("house")

    now = datetime.now()

    sections: list[str] = []

    # -- Header
    sections.append(
        f"## Current Date & Time\n{now.strftime('%Y-%m-%d %H:%M:%S')} "
        f"({now.strftime('%A')})"
    )

    # -- House-level overview
    if house_state is not None:
        sections.append(_build_house_section(house_state))

    # -- HVAC systems (group rooms by shared climate entity)
    hvac_section = _build_hvac_systems_section(rooms_data)
    if hvac_section:
        sections.append(hvac_section)

    # -- Room details
    room_section = _build_rooms_section(rooms_data)
    sections.append(room_section)

    prompt = "\n\n".join(sections)

    # Truncate if too long to respect token budget
    if len(prompt) > MAX_USER_PROMPT_CHARS:
        _LOGGER.debug(
            "User prompt too long (%d chars); summarizing rooms", len(prompt)
        )
        room_section = _build_rooms_section(rooms_data, summarize=True)
        sections[-1] = room_section
        prompt = "\n\n".join(sections)

    sections.append(
        "## Instructions\n"
        "Analyze the data above and provide your suggestions as JSON."
    )

    return "\n\n".join(sections)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _minimal_prompt() -> str:
    """Return a minimal prompt when no coordinator data is available."""
    return (
        "No climate data is currently available. "
        "Please respond with an empty suggestions array and a summary "
        "indicating that data collection is still in progress."
    )


def _build_house_section(house_state: Any) -> str:
    """Serialize HouseState into a readable prompt section."""
    lines = ["## House Overview"]

    comfort = getattr(house_state, "comfort_score", None)
    if comfort is not None and comfort > 0:
        lines.append(f"- Overall comfort score: {comfort}/100")

    efficiency = getattr(house_state, "efficiency_score", None)
    if efficiency is not None and efficiency > 0:
        lines.append(f"- Overall efficiency score: {efficiency}/100")

    runtime = getattr(house_state, "total_hvac_runtime", None)
    if runtime is not None and runtime > 0:
        lines.append(f"- Total HVAC runtime today: {runtime:.0f} minutes")

    outdoor_temp = getattr(house_state, "outdoor_temperature", None)
    if outdoor_temp is not None:
        lines.append(f"- Outdoor temperature: {outdoor_temp}")

    outdoor_humidity = getattr(house_state, "outdoor_humidity", None)
    if outdoor_humidity is not None:
        lines.append(f"- Outdoor humidity: {outdoor_humidity}%")

    hdd = getattr(house_state, "heating_degree_days", None)
    if hdd is not None and hdd > 0:
        lines.append(f"- Heating degree days: {hdd:.1f}")

    cdd = getattr(house_state, "cooling_degree_days", None)
    if cdd is not None and cdd > 0:
        lines.append(f"- Cooling degree days: {cdd:.1f}")

    follow_me = getattr(house_state, "follow_me_target", None)
    if follow_me:
        lines.append(f"- Follow-me target room: {follow_me}")

    active_schedule = getattr(house_state, "active_schedule", None)
    if active_schedule:
        lines.append(f"- Active schedule: {active_schedule}")

    return "\n".join(lines)


def _build_rooms_section(
    rooms_data: dict[str, Any], summarize: bool = False
) -> str:
    """Serialize all room states into a prompt section.

    Args:
        rooms_data: Mapping of room slug to RoomState instances.
        summarize: If True, only include key metrics per room to reduce
            prompt length.
    """
    if not rooms_data:
        return "## Rooms\nNo room data available."

    lines = ["## Rooms"]

    for slug, room in rooms_data.items():
        name = getattr(getattr(room, "config", None), "name", slug)

        if summarize:
            lines.append(_summarize_room(slug, name, room))
        else:
            lines.append(_detail_room(slug, name, room))

    return "\n".join(lines)


def _detail_room(slug: str, name: str, room: Any) -> str:
    """Build a detailed block for a single room."""
    config = getattr(room, "config", None)
    climate_entity = getattr(config, "climate_entity", None) if config else None

    parts = [f"\n### {name} ({slug})"]

    if climate_entity:
        parts.append(f"  - Climate entity: {climate_entity}")

    temp = getattr(room, "temperature", None)
    if temp is not None:
        parts.append(f"  - Room sensor temperature: {temp}")

    humidity = getattr(room, "humidity", None)
    if humidity is not None:
        parts.append(f"  - Humidity: {humidity}%")

    target = getattr(room, "current_target", None)
    entity_label = climate_entity or "climate entity"
    if target is not None:
        parts.append(f"  - HVAC target (from {entity_label}): {target}")

    smart_target = getattr(room, "smart_target", None)
    if smart_target is not None:
        parts.append(f"  - Smart target: {smart_target}")

    comfort = getattr(room, "comfort_score", None)
    if comfort is not None and comfort > 0:
        parts.append(f"  - Comfort score: {comfort}/100")

    efficiency = getattr(room, "efficiency_score", None)
    if efficiency is not None and efficiency > 0:
        parts.append(f"  - Efficiency score: {efficiency}/100")

    occupied = getattr(room, "occupied", None)
    if occupied is not None:
        parts.append(f"  - Occupied: {'yes' if occupied else 'no'}")

    window_open = getattr(room, "window_open", None)
    if window_open is not None:
        parts.append(f"  - Window/door open: {'yes' if window_open else 'no'}")

    action = getattr(room, "hvac_action", None)
    if action is not None:
        parts.append(f"  - HVAC action: {action}")

    runtime = getattr(room, "hvac_runtime_today", None)
    if runtime is not None and runtime > 0:
        parts.append(f"  - HVAC runtime today: {runtime:.0f} min")

    cycles = getattr(room, "hvac_cycles_today", None)
    if cycles is not None and cycles > 0:
        parts.append(f"  - HVAC cycles today: {cycles}")

    trend = getattr(room, "temp_trend", None)
    if trend is not None and trend != 0.0:
        direction = "rising" if trend > 0 else "falling"
        parts.append(f"  - Temp trend: {direction} at {abs(trend):.1f} deg/hr")

    follow_me = getattr(room, "follow_me_active", None)
    if follow_me:
        parts.append("  - Follow-me: ACTIVE (primary room)")

    schedule = getattr(room, "active_schedule", None)
    if schedule:
        parts.append(f"  - Active schedule: {schedule}")

    aux_active = getattr(room, "auxiliary_active", None)
    if aux_active:
        reason = getattr(room, "auxiliary_reason", "")
        parts.append(f"  - Auxiliary heating/cooling: ACTIVE ({reason})")

    override = getattr(room, "user_override_active", None)
    if override:
        parts.append("  - User override: ACTIVE")

    reason = getattr(room, "last_adjustment_reason", "")
    if reason:
        parts.append(f"  - Last adjustment: {reason}")

    return "\n".join(parts)


def _summarize_room(slug: str, name: str, room: Any) -> str:
    """Build a compact one-line summary for a room (used when truncating)."""
    temp = getattr(room, "temperature", "?")
    target = getattr(room, "current_target", "?")
    comfort = getattr(room, "comfort_score", "?")
    occupied = "Y" if getattr(room, "occupied", False) else "N"
    action = getattr(room, "hvac_action", "?")

    return (
        f"  - {name} ({slug}): sensor_temp={temp}, hvac_target={target}, "
        f"comfort={comfort}, occupied={occupied}, hvac={action}"
    )


def _build_hvac_systems_section(rooms_data: dict[str, Any]) -> str:
    """Build an HVAC systems section grouping rooms by shared climate entity."""
    # Map climate_entity -> list of room names
    hvac_groups: dict[str, list[str]] = {}
    for slug, room in rooms_data.items():
        config = getattr(room, "config", None)
        entity = getattr(config, "climate_entity", None) if config else None
        if entity:
            hvac_groups.setdefault(entity, []).append(slug)

    if not hvac_groups:
        return ""

    lines = ["## HVAC Systems"]
    for entity, room_slugs in hvac_groups.items():
        if len(room_slugs) > 1:
            lines.append(
                f"- **{entity}** controls {len(room_slugs)} rooms: "
                f"{', '.join(room_slugs)} "
                f"(shared — one set_temperature affects all)"
            )
        else:
            lines.append(f"- **{entity}** controls: {room_slugs[0]}")

    return "\n".join(lines)
