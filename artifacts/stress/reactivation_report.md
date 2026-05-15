# Reativacao Contextual e Reconstrucao Cognitiva

## Tabela

| Modo | Contextos | Cobertura | Reativacao | Reconstrucao | Score cognitivo |
| --- | ---: | ---: | ---: | ---: | ---: |
| aggressive | 10 | 100.00% | 54.13% | 54.49% | 53.43% |
| aggressive | 20 | 95.00% | 64.51% | 64.77% | 61.20% |
| aggressive | 40 | 92.50% | 70.50% | 70.64% | 65.70% |
| balanced | 10 | 100.00% | 54.13% | 54.49% | 53.43% |
| balanced | 20 | 100.00% | 67.01% | 67.27% | 63.70% |
| balanced | 40 | 100.00% | 74.75% | 74.89% | 69.85% |
| coverage | 10 | 100.00% | 54.13% | 54.49% | 53.43% |
| coverage | 20 | 100.00% | 67.01% | 67.27% | 63.70% |
| coverage | 40 | 100.00% | 74.75% | 74.89% | 69.85% |

## Leitura

### aggressive em 40 contextos
- Cobertura reativada: 92.50%
- Reativacao media: 70.50%
- Reconstrucao media: 70.64%
- Score cognitivo medio: 65.70%
- Piores contextos:
  - `ctx_006` score=0.00% anchors=0 missing=auditabilidade, carregar, cobertura, compressao, junto
  - `ctx_012` score=0.00% anchors=0 missing=preservando, reduzir, repeticao, sentido, tokens
  - `ctx_027` score=0.00% anchors=0 missing=antes, dentro, explicacao, json, localizar

### balanced em 40 contextos
- Cobertura reativada: 100.00%
- Reativacao media: 74.75%
- Reconstrucao media: 74.89%
- Score cognitivo medio: 69.85%
- Piores contextos:
  - `ctx_040` score=17.27% anchors=1 missing=aumenta, compressao, demais, ponto, precisa
  - `ctx_012` score=26.00% anchors=1 missing=preservando, reduzir, sentido, tokens
  - `ctx_004` score=33.48% anchors=1 missing=ambiguidade, carga, contextual, deve, fertil

### coverage em 40 contextos
- Cobertura reativada: 100.00%
- Reativacao media: 74.75%
- Reconstrucao media: 74.89%
- Score cognitivo medio: 69.85%
- Piores contextos:
  - `ctx_040` score=17.27% anchors=1 missing=aumenta, compressao, demais, ponto, precisa
  - `ctx_012` score=26.00% anchors=1 missing=preservando, reduzir, sentido, tokens
  - `ctx_004` score=33.48% anchors=1 missing=ambiguidade, carga, contextual, deve, fertil

## Criterio de viabilidade

- Acima de 60% de score cognitivo medio: viavel para MVP textual.
- Entre 40% e 60%: viavel, mas precisa julgador/embedding.
- Abaixo de 40%: ancoras insuficientes para reconstrucao.
