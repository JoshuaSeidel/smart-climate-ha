"""Tests for the button entity and enhanced sensor attributes."""

from datetime import datetime
from unittest.mock import MagicMock

from custom_components.smart_climate.const import (
    AI_PROVIDER_NONE,
    CONF_AI_PROVIDER,
    ENTITY_PREFIX,
)

# ---------------------------------------------------------------------------
# Button entity
# ---------------------------------------------------------------------------


class TestButtonEntity:
    """Tests for SmartClimateTriggerAnalysisButton."""

    def test_button_module_importable(self):
        """button.py should be importable."""
        from custom_components.smart_climate.button import (
            SmartClimateTriggerAnalysisButton,
        )

        assert SmartClimateTriggerAnalysisButton is not None

    def test_button_has_async_press(self):
        """Button entity should have async_press method."""
        from custom_components.smart_climate.button import (
            SmartClimateTriggerAnalysisButton,
        )

        assert hasattr(SmartClimateTriggerAnalysisButton, "async_press")

    def test_button_icon(self):
        """Button should have brain icon."""
        from custom_components.smart_climate.button import (
            SmartClimateTriggerAnalysisButton,
        )

        assert SmartClimateTriggerAnalysisButton._attr_icon == "mdi:brain"

    def test_button_entity_id_format(self):
        """Button entity_id should follow sc_ prefix convention."""
        expected = f"button.{ENTITY_PREFIX}_trigger_analysis"
        assert expected == "button.sc_trigger_analysis"

    def test_button_platform_setup_importable(self):
        """async_setup_entry should be importable from button module."""
        from custom_components.smart_climate.button import async_setup_entry

        assert async_setup_entry is not None


# ---------------------------------------------------------------------------
# Enhanced daily summary sensor attributes
# ---------------------------------------------------------------------------


class TestDailySummarySensorAttributes:
    """Tests for SmartClimateDailySummarySensor extra_state_attributes."""

    def test_summary_sensor_has_extra_attributes(self):
        """Daily summary sensor should have extra_state_attributes property."""
        from custom_components.smart_climate.sensor import (
            SmartClimateDailySummarySensor,
        )

        assert hasattr(SmartClimateDailySummarySensor, "extra_state_attributes")

    def test_summary_attributes_structure(
        self, sample_house_state, sample_config_data
    ):
        """Summary attributes should contain full_summary, provider, analysis_time."""
        from custom_components.smart_climate.sensor import (
            SmartClimateDailySummarySensor,
        )

        sample_house_state.ai_daily_summary = "Test summary text that is very long"
        sample_house_state.last_analysis_time = datetime(2026, 2, 10, 6, 0, 0)

        coordinator = MagicMock()
        coordinator.data = {"house": sample_house_state}
        coordinator.config_entry = MagicMock()
        coordinator.config_entry.entry_id = "test_entry"
        coordinator.entry = MagicMock()
        coordinator.entry.data = {CONF_AI_PROVIDER: "openai"}

        sensor = SmartClimateDailySummarySensor(coordinator)
        attrs = sensor.extra_state_attributes

        assert "full_summary" in attrs
        assert attrs["full_summary"] == "Test summary text that is very long"
        assert "provider" in attrs
        assert attrs["provider"] == "openai"
        assert "analysis_time" in attrs
        assert attrs["analysis_time"] == "2026-02-10T06:00:00"

    def test_summary_attributes_empty_when_no_house(self):
        """Summary attributes should be empty dict when house state is None."""
        from custom_components.smart_climate.sensor import (
            SmartClimateDailySummarySensor,
        )

        coordinator = MagicMock()
        coordinator.data = {}
        coordinator.config_entry = MagicMock()
        coordinator.config_entry.entry_id = "test_entry"

        sensor = SmartClimateDailySummarySensor(coordinator)
        assert sensor.extra_state_attributes == {}

    def test_summary_attributes_no_analysis_time(self, sample_house_state):
        """analysis_time should be None when no analysis has run."""
        from custom_components.smart_climate.sensor import (
            SmartClimateDailySummarySensor,
        )

        sample_house_state.last_analysis_time = None

        coordinator = MagicMock()
        coordinator.data = {"house": sample_house_state}
        coordinator.config_entry = MagicMock()
        coordinator.config_entry.entry_id = "test_entry"
        coordinator.entry = MagicMock()
        coordinator.entry.data = {CONF_AI_PROVIDER: AI_PROVIDER_NONE}

        sensor = SmartClimateDailySummarySensor(coordinator)
        attrs = sensor.extra_state_attributes
        assert attrs["analysis_time"] is None


