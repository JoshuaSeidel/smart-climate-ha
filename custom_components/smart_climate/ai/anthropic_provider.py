"""Anthropic Claude AI provider using direct aiohttp (no SDK dependency)."""

from __future__ import annotations

import asyncio
import json
import logging

import aiohttp

from .provider import AIConnectionError, AIProviderBase, AIResponseError

_LOGGER = logging.getLogger(__name__)

DEFAULT_API_URL = "https://api.anthropic.com"
DEFAULT_MODEL = "claude-sonnet-4-20250514"
ANTHROPIC_VERSION = "2023-06-01"
REQUEST_TIMEOUT = 120  # seconds
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = [2, 4, 8]


class AnthropicProvider(AIProviderBase):
    """AI provider that talks to the Anthropic Messages API."""

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self._api_key: str = config.get("api_key", "")
        self._model: str = config.get("model", "") or DEFAULT_MODEL
        self._base_url: str = (config.get("base_url", "") or DEFAULT_API_URL).rstrip("/")

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    async def analyze(self, system_prompt: str, user_prompt: str) -> str:
        """Send prompts to the Anthropic messages endpoint.

        Retries up to MAX_RETRIES times with exponential back-off on
        transient failures (5xx, timeouts, connection errors).
        """
        url = f"{self._base_url}/v1/messages"
        headers = {
            "x-api-key": self._api_key,
            "anthropic-version": ANTHROPIC_VERSION,
            "Content-Type": "application/json",
        }
        payload = {
            "model": self._model,
            "max_tokens": 4096,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": user_prompt},
            ],
        }

        last_error: Exception | None = None

        for attempt in range(MAX_RETRIES):
            try:
                return await self._make_request(url, headers, payload)
            except AIConnectionError as err:
                last_error = err
                if attempt < MAX_RETRIES - 1:
                    wait = RETRY_BACKOFF_SECONDS[attempt]
                    _LOGGER.warning(
                        "Anthropic request failed (attempt %d/%d), retrying in %ds: %s",
                        attempt + 1,
                        MAX_RETRIES,
                        wait,
                        err,
                    )
                    await asyncio.sleep(wait)
            except AIResponseError:
                # Non-retryable response error -- propagate immediately
                raise

        raise AIConnectionError(
            f"Anthropic request failed after {MAX_RETRIES} attempts: {last_error}"
        )

    async def test_connection(self) -> bool:
        """Test connectivity by sending a minimal message request."""
        url = f"{self._base_url}/v1/messages"
        headers = {
            "x-api-key": self._api_key,
            "anthropic-version": ANTHROPIC_VERSION,
            "Content-Type": "application/json",
        }
        payload = {
            "model": self._model,
            "max_tokens": 10,
            "messages": [
                {"role": "user", "content": "Hi"},
            ],
        }
        timeout = aiohttp.ClientTimeout(total=30)

        try:
            async with aiohttp.ClientSession(timeout=timeout) as session, session.post(
                url, headers=headers, json=payload
            ) as resp:
                if resp.status == 200:
                    return True
                _LOGGER.warning(
                    "Anthropic connection test returned status %d",
                    resp.status,
                )
                return False
        except Exception:
            _LOGGER.exception("Anthropic connection test failed")
            return False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _make_request(
        self, url: str, headers: dict, payload: dict
    ) -> str:
        """Execute a single HTTP POST and return the assistant text content."""
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)

        try:
            async with aiohttp.ClientSession(timeout=timeout) as session, session.post(
                url, headers=headers, json=payload
            ) as resp:
                body = await resp.text()

                if resp.status >= 500:
                    raise AIConnectionError(
                        f"Anthropic server error {resp.status}: {body[:500]}"
                    )

                if resp.status != 200:
                    raise AIResponseError(
                        f"Anthropic request returned {resp.status}: {body[:500]}"
                    )

                try:
                    data = json.loads(body)
                except json.JSONDecodeError as err:
                    raise AIResponseError(
                        f"Anthropic returned invalid JSON: {err}"
                    ) from err

                try:
                    content = data["content"][0]["text"]
                except (KeyError, IndexError, TypeError) as err:
                    raise AIResponseError(
                        f"Unexpected Anthropic response structure: {err}"
                    ) from err

                return content

        except aiohttp.ClientError as err:
            raise AIConnectionError(
                f"HTTP connection error talking to Anthropic: {err}"
            ) from err
        except asyncio.TimeoutError as err:
            raise AIConnectionError(
                f"Anthropic request timed out after {REQUEST_TIMEOUT}s"
            ) from err
