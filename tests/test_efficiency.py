"""Tests for efficiency scoring and degree-day calculations."""

from custom_components.smart_climate.helpers.efficiency import (
    calculate_cooling_degree_days,
    calculate_efficiency_score,
    calculate_heating_degree_days,
    efficiency_label,
)

# ---------------------------------------------------------------------------
# calculate_efficiency_score: core tests
# ---------------------------------------------------------------------------


class TestEfficiencyScore:
    """Tests for the HVAC efficiency scoring function."""

    def test_perfect_score_no_issues(self):
        """Score should be 100 with no runtime, no cycles, no deviation."""
        score = calculate_efficiency_score(
            hvac_runtime_minutes=0.0,
            hvac_cycles=0,
            temp_deviation=0.0,
        )
        assert score == 100.0

    def test_perfect_score_few_cycles(self):
        """Score should be 100 with 6 or fewer cycles (no penalty)."""
        score = calculate_efficiency_score(
            hvac_runtime_minutes=100.0,
            hvac_cycles=6,
            temp_deviation=0.0,
        )
        assert score == 100.0

    def test_short_cycling_penalty(self):
        """Many cycles should reduce the score."""
        # 12 cycles: penalty = min(30, max(0, (12-6)*3)) = 18
        score = calculate_efficiency_score(
            hvac_runtime_minutes=100.0,
            hvac_cycles=12,
            temp_deviation=0.0,
        )
        assert score == 82.0

    def test_short_cycling_penalty_capped(self):
        """Short cycling penalty should be capped at 30."""
        # 20 cycles: penalty = min(30, max(0, (20-6)*3)) = min(30, 42) = 30
        score = calculate_efficiency_score(
            hvac_runtime_minutes=100.0,
            hvac_cycles=20,
            temp_deviation=0.0,
        )
        assert score == 70.0

    def test_temperature_deviation_penalty(self):
        """Temperature deviation should reduce the score."""
        # deviation=3.0: penalty = min(25, 3.0*5) = 15
        score = calculate_efficiency_score(
            hvac_runtime_minutes=0.0,
            hvac_cycles=0,
            temp_deviation=3.0,
        )
        assert score == 85.0

    def test_temperature_deviation_penalty_capped(self):
        """Deviation penalty should be capped at 25."""
        # deviation=10: penalty = min(25, 10*5) = 25
        score = calculate_efficiency_score(
            hvac_runtime_minutes=0.0,
            hvac_cycles=0,
            temp_deviation=10.0,
        )
        assert score == 75.0

    def test_window_open_penalty(self):
        """Window open should add a 15-point penalty."""
        score = calculate_efficiency_score(
            hvac_runtime_minutes=0.0,
            hvac_cycles=0,
            temp_deviation=0.0,
            window_open=True,
        )
        assert score == 85.0

    def test_runtime_over_expected(self):
        """Running much more than expected should penalize efficiency."""
        # outdoor=90, target=72 -> differential=18, expected=18*48=864
        # runtime=2000 -> ratio=2000/864=2.31 -> penalty=min(25,(2.31-1)*15)=min(25,19.7)=19.7
        score = calculate_efficiency_score(
            hvac_runtime_minutes=2000.0,
            hvac_cycles=0,
            temp_deviation=0.0,
            outdoor_temp=90.0,
            target_temp=72.0,
        )
        assert score < 100.0
        # Verify it got penalized
        assert score < 85.0

    def test_runtime_efficient_bonus(self):
        """Running less than expected while maintaining temp gives a bonus."""
        # outdoor=80, target=72 -> differential=8, expected=8*48=384
        # runtime=100 -> ratio=100/384=0.26 (<0.5) and deviation=0.5 (<1.0) -> bonus
        score = calculate_efficiency_score(
            hvac_runtime_minutes=100.0,
            hvac_cycles=0,
            temp_deviation=0.5,
            outdoor_temp=80.0,
            target_temp=72.0,
        )
        assert score == 100.0  # 100 + 5 clamped to 100

    def test_runtime_efficient_bonus_capped_at_100(self):
        """Efficiency bonus should not push score above 100."""
        score = calculate_efficiency_score(
            hvac_runtime_minutes=50.0,
            hvac_cycles=0,
            temp_deviation=0.0,
            outdoor_temp=80.0,
            target_temp=72.0,
        )
        assert score <= 100.0

    def test_combined_penalties(self):
        """Multiple penalties should stack."""
        # cycles=12 -> penalty=18
        # deviation=2 -> penalty=10
        # window_open -> penalty=15
        # total penalty = 43, score = 100-43 = 57
        score = calculate_efficiency_score(
            hvac_runtime_minutes=100.0,
            hvac_cycles=12,
            temp_deviation=2.0,
            window_open=True,
        )
        assert score == 57.0

    def test_all_max_penalties(self):
        """All maximum penalties together should clamp at 0."""
        # cycles=20 -> 30
        # deviation=10 -> 25
        # window -> 15
        # runtime over-run -> up to 25
        # Total max possible penalty = 95, which would be 5.0
        score = calculate_efficiency_score(
            hvac_runtime_minutes=5000.0,
            hvac_cycles=20,
            temp_deviation=10.0,
            outdoor_temp=90.0,
            target_temp=72.0,
            window_open=True,
        )
        assert score >= 0.0

    def test_score_never_below_zero(self):
        """Score should never go below 0 regardless of penalties."""
        score = calculate_efficiency_score(
            hvac_runtime_minutes=10000.0,
            hvac_cycles=100,
            temp_deviation=50.0,
            window_open=True,
        )
        assert score >= 0.0

    def test_score_never_above_100(self):
        """Score should never exceed 100."""
        score = calculate_efficiency_score(
            hvac_runtime_minutes=0.0,
            hvac_cycles=0,
            temp_deviation=0.0,
            outdoor_temp=72.0,
            target_temp=72.0,
        )
        assert score <= 100.0

    def test_no_outdoor_temp_skips_runtime_assessment(self):
        """Without outdoor temp, runtime assessment is skipped."""
        score_no_outdoor = calculate_efficiency_score(
            hvac_runtime_minutes=5000.0,
            hvac_cycles=0,
            temp_deviation=0.0,
        )
        # No runtime penalty without outdoor/target temp
        assert score_no_outdoor == 100.0

    def test_zero_differential_skips_runtime_assessment(self):
        """When outdoor = target, expected runtime is 0, division avoided."""
        score = calculate_efficiency_score(
            hvac_runtime_minutes=100.0,
            hvac_cycles=0,
            temp_deviation=0.0,
            outdoor_temp=72.0,
            target_temp=72.0,
        )
        # expected_runtime = 0 * 48 = 0, so runtime assessment is skipped
        assert score == 100.0

    def test_score_is_rounded(self):
        """Score should be rounded to one decimal place."""
        score = calculate_efficiency_score(
            hvac_runtime_minutes=100.0,
            hvac_cycles=7,
            temp_deviation=0.0,
        )
        assert score == round(score, 1)


