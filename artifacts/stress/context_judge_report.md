# ContextJudge e Potencializacao Progressiva

Perfil: `llm_continuous`

## Tabela

| Contextos | Sustainment | Poder semantico | Potencial progressivo | Ativos | Auditoria | Descarte | Potencial ativo | Prog. bidirecional |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 10 | 50.45% | 35.16% | 18.64% | 10.00% | 60.00% | 30.00% | 34.57% | 24.62% |
| 20 | 50.17% | 41.39% | 22.73% | 25.00% | 35.00% | 40.00% | 43.16% | 39.62% |
| 40 | 50.83% | 43.88% | 24.40% | 22.50% | 42.50% | 35.00% | 45.82% | 45.11% |

## Top contextos progressivos

- `ctx_004` promote score=83.29% power=81.73% potential=68.07%
- `ctx_001` compact score=73.80% power=75.65% potential=55.83%
- `ctx_006` compact score=68.56% power=75.29% potential=51.62%
- `ctx_007` compact score=66.05% power=67.30% potential=44.45%
- `ctx_005` compact score=66.92% power=65.61% potential=43.91%
- `ctx_021` compact score=64.35% power=59.55% potential=38.32%
- `ctx_003` compact score=61.91% power=60.71% potential=37.59%
- `ctx_002` compact score=62.06% power=59.72% potential=37.06%

## Leitura

Semantic Sustainment Score julga se um contexto deve entrar no fluxo.
Potencializacao progressiva combina o score do julgador com o poder semantico inferido contra contextos futuros.
Ativos mede apenas contextos liberados para uso operacional: promote ou compact.
Auditoria e uma fila de quarentena, nao retencao para geracao.
