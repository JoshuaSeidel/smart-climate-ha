"""Tests for AI provider abstractions and response parsing."""
import json
from datetime import datetime, timedelta

import pytest

from custom_components.smart_climate.ai.analysis import (
    ALLOWED_ACTION_TYPES,
    MAX_SAFE_TEMP,
    MIN_SAFE_TEMP,
    parse_ai_response,
)
from custom_components.smart_climate.ai.prompts import (
    build_system_prompt,
    build_user_prompt,
)
from custom_components.smart_climate.ai.provider import (
    AIConnectionError,
    AIProviderBase,
    AIProviderError,
    AIResponseError,
    NoOpProvider,
    create_ai_provider,
)
from custom_components.smart_climate.const import (
    AI_PROVIDER_ANTHROPIC,
    AI_PROVIDER_GEMINI,
    AI_PROVIDER_GROK,
    AI_PROVIDER_OLLAMA,
    AI_PROVIDER_OPENAI,
    SUGGESTION_PENDING,
)
from custom_components.smart_climate.models import (
    HouseState,
    HVACAction,
    RoomConfig,
    RoomState,
    Suggestion,
    SuggestionPriority,
)

# ---------------------------------------------------------------------------
# NoOpProvider tests
# ---------------------------------------------------------------------------


class TestNoOpProvider:
    """Tests for the NoOpProvider (AI disabled)."""

    @pytest.mark.asyncio
    async def test_analyze_returns_empty_json(self):
        """NoOpProvider.analyze should return an empty JSON object string."""
        provider = NoOpProvider({})
        result = await provider.analyze("system", "user")
        assert result == "{}"

    @pytest.mark.asyncio
    async def test_test_connection_returns_true(self):
        """NoOpProvider.test_connection should always return True."""
        provider = NoOpProvider({})
        result = await provider.test_connection()
        assert result is True

    def test_inherits_from_base(self):
        """NoOpProvider should be an instance of AIProviderBase."""
        provider = NoOpProvider({})
        assert isinstance(provider, AIProviderBase)

    def test_stores_config(self):
        """Provider should store the config dict."""
        config = {"api_key": "test", "model": "test-model"}
        provider = NoOpProvider(config)
        assert provider._config == config


# ---------------------------------------------------------------------------
# Factory tests
# ---------------------------------------------------------------------------


class TestProviderFactory:
    """Tests for the create_ai_provider factory function."""

    def test_factory_returns_noop_for_none(self):
        """Factory should return NoOpProvider for 'none'."""
        provider = create_ai_provider("none", {})
        assert isinstance(provider, NoOpProvider)

    def test_factory_returns_openai(self):
        """Factory should return OpenAIProvider for 'openai'."""
        from custom_components.smart_climate.ai.openai_provider import OpenAIProvider

        provider = create_ai_provider(AI_PROVIDER_OPENAI, {"api_key": "sk-test"})
        assert isinstance(provider, OpenAIProvider)

    def test_factory_returns_anthropic(self):
        """Factory should return AnthropicProvider for 'anthropic'."""
        from custom_components.smart_climate.ai.anthropic_provider import (
            AnthropicProvider,
        )

        provider = create_ai_provider(
            AI_PROVIDER_ANTHROPIC, {"api_key": "sk-ant-test"}
        )
        assert isinstance(provider, AnthropicProvider)

    def test_factory_returns_ollama(self):
        """Factory should return OllamaProvider for 'ollama'."""
        from custom_components.smart_climate.ai.ollama_provider import OllamaProvider

        provider = create_ai_provider(AI_PROVIDER_OLLAMA, {})
        assert isinstance(provider, OllamaProvider)

    def test_factory_returns_gemini(self):
        """Factory should return GeminiProvider for 'gemini'."""
        from custom_components.smart_climate.ai.gemini_provider import GeminiProvider

        provider = create_ai_provider(AI_PROVIDER_GEMINI, {"api_key": "test"})
        assert isinstance(provider, GeminiProvider)

    def test_factory_returns_grok(self):
        """Factory should return GrokProvider for 'grok'."""
        from custom_components.smart_climate.ai.grok_provider import GrokProvider

        provider = create_ai_provider(AI_PROVIDER_GROK, {"api_key": "test"})
        assert isinstance(provider, GrokProvider)

    def test_factory_returns_noop_for_unknown(self):
        """Factory should fall back to NoOpProvider for unknown types."""
        provider = create_ai_provider("unknown_provider", {})
        assert isinstance(provider, NoOpProvider)

    def test_factory_returns_noop_for_empty_string(self):
        """Factory should fall back to NoOpProvider for empty string."""
        provider = create_ai_provider("", {})
        assert isinstance(provider, NoOpProvider)


