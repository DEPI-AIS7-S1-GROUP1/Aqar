"""LLM wrapper for Gemini and Groq using OpenAI-compatible endpoints.

Return shape of chat():
{
    "content": str | None,
    "tool_calls": [{"name": str, "arguments": dict}],
    "provider": str,
    "model": str,
    "duration_s": float,
}
"""

import json
import logging
import os
import time
from typing import Any

import openai
from openai import OpenAI

logger = logging.getLogger(__name__)

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

DEFAULT_GEMINI_MODEL = "gemini-2.0-flash"
DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"


class LLMError(Exception):
    """Base exception for LLM wrapper failures."""


class LLMRateLimitError(LLMError):
    """Raised immediately when the provider returns HTTP 429 rate limit."""


def _get_provider_config() -> tuple[str, str, str, str]:
    """Retrieve and validate provider configuration from environment variables.

    Returns:
        tuple of (provider, api_key, base_url, model)
    """
    provider = os.getenv("LLM_PROVIDER")
    if provider not in ("gemini", "groq"):
        raise LLMError(
            f"Unsupported or missing LLM_PROVIDER: {provider!r}. Must be 'gemini' or 'groq'."
        )

    if provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise LLMError("GEMINI_API_KEY environment variable is not set.")
        base_url = GEMINI_BASE_URL
        model = os.getenv("GEMINI_MODEL") or DEFAULT_GEMINI_MODEL
    else:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise LLMError("GROQ_API_KEY environment variable is not set.")
        base_url = GROQ_BASE_URL
        model = os.getenv("GROQ_MODEL") or DEFAULT_GROQ_MODEL

    return provider, api_key, base_url, model


def chat(
    messages: list[dict[str, Any]],
    tools: list[dict[str, Any]] | None = None,
    response_format: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Send a chat completion request to the active LLM provider.

    Args:
        messages: List of chat messages in OpenAI format.
        tools: Optional list of tool definitions.
        response_format: Optional response format (e.g. {"type": "json_object"}).

    Returns:
        Dict conforming to the documented return shape.
    """
    provider, api_key, base_url, model = _get_provider_config()

    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
        timeout=20.0,
        max_retries=0,
    )

    kwargs: dict[str, Any] = {
        "model": model,
        "messages": messages,
    }
    if tools is not None:
        kwargs["tools"] = tools
    if response_format is not None:
        kwargs["response_format"] = response_format

    retry_delays = [1.0, 2.0]
    max_attempts = len(retry_delays) + 1
    last_err: Exception | None = None

    start_time = time.perf_counter()

    for attempt in range(max_attempts):
        attempt_start = time.perf_counter()
        try:
            response = client.chat.completions.create(**kwargs)
            duration_s = round(time.perf_counter() - start_time, 4)
            logger.info(
                "provider=%s model=%s duration_s=%.3f status=success",
                provider,
                model,
                duration_s,
            )

            choice = response.choices[0]
            raw_tool_calls = choice.message.tool_calls or []
            parsed_tool_calls = []

            for tc in raw_tool_calls:
                arguments_raw = tc.function.arguments
                if isinstance(arguments_raw, str):
                    try:
                        arguments_dict = json.loads(arguments_raw)
                    except json.JSONDecodeError as err:
                        raise LLMError(
                            f"Failed to parse tool call arguments as JSON: {err}"
                        ) from err
                elif isinstance(arguments_raw, dict):
                    arguments_dict = arguments_raw
                else:
                    arguments_dict = {}

                parsed_tool_calls.append(
                    {
                        "name": tc.function.name,
                        "arguments": arguments_dict,
                    }
                )

            return {
                "content": choice.message.content,
                "tool_calls": parsed_tool_calls,
                "provider": provider,
                "model": model,
                "duration_s": duration_s,
            }

        except openai.RateLimitError as err:
            duration_s = round(time.perf_counter() - start_time, 4)
            logger.error(
                "provider=%s model=%s duration_s=%.3f status=rate_limit",
                provider,
                model,
                duration_s,
            )
            raise LLMRateLimitError(str(err)) from err

        except openai.APIStatusError as err:
            if err.status_code == 429:
                duration_s = round(time.perf_counter() - start_time, 4)
                logger.error(
                    "provider=%s model=%s duration_s=%.3f status=rate_limit",
                    provider,
                    model,
                    duration_s,
                )
                raise LLMRateLimitError(str(err)) from err

            # Retry on 5xx errors
            if err.status_code and err.status_code >= 500:
                last_err = err
                if attempt < len(retry_delays):
                    delay = retry_delays[attempt]
                    duration_s = round(time.perf_counter() - attempt_start, 4)
                    logger.warning(
                        "provider=%s model=%s duration_s=%.3f status=retry_%d",
                        provider,
                        model,
                        duration_s,
                        attempt + 1,
                    )
                    time.sleep(delay)
                    continue
            # Non-retryable API status error (e.g. 400, 401)
            duration_s = round(time.perf_counter() - start_time, 4)
            logger.error(
                "provider=%s model=%s duration_s=%.3f status=error",
                provider,
                model,
                duration_s,
            )
            raise LLMError(str(err)) from err

        except (openai.APITimeoutError, openai.APIConnectionError) as err:
            last_err = err
            if attempt < len(retry_delays):
                delay = retry_delays[attempt]
                duration_s = round(time.perf_counter() - attempt_start, 4)
                logger.warning(
                    "provider=%s model=%s duration_s=%.3f status=retry_%d",
                    provider,
                    model,
                    duration_s,
                    attempt + 1,
                )
                time.sleep(delay)
                continue

        except Exception as err:
            duration_s = round(time.perf_counter() - start_time, 4)
            logger.error(
                "provider=%s model=%s duration_s=%.3f status=error",
                provider,
                model,
                duration_s,
            )
            raise LLMError(str(err)) from err

    duration_s = round(time.perf_counter() - start_time, 4)
    logger.error(
        "provider=%s model=%s duration_s=%.3f status=error",
        provider,
        model,
        duration_s,
    )
    raise LLMError(f"Request failed after retries: {last_err}") from last_err
