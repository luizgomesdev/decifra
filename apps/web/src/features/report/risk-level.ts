import { RISK_LEVELS } from './content'

export type RiskTone = 'increased' | 'slightly' | 'standard' | 'reduced' | 'other'

/**
 * Maps the report's own wording to a visual tone.
 *
 * Deliberately no red anywhere. An increased genetic predisposition is a
 * probability, not an emergency, and the project's own governance rule says
 * colour must not turn it into an alarm. Amber carries "worth your attention"
 * without the error semantics red brings.
 */
const TONE_STYLES: Record<RiskTone, { badge: string; accent: string }> = {
  increased: {
    badge: 'bg-amber-100 text-amber-900 dark:bg-amber-950 dark:text-amber-200',
    accent: 'border-l-amber-400 dark:border-l-amber-600',
  },
  slightly: {
    badge: 'bg-amber-50 text-amber-800 dark:bg-amber-950/60 dark:text-amber-200/90',
    accent: 'border-l-amber-200 dark:border-l-amber-800',
  },
  standard: {
    badge: 'bg-muted text-muted-foreground',
    accent: 'border-l-border',
  },
  reduced: {
    badge: 'bg-emerald-50 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-200',
    accent: 'border-l-emerald-300 dark:border-l-emerald-700',
  },
  other: {
    badge: 'bg-muted text-muted-foreground',
    accent: 'border-l-border',
  },
}

export function toneFor(riskLevel: string): RiskTone {
  const level = riskLevel.trim().toLowerCase()
  if (level.startsWith('levemente')) return 'slightly'
  if (level.startsWith('aumentado')) return 'increased'
  if (level.startsWith('reduzido')) return 'reduced'
  if (level.startsWith('padrao') || level.startsWith('padrão')) return 'standard'
  return 'other'
}

export function labelFor(tone: RiskTone): string {
  return RISK_LEVELS[tone]
}

export function stylesFor(tone: RiskTone) {
  return TONE_STYLES[tone]
}