# ---------------------------------------------------------------------------
# Provider configuration tests
# ---------------------------------------------------------------------------


class TestProviderConfiguration:
    """Tests for provider-specific configuration handling."""

    def test_openai_default_model(self):
        """OpenAIProvider should use gpt-4o-mini as default model."""
        from custom_components.smart_climate.ai.openai_provider import OpenAIProvider

        provider = OpenAIProvider({"api_key": "sk-test"})
        assert provider._model == "gpt-4o-mini"

    def test_openai_custom_model(self):
        """OpenAIProvider should accept a custom model."""
        from custom_components.smart_climate.ai.openai_provider import OpenAIProvider

        provider = OpenAIProvider({"api_key": "sk-test", "model": "gpt-4"})
        assert provider._model == "gpt-4"

    def test_openai_default_base_url(self):
        """OpenAIProvider should use the OpenAI API URL by default."""
        from custom_components.smart_climate.ai.openai_provider import OpenAIProvider

        provider = OpenAIProvider({"api_key": "sk-test"})
        assert "api.openai.com" in provider._base_url

    def test_openai_custom_base_url(self):
        """OpenAIProvider should accept a custom base URL."""
        from custom_components.smart_climate.ai.openai_provider import OpenAIProvider

        provider = OpenAIProvider(
            {"api_key": "sk-test", "base_url": "https://my-proxy.com/v1"}
        )
        assert "my-proxy.com" in provider._base_url

    def test_anthropic_default_model(self):
        """AnthropicProvider should use claude-sonnet as default."""
        from custom_components.smart_climate.ai.anthropic_provider import (
            AnthropicProvider,
        )

        provider = AnthropicProvider({"api_key": "sk-ant-test"})
        assert "claude" in provider._model

    def test_ollama_default_base_url(self):
        """OllamaProvider should default to localhost:11434."""
        from custom_components.smart_climate.ai.ollama_provider import OllamaProvider

        provider = OllamaProvider({})
        assert "localhost:11434" in provider._base_url

    def test_grok_default_base_url(self):
        """GrokProvider should default to the xAI API URL."""
        from custom_components.smart_climate.ai.grok_provider import GrokProvider

        provider = GrokProvider({"api_key": "test"})
        assert "api.x.ai" in provider._base_url

    def test_grok_default_model(self):
        """GrokProvider should default to grok-3-mini."""
        from custom_components.smart_climate.ai.grok_provider import GrokProvider

        provider = GrokProvider({"api_key": "test"})
        assert provider._model == "grok-3-mini"

    def test_gemini_default_model(self):
        """GeminiProvider should default to gemini-2.0-flash."""
        from custom_components.smart_climate.ai.gemini_provider import GeminiProvider

        provider = GeminiProvider({"api_key": "test"})
        assert provider._model == "gemini-2.0-flash"


# ---------------------------------------------------------------------------
# Exception hierarchy tests
# ---------------------------------------------------------------------------


class TestExceptions:
    """Tests for the AI exception hierarchy."""

    def test_ai_provider_error_is_exception(self):
        """AIProviderError should inherit from Exception."""
        assert issubclass(AIProviderError, Exception)

    def test_ai_connection_error_inherits(self):
        """AIConnectionError should inherit from AIProviderError."""
        assert issubclass(AIConnectionError, AIProviderError)

    def test_ai_response_error_inherits(self):
        """AIResponseError should inherit from AIProviderError."""
        assert issubclass(AIResponseError, AIProviderError)

    def test_exceptions_are_catchable(self):
        """All AI exceptions should be catchable as AIProviderError."""
        try:
            raise AIConnectionError("connection failed")
        except AIProviderError:
            pass

        try:
            raise AIResponseError("bad response")
        except AIProviderError:
            pass


# ---------------------------------------------------------------------------
# parse_ai_response tests
# ---------------------------------------------------------------------------


