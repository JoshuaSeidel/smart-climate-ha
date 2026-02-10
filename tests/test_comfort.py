"""Tests for comfort score calculations."""

from custom_components.smart_climate.helpers.comfort import (
    calculate_comfort_score,
    comfort_label,
)

# ---------------------------------------------------------------------------
# calculate_comfort_score: temperature-only tests
# ---------------------------------------------------------------------------


class TestComfortScoreTemperature:
    """Tests focused on the temperature component of comfort scoring."""

    def test_perfect_score_at_target(self):
        """Score should be 100 when current temp equals target, no humidity."""
        score = calculate_comfort_score(
            current_temp=72.0, target_temp=72.0, humidity=None
        )
        assert score == 100.0

    def test_score_within_half_degree(self):
        """Score should be 100 when deviation is <= 0.5 degrees."""
        score = calculate_comfort_score(
            current_temp=72.3, target_temp=72.0, humidity=None
        )
        assert score == 100.0

        score_neg = calculate_comfort_score(
            current_temp=71.5, target_temp=72.0, humidity=None
        )
        assert score_neg == 100.0

    def test_score_at_exactly_half_degree(self):
        """Score should be 100 when deviation is exactly 0.5."""
        score = calculate_comfort_score(
            current_temp=72.5, target_temp=72.0, humidity=None
        )
        assert score == 100.0

    def test_score_deviation_one_degree(self):
        """Score should be 95 when deviation is 1.0 degree."""
        score = calculate_comfort_score(
            current_temp=73.0, target_temp=72.0, humidity=None
        )
        assert score == 95.0

    def test_score_deviation_two_degrees(self):
        """Score should degrade in the 1-2 degree range."""
        # At 2.0 deviation: 85.0 - (2.0-1.0)*10.0 = 75.0
        score = calculate_comfort_score(
            current_temp=74.0, target_temp=72.0, humidity=None
        )
        assert score == 75.0

    def test_score_deviation_three_degrees(self):
        """Score should degrade in the 2-3 degree range."""
        # At 3.0 deviation: 75.0 - (3.0-2.0)*15.0 = 60.0
        score = calculate_comfort_score(
            current_temp=75.0, target_temp=72.0, humidity=None
        )
        assert score == 60.0

    def test_score_deviation_five_degrees(self):
        """Score should degrade in the 3-5 degree range."""
        # At 5.0 deviation: 60.0 - (5.0-3.0)*15.0 = 30.0
        score = calculate_comfort_score(
            current_temp=77.0, target_temp=72.0, humidity=None
        )
        assert score == 30.0

    def test_score_deviation_eight_degrees(self):
        """Score at extreme deviation (>5 degrees)."""
        # At 8.0 deviation: max(0, 30.0 - (8.0-5.0)*6.0) = max(0, 12.0) = 12.0
        score = calculate_comfort_score(
            current_temp=80.0, target_temp=72.0, humidity=None
        )
        assert score == 12.0

    def test_score_very_large_deviation(self):
        """Score should never go below 0."""
        score = calculate_comfort_score(
            current_temp=90.0, target_temp=72.0, humidity=None
        )
        assert score >= 0.0

    def test_score_deviation_negative_direction(self):
        """Score should be the same regardless of direction of deviation."""
        score_above = calculate_comfort_score(
            current_temp=74.0, target_temp=72.0, humidity=None
        )
        score_below = calculate_comfort_score(
            current_temp=70.0, target_temp=72.0, humidity=None
        )
        assert score_above == score_below

    def test_none_temp_returns_zero(self):
        """Score should be 0 when current_temp is None."""
        score = calculate_comfort_score(
            current_temp=None, target_temp=72.0, humidity=50.0
        )
        assert score == 0.0

    def test_none_target_returns_zero(self):
        """Score should be 0 when target_temp is None."""
        score = calculate_comfort_score(
            current_temp=72.0, target_temp=None, humidity=50.0
        )
        assert score == 0.0

    def test_both_none_returns_zero(self):
        """Score should be 0 when both temps are None."""
        score = calculate_comfort_score(
            current_temp=None, target_temp=None, humidity=50.0
        )
        assert score == 0.0


