# Integracao Gemma API

## Decisao

Foi adicionada uma integracao opcional com a API do Google/Gemini para testar o prompt
compacto do Bankmap em um modelo Gemma.

## Arquivos

- `noemakernel/gemma_api.py`: cliente REST sem dependencias externas.
- `examples/run_gemma_bankmap.py`: gera o pacote Bankmap, chama a API e valida o output.

## Variaveis de ambiente

```powershell
$env:GEMINI_API_KEY="sua-chave"
$env:GEMMA_MODEL="gemma-4-31b-it"
```

Tambem aceita `GOOGLE_API_KEY` se `GEMINI_API_KEY` nao estiver definida.

## Arquivo .env

Tambem foi criado `.env.example`. Para usar:

```powershell
Copy-Item .env.example .env
notepad .env
python .\examples\run_gemma_bankmap.py
```

O arquivo `.env` real esta listado no `.gitignore`.

## Arquivo Python local

Tambem foi criado `local_api_key.example.py`. Para quem prefere setar direto em `.py`:

```powershell
Copy-Item local_api_key.example.py local_api_key.py
notepad local_api_key.py
python .\examples\run_gemma_bankmap.py
```

O arquivo `local_api_key.py` real esta listado no `.gitignore`.

Se a chamada demorar, defina no arquivo local:

```python
GEMMA_TIMEOUT_SECONDS = 180
```

## Observacao tecnica

O nome do modelo fica configuravel porque os IDs disponiveis podem variar por conta, regiao
ou canal de release. A pagina oficial da Gemma 4 informa disponibilidade em Google AI Studio
e modelos 26B/31B, mas o ID exato usado na API deve ser confirmado no ambiente do usuario.

## Comando

```powershell
python .\examples\run_gemma_bankmap.py
```

## Saidas

O script grava:

- `artifacts/gemma/bankmap_prompt.md`
- `artifacts/gemma/gemma_response.json`
- `artifacts/gemma/validation.json`