class TestParseAIResponse:
    """Tests for the AI response parsing function."""

    def test_valid_json_response(self):
        """Valid JSON with suggestions should parse correctly."""
        response = json.dumps(
            {
                "summary": "All rooms are comfortable.",
                "suggestions": [
                    {
                        "title": "Lower living room temp",
                        "description": "Reduce by 1 degree",
                        "reasoning": "Based on patterns",
                        "room": "living_room",
                        "action_type": "set_temperature",
                        "action_data": {"temperature": 71.0},
                        "confidence": 0.85,
                        "priority": "high",
                    }
                ],
            }
        )
        suggestions, summary = parse_ai_response(response)
        assert len(suggestions) == 1
        assert summary == "All rooms are comfortable."
        assert suggestions[0].title == "Lower living room temp"
        assert suggestions[0].action_type == "set_temperature"
        assert suggestions[0].confidence == 0.85
        assert suggestions[0].priority == SuggestionPriority.HIGH
        assert suggestions[0].status == SUGGESTION_PENDING

    def test_markdown_wrapped_json(self):
        """JSON wrapped in markdown code fences should parse correctly."""
        response = '```json\n{"summary": "Test summary", "suggestions": []}\n```'
        suggestions, summary = parse_ai_response(response)
        assert len(suggestions) == 0
        assert summary == "Test summary"

    def test_markdown_wrapped_without_language(self):
        """JSON in code fences without language tag should parse."""
        response = '```\n{"summary": "Test", "suggestions": []}\n```'
        suggestions, summary = parse_ai_response(response)
        assert summary == "Test"

    def test_invalid_json_returns_empty(self):
        """Invalid JSON should return empty suggestions and fallback summary."""
        suggestions, summary = parse_ai_response("this is not json")
        assert len(suggestions) == 0
        assert "could not be parsed" in summary.lower() or "parse" in summary.lower()

    def test_empty_string_returns_empty(self):
        """Empty string should return empty suggestions."""
        suggestions, summary = parse_ai_response("")
        assert len(suggestions) == 0

    def test_sanitizes_dangerous_action_types(self):
        """Suggestions with disallowed action types should be filtered out."""
        response = json.dumps(
            {
                "summary": "Test",
                "suggestions": [
                    {
                        "title": "Dangerous action",
                        "action_type": "execute_shell",
                        "confidence": 0.9,
                        "priority": "high",
                    }
                ],
            }
        )
        suggestions, summary = parse_ai_response(response)
        assert len(suggestions) == 0

    def test_allowed_action_types(self):
        """All allowed action types should pass through."""
        for action_type in ALLOWED_ACTION_TYPES:
            response = json.dumps(
                {
                    "summary": "Test",
                    "suggestions": [
                        {
                            "title": f"Test {action_type}",
                            "action_type": action_type,
                            "confidence": 0.5,
                            "priority": "medium",
                        }
                    ],
                }
            )
            suggestions, _ = parse_ai_response(response)
            assert len(suggestions) == 1
            assert suggestions[0].action_type == action_type

    def test_clamps_temperature_to_safe_range(self):
        """Temperatures should be clamped to MIN_SAFE_TEMP..MAX_SAFE_TEMP."""
        response = json.dumps(
            {
                "summary": "Test",
                "suggestions": [
                    {
                        "title": "Too hot",
                        "action_type": "set_temperature",
                        "action_data": {"temperature": 120.0},
                        "confidence": 0.5,
                        "priority": "medium",
                    },
                    {
                        "title": "Too cold",
                        "action_type": "set_temperature",
                        "action_data": {"temperature": 30.0},
                        "confidence": 0.5,
                        "priority": "medium",
                    },
                ],
            }
        )
        suggestions, _ = parse_ai_response(response)
        assert len(suggestions) == 2
        # Temperature clamped to max
        assert suggestions[0].action_data["temperature"] == MAX_SAFE_TEMP
        # Temperature clamped to min
        assert suggestions[1].action_data["temperature"] == MIN_SAFE_TEMP

    def test_clamps_confidence(self):
        """Confidence values should be clamped to 0.0-1.0."""
        response = json.dumps(
            {
                "summary": "Test",
                "suggestions": [
                    {
                        "title": "Over confident",
                        "action_type": "general",
                        "action_data": {"advice": "test"},
                        "confidence": 5.0,
                        "priority": "medium",
                    },
                    {
                        "title": "Negative confidence",
                        "action_type": "general",
                        "action_data": {"advice": "test"},
                        "confidence": -1.0,
                        "priority": "low",
                    },
                ],
            }
        )
        suggestions, _ = parse_ai_response(response)
        assert len(suggestions) == 2
        assert suggestions[0].confidence == 1.0
        assert suggestions[1].confidence == 0.0

    def test_invalid_priority_defaults_to_medium(self):
        """Invalid priority should default to medium."""
        response = json.dumps(
            {
                "summary": "Test",
                "suggestions": [
                    {
                        "title": "Bad priority",
                        "action_type": "general",
                        "action_data": {"advice": "test"},
                        "confidence": 0.5,
                        "priority": "super_high",
                    }
                ],
            }
        )
        suggestions, _ = parse_ai_response(response)
        assert len(suggestions) == 1
        assert suggestions[0].priority == SuggestionPriority.MEDIUM

    def test_max_10_suggestions(self):
        """Response should be truncated to at most 10 suggestions."""
        many_suggestions = [
            {
                "title": f"Suggestion {i}",
                "action_type": "general",
                "action_data": {"advice": f"advice {i}"},
                "confidence": 0.5,
                "priority": "medium",
            }
            for i in range(15)
        ]
        response = json.dumps(
            {"summary": "Test", "suggestions": many_suggestions}
        )
        suggestions, _ = parse_ai_response(response)
        assert len(suggestions) == 10

    def test_missing_summary_gives_fallback(self):
        """Missing summary field should give a fallback."""
        response = json.dumps({"suggestions": []})
        _, summary = parse_ai_response(response)
        assert summary == "No summary provided."

    def test_empty_suggestions_list(self):
        """Empty suggestions array should return empty list."""
        response = json.dumps({"summary": "All good", "suggestions": []})
        suggestions, summary = parse_ai_response(response)
        assert len(suggestions) == 0
        assert summary == "All good"

    def test_suggestion_gets_uuid(self):
        """Each parsed suggestion should get a unique UUID."""
        response = json.dumps(
            {
                "summary": "Test",
                "suggestions": [
                    {
                        "title": "Test 1",
                        "action_type": "general",
                        "action_data": {"advice": "test"},
                        "confidence": 0.5,
                        "priority": "medium",
                    },
                    {
                        "title": "Test 2",
                        "action_type": "general",
                        "action_data": {"advice": "test"},
                        "confidence": 0.5,
                        "priority": "low",
                    },
                ],
            }
        )
        suggestions, _ = parse_ai_response(response)
        assert len(suggestions) == 2
        assert suggestions[0].id != suggestions[1].id
        # IDs should look like UUIDs
        assert len(suggestions[0].id) == 36

    def test_non_dict_suggestion_skipped(self):
        """Non-dict items in suggestions list should be skipped."""
        response = json.dumps(
            {
                "summary": "Test",
                "suggestions": ["not a dict", 42, None],
            }
        )
        suggestions, _ = parse_ai_response(response)
        assert len(suggestions) == 0

    def test_non_list_suggestions_returns_empty(self):
        """Non-list suggestions field should return empty list."""
        response = json.dumps(
            {"summary": "Test", "suggestions": "not a list"}
        )
        suggestions, _ = parse_ai_response(response)
        assert len(suggestions) == 0

    def test_set_mode_sanitizes_unsafe_modes(self):
        """Unsafe HVAC modes should be filtered out from action_data."""
        response = json.dumps(
            {
                "summary": "Test",
                "suggestions": [
                    {
                        "title": "Set bad mode",
                        "action_type": "set_mode",
                        "action_data": {"mode": "destroy"},
                        "confidence": 0.5,
                        "priority": "medium",
                    }
                ],
            }
        )
        suggestions, _ = parse_ai_response(response)
        assert len(suggestions) == 1
        # The mode should be filtered out, leaving empty action_data
        assert "mode" not in suggestions[0].action_data

    def test_set_mode_allows_safe_modes(self):
        """Safe HVAC modes should pass through."""
        safe_modes = ["heat", "cool", "auto", "off", "fan_only", "heat_cool", "dry"]
        for mode in safe_modes:
            response = json.dumps(
                {
                    "summary": "Test",
                    "suggestions": [
                        {
                            "title": f"Set {mode}",
                            "action_type": "set_mode",
                            "action_data": {"mode": mode},
                            "confidence": 0.5,
                            "priority": "medium",
                        }
                    ],
                }
            )
            suggestions, _ = parse_ai_response(response)
            assert len(suggestions) == 1
            assert suggestions[0].action_data.get("mode") == mode

    def test_vent_adjustment_clamps_position(self):
        """Vent positions should be clamped to 0-100."""
        response = json.dumps(
            {
                "summary": "Test",
                "suggestions": [
                    {
                        "title": "Over vent",
                        "action_type": "vent_adjustment",
                        "action_data": {"vent_position": 150},
                        "confidence": 0.5,
                        "priority": "medium",
                    }
                ],
            }
        )
        suggestions, _ = parse_ai_response(response)
        assert suggestions[0].action_data["vent_position"] == 100


