import { HugeiconsIcon } from '@hugeicons/react'
import { ArrowRight01Icon, Message01Icon } from '@hugeicons/core-free-icons'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { RiskFinding } from '@/shared/api/schemas'
import { REPORT } from '../content'
import { stylesFor, toneFor } from '../risk-level'

/**
 * One finding, one card.
 *
 * Numbers, not charts: usability testing on a genetic-results portal had users
 * ask for the pie charts to be replaced with numeric risk, so the absolute risk
 * sentence is the emphasised element and there is no visualisation of it.
 *
 * The absolute risk sits directly under the relative one, because "3x" alone
 * frightens and "3 in 1000" informs.
 */
export function RiskCard({
  finding,
  onAsk,
}: {
  finding: RiskFinding
  onAsk: (question: string) => void
}) {
  const tone = toneFor(finding.risk_level)
  const styles = stylesFor(tone)

  return (
    <Card className={`border-l-4 ${styles.accent}`}>
      <CardHeader className="gap-2">
        <div className="flex flex-wrap items-start justify-between gap-2">
          <CardTitle className="text-base leading-snug">{finding.condition}</CardTitle>
          <Badge className={styles.badge} variant="secondary">
            {finding.risk_level}
          </Badge>
        </div>
        <dl className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
          <div className="flex gap-1">
            <dt>{REPORT.card.gene}</dt>
            <dd className="font-medium text-foreground">{finding.gene}</dd>
          </div>
          <div className="flex gap-1">
            <dt>{REPORT.card.genotype}</dt>
            <dd className="font-medium text-foreground">{finding.genotype}</dd>
          </div>
        </dl>
      </CardHeader>

      <CardContent className="space-y-3 text-sm">
        {finding.absolute_risk && (
          <p className="rounded-md bg-muted/60 p-3 leading-relaxed">
            <span className="font-medium">{REPORT.card.absolute}: </span>
            {finding.absolute_risk}
          </p>
        )}

        <p className="leading-relaxed text-muted-foreground">{finding.interpretation}</p>

        {finding.recommended_action && (
          <p className="flex gap-2 leading-relaxed">
            <HugeiconsIcon
              icon={ArrowRight01Icon}
              className="mt-0.5 size-4 shrink-0 text-muted-foreground"
              aria-hidden
            />
            <span>
              <span className="font-medium">{REPORT.card.action}: </span>
              {finding.recommended_action}
            </span>
          </p>
        )}

        <div className="flex flex-wrap items-center justify-between gap-2 pt-1">
          <span className="text-xs text-muted-foreground">
            {REPORT.card.source.replace('{page}', String(finding.source_page))}
          </span>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onAsk(`Me explica melhor o resultado de ${finding.condition}.`)}
          >
            <HugeiconsIcon icon={Message01Icon} className="size-4" aria-hidden />
            {REPORT.card.ask}
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
