# Proveniência dos dados dos laudos sintéticos

Os laudos em `data/reports/inbox/` são sintéticos. Este documento separa, item a item, o que é real e o que é inventado, e de onde vieram os números.

## O que é inventado

- **Pacientes.** Helena Vasconcelos Prado e Rogerio Kimura Tavares não existem. Nome, idade, sexo, datas e identificação da amostra são fictícios.
- **Genótipos.** Quem tem qual variante foi escolhido para produzir dois perfis contrastantes, não a partir de dado real.
- **Percentuais de ancestralidade.** Plausíveis para a formação populacional brasileira, mas não derivados de amostra real.

## O que é real

- **Genes e variantes.** Todos os `rs` citados existem e correspondem ao gene indicado.
- **Associações.** Cada par variante/condição tem literatura publicada.
- **Magnitudes de risco.** Verificadas contra fonte, não escritas de memória. Toda predisposição carrega a referência no próprio PDF.
- **Terminologia de risco.** "Risco aumentado", "padrão" e "reduzido" são as categorias que a Genera usa na Escala de Risco Genético.

## Referências por achado

| Variante | Condição | Valor no laudo | Fonte |
|---|---|---|---|
| `F5` rs6025 heterozigoto | Trombofilia | ~3x, faixa de 2x a 5x | *Blood* 143(23):2425, 2024 (FinnGen + UK Biobank); Elsevier, *Genetics of venous thrombosis* |
| `MTHFR` rs1801133 T/T | Homocisteína | Prevalência de 5 a 10%, atividade enzimática ~70% menor | BMC Cardiovascular Disorders, 2025; PMC1074713 |
| `APOE` e3/e4 | Alzheimer tardio | 2,59x (IC 95%: 2,31 a 2,91) | Meta-análise de APOE na América Latina, PMC12927995 |
| `TCF7L2` rs7903146 heterozigoto | Diabetes tipo 2 | 1,41x (IC 95%: 1,34 a 1,48) | *Mutagenesis* 28(1):25, 121.174 indivíduos; HuGE review PMC2653476 |
| `CFH` rs1061170 C/C | Degeneração macular | 2,45x a 5,57x conforme o estudo | Maugeri et al., *Acta Ophthalmologica*, 2019 |
| `HFE` rs1800562 heterozigoto | Hemocromatose | OR 4,1 (IC 95%: 2,9 a 5,8) para sobrecarga, penetrância clínica baixa | Pooled analysis, PubMed 11399207; NEJM |
| `MCM6`/`LCT` rs4988235 G/G | Intolerância a lactose | Genótipo ancestral, sem persistência de lactase | Literatura estabelecida |

## Correções aplicadas na primeira versão

A primeira versão destes laudos foi escrita sem verificação, e três números não se sustentaram:

| Item | Antes | Depois | Motivo |
|---|---|---|---|
| Fator V de Leiden | 4,2x | ~3x, faixa de 2x a 5x | O valor original não aparece na literatura consultada |
| MTHFR T/T, prevalência | 10 a 15% | 5 a 10% | Superestimado para a população geral |
| APOE e3/e4 | 2,7x | 2,59x com intervalo de confiança | Trocado por valor de meta-análise em população latino-americana, mais aplicável ao Brasil |

Registrado aqui porque a diferença entre um número plausível e um número verificado é justamente o que separa uma ferramenta de saúde de um gerador de texto convincente.

## Por que não usamos laudo real

Dado genético é categoria especial pela LGPD. Usar laudo de paciente real exigiria acordo formal com DASA e Genera, aprovação ética via CEP/CONEP e validação clínica. A Genera publica um exemplo de resultado em `descubra.genera.com.br`, que serviu de referência para a terminologia e a estrutura de seções, mas o conteúdo dos laudos aqui é integralmente sintético.
