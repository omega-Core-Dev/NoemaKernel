# Integracao OpenAI / GPT

## Decisao

Foi adicionada uma integracao opcional com a OpenAI Responses API para testar o mesmo
prompt compacto do Bankmap em GPT.

## Arquivos

- `noemakernel/openai_api.py`: cliente REST sem dependencias externas.
- `examples/run_openai_bankmap.py`: gera o pacote Bankmap, chama OpenAI e valida o output.

## Configuracao

No `local_api_key.py`:

```python
OPENAI_API_KEY = "sua-chave"
OPENAI_MODEL = "gpt-5.4-mini"
OPENAI_MAX_OUTPUT_TOKENS = 2048
OPENAI_TIMEOUT_SECONDS = 180
```

## Comando

```powershell
python .\examples\run_openai_bankmap.py
```

## Saidas

- `artifacts/openai/bankmap_prompt.md`
- `artifacts/openai/openai_response.json`
- `artifacts/openai/validation.json`
