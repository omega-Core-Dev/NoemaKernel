"""Prompt builders for manual LLM experiments."""

from __future__ import annotations

from .bankmap import ContextItem, InferencePacket


OUTPUT_SCHEMA = """{
  "user_response": "resposta final ao usuario",
  "memory_updates": [],
  "activated_noemas": [],
  "axiom_checks": [],
  "audit_trail": [],
  "quality_checks": [],
  "next_actions": [],
  "metrics": {
    "contextual_throughput": 0,
    "token_compression_percent": 0,
    "context_coverage_percent": 0,
    "semantic_sustentation_percent": 0,
    "structural_lightness_percent": 0,
    "separability_output_percent": 0,
    "semantic_quality_percent": 0,
    "prompt_quality_percent": 0,
    "auditability_percent": 0
  }
}"""


def build_raw_prompt(contexts: list[ContextItem], objective: str) -> str:
    """Build a baseline prompt with all raw contexts."""

    context_block = "\n\n".join(
        f"## Contexto {context.context_id}\n{context.content}" for context in contexts
    )
    return f"""# Experimento NoemaKernel: Baseline Bruto

## Objetivo
{objective}

## Contextos brutos
{context_block}

## Tarefa
Responda usando os contextos acima. Separe a saida no JSON abaixo, sem texto fora do JSON.

## Schema obrigatorio
```json
{OUTPUT_SCHEMA}
```
"""


def build_bankmap_prompt(packet: InferencePacket) -> str:
    """Build a compact Bankmap prompt from selected anchors."""

    anchors = "\n".join(
        f"- ({anchor.context_id}, {anchor.decision}, score={anchor.score:.2f}) {anchor.text}"
        for anchor in packet.anchors
    )
    metrics = "\n".join(f"- {key}: {_format_metric(value)}" for key, value in packet.metrics.items())
    return f"""# Experimento NoemaKernel: Bankmap Compacto

## Objetivo
{packet.objective}

## Contexto compacto
{packet.compact_context}

## Ancoras semanticas auditadas
{anchors}

## Metricas do Bankmap
{metrics}

## Instrucao
Use o contexto compacto como base principal. Se notar uma ambiguidade fertil, preserve em
`activated_noemas`. Se faltar informacao critica, registre em `next_actions`. Responda sem
texto fora do JSON.

Inclua as metricas do Bankmap dentro de `metrics`, convertendo razoes para porcentagem
quando o campo terminar com `_percent`.

Inclua `quality_checks` com criterios objetivos:

- preservacao semantica;
- qualidade do prompt compacto;
- auditabilidade;
- separacao dos fluxos;
- perda ou risco de perda contextual.

Cada item de `quality_checks` deve ter `criterion`, `score_percent`, `evidence` e `risk`.

Regra dura: o primeiro caractere da resposta deve ser `{{` e o ultimo caractere deve ser `}}`.
Nao explique o que vai fazer. Nao use Markdown. Nao use lista fora do JSON.

## Schema obrigatorio
```json
{OUTPUT_SCHEMA}
```
"""


def _format_metric(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def build_comparison_prompt(raw_response: str, compact_response: str, objective: str) -> str:
    """Build a judge prompt for manual comparison between two outputs."""

    return f"""# Julgamento NoemaKernel

## Objetivo original
{objective}

## Resposta A: contexto bruto
{raw_response}

## Resposta B: Bankmap compacto
{compact_response}

## Tarefa
Compare as respostas tecnicamente. Avalie:

- preservacao de sentido;
- objetividade;
- separabilidade do output;
- perda semantica;
- utilidade para o usuario;
- qual resposta usou melhor o contexto.

Responda em JSON:

```json
{{
  "winner": "A | B | empate",
  "semantic_preservation_A": 0,
  "semantic_preservation_B": 0,
  "output_separation_A": 0,
  "output_separation_B": 0,
  "token_efficiency_winner": "A | B",
  "main_loss_in_B": "",
  "main_gain_in_B": "",
  "verdict": ""
}}
```
"""
