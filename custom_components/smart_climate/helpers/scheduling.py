"""Room schedule engine for Smart Climate."""

from __future__ import annotations

from datetime import datetime, time

from ..const import CONF_SCHEDULE_ALL_ROOMS
from ..models import Schedule


def parse_time(time_str: str) -> time:
    """Parse HH:MM string to time object."""
    parts = time_str.split(":")
    return time(int(parts[0]), int(parts[1]))


def is_schedule_active_now(
    schedule: Schedule,
    now: datetime | None = None,
) -> bool:
    """Check if a schedule is currently active."""
    if not schedule.enabled:
        return False

    if now is None:
        now = datetime.now()

    # Check day of week (0=Monday in Python's weekday())
    if now.weekday() not in schedule.days:
        return False

    current_time = now.time()
    start = parse_time(schedule.start_time)
    end = parse_time(schedule.end_time)

    # Handle overnight schedules (e.g., 22:00 - 06:00)
    if start <= end:
        return start <= current_time <= end
    else:
        return current_time >= start or current_time <= end


def get_active_schedules_for_room(
    schedules: list[Schedule],
    room_slug: str,
    now: datetime | None = None,
) -> list[Schedule]:
    """Get all currently active schedules that apply to a room.

    Sorted by priority (highest first), then specificity (room-specific > all).
    """
    active: list[Schedule] = []

    for schedule in schedules:
        if not is_schedule_active_now(schedule, now):
            continue

        applies = (
            CONF_SCHEDULE_ALL_ROOMS in schedule.rooms
            or room_slug in schedule.rooms
        )
        if applies:
            active.append(schedule)

    # Sort: highest priority first, then specific rooms before __all__
    active.sort(
        key=lambda s: (
            s.priority,
            0 if CONF_SCHEDULE_ALL_ROOMS not in s.rooms else 1,
        ),
        reverse=True,
    )

    return active


def get_winning_schedule(
    schedules: list[Schedule],
    room_slug: str,
    now: datetime | None = None,
) -> Schedule | None:
    """Get the highest-priority active schedule for a room."""
    active = get_active_schedules_for_room(schedules, room_slug, now)
    return active[0] if active else None


def get_all_active_schedules(
    schedules: list[Schedule],
    room_slugs: list[str],
    now: datetime | None = None,
) -> dict[str, Schedule | None]:
    """Get winning schedule for every room."""
    result: dict[str, Schedule | None] = {}
    for slug in room_slugs:
        result[slug] = get_winning_schedule(schedules, slug, now)
    return result


def get_house_active_schedule(
    schedules: list[Schedule],
    now: datetime | None = None,
) -> str | None:
    """Get the name of any house-wide active schedule."""
    for schedule in schedules:
        if not is_schedule_active_now(schedule, now):
            continue
        if CONF_SCHEDULE_ALL_ROOMS in schedule.rooms:
            return schedule.name
    return None


def get_todays_schedules(
    schedules: list[Schedule],
    now: datetime | None = None,
) -> list[Schedule]:
    """Get all schedules that apply today (for timeline display)."""
    if now is None:
        now = datetime.now()

    return [
        s
        for s in schedules
        if s.enabled and now.weekday() in s.days
    ]
