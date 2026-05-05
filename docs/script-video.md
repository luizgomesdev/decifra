# Script Video Demo — Decifra (até 5 min)

> Tom: técnico-didático, sério (saúde), ritmo confortável. Sem ser solene.
> Setup recomendado: tela compartilhada com README + diagrama, câmera pequena no canto.

---

## **00:00 — 00:20 — Abertura (20s)**

> "Oi. Sou o Luiz, RM 565151, FIAP turma A.
> Apresentando minha proposta para o Enterprise Challenge da DASA — Sprint 1.
> O projeto se chama **Decifra** — uma camada de IA pra tornar acessíveis os relatórios genéticos da plataforma Genera."

## **00:20 — 01:00 — O Problema (40s)**

> "A Genera entrega informação genética muito valiosa: predisposição a doenças, ancestralidade, farmacogenômica. Mas entrega num PDF de 30 a 80 páginas, com linguagem clínica densa.
>
> Resultado prático: o paciente recebe e não consegue usar pra decisão. Imagina alguém recebendo predisposição a Cardiomiopatia Hipertrófica — uma variante MYH7 patogênica. Sem conhecimento técnico, ele não entende o nível de risco real, não sabe se familiares devem testar, não sabe se precisa cardiologista, se precisa mudar exercício.
>
> A informação fica congelada no documento. É um problema de **interface**, não de qualidade do exame."

## **01:00 — 01:30 — A Solução (30s)**

> "**Decifra** transforma o PDF em conversa.
>
> Em três camadas:
> - **Ingestão automática** do PDF — sai PDF, entra JSON estruturado com cada finding catalogado, classificado pela ACMG, com rastreabilidade até a página original.
> - **Camada de IA** que responde perguntas em duas vozes — paciente e clínico — com guardrails clínicos não-negociáveis.
> - **Frontend** com chat e dashboard de findings categorizados por sistema — cardiovascular, oncológico, farmacogenômica, ancestralidade.
>
> Princípio central: a IA aqui **não substitui médico, ela traduz**."

## **01:30 — 03:30 — Pipeline e Arquitetura (2 min) — TELA: diagrama**

> "Mostra o diagrama. Pipeline tem dois fluxos:
>
> **Fluxo 1 — ingestão, async**, uma vez por relatório:
> - Upload do PDF
> - Parser **LlamaParse** ou Unstructured.io — eu escolhi LlamaParse porque tabelas clínicas com layout multi-coluna quebram parsers convencionais
> - **Chunking contextual** seguindo o paper recente da Anthropic — antes de embedar cada chunk, um LLM gera um contexto curto situando o chunk no documento. Isso reduz 49% das falhas de retrieval, comprovado em benchmark
> - **Embedding com Voyage-3-large**, hoje o melhor em retrieval
> - Vai pra dois lugares ao mesmo tempo: vector store em **pgvector** e Postgres relacional com findings normalizados pra dashboard. Não duplico DB porque Postgres já é fonte primária
>
> **Fluxo 2 — query, síncrono, latência menor que 3s**:
> - Pergunta entra
> - Router classifica intent: paciente, clínico, ou recusa por solicitação de diagnóstico
> - **Hybrid search**: BM25 e dense retrieval em paralelo, fusionados via Reciprocal Rank Fusion
> - **Cross-encoder rerank** com Cohere Rerank 3, top 5 chunks
> - Geração com **Claude Sonnet 4.6** — escolhi pelo Constitutional AI, que ajuda em recusa apropriada no domínio médico
> - **Output guardrail**: scrub PII, valida que tem citação, valida que não dá diagnóstico, valida que não prescreve
> - Resposta vai pro frontend com fonte original embutida"

## **03:30 — 04:15 — Governança (45s)**

> "Domínio é dado genético — categoria especial pela LGPD e resolução CFM.
>
> Cinco controles não-negociáveis:
> - Patient ID hash SHA-256 antes de qualquer log
> - Encryption at rest e in transit
> - Audit log de toda query, retention 5 anos
> - Direito ao esquecimento via pipeline forget cascateado
> - **Modelo proprietário não vê dado de paciente real** — só dado sintético em treino
>
> E os guardrails clínicos: nunca diagnóstico, nunca prescrição, nunca prognóstico, sempre citação, sempre marca incerteza, sempre encaminha pra clínico em caso acionável."

## **04:15 — 04:50 — Próximos Passos (35s)**

> "Sprint 2: protótipo funcional — backend FastAPI ingerindo um PDF sintético, frontend React com chat, eval pipeline com 10 golden cases.
>
> Sprint 3: multi-modo paciente/clínico, dashboard, guardrails NeMo completos.
>
> Pós-Challenge: validação com clínicos, fine-tuning embedding em corpus médico BR, integração HL7 FHIR pra entrar em EHR."

## **04:50 — 05:00 — Fechamento (10s)**

> "Repositório privado vai estar com o tutor Caique convidado.
>
> Esse é o Decifra. Obrigado."

---

## Notas de gravação

### Setup
- **Loom** ou **OBS** (ambos free)
- Resolução: 1920x1080
- Áudio: headset com mic decente, não use mic do laptop
- Background: parede limpa atrás OU virtual blur

### Durante
- **Tela cheia do README + diagrama Mermaid** (faz isso no GitHub que renderiza Mermaid nativo)
- Quando falar do diagrama, **highlight cada caixa** ao mencionar
- Mantém o ritmo — 5 min é apertado, **não erra a marcha**
- 1ª take quase nunca presta — calcule 2-3 takes

### Ferramenta de teleprompter
- Use o próprio script no segundo monitor
- Ou app de teleprompter no celular ([Selvi](https://selvi.app/), free)

### Timer
- Marca tempo de cada bloco no script
- Se passou 30s do alvo, corta

### Output
- MP4 H.264, ≤500MB
- Hospedagem: Loom direto (link público) ou YouTube unlisted
- **Cole o link no README** (seção "Vídeo")

## Histórico

- 2026-05-04 — script v1
