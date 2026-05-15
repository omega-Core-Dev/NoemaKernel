# Contexto Bidirecional

## Resultado

- Ancoras avaliadas: 40
- Estabilidade bidirecional: 72.50%
- Score regressivo medio: 100.00%
- Score progressivo medio: 45.11%
- Score bidirecional medio: 75.30%

## Top ancoras bidirecionais

- `ctx_012` bidirectional bi=95.50% reg=100.00% prog=90.00%: Repeticao:
- `ctx_001` bidirectional bi=95.00% reg=100.00% prog=88.89%: A reducao de tokens precisa preservar sentido e separar o output em fluxos.
- `ctx_006` bidirectional bi=91.56% reg=100.00% prog=81.25%: compressao, cobertura, sustentacao semantica, auditabilidade e separabilidade.
- `ctx_008` bidirectional bi=90.36% reg=100.00% prog=78.57%: Ambiguidade fertil nao deve ser removida cedo demais.
- `ctx_004` bidirectional bi=90.36% reg=100.00% prog=78.57%: Nao basta cortar firula textual.
- `ctx_002` bidirectional bi=90.00% reg=100.00% prog=77.78%: O final pode ser o comeco quando o objetivo e entender o que sustenta o todo.
- `ctx_007` bidirectional bi=88.16% reg=100.00% prog=73.68%: Ela transforma contexto bruto em estrutura auditavel com ancoras, scores, decisoes e trilha.
- `ctx_005` bidirectional bi=87.50% reg=100.00% prog=72.22%: Se algum contexto essencial desaparecer, a compressao vira perda de entendimento.

## Leitura

Contexto regressivo mede sustentacao pelo que veio antes e pelo objetivo.
Contexto progressivo mede se a ancora abre caminho para contextos seguintes.
Estabilidade bidirecional mede quantas ancoras conseguem operar nos dois sentidos.
