"""Optional Gemma/Gemini API client.

The client uses only Python stdlib so the prototype stays dependency-free. It targets the
Google Gemini API generateContent endpoint and keeps the model name configurable because
Gemma availability/model IDs can vary by account, region, and release channel.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
import socket
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from .config import load_local_config


DEFAULT_GEMMA_MODEL = "gemma-4-31b-it"
DEFAULT_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


class GemmaApiError(RuntimeError):
    """Raised when the Gemma/Gemini API request fails."""


@dataclass(slots=True)
class GemmaApiClient:
    """Small REST client for Gemma-compatible Gemini API calls."""

    api_key: str | None = None
    model: str | None = None
    endpoint_template: str = DEFAULT_ENDPOINT
    timeout: float = 60.0

    @classmethod
    def from_env(cls) -> "GemmaApiClient":
        load_local_config()
        return cls(
            api_key=os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"),
            model=os.getenv("GEMMA_MODEL") or DEFAULT_GEMMA_MODEL,
            timeout=float(os.getenv("GEMMA_TIMEOUT_SECONDS", "180")),
        )

    def generate(
        self,
        prompt: str,
        temperature: float = 0.2,
        max_output_tokens: int = 2048,
        response_mime_type: str | None = "application/json",
    ) -> str:
        response = self.generate_raw(
            prompt,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            response_mime_type=response_mime_type,
        )
        return extract_text(response)

    def generate_raw(
        self,
        prompt: str,
        temperature: float = 0.2,
        max_output_tokens: int = 2048,
        response_mime_type: str | None = "application/json",
    ) -> dict[str, Any]:
        if not self.api_key:
            raise GemmaApiError("Missing API key. Set GEMINI_API_KEY or GOOGLE_API_KEY.")
        model = self.model or DEFAULT_GEMMA_MODEL
        url = self.endpoint_template.format(model=urllib.parse.quote(model, safe=""))
        url = f"{url}?key={urllib.parse.quote(self.api_key)}"
        generation_config: dict[str, Any] = {
            "temperature": temperature,
            "maxOutputTokens": max_output_tokens,
        }
        if response_mime_type:
            generation_config["responseMimeType"] = response_mime_type

        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": generation_config,
        }
        request = urllib.request.Request(
            url=url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise GemmaApiError(f"Gemma API HTTP {exc.code}: {body}") from exc
        except urllib.error.URLError as exc:
            raise GemmaApiError(f"Gemma API connection error: {exc}") from exc
        except (TimeoutError, socket.timeout) as exc:
            raise GemmaApiError(f"Gemma API timeout after {self.timeout:.0f}s") from exc


def extract_text(response: dict[str, Any]) -> str:
    """Extract text from a generateContent response."""

    candidates = response.get("candidates") or []
    if not candidates:
        raise GemmaApiError("Gemma API returned no candidates.")
    parts = candidates[0].get("content", {}).get("parts", [])
    texts = [part.get("text", "") for part in parts if isinstance(part, dict)]
    text = "".join(texts).strip()
    if not text:
        raise GemmaApiError("Gemma API candidate had no text content.")
    return text
