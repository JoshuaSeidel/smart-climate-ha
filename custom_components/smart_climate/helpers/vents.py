"""Smart vent control logic for Smart Climate."""

from __future__ import annotations

import logging

from homeassistant.core import HomeAssistant

from ..models import RoomState

_LOGGER = logging.getLogger(__name__)

# Safety: never close more than this percentage of all vents
MAX_CLOSED_VENT_RATIO = 0.7
MIN_VENT_POSITION = 10  # Never fully close - static pressure safety


def calculate_vent_positions(
    rooms: dict[str, RoomState],
) -> dict[str, list[tuple[str, int]]]:
    """Calculate optimal vent positions for all rooms.

    Returns dict of room_slug -> list of (vent_entity_id, position_percent).
    Position is 0-100 where 100 is fully open.
    """
    positions: dict[str, list[tuple[str, int]]] = {}
    total_vents = 0
    vents_to_restrict = 0

    # First pass: determine which rooms need more/less airflow
    room_needs: dict[str, float] = {}
    for slug, state in rooms.items():
        if not state.config.vent_entities:
            continue
        total_vents += len(state.config.vent_entities)

        if state.current_target is None or state.temperature is None:
            room_needs[slug] = 0.0
            continue

        # Positive = needs more heating/cooling, negative = over-conditioned
        need = state.current_target - state.temperature
        if state.hvac_action.value == "cooling":
            need = -need  # For cooling, being above target means more need
        room_needs[slug] = need

    if not room_needs:
        return positions

    # Second pass: calculate positions based on need
    for slug, state in rooms.items():
        if not state.config.vent_entities:
            continue

        need = room_needs.get(slug, 0.0)
        vent_positions: list[tuple[str, int]] = []

        if state.window_open:
            # Window open: close vents to save energy
            position = MIN_VENT_POSITION
            vents_to_restrict += len(state.config.vent_entities)
        elif not state.occupied and need <= 0:
            # Unoccupied and at/above target: reduce airflow
            position = max(MIN_VENT_POSITION, 30)
            vents_to_restrict += len(state.config.vent_entities)
        elif need > 2.0:
            # Far from target: fully open
            position = 100
        elif need > 0.5:
            # Approaching target: proportional
            position = min(100, max(50, int(50 + need * 25)))
        elif need < -1.0:
            # Over-conditioned: restrict
            position = max(MIN_VENT_POSITION, int(50 + need * 15))
            vents_to_restrict += len(state.config.vent_entities)
        else:
            # Near target: moderate
            position = 70

        for vent_entity in state.config.vent_entities:
            vent_positions.append((vent_entity, position))

        positions[slug] = vent_positions

    # Safety check: don't restrict too many vents (static pressure)
    if total_vents > 0 and vents_to_restrict / total_vents > MAX_CLOSED_VENT_RATIO:
        _LOGGER.warning(
            "Too many vents would be restricted (%d/%d). "
            "Increasing minimum positions for safety",
            vents_to_restrict,
            total_vents,
        )
        # Raise minimum position on restricted vents
        for slug in positions:
            positions[slug] = [
                (eid, max(40, pos)) for eid, pos in positions[slug]
            ]

    return positions


def generate_vent_recommendations(
    rooms: dict[str, RoomState],
) -> list[dict[str, str]]:
    """Generate text recommendations for manual vent adjustments.

    Used when no smart vent entities are configured.
    """
    recommendations: list[dict[str, str]] = []
    positions = calculate_vent_positions(rooms)

    for slug, vent_positions in positions.items():
        state = rooms[slug]
        for _vent_entity, position in vent_positions:
            if position <= 30:
                action = "Close"
            elif position <= 60:
                action = "Partially close"
            elif position >= 90:
                action = "Fully open"
            else:
                action = f"Open to ~{position}%"

            recommendations.append(
                {
                    "room": state.config.name,
                    "action": f"{action} vents in {state.config.name}",
                    "position": f"{position}%",
                    "reason": _get_vent_reason(state, position),
                }
            )

    return recommendations


def _get_vent_reason(state: RoomState, position: int) -> str:
    """Generate a reason for a vent recommendation."""
    if state.window_open:
        return "Window is open - minimize conditioned air loss"
    if not state.occupied and position < 50:
        return "Room is unoccupied - redirect airflow to occupied rooms"
    if state.temperature and state.current_target:
        diff = state.temperature - state.current_target
        if abs(diff) > 2:
            direction = "above" if diff > 0 else "below"
            return f"Room is {abs(diff):.1f}° {direction} target"
    return "Optimizing airflow balance"


async def async_apply_vent_positions(
    hass: HomeAssistant,
    positions: dict[str, list[tuple[str, int]]],
) -> None:
    """Apply calculated vent positions to smart vent entities."""
    for _slug, vent_positions in positions.items():
        for vent_entity, position in vent_positions:
            domain = vent_entity.split(".")[0]
            try:
                if domain == "cover":
                    await hass.services.async_call(
                        "cover",
                        "set_cover_position",
                        {"entity_id": vent_entity, "position": position},
                    )
                elif domain == "number":
                    await hass.services.async_call(
                        "number",
                        "set_value",
                        {"entity_id": vent_entity, "value": position},
                    )
                elif domain == "switch":
                    service = "turn_on" if position > 50 else "turn_off"
                    await hass.services.async_call(
                        "switch",
                        service,
                        {"entity_id": vent_entity},
                    )
            except Exception:
                _LOGGER.exception("Failed to set vent %s to %d%%", vent_entity, position)
