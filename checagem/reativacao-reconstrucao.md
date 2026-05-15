# Reativacao Contextual e Reconstrucao Cognitiva

## Objetivo

Avaliar se as ancoras selecionadas pelo Bankmap conseguem reativar contexto suficiente para
sustentar uma resposta, sem depender apenas da metrica de compressao.

## Metricas implementadas

### Reativacao contextual

Mede quanto dos termos centrais do contexto original reaparece nas ancoras selecionadas.

```text
reactivation_ratio = termos_reativados / termos_originais
```

### Reconstrucao cognitiva

Mede a capacidade das ancoras de reconstruir o contexto por correspondencia direta e ponte
semantica simples.

```text
reconstruction_ratio = cobertura_direta * 0.75 + ponte_semantica * 0.25
```

### Score cognitivo

Combina reativacao, reconstrucao e densidade de ancoras.

```text
cognitive_reconstruction_score =
  0.45 * reactivation_ratio
+ 0.35 * reconstruction_ratio
+ 0.20 * anchor_density
```

## Resultado em 40 contextos

| Modo | Cobertura | Reativacao | Reconstrucao | Score cognitivo |
| --- | ---: | ---: | ---: | ---: |
| aggressive | 92.50% | 70.50% | 70.64% | 65.70% |
| balanced | 100.00% | 74.75% | 74.89% | 69.85% |
| coverage | 100.00% | 74.75% | 74.89% | 69.85% |

## Leitura

A abordagem e viavel para MVP textual.

O criterio adotado foi:

- acima de 60%: viavel para MVP textual;
- 40% a 60%: viavel, mas precisa julgador/embedding;
- abaixo de 40%: ancoras insuficientes.

`balanced` e `coverage` chegaram a 69.85% de score cognitivo medio em 40 contextos, com
100% de cobertura. Isso indica que as ancoras nao apenas comprimem: elas preservam capacidade
de reativacao contextual.

## Limite

A metrica atual ainda e lexical/heuristica. Ela mede sobreposicao e correspondencia suave de
termos, nao compreensao semantica profunda.

Proxima melhoria recomendada:

- usar embeddings locais ou LLM julgador para medir reconstrucao semantica real;
- separar reconstrucao narrativa, estrutural e inferencial;
- testar com contexto maior e mais ambiguo.

## Arquivos

- `noemakernel/reactivation.py`
- `examples/run_reactivation_test.py`
- `artifacts/stress/reactivation_report.md`
- `artifacts/stress/reactivation_results.json`
