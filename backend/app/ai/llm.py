from __future__ import annotations

import json
from typing import Any

import requests

from app.core.config import settings


class LLMError(RuntimeError):
    """Base exception for controlled LLM failures."""


class LLMConnectionError(LLMError):
    """Ollama could not be reached."""


class LLMTimeoutError(LLMError):
    """The LLM request exceeded its configured timeout."""


class LLMResponseError(LLMError):
    """Ollama returned an invalid or unsuccessful response."""


def _generate(
    prompt: str,
    *,
    json_mode: bool = False,
    schema: dict[str, Any] | None = None,
) -> str:
    if not prompt or not prompt.strip():
        raise ValueError("The LLM prompt must not be empty.")

    base_url = settings.ollama_base_url.rstrip("/")
    url = f"{base_url}/api/generate"

    options = {
        "temperature": settings.ollama_temperature,
        "num_ctx": settings.ollama_num_ctx,
        "num_predict": settings.ollama_num_predict,
    }

    payload: dict[str, Any] = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
        "options": options,
    }

    # Ollama's JSON output mode constrains the response format.
    if json_mode:
        payload["format"] = schema if schema else "json"

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=(
                settings.ollama_connect_timeout_seconds,
                settings.ollama_timeout_seconds,
            ),
        )
        response.raise_for_status()

    except requests.Timeout as exc:
        raise LLMTimeoutError(
            "Ollama did not respond within the configured timeout."
        ) from exc

    except requests.ConnectionError as exc:
        raise LLMConnectionError(
            "Could not connect to Ollama. Check that Ollama is running "
            "and the configured base URL is correct."
        ) from exc

    except requests.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        raise LLMResponseError(
            f"Ollama returned HTTP status {status}."
        ) from exc

    except requests.RequestException as exc:
        raise LLMResponseError(
            "The request to Ollama failed."
        ) from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise LLMResponseError(
            "Ollama returned a response that was not valid JSON."
        ) from exc

    if data.get("error"):
        raise LLMResponseError(
            f"Ollama reported an error: {data['error']}"
        )

    text = data.get("response")
    if not isinstance(text, str) or not text.strip():
        raise LLMResponseError(
            "Ollama returned an empty text response."
        )

    return text.strip()


def generate_text(prompt: str) -> str:
    """Generate ordinary text; preserves the existing public interface."""
    return _generate(prompt)


def generate_json(
    prompt: str,
    *,
    schema: dict[str, Any] | None = None,
) -> dict[str, Any] | list[Any]:
    """
    Ask Ollama for JSON and parse the response.

    Optional `schema` is an Ollama-supported JSON format schema. Application
    validation should still be performed separately with Pydantic.
    """
    raw_text = _generate(
        prompt,
        json_mode=True,
        schema=schema,
    )

    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise LLMResponseError(
            "The model response was not valid JSON."
        ) from exc

    if not isinstance(parsed, (dict, list)):
        raise LLMResponseError(
            "The model response must be a JSON object or array."
        )

    return parsed


def get_model_name() -> str:
    """Return a stable model identifier for analysis metadata."""
    return f"ollama:{settings.ollama_model}"
