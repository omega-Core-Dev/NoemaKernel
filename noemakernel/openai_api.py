"""Optional OpenAI Responses API client."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
import socket
import urllib.error
import urllib.request
from typing import Any

from .config import load_local_config


DEFAULT_OPENAI_MODEL = "gpt-5.4-mini"
DEFAULT_OPENAI_ENDPOINT = "https://api.openai.com/v1/responses"


class OpenAIApiError(RuntimeError):
    """Raised when the OpenAI API request fails."""


@dataclass(slots=True)
class OpenAIResponsesClient:
    """Small REST client for OpenAI Responses API calls."""

    api_key: str | None = None
    model: str | None = None
    endpoint: str = DEFAULT_OPENAI_ENDPOINT
    timeout: float = 180.0

    @classmethod
    def from_env(cls) -> "OpenAIResponsesClient":
        load_local_config()
        return cls(
            api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv("OPENAI_MODEL") or DEFAULT_OPENAI_MODEL,
            timeout=float(os.getenv("OPENAI_TIMEOUT_SECONDS", "180")),
        )

    def generate(self, prompt: str, max_output_tokens: int = 2048) -> str:
        response = self.generate_raw(prompt, max_output_tokens=max_output_tokens)
        return extract_response_text(response)

    def generate_raw(self, prompt: str, max_output_tokens: int = 2048) -> dict[str, Any]:
        if not self.api_key:
            raise OpenAIApiError("Missing API key. Set OPENAI_API_KEY.")
        payload = {
            "model": self.model or DEFAULT_OPENAI_MODEL,
            "input": prompt,
            "max_output_tokens": max_output_tokens,
            "text": {
                "format": {"type": "json_object"},
            },
        }
        request = urllib.request.Request(
            url=self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise OpenAIApiError(f"OpenAI API HTTP {exc.code}: {body}") from exc
        except urllib.error.URLError as exc:
            raise OpenAIApiError(f"OpenAI API connection error: {exc}") from exc
        except (TimeoutError, socket.timeout) as exc:
            raise OpenAIApiError(f"OpenAI API timeout after {self.timeout:.0f}s") from exc


def extract_response_text(response: dict[str, Any]) -> str:
    """Extract text from an OpenAI Responses API response."""

    if isinstance(response.get("output_text"), str):
        return response["output_text"].strip()

    chunks: list[str] = []
    for item in response.get("output", []):
        for content in item.get("content", []):
            text = content.get("text")
            if isinstance(text, str):
                chunks.append(text)
    text = "".join(chunks).strip()
    if not text:
        raise OpenAIApiError("OpenAI API response had no text content.")
    return text
