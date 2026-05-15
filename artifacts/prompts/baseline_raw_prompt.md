# Experimento NoemaKernel: Baseline Bruto

## Objetivo
Prototipar Bankmap para reduzir tokens preservando contexto e output separado.

## Contextos brutos
## Contexto ctx_001
Eu almejo uma LLM de convivio. Nao quero apenas uma ferramenta que responde. Quero que ela perceba frases pequenas e instigue reflexao sem ser intrusiva.

## Contexto ctx_002
O Bankmap deve tratar muitos contextos em uma unica inferencia. Depois a saida precisa voltar separada em resposta, memoria, auditoria e noemas.

## Contexto ctx_003
O insight veio da leitura regressiva: o final de um livro pode ser o comeco para quem quer compreender a estrutura. Frases curtas podem carregar o contexto inteiro.

## Contexto ctx_004
Reducao de tokens so importa se preservar o sentido. Nao basta cortar firula; e preciso medir carga contextual e ambiguidade fertil.

## Tarefa
Responda usando os contextos acima. Separe a saida no JSON abaixo, sem texto fora do JSON.

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
