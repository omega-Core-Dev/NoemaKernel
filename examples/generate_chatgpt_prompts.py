from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from noemakernel import BankmapEngine, ContextItem
from noemakernel.prompts import build_bankmap_prompt, build_raw_prompt


def load_contexts(path: Path) -> tuple[str, list[ContextItem]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    contexts = [
        ContextItem(
            context_id=item["context_id"],
            content=item["content"],
            source=item.get("source", "user"),
            kind=item.get("kind", "text"),
            weight=float(item.get("weight", 1.0)),
            metadata=item.get("metadata", {}),
        )
        for item in data["contexts"]
    ]
    return data["objective"], contexts


def main() -> None:
    source = ROOT / "data" / "sample_contexts.json"
    output_dir = ROOT / "artifacts" / "prompts"
    output_dir.mkdir(parents=True, exist_ok=True)

    objective, contexts = load_contexts(source)
    engine = BankmapEngine()
    packet = engine.build_packet(contexts, objective)

    (output_dir / "baseline_raw_prompt.md").write_text(
        build_raw_prompt(contexts, objective),
        encoding="utf-8",
    )
    (output_dir / "bankmap_compact_prompt.md").write_text(
        build_bankmap_prompt(packet),
        encoding="utf-8",
    )
    (output_dir / "bankmap_packet.json").write_text(packet.to_json(), encoding="utf-8")

    print(f"Wrote prompts to: {output_dir}")
    print(f"token_compression={packet.metrics['token_compression']:.2%}")
    print(f"context_coverage={packet.metrics['context_coverage']:.2%}")


if __name__ == "__main__":
    main()
