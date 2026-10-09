# Decifra

Camada de IA que traduz o relatório genético da Genera para linguagem que o paciente entende, sem perder a fidelidade ao documento original.

> Enterprise Challenge DASA · FIAP · Graduação em IA
>
> Repositório: [github.com/luizgomesdev/decifra](https://github.com/luizgomesdev/decifra)

> ⚠️ Projeto acadêmico com **dados sintéticos**. Não é produto, não é dispositivo médico e não substitui avaliação profissional. Ver [Governança](docs/governance.md).

---

## Em produção

**[Abrir a aplicação](http://100.24.98.206)** · instância de demonstração na AWS, com laudos sintéticos. É HTTP sem domínio e fica no ar até a correção; se não responder, foi desligada para não gerar custo. Como está montada e como subir de novo: [deploy.md](docs/deploy.md).

## Vídeos

| Sprint | Vídeo |
|---|---|
| Sprint 3, experiência do paciente | [Assistir (5 min)](https://youtu.be/eXz8iwZeJ7w) |
| Sprint 4, produção e governança | a publicar |

---

## As quatro sprints

**Sprint 1, estruturar o laudo.** O relatório da Genera chega como PDF longo, com tabelas densas. A primeira etapa transformou esse documento em dado estruturado, preservando a página de origem de cada achado, porque sem origem não há como responder nada de forma verificável.

**Sprint 2, o agente com busca semântica.** Cada achado virou trecho indexado no Qdrant, isolado por paciente, e o agente passou a responder sobre o laudo recuperando os trechos certos em vez de inventar a partir do nome da doença.

**Sprint 3, a experiência do paciente.** Dashboard com riscos, ancestralidade, características e farmacogenética; respostas em linguagem simples com citação de página; resumos automáticos; e as salvaguardas de comunicação, que recusam pedido de diagnóstico, prescrição e prognóstico, com política fail-closed.

**Sprint 4, produção e governança.** A solução saiu da máquina local: roda numa instância EC2 com os quatro containers, tem `/health` checando cada dependência, registra um evento JSON por requisição sem gravar conteúdo de laudo, teve a qualidade medida em três execuções por caso e ganhou uma política de governança cobrindo LGPD, explicabilidade e logging.

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

### Observando a operação

```bash
curl -s localhost:8000/health | jq                 # dependências
docker compose -f compose.prod.yml logs -f api     # um evento JSON por requisição
```

### Verificando a qualidade das respostas

```bash
cd apps/api
uv run pytest tests/                              # rápido, sem API
uv run python ../../scripts/run_golden.py         # 12 casos contra o agente real
```

O segundo roda cada caso três vezes e gera [`docs/golden-cases.md`](docs/golden-cases.md), com as respostas na íntegra, e [`docs/evaluation.md`](docs/evaluation.md), com o resumo. Na última execução, 11 dos 12 casos passaram nas três tentativas; o caso `diabetes` falhou uma vez, com o verificador clínico recusando uma resposta que deveria passar.

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
| [Vídeo de demonstração](https://youtu.be/eXz8iwZeJ7w) | Apresentação de 5 minutos da experiência do usuário |
| [Guia do projeto](docs/guia.md) | Visão geral em linguagem simples, com diagramas. **Comece por aqui** |
| [Arquitetura de IA](docs/architecture.md) | Pipeline, RAG, escolha de modelo, chunking, streaming |
| [Governança e riscos](docs/governance.md) | LGPD, limites do agente, guardrails em camadas, política de falha |
| [Decisões de experiência](docs/ux-decisions.md) | Dashboard, comunicação de risco, UX do chat, acessibilidade |
| [Proveniência dos dados](docs/data-sources.md) | O que é real e o que é sintético nos laudos, com referências |
| [Testes de qualidade](docs/golden-cases.md) | Os 12 casos e as respostas geradas |
| [Avaliação do modelo](docs/evaluation.md) | Qualidade e consistência medidas em 3 execuções por caso |
| [Política de governança de IA](docs/ai-governance-policy.md) | LGPD, explicabilidade, registro de eventos e política de falha |
| [Deploy](docs/deploy.md) | Como a aplicação está no ar e como subir de novo |

## Dados

Apenas laudos **sintéticos**, em `data/reports/`. Os PDFs são gerados por script: o conteúdo vive versionado em `scripts/synthetic_reports.py`, o PDF renderizado não.

Usar laudo de paciente real exigiria acordo formal com DASA e Genera, aprovação ética via CEP/CONEP e validação clínica. Não é restrição arbitrária: é a única forma compatível com a LGPD para dado genético, que é categoria especial.

## Autor

**Luiz Felipe Alves Gomes** · RM 565151 · Turma A

Ver [NOTICE.md](NOTICE.md) e [LICENSE.md](LICENSE.md) quanto a propriedade intelectual.