# ---------------------------------------------------------------------------
# calculate_comfort_score: humidity component tests
# ---------------------------------------------------------------------------


class TestComfortScoreHumidity:
    """Tests focused on the humidity component of comfort scoring."""

    def test_perfect_with_ideal_humidity(self):
        """Score should be 100 when at target temp with ideal humidity."""
        score = calculate_comfort_score(
            current_temp=72.0, target_temp=72.0, humidity=45.0
        )
        # temp_score=100 * 0.7 + humidity_score=100 * 0.3 = 100
        assert score == 100.0

    def test_ideal_humidity_range_lower_bound(self):
        """Humidity of 30% should still be in ideal range (score 100)."""
        score = calculate_comfort_score(
            current_temp=72.0, target_temp=72.0, humidity=30.0
        )
        assert score == 100.0

    def test_ideal_humidity_range_upper_bound(self):
        """Humidity of 60% should still be in ideal range (score 100)."""
        score = calculate_comfort_score(
            current_temp=72.0, target_temp=72.0, humidity=60.0
        )
        assert score == 100.0

    def test_low_humidity_below_30(self):
        """Humidity between 20-30% should penalize but not drastically."""
        # humidity=25 -> 70 + (25-20)*3 = 85
        score = calculate_comfort_score(
            current_temp=72.0, target_temp=72.0, humidity=25.0
        )
        # temp=100*0.7 + humidity=85*0.3 = 70 + 25.5 = 95.5
        assert score == 95.5

    def test_very_low_humidity(self):
        """Humidity below 20% should penalize significantly."""
        # humidity=10 -> max(0, 70 - (20-10)*5) = max(0, 20) = 20
        score = calculate_comfort_score(
            current_temp=72.0, target_temp=72.0, humidity=10.0
        )
        # temp=100*0.7 + humidity=20*0.3 = 70 + 6 = 76
        assert score == 76.0

    def test_high_humidity_above_60(self):
        """Humidity between 60-70% should penalize."""
        # humidity=65 -> 70 + (70-65)*3 = 85
        score = calculate_comfort_score(
            current_temp=72.0, target_temp=72.0, humidity=65.0
        )
        # temp=100*0.7 + humidity=85*0.3 = 95.5
        assert score == 95.5

    def test_very_high_humidity(self):
        """Humidity above 70% should penalize significantly."""
        # humidity=80 -> max(0, 70 - (80-70)*5) = max(0, 20) = 20
        score = calculate_comfort_score(
            current_temp=72.0, target_temp=72.0, humidity=80.0
        )
        # temp=100*0.7 + humidity=20*0.3 = 76
        assert score == 76.0

    def test_extreme_humidity(self):
        """Humidity at 90% should result in very low humidity score."""
        # humidity=90 -> max(0, 70 - (90-70)*5) = max(0, -30) = 0
        score = calculate_comfort_score(
            current_temp=72.0, target_temp=72.0, humidity=90.0
        )
        # temp=100*0.7 + humidity=0*0.3 = 70
        assert score == 70.0

    def test_zero_humidity(self):
        """Humidity of 0% should give very low humidity score."""
        # humidity=0 -> max(0, 70 - (20-0)*5) = max(0, -30) = 0
        score = calculate_comfort_score(
            current_temp=72.0, target_temp=72.0, humidity=0.0
        )
        # temp=100*0.7 + humidity=0*0.3 = 70
        assert score == 70.0


# ---------------------------------------------------------------------------
# calculate_comfort_score: combined & custom weights
# ---------------------------------------------------------------------------


