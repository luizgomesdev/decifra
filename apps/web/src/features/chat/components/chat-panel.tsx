import { zodResolver } from '@hookform/resolvers/zod'
import { HugeiconsIcon } from '@hugeicons/react'
import {
  ArrowTurnBackwardIcon,
  PauseIcon,
  RefreshIcon,
  SentIcon,
} from '@hugeicons/core-free-icons'
import { useEffect, useState } from 'react'
import { Controller, useForm } from 'react-hook-form'
import { z } from 'zod'

import { Badge } from '@/components/ui/badge'
import { Bubble, BubbleContent } from '@/components/ui/bubble'
import { Button } from '@/components/ui/button'
import { Field, FieldError } from '@/components/ui/field'
import { Marker, MarkerContent } from '@/components/ui/marker'
import { Message, MessageContent } from '@/components/ui/message'
import {
  MessageScroller,
  MessageScrollerContent,
  MessageScrollerItem,
  MessageScrollerProvider,
  MessageScrollerViewport,
} from '@/components/ui/message-scroller'
import { Textarea } from '@/components/ui/textarea'
import { useHistory } from '@/shared/api/queries'
import { Markdown } from '@/shared/ui/markdown'
import { CapabilitiesCard } from './capabilities-card'
import { CitationList } from './citation-list'
import { CHAT } from '../content'
import { useChatStream } from '../use-chat-stream'
import { useSession } from '../use-session'

const questionSchema = z.object({
  question: z.string().trim().min(1, CHAT.validation.empty).max(500, CHAT.validation.tooLong),
})

type QuestionForm = z.infer<typeof questionSchema>

