# Avaliação do modelo

Execução de 09/10/2026 contra o agente em funcionamento, 3 execuções por caso.

| Medida | Resultado |
|---|---|
| Casos avaliados | 12 |
| Execuções por caso | 3 |
| Casos aprovados em todas as execuções | 11 de 12 |
| Casos com resultado instável entre execuções | 1 |
| Tempo médio de resposta | 6172 ms |
| Respostas recusadas pelas salvaguardas | 6 |
| Modelo de resposta | `gpt-5.6-terra` |
| Modelo de classificação e verificação | `gpt-5.6-luna` |

## Consistência

Casos que mudaram de resultado entre execuções:

- `diabetes`: 2 de 3 execuções aprovadas. faltou `1,41 ou 1.41`; faltou `TCF7L2`; refused True, esperado False; sem citacao de pagina no texto

## Validação das respostas

Toda resposta passa pelo verificador de fronteira clínica antes de chegar ao paciente, e a política é fail-closed: sem verificação, nada é entregue. Nesta execução 6 resposta(s) foram recusadas e as salvaguardas acionadas foram: `refused_by_intent`, `ungrounded`.

O detalhe caso a caso, com as respostas na íntegra, está em [golden-cases.md](golden-cases.md).
