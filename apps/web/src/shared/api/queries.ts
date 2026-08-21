import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { z } from 'zod'

import { api } from './client'
import {
  chatAnswerSchema,
  historyTurnSchema,
  patientSchema,
  reportSchema,
  summarySchema,
} from './schemas'

export const queryKeys = {
  patients: ['patients'] as const,
  report: (patientId: string) => ['report', patientId] as const,
  summary: (patientId: string) => ['summary', patientId] as const,
  history: (patientId: string, sessionId: string) =>
    ['history', patientId, sessionId] as const,
}

export function usePatients() {
  return useQuery({
    queryKey: queryKeys.patients,
    queryFn: () => api.get('/patients', z.array(patientSchema)),
  })
}

export function useReport(patientId: string | undefined) {
  return useQuery({
    queryKey: queryKeys.report(patientId ?? ''),
    queryFn: () => api.get(`/patients/${patientId}/report`, reportSchema),
    enabled: Boolean(patientId),
  })
}

export function useSummary(patientId: string | undefined) {
  return useQuery({
    queryKey: queryKeys.summary(patientId ?? ''),
    queryFn: () => api.get(`/patients/${patientId}/summary`, summarySchema),
    enabled: Boolean(patientId),
    // The summary is generated on the fly and costs a model call, so it is not
    // refetched on every focus.
    staleTime: 5 * 60 * 1000,
  })
}

export function useHistory(patientId: string | undefined, sessionId: string | undefined) {
  return useQuery({
    queryKey: queryKeys.history(patientId ?? '', sessionId ?? ''),
    queryFn: () =>
      api.get(
        `/patients/${patientId}/sessions/${sessionId}/messages`,
        z.array(historyTurnSchema),
      ),
    enabled: Boolean(patientId && sessionId),
  })
}

export function useAsk(patientId: string | undefined) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (input: { question: string; sessionId?: string }) =>
      api.post(`/patients/${patientId}/chat`, chatAnswerSchema, {
        question: input.question,
        session_id: input.sessionId ?? null,
      }),
    onSuccess: (answer) => {
      queryClient.invalidateQueries({
        queryKey: queryKeys.history(patientId ?? '', answer.session_id),
      })
    },
  })
}
