"""Google Gemini AI provider using direct aiohttp (no SDK dependency)."""

from __future__ import annotations

import asyncio
import json
import logging

import aiohttp

from .provider import AIConnectionError, AIProviderBase, AIResponseError

_LOGGER = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://generativelanguage.googleapis.com"
DEFAULT_MODEL = "gemini-2.0-flash"
REQUEST_TIMEOUT = 120  # seconds
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = [2, 4, 8]


class GeminiProvider(AIProviderBase):
    """AI provider that talks to the Google Gemini (Generative Language) API."""

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self._api_key: str = config.get("api_key", "")
        self._model: str = config.get("model", "") or DEFAULT_MODEL
        self._base_url: str = (config.get("base_url", "") or DEFAULT_BASE_URL).rstrip("/")

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    async def analyze(self, system_prompt: str, user_prompt: str) -> str:
        """Send prompts to the Gemini generateContent endpoint.

        Retries up to MAX_RETRIES times with exponential back-off on
        transient failures (5xx, timeouts, connection errors).
        """
        url = (
            f"{self._base_url}/v1beta/models/{self._model}:generateContent"
            f"?key={self._api_key}"
        )
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{system_prompt}\n\n{user_prompt}"},
                    ],
                },
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.3,
            },
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
                        "Gemini request failed (attempt %d/%d), retrying in %ds: %s",
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
            f"Gemini request failed after {MAX_RETRIES} attempts: {last_error}"
        )

    async def test_connection(self) -> bool:
        """Test connectivity by listing available models."""
        url = f"{self._base_url}/v1beta/models?key={self._api_key}"
        timeout = aiohttp.ClientTimeout(total=30)

        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        return True
                    _LOGGER.warning(
                        "Gemini connection test returned status %d", resp.status
                    )
                    return False
        except Exception:
            _LOGGER.exception("Gemini connection test failed")
            return False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _make_request(
        self, url: str, headers: dict, payload: dict
    ) -> str:
        """Execute a single HTTP POST and return the generated text content."""
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)

        try:
            async with aiohttp.ClientSession(timeout=timeout) as session, session.post(
                url, headers=headers, json=payload
            ) as resp:
                body = await resp.text()

                if resp.status >= 500:
                    raise AIConnectionError(
                        f"Gemini server error {resp.status}: {body[:500]}"
                    )

                if resp.status != 200:
                    raise AIResponseError(
                        f"Gemini request returned {resp.status}: {body[:500]}"
                    )

                try:
                    data = json.loads(body)
                except json.JSONDecodeError as err:
                    raise AIResponseError(
                        f"Gemini returned invalid JSON: {err}"
                    ) from err

                try:
                    content = data["candidates"][0]["content"]["parts"][0]["text"]
                except (KeyError, IndexError, TypeError) as err:
                    raise AIResponseError(
                        f"Unexpected Gemini response structure: {err}"
                    ) from err

                return content

        except aiohttp.ClientError as err:
            raise AIConnectionError(
                f"HTTP connection error talking to Gemini: {err}"
            ) from err
        except asyncio.TimeoutError as err:
            raise AIConnectionError(
                f"Gemini request timed out after {REQUEST_TIMEOUT}s"
            ) from err
