# Decifra

Camada de IA que traduz o relatório genético da Genera para linguagem que o paciente entende, sem perder a fidelidade ao documento original.

> Enterprise Challenge DASA · FIAP · Graduação em IA

> ⚠️ Projeto acadêmico com **dados sintéticos**. Não é produto, não é dispositivo médico e não substitui avaliação profissional. Ver [Governança](docs/governance.md).

---

## O problema

A Genera entrega informação genética de alto valor em PDFs longos, com linguagem técnica e tabelas densas. O paciente recebe e não consegue usar para decisão: não sabe o que é predisposição, confunde risco relativo com certeza, e não tem a quem perguntar às onze da noite.

A dor não é do exame. É da **interface** com o conhecimento que o exame produziu.

## O que o sistema faz

1. Lê o PDF do laudo e o transforma em dado estruturado, preservando a página de origem de cada achado
2. Indexa cada achado para busca semântica, isolado por paciente
3. Responde perguntas em linguagem simples, sempre citando de onde a resposta veio
4. Organiza tudo num painel com riscos, ancestralidade, características e farmacogenética
5. Recusa o que não pode responder, em vez de improvisar

O princípio que orienta tudo: **a IA não substitui o médico**. Ela apoia o entendimento e encaminha ao profissional.

## Como rodar

Pré-requisitos: Docker, [uv](https://docs.astral.sh/uv/), Node 20+ e pnpm.

```bash
# 1. Infraestrutura
docker compose up -d                  # Qdrant e Postgres

# 2. Configuração
cp .env.example .env                  # preencha OPENAI_API_KEY

# 3. Laudos sintéticos e ingestão
cd apps/api
uv sync
uv run python ../../scripts/generate_reports.py   # gera os PDFs
uv run python ../../scripts/ingest.py             # PDF → JSON → Qdrant

# 4. Backend
uv run uvicorn decifra.main:app --reload          # http://localhost:8000

# 5. Front, em outro terminal
cd apps/web && pnpm install && pnpm dev           # http://localhost:5173
```

O Postgres escuta em **5433** no host, para não colidir com instalações locais.

### Verificando a qualidade das respostas

```bash
cd apps/api
uv run pytest tests/                              # rápido, sem API
uv run python ../../scripts/run_golden.py         # 12 casos contra o agente real
```

O segundo gera [`docs/golden-cases.md`](docs/golden-cases.md) com as respostas na íntegra.

## Estrutura

```
decifra/
├── apps/
│   ├── api/                     FastAPI + LangChain
│   │   ├── src/decifra/
│   │   │   ├── shared/          llm, vectorstore, db
│   │   │   └── features/
│   │   │       ├── reports/     PDF → JSON → Qdrant, resumo automático
│   │   │       ├── chat/        agente, middleware, streaming
│   │   │       └── safety/      verificação de fronteira clínica
│   │   └── tests/
│   └── web/                     Vite + React + shadcn/ui
│       └── src/features/        dashboard, chat, report
├── data/reports/                inbox → processed, estruturados
├── docs/                        documentação técnica
├── scripts/                     geração de laudos, ingestão, avaliação
└── compose.yml
```

Colocação por feature, não por camada. Feature nova é pasta nova em `features/`; só sobe para `shared/` o que já tem dois consumidores reais.

## Stack

| Camada | Escolha | Por quê |
|---|---|---|
| Parsing | Docling | O laudo é tabela, e a coluna a que um valor pertence *é* o significado dele |
| Orquestração | LangChain + LangGraph 1.x | Middleware como ponto de inserção dos guardrails |
| LLM | OpenAI `gpt-5.6-terra` e `gpt-5.6-luna` | Terra para resposta fundamentada, Luna para classificação e resumo |
| Vetorial | Qdrant | Filtro por payload isola laudo por paciente |
| Relacional | Postgres | Memória de conversa via checkpointer do LangGraph |
| Front | Vite + React + shadcn/ui | O backend é FastAPI; SSR não teria uso e SEO é indesejado |

Justificativa completa de cada decisão em [Arquitetura](docs/architecture.md).

## Documentação

| Documento | Conteúdo |
|---|---|
| [Arquitetura de IA](docs/architecture.md) | Pipeline, RAG, escolha de modelo, chunking, streaming |
| [Governança e riscos](docs/governance.md) | LGPD, limites do agente, guardrails em camadas, política de falha |
| [Decisões de experiência](docs/ux-decisions.md) | Dashboard, comunicação de risco, UX do chat, acessibilidade |
| [Proveniência dos dados](docs/data-sources.md) | O que é real e o que é sintético nos laudos, com referências |
| [Testes de qualidade](docs/golden-cases.md) | Os 12 casos e as respostas geradas |

## Dados

Apenas laudos **sintéticos**, em `data/reports/`. Os PDFs são gerados por script: o conteúdo vive versionado em `scripts/synthetic_reports.py`, o PDF renderizado não.

Usar laudo de paciente real exigiria acordo formal com DASA e Genera, aprovação ética via CEP/CONEP e validação clínica. Não é restrição arbitrária: é a única forma compatível com a LGPD para dado genético, que é categoria especial.

## Autor

**Luiz Felipe Alves Gomes** · RM 565151 · Turma A

Ver [NOTICE.md](NOTICE.md) e [LICENSE.md](LICENSE.md) quanto a propriedade intelectual.
