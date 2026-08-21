// Textos em português da camada de relatório. Valores em PT, chaves em inglês.
// Redação curta e sem jargão por decisão: teste de usabilidade de portal de
// resultado genético apontou frases curtas e glossário como o que reduz
// ansiedade, e risco em número no lugar de gráfico.

export const RISK_LEVELS = {
  increased: 'Risco aumentado',
  slightly: 'Risco levemente aumentado',
  standard: 'Risco padrão',
  reduced: 'Risco reduzido',
  other: 'Resultado informativo',
} as const

export const REPORT = {
  sections: {
    risks: 'Riscos',
    ancestry: 'Ancestralidade',
    traits: 'Características',
    pharma: 'Medicamentos',
  },
  card: {
    gene: 'Gene',
    genotype: 'Genótipo',
    variant: 'Variante',
    relative: 'Comparado à média',
    absolute: 'O que isso significa',
    action: 'O que fazer com isso',
    source: 'Página {page} do seu relatório',
    ask: 'Perguntar sobre isso',
    reference: 'Referência científica',
  },
  ancestry: {
    title: 'De onde vem o seu DNA',
    lineages: 'Linhagens',
    maternal: 'Linhagem materna',
    paternal: 'Linhagem paterna',
    neanderthal: 'Componente neandertal',
  },
  traits: {
    title: 'Características',
    description: 'Achados sem implicação clínica, de caráter informativo.',
    columns: { name: 'Característica', gene: 'Gene', result: 'Resultado', page: 'Página' },
  },
  pharma: {
    title: 'Medicamentos',
    description:
      'Informação para levar ao seu médico. Nada aqui indica iniciar, ajustar ou suspender medicamento.',
    columns: { drug: 'Medicamento', gene: 'Gene', phenotype: 'Como seu corpo processa', page: 'Página' },
  },
  summary: {
    title: 'Resumo do seu relatório',
    loading: 'Preparando seu resumo...',
  },
  glossary: {
    Gene: 'Trecho do DNA com uma função. Você herda duas cópias de cada, uma de cada mãe ou pai.',
    Genótipo: 'A combinação específica que você tem desse gene.',
    Variante: 'Uma diferença pontual no DNA. Ter uma variante é comum e não significa doença.',
    'Risco relativo': 'Quantas vezes a chance é maior comparada a quem não tem a variante. Não é a sua chance real.',
  } as Record<string, string>,
  empty: {
    patients: 'Nenhum relatório disponível.',
    error: 'Não consegui carregar seus dados agora. Tente novamente em instantes.',
  },
}
