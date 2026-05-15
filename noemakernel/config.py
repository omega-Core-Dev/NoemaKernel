"""Local configuration helpers."""

from __future__ import annotations

from pathlib import Path
import importlib.util
import os


def load_dotenv(path: str | Path = ".env") -> None:
    """Load simple KEY=VALUE pairs into os.environ if they are not already set."""

    env_path = Path(path)
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def load_local_python_settings(path: str | Path = "local_api_key.py") -> None:
    """Load local Python settings into os.environ if present.

    This supports a local-only file for users who prefer terminal editing over env vars.
    """

    settings_path = Path(path)
    if not settings_path.exists():
        return

    spec = importlib.util.spec_from_file_location("_noemakernel_local_api_key", settings_path)
    if spec is None or spec.loader is None:
        return

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    mappings = {
        "GEMINI_API_KEY": getattr(module, "GEMINI_API_KEY", None),
        "GOOGLE_API_KEY": getattr(module, "GOOGLE_API_KEY", None),
        "GEMMA_MODEL": getattr(module, "GEMMA_MODEL", None),
        "GEMMA_MAX_OUTPUT_TOKENS": getattr(module, "GEMMA_MAX_OUTPUT_TOKENS", None),
        "GEMMA_TIMEOUT_SECONDS": getattr(module, "GEMMA_TIMEOUT_SECONDS", None),
        "OPENAI_API_KEY": getattr(module, "OPENAI_API_KEY", None),
        "OPENAI_MODEL": getattr(module, "OPENAI_MODEL", None),
        "OPENAI_MAX_OUTPUT_TOKENS": getattr(module, "OPENAI_MAX_OUTPUT_TOKENS", None),
        "OPENAI_TIMEOUT_SECONDS": getattr(module, "OPENAI_TIMEOUT_SECONDS", None),
    }
    for key, value in mappings.items():
        if value is not None and key not in os.environ:
            os.environ[key] = str(value)


def load_local_config() -> None:
    """Load local config from Python settings first, then .env."""

    load_local_python_settings()
    load_dotenv()
