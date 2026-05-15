# Modos do Bankmap

## Modos implementados

- `aggressive`: prioriza compressao e aceita alguma perda de cobertura.
- `balanced`: equilibra compressao, cobertura e sustentacao.
- `coverage`: prioriza representacao ampla dos contextos.

## Resultado em 40 contextos

| Modo | Compressao | Cobertura | Sustentacao | Leveza |
| --- | ---: | ---: | ---: | ---: |
| aggressive | 30.54% | 92.50% | 100.00% | 30.54% |
| balanced | 26.57% | 100.00% | 81.25% | 21.59% |
| coverage | 26.57% | 100.00% | 74.00% | 19.66% |

## Leitura

O modo `aggressive` apresentou melhor leveza em 40 contextos, mas abriu mao de cobertura
total. Isso confirma o tradeoff esperado.

O modo `balanced` preservou 100% de cobertura e sustentacao alta, com compressao menor.

O modo `coverage` tambem preservou cobertura total, mas nao superou o `balanced` nesse
dataset. Isso indica que os thresholds ainda precisam ser calibrados para diferenciar melhor
os modos em casos grandes.

## Arquivos

- `examples/compare_bankmap_modes.py`
- `artifacts/stress/mode_comparison_report.md`
- `artifacts/stress/mode_comparison_results.json`
