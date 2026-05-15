from pathlib import Path
import argparse
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from noemakernel.gemma_api import DEFAULT_GEMMA_MODEL, GemmaApiClient, GemmaApiError


HELP = """Commands:
  /help              show commands
  /exit              quit
  /clear             clear local conversation history
  /history           show local conversation history
  /model NAME        switch model for next calls
  /temp VALUE        set temperature, example: /temp 0.4
  /tokens VALUE      set max output tokens, example: /tokens 2048
  /json on|off       request JSON response mime type
  /raw               next message is sent without local history
"""


def build_prompt(history: list[tuple[str, str]], user_text: str) -> str:
    if not history:
        return user_text
    turns = []
    for role, text in history:
        turns.append(f"{role.upper()}:\n{text}")
    turns.append(f"USER:\n{user_text}")
    return "\n\n".join(turns)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Interactive Gemma/Gemini terminal.")
    parser.add_argument("--model", default=None, help="Model id. Defaults to GEMMA_MODEL or gemma-4-31b-it.")
    parser.add_argument("--temperature", type=float, default=0.4)
    parser.add_argument("--max-output-tokens", type=int, default=None)
    parser.add_argument("--json", action="store_true", help="Request application/json responses.")
    parser.add_argument("--no-history", action="store_true", help="Do not include previous turns in prompts.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    client = GemmaApiClient.from_env()
    if args.model:
        client.model = args.model

    max_tokens = args.max_output_tokens or int(os.getenv("GEMMA_MAX_OUTPUT_TOKENS", "2048"))
    temperature = args.temperature
    json_mode = args.json
    use_history = not args.no_history
    raw_next = False
    history: list[tuple[str, str]] = []

    print("NoemaKernel Gemma terminal")
    print(f"model: {client.model or DEFAULT_GEMMA_MODEL}")
    print(f"temperature: {temperature}")
    print(f"max_output_tokens: {max_tokens}")
    print(f"json_mode: {'on' if json_mode else 'off'}")
    print("Type /help for commands, /exit to quit.")

    while True:
        try:
            user_text = input("\nyou> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye")
            return

        if not user_text:
            continue

        if user_text.startswith("/"):
            parts = user_text.split(maxsplit=1)
            command = parts[0].lower()
            value = parts[1].strip() if len(parts) > 1 else ""

            if command == "/exit":
                print("bye")
                return
            if command == "/help":
                print(HELP)
                continue
            if command == "/clear":
                history.clear()
                print("history cleared")
                continue
            if command == "/history":
                if not history:
                    print("history empty")
                for role, text in history:
                    print(f"\n{role}> {text}")
                continue
            if command == "/model":
                if not value:
                    print(f"model: {client.model or DEFAULT_GEMMA_MODEL}")
                    continue
                client.model = value
                print(f"model set to: {client.model}")
                continue
            if command == "/temp":
                try:
                    temperature = float(value)
                except ValueError:
                    print("usage: /temp 0.4")
                    continue
                print(f"temperature set to: {temperature}")
                continue
            if command == "/tokens":
                try:
                    max_tokens = int(value)
                except ValueError:
                    print("usage: /tokens 2048")
                    continue
                print(f"max_output_tokens set to: {max_tokens}")
                continue
            if command == "/json":
                if value.lower() not in {"on", "off"}:
                    print("usage: /json on|off")
                    continue
                json_mode = value.lower() == "on"
                print(f"json_mode: {'on' if json_mode else 'off'}")
                continue
            if command == "/raw":
                raw_next = True
                print("next message will be sent without history")
                continue

            print("unknown command. Type /help.")
            continue

        prompt = user_text if raw_next or not use_history else build_prompt(history, user_text)
        raw_next = False
        response_mime_type = "application/json" if json_mode else None

        try:
            print("gemma> ", end="", flush=True)
            answer = client.generate(
                prompt,
                temperature=temperature,
                max_output_tokens=max_tokens,
                response_mime_type=response_mime_type,
            )
        except GemmaApiError as exc:
            print(f"\nGemma API error: {exc}")
            continue

        print(answer)
        if use_history:
            history.append(("user", user_text))
            history.append(("gemma", answer))


if __name__ == "__main__":
    main()
