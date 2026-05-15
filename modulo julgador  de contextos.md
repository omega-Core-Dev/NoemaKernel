Implemente um módulo chamado ContextJudge para o Bankmap.

Objetivo:
Avaliar cada bloco de contexto C_i em relação a uma pergunta Q e ao estado atual do sistema S, retornando um score entre 0 e 1 e uma decisão operacional.

Referência conceitual:
A métrica segue a ideia de contextual relevancy usada em avaliação de RAG: medir se um contexto recuperado é útil/relevante para a pergunta antes de usá-lo na geração. Também deve ser auditável, retornando cada termo do cálculo separadamente.

Entradas:
- context_id: string
- context_text: string
- query: string
- system_state: object
- metrics: object com valores normalizados entre 0 e 1:
  - relevance
  - coherence
  - confidence
  - recency
  - semantic_power
  - redundancy_penalty
  - noise_penalty
  - contradiction_penalty

Fórmula:
score = clip(
  wr*relevance +
  wk*coherence +
  wf*confidence +
  wt*recency +
  wp*semantic_power -
  wred*redundancy_penalty -
  wnoise*noise_penalty -
  wcon*contradiction_penalty,
  0,
  1
)

Pesos padrão:
- wr = 0.30
- wk = 0.25
- wf = 0.15
- wt = 0.10
- wp = 0.20
- wred = 0.10
- wnoise = 0.15
- wcon = 0.25

Decisão:
- score >= 0.85 => promote
- score >= 0.60 => compact
- score >= 0.35 => audit
- score < 0.35 => discard

Saída obrigatória:
{
  "context_id": "...",
  "judge_score": 0.0,
  "decision": "promote | compact | audit | discard",
  "color_state": "green | yellow_green | yellow | red",
  "terms": {
    "relevance": 0.0,
    "coherence": 0.0,
    "confidence": 0.0,
    "recency": 0.0,
    "semantic_power": 0.0,
    "redundancy_penalty": 0.0,
    "noise_penalty": 0.0,
    "contradiction_penalty": 0.0
  },
  "weighted_terms": {
    "relevance": 0.0,
    "coherence": 0.0,
    "confidence": 0.0,
    "recency": 0.0,
    "semantic_power": 0.0,
    "redundancy_penalty": 0.0,
    "noise_penalty": 0.0,
    "contradiction_penalty": 0.0
  },
  "audit_reason": "...",
  "repair_instruction": "..."
}

Regras:
1. Todos os valores devem ser normalizados entre 0 e 1.
2. O score final deve sempre ser limitado com clip(0, 1).
3. Redundância, ruído e contradição devem ser penalidades separadas.
4. O módulo não deve gerar resposta ao usuário; ele apenas julga contexto.
5. A saída deve ser JSON serializável.
6. O módulo precisa aceitar pesos customizados, mas usar os pesos padrão se nenhum peso for informado.
7. Deve incluir testes unitários para:
   - contexto altamente relevante
   - contexto redundante
   - contexto contraditório
   - contexto ruidoso
   - contexto descartável
   - score acima de 1 sendo cortado para 1
   - score abaixo de 0 sendo cortado para 0

Nome sugerido da métrica:
Semantic Sustainment Score.

Função esperada:
judge_context(context_item, query, system_state, weights=None) -> JudgeResult