import { useState } from 'react'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { useReport } from '@/shared/api/queries'
import type { Citation } from '@/shared/api/schemas'
import { CHAT } from '../content'

/**
 * Citations that open the source, instead of only naming it.
 *
 * Naming a page is a claim; showing the sentence is evidence. Since the report
 * is already loaded for the dashboard, the excerpt costs nothing extra to
 * surface, and the person can check the answer against the document without
 * leaving the conversation.
 */
export function CitationList({
  patientId,
  citations,
}: {
  patientId: string
  citations: Citation[]
}) {
  const [openTitle, setOpenTitle] = useState<string | null>(null)
  const { data: report } = useReport(patientId)

  function excerptFor(citation: Citation): string | null {
    if (!report) return null
    const finding = report.risk_findings.find((item) => item.condition === citation.title)
    if (finding) return finding.interpretation
    if (citation.section === 'ancestry') return report.ancestry.summary
    const trait = report.traits.find((item) => item.name === citation.title)
    if (trait) return `${trait.gene} · ${trait.variant} · ${trait.result}`
    const drug = report.pharmacogenomics.find((item) => item.drug === citation.title)
    if (drug) return `${drug.gene} · ${drug.genotype} · ${drug.phenotype}`
    return null
  }

  return (
    <div className="space-y-1.5 pt-1">
      <p className="text-xs font-medium text-muted-foreground">{CHAT.sources}</p>
      <ul className="space-y-1.5">
        {citations.map((citation) => {
          const isOpen = openTitle === citation.title
          const excerpt = excerptFor(citation)
          return (
            <li key={`${citation.title}-${citation.page}`}>
              <div className="flex flex-wrap items-center gap-1.5">
                <Badge variant="outline" className="font-normal">
                  {citation.title} · {CHAT.page.replace('{page}', String(citation.page))}
                </Badge>
                {excerpt && (
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-6 px-1.5 text-xs"
                    aria-expanded={isOpen}
                    onClick={() => setOpenTitle(isOpen ? null : citation.title)}
                  >
                    {CHAT.citation.trigger}
                  </Button>
                )}
              </div>
              {isOpen && excerpt && (
                <blockquote className="mt-1.5 border-l-2 py-1 pl-3 text-xs leading-relaxed text-muted-foreground">
                  {excerpt}
                </blockquote>
              )}
            </li>
          )
        })}
      </ul>
    </div>
  )
}
