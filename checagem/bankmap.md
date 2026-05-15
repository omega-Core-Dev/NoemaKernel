# Bankmap

## Definicao atual

O Bankmap e o motor de orquestracao de fluxos contextuais do NoemaKernel.
Ele organiza multiplos contextos de entrada para que possam ser tratados em uma unica
inferencia de LLM e, depois, separa o output em fluxos distintos de resposta, memoria,
auditoria e atualizacao semantica.

Definicao curta:

> Bankmap = motor de compressao, roteamento e expansao contextual para LLMs.

## Hipotese central

Em vez de executar uma chamada para cada contexto, o sistema agrupa `N` contextos,
calcula relevancia, conflitos, axiomas ativos e relacoes semanticas, e monta um pacote
unico de inferencia.

Depois da resposta, o sistema decompoe a saida em partes operacionais separadas.

```text
C1 + C2 + C3 + ... + Cn
        |
        v
Bankmap: normaliza, pesa, agrupa, reduz ruido, resolve conflito
        |
        v
Uma chamada de LLM
        |
        v
R_usuario + R_memoria + R_auditoria + R_noema + R_acao
```

## Objetivo pratico

Reduzir tokens e chamadas sem perder separacao logica dos contextos.

O ganho esperado nao vem apenas de resumir texto. Ele vem de:

- remover repeticao entre contextos;
- fundir contextos equivalentes;
- manter fronteiras entre fluxos;
- enviar para a LLM apenas o necessario para a inferencia atual;
- exigir que a resposta volte separada por destino operacional.

## Relacao com contexto regressivo

A metrica de contexto regressivo entra como criterio de qualidade da compressao.
O Bankmap nao deve apenas reduzir tokens; ele deve remover ou resumir contextos de baixa
carga sem derrubar a sustentacao semantica do conjunto.

```text
contexto colapsado -> ancoras semanticas -> carga contextual -> contexto minimo sustentavel
```

Isso cria uma diferenca importante:

- compressao comum: reduz tamanho;
- Bankmap com contexto regressivo: reduz tamanho preservando estrutura.

## Entrada

Cada contexto de entrada deve ser tratado como um item independente antes da fusao:

```json
{
  "context_id": "ctx_001",
  "source": "usuario",
  "type": "mensagem",
  "content": "tomar um belo banho",
  "weight": 0.74,
  "noemas": ["pausa_reflexiva", "convivio_sutil"],
  "axioms": ["nao_intrusao", "micro_reflexao"],
  "ttl": "session"
}
```

## Saida

A LLM deve responder em blocos separados por fluxo:

```json
{
  "user_response": "Resposta final ao usuario.",
  "memory_updates": [],
  "activated_noemas": [],
  "axiom_checks": [],
  "audit_trail": [],
  "next_actions": []
}
```

Isso permite que uma unica inferencia alimente varios destinos sem misturar tudo em uma
resposta textual plana.

## Metricas principais

### Vazao contextual

Mede quantos contextos foram tratados por chamada de LLM.

```text
vazao_contextual = contextos_processados / chamadas_llm
```

Exemplo:

```text
8 contextos / 1 chamada = vazao 8.0
```

### Reducao de chamadas

Compara o fluxo Bankmap contra o fluxo linear.

```text
reducao_chamadas = 1 - (chamadas_bankmap / chamadas_baseline)
```

Exemplo:

```text
baseline: 8 chamadas
bankmap: 1 chamada
reducao = 87.5%
```

### Compressao de tokens

Mede a reducao de tokens de entrada depois da fusao contextual.

```text
compressao_tokens = 1 - (tokens_contexto_final / tokens_contextos_brutos)
```

Exemplo:

```text
contextos brutos: 12000 tokens
contexto final: 4200 tokens
compressao = 65%
```

### Sustentacao semantica

Mede quanto dos contextos sustentadores sobreviveu a compressao.

```text
sustentacao_semantica = contextos_sustentadores_preservados / contextos_sustentadores_identificados
```

Essa metrica impede que o sistema reduza tokens destruindo o significado.

### Leveza estrutural

Combina reducao de tokens com preservacao de sentido.

```text
leveza_estrutural = compressao_tokens * sustentacao_semantica
```

### Separabilidade de output

Mede se a saida voltou corretamente dividida em fluxos operacionais.

```text
separabilidade_output = blocos_validos / blocos_esperados
```

Exemplo:

```text
5 blocos validos / 6 blocos esperados = 83.3%
```

### Aproveitamento contextual

Mede quantos contextos disponiveis foram realmente usados.

```text
aproveitamento_contextual = contextos_usados / contextos_disponiveis
```

Essa metrica ajuda a detectar tanto excesso de descarte quanto excesso de inclusao.

## Funcoes minimas do motor

```text
add_context(context)
extract_noemas(context)
score_relevance(contexts, goal)
detect_conflicts(contexts)
merge_contexts(contexts)
build_inference_packet(contexts, axioms, noemas)
parse_output(response)
route_output_blocks(parsed_response)
audit_flow(input_contexts, output_blocks)
```

## MVP recomendado

Primeiro teste deve ser textual e local:

1. Receber uma lista de contextos textuais.
2. Atribuir `context_id`, peso, noemas e axiomas.
3. Gerar um pacote unico para uma LLM.
4. Forcar resposta em JSON com blocos separados.
5. Medir tokens brutos versus tokens finais.
6. Medir quantos outputs operacionais foram gerados corretamente.

## Criterio de viabilidade

O Bankmap comeca a fazer sentido se, em testes pequenos, atingir:

- reducao de tokens de entrada acima de 30%;
- reducao de chamadas acima de 50% em cenarios multi-contexto;
- separabilidade de output acima de 90%;
- perda semantica baixa, validada por revisao humana ou score de similaridade.

## Risco principal

Compressao demais pode apagar sinais importantes.

Por isso o Bankmap precisa registrar o que foi descartado, o que foi fundido e por que
cada contexto entrou ou saiu da inferencia final.
