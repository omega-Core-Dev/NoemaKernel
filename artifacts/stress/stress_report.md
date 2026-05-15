# Bankmap Stress Test

## Resumo

| Contextos | Max ancoras | Compressao | Cobertura | Sustentacao | Leveza | Throughput |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 4 | 6 | 23.01% | 100.00% | 75.00% | 17.26% | 4.0 |
| 10 | 6 | 42.80% | 100.00% | 52.94% | 22.66% | 10.0 |
| 20 | 13 | 33.60% | 100.00% | 70.37% | 23.64% | 20.0 |
| 40 | 26 | 26.57% | 100.00% | 81.25% | 21.59% | 40.0 |

## Leitura tecnica

### 4 contextos

- Compressao: 23.01%
- Cobertura: 100.00%
- Sustentacao semantica: 75.00%
- Leveza estrutural: 17.26%
- Top ancoras:
  - `ctx_002` score=0.6517 open_noema: O final pode ser o comeco quando o objetivo e entender o que sustenta o todo.
  - `ctx_004` score=0.6412 preserve: O sistema deve medir carga contextual, ambiguidade fertil e risco de perda semantica.
  - `ctx_001` score=0.5667 summarize: A reducao de tokens precisa preservar sentido e separar o output em fluxos.
  - `ctx_004` score=0.5333 summarize: Nao basta cortar firula textual.
  - `ctx_003` score=0.5 summarize: Frases curtas podem carregar contexto inteiro.

### 10 contextos

- Compressao: 42.80%
- Cobertura: 100.00%
- Sustentacao semantica: 52.94%
- Leveza estrutural: 22.66%
- Top ancoras:
  - `ctx_002` score=0.5967 summarize: O final pode ser o comeco quando o objetivo e entender o que sustenta o todo.
  - `ctx_004` score=0.5552 summarize: O sistema deve medir carga contextual, ambiguidade fertil e risco de perda semantica.
  - `ctx_008` score=0.5488 summarize: Ambiguidade fertil nao deve ser removida cedo demais.
  - `ctx_009` score=0.5348 summarize: O maior risco do Bankmap e reconstruir errado a partir de poucas ancoras.
  - `ctx_010` score=0.5317 summarize: Ele recalcula o peso das partes depois que o objetivo ou final esta conhecido.

### 20 contextos

- Compressao: 33.60%
- Cobertura: 100.00%
- Sustentacao semantica: 70.37%
- Leveza estrutural: 23.64%
- Top ancoras:
  - `ctx_002` score=0.5567 summarize: O final pode ser o comeco quando o objetivo e entender o que sustenta o todo.
  - `ctx_015` score=0.5519 summarize: o modelo ideal nao apenas responde, ele convive, percebe pequenas frases e instiga reflexao sem ser invasivo.
  - `ctx_008` score=0.5488 summarize: Ambiguidade fertil nao deve ser removida cedo demais.
  - `ctx_011` score=0.533 summarize: este trecho fala de configuracao de terminal, arquivos locais e execucao de scripts, mas nao muda a tese do Bankmap.
  - `ctx_017` score=0.5127 summarize: hoje o servico de API pode retornar erro 500, timeout ou texto antes do JSON.

### 40 contextos

- Compressao: 26.57%
- Cobertura: 100.00%
- Sustentacao semantica: 81.25%
- Leveza estrutural: 21.59%
- Top ancoras:
  - `ctx_002` score=0.5367 summarize: O final pode ser o comeco quando o objetivo e entender o que sustenta o todo.
  - `ctx_015` score=0.5305 summarize: o modelo ideal nao apenas responde, ele convive, percebe pequenas frases e instiga reflexao sem ser invasivo.
  - `ctx_025` score=0.5182 summarize: nomes de arquivos temporarios podem confundir, mas nao carregam a tese semantica principal.
  - `ctx_031` score=0.5127 summarize: esta frase existe para aumentar densidade, mas nao adiciona nova tese estrutural ao sistema.
  - `ctx_008` score=0.506 summarize: Ambiguidade fertil nao deve ser removida cedo demais.

## Criterio de alerta

- Cobertura abaixo de 80% indica perda de representacao entre contextos.
- Sustentacao abaixo de 50% indica que a compressao ficou agressiva demais.
- Leveza estrutural baixa com compressao alta indica que o contexto ficou pequeno, mas pouco sustentavel.