# ---------------------------------------------------------------------------
# Prompt builder tests
# ---------------------------------------------------------------------------


class TestPromptBuilders:
    """Tests for prompt building functions."""

    def test_system_prompt_non_empty(self):
        """build_system_prompt should return a non-empty string."""
        prompt = build_system_prompt()
        assert isinstance(prompt, str)
        assert len(prompt) > 100  # Should be a substantial prompt

    def test_system_prompt_contains_safety_constraints(self):
        """System prompt should mention safety constraints."""
        prompt = build_system_prompt()
        assert "safe" in prompt.lower() or "constraint" in prompt.lower()

    def test_system_prompt_mentions_json_output(self):
        """System prompt should specify JSON output format."""
        prompt = build_system_prompt()
        assert "json" in prompt.lower()

    def test_system_prompt_mentions_action_types(self):
        """System prompt should list the allowed action types."""
        prompt = build_system_prompt()
        assert "set_temperature" in prompt
        assert "set_mode" in prompt
        assert "vent_adjustment" in prompt

    def test_user_prompt_with_empty_data(self):
        """build_user_prompt with empty data should return minimal prompt."""
        prompt = build_user_prompt({})
        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_user_prompt_with_none_data(self):
        """build_user_prompt with None-like data should return minimal prompt."""
        prompt = build_user_prompt({})
        assert isinstance(prompt, str)

    def test_user_prompt_with_sample_data(self):
        """build_user_prompt with real coordinator data should include room info."""
        config = RoomConfig(
            name="Living Room",
            slug="living_room",
            climate_entity="climate.living_room",
        )
        room_state = RoomState(
            config=config,
            temperature=72.0,
            humidity=45.0,
            occupied=True,
            comfort_score=85.0,
            hvac_action=HVACAction.COOLING,
            current_target=72.0,
        )
        house_state = HouseState(
            comfort_score=85.0,
            efficiency_score=75.0,
            outdoor_temperature=82.0,
        )
        data = {"rooms": {"living_room": room_state}, "house": house_state}

        prompt = build_user_prompt(data)
        assert isinstance(prompt, str)
        assert len(prompt) > 50
        assert "Living Room" in prompt or "living_room" in prompt


