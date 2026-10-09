# Política de governança de IA

Como o Decifra trata dados, explica o que responde, registra o que acontece e o que ele faz quando algo falha. Vale para a versão em demonstração, com laudos sintéticos.

## 1. Dados e LGPD

**O sistema não processa dado pessoal.** Todos os laudos são sintéticos, gerados por `scripts/synthetic_reports.py`. Nomes, idades, identificadores e genótipos são inventados. A separação item a item entre o que é real (genes, variantes e magnitudes de risco, com referência na literatura) e o que é inventado está em [data-sources.md](data-sources.md).

Como não há titular de dados, não há tratamento de dado pessoal sensível na forma do art. 5º, II da LGPD, e nenhuma base legal precisa ser invocada para esta demonstração.

**O que existe hoje, e onde:**

| Dado | Onde fica | Por quanto tempo |
|---|---|---|
| Laudos sintéticos estruturados (JSON) | disco da instância EC2 | até a instância ser encerrada |
| Trechos indexados e seus vetores | Qdrant, na mesma instância | até a instância ser encerrada |
| Histórico de conversa | Postgres, na mesma instância | até a instância ser encerrada |
| Registros de operação | log dos containers | rotação por tamanho (10 MB por arquivo, 3 arquivos) |

A instância é desligada depois da avaliação acadêmica, e com ela todo o conteúdo acima.

**O que mudaria com laudo real.** Dado genético é dado pessoal sensível. Usar laudo de paciente exigiria, antes de qualquer linha de código: acordo formal com a DASA e a Genera, aprovação ética via CEP/CONEP, base legal definida (tutela da saúde por profissional, art. 11, II, "f", ou consentimento específico e destacado), relatório de impacto à proteção de dados, minimização do que é indexado, criptografia em repouso e em trânsito, controle de acesso por paciente, prazo de retenção declarado e um canal para o titular exercer seus direitos. Nada disso está implementado, e por isso o sistema só opera com dado sintético.

## 2. Explicabilidade

O paciente precisa saber de onde veio cada afirmação.

- **Citação de origem.** Toda resposta sobre o laudo cita o título do achado e a página de onde o trecho saiu. A interface mostra essas citações junto da resposta.
- **Intenção declarada.** Cada resposta carrega a intenção que o agente classificou (pergunta sobre o laudo, pedido de conduta clínica, conversa geral). É isso que decide o caminho da resposta.
- **Recusa explicada.** Quando o agente se recusa a responder, ele diz por quê e encaminha ao profissional, em vez de devolver uma resposta vazia.
- **Limite declarado.** O sistema não dá diagnóstico, não prescreve e não substitui consulta. Isso está na interface, não só na documentação.
- **O que não é explicável.** O ranqueamento semântico do Qdrant e a geração do texto são probabilísticos. Por isso a verificação de fronteira clínica é feita por outro modelo, e a política é recusar quando ela não puder rodar.

## 3. Registro de eventos

Cada requisição de chat e cada execução do pipeline de ingestão gera uma linha JSON (`apps/api/src/decifra/shared/logging.py`).

**O que é registrado:** identificador da requisição, identificador do paciente sintético, intenção classificada, se houve recusa, duração em milissegundos, modelo usado e, em caso de falha, o tipo do erro. No pipeline: início, cada laudo processado com o número de trechos indexados, e cada laudo que falhou.

**O que nunca é registrado:** a pergunta do paciente, o texto da resposta e qualquer conteúdo do laudo. Há teste automatizado garantindo isso (`apps/api/tests/test_logging.py`).

**Onde fica e por quanto tempo:** no log dos containers da instância, com rotação por tamanho. Quem opera lê com `docker compose logs`. Não há envio para serviço externo de observabilidade.

## 4. Falhas e responsabilidade

- **Fail-closed.** Se o verificador de fronteira clínica não puder rodar, nada é entregue ao paciente. Um texto não verificado sobre a saúde de alguém é pior que um erro honesto. O porquê, com a medição que motivou a decisão, está em [governance.md](governance.md).
- **Dependência fora do ar.** `GET /health` checa Qdrant, Postgres e a configuração do modelo e responde 503 nomeando quem falhou, em vez de aceitar requisição que vai quebrar adiante.
- **Falha na ingestão.** Um laudo com problema é registrado como falha e o restante do lote continua.
- **Responsável pela operação.** Luiz Felipe Alves Gomes, autor do projeto. A demonstração é acadêmica, roda em instância própria e é desligada após a correção.
- **Escopo de uso.** O sistema não foi validado clinicamente, não é dispositivo médico e não deve ser usado fora deste contexto acadêmico.
