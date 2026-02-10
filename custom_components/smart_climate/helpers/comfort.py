"""Comfort score calculation for Smart Climate."""

from __future__ import annotations

from ..const import DEFAULT_COMFORT_HUMIDITY_WEIGHT, DEFAULT_COMFORT_TEMP_WEIGHT


def calculate_comfort_score(
    current_temp: float | None,
    target_temp: float | None,
    humidity: float | None = None,
    temp_weight: float = DEFAULT_COMFORT_TEMP_WEIGHT,
    humidity_weight: float = DEFAULT_COMFORT_HUMIDITY_WEIGHT,
) -> float:
    """Calculate a 0-100 comfort score for a room.

    Score is based on:
    - Temperature deviation from target (primary factor)
    - Humidity comfort range (secondary factor, 30-60% ideal)
    """
    if current_temp is None or target_temp is None:
        return 0.0

    # Temperature score: 100 when at target, decreasing with deviation
    temp_diff = abs(current_temp - target_temp)
    if temp_diff <= 0.5:
        temp_score = 100.0
    elif temp_diff <= 1.0:
        temp_score = 95.0
    elif temp_diff <= 2.0:
        temp_score = 85.0 - (temp_diff - 1.0) * 10.0
    elif temp_diff <= 3.0:
        temp_score = 75.0 - (temp_diff - 2.0) * 15.0
    elif temp_diff <= 5.0:
        temp_score = 60.0 - (temp_diff - 3.0) * 15.0
    else:
        temp_score = max(0.0, 30.0 - (temp_diff - 5.0) * 6.0)

    # Humidity score: 100 in ideal range (30-60%), decreasing outside
    if humidity is not None:
        if 30.0 <= humidity <= 60.0:
            humidity_score = 100.0
        elif 20.0 <= humidity < 30.0:
            humidity_score = 70.0 + (humidity - 20.0) * 3.0
        elif 60.0 < humidity <= 70.0:
            humidity_score = 70.0 + (70.0 - humidity) * 3.0
        elif humidity < 20.0:
            humidity_score = max(0.0, 70.0 - (20.0 - humidity) * 5.0)
        else:
            humidity_score = max(0.0, 70.0 - (humidity - 70.0) * 5.0)

        score = temp_score * temp_weight + humidity_score * humidity_weight
    else:
        score = temp_score

    return round(max(0.0, min(100.0, score)), 1)


def comfort_label(score: float) -> str:
    """Return a human-readable label for a comfort score."""
    if score >= 90:
        return "Excellent"
    if score >= 70:
        return "Good"
    if score >= 50:
        return "Fair"
    if score >= 30:
        return "Poor"
    return "Critical"
