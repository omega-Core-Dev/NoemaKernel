from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from noemakernel import BankmapEngine, ContextItem
from noemakernel.reactivation import ReactivationEvaluator


def load_contexts(path: Path) -> tuple[str, list[ContextItem]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    contexts = [
        ContextItem(context_id=item["context_id"], content=item["content"])
        for item in data["contexts"]
    ]
    return data["objective"], contexts


def percent(value: float) -> str:
    return f"{value * 100:.2f}%"


def run_case(objective: str, contexts: list[ContextItem], mode: str, size: int) -> dict:
    max_anchors = {
        "aggressive": max(4, min(size, round(size * 0.35))),
        "balanced": max(6, min(size, round(size * 0.65))),
        "coverage": max(6, min(size, round(size * 0.85))),
    }[mode]
    engine = BankmapEngine(mode=mode, max_anchors=max_anchors)
    selected_contexts = contexts[:size]
    packet = engine.build_packet(selected_contexts, objective)
    reactivation = ReactivationEvaluator().evaluate(selected_contexts, packet)
    return {
        "mode": mode,
        "size": size,
        "bankmap_metrics": packet.metrics,
        "reactivation_metrics": reactivation,
    }


def render_report(results: list[dict]) -> str:
    lines = [
        "# Reativacao Contextual e Reconstrucao Cognitiva",
        "",
        "## Tabela",
        "",
        "| Modo | Contextos | Cobertura | Reativacao | Reconstrucao | Score cognitivo |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for result in results:
        bankmap = result["bankmap_metrics"]
        metrics = result["reactivation_metrics"]
        lines.append(
            "| {mode} | {size} | {coverage} | {reactivation} | {reconstruction} | {cognitive} |".format(
                mode=result["mode"],
                size=result["size"],
                coverage=percent(bankmap["context_coverage"]),
                reactivation=percent(metrics["reactivation_ratio_avg"]),
                reconstruction=percent(metrics["reconstruction_ratio_avg"]),
                cognitive=percent(metrics["cognitive_reconstruction_score_avg"]),
            )
        )

    lines.extend(["", "## Leitura", ""])
    for result in results:
        if result["size"] != 40:
            continue
        metrics = result["reactivation_metrics"]
        lines.append(f"### {result['mode']} em 40 contextos")
        lines.append(f"- Cobertura reativada: {percent(metrics['reactivation_context_coverage'])}")
        lines.append(f"- Reativacao media: {percent(metrics['reactivation_ratio_avg'])}")
        lines.append(f"- Reconstrucao media: {percent(metrics['reconstruction_ratio_avg'])}")
        lines.append(f"- Score cognitivo medio: {percent(metrics['cognitive_reconstruction_score_avg'])}")
        weak = sorted(
            metrics["contexts"],
            key=lambda item: item["cognitive_reconstruction_score"],
        )[:3]
        lines.append("- Piores contextos:")
        for item in weak:
            lines.append(
                f"  - `{item['context_id']}` score={percent(item['cognitive_reconstruction_score'])} "
                f"anchors={item['anchor_count']} missing={', '.join(item['missing_terms'][:5])}"
            )
        lines.append("")

    lines.extend(
        [
            "## Criterio de viabilidade",
            "",
            "- Acima de 60% de score cognitivo medio: viavel para MVP textual.",
            "- Entre 40% e 60%: viavel, mas precisa julgador/embedding.",
            "- Abaixo de 40%: ancoras insuficientes para reconstrucao.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    objective, contexts = load_contexts(ROOT / "data" / "stress_contexts.json")
    modes = ["aggressive", "balanced", "coverage"]
    sizes = [10, 20, 40]
    results = [run_case(objective, contexts, mode, size) for mode in modes for size in sizes]

    output_dir = ROOT / "artifacts" / "stress"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "reactivation_results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    report = render_report(results)
    (output_dir / "reactivation_report.md").write_text(report, encoding="utf-8")
    print(report)
    print(f"Wrote reactivation artifacts to: {output_dir}")


if __name__ == "__main__":
    main()
