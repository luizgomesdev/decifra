import { useCallback, useRef, useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'

import { queryKeys } from '@/shared/api/queries'
import type { Citation } from '@/shared/api/schemas'

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export type StreamState = {
  stage: string | null
  text: string
  citations: Citation[]
  flags: string[]
  refused: boolean
  isStreaming: boolean
  error: string | null
}

const IDLE: StreamState = {
  stage: null,
  text: '',
  citations: [],
  flags: [],
  refused: false,
  isStreaming: false,
  error: null,
}

/**
 * Consumes the SSE chat endpoint.
 *
 * The server releases one verified paragraph at a time, so `text` only ever
 * holds content that already passed the clinical check. The `final` event may
 * still replace it, which happens when a guardrail rewrote the whole answer.
 *
 * An AbortController backs the stop button: cancelling matters more here than
 * in a generic chat, because the person is waiting on something about their own
 * health and should not feel stuck.
 */
export function useChatStream(
  patientId: string,
  sessionId: string | undefined,
  onSession: (sessionId: string) => void,
) {
  const [state, setState] = useState<StreamState>(IDLE)
  const abortRef = useRef<AbortController | null>(null)
  const queryClient = useQueryClient()

  const stop = useCallback(() => {
    abortRef.current?.abort()
    setState((previous) => ({ ...previous, isStreaming: false, stage: null }))
  }, [])

  const send = useCallback(
    async (question: string) => {
      abortRef.current?.abort()
      const controller = new AbortController()
      abortRef.current = controller
      setState({ ...IDLE, isStreaming: true })

      let activeSession = sessionId

      try {
        const response = await fetch(`${BASE_URL}/patients/${patientId}/chat/stream`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question, session_id: sessionId ?? null }),
          signal: controller.signal,
        })
        if (!response.ok || !response.body) throw new Error(`HTTP ${response.status}`)

        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let carry = ''

        for (;;) {
          const { done, value } = await reader.read()
          if (done) break
          carry += decoder.decode(value, { stream: true })

          const frames = carry.split('\n\n')
          carry = frames.pop() ?? ''

          for (const frame of frames) {
            const nameLine = frame.split('\n').find((line) => line.startsWith('event: '))
            const dataLine = frame.split('\n').find((line) => line.startsWith('data: '))
            if (!nameLine || !dataLine) continue

            const name = nameLine.slice(7).trim()
            const payload = JSON.parse(dataLine.slice(6))

            if (name === 'session') {
              activeSession = payload.session_id
              onSession(payload.session_id)
            } else if (name === 'stage') {
              setState((previous) => ({ ...previous, stage: payload.label }))
            } else if (name === 'delta') {
              setState((previous) => ({ ...previous, text: previous.text + payload.text }))
            } else if (name === 'final') {
              setState((previous) => ({
                ...previous,
                text: payload.replaced ? payload.text : previous.text || payload.text,
                citations: payload.citations,
                flags: payload.flags,
                refused: payload.refused,
                isStreaming: false,
                stage: null,
              }))
            }
          }
        }
      } catch (error) {
        if ((error as Error).name === 'AbortError') return
        setState((previous) => ({
          ...previous,
          isStreaming: false,
          stage: null,
          error: (error as Error).message,
        }))
        return
      }

      if (activeSession) {
        queryClient.invalidateQueries({ queryKey: queryKeys.history(patientId, activeSession) })
      }
    },
    [patientId, sessionId, onSession, queryClient],
  )

  const reset = useCallback(() => setState(IDLE), [])

  return { state, send, stop, reset }
}
