"""Validation helpers for multi-flow LLM outputs."""

from __future__ import annotations

import json
from typing import Any


REQUIRED_OUTPUT_KEYS = {
    "user_response",
    "memory_updates",
    "activated_noemas",
    "axiom_checks",
    "audit_trail",
    "quality_checks",
    "next_actions",
    "metrics",
}


def parse_json_output(text: str) -> tuple[dict[str, Any] | None, list[str]]:
    """Parse a model output that should be JSON."""

    cleaned = strip_code_fence(text.strip())
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        parsed = find_embedded_json_object(cleaned)
        if parsed is None:
            return None, [f"invalid_json: {exc}"]
    if not isinstance(parsed, dict):
        return None, ["json_root_must_be_object"]
    return parsed, []


def strip_code_fence(text: str) -> str:
    """Strip a surrounding Markdown code fence when present."""

    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.strip("`")
        if stripped.lower().startswith("json"):
            stripped = stripped[4:].strip()
    return stripped


def find_embedded_json_object(text: str) -> dict[str, Any] | None:
    """Find a JSON object embedded in mixed model output."""

    decoder = json.JSONDecoder()
    best: dict[str, Any] | None = None
    best_score = -1
    for index, char in enumerate(text):
        if char != "{":
            continue
        try:
            parsed, _ = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            continue
        if not isinstance(parsed, dict):
            continue
        score = len(REQUIRED_OUTPUT_KEYS & set(parsed))
        if score > best_score:
            best = parsed
            best_score = score
        if score == len(REQUIRED_OUTPUT_KEYS):
            return parsed
    return best


def validate_multiflow_output(output: dict[str, Any]) -> dict[str, Any]:
    """Validate expected multi-flow fields and compute separability."""

    keys = set(output)
    missing = sorted(REQUIRED_OUTPUT_KEYS - keys)
    extra = sorted(keys - REQUIRED_OUTPUT_KEYS)
    valid = len(REQUIRED_OUTPUT_KEYS) - len(missing)
    separability = valid / len(REQUIRED_OUTPUT_KEYS)

    type_errors: list[str] = []
    if "user_response" in output and not isinstance(output["user_response"], str):
        type_errors.append("user_response_must_be_string")
    for key in REQUIRED_OUTPUT_KEYS - {"user_response", "metrics"}:
        if key in output and not isinstance(output[key], list):
            type_errors.append(f"{key}_must_be_list")
    if "metrics" in output and not isinstance(output["metrics"], dict):
        type_errors.append("metrics_must_be_object")

    return {
        "missing": missing,
        "extra": extra,
        "type_errors": type_errors,
        "separability_output": separability,
        "is_valid": not missing and not type_errors,
    }
