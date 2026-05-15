# Arquitetura NoemaKernel

## Leitura tecnica

A arquitetura proposta funciona como uma camada intermediaria entre entradas humanas/multimodais
e uma LLM. Essa camada nao substitui a LLM: ela prepara, filtra, pesa, resume e audita o
contexto antes e depois da inferencia.

## Componentes

### 0. Bankmap

Motor de orquestracao de fluxos contextuais. Recebe `N` contextos, preserva suas
fronteiras logicas, calcula relevancia/conflito e produz um pacote unico de inferencia.

O Bankmap pode usar contexto regressivo como metrica interna: parte do contexto colapsado,
do objetivo ou do estado final, identifica contextos sustentadores e ancoras semanticas, e
remove camadas ate chegar ao contexto minimo sustentavel.

Na saida, separa a resposta da LLM em fluxos operacionais distintos:

- resposta ao usuario;
- memoria;
- noemas ativados;
- checagem de axiomas;
- audit trail;
- proximas acoes.

Esse componente e a base das metricas de reducao de tokens, reducao de chamadas e
separabilidade de output. Com o contexto regressivo, tambem passa a medir sustentacao
semantica e leveza estrutural.

### 1. Ingestao multimodal

Recebe texto, imagem, audio e sinais estruturados. Cada modalidade precisa de um adaptador:

- texto: parsing, segmentacao, entidades, topicos;
- imagem: OCR, descricao visual, embeddings visuais;
- audio: ASR, prosodia se aplicavel, transcricao;
- dados estruturados: schemas, tabelas, eventos e metadados.

### 2. Normalizador semantico

Converte sinais diferentes para uma representacao comparavel. Aqui os noemas sao extraidos
como focos semanticos/intencionais.

Saida esperada:

```json
{
  "noemas": [
    {
      "id": "n_relax_banho",
      "label": "banho como pausa reflexiva",
      "confidence": 0.82,
      "source": ["texto"],
      "intent": "convivio_reflexivo"
    }
  ]
}
```

### 3. Modulo de axiomas

Armazena regras e pressupostos. Para virar sistema executavel, cada axioma deve ter:

- identificador;
- descricao humana;
- tipo: seguranca, estilo, epistemologia, privacidade, tarefa;
- prioridade;
- condicao de ativacao;
- criterio de violacao;
- acao: injetar no prompt, filtrar, pedir confirmacao, bloquear, reescrever ou auditar.

### 4. Bootloader / orquestrador

Monta o pacote de contexto para a LLM:

- objetivo da interacao;
- resumo multimodal;
- noemas ativos;
- axiomas ativos;
- memoria relevante;
- modo conversacional;
- politicas de intervencao;
- formato de resposta;
- campos de auditoria.

### 5. LLM final

Recebe o pacote ja organizado. A LLM deve responder com conteudo e, quando necessario, com
metadados de raciocinio operacional auditavel, sem expor cadeia interna sensivel.

### 6. Monitoramento e realimentacao

Valida a resposta contra os axiomas, mede alinhamento semantico e registra quais noemas
foram usados.

## Extensao: LLM de convivio

A segunda parte do arquivo amplia a arquitetura para uma LLM que convive com o usuario.
O nucleo deixa de ser apenas resolver tarefas e passa a incluir:

- sensibilidade ao momento;
- intervencoes nao intrusivas;
- micro-reflexoes;
- memoria episodica controlada;
- modos de conversa;
- humildade epistemica;
- privacidade e comandos de esquecer.

## Contratos ainda ausentes

- schema oficial de noema;
- schema oficial de axioma;
- schema oficial de contexto Bankmap;
- formato estruturado de output multi-fluxo;
- formato de memoria;
- API do bootloader;
- politica de quando intervir;
- modelo de permissao para memoria;
- criterio objetivo de sucesso;
- dataset de avaliacao;
- arquitetura de persistencia;
- escolha entre modelos locais, remotos ou hibridos.
