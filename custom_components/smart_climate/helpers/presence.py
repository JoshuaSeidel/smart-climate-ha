"""Follow-me presence logic for Smart Climate."""

from __future__ import annotations

from datetime import datetime, timedelta

from ..const import DEFAULT_AWAY_TEMP_OFFSET, DEFAULT_FOLLOW_ME_COOLDOWN
from ..models import RoomState


def determine_follow_me_target(
    rooms: dict[str, RoomState],
    current_target: str | None = None,
    cooldown_minutes: int = DEFAULT_FOLLOW_ME_COOLDOWN,
) -> str | None:
    """Determine which room should be the follow-me target.

    Rules:
    1. Room must have presence sensors and be occupied
    2. Most recently active room wins (by last_presence_time)
    3. If tied, higher priority room wins
    4. Cooldown prevents thrashing between rooms
    """
    now = datetime.now()
    occupied_rooms: list[tuple[str, RoomState]] = []

    for slug, state in rooms.items():
        if state.occupied and state.config.presence_sensors:
            occupied_rooms.append((slug, state))

    if not occupied_rooms:
        return None

    # Sort by last presence time (most recent first), then by priority (highest first)
    occupied_rooms.sort(
        key=lambda x: (
            x[1].last_presence_time or datetime.min,
            x[1].config.priority,
        ),
        reverse=True,
    )

    best_candidate = occupied_rooms[0][0]

    # Apply cooldown: don't switch if we recently changed
    if current_target and current_target != best_candidate:
        current_room = rooms.get(current_target)
        if current_room and current_room.occupied:
            if current_room.last_presence_time:
                time_since = now - current_room.last_presence_time
                if time_since < timedelta(minutes=cooldown_minutes):
                    return current_target

    return best_candidate


def calculate_follow_me_targets(
    rooms: dict[str, RoomState],
    primary_room: str | None,
    away_temp_offset: float = DEFAULT_AWAY_TEMP_OFFSET,
) -> dict[str, float | None]:
    """Calculate temperature targets for all rooms based on follow-me.

    Returns dict of room_slug -> target_temp adjustment.
    Primary room gets no offset, occupied rooms get small offset,
    unoccupied rooms get full away offset.
    """
    targets: dict[str, float | None] = {}

    for slug, state in rooms.items():
        if state.current_target is None:
            targets[slug] = None
            continue

        if slug == primary_room:
            # Primary room: target + room offset
            targets[slug] = state.current_target + state.config.target_temp_offset
        elif state.occupied:
            # Other occupied rooms: slight offset
            targets[slug] = state.current_target + state.config.target_temp_offset
        else:
            # Unoccupied: apply away offset
            # If heating, lower the target; if cooling, raise it
            if state.hvac_action.value in ("heating",):
                targets[slug] = state.current_target - away_temp_offset
            elif state.hvac_action.value in ("cooling",):
                targets[slug] = state.current_target + away_temp_offset
            else:
                targets[slug] = state.current_target - away_temp_offset

    return targets
