from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from noemakernel.config import load_local_config


def masked(value: str | None) -> str:
    if not value:
        return "missing"
    if len(value) <= 8:
        return "present"
    return f"{value[:4]}...{value[-4:]}"


def main() -> None:
    load_local_config()
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    model = os.getenv("GEMMA_MODEL")
    max_tokens = os.getenv("GEMMA_MAX_OUTPUT_TOKENS")
    timeout = os.getenv("GEMMA_TIMEOUT_SECONDS")
    openai_key = os.getenv("OPENAI_API_KEY")
    openai_model = os.getenv("OPENAI_MODEL")
    openai_timeout = os.getenv("OPENAI_TIMEOUT_SECONDS")

    print(f"cwd: {Path.cwd()}")
    print(f"local_api_key.py exists: {(ROOT / 'local_api_key.py').exists()}")
    print(f".env exists: {(ROOT / '.env').exists()}")
    print(f"api key: {masked(key)}")
    print(f"model: {model or 'missing'}")
    print(f"max_output_tokens: {max_tokens or 'missing'}")
    print(f"timeout_seconds: {timeout or 'missing'}")
    print(f"openai api key: {masked(openai_key)}")
    print(f"openai model: {openai_model or 'missing'}")
    print(f"openai timeout_seconds: {openai_timeout or 'missing'}")

    if not key and not openai_key:
        raise SystemExit("Config error: no provider API key loaded.")


if __name__ == "__main__":
    main()
