from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from noemakernel import BankmapEngine, ContextItem
from noemakernel.bidirectional import BidirectionalEvaluator
from noemakernel.context_judge import ContextJudge


def load_contexts(path: Path) -> tuple[str, list[ContextItem]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    contexts = [
        ContextItem(context_id=item["context_id"], content=item["content"])
        for item in data["contexts"]
    ]
    return data["objective"], contexts


def percent(value: float) -> str:
    return f"{value * 100:.2f}%"


def average(values) -> float:
    items = list(values)
    return sum(items) / len(items) if items else 0.0


def judge_contexts(contexts: list[ContextItem], objective: str, profile: str) -> list[dict]:
    judge = ContextJudge(profile=profile)
    results = []
    for index, context in enumerate(contexts):
        state = {
            "previous_contexts": [item.content for item in contexts[:index]],
            "future_contexts": [item.content for item in contexts[index + 1 :]],
            "position": index,
            "total_contexts": len(contexts),
        }
        result = judge.judge_context(context, objective, state).to_dict()
        result["progressive_potentialization"] = round(
            result["judge_score"] * result["terms"]["semantic_power"],
            4,
        )
        results.append(result)
    return results


def run_case(objective: str, contexts: list[ContextItem], size: int, profile: str) -> dict:
    selected_contexts = contexts[:size]
    engine = BankmapEngine(mode="balanced", max_anchors=max(6, min(size, round(size * 0.65))))
    packet = engine.build_packet(selected_contexts, objective)
    bidirectional = BidirectionalEvaluator().evaluate(selected_contexts, packet, objective)
    judge_results = judge_contexts(selected_contexts, objective, profile)
    active = [
        item for item in judge_results
        if item["decision"] in {"promote", "compact"}
    ]
    audit_queue = [
        item for item in judge_results
        if item["decision"] == "audit"
    ]
    discard_queue = [
        item for item in judge_results
        if item["decision"] == "discard"
    ]

    return {
        "size": size,
        "judge_profile": profile,
        "bankmap_metrics": packet.metrics,
        "bidirectional_metrics": bidirectional,
        "judge_metrics": {
            "semantic_sustainment_score_avg": average(
                item["judge_score"] for item in judge_results
            ),
            "semantic_power_avg": average(
                item["terms"]["semantic_power"] for item in judge_results
            ),
            "progressive_potentialization_avg": average(
                item["progressive_potentialization"] for item in judge_results
            ),
            "active_context_ratio": len(active) / len(judge_results) if judge_results else 0.0,
            "audit_context_ratio": len(audit_queue) / len(judge_results) if judge_results else 0.0,
            "discard_context_ratio": len(discard_queue) / len(judge_results) if judge_results else 0.0,
            "active_progressive_potentialization_avg": average(
                item["progressive_potentialization"] for item in active
            ),
            "audit_progressive_potentialization_avg": average(
                item["progressive_potentialization"] for item in audit_queue
            ),
            "decisions": {
                decision: sum(1 for item in judge_results if item["decision"] == decision)
                for decision in ["promote", "compact", "audit", "discard"]
            },
        },
        "contexts": judge_results,
    }


def render_report(results: list[dict]) -> str:
    lines = [
        "# ContextJudge e Potencializacao Progressiva",
        "",
        f"Perfil: `{results[0]['judge_profile']}`",
        "",
        "## Tabela",
        "",
        "| Contextos | Sustainment | Poder semantico | Potencial progressivo | Ativos | Auditoria | Descarte | Potencial ativo | Prog. bidirecional |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for result in results:
        judge = result["judge_metrics"]
        bidirectional = result["bidirectional_metrics"]
        lines.append(
            "| {size} | {sustainment} | {semantic_power} | {progressive} | {active_ratio} | {audit_ratio} | {discard_ratio} | {active_progressive} | {bidirectional_progressive} |".format(
                size=result["size"],
                sustainment=percent(judge["semantic_sustainment_score_avg"]),
                semantic_power=percent(judge["semantic_power_avg"]),
                progressive=percent(judge["progressive_potentialization_avg"]),
                active_ratio=percent(judge["active_context_ratio"]),
                audit_ratio=percent(judge["audit_context_ratio"]),
                discard_ratio=percent(judge["discard_context_ratio"]),
                active_progressive=percent(judge["active_progressive_potentialization_avg"]),
                bidirectional_progressive=percent(bidirectional["progressive_score_avg"]),
            )
        )

    lines.extend(["", "## Top contextos progressivos", ""])
    latest = results[-1]
    top = sorted(
        latest["contexts"],
        key=lambda item: item["progressive_potentialization"],
        reverse=True,
    )[:8]
    for item in top:
        lines.append(
            f"- `{item['context_id']}` {item['decision']} "
            f"score={percent(item['judge_score'])} "
            f"power={percent(item['terms']['semantic_power'])} "
            f"potential={percent(item['progressive_potentialization'])}"
        )

    lines.extend(
        [
            "",
            "## Leitura",
            "",
            "Semantic Sustainment Score julga se um contexto deve entrar no fluxo.",
            "Potencializacao progressiva combina o score do julgador com o poder semantico inferido contra contextos futuros.",
            "Ativos mede apenas contextos liberados para uso operacional: promote ou compact.",
            "Auditoria e uma fila de quarentena, nao retencao para geracao.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    objective, contexts = load_contexts(ROOT / "data" / "stress_contexts.json")
    profile = "llm_continuous"
    results = [run_case(objective, contexts, size, profile) for size in [10, 20, 40]]

    output_dir = ROOT / "artifacts" / "stress"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "context_judge_results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    report = render_report(results)
    (output_dir / "context_judge_report.md").write_text(report, encoding="utf-8")
    print(report)
    print(f"Wrote ContextJudge artifacts to: {output_dir}")


if __name__ == "__main__":
    main()