class TestComfortScoreCombined:
    """Tests for combined temp/humidity and custom weight scenarios."""

    def test_custom_weights(self):
        """Custom weights should affect the final score."""
        # All temp weight, no humidity
        score_temp_only = calculate_comfort_score(
            current_temp=72.0,
            target_temp=72.0,
            humidity=90.0,
            temp_weight=1.0,
            humidity_weight=0.0,
        )
        # humidity_score=0 but weight is 0, so 100*1.0 + 0*0.0 = 100
        assert score_temp_only == 100.0

    def test_custom_weights_humidity_heavy(self):
        """Heavy humidity weight should amplify humidity penalties."""
        score = calculate_comfort_score(
            current_temp=72.0,
            target_temp=72.0,
            humidity=90.0,
            temp_weight=0.0,
            humidity_weight=1.0,
        )
        # temp_score=100*0.0 + humidity_score=0*1.0 = 0
        assert score == 0.0

    def test_score_never_exceeds_100(self):
        """Score should be clamped at 100 maximum."""
        # Even with perfect conditions + any rounding
        score = calculate_comfort_score(
            current_temp=72.0,
            target_temp=72.0,
            humidity=45.0,
            temp_weight=0.7,
            humidity_weight=0.3,
        )
        assert score <= 100.0

    def test_score_never_below_zero(self):
        """Score should be clamped at 0 minimum."""
        score = calculate_comfort_score(
            current_temp=100.0,
            target_temp=60.0,
            humidity=100.0,
            temp_weight=0.7,
            humidity_weight=0.3,
        )
        assert score >= 0.0

    def test_combined_bad_temp_good_humidity(self):
        """Bad temp but good humidity should give partial credit."""
        score = calculate_comfort_score(
            current_temp=77.0,
            target_temp=72.0,
            humidity=45.0,
        )
        # temp_diff=5 -> temp_score=30
        # humidity=45 -> humidity_score=100
        # combined = 30*0.7 + 100*0.3 = 21 + 30 = 51
        assert score == 51.0

    def test_combined_good_temp_bad_humidity(self):
        """Good temp with bad humidity should still score well due to weighting."""
        score = calculate_comfort_score(
            current_temp=72.0,
            target_temp=72.0,
            humidity=90.0,
        )
        # temp=100*0.7 + humidity=0*0.3 = 70
        assert score == 70.0

    def test_score_is_rounded(self):
        """Score should be rounded to one decimal place."""
        score = calculate_comfort_score(
            current_temp=72.0,
            target_temp=72.0,
            humidity=25.0,
        )
        # Should be rounded to 1 decimal
        assert score == round(score, 1)


# ---------------------------------------------------------------------------
# comfort_label tests
# ---------------------------------------------------------------------------


class TestComfortLabel:
    """Tests for comfort_label function."""

    def test_excellent_at_90(self):
        """Score of 90 should return 'Excellent'."""
        assert comfort_label(90.0) == "Excellent"

    def test_excellent_at_100(self):
        """Score of 100 should return 'Excellent'."""
        assert comfort_label(100.0) == "Excellent"

    def test_good_at_70(self):
        """Score of 70 should return 'Good'."""
        assert comfort_label(70.0) == "Good"

    def test_good_at_89(self):
        """Score of 89 should return 'Good'."""
        assert comfort_label(89.9) == "Good"

    def test_fair_at_50(self):
        """Score of 50 should return 'Fair'."""
        assert comfort_label(50.0) == "Fair"

    def test_fair_at_69(self):
        """Score of 69 should return 'Fair'."""
        assert comfort_label(69.9) == "Fair"

    def test_poor_at_30(self):
        """Score of 30 should return 'Poor'."""
        assert comfort_label(30.0) == "Poor"

    def test_poor_at_49(self):
        """Score of 49 should return 'Poor'."""
        assert comfort_label(49.9) == "Poor"

    def test_critical_at_29(self):
        """Score of 29 should return 'Critical'."""
        assert comfort_label(29.9) == "Critical"

    def test_critical_at_0(self):
        """Score of 0 should return 'Critical'."""
        assert comfort_label(0.0) == "Critical"
