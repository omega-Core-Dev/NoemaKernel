# Contexto Regressivo e Ancoras Semanticas

## Ideia central

Algumas frases, paragrafos e narrativas so revelam seu sentido completo no final. O final
funciona como chave de leitura: ele reorganiza retroativamente o peso das partes anteriores.

Para quem escreve, o final e chegada. Para quem analisa, o final pode ser ponto de partida.

No NoemaKernel, isso vira uma estrategia:

```text
estado final / pergunta / objetivo
-> busca regressiva dos contextos que sustentam esse estado
-> selecao das ancoras semanticas de maior peso
-> montagem de contexto minimo sustentavel
-> inferencia unica
```

## O que muda

A metafora de "tijolos" e limitada. O conceito mais correto e:

- contexto sustentador;
- ancora semantica;
- carga contextual;
- saliencia regressiva.

Nao se trata de quebrar tudo em pecas minimas fisicas. Trata-se de descobrir quais partes
do contexto sustentam a compreensao do todo.

## Frases curtas que montam contexto inteiro

Existem expressoes pequenas que carregam uma carga contextual muito alta.

```text
"tomar um belo banho"
"depois de tudo"
"era isso"
"nao era sobre dinheiro"
"ele sabia"
```

Essas frases podem ativar estado emocional, relacao temporal, expectativa, tensao
narrativa, intencao implicita e contraste com informacao anterior.

Para o Bankmap, isso significa que tamanho em tokens nao e igual a importancia. Uma frase
curta pode ter mais peso que um paragrafo longo.

## Metrica: carga contextual

```text
carga_contextual =
centralidade_semantica
+ poder_de_desambiguacao
+ dependencia_do_objetivo
+ capacidade_de_reconstrucao
+ risco_de_perda
- redundancia
```

Interpretacao:

- carga alta: preservar literalmente ou quase literalmente;
- carga media: resumir mantendo relacoes;
- carga baixa: descartar ou arquivar;
- carga ambigua fertil: preservar como noema aberto.

## Metrica: saliencia regressiva

Mede quanto um trecho ganha importancia depois que o final/objetivo e conhecido.

```text
saliencia_regressiva =
peso_do_trecho_dado_o_final - peso_do_trecho_sem_o_final
```

Se a diferenca for alta, o trecho era uma pista ou sustentador oculto.

## Metrica: capacidade de reconstrucao

Mede se uma ancora permite reconstruir o contexto suficiente para responder.

```text
capacidade_reconstrucao =
contexto_reconstruido_corretamente / contexto_necessario
```

Isso e proximo do insight: se o modelo identifica as palavras ou blocos de maior peso, ele
pode montar uma resposta adequada sem carregar todo o texto bruto.

## Encaixe no Bankmap

O Bankmap pode operar em dois movimentos.

Movimento progressivo:

```text
C1 -> C2 -> C3 -> Cn
```

Movimento regressivo:

```text
Cn / objetivo -> C3 -> C2 -> C1
```

O contexto final para a LLM deve preservar o que sobrevive aos dois movimentos:

```text
contexto_final =
ancoras_progressivas
+ ancoras_regressivas
+ restricoes
+ noemas_abertos
+ relacoes_essenciais
```

## Regra arquitetural

```text
Nao reduzir pelo tamanho.
Reduzir pela carga contextual.
Nao remover ambiguidade fertil.
Isolar ambiguidade improdutiva.
Preservar ancoras que permitem reconstruir o sentido.
```
