"""LLM client wrapper for OpenRouter chat completions."""

import os
import logging
from typing import Optional

import httpx


logger = logging.getLogger(__name__)


class LLMClient:
    """Asynchronous OpenRouter LLM client."""

    OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "mistralai/mistral-7b-instruct",
        timeout_seconds: float = 30.0,
    ):
        """Initialize LLMClient.

        Args:
            api_key: API key for OpenRouter. Falls back to OPENROUTER_API_KEY env var.
            model: Model name to use.
            timeout_seconds: Request timeout in seconds.
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is required")

        self.model = model
        self.timeout = timeout_seconds

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate text completion from OpenRouter.

        Args:
            system_prompt: System-level instruction for the model.
            user_prompt: User message to generate content from.

        Returns:
            str: Generated response text.

        Raises:
            RuntimeError: When the API response indicates an error or invalid data.
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": 300,
            "temperature": 0.7,
        }

        logger.debug("OpenRouter request payload: %s", payload)

        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(self.timeout)) as client:
                response = await client.post(
                    self.OPENROUTER_URL,
                    json=payload,
                    headers=headers,
                )

            response.raise_for_status()
            data = response.json()
            logger.debug("OpenRouter response: %s", data)

            choices = data.get("choices")
            if not choices or not isinstance(choices, list):
                raise RuntimeError("OpenRouter response does not contain choices")

            first_choice = choices[0]
            message = first_choice.get("message")
            if message is None:
                raise RuntimeError("OpenRouter response choice missing message")

            text = message.get("content")
            if not isinstance(text, str):
                raise RuntimeError("OpenRouter response does not contain content text")

            return text.strip()

        except httpx.TimeoutException as exc:
            logger.error("OpenRouter request timed out: %s", exc)
            raise RuntimeError("OpenRouter request timed out") from exc
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            body = exc.response.text
            logger.error("OpenRouter HTTP error %s: %s", status, body)
            raise RuntimeError(f"OpenRouter HTTP error {status}") from exc
        except httpx.RequestError as exc:
            logger.error("OpenRouter request error: %s", exc)
            raise RuntimeError("OpenRouter network request failed") from exc
        except ValueError as exc:
            logger.error("OpenRouter response parse error: %s", exc)
            raise RuntimeError("Failed to parse OpenRouter response") from exc