# ---------------------------------------------------------------------------
# Degree day calculations
# ---------------------------------------------------------------------------


class TestDegreeDays:
    """Tests for heating and cooling degree day calculations."""

    def test_hdd_cold_day(self):
        """HDD should be positive when outdoor temp is below base."""
        hdd = calculate_heating_degree_days(30.0, base_temp=65.0)
        assert hdd == 35.0

    def test_hdd_warm_day(self):
        """HDD should be 0 when outdoor temp is above base."""
        hdd = calculate_heating_degree_days(80.0, base_temp=65.0)
        assert hdd == 0.0

    def test_hdd_at_base(self):
        """HDD should be 0 when outdoor temp equals base."""
        hdd = calculate_heating_degree_days(65.0, base_temp=65.0)
        assert hdd == 0.0

    def test_cdd_hot_day(self):
        """CDD should be positive when outdoor temp is above base."""
        cdd = calculate_cooling_degree_days(85.0, base_temp=65.0)
        assert cdd == 20.0

    def test_cdd_cold_day(self):
        """CDD should be 0 when outdoor temp is below base."""
        cdd = calculate_cooling_degree_days(50.0, base_temp=65.0)
        assert cdd == 0.0

    def test_cdd_at_base(self):
        """CDD should be 0 when outdoor temp equals base."""
        cdd = calculate_cooling_degree_days(65.0, base_temp=65.0)
        assert cdd == 0.0

    def test_hdd_custom_base(self):
        """HDD with custom base temperature."""
        hdd = calculate_heating_degree_days(50.0, base_temp=55.0)
        assert hdd == 5.0

    def test_cdd_custom_base(self):
        """CDD with custom base temperature."""
        cdd = calculate_cooling_degree_days(75.0, base_temp=70.0)
        assert cdd == 5.0

    def test_hdd_never_negative(self):
        """HDD should never be negative."""
        hdd = calculate_heating_degree_days(100.0)
        assert hdd >= 0.0

    def test_cdd_never_negative(self):
        """CDD should never be negative."""
        cdd = calculate_cooling_degree_days(-10.0)
        assert cdd >= 0.0


# ---------------------------------------------------------------------------
# efficiency_label tests
# ---------------------------------------------------------------------------


class TestEfficiencyLabel:
    """Tests for the efficiency_label function."""

    def test_excellent(self):
        """Score >= 90 should return 'Excellent'."""
        assert efficiency_label(95.0) == "Excellent"
        assert efficiency_label(90.0) == "Excellent"

    def test_good(self):
        """Score >= 70 and < 90 should return 'Good'."""
        assert efficiency_label(75.0) == "Good"
        assert efficiency_label(70.0) == "Good"
        assert efficiency_label(89.9) == "Good"

    def test_fair(self):
        """Score >= 50 and < 70 should return 'Fair'."""
        assert efficiency_label(50.0) == "Fair"
        assert efficiency_label(69.9) == "Fair"

    def test_poor(self):
        """Score >= 30 and < 50 should return 'Poor'."""
        assert efficiency_label(30.0) == "Poor"
        assert efficiency_label(49.9) == "Poor"

    def test_critical(self):
        """Score < 30 should return 'Critical'."""
        assert efficiency_label(29.9) == "Critical"
        assert efficiency_label(0.0) == "Critical"
