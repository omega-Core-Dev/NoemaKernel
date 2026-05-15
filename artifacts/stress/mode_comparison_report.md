# Bankmap Mode Comparison

## Tabela

| Modo | Contextos | Max ancoras | Compressao | Cobertura | Sustentacao | Leveza |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| aggressive | 4 | 4 | 44.25% | 100.00% | 50.00% | 22.12% |
| aggressive | 10 | 4 | 42.80% | 100.00% | 80.00% | 34.24% |
| aggressive | 20 | 7 | 35.77% | 95.00% | 100.00% | 35.77% |
| aggressive | 40 | 14 | 30.54% | 92.50% | 100.00% | 30.54% |
| balanced | 4 | 6 | 23.01% | 100.00% | 75.00% | 17.26% |
| balanced | 10 | 6 | 42.80% | 100.00% | 52.94% | 22.66% |
| balanced | 20 | 13 | 33.60% | 100.00% | 70.37% | 23.64% |
| balanced | 40 | 26 | 26.57% | 100.00% | 81.25% | 21.59% |
| coverage | 4 | 6 | 23.01% | 100.00% | 75.00% | 17.26% |
| coverage | 10 | 8 | 42.80% | 100.00% | 50.00% | 21.40% |
| coverage | 20 | 17 | 33.60% | 100.00% | 59.38% | 19.95% |
| coverage | 40 | 34 | 26.57% | 100.00% | 74.00% | 19.66% |

## Leitura por modo

### aggressive

- Em 40 contextos: compressao 30.54%.
- Em 40 contextos: cobertura 92.50%.
- Em 40 contextos: sustentacao 100.00%.
- Em 40 contextos: leveza 30.54%.
- Top ancoras em 40 contextos:
  - `ctx_002` summarize score=0.5367: O final pode ser o comeco quando o objetivo e entender o que sustenta o todo.
  - `ctx_015` summarize score=0.5305: o modelo ideal nao apenas responde, ele convive, percebe pequenas frases e instiga reflexao sem ser invasivo.
  - `ctx_025` summarize score=0.5182: nomes de arquivos temporarios podem confundir, mas nao carregam a tese semantica principal.
  - `ctx_031` summarize score=0.5127: esta frase existe para aumentar densidade, mas nao adiciona nova tese estrutural ao sistema.
  - `ctx_008` summarize score=0.506: Ambiguidade fertil nao deve ser removida cedo demais.

### balanced

- Em 40 contextos: compressao 26.57%.
- Em 40 contextos: cobertura 100.00%.
- Em 40 contextos: sustentacao 81.25%.
- Em 40 contextos: leveza 21.59%.
- Top ancoras em 40 contextos:
  - `ctx_002` summarize score=0.5367: O final pode ser o comeco quando o objetivo e entender o que sustenta o todo.
  - `ctx_015` summarize score=0.5305: o modelo ideal nao apenas responde, ele convive, percebe pequenas frases e instiga reflexao sem ser invasivo.
  - `ctx_025` summarize score=0.5182: nomes de arquivos temporarios podem confundir, mas nao carregam a tese semantica principal.
  - `ctx_031` summarize score=0.5127: esta frase existe para aumentar densidade, mas nao adiciona nova tese estrutural ao sistema.
  - `ctx_008` summarize score=0.506: Ambiguidade fertil nao deve ser removida cedo demais.

### coverage

- Em 40 contextos: compressao 26.57%.
- Em 40 contextos: cobertura 100.00%.
- Em 40 contextos: sustentacao 74.00%.
- Em 40 contextos: leveza 19.66%.
- Top ancoras em 40 contextos:
  - `ctx_002` summarize score=0.5367: O final pode ser o comeco quando o objetivo e entender o que sustenta o todo.
  - `ctx_015` summarize score=0.5305: o modelo ideal nao apenas responde, ele convive, percebe pequenas frases e instiga reflexao sem ser invasivo.
  - `ctx_025` summarize score=0.5182: nomes de arquivos temporarios podem confundir, mas nao carregam a tese semantica principal.
  - `ctx_031` summarize score=0.5127: esta frase existe para aumentar densidade, mas nao adiciona nova tese estrutural ao sistema.
  - `ctx_008` summarize score=0.506: Ambiguidade fertil nao deve ser removida cedo demais.

## Conclusao

- `aggressive` deve maximizar compressao e aceitar perda de cobertura.
- `balanced` deve equilibrar cobertura e compressao.
- `coverage` deve preservar representacao ampla e aceitar menos compressao.
