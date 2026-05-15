# Retomada - NoemaKernel / Bankmap

Data: 2026-05-13

## Estado atual

Projeto evoluiu de conceito para prototipo local executavel.

Nucleo atual:

```text
NoemaKernel = arquitetura experimental
Bankmap = motor de navegacao contextual bidirecional
```

Principais ideias estabilizadas:

- N contextos podem ser tratados como fluxo contextual, nao apenas historico linear.
- Bankmap seleciona ancoras semanticas por carga contextual.
- Contexto regressivo: parte do objetivo/final e volta aos contextos sustentadores.
- Contexto progressivo: mede o que uma ancora ativa nos proximos contextos.
- Contexto bidirecional: cruza regressivo + progressivo.
- Output multi-fluxo: resposta, memoria, noemas, axiomas, auditoria, quality checks e metricas.
- Compressao deixou de ser objetivo principal; foco atual e reativacao contextual e reconstrucao cognitiva.

## Resultados importantes

Stress test com 40 contextos:

```text
balanced:
compressao: 26.57%
cobertura: 100.00%
sustentacao: 81.25%
leveza: 21.59%
```

Reativacao/reconstrucao com 40 contextos:

```text
balanced:
cobertura: 100.00%
reativacao media: 74.75%
reconstrucao media: 74.89%
score cognitivo: 69.85%
```

Contexto bidirecional:

```text
ancoras avaliadas: 40
estabilidade bidirecional: 72.50%
score regressivo medio: 100.00%
score progressivo medio: 45.11%
score bidirecional medio: 75.30%
```

ContextJudge / Semantic Sustainment Score:

```text
modulo implementado: noemakernel/context_judge.py
testes unitarios: tests/test_context_judge.py
script: examples/run_context_judge_test.py
perfil operacional: llm_continuous

40 contextos:
sustainment medio: 50.83%
poder semantico medio: 43.88%
potencializacao progressiva media: 24.40%
contextos ativos para promote/compact: 22.50%
contextos em auditoria: 42.50%
contextos descartados: 35.00%
potencializacao progressiva ativa: 45.82%

parametros llm_continuous:
pesos: relevance=0.25, coherence=0.20, confidence=0.25, recency=0.05, semantic_power=0.45,
       redundancy_penalty=0.08, noise_penalty=0.25, contradiction_penalty=0.30
limiares: promote>=0.82, compact>=0.60, audit>=0.45, discard<0.45
```

Gemma API:

- chave local carregada em `local_api_key.py`;
- chamada funcionou;
- output validado com `separability_output = 1.0`;
- API as vezes retorna HTTP 500 ou demora ~40-60s.

## Arquivos principais

Codigo:

- `noemakernel/bankmap.py`
- `noemakernel/reactivation.py`
- `noemakernel/bidirectional.py`
- `noemakernel/context_judge.py`
- `noemakernel/gemma_api.py`
- `noemakernel/openai_api.py`
- `noemakernel/prompts.py`
- `noemakernel/validation.py`

Exemplos:

- `examples/demo_bankmap.py`
- `examples/run_gemma_bankmap.py`
- `examples/gemma_terminal.py`
- `examples/run_stress_test.py`
- `examples/compare_bankmap_modes.py`
- `examples/run_reactivation_test.py`
- `examples/run_bidirectional_test.py`
- `examples/run_context_judge_test.py`
- `examples/generate_chatgpt_prompts.py`

Docs/checagem:

- `checagem/README.md`
- `checagem/bankmap.md`
- `checagem/contexto-regressivo-e-ancoras.md`
- `checagem/reativacao-reconstrucao.md`
- `checagem/contexto-bidirecional.md`
- `checagem/modos-bankmap.md`
- `checagem/stress-test.md`
- `checagem/grafo-arquitetura.html`
- `checagem/grafo-arquitetura-mermaid.md`

Artifacts:

- `artifacts/stress/stress_report.md`
- `artifacts/stress/mode_comparison_report.md`
- `artifacts/stress/reactivation_report.md`
- `artifacts/stress/bidirectional_report.md`
- `artifacts/stress/context_judge_report.md`
- `artifacts/prompts/bankmap_compact_prompt.md`

## Comandos uteis

```powershell
python -m unittest discover -s tests
python .\examples\demo_bankmap.py
python .\examples\run_stress_test.py
python .\examples\compare_bankmap_modes.py
python .\examples\run_reactivation_test.py
python .\examples\run_bidirectional_test.py
python .\examples\run_context_judge_test.py
python .\examples\generate_chatgpt_prompts.py
python .\examples\check_api_config.py
python .\examples\run_gemma_bankmap.py
python .\examples\gemma_terminal.py
```

## Proxima sessao

Objetivo: preparar repo para GitHub/open source.

Checklist:

1. Limpar estrutura publica do projeto.
2. Revisar `README.md` com pitch, status, uso e aviso de metricas heuristicas.
3. Criar `LICENSE`.
4. Criar `ROADMAP.md`.
5. Criar `CONTRIBUTING.md` simples.
6. Mover docs publicas para `docs/`.
7. Decidir se `checagem/` fica como laboratorio ou vira `docs/internal/`.
8. Garantir `.gitignore` protege `local_api_key.py`, `.env` e artifacts sensiveis.
9. Rodar todos os testes.
10. Preparar texto de divulgacao para X.

## Tom publico recomendado

Nao vender como benchmark nem como substituto de agentes.

Mensagem:

```text
NoemaKernel is an experimental open-source architecture for bidirectional contextual
navigation in LLM workflows.
```

Aviso:

```text
Early prototype. Metrics are heuristic and should not be treated as benchmark claims yet.
```

Frase forte:

```text
Bankmap does not replace agents. It gives agents a measurable contextual substrate.
```

## Ideia futura

Perfis de agentes:

```text
profiles/
  coding_agent.json
  research_agent.json
  personal_agent.json
  teacher_agent.json
```

Cada perfil deve ter:

- axiomas;
- metricas;
- output esperado;
- Judge especifico.
