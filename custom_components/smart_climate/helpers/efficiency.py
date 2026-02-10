"""Efficiency scoring and degree-day calculations for Smart Climate."""

from __future__ import annotations


def calculate_efficiency_score(
    hvac_runtime_minutes: float,
    hvac_cycles: int,
    temp_deviation: float,
    outdoor_temp: float | None = None,
    target_temp: float | None = None,
    window_open: bool = False,
) -> float:
    """Calculate a 0-100 HVAC efficiency score.

    Factors:
    - Runtime vs expected for conditions (less is better)
    - Short-cycling penalty (many on/off cycles is bad)
    - Temperature maintenance (staying near target is efficient)
    - Window-open penalty
    """
    score = 100.0

    # Short-cycling penalty: ideal is fewer, longer runs
    # More than 12 cycles in a day suggests issues
    if hvac_cycles > 0:
        cycle_penalty = min(30.0, max(0.0, (hvac_cycles - 6) * 3.0))
        score -= cycle_penalty

    # Temperature deviation penalty
    # If HVAC is running but temp is far from target, it's inefficient
    deviation_penalty = min(25.0, abs(temp_deviation) * 5.0)
    score -= deviation_penalty

    # Runtime assessment: compare to expected based on outdoor conditions
    if outdoor_temp is not None and target_temp is not None:
        temp_differential = abs(target_temp - outdoor_temp)
        # Rough expected runtime: ~2 min per degree differential per hour
        # For a 24h period, that's ~48 min per degree
        expected_runtime = temp_differential * 48.0
        if expected_runtime > 0:
            runtime_ratio = hvac_runtime_minutes / expected_runtime
            if runtime_ratio > 1.5:
                # Running much more than expected
                runtime_penalty = min(25.0, (runtime_ratio - 1.0) * 15.0)
                score -= runtime_penalty
            elif runtime_ratio < 0.5 and temp_deviation < 1.0:
                # Running less than expected but maintaining temp - bonus
                score = min(100.0, score + 5.0)

    # Window open penalty - HVAC running with window open is wasteful
    if window_open:
        score -= 15.0

    return round(max(0.0, min(100.0, score)), 1)


def calculate_heating_degree_days(
    outdoor_temp: float, base_temp: float = 65.0
) -> float:
    """Calculate heating degree days.

    HDD = max(0, base_temp - outdoor_temp)
    Standard base is 65°F / 18°C.
    """
    return max(0.0, base_temp - outdoor_temp)


def calculate_cooling_degree_days(
    outdoor_temp: float, base_temp: float = 65.0
) -> float:
    """Calculate cooling degree days.

    CDD = max(0, outdoor_temp - base_temp)
    Standard base is 65°F / 18°C.
    """
    return max(0.0, outdoor_temp - base_temp)


def efficiency_label(score: float) -> str:
    """Return a human-readable label for an efficiency score."""
    if score >= 90:
        return "Excellent"
    if score >= 70:
        return "Good"
    if score >= 50:
        return "Fair"
    if score >= 30:
        return "Poor"
    return "Critical"
