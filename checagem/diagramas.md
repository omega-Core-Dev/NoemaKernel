# Diagramas

Os diagramas abaixo usam Mermaid e podem ser renderizados em ferramentas compativeis com Markdown.

## Arquitetura em camadas

```mermaid
flowchart TD
    U[Usuario / Ambiente] --> I[Ingestao multimodal]
    I --> T[Texto]
    I --> IMG[Imagem / OCR]
    I --> A[Audio / ASR]
    I --> D[Dados estruturados]

    T --> N[Normalizacao semantica]
    IMG --> N
    A --> N
    D --> N

    N --> BM[Bankmap / fluxos contextuais]
    BM --> DR[Contexto regressivo / ancoras]
    DR --> CJ[ContextJudge / Semantic Sustainment Score]
    CJ --> NO[Extrator de noemas]
    AX[Repositorio de axiomas] --> B[Bootloader organizacional]
    NO --> B
    CJ --> B
    DR --> B
    MEM[Memoria episodica leve] --> B
    MODE[Modo de convivio] --> B

    B --> CTX[Pacote de contexto priorizado]
    CTX --> LLM[LLM final]
    LLM --> OUT[Output multi-fluxo]
    OUT --> R[Resposta ao usuario]
    OUT --> OM[Atualizacoes de memoria]
    OUT --> OA[Auditoria]
    OUT --> ON[Noemas ativados]
    OM --> MEM
    OA --> MON[Monitoramento e validacao]
    ON --> MON
    R --> MON
    MON --> AUD[Audit trail]
    MON --> MEM
    MON --> B
```

## Fluxo de inferencia

```mermaid
sequenceDiagram
    participant U as Usuario
    participant IN as Ingestao
    participant NS as Normalizador
    participant BO as Bootloader
    participant L as LLM
    participant MO as Monitor
    participant M as Memoria

    U->>IN: Entrada textual/multimodal
    IN->>NS: Sinais preprocessados
    NS->>BO: Noemas, entidades, intencoes
    M->>BO: Memorias relevantes
    BO->>BO: Julga contextos com ContextJudge
    BO->>BO: Seleciona axiomas e modo
    BO->>L: Prompt/contexto priorizado
    L->>MO: Resposta candidata
    MO->>MO: Checa axiomas e alinhamento
    MO->>M: Registra evento se permitido
    MO->>U: Resposta final + auditabilidade quando util
```

## Modelo conceitual de dados

```mermaid
erDiagram
    INTERACAO ||--o{ NOEMA : extrai
    INTERACAO ||--o{ EVENTO_MEMORIA : pode_gerar
    NOEMA }o--o{ AXIOMA : ativa
    BOOTLOADER ||--o{ AXIOMA : injeta
    BOOTLOADER ||--o{ NOEMA : prioriza
    BOOTLOADER ||--o{ EVENTO_MEMORIA : consulta
    RESPOSTA ||--|| AUDIT_TRAIL : possui
    AUDIT_TRAIL }o--o{ AXIOMA : registra
    AUDIT_TRAIL }o--o{ NOEMA : registra

    INTERACAO {
        string id
        string modalidade
        datetime criada_em
        string modo
    }

    NOEMA {
        string id
        string label
        float confianca
        string intencao
    }

    AXIOMA {
        string id
        string tipo
        int prioridade
        string acao
    }

    EVENTO_MEMORIA {
        string id
        string conteudo
        datetime expira_em
        string permissao
    }

    AUDIT_TRAIL {
        string id
        string resposta_id
        string avaliacao
    }
```

## Loop de avaliacao

```mermaid
flowchart LR
    BASE[Fluxo LLM usual] --> A[Bateria de testes]
    NOEMA[Fluxo com NoemaBoot] --> A
    A --> M1[Coerencia semantica]
    A --> M2[Violacoes de axiomas]
    A --> M3[Tokens e custo]
    A --> M4[Latencia]
    A --> M5[Aceitacao de intervencao]
    M1 --> COMP[Comparacao A/B]
    M2 --> COMP
    M3 --> COMP
    M4 --> COMP
    M5 --> COMP
    COMP --> AJUSTE[Ajuste de thresholds, axiomas e modos]
    AJUSTE --> NOEMA
```
