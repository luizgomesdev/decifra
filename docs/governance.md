# Governança e riscos

Dado genético é **categoria especial** pela LGPD. Este documento registra os limites do agente, como eles são impostos tecnicamente, e o que acontece quando a imposição falha.

## Limites não negociáveis

O agente nunca:

- Diagnostica, nem afirma que a pessoa tem, está com ou é portadora de uma condição
- Indica, ajusta ou desaconselha medicamento, dose ou suplemento
- Prevê desfecho ou prazo
- Responde além do que está escrito no laudo

O agente sempre:

- Cita a página de origem de cada afirmação sobre o laudo
- Diz "não consta no seu relatório" quando não consta, em vez de completar a lacuna
- Encaminha ao profissional de saúde em caso acionável
- Anexa o disclaimer de natureza informativa e não diagnóstica

## Guardrails em camadas

Cada camada existe porque a anterior não cobre o caso dela. Ordem importa.

| # | Middleware | Hook | Pega o quê |
|---|---|---|---|
| 1 | `IntentGuardMiddleware` | `before_agent` | Pedido de diagnóstico, prescrição, prognóstico ou emergência. Recusa **antes** de gastar retrieval e modelo caro. A resposta é texto que um humano escreveu, então é auditável e não varia entre execuções |
| 2 | `PIIMiddleware` | input | CPF e e-mail digitados no chat |
| 3 | `RetrievalMiddleware` | `before_model` | Garante que a busca sempre roda e sempre filtrada por paciente |
| 4 | `ClinicalBoundaryMiddleware` | `after_model` | Afirmação diagnóstica, verbo de prescrição, tom alarmista, citação ausente. Julgado por modelo **separado**, não pelo gerador |
| 5 | `GroundingMiddleware` | `after_agent` | Resposta fluente, calma e não sustentada pelo laudo |
| 6 | `DisclaimerMiddleware` | `after_agent` | Anexa o aviso a toda resposta, recusa inclusive |

Camada 4 **substitui** a resposta em caso de violação de fronteira, nunca suaviza. Camada 5 só roda em texto que já passou pela 4.

> Detalhe que custou um bug: os hooks `after_*` executam em **ordem reversa**. O `DisclaimerMiddleware` é listado *antes* do `GroundingMiddleware` para acabar rodando *depois* dele. Na ordem intuitiva, um bloqueio por falta de fundamentação substituía a mensagem e **derrubava o disclaimer junto**. Há teste travando essa ordem.

## Por que a verificação é por modelo, e não por regex

A primeira versão usava lista de padrões. A medição a aposentou:

```
18 formas realistas de cruzar a fronteira clínica, em português
  lista de regex   ->   5/18 detectadas
  verificador LLM  ->  18/18 detectadas, 0 falso positivo em 7 frases legítimas
```

A lista não via "o senhor apresenta quadro compatível com hemocromatose", "trata-se de um caso de trombofilia instalada", "considere suspender o anticoagulante" e outras dez. O português tem formas demais de afirmar diagnóstico para uma lista enumerar, e cada escape chega num paciente.

O verificador também precisou de calibração no sentido oposto: ele bloqueava "o resultado é compatível com intolerância à lactose", que é **literalmente a classificação impressa no laudo**. Reproduzir a classificação do documento não é emitir diagnóstico. Depois do ajuste, o falso positivo sumiu e as 18 violações continuaram detectadas.

### Onde o determinístico permanece, e por quê

A detecção de **CPF** é regex, deliberadamente. Para uma LLM decidir se há CPF num texto, seria preciso **enviar o texto com o CPF para a API**, expondo exatamente o dado que a camada existe para proteger. O regex resolve localmente. Some-se que CPF tem formato fixo, ao contrário da fronteira clínica, que é semântica.

O `PIIMiddleware` nativo do LangChain cobre `email`, `credit_card`, `ip`, `mac_address` e `url`. **Nenhum documento brasileiro.** O detector de CPF é próprio; do framework se aproveita a infraestrutura de estratégia (`block`, `redact`, `mask`, `hash`).

## Política de falha: fail-closed

Não existe fallback determinístico. Se o verificador não roda, **nada é entregue**: o paciente recebe uma mensagem dizendo que a resposta não pôde ser conferida.

Texto não verificado sobre a saúde de alguém é precisamente o que este sistema existe para impedir, então falhar fecha em vez de degradar. Vale para o chat e para o resumo automático, que é uma segunda superfície onde o modelo escreve sobre saúde e passa pelo mesmo verificador.

## Transparência ao usuário

Toda intervenção de guardrail é **visível na interface**, não silenciosa:

| Sinal | Significado |
|---|---|
| `Fora do que posso responder` | Recusado por intenção |
| `Resposta bloqueada pela verificação clínica` | Cruzou a fronteira |
| `Reescrito para tom mais calmo` | Detectado alarmismo |
| `Fonte adicionada` | Faltava citação |
| `Resposta não sustentada pelo relatório` | Reprovado na fundamentação |
| `Verificação indisponível` | Fail-closed acionado |

O card de abertura declara o que o agente faz e o que **não** faz antes da primeira pergunta. Em saúde, um assistente superestimado é a falha perigosa.

## Dados

- Somente laudos **sintéticos**. Ver [proveniência](data-sources.md)
- Os PDFs não são versionados; o conteúdo vive em `scripts/synthetic_reports.py`
- Isolamento por paciente vale em toda a pilha: busca, perfil, resumo e histórico
- Nenhum treino com dado real, em nenhuma hipótese

Controles previstos para um cenário produtivo, hoje **não implementados** porque o projeto é acadêmico e não trata dado real: anonimização em logs e traces, criptografia em repouso e em trânsito, auditoria de inferência com retenção definida, pipeline de esquecimento em cascata e residência de dados em região brasileira.

## O que deliberadamente não seguimos

As Guidelines for Human-AI Interaction recomendam **G13 (aprender com o comportamento)** e **G17 (controles globais de personalização)**. Não aplicamos nenhuma das duas.

Personalizar a partir do histórico de alguém em cima de dado genético é perfilamento de categoria especial pela LGPD. É um caso em que a diretriz de UX briga com a governança, e a governança ganha.

## Riscos conhecidos

| Risco | Mitigação atual | Limitação |
|---|---|---|
| Alucinação sobre saúde | Verificação de fundamentação por modelo separado | Um verificador é um modelo, e modelos erram |
| Vazamento entre pacientes | Filtro obrigatório na busca, thread por paciente | Verificado por teste, não por prova formal |
| Alarmismo | Detecção e reescrita, número absoluto ao lado do relativo | Depende de o laudo trazer o risco absoluto |
| Excesso de confiança do usuário | Disclaimer em toda resposta, limites declarados na abertura | Não há como impedir que alguém ignore |
| Uso da chave de API | `.env` fora do versionamento | Não há rotação nem cofre |

## Uso do sistema fora deste contexto

Implementação sobre laudo real exige, cumulativamente:

1. Acordo formal com DASA e Genera
2. Aprovação ética via CEP/CONEP
3. Validação clínica com especialistas
4. Adequação aos controles listados acima como não implementados
