import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import type { Pharmacogenomic, Trait } from '@/shared/api/schemas'
import { REPORT } from '../content'

// Tables scroll inside their own container: on a phone the page itself must
// never scroll sideways.
function TableShell({
  title,
  description,
  children,
}: {
  title: string
  description: string
  children: React.ReactNode
}) {
  return (
    <Card>
      <CardHeader className="gap-1">
        <CardTitle className="text-base">{title}</CardTitle>
        <p className="text-sm text-muted-foreground">{description}</p>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">{children}</div>
      </CardContent>
    </Card>
  )
}

const headCell = 'px-3 py-2 text-left text-xs font-medium text-muted-foreground'
const cell = 'px-3 py-2.5 align-top'

export function TraitTable({ traits }: { traits: Trait[] }) {
  return (
    <TableShell title={REPORT.traits.title} description={REPORT.traits.description}>
      <table className="w-full min-w-[34rem] border-collapse text-sm">
        <thead>
          <tr className="border-b">
            <th className={headCell}>{REPORT.traits.columns.name}</th>
            <th className={headCell}>{REPORT.traits.columns.gene}</th>
            <th className={headCell}>{REPORT.traits.columns.result}</th>
            <th className={headCell}>{REPORT.traits.columns.page}</th>
          </tr>
        </thead>
        <tbody>
          {traits.map((trait) => (
            <tr key={`${trait.gene}-${trait.name}`} className="border-b last:border-0">
              <td className={`${cell} font-medium`}>{trait.name}</td>
              <td className={`${cell} text-muted-foreground`}>{trait.gene}</td>
              <td className={cell}>{trait.result}</td>
              <td className={`${cell} tabular-nums text-muted-foreground`}>
                {trait.source_page}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </TableShell>
  )
}

export function PharmaTable({ entries }: { entries: Pharmacogenomic[] }) {
  return (
    <TableShell title={REPORT.pharma.title} description={REPORT.pharma.description}>
      <table className="w-full min-w-[38rem] border-collapse text-sm">
        <thead>
          <tr className="border-b">
            <th className={headCell}>{REPORT.pharma.columns.drug}</th>
            <th className={headCell}>{REPORT.pharma.columns.gene}</th>
            <th className={headCell}>{REPORT.pharma.columns.phenotype}</th>
            <th className={headCell}>{REPORT.pharma.columns.page}</th>
          </tr>
        </thead>
        <tbody>
          {entries.map((entry) => (
            <tr key={`${entry.drug}-${entry.gene}`} className="border-b last:border-0">
              <td className={`${cell} font-medium`}>{entry.drug}</td>
              <td className={`${cell} text-muted-foreground`}>{entry.gene}</td>
              <td className={cell}>
                <span>{entry.phenotype}</span>
                {entry.note && (
                  <span className="mt-1 block text-xs text-muted-foreground">{entry.note}</span>
                )}
              </td>
              <td className={`${cell} tabular-nums text-muted-foreground`}>
                {entry.source_page}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </TableShell>
  )
}
