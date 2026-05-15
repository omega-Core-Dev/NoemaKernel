# Metrica de Contexto Regressivo

Fonte analisada: `Arquitetura de Dados.txt`

## Leitura

A metrica apresentada descreve um modo de compreensao que parte do estado final complexo,
ou "colapsado", e retorna ate os contextos que sustentam sua compreensao.

Em vez de perguntar apenas "como construir isso passo a passo?", ela pergunta:

> Se eu parto do final, quais contextos anteriores sustentam o sentido?

Essa abordagem e relevante para o NoemaKernel porque o Bankmap pretende comprimir muitos
contextos em uma unica inferencia. Compressao sem criterio pode apagar sentido. O contexto
regressivo oferece um criterio para saber o que pode ser removido sem quebrar a estrutura
semantica.

## Conceitos extraidos

| Conceito | Definicao operacional | Encaixe no NoemaKernel |
| --- | --- | --- |
| Colapso | Estado final de alta complexidade. | Conjunto bruto de contextos, memorias, axiomas e sinais antes da compressao. |
| Funcao regressiva | Partir do final complexo para descobrir a base. | Metodo de analise do Bankmap antes de montar a inferencia. |
| Contexto sustentador | Parte do contexto que sustenta a compreensao do estado final. | Unidade funcional que precisa existir no prompt final ou ser reconstruivel por ancora. |
| Encaixe | Sincronizacao entre etapas/contextos. | Relacao entre noemas, axiomas e contextos que mantem coerencia. |
| Leveza | Sustentacao minima viavel. | Contexto final com menos tokens, mas sem perda semantica critica. |
| Ancora semantica | Palavra, frase ou bloco curto com alto poder de reconstrucao contextual. | Permite comprimir sem perder o sentido principal. |

## Metrica proposta

### Sustentacao semantica

Mede quanto da estrutura de sentido permanece depois da retirada de contexto.

```text
sustentacao_semantica = contextos_sustentadores_preservados / contextos_sustentadores_identificados
```

Exemplo:

```text
12 contextos sustentadores identificados
11 preservados no contexto final
sustentacao_semantica = 91.6%
```

### Leveza estrutural

Mede o quanto o sistema ficou mais leve sem perder sustentacao.

```text
leveza_estrutural = compressao_tokens * sustentacao_semantica
```

Exemplo:

```text
compressao_tokens = 65%
sustentacao_semantica = 91.6%
leveza_estrutural = 59.5%
```

Essa metrica evita comemorar compressao agressiva que destruiu o significado.

### Carga contextual

Mede a importancia de cada trecho, frase ou bloco para a estabilidade do contexto.

```text
carga_contextual = impacto_da_remocao * centralidade_semantica
```

Uso pratico:

- contexto com carga alta: nao remover;
- contexto com carga media: resumir;
- contexto com carga baixa: descartar ou arquivar no audit trail.

### Encaixe contextual

Mede se os contextos preservados ainda se conectam de forma coerente.

```text
encaixe_contextual = relacoes_validas_preservadas / relacoes_essenciais
```

Essa metrica e importante porque um resumo pode preservar varios conceitos isolados,
mas perder a relacao entre eles.

## Como encaixa no Bankmap

O Bankmap ganha duas etapas regressivas:

```text
1. Receber N contextos brutos.
2. Identificar o estado colapsado: tudo que esta competindo por atencao.
3. Identificar contextos sustentadores e ancoras semanticas.
4. Medir carga contextual de cada parte.
5. Preservar, resumir ou descartar.
6. Montar contexto leve.
7. Enviar uma inferencia.
8. Verificar se a saida preservou sustentacao e encaixe.
```

## Por que isso e forte

A metrica adiciona uma pergunta que falta em muitas tecnicas de reducao de tokens:

> O que e removivel sem destruir a compreensao?

Isso transforma compressao em analise estrutural. Para uma arquitetura de LLM, esse ponto e
importante porque o objetivo nao e apenas economizar token. O objetivo e reduzir custo sem
perder os elementos que sustentam uma resposta correta.

## Risco

O principal risco e tratar "contexto sustentador" como algo subjetivo demais.

Para virar codigo, o projeto precisa definir como detectar contextos sustentadores:

- por entidades;
- por proposicoes;
- por noemas;
- por axiomas ativados;
- por dependencias causais;
- por embeddings e centralidade em grafo;
- ou por uma combinacao desses criterios.

## Encaixe recomendado

Esta metrica deve ficar entre o Bankmap e o Bootloader.

```text
Contextos brutos
-> Bankmap
-> Contexto regressivo
-> Contexto minimo sustentavel
-> Bootloader
-> LLM
-> Output multi-fluxo
```

No MVP, a versao mais simples pode marcar manualmente os contextos sustentadores em 20 a 30
casos de teste e comparar:

- prompt bruto;
- prompt comprimido simples;
- prompt comprimido com contexto regressivo.

Se a terceira opcao reduzir tokens mantendo maior qualidade, a metrica valida sua utilidade.
