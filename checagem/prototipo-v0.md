# Prototipo v0

## Objetivo

Validar localmente a primeira forma executavel do Bankmap:

```text
N contextos -> ancoras semanticas -> contexto compacto -> output multi-fluxo
```

## Arquivos criados

- `noemakernel/bankmap.py`: motor heuristico local.
- `noemakernel/__init__.py`: exportacao do pacote.
- `examples/demo_bankmap.py`: demonstracao executavel.
- `tests/test_bankmap.py`: testes basicos.
- `README.md`: instrucoes de execucao.

## O que o prototipo faz

1. Recebe varios `ContextItem`.
2. Divide cada contexto em frases.
3. Calcula carga contextual por heuristica.
4. Classifica trechos como `preserve`, `summarize`, `open_noema` ou `remove`.
5. Seleciona ancoras com cobertura minima por contexto.
6. Monta um `InferencePacket`.
7. Gera um output multi-fluxo simulado.

## Metricas emitidas

- `contexts_processed`
- `calls_required`
- `contextual_throughput`
- `raw_tokens_est`
- `compact_tokens_est`
- `token_compression`
- `anchors_selected`
- `context_coverage`
- `semantic_sustentation`
- `structural_lightness`

## Resultado da demo atual

Com 4 contextos de exemplo:

- vazao contextual: 4 contextos / 1 chamada;
- tokens brutos estimados: 124;
- tokens compactos estimados: 73;
- compressao estimada: 41.1%;
- cobertura de contexto: 100%;
- sustentacao semantica: 54.5%;
- leveza estrutural: 22.4%.

## Leitura tecnica

O resultado ja mostra o comportamento que precisa ser testado:

- a compressao existe;
- a cobertura entre contextos foi preservada;
- o audit trail separa o que foi medido do que seria enviado para a LLM;
- a sustentacao semantica ainda e baixa e precisa de validacao humana/modelo.

## Proxima melhoria

Trocar parte das heuristicas por avaliacao com LLM ou embeddings locais:

- detectar ancoras melhores;
- medir similaridade entre contexto bruto e compacto;
- validar se a resposta com contexto compacto preserva qualidade;
- comparar contra baseline de prompt bruto.