export function ChatPanel({
  patientId,
  pendingQuestion,
  onPendingConsumed,
}: {
  patientId: string
  pendingQuestion?: string
  onPendingConsumed: () => void
}) {
  const { sessionId, remember, clear } = useSession(patientId)
  const { data: history = [] } = useHistory(patientId, sessionId)
  const { state, send, stop, reset } = useChatStream(patientId, sessionId, remember)
  const [lastQuestion, setLastQuestion] = useState<string>()

  const form = useForm<QuestionForm>({
    resolver: zodResolver(questionSchema),
    defaultValues: { question: '' },
  })

  function ask(question: string) {
    setLastQuestion(question)
    void send(question)
  }

  useEffect(() => {
    if (!pendingQuestion) return
    onPendingConsumed()
    ask(pendingQuestion)
  }, [pendingQuestion])

  function submit(values: QuestionForm) {
    form.reset({ question: '' })
    ask(values.question)
  }

  // While a stream is running its text is shown live; once it settles the
  // persisted history is the source of truth, so the live copy is dropped to
  // avoid rendering the same answer twice.
  const settled = !state.isStreaming && !state.text
  const showLive = state.isStreaming || Boolean(state.text)
  const isEmpty = history.length === 0 && !showLive

  return (
    <div className="flex h-full min-h-0 flex-col">
      <header className="flex items-start justify-between gap-2 border-b px-4 py-3">
        <div>
          <h2 className="text-sm font-medium">{CHAT.title}</h2>
          <p className="text-xs text-muted-foreground">{CHAT.subtitle}</p>
        </div>
        {(history.length > 0 || showLive) && (
          <Button
            variant="ghost"
            size="sm"
            className="shrink-0 text-xs"
            onClick={() => {
              clear()
              reset()
            }}
          >
            {CHAT.actions.newChat}
          </Button>
        )}
      </header>

      <MessageScrollerProvider>
        <MessageScroller className="min-h-0 flex-1">
          <MessageScrollerViewport className="px-4 py-4">
            <MessageScrollerContent className="space-y-4">
              {isEmpty && (
                <div className="space-y-3 py-2">
                  <CapabilitiesCard />
                  <div className="space-y-2 text-center">
                    <p className="text-xs text-muted-foreground">{CHAT.empty.hint}</p>
                    <div className="flex flex-col gap-2">
                      {CHAT.suggestions.map((suggestion) => (
                        <Button
                          key={suggestion}
                          variant="outline"
                          size="sm"
                          className="h-auto whitespace-normal py-2 text-left"
                          onClick={() => ask(suggestion)}
                        >
                          {suggestion}
                        </Button>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {history.map((turn, index) => (
                <MessageScrollerItem key={`${turn.role}-${index}`}>
                  <Message align={turn.role === 'user' ? 'end' : 'start'}>
                    <MessageContent>
                      <Bubble variant={turn.role === 'user' ? 'default' : 'muted'}>
                        <BubbleContent className="text-sm leading-relaxed">
                          {turn.role === 'user' ? (
                            <span className="whitespace-pre-wrap">{turn.text}</span>
                          ) : (
                            <Markdown>{turn.text}</Markdown>
                          )}
                        </BubbleContent>
                      </Bubble>
                    </MessageContent>
                  </Message>
                </MessageScrollerItem>
              ))}

              {showLive && !settled && (
                <MessageScrollerItem scrollAnchor>
                  <Message align="start">
                    <MessageContent>
                      <Bubble variant="muted">
                        <BubbleContent className="text-sm leading-relaxed">
                          <Markdown>{state.text}</Markdown>
                        </BubbleContent>
                      </Bubble>
                    </MessageContent>
                  </Message>
                </MessageScrollerItem>
              )}

              {state.stage && (
                <Marker>
                  <MarkerContent className="flex items-center gap-2">
                    <span className="size-1.5 animate-pulse rounded-full bg-current" />
                    {state.stage}
                  </MarkerContent>
                </Marker>
              )}

              {state.error && (
                <Marker>
                  <MarkerContent>{CHAT.error}</MarkerContent>
                </Marker>
              )}

              {!state.isStreaming && state.citations.length > 0 && (
                <CitationList patientId={patientId} citations={state.citations} />
              )}

              {!state.isStreaming && state.flags.length > 0 && (
                <ul className="flex flex-wrap gap-1.5">
                  {state.flags.map((flag) => (
                    <li key={flag}>
                      <Badge variant="secondary" className="font-normal">
                        {CHAT.guardLabels[flag] ?? flag}
                      </Badge>
                    </li>
                  ))}
                </ul>
              )}

              {/* G9: recovering from a bad answer without retyping it. */}
              {!state.isStreaming && lastQuestion && (
                <div className="flex flex-wrap gap-2">
                  <Button variant="ghost" size="sm" className="text-xs" onClick={() => ask(lastQuestion)}>
                    <HugeiconsIcon icon={RefreshIcon} className="size-3.5" aria-hidden />
                    {CHAT.actions.retry}
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-xs"
                    onClick={() => form.setValue('question', lastQuestion)}
                  >
                    <HugeiconsIcon icon={ArrowTurnBackwardIcon} className="size-3.5" aria-hidden />
                    {CHAT.actions.edit}
                  </Button>
                </div>
              )}
            </MessageScrollerContent>
          </MessageScrollerViewport>
        </MessageScroller>
      </MessageScrollerProvider>

      <form onSubmit={form.handleSubmit(submit)} className="border-t p-3">
        <Controller
          name="question"
          control={form.control}
          render={({ field, fieldState }) => (
            <Field data-invalid={fieldState.invalid} className="gap-2">
              <div className="flex items-end gap-2">
                <Textarea
                  {...field}
                  rows={2}
                  aria-label={CHAT.placeholder}
                  aria-invalid={fieldState.invalid}
                  placeholder={CHAT.placeholder}
                  className="max-h-32 min-h-11 resize-none"
                  onKeyDown={(event) => {
                    if (event.key === 'Enter' && !event.shiftKey) {
                      event.preventDefault()
                      void form.handleSubmit(submit)()
                    }
                  }}
                />
                {state.isStreaming ? (
                  <Button type="button" size="icon" variant="outline" onClick={stop} aria-label={CHAT.actions.stop}>
                    <HugeiconsIcon icon={PauseIcon} className="size-4" aria-hidden />
                  </Button>
                ) : (
                  <Button type="submit" size="icon" aria-label={CHAT.send}>
                    <HugeiconsIcon icon={SentIcon} className="size-4" aria-hidden />
                  </Button>
                )}
              </div>
              {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
            </Field>
          )}
        />
      </form>
    </div>
  )
}
