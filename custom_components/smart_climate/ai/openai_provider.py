"""OpenAI-compatible AI provider using direct aiohttp (no SDK dependency)."""

from __future__ import annotations

import asyncio
import json
import logging

import aiohttp

from .provider import AIConnectionError, AIProviderBase, AIResponseError

_LOGGER = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://api.openai.com"
DEFAULT_MODEL = "gpt-4o-mini"
REQUEST_TIMEOUT = 120  # seconds
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = [2, 4, 8]


class OpenAIProvider(AIProviderBase):
    """AI provider that talks to OpenAI (or any OpenAI-compatible API)."""

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self._api_key: str = config.get("api_key", "")
        self._model: str = config.get("model", "") or DEFAULT_MODEL
        self._base_url: str = (config.get("base_url", "") or DEFAULT_BASE_URL).rstrip("/")

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    async def analyze(self, system_prompt: str, user_prompt: str) -> str:
        """Send prompts to the OpenAI chat completions endpoint.

        Retries up to MAX_RETRIES times with exponential back-off on
        transient failures (5xx, timeouts, connection errors).
        """
        url = f"{self._base_url}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.3,
            "response_format": {"type": "json_object"},
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
                        "OpenAI request failed (attempt %d/%d), retrying in %ds: %s",
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
            f"OpenAI request failed after {MAX_RETRIES} attempts: {last_error}"
        )

    async def test_connection(self) -> bool:
        """Test connectivity by listing available models."""
        url = f"{self._base_url}/v1/models"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        timeout = aiohttp.ClientTimeout(total=30)

        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 200:
                        return True
                    _LOGGER.warning(
                        "OpenAI connection test returned status %d", resp.status
                    )
                    return False
        except Exception:
            _LOGGER.exception("OpenAI connection test failed")
            return False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _make_request(
        self, url: str, headers: dict, payload: dict
    ) -> str:
        """Execute a single HTTP POST and return the assistant message content."""
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)

        try:
            async with aiohttp.ClientSession(timeout=timeout) as session, session.post(
                url, headers=headers, json=payload
            ) as resp:
                body = await resp.text()

                if resp.status >= 500:
                    raise AIConnectionError(
                        f"OpenAI server error {resp.status}: {body[:500]}"
                    )

                if resp.status != 200:
                    raise AIResponseError(
                        f"OpenAI request returned {resp.status}: {body[:500]}"
                    )

                try:
                    data = json.loads(body)
                except json.JSONDecodeError as err:
                    raise AIResponseError(
                        f"OpenAI returned invalid JSON: {err}"
                    ) from err

                try:
                    content = data["choices"][0]["message"]["content"]
                except (KeyError, IndexError, TypeError) as err:
                    raise AIResponseError(
                        f"Unexpected OpenAI response structure: {err}"
                    ) from err

                return content

        except aiohttp.ClientError as err:
            raise AIConnectionError(
                f"HTTP connection error talking to OpenAI: {err}"
            ) from err
        except asyncio.TimeoutError as err:
            raise AIConnectionError(
                f"OpenAI request timed out after {REQUEST_TIMEOUT}s"
            ) from err
