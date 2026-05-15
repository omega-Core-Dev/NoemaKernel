# Experimento NoemaKernel: Bankmap Compacto

## Objetivo
Prototipar Bankmap para reduzir tokens preservando contexto e output separado.

## Contexto compacto
- o final de um livro pode ser o comeco para quem quer compreender a estrutura.
- Reducao de tokens so importa se preservar o sentido.
- Nao quero apenas uma ferramenta que responde.
- Frases curtas podem carregar o contexto inteiro.
- e preciso medir carga contextual e ambiguidade fertil.
- O Bankmap deve tratar muitos contextos em uma unica inferencia.

## Ancoras semanticas auditadas
- (ctx_003, open_noema, score=0.63) o final de um livro pode ser o comeco para quem quer compreender a estrutura.
- (ctx_004, summarize, score=0.56) Reducao de tokens so importa se preservar o sentido.
- (ctx_001, summarize, score=0.52) Nao quero apenas uma ferramenta que responde.
- (ctx_003, summarize, score=0.51) Frases curtas podem carregar o contexto inteiro.
- (ctx_004, summarize, score=0.50) e preciso medir carga contextual e ambiguidade fertil.
- (ctx_002, summarize, score=0.49) O Bankmap deve tratar muitos contextos em uma unica inferencia.

## Metricas do Bankmap
- contexts_processed: 4.0000
- calls_required: 1.0000
- contextual_throughput: 4.0000
- raw_tokens_est: 124.0000
- compact_tokens_est: 73.0000
- token_compression: 0.4113
- anchors_selected: 6.0000
- context_coverage: 1.0000
- semantic_sustentation: 0.5455
- structural_lightness: 0.2243

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

Regra dura: o primeiro caractere da resposta deve ser `{` e o ultimo caractere deve ser `}`.
Nao explique o que vai fazer. Nao use Markdown. Nao use lista fora do JSON.

## Schema obrigatorio
```json
{
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
}
```
