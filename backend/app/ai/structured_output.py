from __future__ import annotations

import json
import re
from typing import TypeVar, Type

from pydantic import BaseModel, ValidationError


T = TypeVar("T", bound=BaseModel)


class StructuredOutputError(ValueError):
    """Base exception for invalid model output."""


class ModelJSONError(StructuredOutputError):
    """The model did not return parseable JSON."""


class ModelSchemaError(StructuredOutputError):
    """The model JSON did not match the required schema."""


def _extract_json_text(raw_text: str) -> str:
    if not isinstance(raw_text, str) or not raw_text.strip():
        raise ModelJSONError("The model returned an empty response.")

    text = raw_text.strip()

    # Remove a surrounding Markdown code fence, if present.
    fenced = re.fullmatch(
        r"```(?:json)?\s*(.*?)\s*```",
        text,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if fenced:
        text = fenced.group(1).strip()

    # First try the entire response as JSON. If the model added introductory
    # prose, attempt to extract the outermost JSON object or array.
    try:
        json.loads(text)
        return text
    except json.JSONDecodeError:
        pass

    starts = [pos for pos in (text.find("{"), text.find("[")) if pos >= 0]
    if not starts:
        raise ModelJSONError("No JSON object or array was found in the response.")

    start = min(starts)
    opener = text[start]
    closer = "}" if opener == "{" else "]"
    depth = 0
    in_string = False
    escaped = False

    for index in range(start, len(text)):
        char = text[index]

        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == opener:
            depth += 1
        elif char == closer:
            depth -= 1
            if depth == 0:
                candidate = text[start : index + 1]
                try:
                    json.loads(candidate)
                    return candidate
                except json.JSONDecodeError as exc:
                    raise ModelJSONError(
                        "The extracted JSON structure is malformed."
                    ) from exc

    raise ModelJSONError("The JSON structure is incomplete.")


def parse_model_json(raw_text: str):
    """Parse the model response into native Python JSON data."""
    json_text = _extract_json_text(raw_text)
    try:
        return json.loads(json_text)
    except json.JSONDecodeError as exc:
        raise ModelJSONError("The model response is not valid JSON.") from exc


def validate_model_output(
    raw_text: str,
    schema: Type[T],
) -> T:
    """
    Parse and validate model output against a Pydantic v2 schema.

    Validation errors are converted into a controlled exception with useful
    detail for logs. Avoid returning raw model output to end users by default.
    """
    payload = parse_model_json(raw_text)

    try:
        return schema.model_validate(payload)
    except ValidationError as exc:
        raise ModelSchemaError(
            f"Model output failed {schema.__name__} validation: {exc}"
        ) from exc


def model_json_schema(schema: Type[BaseModel]) -> dict:
    """Return the JSON Schema that can be supplied to compatible LLM APIs."""
    return schema.model_json_schema()