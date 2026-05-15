# Stress Test Bankmap

## Objetivo

Medir o comportamento do Bankmap com aumento de densidade contextual:

- 4 contextos;
- 10 contextos;
- 20 contextos;
- 40 contextos.

O dataset inclui contexto essencial, ruido, repeticao, conflito e ambiguidade fertil.

## Resultado atual

| Contextos | Compressao | Cobertura | Sustentacao | Leveza | Throughput |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 4 | 23.01% | 100.00% | 75.00% | 17.26% | 4.0 |
| 10 | 42.80% | 100.00% | 52.94% | 22.66% | 10.0 |
| 20 | 33.60% | 100.00% | 70.37% | 23.64% | 20.0 |
| 40 | 26.57% | 100.00% | 81.25% | 21.59% | 40.0 |

## Achado tecnico

A primeira rodada com ranking puro gerou boa compressao em 40 contextos, mas cobertura de
apenas 65%. Isso indicava perda de representacao entre contextos.

Foi adicionada a decisao `low_signal`, que preserva uma ancora de baixa carga quando
necessario para manter cobertura. O efeito foi:

- cobertura subiu para 100%;
- compressao em 40 contextos caiu de 50.06% para 26.57%;
- sustentacao semantica permaneceu alta em 81.25%.

## Leitura

O Bankmap mostrou um tradeoff claro:

```text
mais cobertura -> menos compressao
mais compressao -> risco de perder contextos inteiros
```

Isso e importante porque valida que o motor precisa de modos:

- `aggressive`: prioriza compressao;
- `balanced`: tenta equilibrar cobertura e compressao;
- `coverage`: preserva representacao de todos os contextos.

## Arquivos

- `data/stress_contexts.json`
- `examples/run_stress_test.py`
- `artifacts/stress/stress_results.json`
- `artifacts/stress/stress_report.md`
