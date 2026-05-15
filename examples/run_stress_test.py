from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from noemakernel import BankmapEngine, ContextItem


def load_contexts(path: Path) -> tuple[str, list[ContextItem]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    contexts = [
        ContextItem(context_id=item["context_id"], content=item["content"])
        for item in data["contexts"]
    ]
    return data["objective"], contexts


def run_case(objective: str, contexts: list[ContextItem], size: int) -> dict:
    engine = BankmapEngine(max_anchors=max(6, min(size, round(size * 0.65))))
    packet = engine.build_packet(contexts[:size], objective)
    output = engine.simulate_output(packet)
    return {
        "size": size,
        "max_anchors": engine.max_anchors,
        "metrics": packet.metrics,
        "output_metrics": output["metrics"],
        "quality_checks": output["quality_checks"],
        "top_anchors": [
            {
                "context_id": anchor.context_id,
                "score": round(anchor.score, 4),
                "decision": anchor.decision,
                "text": anchor.text,
            }
            for anchor in packet.anchors[:8]
        ],
    }


def percent(value: float) -> str:
    return f"{value * 100:.2f}%"


def render_report(results: list[dict]) -> str:
    lines = [
        "# Bankmap Stress Test",
        "",
        "## Resumo",
        "",
        "| Contextos | Max ancoras | Compressao | Cobertura | Sustentacao | Leveza | Throughput |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for result in results:
        metrics = result["metrics"]
        lines.append(
            "| {size} | {max_anchors} | {compression} | {coverage} | {sustentation} | {lightness} | {throughput:.1f} |".format(
                size=result["size"],
                max_anchors=result["max_anchors"],
                compression=percent(metrics["token_compression"]),
                coverage=percent(metrics["context_coverage"]),
                sustentation=percent(metrics["semantic_sustentation"]),
                lightness=percent(metrics["structural_lightness"]),
                throughput=metrics["contextual_throughput"],
            )
        )

    lines.extend(["", "## Leitura tecnica", ""])
    for result in results:
        metrics = result["metrics"]
        lines.append(f"### {result['size']} contextos")
        lines.append("")
        lines.append(f"- Compressao: {percent(metrics['token_compression'])}")
        lines.append(f"- Cobertura: {percent(metrics['context_coverage'])}")
        lines.append(f"- Sustentacao semantica: {percent(metrics['semantic_sustentation'])}")
        lines.append(f"- Leveza estrutural: {percent(metrics['structural_lightness'])}")
        lines.append("- Top ancoras:")
        for anchor in result["top_anchors"][:5]:
            lines.append(
                f"  - `{anchor['context_id']}` score={anchor['score']} {anchor['decision']}: {anchor['text']}"
            )
        lines.append("")

    lines.extend(
        [
            "## Criterio de alerta",
            "",
            "- Cobertura abaixo de 80% indica perda de representacao entre contextos.",
            "- Sustentacao abaixo de 50% indica que a compressao ficou agressiva demais.",
            "- Leveza estrutural baixa com compressao alta indica que o contexto ficou pequeno, mas pouco sustentavel.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    objective, contexts = load_contexts(ROOT / "data" / "stress_contexts.json")
    sizes = [4, 10, 20, 40]
    results = [run_case(objective, contexts, size) for size in sizes]

    output_dir = ROOT / "artifacts" / "stress"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "stress_results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (output_dir / "stress_report.md").write_text(render_report(results), encoding="utf-8")

    print(render_report(results))
    print(f"Wrote stress artifacts to: {output_dir}")


if __name__ == "__main__":
    main()