# ---------------------------------------------------------------------------
# Suggestion lifecycle tests
# ---------------------------------------------------------------------------


class TestSuggestionLifecycle:
    """Tests for Suggestion model lifecycle methods."""

    def test_suggestion_creation(self):
        """Suggestion should be created with proper defaults."""
        suggestion = Suggestion(
            title="Test",
            action_type="general",
            confidence=0.7,
        )
        assert suggestion.status == SUGGESTION_PENDING
        assert suggestion.id is not None
        assert len(suggestion.id) == 36  # UUID length

    def test_suggestion_not_expired(self):
        """Suggestion should not be expired when within expiry window."""
        suggestion = Suggestion(
            expires_at=datetime.now() + timedelta(hours=24),
        )
        assert suggestion.is_expired() is False

    def test_suggestion_expired(self):
        """Suggestion should be expired when past expiry time."""
        suggestion = Suggestion(
            expires_at=datetime.now() - timedelta(hours=1),
        )
        assert suggestion.is_expired() is True

    def test_suggestion_to_dict(self, sample_suggestion):
        """Suggestion.to_dict should serialize all fields."""
        data = sample_suggestion.to_dict()
        assert data["id"] == "test-uuid-1234"
        assert data["title"] == "Lower nursery temperature"
        assert data["room"] == "nursery"
        assert data["action_type"] == "set_temperature"
        assert data["confidence"] == 0.85
        assert data["priority"] == SuggestionPriority.HIGH
        assert data["status"] == SUGGESTION_PENDING
        assert "created_at" in data
        assert "expires_at" in data

    def test_suggestion_to_dict_iso_dates(self, sample_suggestion):
        """Dates in to_dict should be ISO format strings."""
        data = sample_suggestion.to_dict()
        # Should be parseable back
        datetime.fromisoformat(data["created_at"])
        datetime.fromisoformat(data["expires_at"])

    def test_suggestion_to_dict_applied_at_none(self):
        """applied_at should be None in dict when not applied."""
        suggestion = Suggestion()
        data = suggestion.to_dict()
        assert data["applied_at"] is None

    def test_suggestion_to_dict_applied_at_set(self):
        """applied_at should be ISO string when set."""
        now = datetime.now()
        suggestion = Suggestion(applied_at=now)
        data = suggestion.to_dict()
        assert data["applied_at"] == now.isoformat()
