# Checagem Minuciosa dos Dados

## Dados explicitamente presentes

- Arquitetura em camadas para bootloader organizacional.
- Bankmap como motor de orquestracao de fluxos contextuais.
- Metrica de contexto regressivo para encontrar sustentacao minima viavel.
- Definicoes de sentido multimodal, axiomas e noema.
- Mecanismos de implementacao possiveis.
- Metricas de avaliacao.
- Plano de MVP em quatro passos.
- Avaliacao qualitativa da arquitetura com nota 8/10.
- Estimativas percentuais de impacto.
- Evolucao conceitual para LLM de convivio.
- Componentes de convivencia: estado situacional, estilo conversacional, memoria leve,
  prompts de micro-reflexao e guardrails de privacidade.

## Dados inferidos

- O projeto quer ser uma camada kernel/orquestradora acima de modelos LLM, nao um modelo base.
- O termo `NoemaKernel` sugere um nucleo semantico para organizar memoria, axiomas e interacoes.
- O Bankmap sugere que o nucleo do ganho esta em tratar muitos contextos em uma inferencia e separar muitos outputs da mesma resposta.
- O contexto regressivo sugere que a reducao de tokens deve ser avaliada pela preservacao dos contextos sustentadores, nao apenas pelo tamanho final.
- O MVP mais natural e textual primeiro, com simulacao multimodal por metadados ou descricoes,
  antes de integrar OCR/ASR/modelos visuais reais.
- A parte de convivencia e tao importante quanto a parte de alinhamento tecnico.

## Pontos consistentes

- A separacao entre ingestao, normalizacao, axiomas, bootloader, LLM e monitoramento e coerente.
- A ideia de audit trail combina bem com axiomas e noemas.
- Testes A/B e ablacoes sao a forma correta de validar o ganho real.
- Memoria com TTL e comandos de lembrar/esquecer reduz risco de comportamento invasivo.
- Modos de convivencia ajudam a controlar tom, tamanho da resposta e momento de intervencao.

## Pontos fragiles ou ainda nao verificaveis

| Ponto | Risco | O que falta |
| --- | --- | --- |
| Percentuais de ganho | Podem soar como promessa sem base experimental. | Dataset, baseline, repeticoes e metricas. |
| Noema | Conceito forte, mas ainda abstrato. | Schema formal, exemplos e extrator. |
| Axiomas | Podem virar prompt solto se nao forem executaveis. | DSL simples ou formato JSON validavel. |
| Multimodalidade | Pode aumentar custo e latencia. | Escopo de modalidades para MVP. |
| Memoria de convivencia | Pode parecer invasiva se mal controlada. | Permissoes, TTL, tela/log de memoria e comandos. |
| Intervencao proativa | Pode ser percebida como interrupcao. | Politica de intervencao e score de oportunidade. |
| Bankmap | Pode comprimir demais e perder sinal semantico. | Log do que entrou, saiu, foi fundido e descartado. |
| Contexto regressivo | Pode ficar subjetivo sem criterio formal de ancora/contexto sustentador. | Definir ancora como noema, proposicao, entidade, relacao ou frase de alta carga. |

## Checagem de arquitetura frente ao fluxo usual de LLM

Fluxo usual:

1. Usuario envia prompt.
2. Sistema injeta instrucoes gerais.
3. LLM responde.
4. Opcionalmente ha ferramentas, memoria ou filtros.

Fluxo proposto:

1. Entrada e interpretada por modalidade.
2. Bankmap agrupa multiplos contextos e preserva suas fronteiras.
3. Contexto regressivo identifica ancoras/contextos sustentadores e remove camadas de baixa carga.
4. Sistema extrai noemas e contexto intencional.
5. Axiomas relevantes sao selecionados.
6. Memoria permitida e consultada.
7. Bootloader monta contexto priorizado para uma unica inferencia.
8. LLM responde em blocos separados por fluxo.
9. Monitor valida e registra audit trail.

Ganho esperado: maior controle semantico e auditabilidade.
Custo esperado: mais engenharia, mais pontos de falha e necessidade de avaliacao continua.

## Melhor MVP recomendado

Para reduzir risco, o primeiro MVP deve ser textual:

- entrada: mensagens de conversa;
- noemas: extraidos por classificacao simples + embeddings;
- contextos sustentadores: marcados manualmente no inicio para validar sustentacao semantica;
- axiomas: JSON com regras avaliaveis;
- memoria: arquivo local JSON com TTL e permissao;
- bootloader: template de prompt;
- output: JSON separado por resposta, memoria, noemas, axiomas, auditoria e proximas acoes;
- monitor: checagem de axiomas + log de noemas usados;
- avaliacao: comparacao com e sem bootloader em 30 a 50 casos.

Depois disso, adicionar imagem/audio.
