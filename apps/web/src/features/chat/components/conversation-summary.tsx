import { Skeleton } from '@/components/ui/skeleton'
import { useConversationSummary } from '@/shared/api/queries'
import { Markdown } from '@/shared/ui/markdown'

/**
 * Recap of the session, generated from the stored turns.
 *
 * Regenerated on open rather than kept incrementally: the checkpointer already
 * holds the conversation, and an incremental recap would drift from it.
 */
export function ConversationSummary({
  patientId,
  sessionId,
}: {
  patientId: string
  sessionId: string
}) {
  const { data, isLoading } = useConversationSummary(patientId, sessionId, true)

  return (
    <div className="border-b bg-muted/30 px-4 py-3 text-xs leading-relaxed">
      {isLoading ? (
        <div className="space-y-2">
          <Skeleton className="h-3 w-full" />
          <Skeleton className="h-3 w-[85%]" />
        </div>
      ) : (
        <Markdown>{data?.summary ?? ''}</Markdown>
      )}
    </div>
  )
}
