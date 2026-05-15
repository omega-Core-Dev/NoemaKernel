# Contributing

Thanks for considering contributing to NoemaKernel.

This project is an early prototype, so contributions should keep changes small,
auditable and easy to test.

## Local setup

```powershell
python -m unittest discover -s tests
```

Optional API tests use local credentials. Do not commit real keys.

Use one of:

```powershell
Copy-Item .env.example .env
Copy-Item local_api_key.example.py local_api_key.py
```

Both `.env` and `local_api_key.py` are ignored by Git.

## Pull request guidelines

- Keep public claims conservative.
- Do not present heuristic metrics as benchmarks.
- Add or update tests for behavior changes.
- Keep generated API responses and private artifacts out of commits.
- Prefer dependency-free stdlib code unless a dependency clearly improves the
  core architecture.

## Security

Never open a pull request containing API keys, tokens, private prompts, private
datasets or provider response payloads that may include sensitive information.
