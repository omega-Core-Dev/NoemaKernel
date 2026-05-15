# Contexto Bidirecional

## Definicao

O contexto bidirecional combina:

- contexto regressivo: o que sustenta o estado final/objetivo;
- contexto progressivo: o que uma ancora permite ativar nos proximos contextos.

## Metricas

```text
regressive_score = overlap(ancora, contexto anterior + objetivo)
progressive_score = overlap(ancora + objetivo, contextos seguintes)
bidirectional_score = regressive_score * 0.55 + progressive_score * 0.45
```

## Resultado atual

Com 40 contextos em modo `balanced`:

- ancoras avaliadas: 40;
- estabilidade bidirecional: 72.50%;
- score regressivo medio: 100.00%;
- score progressivo medio: 45.11%;
- score bidirecional medio: 75.30%.

## Leitura

O resultado indica que a maior parte das ancoras nao apenas explica o contexto anterior,
mas tambem ajuda a ativar caminhos posteriores. Isso transforma o Bankmap de compressor
contextual em motor de navegacao contextual.

## Arquivos

- `noemakernel/bidirectional.py`
- `examples/run_bidirectional_test.py`
- `artifacts/stress/bidirectional_report.md`
- `artifacts/stress/bidirectional_results.json`
