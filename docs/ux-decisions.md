# Decisões de experiência

Cada decisão aqui tem uma razão declarada. Onde há evidência externa, ela está citada.

## O princípio que orienta tudo

Quem lê esta tela acabou de receber informação sobre o próprio corpo e não tem formação em saúde. **Risco aumentado é probabilidade, não sentença.** Toda escolha de layout, cor e palavra é avaliada por: isso informa, ou assusta?

## Comunicação de risco

### Número, não gráfico

Um estudo de desenvolvimento e teste de usabilidade de portal de resultado genético para pacientes registra que os **gráficos de pizza foram substituídos por risco numérico a pedido dos próprios usuários**.

Consequência direta no produto: os cards de risco não têm visualização. O número lidera.

### Absoluto ao lado do relativo

"3x" assusta. "2 a 5 em 1000 pessoas por ano" informa. Quando o laudo traz o risco absoluto, ele aparece em destaque, acima da interpretação, dentro de um bloco próprio.

Quando há risco aumentado, a mesma resposta traz o contrapeso de que a maioria das pessoas com aquele resultado não desenvolve a condição, desde que o laudo sustente a afirmação.

### Cor sem alarme

**Não há vermelho em lugar nenhum.** Vermelho carrega semântica de erro e emergência, e uma predisposição genética não é nem uma coisa nem outra.

| Classificação | Tom |
|---|---|
| Aumentado | Âmbar |
| Levemente aumentado | Âmbar claro |
| Padrão | Neutro |
| Reduzido | Verde suave |

A terminologia é a real da Genera, que usa a "Escala de Risco Genético" com as categorias *aumentado*, *padrão* e *reduzido*.

### Ordem por relevância clínica, não do PDF

Achados com risco aumentado sobem. Um resultado acionável não deve ficar abaixo de um traço sobre cor dos olhos só porque o PDF assim os imprimiu.

## Estrutura da tela

### Resumo primeiro

O mesmo estudo moveu a visão geral para antes de tudo após feedback de usuários. É o que responde "o que isso significa para mim" sem exigir a leitura de quatro seções.

O resumo é gerado automaticamente e passa pelo mesmo verificador do chat.

### Duas colunas, chat ao lado

O chat fica ao lado do relatório, não em página separada, porque **toda pergunta nasce de algo que a pessoa acabou de ler**. Mandar para outro lugar perde o contexto.

Cada card tem "Perguntar sobre isso", que envia a pergunta já formulada. Em telas pequenas, o chat vira uma folha lateral.

### Ancestralidade em barras

Barras proporcionais com o número ao lado, não pizza. Além do argumento acima, barras permanecem legíveis sem percepção de cor, o que uma pizza de seis fatias não permite.

## UX do chat

Aplicado a partir das [Guidelines for Human-AI Interaction](https://www.microsoft.com/en-us/research/publication/guidelines-for-human-ai-interaction/) (CHI 2019) e do PAIR.

| Diretriz | Como aparece |
|---|---|
| **G1** e **G2** o que o sistema faz e quão bem | Card de abertura com "o que eu consigo fazer" e "o que eu não faço", antes da primeira pergunta. O PAIR trata "diga o que o sistema não consegue fazer" como central para calibração de confiança, e em saúde o assistente superestimado é a falha perigosa |
| **G4** informação contextualmente relevante | Retrieval sempre filtrado pelo paciente |
| **G9** correção eficiente | "Perguntar de novo" e "Editar pergunta" sem redigitar. Quando a pessoa não consegue identificar ou corrigir um erro da IA, a conclusão da tarefa cai cerca de 40% (NN/g) |
| **G10** delimitar quando em dúvida | Recusa por intenção e redirecionamento em `off_topic` degradam com elegância |
| **G11** por que o sistema agiu assim | Citações com trecho expansível, mais os badges de guardrail visíveis |
| **G12** lembrar interações recentes | Sessão persistida por paciente, histórico retomado do Postgres |

### Espera honesta

A resposta leva dezenas de segundos. A linha de progresso mostra a etapa real ("Lendo o seu relatório", "Conferindo o que escrevi"), derivada dos updates do grafo, não uma animação decorativa. Há botão de parar.

O texto aparece por parágrafo, e cada parágrafo é verificado antes de ser exibido. O detalhe técnico está em [Arquitetura](architecture.md#streaming-com-verificação-por-parágrafo).

### Recapitulação da conversa

O botão "Resumo" recapitula a sessão em tópicos curtos, preservando números e páginas que apareceram. É regenerado a partir dos turnos guardados, não mantido incrementalmente: o checkpointer já é a fonte da verdade e um resumo incremental divergiria dela.

Passa pelo mesmo verificador do chat. Um recap continua sendo o modelo escrevendo sobre a saúde de alguém.

### Citação que abre a fonte

Nomear uma página é uma afirmação; mostrar a frase é evidência. Como o relatório já está carregado para o painel, o trecho não custa nada a mais e permite conferir a resposta sem sair da conversa.

## Acessibilidade

As normas de acessibilidade de 2026 do HHS exigem **WCAG 2.1 nível A e AA** para portais de paciente. O que já está no lugar:

- Marcação semântica: `dl` para pares campo/valor, `table` para dados tabulares, `blockquote` para trechos citados
- Rótulo acessível em todo controle sem texto visível
- Barras de ancestralidade com `role="img"` e `aria-label` contendo região e percentual, para quem usa leitor de tela
- Estado do acordeão de citação anunciado com `aria-expanded`
- Campo inválido marcado com `aria-invalid`
- Tabelas rolam dentro do próprio contêiner; a página nunca rola na horizontal
- Enter envia, Shift+Enter quebra linha

Não auditado ainda: contraste medido, navegação completa por teclado e teste com leitor de tela real.

## Linguagem

- Frases curtas e vocabulário comum, seguindo a recomendação de *plain language* do estudo citado
- Termo técnico do laudo é explicado na mesma frase em que aparece
- **Glossário no lugar do termo**: "Gene" e "Genótipo" nos cards abrem a definição ao toque. O estudo lista glossário e definição de termos entre as mudanças pedidas após o teste de usabilidade. É popover e não tooltip porque tooltip não abre em toque, o que esconderia o glossário de todo leitor no celular
- O texto da interface fica isolado em arquivos `content.ts`, o que permite revisar a redação sem ler código: relevante quando a redação é responsabilidade clínica, não estética

## Estilo visual

`shadcn/ui` no estilo **Maia** (suave e arredondado). Os estilos mudam forma e densidade: Nova é compacto, Mira é denso, Lyra é sharp, Sera é editorial. Denso e anguloso servem a ferramenta de trabalho; para alguém lendo sobre a própria predisposição genética, trabalham contra.

Os componentes de chat (`MessageScroller`, `Message`, `Bubble`, `Marker`) são os oficiais do shadcn, lançados em junho de 2026.

## Fontes

- [Developing the MyCancerGene Digital Health Portal](https://pmc.ncbi.nlm.nih.gov/articles/PMC12120370/) · desenvolvimento e teste de usabilidade de portal de resultado genético
- [Guidelines for Human-AI Interaction](https://www.microsoft.com/en-us/research/publication/guidelines-for-human-ai-interaction/) · Microsoft Research, CHI 2019
- [Escala de Risco Genético](https://www.genera.com.br/escala-de-risco-genetico/) · terminologia da própria Genera
- [Healthcare Dashboard Design](https://www.aufaitux.com/blog/healthcare-dashboard-ui-ux-design-best-practices/) · carga cognitiva e acessibilidade em saúde
