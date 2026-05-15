# NoemaKernel

Prototipo inicial para testar a arquitetura Bankmap / NoemaKernel.

## Ideia

O Bankmap recebe multiplos contextos, mede carga contextual, seleciona ancoras semanticas
e monta um pacote compacto para uma unica inferencia de LLM. A saida esperada e multi-fluxo:
resposta ao usuario, memoria, noemas, auditoria, checagem de axiomas e proximas acoes.

## Rodar demo

```powershell
python .\examples\demo_bankmap.py
```

## Gerar prompts para testar no ChatGPT Plus

```powershell
python .\examples\generate_chatgpt_prompts.py
```

Isso cria:

- `artifacts/prompts/baseline_raw_prompt.md`
- `artifacts/prompts/bankmap_compact_prompt.md`
- `artifacts/prompts/bankmap_packet.json`

Cole primeiro o prompt bruto no ChatGPT, depois o prompt compacto, e compare as respostas.

## Validar output multi-fluxo

Depois de salvar uma resposta JSON em arquivo:

```powershell
python .\examples\validate_output.py .\artifacts\resposta.json
```

## Rodar com Gemma/Gemini API

Configure uma chave do Google AI Studio/Gemini API. Voce pode usar variavel de ambiente:

```powershell
$env:GEMINI_API_KEY="sua-chave"
$env:GEMMA_MODEL="gemma-4-31b-it"
python .\examples\run_gemma_bankmap.py
```

Ou copie `.env.example` para `.env` e preencha `GEMINI_API_KEY`:

```powershell
Copy-Item .env.example .env
notepad .env
python .\examples\run_gemma_bankmap.py
```

Se o ID do modelo na sua conta for diferente, ajuste `GEMMA_MODEL`. O prototipo deixa o
modelo configuravel para acompanhar disponibilidade por conta/regiao.

Tambem da para usar arquivo Python local:

```powershell
Copy-Item local_api_key.example.py local_api_key.py
notepad local_api_key.py
python .\examples\run_gemma_bankmap.py
```

Preencha `GEMINI_API_KEY` dentro de `local_api_key.py`. Esse arquivo esta no `.gitignore`.

Para chamadas lentas, adicione tambem:

```python
GEMMA_TIMEOUT_SECONDS = 180
```

## Terminal interativo Gemma

```powershell
python .\examples\gemma_terminal.py
```

Opcoes uteis:

```powershell
python .\examples\gemma_terminal.py --model gemma-4-31b-it --temperature 0.4 --max-output-tokens 2048
python .\examples\gemma_terminal.py --json
```

Dentro do terminal use `/help`, `/model`, `/temp`, `/tokens`, `/json`, `/clear`,
`/raw` e `/exit`.

## Rodar com OpenAI / GPT

No `local_api_key.py`, preencha:

```python
OPENAI_API_KEY = "sua-chave"
OPENAI_MODEL = "gpt-5.4-mini"
OPENAI_MAX_OUTPUT_TOKENS = 2048
OPENAI_TIMEOUT_SECONDS = 180
```

Depois rode:

```powershell
python .\examples\run_openai_bankmap.py
```

## Rodar testes

```powershell
python -m unittest discover -s tests
```

## Rodar stress test local

```powershell
python .\examples\run_stress_test.py
```

Saidas:

- `artifacts/stress/stress_results.json`
- `artifacts/stress/stress_report.md`

## Comparar modos Bankmap

```powershell
python .\examples\compare_bankmap_modes.py
```

Saidas:

- `artifacts/stress/mode_comparison_results.json`
- `artifacts/stress/mode_comparison_report.md`

## Testar reativacao contextual

```powershell
python .\examples\run_reactivation_test.py
```

Saidas:

- `artifacts/stress/reactivation_results.json`
- `artifacts/stress/reactivation_report.md`

## Testar contexto bidirecional

```powershell
python .\examples\run_bidirectional_test.py
```

Saidas:

- `artifacts/stress/bidirectional_results.json`
- `artifacts/stress/bidirectional_report.md`

## Testar julgador de contextos

```powershell
python .\examples\run_context_judge_test.py
```

Saidas:

- `artifacts/stress/context_judge_results.json`
- `artifacts/stress/context_judge_report.md`

O `ContextJudge` calcula o Semantic Sustainment Score por contexto e retorna decisao
operacional: `promote`, `compact`, `audit` ou `discard`.

O exemplo usa o perfil parametrizado `llm_continuous`, calibrado para liberar apenas
`promote`/`compact` para uso ativo, manter incerteza em `audit` e descartar abaixo do
limiar operacional.

## Estado

Esta primeira versao nao chama LLM externa. Ela usa heuristicas locais para validar:

- vazao contextual;
- compressao estimada de tokens;
- sustentacao semantica;
- leveza estrutural;
- output multi-fluxo.
