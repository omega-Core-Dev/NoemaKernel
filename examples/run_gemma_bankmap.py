from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from noemakernel import BankmapEngine, ContextItem
from noemakernel.gemma_api import GemmaApiClient, GemmaApiError
from noemakernel.prompts import build_bankmap_prompt
from noemakernel.validation import parse_json_output, validate_multiflow_output


def load_contexts(path: Path) -> tuple[str, list[ContextItem]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["objective"], [
        ContextItem(context_id=item["context_id"], content=item["content"])
        for item in data["contexts"]
    ]


def main() -> None:
    source = ROOT / "data" / "sample_contexts.json"
    output_dir = ROOT / "artifacts" / "gemma"
    output_dir.mkdir(parents=True, exist_ok=True)

    objective, contexts = load_contexts(source)
    packet = BankmapEngine().build_packet(contexts, objective)
    prompt = build_bankmap_prompt(packet)

    client = GemmaApiClient.from_env()
    try:
        import os

        max_tokens = int(os.getenv("GEMMA_MAX_OUTPUT_TOKENS", "2048"))
        response_text = client.generate(prompt, max_output_tokens=max_tokens)
    except GemmaApiError as exc:
        print(f"Gemma API error: {exc}")
        print("Configure GEMINI_API_KEY or GOOGLE_API_KEY and, if needed, GEMMA_MODEL.")
        raise SystemExit(1)

    (output_dir / "bankmap_prompt.md").write_text(prompt, encoding="utf-8")
    (output_dir / "gemma_response.json").write_text(response_text, encoding="utf-8")
    parsed, errors = parse_json_output(response_text)
    validation = {"parse_errors": errors}
    if parsed is not None:
        validation.update(validate_multiflow_output(parsed))
    (output_dir / "validation.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Wrote Gemma artifacts to: {output_dir}")
    print(validation)


if __name__ == "__main__":
    main()
