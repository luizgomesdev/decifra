// Textos em português do chat. Valores em PT, chaves em inglês.

export const CHAT = {
  title: 'Converse sobre o seu relatório',
  subtitle: 'Respondo apenas com base no que está escrito nele.',
  placeholder: 'Pergunte algo sobre o seu relatório',
  send: 'Enviar',
  sending: 'Pensando...',
  empty: {
    title: 'O que você quer entender?',
    hint: 'Toque em uma sugestão ou pergunte do seu jeito.',
  },
  capabilities: {
    title: 'Antes de começar',
    can: {
      label: 'O que eu consigo fazer',
      items: [
        'Explicar o que cada resultado do seu relatório significa',
        'Traduzir termo técnico para linguagem do dia a dia',
        'Mostrar em que página do relatório está cada informação',
      ],
    },
    cannot: {
      label: 'O que eu não faço',
      items: [
        'Dizer se você tem ou não uma doença',
        'Indicar, ajustar ou suspender medicamento',
        'Prever se ou quando algo vai acontecer',
      ],
    },
    note: 'Se a resposta não estiver no seu relatório, eu digo que não consta em vez de supor.',
  },
  actions: {
    stop: 'Parar',
    retry: 'Perguntar de novo',
    edit: 'Editar pergunta',
    newChat: 'Nova conversa',
  },
  citation: {
    trigger: 'Ver trecho',
    title: 'Trecho do seu relatório',
    page: 'Página {page}',
  },
  suggestions: [
    'O que meu relatório diz sobre ancestralidade?',
    'Tenho algum risco aumentado?',
    'O que significa genótipo?',
  ],
  sources: 'Fontes no seu relatório',
  page: 'página {page}',
  error: 'Não consegui responder agora. Tente novamente em instantes.',
  validation: {
    empty: 'Escreva sua pergunta.',
    tooLong: 'Pergunta muito longa. Tente resumir.',
  },
  guardLabels: {
    refused_by_intent: 'Fora do que posso responder',
    forbidden_language: 'Resposta bloqueada pela verificação clínica',
    alarmist_rewritten: 'Reescrito para tom mais calmo',
    citation_appended: 'Fonte adicionada',
    ungrounded: 'Resposta não sustentada pelo relatório',
    verifier_unavailable: 'Verificação indisponível',
  } as Record<string, string>,
}
