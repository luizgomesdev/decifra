import { HugeiconsIcon } from '@hugeicons/react'
import { SparklesIcon } from '@hugeicons/core-free-icons'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { useSummary } from '@/shared/api/queries'
import { Markdown } from '@/shared/ui/markdown'
import { REPORT } from '../content'

/**
 * The summary opens the page.
 *
 * The portal study put the overview before everything else after user feedback,
 * and it is the piece that answers "what does this mean for me" without making
 * someone read four sections first.
 *
 * The disclaimer arrives inside the text from the API, appended by the same
 * middleware that guards the chat, so it cannot be forgotten here.
 */
export function SummaryCard({ patientId }: { patientId: string }) {
  const { data, isLoading } = useSummary(patientId)
  const [body, disclaimer] = (data?.summary ?? '').split('\n---\n')

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <HugeiconsIcon icon={SparklesIcon} className="size-4 text-primary" aria-hidden />
          {REPORT.summary.title}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {isLoading ? (
          <div className="space-y-2" aria-label={REPORT.summary.loading}>
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-[92%]" />
            <Skeleton className="h-4 w-[78%]" />
          </div>
        ) : (
          <>
            <div className="text-sm leading-relaxed">
              <Markdown>{body}</Markdown>
            </div>
            {disclaimer && (
              <p className="border-t pt-3 text-xs leading-relaxed text-muted-foreground">
                {disclaimer.trim()}
              </p>
            )}
          </>
        )}
      </CardContent>
    </Card>
  )
}
