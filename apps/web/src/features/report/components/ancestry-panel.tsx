import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { Report } from '@/shared/api/schemas'
import { REPORT } from '../content'

function parsePercentage(value: string): number {
  return Number.parseFloat(value.replace('%', '').replace(',', '.')) || 0
}

/**
 * Ancestry as proportional bars, not a pie.
 *
 * Same reasoning as the risk cards: the number leads, the bar only helps
 * compare magnitudes at a glance. Bars are also readable without colour
 * perception, which a pie chart with six slices is not.
 */
export function AncestryPanel({ report }: { report: Report }) {
  const { ancestry } = report
  const lineages = [
    [REPORT.ancestry.maternal, ancestry.maternal_haplogroup],
    [REPORT.ancestry.paternal, ancestry.paternal_haplogroup],
    [REPORT.ancestry.neanderthal, ancestry.neanderthal],
  ].filter(([, value]) => value)

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">{REPORT.ancestry.title}</CardTitle>
        </CardHeader>
        <CardContent className="space-y-5">
          <p className="text-sm leading-relaxed text-muted-foreground">{ancestry.summary}</p>

          <ul className="space-y-3">
            {ancestry.components.map((component) => (
              <li key={component.region} className="space-y-1.5">
                <div className="flex items-baseline justify-between gap-3 text-sm">
                  <span className="font-medium">{component.region}</span>
                  <span className="tabular-nums text-muted-foreground">
                    {component.percentage}
                  </span>
                </div>
                <div
                  className="h-1.5 w-full overflow-hidden rounded-full bg-muted"
                  role="img"
                  aria-label={`${component.region}: ${component.percentage}`}
                >
                  <div
                    className="h-full rounded-full bg-primary/70"
                    style={{ width: `${parsePercentage(component.percentage)}%` }}
                  />
                </div>
                {component.detail && (
                  <p className="text-xs text-muted-foreground">{component.detail}</p>
                )}
              </li>
            ))}
          </ul>

          <p className="text-xs text-muted-foreground">
            {REPORT.card.source.replace('{page}', String(ancestry.source_page))}
          </p>
        </CardContent>
      </Card>

      {lineages.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">{REPORT.ancestry.lineages}</CardTitle>
          </CardHeader>
          <CardContent>
            <dl className="space-y-3 text-sm">
              {lineages.map(([label, value]) => (
                <div key={label} className="space-y-0.5">
                  <dt className="text-xs text-muted-foreground">{label}</dt>
                  <dd className="leading-relaxed">{value}</dd>
                </div>
              ))}
            </dl>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
