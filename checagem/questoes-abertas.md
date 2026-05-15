# Questoes Abertas

Estas perguntas nao bloqueiam a documentacao, mas bloqueiam uma implementacao precisa.

## Produto e objetivo

1. O NoemaKernel sera uma biblioteca, um app local, um agente pessoal ou uma camada de API?
2. O foco inicial e pesquisa, produto de uso pessoal ou demonstracao publica?
3. A prioridade e alinhamento tecnico, convivencia pessoal ou os dois em equilibrio?

## Arquitetura

1. O bootloader sera executado antes de toda chamada de LLM ou apenas em modos especificos?
2. Os axiomas devem ser regras duras, preferencias flexiveis ou ambos?
3. O sistema deve poder bloquear resposta ou apenas reescrever/recalibrar?
4. O audit trail sera visivel ao usuario final ou apenas log tecnico?
5. O Bankmap sera o componente principal antes do bootloader ou parte interna dele?
6. Qual limite maximo de contextos deve entrar em uma unica inferencia?
7. Qual perda semantica e aceitavel na compressao de tokens?

## Bankmap

1. O contexto final sera montado por resumo, ranking, grafo, clustering ou combinacao desses metodos?
2. Como preservar a separacao de contextos depois da fusao?
3. Qual schema obrigatorio a LLM deve devolver para separar os outputs?
4. O que acontece se a LLM misturar os fluxos de saida?
5. Quais metricas validam a primeira versao: tokens, chamadas, qualidade, latencia ou separabilidade?

## Contexto regressivo

1. A ancora minima sera uma entidade, proposicao, noema, relacao ou trecho textual?
2. Como medir a carga contextual de uma ancora na estabilidade do contexto?
3. A remocao de contextos de baixa carga sera automatica ou supervisionada no MVP?
4. Qual sustentacao semantica minima valida uma compressao?
5. O sistema deve registrar as ancoras e contextos descartados para auditoria?

## Noemas

1. Um noema sera uma entidade, uma intencao, um topico, uma memoria ou um objeto proprio?
2. Noemas terao hierarquia/ontologia?
3. Como resolver conflito entre noemas ativos?
4. Qual threshold minimo de confianca ativa um noema?

## Memoria e privacidade

1. Memoria sera local por padrao?
2. Quais eventos podem ser lembrados sem confirmacao?
3. Todo item de memoria tera TTL?
4. O usuario tera comandos padrao como `lembrar`, `esquecer`, `privado` e `listar memoria`?

## MVP

1. Qual caso de uso inicial sera testado?
2. Qual LLM final sera usada?
3. Havera modelos locais para embeddings?
4. O primeiro prototipo precisa de interface visual ou pode ser CLI/notebook?

## Avaliacao

1. O que conta como resposta melhor?
2. Quem rotula os casos de teste?
3. Qual baseline sera usado?
4. Qual ganho minimo valida a arquitetura?
