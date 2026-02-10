"""Ollama local AI provider using direct aiohttp."""

from __future__ import annotations

import asyncio
import json
import logging

import aiohttp

from .provider import AIConnectionError, AIProviderBase, AIResponseError

_LOGGER = logging.getLogger(__name__)

DEFAULT_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3.1"
REQUEST_TIMEOUT = 120  # seconds
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = [2, 4, 8]


class OllamaProvider(AIProviderBase):
    """AI provider that talks to a local Ollama instance."""

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self._model: str = config.get("model", "") or DEFAULT_MODEL
        self._base_url: str = (config.get("base_url", "") or DEFAULT_BASE_URL).rstrip("/")

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    async def analyze(self, system_prompt: str, user_prompt: str) -> str:
        """Send prompts to the Ollama chat endpoint.

        Retries up to MAX_RETRIES times with exponential back-off on
        transient failures (connection errors, timeouts).
        """
        url = f"{self._base_url}/api/chat"
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "format": "json",
        }

        last_error: Exception | None = None

        for attempt in range(MAX_RETRIES):
            try:
                return await self._make_request(url, payload)
            except AIConnectionError as err:
                last_error = err
                if attempt < MAX_RETRIES - 1:
                    wait = RETRY_BACKOFF_SECONDS[attempt]
                    _LOGGER.warning(
                        "Ollama request failed (attempt %d/%d), retrying in %ds: %s",
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
            f"Ollama request failed after {MAX_RETRIES} attempts: {last_error}"
        )

    async def test_connection(self) -> bool:
        """Test connectivity by requesting the list of available models."""
        url = f"{self._base_url}/api/tags"
        timeout = aiohttp.ClientTimeout(total=15)

        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        return True
                    _LOGGER.warning(
                        "Ollama connection test returned status %d", resp.status
                    )
                    return False
        except Exception:
            _LOGGER.exception("Ollama connection test failed")
            return False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _make_request(self, url: str, payload: dict) -> str:
        """Execute a single HTTP POST and return the assistant message content."""
        timeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)
        headers = {"Content-Type": "application/json"}

        try:
            async with aiohttp.ClientSession(timeout=timeout) as session, session.post(
                url, headers=headers, json=payload
            ) as resp:
                body = await resp.text()

                if resp.status >= 500:
                    raise AIConnectionError(
                        f"Ollama server error {resp.status}: {body[:500]}"
                    )

                if resp.status != 200:
                    raise AIResponseError(
                        f"Ollama request returned {resp.status}: {body[:500]}"
                    )

                try:
                    data = json.loads(body)
                except json.JSONDecodeError as err:
                    raise AIResponseError(
                        f"Ollama returned invalid JSON: {err}"
                    ) from err

                try:
                    content = data["message"]["content"]
                except (KeyError, TypeError) as err:
                    raise AIResponseError(
                        f"Unexpected Ollama response structure: {err}"
                    ) from err

                return content

        except aiohttp.ClientError as err:
            raise AIConnectionError(
                f"HTTP connection error talking to Ollama: {err}"
            ) from err
        except asyncio.TimeoutError as err:
            raise AIConnectionError(
                f"Ollama request timed out after {REQUEST_TIMEOUT}s"
            ) from err
