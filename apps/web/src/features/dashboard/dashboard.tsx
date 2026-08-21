import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { AncestryPanel } from '@/features/report/components/ancestry-panel'
import { PharmaTable, TraitTable } from '@/features/report/components/data-tables'
import { RiskCard } from '@/features/report/components/risk-card'
import { SummaryCard } from '@/features/report/components/summary-card'
import { REPORT } from '@/features/report/content'
import { useReport } from '@/shared/api/queries'
import { DASHBOARD } from './content'

/**
 * Summary first, then sections.
 *
 * The portal usability study moved the overview above everything else after
 * user feedback: it answers "what does this mean for me" without requiring
 * someone to read four sections to find out.
 */
export function Dashboard({
  patientId,
  onAsk,
}: {
  patientId: string
  onAsk: (question: string) => void
}) {
  const { data: report, isLoading, isError } = useReport(patientId)

  if (isLoading) {
    return (
      <div className="space-y-4" aria-label={DASHBOARD.loading}>
        <Skeleton className="h-40 w-full" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
      </div>
    )
  }

  if (isError || !report) {
    return <p className="text-sm text-muted-foreground">{REPORT.empty.error}</p>
  }

  return (
    <div className="space-y-6">
      <SummaryCard patientId={patientId} />

      <Tabs defaultValue="risks">
        <TabsList className="w-full justify-start overflow-x-auto">
          <TabsTrigger value="risks">{REPORT.sections.risks}</TabsTrigger>
          <TabsTrigger value="ancestry">{REPORT.sections.ancestry}</TabsTrigger>
          <TabsTrigger value="traits">{REPORT.sections.traits}</TabsTrigger>
          <TabsTrigger value="pharma">{REPORT.sections.pharma}</TabsTrigger>
        </TabsList>

        <TabsContent value="risks" className="mt-4 space-y-3">
          {report.risk_findings.map((finding) => (
            <RiskCard key={`${finding.gene}-${finding.condition}`} finding={finding} onAsk={onAsk} />
          ))}
        </TabsContent>

        <TabsContent value="ancestry" className="mt-4">
          <AncestryPanel report={report} />
        </TabsContent>

        <TabsContent value="traits" className="mt-4">
          <TraitTable traits={report.traits} />
        </TabsContent>

        <TabsContent value="pharma" className="mt-4">
          <PharmaTable entries={report.pharmacogenomics} />
        </TabsContent>
      </Tabs>
    </div>
  )
}
