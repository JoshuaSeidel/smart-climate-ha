"""AI response parsing and validation for Smart Climate."""

from __future__ import annotations

import json
import logging
import re
import uuid
from datetime import datetime, timedelta
from typing import Any

from ..const import SUGGESTION_EXPIRY_HOURS, SUGGESTION_PENDING
from ..models import Suggestion, SuggestionPriority

_LOGGER = logging.getLogger(__name__)

# Action types that are allowed through the pipeline.  Anything else
# returned by the LLM will be silently filtered out.
ALLOWED_ACTION_TYPES = frozenset(
    {
        "set_temperature",
        "set_mode",
        "vent_adjustment",
        "schedule_change",
        "general",
    }
)

ALLOWED_PRIORITIES = frozenset({"low", "medium", "high", "critical"})

# HVAC modes that are considered safe to set via set_mode suggestions.
SAFE_HVAC_MODES = frozenset({"heat", "cool", "auto", "off", "fan_only", "heat_cool", "dry"})

# Temperature sanity bounds (Fahrenheit).
MIN_SAFE_TEMP = 55.0
MAX_SAFE_TEMP = 85.0


def parse_ai_response(response_text: str) -> tuple[list[Suggestion], str]:
    """Parse raw AI response text into structured suggestions.

    Args:
        response_text: The raw text returned by the AI provider.  May be
            plain JSON or wrapped in markdown code fences.

    Returns:
        A tuple of ``(suggestions_list, summary_text)``.  On parse failure
        an empty list and a fallback summary are returned so the pipeline
        never raises from bad AI output.
    """
    try:
        data = _extract_json(response_text)
    except (json.JSONDecodeError, ValueError) as err:
        _LOGGER.warning("Failed to parse AI response as JSON: %s", err)
        return [], "AI analysis could not be parsed."

    if not isinstance(data, dict):
        _LOGGER.warning("AI response root is not a JSON object")
        return [], "AI analysis returned an unexpected format."

    summary = _extract_summary(data)
    raw_suggestions = data.get("suggestions", [])

    if not isinstance(raw_suggestions, list):
        _LOGGER.warning("AI 'suggestions' field is not a list")
        return [], summary

    suggestions: list[Suggestion] = []
    for idx, raw in enumerate(raw_suggestions):
        try:
            suggestion = _parse_single_suggestion(raw)
            if suggestion is not None:
                suggestions.append(suggestion)
        except Exception:
            _LOGGER.warning(
                "Skipping invalid suggestion at index %d", idx, exc_info=True
            )

    # Enforce a maximum of 10 suggestions
    suggestions = suggestions[:10]

    _LOGGER.debug(
        "Parsed %d valid suggestions from AI response", len(suggestions)
    )
    return suggestions, summary


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _extract_json(text: str) -> Any:
    """Extract a JSON object from raw text.

    Handles responses that are:
    - Plain JSON
    - Wrapped in ```json ... ``` markdown fences
    - Wrapped in ``` ... ``` without a language tag
    """
    text = text.strip()

    # Try to extract from markdown code blocks first
    pattern = r"```(?:json)?\s*\n?(.*?)\n?\s*```"
    match = re.search(pattern, text, re.DOTALL)
    if match:
        text = match.group(1).strip()

    return json.loads(text)


def _extract_summary(data: dict) -> str:
    """Extract and validate the summary field."""
    summary = data.get("summary", "")
    if not isinstance(summary, str):
        summary = str(summary)
    return summary.strip() or "No summary provided."


def _parse_single_suggestion(raw: Any) -> Suggestion | None:
    """Parse and validate a single suggestion dict into a Suggestion model.

    Returns None if the suggestion fails validation (unknown action type,
    unsafe parameters, etc.).
    """
    if not isinstance(raw, dict):
        _LOGGER.debug("Suggestion is not a dict, skipping")
        return None

    # -- action_type validation
    action_type = str(raw.get("action_type", "")).strip()
    if action_type not in ALLOWED_ACTION_TYPES:
        _LOGGER.debug(
            "Filtering out suggestion with disallowed action_type '%s'",
            action_type,
        )
        return None

    # -- priority validation
    raw_priority = str(raw.get("priority", "medium")).strip().lower()
    if raw_priority not in ALLOWED_PRIORITIES:
        raw_priority = "medium"

    try:
        priority = SuggestionPriority(raw_priority)
    except ValueError:
        priority = SuggestionPriority.MEDIUM

    # -- confidence validation
    try:
        confidence = float(raw.get("confidence", 0.5))
    except (ValueError, TypeError):
        confidence = 0.5
    confidence = max(0.0, min(1.0, confidence))

    # -- action_data sanitization
    action_data = raw.get("action_data", {})
    if not isinstance(action_data, dict):
        action_data = {}

    action_data = _sanitize_action_data(action_type, action_data)

    # -- room field
    room = raw.get("room")
    if room is not None:
        room = str(room).strip() or None

    # -- text fields
    title = str(raw.get("title", "")).strip() or "Untitled suggestion"
    description = str(raw.get("description", "")).strip()
    reasoning = str(raw.get("reasoning", "")).strip()

    now = datetime.now()

    return Suggestion(
        id=str(uuid.uuid4()),
        title=title,
        description=description,
        reasoning=reasoning,
        room=room,
        action_type=action_type,
        action_data=action_data,
        confidence=confidence,
        priority=priority,
        status=SUGGESTION_PENDING,
        created_at=now,
        expires_at=now + timedelta(hours=SUGGESTION_EXPIRY_HOURS),
    )


def _sanitize_action_data(action_type: str, data: dict) -> dict:
    """Sanitize action_data based on the action_type.

    Ensures only known, safe keys are passed through and values are within
    acceptable ranges.
    """
    sanitized: dict[str, Any] = {}

    if action_type == "set_temperature":
        temp = data.get("temperature")
        if temp is not None:
            try:
                temp = float(temp)
                temp = max(MIN_SAFE_TEMP, min(MAX_SAFE_TEMP, temp))
                sanitized["temperature"] = round(temp, 1)
            except (ValueError, TypeError):
                pass

    elif action_type == "set_mode":
        mode = str(data.get("mode", "")).strip().lower()
        if mode in SAFE_HVAC_MODES:
            sanitized["mode"] = mode
        else:
            _LOGGER.debug("Filtering unsafe HVAC mode '%s'", mode)

    elif action_type == "vent_adjustment":
        position = data.get("vent_position")
        if position is not None:
            try:
                position = int(float(position))
                position = max(0, min(100, position))
                sanitized["vent_position"] = position
            except (ValueError, TypeError):
                pass

    elif action_type == "schedule_change":
        desc = data.get("description", "")
        if isinstance(desc, str) and desc.strip():
            sanitized["description"] = desc.strip()

    elif action_type == "general":
        advice = data.get("advice", "")
        if isinstance(advice, str) and advice.strip():
            sanitized["advice"] = advice.strip()

    return sanitized
