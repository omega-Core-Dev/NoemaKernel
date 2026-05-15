from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from noemakernel import BankmapEngine, ContextItem


MODES = ["aggressive", "balanced", "coverage"]
SIZES = [4, 10, 20, 40]


def load_contexts(path: Path) -> tuple[str, list[ContextItem]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    contexts = [
        ContextItem(context_id=item["context_id"], content=item["content"])
        for item in data["contexts"]
    ]
    return data["objective"], contexts


def anchors_for(mode: str, size: int) -> int:
    if mode == "aggressive":
        return max(4, min(size, round(size * 0.35)))
    if mode == "coverage":
        return max(6, min(size, round(size * 0.85)))
    return max(6, min(size, round(size * 0.65)))


def run_case(objective: str, contexts: list[ContextItem], mode: str, size: int) -> dict:
    engine = BankmapEngine(mode=mode, max_anchors=anchors_for(mode, size))
    packet = engine.build_packet(contexts[:size], objective)
    return {
        "mode": mode,
        "size": size,
        "max_anchors": engine.max_anchors,
        "thresholds": {
            "preserve_threshold": engine.preserve_threshold,
            "summarize_threshold": engine.summarize_threshold,
            "coverage_floor": engine.coverage_floor,
        },
        "metrics": packet.metrics,
        "top_anchors": [
            {
                "context_id": anchor.context_id,
                "score": round(anchor.score, 4),
                "decision": anchor.decision,
                "text": anchor.text,
            }
            for anchor in packet.anchors[:5]
        ],
    }


def percent(value: float) -> str:
    return f"{value * 100:.2f}%"


def render_report(results: list[dict]) -> str:
    lines = [
        "# Bankmap Mode Comparison",
        "",
        "## Tabela",
        "",
        "| Modo | Contextos | Max ancoras | Compressao | Cobertura | Sustentacao | Leveza |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for result in results:
        metrics = result["metrics"]
        lines.append(
            "| {mode} | {size} | {max_anchors} | {compression} | {coverage} | {sustentation} | {lightness} |".format(
                mode=result["mode"],
                size=result["size"],
                max_anchors=result["max_anchors"],
                compression=percent(metrics["token_compression"]),
                coverage=percent(metrics["context_coverage"]),
                sustentation=percent(metrics["semantic_sustentation"]),
                lightness=percent(metrics["structural_lightness"]),
            )
        )

    lines.extend(["", "## Leitura por modo", ""])
    for mode in MODES:
        mode_results = [result for result in results if result["mode"] == mode]
        last = mode_results[-1]
        metrics = last["metrics"]
        lines.append(f"### {mode}")
        lines.append("")
        lines.append(f"- Em 40 contextos: compressao {percent(metrics['token_compression'])}.")
        lines.append(f"- Em 40 contextos: cobertura {percent(metrics['context_coverage'])}.")
        lines.append(f"- Em 40 contextos: sustentacao {percent(metrics['semantic_sustentation'])}.")
        lines.append(f"- Em 40 contextos: leveza {percent(metrics['structural_lightness'])}.")
        lines.append("- Top ancoras em 40 contextos:")
        for anchor in last["top_anchors"]:
            lines.append(f"  - `{anchor['context_id']}` {anchor['decision']} score={anchor['score']}: {anchor['text']}")
        lines.append("")

    lines.extend(
        [
            "## Conclusao",
            "",
            "- `aggressive` deve maximizar compressao e aceitar perda de cobertura.",
            "- `balanced` deve equilibrar cobertura e compressao.",
            "- `coverage` deve preservar representacao ampla e aceitar menos compressao.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    objective, contexts = load_contexts(ROOT / "data" / "stress_contexts.json")
    results = [
        run_case(objective, contexts, mode, size)
        for mode in MODES
        for size in SIZES
    ]
    output_dir = ROOT / "artifacts" / "stress"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "mode_comparison_results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    report = render_report(results)
    (output_dir / "mode_comparison_report.md").write_text(report, encoding="utf-8")
    print(report)
    print(f"Wrote mode comparison artifacts to: {output_dir}")


if __name__ == "__main__":
    main()
