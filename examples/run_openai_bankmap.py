from pathlib import Path
import json
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from noemakernel import BankmapEngine, ContextItem
from noemakernel.openai_api import OpenAIApiError, OpenAIResponsesClient
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
    output_dir = ROOT / "artifacts" / "openai"
    output_dir.mkdir(parents=True, exist_ok=True)

    objective, contexts = load_contexts(source)
    packet = BankmapEngine().build_packet(contexts, objective)
    prompt = build_bankmap_prompt(packet)

    client = OpenAIResponsesClient.from_env()
    try:
        max_tokens = int(os.getenv("OPENAI_MAX_OUTPUT_TOKENS", "2048"))
        response_text = client.generate(prompt, max_output_tokens=max_tokens)
    except OpenAIApiError as exc:
        print(f"OpenAI API error: {exc}")
        print("Configure OPENAI_API_KEY and, if needed, OPENAI_MODEL.")
        raise SystemExit(1)

    (output_dir / "bankmap_prompt.md").write_text(prompt, encoding="utf-8")
    (output_dir / "openai_response.json").write_text(response_text, encoding="utf-8")
    parsed, errors = parse_json_output(response_text)
    validation = {"parse_errors": errors}
    if parsed is not None:
        validation.update(validate_multiflow_output(parsed))
    (output_dir / "validation.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Wrote OpenAI artifacts to: {output_dir}")
    print(validation)


if __name__ == "__main__":
    main()
