from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from noemakernel import BankmapEngine, ContextItem
from noemakernel.bidirectional import BidirectionalEvaluator


def load_contexts(path: Path) -> tuple[str, list[ContextItem]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["objective"], [
        ContextItem(context_id=item["context_id"], content=item["content"])
        for item in data["contexts"]
    ]


def percent(value: float) -> str:
    return f"{value * 100:.2f}%"


def main() -> None:
    objective, contexts = load_contexts(ROOT / "data" / "stress_contexts.json")
    selected = contexts[:40]
    engine = BankmapEngine(mode="balanced", max_anchors=26)
    packet = engine.build_packet(selected, objective)
    result = BidirectionalEvaluator().evaluate(selected, packet, objective)

    output_dir = ROOT / "artifacts" / "stress"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "bidirectional_results.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# Contexto Bidirecional",
        "",
        "## Resultado",
        "",
        f"- Ancoras avaliadas: {result['anchors_evaluated']}",
        f"- Estabilidade bidirecional: {percent(result['bidirectional_stability'])}",
        f"- Score regressivo medio: {percent(result['regressive_score_avg'])}",
        f"- Score progressivo medio: {percent(result['progressive_score_avg'])}",
        f"- Score bidirecional medio: {percent(result['bidirectional_score_avg'])}",
        "",
        "## Top ancoras bidirecionais",
        "",
    ]
    top = sorted(result["anchors"], key=lambda item: item["bidirectional_score"], reverse=True)[:8]
    for item in top:
        lines.append(
            f"- `{item['context_id']}` {item['direction']} "
            f"bi={percent(item['bidirectional_score'])} "
            f"reg={percent(item['regressive_score'])} "
            f"prog={percent(item['progressive_score'])}: {item['anchor_text']}"
        )

    lines.extend(
        [
            "",
            "## Leitura",
            "",
            "Contexto regressivo mede sustentacao pelo que veio antes e pelo objetivo.",
            "Contexto progressivo mede se a ancora abre caminho para contextos seguintes.",
            "Estabilidade bidirecional mede quantas ancoras conseguem operar nos dois sentidos.",
        ]
    )
    report = "\n".join(lines) + "\n"
    (output_dir / "bidirectional_report.md").write_text(report, encoding="utf-8")
    print(report)
    print(f"Wrote bidirectional artifacts to: {output_dir}")


if __name__ == "__main__":
    main()