# ---------------------------------------------------------------------------
# Enhanced suggestion count sensor attributes
# ---------------------------------------------------------------------------


class TestSuggestionCountSensorAttributes:
    """Tests for SmartClimateSuggestionCountSensor enhanced attributes."""

    def test_suggestion_attributes_contain_suggestions_list(
        self, sample_house_state, sample_suggestion
    ):
        """Suggestion count sensor should include full suggestions list."""
        from custom_components.smart_climate.sensor import (
            SmartClimateSuggestionCountSensor,
        )

        sample_house_state.suggestions = [sample_suggestion]

        coordinator = MagicMock()
        coordinator.data = {"house": sample_house_state}
        coordinator.config_entry = MagicMock()
        coordinator.config_entry.entry_id = "test_entry"

        sensor = SmartClimateSuggestionCountSensor(coordinator)
        attrs = sensor.extra_state_attributes

        assert "suggestions" in attrs
        assert len(attrs["suggestions"]) == 1

        s = attrs["suggestions"][0]
        assert s["id"] == sample_suggestion.id
        assert s["title"] == sample_suggestion.title
        assert s["description"] == sample_suggestion.description
        assert s["reasoning"] == sample_suggestion.reasoning
        assert s["confidence"] == sample_suggestion.confidence
        assert s["priority"] == sample_suggestion.priority
        assert s["status"] == sample_suggestion.status
        assert s["room"] == sample_suggestion.room
        assert s["action_type"] == sample_suggestion.action_type

    def test_suggestion_attributes_still_have_legacy_fields(
        self, sample_house_state, sample_suggestion
    ):
        """Suggestion count sensor should still have total_suggestions and pending_titles."""
        from custom_components.smart_climate.sensor import (
            SmartClimateSuggestionCountSensor,
        )

        sample_house_state.suggestions = [sample_suggestion]

        coordinator = MagicMock()
        coordinator.data = {"house": sample_house_state}
        coordinator.config_entry = MagicMock()
        coordinator.config_entry.entry_id = "test_entry"

        sensor = SmartClimateSuggestionCountSensor(coordinator)
        attrs = sensor.extra_state_attributes

        assert "total_suggestions" in attrs
        assert attrs["total_suggestions"] == 1
        assert "pending_titles" in attrs
        assert sample_suggestion.title in attrs["pending_titles"]

    def test_suggestion_attributes_empty_list_when_no_suggestions(
        self, sample_house_state
    ):
        """Suggestions list should be empty when no suggestions exist."""
        from custom_components.smart_climate.sensor import (
            SmartClimateSuggestionCountSensor,
        )

        sample_house_state.suggestions = []

        coordinator = MagicMock()
        coordinator.data = {"house": sample_house_state}
        coordinator.config_entry = MagicMock()
        coordinator.config_entry.entry_id = "test_entry"

        sensor = SmartClimateSuggestionCountSensor(coordinator)
        attrs = sensor.extra_state_attributes

        assert attrs["suggestions"] == []
        assert attrs["total_suggestions"] == 0
        assert attrs["pending_titles"] == []


# ---------------------------------------------------------------------------
# Platform registration
# ---------------------------------------------------------------------------


class TestPlatformRegistration:
    """Tests that button platform is registered."""

    def test_button_in_platforms_list(self):
        """Platform.BUTTON should be in PLATFORMS_LIST."""
        from custom_components.smart_climate import PLATFORMS_LIST

        platform_values = [p if isinstance(p, str) else str(p) for p in PLATFORMS_LIST]
        assert "button" in platform_values

    def test_button_in_const_platforms(self):
        """'button' should be in the PLATFORMS constant."""
        from custom_components.smart_climate.const import PLATFORMS

        assert "button" in PLATFORMS


# ---------------------------------------------------------------------------
# Coordinator notification method
# ---------------------------------------------------------------------------


class TestCoordinatorNotification:
    """Tests for notification methods."""

    def test_coordinator_has_send_notification(self):
        """Coordinator should have _send_notification."""
        from custom_components.smart_climate.coordinator import (
            SmartClimateCoordinator,
        )

        assert hasattr(SmartClimateCoordinator, "_send_notification")

    def test_coordinator_has_format_notification(self):
        """Coordinator should have _format_analysis_notification."""
        from custom_components.smart_climate.coordinator import (
            SmartClimateCoordinator,
        )

        assert hasattr(SmartClimateCoordinator, "_format_analysis_notification")
